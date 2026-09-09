"""Synthetic fixtures only. No model tasks, credentials, or external network."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import usage_capture as u
import usage

STAMP = '2026-09-07T12:00:00Z'

def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows), encoding='utf-8')
    return path


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.project = self.root/'repo'; self.project.mkdir()
        self.other = self.root/'other'; self.other.mkdir()
        self.ch, self.cx, self.out = self.root/'claude', self.root/'codex', self.root/'out'; self.out.mkdir()
        self.projects = u.Projects([f'Example={self.project}'])

    def audit(self):
        a = u.Collector(self.projects, u.dt('2026-09-07T00:00:00Z'), u.dt('2026-09-08T00:00:00Z'),
                        self.out, 1024**2, 1024**2)
        a.scan(self.ch, self.cx)
        self.events = [json.loads(x) for x in (self.out/'events.jsonl').read_text().splitlines()]
        return a

    def ce(self, typ='assistant', **kw):
        e = {'type': typ, 'sessionId': 'parent', 'cwd': str(self.project), 'timestamp': STAMP,
             'message': {'id': 'm1', 'model': 'claude-opus-5', 'content': [{'type': 'text', 'text': 'PRIVATE SOURCE'}],
                         'usage': {'input_tokens': 30, 'output_tokens': 5, 'cache_read_input_tokens': 400}}}
        e.update(kw); return e

    def xe(self, typ, payload): return {'type': typ, 'timestamp': STAMP, 'payload': payload}

    def test_project_boundaries_and_worktree_alias(self):
        self.assertEqual(self.projects.match(str(self.project/'sub')), 'Example')
        self.assertIsNone(self.projects.match(str(self.project)+'-other'))
        old = self.project.parent / 'old-deleted-worktree'
        p = u.Projects([f'Example={self.project}'], [f'Example={old}'])
        self.assertEqual(p.match(str(old/'src')), 'Example')
        self.assertTrue(u.within(u.norm(r'C:\code\test\src'), u.norm(r'C:\code\test')))
        self.assertFalse(u.within(u.norm(r'C:\code\testing'), u.norm(r'C:\code\test')))

    def test_registered_worktree(self):
        with patch.object(u, 'git', return_value='worktree /registered/tree\nHEAD abc\n'):
            p = u.Projects([f'Example={self.project}'])
        self.assertIsNone(p.match('/registered/tree/subdir'))

    def test_primary_child_exclusion_and_synthetic(self):
        write(self.ch/'projects/r/parent.jsonl', [self.ce()])
        child = self.ce(agentId='child', message={'id': 'm2', 'model': '<synthetic>',
                  'content': [{'type': 'text', 'text': 'You hit your usage limit'}], 'usage': {'input_tokens': 0}},
                  isApiErrorMessage=True)
        path = write(self.ch/'projects/r/parent/subagents/agent-child.jsonl', [child])
        path.with_suffix('.meta.json').write_text(json.dumps({'agentType': 'rfc-scout', 'toolUseId': 'call1'}))
        write(self.ch/'projects/other/a.jsonl', [self.ce(cwd=str(self.other))])
        a = self.audit()
        self.assertEqual(len(a.sessions), 2)
        s = next(s for s in a.sessions.values() if s['kind']=='subagent')
        self.assertEqual(s['launch_tool_use_id'], u.ident('call1'))
        errors = [e for e in self.events if e.get('synthetic_or_api_error')]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_class_text_candidate'], 'quota_or_rate_limit')
        raw=(self.out/'events.jsonl').read_text()
        self.assertNotIn('PRIVATE SOURCE', raw); self.assertNotIn(str(self.project), raw)

    def test_streamed_responses_remain_reconcilable_not_summed(self):
        a = self.ce(); b = self.ce(); b['message']['usage']['output_tokens'] = 9
        write(self.ch/'projects/r/p.jsonl', [a,a,b])
        audit = self.audit()
        rows=[e for e in self.events if e['kind']=='assistant_record']
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['response_id'], rows[1]['response_id'])
        self.assertGreater(audit.stats['duplicate_normalized_events'], 0)
        self.assertNotIn('billed_tokens', rows[0])

    def test_tool_limit_join_does_not_count_bash_grep(self):
        calls = self.ce(message={'id':'m1','model':'claude-opus-5','content':[
          {'type':'tool_use','id':'agentcall','name':'Agent','input':{'subagent_type':'rfc-scout','prompt':'private'}},
          {'type':'tool_use','id':'bashcall','name':'Bash','input':{'command':'grep private'}}]})
        results = self.ce('user', message={'content':[
          {'type':'tool_result','tool_use_id':'agentcall','content':'Maximum turns reached. Partial result.\nagentId: child'},
          {'type':'tool_result','tool_use_id':'bashcall','content':'Maximum turns reached. Partial result.'}]})
        resume = self.ce(message={'id':'m2','model':'claude-opus-5','content':[
          {'type':'tool_use','id':'resume','name':'SendMessage','input':{'to':'child','message':'report only'}}]})
        write(self.ch/'projects/r/p.jsonl', [calls, results, resume]); self.audit()
        stop=[e for e in self.events if e.get('turn_limit_text_candidate')]
        self.assertEqual(len(stop), 1)
        self.assertEqual(stop[0]['tool'], 'Agent')
        control=next(e for e in self.events if e.get('tool')=='SendMessage')
        self.assertEqual(control['target'],stop[0]['returned_agent_id'])

    def test_codex_child_ownership_cumulative_and_last_separate(self):
        rows=[self.xe('session_meta', {'id':'child','cwd':str(self.project),
                  'source': {'subagent': {'thread_spawn': {'parent_thread_id':'parent','agent_role':'rfc-worker'}}}}),
              self.xe('turn_context', {'turn_id':'t0','model':'gpt-5.6-sol','effort':'high'}),
              self.xe('event_msg', {'type':'token_count','info': {'total_token_usage':{'input_tokens':100}}}),
              self.xe('event_msg', {'type':'task_started','thread_id':'child','turn_id':'t1'}),
              self.xe('turn_context', {'turn_id':'t1','model':'gpt-6-astra','effort':'low'}),
              self.xe('event_msg', {'type':'token_count','turn_id':'t1','info': {
                 'total_token_usage': {'input_tokens':150,'cached_input_tokens':100,'output_tokens':50,'reasoning_output_tokens':40},
                 'last_token_usage': {'input_tokens':50,'output_tokens':10}},
                 'rate_limits': {'primary': {'used_percent': 20}}})]
        write(self.cx/'sessions/r.jsonl',rows)
        a=self.audit(); tok=[e for e in self.events if e['kind']=='token_observation']
        self.assertEqual([e['ownership'] for e in tok], ['uncertain_fork_or_child','explicit'])
        self.assertEqual(tok[1]['cumulative']['output_tokens'],50)
        self.assertEqual(tok[1]['last']['output_tokens'],10)
        self.assertEqual(a.stats['coverage_warnings'],0)

    def test_codex_string_child_source_not_primary(self):
        write(self.cx/'sessions/r.jsonl',[self.xe('session_meta', {'id':'child','cwd':str(self.project),'source': {'subagent':'review'}}),
             self.xe('turn_context', {'turn_id':'t','model':'gpt-6-astra','effort':'low'})])
        a=self.audit(); self.assertEqual(next(iter(a.sessions.values()))['kind'],'subagent')

    def test_malformed_and_missing_time_are_coverage_warnings(self):
        path=write(self.ch/'projects/r/p.jsonl',[self.ce(),self.ce(timestamp='not a timestamp')])
        with path.open('a') as f:f.write('not json\n')
        a=self.audit(); self.assertEqual(a.stats['coverage_warnings'],2)

    def test_claude_structured_rates_no_argument_collision(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce(rate_limits={'five_hour':{'used_percentage':40,'resets_at':1788811200}})])
        a=self.audit(); self.assertEqual(a.stats['coverage_warnings'],0)
        self.assertEqual(len([e for e in self.events if e['kind']=='quota_observation']),1)

    def test_date_window_excludes_old_activity(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce(timestamp='2026-09-06T23:00:00Z'),self.ce()])
        self.audit(); self.assertEqual(len(self.events),1)

    def test_config_secret_allowlist(self):
        self.ch.mkdir(parents=True)
        (self.ch/'settings.json').write_text(json.dumps({'model':'claude-opus-5','env':{'TOKEN':'DO_NOT_EXPORT'},
            'hooks':{'Stop':[{'command':'DO_NOT_EXPORT'}]},'statusLine':{'command':'DO_NOT_EXPORT'}}))
        (self.ch/'auth.json').write_text('DO_NOT_EXPORT')
        out=u.inventory(self.projects,self.ch,self.cx)
        self.assertNotIn('DO_NOT_EXPORT',json.dumps(out)); self.assertEqual(out['config_allowlist'][0]['settings']['model'],'claude-opus-5')

    def test_size_limit_is_not_zero_usage(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce(message={'content':'x'*(1024**2+1)})])
        a=self.audit(); self.assertGreater(a.stats['coverage_warnings'],0)

    def test_cli_archive_and_no_overwrite(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce()])
        output=self.root/'result.zip'
        command=[sys.executable,str(Path(u.__file__).with_name('usage.py')), '--project',f'Example={self.project}', '--since','2026-09-07',
                  '--until','2026-09-08','--claude-home',str(self.ch),'--codex-home',str(self.cx),'--out',str(output)]
        done=subprocess.run(command,capture_output=True,text=True); self.assertEqual(done.returncode,0,done.stderr)
        with zipfile.ZipFile(output) as z:
            manifest=json.loads(z.read('manifest.json'))
            self.assertIn('SUMMARY.md',manifest['files'])
            self.assertFalse(manifest['billing_or_quota_estimates'])
            for name in z.namelist(): self.assertNotIn(b'PRIVATE SOURCE',z.read(name))
        again=subprocess.run(command,capture_output=True,text=True); self.assertNotEqual(again.returncode,0)


    def test_native_response_owner_is_not_inherited_turn_context(self):
        rows=[self.xe('session_meta',{'id':'child','cwd':str(self.project),'parent_thread_id':'root'}),
              self.xe('turn_context',{'turn_id':'t','model':'configured-model','effort':'high'}),
              self.xe('token_usage_record',{'thread_id':'child','response_id':'r','turn_id':'t',
                       'usage':{'input_tokens':100,'cached_input_tokens':80,'cache_write_input_tokens':0,'output_tokens':10},
                       'private':'PRIVATE SOURCE'}),
              self.xe('token_usage_record',{'thread_id':'root','response_id':'inherited','turn_id':'t',
                       'usage':{'input_tokens':20,'output_tokens':2}}),
              self.xe('event_msg',{'type':'token_usage_record','response_id':'owner-missing','turn_id':'t',
                       'usage':{'input_tokens':30,'output_tokens':3}}),
              self.xe('token_usage_record',{'thread_id':'child','response_id':'','usage':{'input_tokens':10,'output_tokens':1}})]
        write(self.cx/'sessions/child.jsonl',rows)
        audit=self.audit();records=[e for e in self.events if e['kind']=='response_usage']
        self.assertEqual([e['ownership'] for e in records],['explicit','other_thread','owner_missing','explicit'])
        self.assertEqual(records[0]['owner_session'],u.ident('codex:child'))
        self.assertIsNone(records[-1]['response_id'])
        self.assertEqual(records[0]['model'],'unknown')
        self.assertEqual(records[0]['usage']['cache_write_input_tokens'],0)
        self.assertEqual(audit.sessions[u.ident('codex:child')]['parent_session'],u.ident('codex:root'))
        self.assertNotIn('PRIVATE SOURCE',(self.out/'events.jsonl').read_text())

    def test_conflicting_session_parents_stay_unknown_in_both_orders(self):
        for index,parents in enumerate((('a','b'),('b','a'))):
            for filename,native,parent in [('root-a','a',None),('root-b','b',None),
                    ('child-first','child',parents[0]),('child-second','child',parents[1]),
                    ('leaf','leaf','child')]:
                write(self.cx/'sessions'/f'{filename}.jsonl',[
                    self.xe('session_meta',{'id':native,'cwd':str(self.project),'parent_thread_id':parent}),
                    self.xe('token_usage_record',{'thread_id':native,'response_id':'r-'+native,
                             'usage':{'input_tokens':10,'output_tokens':1}})])
            capture=self.root/f'parents-{index}.zip';report_dir=self.root/f'parents-report-{index}'
            command=[sys.executable,'-B',str(Path(u.__file__).with_name('usage.py')),
                     '--project',f'Example={self.project}','--since','2026-09-07','--until','2026-09-08',
                     '--claude-home',str(self.ch),'--codex-home',str(self.cx),'--out',str(capture)]
            done=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)
            with zipfile.ZipFile(capture) as archive:
                coverage=json.loads(archive.read('coverage.json'))
                self.assertIn('native_session_parent_conflict',[v['code'] for v in coverage['warnings']])
                sessions=json.loads(archive.read('sessions.json'))
                child=next(v for v in sessions if v['key']==u.ident('codex:child'))
                self.assertTrue(child['parent_conflict'])
                self.assertIsNone(child['parent_session'])
            done=subprocess.run([sys.executable,'-B',str(Path(u.__file__).with_name('usage_report.py')),
                                 str(capture),'--out',str(report_dir)],capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)
            report=json.loads((report_dir/'summary.json').read_text())['captures'][0]
            for native in ('child','leaf'):
                lineage=report['session_lineage'][u.ident('codex:'+native)]
                self.assertIsNone(lineage['family_root'])
                self.assertEqual(lineage['lineage_status'],'conflicting_parent')
            self.assertEqual(sum(v['observed_tokens'] for v in report['groups']),44)
            self.assertEqual(sum(v['observed_tokens'] for v in report['families']),22)

    def test_public_owning_family_capture_report(self):
        fixture=Path(__file__).resolve().parents[3]/'docs/rfcs/assets/agent-skills-interactive-coordinator-2026-09-08/fixtures/owning-response.synthetic.json'
        original=fixture.read_bytes();value=json.loads(original)
        for thread in value['lineage']:
            native=thread['thread'];parent=thread['parent']
            rows=[self.xe('session_meta',{'id':native,'cwd':str(self.project),
                  'parent_thread_id':parent,'agent_role':'rfc-integrator' if native.startswith('integrator') else 'unknown'})]
            baseline=self.xe('event_msg',{'type':'token_count','thread_id':native,
                     'info':{'total_token_usage':{'input_tokens':0,'output_tokens':0}}})
            baseline['timestamp']='2026-09-06T23:59:59Z';rows.append(baseline)
            owning=[v for v in value['records'] if v['file_thread']==native]
            rows += [self.xe(v['type'],{**v['payload'],'private':'PRIVATE SOURCE'}) for v in owning]
            usage_counts=owning[0]['payload']['usage']
            total=self.xe('event_msg',{'type':'token_count','thread_id':native,
                     'info':{'total_token_usage':{'input_tokens':usage_counts['input_tokens'],'output_tokens':usage_counts['output_tokens']}}})
            total['timestamp']='2026-09-07T12:00:01Z';rows.append(total)
            write(self.cx/'sessions'/f'{native}.jsonl',rows)
        capture=self.root/'family.zip'
        command=[sys.executable,'-B',str(Path(u.__file__).with_name('usage.py')),'--project',f'Example={self.project}',
                 '--since','2026-09-07','--until','2026-09-08','--claude-home',str(self.ch),'--codex-home',str(self.cx),'--out',str(capture)]
        done=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(done.returncode,0,done.stderr)
        captured=capture.read_bytes()
        with zipfile.ZipFile(capture) as archive:
            for name in archive.namelist():self.assertNotIn(b'PRIVATE SOURCE',archive.read(name))
            events=[json.loads(line) for line in archive.read('events.jsonl').splitlines()]
            self.assertEqual(len([e for e in events if e['kind']=='response_usage']),4)
        for observed in (False,True):
            out=self.root/('family-observed' if observed else 'family-missing')
            command=[sys.executable,'-B',str(Path(u.__file__).with_name('usage_report.py')),str(capture),'--out',str(out)]
            if observed:
                outcomes={'schema':'implement-rfc.outcomes.v1','assignments':[
                    {'session':u.ident('codex:'+t['thread']),'task_id':'capability','attempt_id':str(i),
                     'evidence_ref':'synthetic-assignment','since':'2026-09-07T00:00:00Z','until':'2026-09-08T00:00:00Z'}
                    for i,t in enumerate(value['lineage'])],
                    'events':[{'event_id':'accepted','state':'accepted','task_id':'capability','timestamp':STAMP,'evidence_ref':'synthetic-verdict'}]}
                path=self.root/'outcomes.json';path.write_text(json.dumps(outcomes));command+=['--outcomes',str(path)]
            done=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)
            report=json.loads((out/'summary.json').read_text());summary=report['captures'][0]
            self.assertEqual(summary['classification_rows'],{'alternate_observation':4,'request_reconciled':4})
            self.assertEqual(sum(g['observed_tokens'] for g in summary['groups']),825)
            self.assertEqual(summary['families'],[{'root_session':u.ident('codex:coordinator'),
                'observed_tokens':825,'unknown_rows':0,'session_count':4,'coverage':'observed_descendants_only'}])
            self.assertEqual(summary['session_lineage'][u.ident('codex:worker-1')]['lineage_depth'],2)
            self.assertEqual(report['outcomes']['accepted_task_count'],1 if observed else None)
            self.assertEqual(report['outcomes']['observed_tokens_per_accepted_task'],825 if observed else None)
        self.assertEqual(capture.read_bytes(),captured)
        self.assertEqual(fixture.read_bytes(),original)


class CaptureBoundsTests(AuditTests):
    def collector(self):
        audit = u.Collector(self.projects, u.dt('2026-09-07T00:00:00Z'), u.dt('2026-09-08T00:00:00Z'), self.out, 0, 4096)
        self.addCleanup(audit.writer.close)
        for index in (audit.sessions, audit.emitted, audit.call_map, audit.counter_baselines):
            self.addCleanup(index.close)
        return audit

    def test_append_reads_only_initial_snapshot(self):
        audit = self.collector()
        path = write(self.root / 'active.jsonl', [{'type': 'one'}, {'type': 'two'}])
        rows = audit.rows(path)
        self.assertEqual(next(rows)[1]['type'], 'one')
        with path.open('a') as stream:
            stream.write('{"type":"later"}\n')
        self.assertEqual([r['type'] for _, r in rows], ['two'])
        self.assertIn('file_changed_while_reading', [x['code'] for x in audit.problems])

    def test_oversize_line_and_torn_tail_are_visible(self):
        audit = self.collector()
        path = self.root / 'hostile.jsonl'
        path.write_bytes(b'x' * 10000 + b'\n{"type":"valid"}\n{"type":"tail"}')
        self.assertEqual([r['type'] for _,r in audit.rows(path)], ['valid'])
        self.assertEqual([x['code'] for x in audit.problems], ['line_size_limit', 'unterminated_snapshot_tail'])
        self.assertEqual(audit.stats['scan_bytes'], path.stat().st_size)

    def test_newest_baseline_and_no_activity(self):
        audit = self.collector()
        session = audit.session('codex', 'test', None, 'Example', None, None, self.root)
        for when, count in [('2026-09-06T23:00:00Z', 8), ('2026-09-06T22:00:00Z', 3)]:
            audit.emit(session, 'token_observation', when, self.root, 1, cumulative={'input_tokens':count})
        self.assertEqual(audit.counter_baselines[session['key']]['cumulative']['input_tokens'], 8)
        self.assertEqual(session['events'], 0)

    def test_publish_preserves_existing_and_symlink(self):
        target = self.root / 'existing.zip'
        target.write_bytes(b'preserve')
        link = self.root / 'link.zip'
        link.symlink_to(target)
        for path in (target, link):
            with self.assertRaises(FileExistsError):
                usage.publish(self.out, path)
        self.assertEqual(target.read_bytes(), b'preserve')
        self.assertTrue(link.is_symlink())

    def test_interrupted_publish_removes_only_created_output(self):
        target = self.root / 'interrupted.zip'
        with patch.object(usage.shutil, 'copyfileobj', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                usage.publish(self.out, target)
        self.assertFalse(target.exists())

    def test_disk_indexes_have_bounded_python_memory(self):
        import tracemalloc
        audit = self.collector()
        tracemalloc.start()
        try:
            for i in range(12000):
                session = audit.session('codex', str(i), None, 'Example', None, None, self.root)
                audit.emit(session, 'token_observation', STAMP, self.root, i, last={'input_tokens':i})
                audit.call_map[(str(i), 'call')] = 'wait_agent'
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(len(audit.sessions), 12000)
        self.assertLess(peak, 4 * 1024 * 1024)


if __name__=='__main__':unittest.main()
