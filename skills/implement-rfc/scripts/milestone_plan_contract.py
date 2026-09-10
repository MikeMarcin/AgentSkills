"""Portable bounded plan syntax, typed remapping and deterministic human view.

Structural validity does not establish semantic coverage or acceptance.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = 'implement-rfc.milestone-plan.v1'
LIMIT = 1024 * 1024
SLUG = re.compile(r'[a-z0-9][a-z0-9-]{0,95}\Z')
ISSUE = re.compile(r'[A-Z][A-Z0-9]*-[0-9]+\Z')
RFC = re.compile(r'RFC-[A-Z][A-Z0-9]*-[0-9]+\Z')


def load_json(path: Path) -> Any:
    """Read bounded UTF-8 JSON and reject duplicated keys/nonfinite values."""
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError(f'expected an ordinary file: {path}')
    with path.open('rb') as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError(f'JSON exceeds {LIMIT} bytes: {path}')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    def constant(value):
        raise ValueError(f'nonfinite JSON value: {value}')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except RecursionError:
        raise ValueError('JSON nesting exceeds supported depth') from None


def normalize(plan: dict) -> dict:
    out = copy.deepcopy(plan)
    out.setdefault('coverage', 'complete')
    out.setdefault('unplanned_work', [])
    return out


def fingerprint(plan: dict) -> str:
    errors = validate_plan(plan)
    if errors:
        raise ValueError('; '.join(errors))
    encoded = json.dumps(normalize(plan), sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return 'sha256:' + hashlib.sha256(encoded).hexdigest()


def validate_plan(value: Any, catalog: dict | None = None) -> list[str]:
    """Structural and optional reference checks; semantic coverage stays unproven.

    catalog = {"issues": {ID: {"rfcs": [...]}}, "rfcs": [ID, ...]}.
    Criterion text resolution and acceptance truth intentionally remain out of scope.
    """
    errors: list[str] = []
    def fail(text): errors.append(text)
    def obj(v, name, required, allowed):
        if not isinstance(v, dict):
            fail(f'{name}: expected object'); return False
        if set(v) - set(allowed): fail(f'{name}: unknown fields {sorted(set(v)-set(allowed))}')
        if set(required) - set(v): fail(f'{name}: missing fields {sorted(set(required)-set(v))}')
        return True
    def text(v): return isinstance(v, str) and bool(v.strip())
    def array_strings(v, name, minimum=0, pattern=None):
        if not isinstance(v, list) or len(v) < minimum:
            fail(f'{name}: expected list of at least {minimum} strings'); return False
        if any(not text(x) or pattern is not None and not pattern.fullmatch(x) for x in v):
            fail(f'{name}: invalid string'); return False
        if len(v) != len(set(v)): fail(f'{name}: duplicate strings')
        return True
    if not obj(value, 'plan', ['schema','id','scope','milestones'],
               ['schema','id','scope','milestones','coverage','unplanned_work']): return errors
    if value.get('schema') != SCHEMA: fail('unsupported plan schema')
    if not text(value.get('id')) or not SLUG.fullmatch(value['id']): fail('invalid plan id')
    scope = value.get('scope')
    if obj(scope, 'scope', [], ['rfcs','issues']):
        for key, pat in [('rfcs', RFC), ('issues', ISSUE)]:
            if key in scope: array_strings(scope[key], 'scope.'+key, pattern=pat)
        if not any(isinstance(scope.get(k),list) and scope[k] for k in ('rfcs','issues')):
            fail('scope: requires at least one RFC or issue')
    else: scope = {}
    coverage = value.get('coverage', 'complete')
    if coverage not in ('complete','partial'): fail('invalid coverage')
    unplanned = value.get('unplanned_work', [])
    if not isinstance(unplanned, list): fail('unplanned_work: expected list'); unplanned=[]
    if coverage=='partial' and not unplanned: fail('partial coverage needs unplanned_work')
    if coverage=='complete' and unplanned: fail('complete coverage cannot have unplanned_work')
    milestones=value.get('milestones')
    if not isinstance(milestones,list) or not 1<=len(milestones)<=256:
        fail('milestones: expected 1 to 256 entries'); return errors
    ids=[]; refs=[]; edges={}
    def work(items, location):
        if not isinstance(items,list) or not items:
            fail(f'{location}: expected nonempty work list'); return
        for i, ref in enumerate(items):
            where=f'{location}[{i}]'
            if not obj(ref,where,[],['issue','rfc','criteria']): continue
            kinds=[k for k in ('issue','rfc') if k in ref]
            if len(kinds)!=1: fail(where+': exactly one issue or rfc required'); continue
            kind=kinds[0]; name=ref[kind]; pat=ISSUE if kind=='issue' else RFC
            if not text(name) or not pat.fullmatch(name): fail(where+': invalid ref'); continue
            sels=ref.get('criteria')
            if 'criteria' in ref and not array_strings(sels,where+'.criteria',minimum=1): continue
            refs.append((kind,name,sels,location))
    for i,m in enumerate(milestones):
        where=f'milestones[{i}]'
        if not obj(m,where,['id','outcome','work','depends_on','exit_criteria','boundary'],
                   ['id','outcome','work','depends_on','exit_criteria','boundary']):continue
        mid=m.get('id')
        if not text(mid) or not SLUG.fullmatch(mid): fail(where+': invalid id'); continue
        ids.append(mid)
        for key in ('outcome','boundary'):
            if not text(m.get(key)): fail(where+': missing '+key)
        array_strings(m.get('exit_criteria'),where+'.exit_criteria',minimum=1)
        if array_strings(m.get('depends_on'),where+'.depends_on',pattern=SLUG):
            edges[mid]=m['depends_on']
        work(m.get('work'),mid)
    if len(ids)!=len(set(ids)):fail('duplicate milestone id')
    if unplanned: work(unplanned,'unplanned_work')
    for mid,deps in edges.items():
        for dep in deps:
            if dep not in ids:fail(f'{mid}: missing milestone dependency {dep}')
            if dep==mid:fail(f'{mid}: self dependency')
    state={}
    def visit(mid):
        if state.get(mid)==1:fail('milestone dependency cycle'); return
        if state.get(mid)==2:return
        state[mid]=1
        for dep in edges.get(mid,[]):
            if dep in edges:visit(dep)
        state[mid]=2
    for mid in ids:visit(mid)
    prior={}
    for kind,name,sels,where in refs:
        key=(kind,name)
        for old,loc in prior.get(key,[]):
            if old is None or sels is None or set(old)&set(sels):
                fail(f'overlapping work {name}: {loc} / {where}')
        prior.setdefault(key,[]).append((sels,where))
    explicit=scope.get('issues',[])
    if isinstance(explicit,list):
        represented={name for kind,name,_,_ in refs if kind=='issue'}
        for item in explicit:
            if isinstance(item,str) and item not in represented:
                fail(f'unaccounted explicit issue {item}')
    if catalog is not None:
        known_issues=catalog.get('issues',{}); known_rfcs=set(catalog.get('rfcs',[]))
        scope_rfcs=set(scope.get('rfcs',[])) if isinstance(scope.get('rfcs',[]),list) and all(isinstance(x,str) for x in scope.get('rfcs',[])) else set()
        scope_issues=set(explicit) if isinstance(explicit,list) and all(isinstance(x,str) for x in explicit) else set()
        for rid in scope_rfcs:
            if rid not in known_rfcs:fail(f'unresolved scoped RFC {rid}')
        for iid in scope_issues:
            if iid not in known_issues:fail(f'unresolved scoped issue {iid}')
        for kind,name,sels,where in refs:
            if kind=='rfc':
                if name not in known_rfcs:fail(f'unresolved RFC {name}')
                if name not in scope_rfcs:fail(f'RFC outside declared scope {name}')
            else:
                if name not in known_issues:fail(f'unresolved issue {name}');continue
                if name not in scope_issues and not scope_rfcs.intersection(known_issues[name].get('rfcs',[])):
                    fail(f'issue outside declared scope {name}')
    return sorted(set(errors))


def remap_plan(plan: dict, mapping: dict[str,str],
               criterion_mapping: dict[tuple[str,str,str],str] | None = None) -> dict:
    """Remap typed IDs only, preserving prose and milestone identities.

    Criterion mapping keys are (kind, original document ID, original selector).
    Relative labels such as AC01 must never be renamed across unrelated sources.
    """
    errors=validate_plan(plan)
    if errors:raise ValueError('; '.join(errors))
    out=copy.deepcopy(plan)
    if not isinstance(mapping, dict):
        raise ValueError('ID mapping must be an object')
    for old, new in mapping.items():
        if not isinstance(old, str):
            raise ValueError('ID mapping keys must be strings')
        pattern = RFC if RFC.fullmatch(old) else ISSUE
        if not pattern.fullmatch(old) or not isinstance(new, str) or not pattern.fullmatch(new):
            raise ValueError('ID mapping must preserve reference types')
    for kind in ('issues','rfcs'):
        if kind in out['scope']:out['scope'][kind]=[mapping.get(x,x) for x in out['scope'][kind]]
    for refs in [m['work'] for m in out['milestones']]+[out.get('unplanned_work',[])]:
        for ref in refs:
            kind='issue' if 'issue' in ref else 'rfc'
            original=ref[kind]
            ref[kind]=mapping.get(original,original)
            if 'criteria' in ref:
                ref['criteria']=[(criterion_mapping or {}).get((kind,original,c),
                    next((new+c[len(old):] for old,new in mapping.items()
                          if re.fullmatch(re.escape(old)+r'-AC[0-9]+',c)),c))
                    for c in ref['criteria']]
    errors=validate_plan(out)
    if errors:raise ValueError('; '.join(errors))
    return out


def render(plan: dict) -> str:
    errors=validate_plan(plan)
    if errors:raise ValueError('; '.join(errors))
    lines=['# Milestones', '', '> Generated from `milestone-plan.json`; edit the JSON, not this view.',
           '', f'Plan: **{plan["id"]}** · Coverage: **{plan.get("coverage","complete")}**', '',
           'These are integration outcomes, not compulsory agent-launch boundaries.', '']
    for m in plan['milestones']:
        lines += ['## '+m['id'], '', m['outcome'], '', '**Work:** '+', '.join(
            ('`'+r.get('issue',r.get('rfc'))+'`'+(' ['+', '.join(r['criteria'])+']' if 'criteria' in r else '')) for r in m['work']),
            '', '**Prerequisites:** '+(', '.join(m['depends_on']) or 'None'), '', '**Completion:**', '']
        lines += ['- '+c for c in m['exit_criteria']]
        lines += ['', '**Boundary:** '+m['boundary'], '']
    if plan.get('unplanned_work'):
        lines+=['## Required work not yet decomposed','','```json',json.dumps(plan['unplanned_work'],indent=2),'```','']
    return '\n'.join(lines).rstrip()+'\n'
