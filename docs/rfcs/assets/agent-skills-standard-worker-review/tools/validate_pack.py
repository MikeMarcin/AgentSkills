#!/usr/bin/env python3
"""Validate this small RFC pack without touching a repository or network."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def matter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'{path}: missing frontmatter')
    head = text.split('---', 2)[1]
    return {key: json.loads(value) for key, value in
            (line.split(':', 1) for line in head.strip().splitlines())}


def main() -> int:
    errors = []
    manifest = json.loads((ROOT / 'PACK_MANIFEST.json').read_text(encoding='utf-8'))
    actual_paths = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
                    and '__pycache__' not in p.parts and p.suffix != '.pyc'
                    and p.name != 'PACK_MANIFEST.json'}
    if actual_paths != set(manifest['files']):
        errors.append('Manifest membership differs from the packet.')
    for rel, entry in manifest['files'].items():
        path = ROOT / rel
        if not path.is_file() or not path.resolve().is_relative_to(ROOT):
            errors.append('Missing or escaping path: ' + rel)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            errors.append('Hash mismatch: ' + rel)
    rfcs = list((ROOT / 'docs/rfcs').glob('RFC-*.md'))
    cards = list((ROOT / 'docs/issues').glob('*/*.md'))
    if len(rfcs) != 1 or len(cards) != 4:
        errors.append('Expected exactly one RFC and four cards.')
    rfc_fields = matter(rfcs[0]); rid = rfc_fields['id']
    byid = {matter(p)['id']: (p, matter(p)) for p in cards}
    if len(byid) != len(cards):
        errors.append('Duplicate card IDs.')
    closeouts = []
    for iid, (path, f) in byid.items():
        if f['rfcs'] != [rid] or f['status'] not in ('Ready', 'Backlog'):
            errors.append('Invalid card/RFC/status: ' + iid)
        if f['depends_on'] and f['status'] == 'Ready':
            errors.append('Unstarted dependency-blocked card is Ready: ' + iid)
        if any(d not in byid for d in f['depends_on']):
            errors.append('Unresolved dependency: ' + iid)
        if rid in f.get('closeout_for', []):
            closeouts.append(path)
    seen = set()
    active = set()
    def visit(iid):
        if iid in active:
            errors.append('Dependency cycle: ' + iid); return
        if iid in seen: return
        active.add(iid)
        for dep in byid[iid][1]['depends_on']:
            if dep in byid: visit(dep)
        active.remove(iid); seen.add(iid)
    for iid in byid: visit(iid)
    if len(closeouts) != 1:
        errors.append('Expected one closeout.')
    else:
        criteria = set(re.findall(r'\*\*('+re.escape(rid)+r'-AC\d{2})\*\*', rfcs[0].read_text()))
        rows = set(re.findall(r'^\| ('+re.escape(rid)+r'-AC\d{2}) \|', closeouts[0].read_text(), re.M))
        if len(criteria) != 6 or rows != criteria:
            errors.append('Acceptance/closeout coverage differs.')
    for path in ROOT.rglob('*.md'):
        for ref in re.findall(r'\[[^\]\n]+\]\(([^)]+)\)', path.read_text()):
            if '://' in ref or ref.startswith('#'): continue
            dest = unquote(ref.split('#', 1)[0])
            if dest and not (path.parent / dest).exists():
                errors.append(f'Broken relative link in {path.relative_to(ROOT)}: {ref}')
    target = json.loads((ROOT / 'fixtures/target-routing.json').read_text())
    if len(target['assignments']) != 7 or target['assignments']['rfc-reviewer'] != 'review':
        errors.append('Wrong target role/route surface.')
    cases = json.loads((ROOT / 'fixtures/selection-cases.json').read_text())['cases']
    if len({c['id'] for c in cases}) != len(cases): errors.append('Duplicate selection cases.')
    for case in cases:
        if case['expected_path'] == 'deep' and not case['deep_reason']:
            errors.append('Deep case lacks concrete reason: ' + case['id'])
    for error in errors: print('ERROR ' + error)
    print(f'{len(rfcs)} RFC, {len(cards)} cards, {len(cases)} policy cases; {len(errors)} packet violations')
    return int(bool(errors))


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        print(f'ERROR {error}', file=sys.stderr)
        raise SystemExit(2)
