#!/usr/bin/env python3
"""Validate pack integrity, link targets, card dependencies and contract examples.

Uses only the stdlib. This does not implement a general JSON Schema engine and
never declares the future product/native acceptance criteria passed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--skip-manifest',action='store_true')
    args=parser.parse_args();root=args.root.resolve();errors=[]
    def require(value,message):
        if not value:errors.append(message)
    plan=json.loads((root/'issue-plan.json').read_text());rfcs=json.loads((root/'rfc_definitions.json').read_text())
    cards={x['id']:x for x in plan}
    require(len(cards)==21,'Expected 21 unique cards')
    require(len(rfcs)==4,'Expected four RFCs')
    for c in plan:
        p=root/c['path'];require(p.is_file(),'Missing card '+c['id'])
        if not p.is_file():continue
        content=p.read_text();m=re.match(r'---\n(.*?)\n---\n',content,re.S)
        require(m is not None,'Missing card frontmatter '+c['id'])
        if m:
            fm={k:json.loads(v) for k,v in (line.split(': ',1) for line in m.group(1).splitlines())}
            require(fm.get('id')==c['id'],'Card ID mismatch '+c['id'])
            require(fm.get('depends_on')==c['depends_on'],'Dependency mismatch '+c['id'])
            require(fm.get('rfcs')==c['rfcs'],'RFC mismatch '+c['id'])
            require(fm.get('status')==('Ready' if not c['depends_on'] else 'Backlog'),'Premature card status '+c['id'])
        for d in c['depends_on']:require(d in cards,'Missing dependency '+d)
    gray=set();black=set()
    def visit(k):
        if k in gray:errors.append('Dependency cycle '+k);return
        if k in black or k not in cards:return
        gray.add(k)
        for d in cards[k]['depends_on']:visit(d)
        gray.remove(k);black.add(k)
    for k in cards:visit(k)
    for r in rfcs.values():
        p=root/'docs/rfcs'/r['filename'];require(p.is_file(),'Missing RFC '+r['id'])
        close=[c for c in plan if r['id'] in c['closeout_for']]
        require(len(close)==1,'Exactly one closeout required '+r['id'])
        if len(close)!=1:continue
        content=(root/close[0]['path']).read_text()
        for i in range(1,len(r['acceptance'])+1):
            ac=f"{r['id']}-AC{i:02d}"
            require(any(ac in c['coverage'] and not c['closeout_for'] for c in plan),'No implementation card covers '+ac)
            require('| '+ac+' |' in content,'Missing closeout row '+ac)
    for p in root.rglob('*.md'):
        # Links created by this pack; source paths in code/backticks are not links.
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if link.startswith(('http:','https:','mailto:','#')):continue
            path=link.split('#',1)[0]
            require((p.parent/path).exists(),f'Broken link {p.relative_to(root)} -> {path}')
    for p in (root/'contracts').glob('*.json'):
        d=json.loads(p.read_text());require(d.get('$schema')=='https://json-schema.org/draft/2020-12/schema','Schema dialect '+p.name)
    example=json.loads((root/'examples/command-stage.example.json').read_text())
    require(example['example_only'] is True,'Example must not be executable authorization')
    tasks={t['id']:t for t in example['tasks']}
    require(len(tasks)==len(example['tasks']),'Duplicate example task')
    require(example['tasks'][-1]['kind']=='integration_gate','Example lacks semantic gate')
    for t in tasks.values():
        require(all(x in tasks for x in t['depends_on']),'Missing task dependency')
        if t['kind']=='command':require(isinstance(t['argv'],list) and bool(t['argv']),'Command argv missing')
    events=json.loads((root/'examples/scout-recovery.events.example.json').read_text())
    require(all(e['simulated'] is True for e in events),'Synthetic trace mislabelled')
    require([e['sequence'] for e in events]==list(range(len(events))),'Trace sequence mismatch')
    require(not any(e['event']=='accepted' for e in events),'Example must not invent acceptance')
    if not args.skip_manifest:
        manifest=json.loads((root/'PACK_MANIFEST.json').read_text())
        actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='PACK_MANIFEST.json'}
        require(actual==set(manifest['files']),'Manifest membership mismatch')
        for name,desc in manifest['files'].items():
            p=root/name
            require(p.is_file(),'Manifest missing file '+name)
            if p.is_file():
                require(p.stat().st_size==desc['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==desc['sha256'],'Integrity mismatch '+name)
    for error in errors:print('ERROR '+error,file=sys.stderr)
    print(f'{len(rfcs)} RFCs, {len(cards)} cards, {sum(len(r["acceptance"]) for r in rfcs.values())} criteria; {len(errors)} pack violations')
    return int(bool(errors))

if __name__=='__main__':raise SystemExit(main())
