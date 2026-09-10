#!/usr/bin/env python3
"""Validate this offline RFC packet, not a deployed implement-rfc runtime."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

from plan_contract import load_json, validate_plan, render, fingerprint


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ValueError(f'missing frontmatter: {path}')
    result = {}
    for line in lines[1:]:
        if line == '---':
            return result
        key, sep, raw = line.partition(':')
        if not sep or key in result:
            raise ValueError(f'invalid/duplicate frontmatter: {path}: {line}')
        result[key] = json.loads(raw.strip())
    raise ValueError(f'unterminated frontmatter: {path}')


def safe_member(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError(f'invalid packet path: {relative!r}')
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'escaped packet path: {relative}')
    for part in [path, *path.parents]:
        if part == root.parent:
            break
        if part.is_symlink():
            raise ValueError(f'linked packet path: {relative}')
    return path


def markdown_links(root: Path) -> list[str]:
    errors = []
    for path in root.rglob('*.md'):
        fence = None
        for line in path.read_text(encoding='utf-8').splitlines():
            match = re.match(r'^\s*(`{3,}|~{3,})', line)
            if match:
                marker = match.group(1)
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
                continue
            if fence:
                continue
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', line):
                if '://' in target or target.startswith(('#', 'mailto:')):
                    continue
                relative = unquote(target.split('#', 1)[0])
                if not relative:
                    continue
                resolved = (path.parent / relative).resolve()
                if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                    errors.append(f'broken/escaped link: {path.relative_to(root)} -> {target}')
    return errors


def check_packet(root: Path, *, check_manifest: bool = True) -> dict:
    errors = []
    index = load_json(root/'packet-index.json')
    refs = index['rfcs']; rows = index['issues']
    catalog = {'rfcs': [r['id'] for r in refs], 'issues': {r['id']: {'rfcs': r['rfcs']} for r in rows}}
    plan = load_json(safe_member(root, index['milestone_plan']))
    errors += validate_plan(plan, catalog)
    if errors:
        return {'ok': False, 'errors': errors}
    cards = {}
    for row in rows:
        path = safe_member(root, row['path'])
        card = frontmatter(path)
        cards[row['id']] = card
        for key in ('id', 'rfcs', 'depends_on'):
            if card.get(key) != row[key]:
                errors.append(f'card/index mismatch {row["id"]}: {key}')
        if card.get('schema') != 'implement-rfc.card.v1' or card.get('status') != 'Backlog':
            errors.append(f'unexpected proposed card schema/status: {row["id"]}')
        if card.get('metadata', {}).get('criterion_coverage') != row['criterion_coverage']:
            errors.append(f'card/index coverage mismatch: {row["id"]}')
    if len(cards) != len(rows):
        errors.append('duplicate issue ID in packet index')
    state = {}
    def visit(iid):
        if state.get(iid) == 1:
            errors.append('card dependency cycle'); return
        if state.get(iid) == 2:
            return
        state[iid] = 1
        for dep in cards[iid]['depends_on']:
            if dep not in cards:
                errors.append(f'missing packet prerequisite {dep}')
            else:
                visit(dep)
        state[iid] = 2
    for iid in cards:
        visit(iid)
    group_of = {w['issue']: m['id'] for m in plan['milestones'] for w in m['work']}
    groups = {m['id']: m for m in plan['milestones']}
    def ancestors(mid):
        found = set(); todo = list(groups[mid]['depends_on'])
        while todo:
            dep = todo.pop()
            if dep not in found:
                found.add(dep); todo.extend(groups[dep]['depends_on'])
        return found
    for iid, card in cards.items():
        for dep in card['depends_on']:
            if dep in group_of and group_of[dep] != group_of[iid] and group_of[dep] not in ancestors(group_of[iid]):
                errors.append(f'card/milestone prerequisite mismatch: {iid} -> {dep}')
    criteria = []
    for row in refs:
        path = safe_member(root, row['path'])
        data = frontmatter(path)
        if data.get('id') != row['id'] or data.get('status') != 'Proposed':
            errors.append(f'RFC identity/status mismatch: {row["id"]}')
        ac = re.findall(r'\*\*(' + re.escape(row['id']) + r'-AC\d+)\b', path.read_text())
        if not ac or len(ac) != len(set(ac)):
            errors.append('missing or duplicate RFC acceptance IDs')
        criteria.extend(ac)
        closers = [item for item in rows if row['id'] in cards[item['id']].get('closeout_for', [])]
        if len(closers) != 1:
            errors.append('each RFC needs exactly one closeout')
        else:
            close_text = safe_member(root, closers[0]['path']).read_text()
            if 'RFC_BASE_SHA: NOT_CAPTURED' not in close_text:
                errors.append('closeout must leave live baseline uncaptured')
            for criterion in ac:
                if f'| {criterion} |' not in close_text:
                    errors.append(f'missing closeout criterion {criterion}')
    named = {c for row in rows for c in row['criterion_coverage']}
    if named != set(criteria):
        errors.append('criterion coverage/index mismatch')
    expected_view = render(plan)
    if (root/'MILESTONES.md').read_text(encoding='utf-8') != expected_view:
        errors.append('MILESTONES.md differs from canonical plan')
    template = load_json(root/'authoring/milestone-plan.template.json')
    errors += ['template: '+x for x in validate_plan(template)]
    raw = load_json(root/'fixtures/raw-pack/milestone-plan.json')
    raw_cards = [frontmatter(p) for p in (root/'fixtures/raw-pack/issues').glob('*.md')]
    raw_catalog = {'rfcs': ['RFC-DEMO-0001'], 'issues': {c['id']: {'rfcs': c['rfcs']} for c in raw_cards}}
    errors += ['raw fixture: '+x for x in validate_plan(raw, raw_catalog)]
    errors += ['partial fixture: '+x for x in validate_plan(load_json(root/'fixtures/partial/milestone-plan.json'))]
    scenarios = load_json(root/'fixtures/scenarios.json')
    if scenarios.get('executed') is not False:
        errors.append('scenario declarations must not claim execution')
    if len({s['id'] for s in scenarios['cases']}) != len(scenarios['cases']):
        errors.append('duplicate scenario ID')
    for case in scenarios['cases']:
        if set(case) != {'id','input','setup','expected','evidence'} or not all(isinstance(v,str) and v.strip() for v in case.values()):
            errors.append('invalid scenario shape')
    errors += markdown_links(root)
    paths = [p for p in root.rglob('*') if p.is_file()]
    if any(p.is_symlink() or p.suffix == '.pyc' or '__pycache__' in p.parts or p.name == '.DS_Store' for p in paths):
        errors.append('linked/transient files must not be packaged')
    manifest_path = root/'PACK_MANIFEST.json'
    manifest_checked = check_manifest and manifest_path.exists()
    if manifest_checked:
        manifest = load_json(manifest_path)
        expected = set()
        for row in manifest['files']:
            relative = row['path']; expected.add(relative)
            path = safe_member(root, relative)
            raw_bytes = path.read_bytes()
            if len(raw_bytes) != row['bytes'] or hashlib.sha256(raw_bytes).hexdigest() != row['sha256']:
                errors.append(f'manifest mismatch: {relative}')
        actual = {p.relative_to(root).as_posix() for p in paths if p != manifest_path}
        if expected != actual:
            errors.append('manifest file set mismatch')
    return {'ok': not errors, 'rfcs': len(refs), 'cards': len(rows), 'milestones': len(plan['milestones']),
            'criteria': len(criteria), 'scenario_definitions': len(scenarios['cases']),
            'plan_fingerprint': fingerprint(plan), 'manifest_checked': manifest_checked,
            'errors': errors,
            'limitations': 'Offline artifact checks only; runtime feature, native qualification and quota savings are not established.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--plan', type=Path, help='Check a standalone authored plan instead of this packet.')
    parser.add_argument('--json', action='store_true', help='Emit one machine-readable JSON result.')
    args = parser.parse_args(argv)
    try:
        if args.plan:
            plan = load_json(args.plan)
            errors = validate_plan(plan)
            result = {'ok': not errors, 'errors': errors, 'limitations': 'Structural only; repository reference/acceptance checks have not run.'}
        else:
            result = check_packet(args.root.resolve())
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        result = {'ok': False, 'errors': [str(exc)]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result['ok']:
        print('Packet checks passed.' if not args.plan else 'Plan structure passed.')
        if 'rfcs' in result:
            print(f"{result['rfcs']} RFC · {result['cards']} cards · {result['milestones']} milestones · {result['criteria']} acceptance criteria")
            print(f"{result['scenario_definitions']} scenario definitions; no native model runs claimed.")
        print(result.get('limitations', ''))
    else:
        print('Validation failed:', file=sys.stderr)
        for error in result['errors']:
            print('  '+error, file=sys.stderr)
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
