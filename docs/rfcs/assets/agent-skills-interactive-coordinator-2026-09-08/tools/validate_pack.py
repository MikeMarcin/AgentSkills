#!/usr/bin/env python3
"""Validate this RFC packet offline; never execute source or invoke agents."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit

RFC = 'RFC-ASK-0010'
ACS = {f'{RFC}-AC{i:02d}' for i in range(1, 15)}
CARD_IDS = {f'ASK-{i:04d}' for i in range(50, 59)}
DISPOSITIONS = {'milestone-complete', 'continue-milestone', 'human-pending', 'blocked', 'cancelled', 'pack-complete', 'review-request'}

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result

def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)

def frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding='utf-8').splitlines()
    if not lines or lines[0] != '---':
        raise ValueError('missing frontmatter')
    result = {}
    for line in lines[1:]:
        if line == '---':
            return result
        key, separator, value = line.partition(':')
        if not separator or key in result:
            raise ValueError('invalid or duplicate frontmatter key')
        result[key] = json.loads(value.strip())
    raise ValueError('unclosed frontmatter')

def return_findings(value: dict) -> list[str]:
    """Check the packet's example implications, not native semantic acceptance."""
    errors = []
    required = {'schema','run_id','dispatch_id','producer_id','mandate_revision','milestone','disposition','summary','candidate_revision','handoff_ref','ownership','next_objective','required_pending','evidence_refs'}
    if not isinstance(value, dict) or not required <= value.keys():
        return ['return: missing required fields']
    if set(value) - required - {'review_request'}:
        errors.append('return: unknown fields')
    if value['schema'] != 'implement-rfc.milestone-return.v1':
        errors.append('return: invalid version')
    if value['disposition'] not in DISPOSITIONS:
        errors.append('return: invalid disposition')
    for key in ('run_id','dispatch_id','producer_id','mandate_revision','milestone','summary'):
        if not isinstance(value[key], str) or not value[key].strip():
            errors.append(f'return: empty {key}')
    for key in ('required_pending','evidence_refs'):
        if not isinstance(value[key], list) or any(not isinstance(x,str) or not x for x in value[key]) or len(set(value[key])) != len(value[key]):
            errors.append(f'return: invalid {key}')
    for key in ('handoff_ref','next_objective'):
        if value[key] is not None and (not isinstance(value[key], str) or not value[key].strip()):
            errors.append(f'return: invalid {key}')
    rev = value['candidate_revision']
    if rev is not None and (not isinstance(rev, str) or re.fullmatch(r'(?:[a-f0-9]{40}|[a-f0-9]{64})', rev) is None):
        errors.append('return: invalid candidate revision')
    if value['ownership'] not in ('active','unknown','quiescent'):
        errors.append('return: invalid ownership')
    if value['disposition'] == 'pack-complete':
        if value['ownership'] != 'quiescent' or value['required_pending'] or value['next_objective'] is not None or not value['evidence_refs']:
            errors.append('return: pack completion prerequisites absent')
    if value['disposition'] == 'milestone-complete':
        if value['ownership'] != 'quiescent' or not value['handoff_ref'] or not value['evidence_refs']:
            errors.append('return: milestone completion prerequisites absent')
    if value['disposition'] == 'review-request':
        r = value.get('review_request', {})
        if value['ownership'] != 'quiescent' or set(r) != {'role','candidate_ref','assignment'} or r.get('role') not in ('rfc-reviewer','rfc-reviewer-critical') or not r.get('candidate_ref') or not r.get('assignment'):
            errors.append('return: invalid review request')
    elif 'review_request' in value:
        errors.append('return: unexpected review request')
    return errors

def safe_relative(value: str) -> bool:
    p = PurePosixPath(value)
    return bool(value) and not p.is_absolute() and '\\' not in value and ':' not in value and all(x not in ('..','.') for x in p.parts)

