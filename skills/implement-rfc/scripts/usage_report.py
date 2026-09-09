#!/usr/bin/env python3
"""Validate immutable captures and write an offline report in a new directory."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import zipfile
sys.dont_write_bytecode=True
from usage_accounting import reconcile,SCHEMAS,estimate
from usage_outcomes import Outcomes,validate_experiment
from usage_capture import dt
from usage_quota import sanitize_snapshot

MAX_TOTAL=1024*1024*1024
MAX_JSON=16*1024*1024
MAX_LINE=1024*1024


class Capture:
    def __init__(self,path):
        self.archive=zipfile.ZipFile(path)
        try:
            infos=self.archive.infolist();names=[i.filename for i in infos]
            if len(names)>64 or len(set(names))!=len(names):raise ValueError('Duplicate or excessive archive members')
            total=0
            for info in infos:
                name=info.filename
                if '/' in name or '\\' in name or ':' in name or name in ('.','..') or not name or stat.S_ISLNK(info.external_attr>>16):
                    raise ValueError('Unsafe archive member')
                total+=info.file_size
                if total>MAX_TOTAL or info.file_size>MAX_TOTAL or info.file_size>max(1,info.compress_size)*500:
                    raise ValueError('Archive exceeds expansion bounds')
            self.manifest=self.json('manifest.json')
            if not isinstance(self.manifest,dict) or self.manifest.get('schema') not in SCHEMAS:raise ValueError('Unsupported capture schema; input not rewritten')
            expected=self.manifest.get('files')
            if not isinstance(expected,dict) or set(expected)!=set(names)-{'manifest.json'}:raise ValueError('Manifest membership mismatch')
            for name,record in expected.items():
                if not isinstance(record,dict) or type(record.get('bytes')) is not int:raise ValueError('Invalid manifest member')
                h=hashlib.sha256();count=0
                with self.archive.open(name) as stream:
                    while chunk:=stream.read(65536):
                        count+=len(chunk)
                        if count>MAX_TOTAL:raise ValueError('Expanded member exceeds bound')
                        h.update(chunk)
                if count!=record['bytes'] or h.hexdigest()!=record.get('sha256'):raise ValueError('Archive hash/size mismatch')
        except BaseException:
            self.archive.close();raise
    def json(self,name,default=None):
        if name not in self.archive.namelist():return default
        if self.archive.getinfo(name).file_size>MAX_JSON:raise ValueError('JSON member exceeds bound')
        with self.archive.open(name) as stream:return json.loads(stream.read(MAX_JSON+1))
    def events(self):
        if 'events.jsonl' not in self.archive.namelist():raise ValueError('Capture lacks events')
        with self.archive.open('events.jsonl') as stream:
            while raw:=stream.readline(MAX_LINE+1):
                if len(raw)>MAX_LINE or not raw.endswith(b'\n'):raise ValueError('Invalid event line bound/tail')
                value=json.loads(raw)
                if not isinstance(value,dict):raise ValueError('Invalid event object')
                yield value
    def close(self):self.archive.close()


def session_lineage(sessions):
    """Resolve only observed native parent edges, including older v1/v2 captures.

    An observed root does not certify complete family coverage. Roles never
    establish ancestry or acceptance/task identity.
    """
    native={}
    for key,session in sessions.items():
        native.setdefault((session.get('provider'),session.get('session_id'),session.get('agent_id')),[]).append(key)
    parents={};resolved={}
    for key,session in sessions.items():
        parent=session.get('parent_session')
        if not parent and session.get('parent_agent_id'):
            identity=(session.get('provider'),session.get('parent_agent_id'),None) if session.get('provider')=='codex' else (
                session.get('provider'),session.get('session_id'),session.get('parent_agent_id'))
            candidates=native.get(identity,[])
            if len(candidates)!=1:
                resolved[key]={'family_root':None,'lineage_depth':None,'lineage_status':'missing_or_ambiguous_parent'}
                continue
            parent=candidates[0]
        if parent:
            target=sessions.get(parent)
            if not target or any(target.get(k)!=session.get(k) for k in ('project','provider','provider_account_alias','device_alias')):
                resolved[key]={'family_root':None,'lineage_depth':None,'lineage_status':'missing_or_conflicting_parent'}
            else:parents[key]=parent
        elif session.get('kind')=='primary' and not session.get('forked_from') and not session.get('ownership_conflict'):
            resolved[key]={'family_root':key,'lineage_depth':0,'lineage_status':'observed'}
        else:resolved[key]={'family_root':None,'lineage_depth':None,'lineage_status':'parent_unknown'}
    for key in sessions:
        path=[];seen=set();current=key
        while current not in resolved and current not in seen:
            seen.add(current);path.append(current);current=parents[current]
        result=resolved.get(current,{'family_root':None,'lineage_depth':None,'lineage_status':'parent_cycle'})
        for child in reversed(path):
            result={**result,'lineage_depth':result['lineage_depth']+1 if result['lineage_depth'] is not None else None}
            resolved[child]=result
    return resolved


def csv_row(writer,row):
    writer.writerow({k: "'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r','\n')) else v for k,v in row.items()})


def report(paths,out,*,outcomes=None,experiment=None,compare=False,rates=(),rate_mode='historical-rate estimate'):
    if out.exists() or out.is_symlink():raise ValueError('Report destination must be new')
    if experiment is not None:validate_experiment(experiment)
    captures=[]
    try:
        for path in paths:
            captures.append(Capture(path))
        if compare and len(captures)!=2:raise ValueError('Comparison requires exactly two captures')
        with tempfile.TemporaryDirectory(prefix='rfc-usage-report-') as tmp:
            root=Path(tmp);results=[];all_outcomes=Outcomes(outcomes)
            with (root/'ledger.csv').open('w',newline='',encoding='utf-8') as stream:
                writer=csv.DictWriter(stream,fieldnames=['capture','project','provider','session','response','family_root','lineage_depth','lineage_status','task','classification','input_tokens','output_tokens','anomalies','role','session_kind','model','effort','price_equivalent','price_unit'])
                writer.writeheader()
                for index,capture in enumerate(captures):
                    all_outcomes=Outcomes(outcomes)
                    sessions={v['key']:v for v in capture.json('sessions.json',[]) if isinstance(v,dict) and 'key' in v}
                    lineage=session_lineage(sessions)
                    family_sizes=Counter(v['family_root'] for v in lineage.values() if v['family_root'])
                    family_tokens=Counter();family_unknown=Counter()
                    buckets=Counter();groups=Counter();unknown=Counter();activity=Counter();rate_coverage=Counter()
                    for event in capture.events():
                        if event.get('kind')=='tool_call':
                            tool=event.get('tool')
                            activity['wait_list' if tool in ('wait','wait_agent','list_agents','TaskOutput') else 'spawn_message' if tool in ('spawn_agent','Agent','Task','SendMessage','send_message') else 'engineering_or_unknown']+=1
                    for row in reconcile(capture.events(),capture.json('counter_baselines.json',[]),capture.manifest['schema']):
                        session=sessions.get(row.get('session'),{})
                        row['role']=session.get('role','unknown');row['session_kind']=session.get('kind','unknown')
                        row.update(lineage.get(row.get('session'),{'family_root':None,'lineage_depth':None,'lineage_status':'session_metadata_missing'}))
                        classification=row['classification'];buckets[classification]+=1;counts=row.get('tokens') or {}
                        key=(row.get('project') or 'unassigned',row.get('provider') or 'unknown',classification,row['role'],row['session_kind'],row.get('model'),row.get('effort'))
                        if classification in ('request_reconciled','aggregate_only'):
                            groups[key]+=counts.get('input_tokens',0)+counts.get('output_tokens',0)
                        elif classification!='alternate_observation' or row['anomalies']:unknown[key]+=1
                        if row['family_root']:
                            if classification in ('request_reconciled','aggregate_only'):
                                family_tokens[row['family_root']]+=counts.get('input_tokens',0)+counts.get('output_tokens',0)
                            elif classification!='alternate_observation' or row['anomalies']:family_unknown[row['family_root']]+=1
                        all_outcomes.observe(row)
                        price=estimate(row,rates,rate_mode)
                        rate_coverage['known' if price['amount'] is not None else 'unknown']+=1
                        csv_row(writer,{'capture':index,'project':row.get('project'),'provider':row.get('provider'),'session':row.get('session'),
                                         'response':row.get('response_id'),**{k:row[k] for k in ('family_root','lineage_depth','lineage_status')},
                                         'task':all_outcomes.assign(row),'classification':classification,'input_tokens':counts.get('input_tokens'),
                                         'output_tokens':counts.get('output_tokens'),'anomalies':';'.join(row['anomalies']),'role':row['role'],'session_kind':row['session_kind'],'model':row.get('model'),'effort':row.get('effort'),'price_equivalent':price['amount'],'price_unit':price.get('unit')})
                    results.append({'capture':index,'schema':capture.manifest['schema'],'classification_rows':dict(buckets),
                                    'groups':[{'project':k[0],'provider':k[1],'classification':k[2],'observed_tokens':v,'role':k[3],'session_kind':k[4],'model':k[5],'effort':k[6]} for k,v in groups.items()],
                                    'unknown_groups':[{'project':k[0],'provider':k[1],'classification':k[2],'rows':v} for k,v in unknown.items()],
                                    'activity':dict(activity),'rate_coverage':dict(rate_coverage),'rate_mode':rate_mode,'coverage':capture.manifest.get('coverage','legacy_or_unknown'),
                                    'families':[{'root_session':key,'observed_tokens':family_tokens[key],
                                                 'unknown_rows':family_unknown[key],
                                                 'session_count':family_sizes[key],
                                                 'coverage':'observed_descendants_only'}
                                                for key in sorted({v['family_root'] for v in lineage.values() if v['family_root']})],
                                    'session_lineage':lineage,
                                    'outcomes':all_outcomes.summary(),
                                    'account_snapshots':[sanitize_snapshot(v) for v in capture.json('quota_snapshots.json',[])],
                                    'possible_cross_capture_duplicates':'not_summed_across_captures'})
            summary={'schema':'implement-rfc.usage-report.v1','captures':results,'outcomes':all_outcomes.summary() if len(captures)==1 else {**Outcomes(outcomes).summary(),'all_assigned_attempt_tokens':None,'observed_tokens_per_accepted_task':None},
                     'experiment':experiment,'comparison':'observational_only' if compare and not experiment else 'configured' if experiment else 'none',
                     'subscription_spend':None,'account_attribution':'not_apportioned; overlapping account activity is uncontrolled'}
            with (root/'groups.csv').open('w',newline='',encoding='utf-8') as stream:
                writer=csv.DictWriter(stream,fieldnames=['capture','project','provider','classification','observed_tokens','role','session_kind','model','effort'])
                writer.writeheader()
                for result in results:
                    for group in result['groups']:csv_row(writer,{'capture':result['capture'],**group})
            (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
            accepted=summary['outcomes']['accepted_task_count']
            if accepted is None:accepted='unknown (outcome input missing)'
            lines=['# Offline usage report','',f'Captures: {len(captures)}. Explicitly accepted tasks: {accepted}.',
                   '', 'Reconciled requests, aggregate-only deltas and unknown observations are separate. Cache and reasoning subsets are not added twice.',
                   'No subscription spend, quota debit, quality improvement or experiment winner is inferred.',
                   'Copied history across captures is not summed into a comparison total. Account pools remain opaque; concurrent account activity prevents attribution.',
                   'Produced, collected and accepted work are distinct. Missing outcome input is unknown; explicitly observed zero accepted work also has no cost-per-accepted denominator.',
                   'Families follow observed transitive native parent links across integrator generations. Missing parents remain unknown; retained descendants do not prove complete family coverage. Roles are not task identities.','']
            for result in results:
                lines += [f"Capture {result['capture']}: {result['coverage']}; ledger classes {result['classification_rows']}.",
                          f"Control activity: {result['activity']}."]
            if compare:lines += ['', 'Comparison is descriptive. Different real backlog tasks do not establish a causal routing or orchestration win.']
            (root/'REPORT.md').write_text('\n'.join(lines)+'\n')
            out.mkdir(parents=True,exist_ok=False)
            for source in root.iterdir():
                with source.open('rb') as src,(out/source.name).open('xb') as dest:shutil.copyfileobj(src,dest)
            return summary
    finally:
        for capture in captures:capture.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures',type=Path,nargs='+');parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--compare',action='store_true');parser.add_argument('--outcomes',type=Path);parser.add_argument('--experiment',type=Path)
    parser.add_argument('--rates',type=Path)
    parser.add_argument('--rate-mode',choices=['historical-rate estimate','current-rate counterfactual'],default='historical-rate estimate')
    args=parser.parse_args()
    def bounded_json(path):
        if path.stat().st_size>MAX_JSON:raise ValueError('Input JSON exceeds bound')
        return json.loads(path.read_bytes())
    result=report(args.captures,args.out,outcomes=bounded_json(args.outcomes) if args.outcomes else None,
                  experiment=bounded_json(args.experiment) if args.experiment else None,compare=args.compare,
                  rates=bounded_json(args.rates) if args.rates else (),rate_mode=args.rate_mode)
    print(json.dumps({'report':str(args.out.resolve()/'REPORT.md'),'captures':len(result['captures']),'accepted_tasks':result['outcomes']['accepted_task_count']}))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,zipfile.BadZipFile) as error:
        print('usage_report: '+str(error),file=sys.stderr);raise SystemExit(2)