def validate(root: Path, *, check_manifest: bool = True) -> list[str]:
    root = root.resolve()
    findings = []
    files = {}
    folded = {}
    # A packet is passive regular files. Do not dereference a symlink.
    for p in sorted(root.rglob('*')):
        relative = p.relative_to(root).as_posix()
        if '__pycache__' in p.parts or p.suffix == '.pyc':
            findings.append(f'layout: generated cache: {relative}')
            continue
        if p.is_symlink():
            findings.append(f'layout: symbolic link: {relative}')
            continue
        if relative.casefold() in folded:
            findings.append(f'layout: case collision: {relative}')
        folded[relative.casefold()] = relative
        if not safe_relative(relative):
            findings.append(f'layout: unsafe path: {relative}')
        if p.is_file():
            files[relative] = p
        elif not p.is_dir():
            findings.append(f'layout: special entry: {relative}')
    def load(name):
        try:
            return read_json(root/name)
        except (OSError, ValueError) as error:
            findings.append(f'json: {name}: {error}')
            return None
    parsed = {name:load(name) for name in files if name.endswith('.json')}
    if check_manifest:
        manifest = parsed.get('PACK_MANIFEST.json')
        if not isinstance(manifest, dict) or not isinstance(manifest.get('files'), list):
            findings.append('manifest: absent or malformed')
        else:
            listed = {}
            for row in manifest['files']:
                if not isinstance(row,dict) or not isinstance(row.get('path'),str) or not safe_relative(row['path']):
                    findings.append('manifest: unsafe or malformed member');continue
                name = row['path']
                if name in listed:
                    findings.append(f'manifest: duplicate member: {name}')
                listed[name] = row
                p=files.get(name)
                if p is None:
                    findings.append(f'manifest: absent member: {name}');continue
                data=p.read_bytes()
                if row.get('bytes') != len(data) or row.get('sha256') != hashlib.sha256(data).hexdigest():
                    findings.append(f'manifest: content mismatch: {name}')
            actual=set(files)-{'PACK_MANIFEST.json'}
            if set(listed) != actual:
                findings.append('manifest: member set differs from actual packet')
    rfc_paths=sorted((root/'docs/rfcs').glob('RFC-ASK-*.md'))
    if len(rfc_paths)!=1:
        findings.append('rfc: expected exactly one live packet RFC')
    else:
        try:
            meta=frontmatter(rfc_paths[0])
            if meta.get('id')!=RFC or meta.get('status')!='Proposed':
                findings.append('rfc: incorrect identity or non-Proposed status')
            declared=set(re.findall(r'\*\*(RFC-ASK-\d{4}-AC\d{2})\s+—', rfc_paths[0].read_text()))
            if declared!=ACS:
                findings.append('rfc: expected fourteen distinct declared criteria')
        except (ValueError,OSError) as error:
            findings.append(f'rfc: {error}')
    cards={}
    card_paths={}
    for p in sorted((root/'docs/issues').glob('*/*.md')):
        try:
            m=frontmatter(p); key=m.get('id')
            if key in cards:
                findings.append(f'card: duplicate id {key}')
            cards[key]=m; card_paths[key]=p
            if m.get('schema')!='implement-rfc.card.v1' or m.get('rfcs')!=[RFC] or m.get('metadata',{}).get('provisional_id') is not True:
                findings.append(f'card: invalid schema, RFC or provisional marker: {key}')
            if not isinstance(m.get('depends_on'),list) or len(set(m['depends_on']))!=len(m['depends_on']):
                findings.append(f'card: invalid dependencies {key}')
            expected_status='Ready' if key=='ASK-0050' else 'Backlog'
            expected_lane='20-ready' if expected_status=='Ready' else '10-backlog'
            if m.get('status')!=expected_status or p.parent.name!=expected_lane:
                findings.append(f'card: wrong initial status/lane: {key}')
        except (ValueError,OSError,TypeError) as error:
            findings.append(f'card: {p.name}: {error}')
    if set(cards)!=CARD_IDS:
        findings.append('card: expected nine provisional IDs ASK-0050 through ASK-0058')
    for key,m in cards.items():
        deps=m.get('depends_on',[])
        if isinstance(deps,list) and any(d not in cards or d==key for d in deps):
            findings.append(f'card: invalid dependency target: {key}')
    visiting=set();visited=set()
    def visit(key):
        if key in visiting:
            findings.append(f'card: dependency cycle at {key}');return
        if key in visited or key not in cards:return
        visiting.add(key)
        for dependency in cards[key].get('depends_on',[]):visit(dependency)
        visiting.remove(key);visited.add(key)
    try:
        for key in cards:visit(key)
    except (TypeError,RecursionError):findings.append('card: malformed dependency graph')
    closeouts=[key for key,m in cards.items() if m.get('closeout_for')==[RFC]]
    if closeouts!=['ASK-0058']:
        findings.append('closeout: expected exactly ASK-0058')
    elif (p:=card_paths.get('ASK-0058')) is not None:
        text=p.read_text()
        rows=set(re.findall(r'^\| (RFC-ASK-\d{4}-AC\d{2}) \|',text,re.M))
        if rows!=ACS:findings.append('closeout: acceptance rows incomplete')
        unrun=set(re.findall(r'^\| (RFC-ASK-\d{4}-AC\d{2}) \| Not recorded \| Not run \| Unrecorded \|$',text,re.M))
        if unrun!=ACS:findings.append('closeout: premature packet acceptance')
        if 'RFC_BASE_SHA: UNRECORDED' not in text:findings.append('closeout: fabricated packet baseline')
        match=re.search(r'^Planned cards: (.+)$',text,re.M)
        if not match or set(re.findall(r'ASK-\d{4}',match.group(1)))!=CARD_IDS-{'ASK-0058'}:
            findings.append('closeout: planned cards incomplete')
    plan=parsed.get('issue-plan.json')
    if isinstance(plan,dict):
        if plan.get('ids_are_provisional') is not True or plan.get('rfc')!=RFC:
            findings.append('plan: incorrect identity/provisional flag')
        covered=set();implementation_covered=set();planned=set()
        for row in plan.get('cards',[]):
            key=row.get('id');planned.add(key)
            if key not in cards or row.get('depends')!=cards.get(key,{}).get('depends_on') or not safe_relative(row.get('path','')) or root/row.get('path','')!=card_paths.get(key):
                findings.append(f'plan: card mismatch {key}')
            covered.update(RFC+'-'+ac for ac in row.get('acs',[]))
            if key!='ASK-0058':implementation_covered.update(RFC+'-'+ac for ac in row.get('acs',[]))
        if planned!=CARD_IDS or covered!=ACS or implementation_covered!=ACS:findings.append('plan: identity or acceptance coverage incomplete')
    else:findings.append('plan: absent')
    target=parsed.get('fixtures/target-routing.json');baseline=parsed.get('reference/baseline/routing.json')
    if isinstance(target,dict) and isinstance(baseline,dict):
        expected={'codex':{'model':'gpt-5.6-sol','effort':'low'},'claude':{'model':'claude-opus-5','effort':'low'}}
        if target.get('coordinator')!=expected:findings.append('routing: owner-selected coordinator pair changed')
        if target.get('preserved_routing_snapshot')!=baseline:findings.append('routing: preserved leaf routes changed')
        if target.get('integration_precedence')!=['explicit_task_choice','preserved_owner_engineering_choice','independent_integration_default']:findings.append('routing: integration precedence changed')
        topo=target.get('ordinary_topology',{})
        if topo.get('rfc-coordinator')!=['rfc-integrator'] or set(topo.get('rfc-integrator',[]))!=set(baseline.get('assignments',{})) or topo.get('leaf_children')!=[]:
            findings.append('routing: invalid ordinary topology')
    else:findings.append('routing: target/baseline absent')
    fixture=parsed.get('fixtures/coordination-cases.json')
    if isinstance(fixture,dict):
        ids=set()
        for c in fixture.get('cases',[]):
            if not all(c.get(k) for k in ('id','trigger','expected','forbidden','criteria')) or c.get('id') in ids or not {RFC+'-'+ac for ac in c.get('criteria',[])}<=ACS:
                findings.append('cases: duplicate, incomplete or invalid case')
            ids.add(c.get('id'))
        if len(ids)!=24:findings.append('cases: expected 24 unique workflow cases')
    else:findings.append('cases: absent')
    example=parsed.get('fixtures/return.example.json')
    try:findings.extend(return_findings(example))
    except (ValueError,TypeError,AttributeError):findings.append('return: malformed example')
    usage=parsed.get('fixtures/owning-response.synthetic.json')
    if isinstance(usage,dict):
        unique={};sums={k:0 for k in ('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')}
        for rec in usage.get('records',[]):
            p=rec.get('payload',{});key=(p.get('thread_id'),p.get('response_id'))
            if key in unique and unique[key]!=p:findings.append('usage fixture: conflicting duplicate')
            unique[key]=p
        for p in unique.values():
            for key in sums:sums[key]+=p.get('usage',{}).get(key,0)
        sums['uncached_input_tokens']=sums['input_tokens']-sums['cached_input_tokens'];sums['unique_owning_responses']=len(unique)
        if sums!=usage.get('expected'):findings.append('usage fixture: hand-calculated totals disagree')
    else:findings.append('usage fixture: absent')
    # Check actual Markdown links only; inline code path examples are not fake links.
    for name,p in files.items():
        if not name.endswith('.md'):continue
        text=p.read_text(encoding='utf-8')
        for match in re.finditer(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)',text):
            link=match.group(1)
            if urlsplit(link).scheme or link.startswith('#'):continue
            raw=unquote(link.split('#',1)[0])
            resolved=(p.parent/raw).resolve()
            if not resolved.is_relative_to(root):findings.append(f'links: escape in {name}: {link}')
            elif not resolved.exists():findings.append(f'links: missing in {name}: {link}')
    skill=root/'draft/skills/implement-rfc/SKILL.md'
    if skill.exists():
        head=skill.read_text().split('---',2)[1]
        keys=set(re.findall(r'^([\w-]+):',head,re.M))
        if keys!={'name','description'}:findings.append('skill: nonportable draft frontmatter')
        if 'name: implement-rfc' not in head:findings.append('skill: incorrect name')
    else:findings.append('skill: missing coordinator draft')
    return findings

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args()
    try:
        findings=validate(args.root)
    except (OSError,ValueError,TypeError) as error:
        findings=[f'packet could not be inspected: {error}']
    result={'ok':not findings,'scope':'packet only; no native/implementation acceptance','rfcs':1,'cards':9,'acceptance_criteria':14,'workflow_cases':24,'findings':findings}
    if args.json:print(json.dumps(result,indent=2))
    elif findings:print('\n'.join(findings),file=sys.stderr)
    else:print('PASS: 1 RFC, 9 cards, 14 criteria, 24 cases; packet checks only.')
    return 1 if findings else 0
if __name__=='__main__':raise SystemExit(main())
