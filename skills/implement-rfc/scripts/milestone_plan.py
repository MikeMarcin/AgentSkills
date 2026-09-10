#!/usr/bin/env python3
"""Discover, check and explicitly adopt authored plans; never execute pack code.

JSON inputs are limited to 1 MiB and plans to 256 milestones. Consumer roots are
explicit; source pointers are relative to --source-root (default: consumer).
Adoption is compare-before-write and retryable, not a multi-file transaction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import board_model
import project_config
from milestone_plan_contract import (load_json, normalize, validate_plan,
                                     remap_plan, render, fingerprint)


class PlanError(ValueError):
    def __init__(self, message, state='invalid'):
        super().__init__(message)
        self.state = state


def digest(value):
    return 'sha256:' + hashlib.sha256(json.dumps(value, sort_keys=True,
        ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def safe_path(root, relative):
    if (not isinstance(relative, str) or not relative or '\\' in relative
            or ':' in relative or any(p in ('', '.', '..') for p in relative.split('/'))
            or Path(relative).is_absolute()):
        raise PlanError(f'expected safe relative path: {relative!r}')
    path = board_model.safe_path(root, root / relative)
    if path.exists() and not path.is_file():
        raise PlanError(f'expected ordinary file: {relative}')
    return path


def load_plan(path):
    plan = load_json(Path(path))
    if isinstance(plan, dict) and plan.get('schema') != 'implement-rfc.milestone-plan.v1':
        raise PlanError('unsupported plan schema', 'unsupported-version')
    errors = validate_plan(plan)
    if errors:
        raise PlanError('; '.join(errors))
    view = Path(path).parent / 'MILESTONES.md'
    if view.exists():
        safe_path(Path(path).parent, 'MILESTONES.md')
        if view.stat().st_size > 1024 * 1024:
            raise PlanError('generated view exceeds 1 MiB')
        text = view.read_text()
        if 'Generated from `milestone-plan.json`' in text and text != render(plan):
            raise PlanError('generated MILESTONES.md has drifted', 'stale')
    return normalize(plan)


def documents(root, config):
    """Index only live top-level RFCs and configured issue lanes."""
    result = {}
    paths = list((root / config['rfc_root']).glob('RFC-*.md'))
    for lane in config['lanes'].values():
        paths.extend((root / config['issue_root'] / lane).glob('*.md'))
    for path in paths:
        safe_path(root, path.relative_to(root).as_posix())
        if path.stat().st_size > 1024 * 1024:
            raise PlanError(f'source exceeds 1 MiB: {path}')
        raw = path.read_bytes()
        matter = board_model.parse_matter(raw, path)
        identity = matter.values.get('id')
        if identity in result:
            raise PlanError(f'duplicate live reference: {identity}', 'ambiguous')
        result[identity] = (path, raw, matter)
    return result


def discover(root, config, *, source_root=None, plan=None, targets=()):
    source = Path(source_root or root).resolve()
    if plan is not None:
        return {'state': 'found', 'path': str(safe_path(source, plan)), 'origin': 'explicit'}
    docs = documents(root, config)
    links = set()
    for target in targets:
        if target not in docs:
            raise PlanError(f'unresolved target: {target}')
        path, raw, matter = docs[target]
        metadata = matter.values.get('metadata', {})
        if not isinstance(metadata, dict):
            raise PlanError(f'{target}: metadata must be an object')
        link = metadata.get('milestone_plan')
        if link:
            if not isinstance(link, dict) or set(link) != {'id', 'path'}:
                raise PlanError('invalid milestone_plan metadata')
            resolved = safe_path(root, link['path'])
            if load_plan(resolved)['id'] != link['id']:
                raise PlanError('live plan identity mismatch', 'ambiguous')
            links.add(str(resolved))
        if target.startswith('RFC-'):
            for pointer in re.findall(r'\[[^\]]*\]\(([^)]+milestone-plan\.json)\)', raw.decode()):
                # RFC links are relative to the RFC document, constrained to root.
                relative = (path.parent / pointer).relative_to(root).as_posix()
                links.add(str(safe_path(root, relative)))
    if len(links) > 1:
        raise PlanError('conflicting live plan candidates', 'ambiguous')
    if links:
        return {'state': 'found', 'path': links.pop(), 'origin': 'live'}
    pointers = set()
    for name in ('PACK_MANIFEST.json', 'packet-index.json'):
        path = safe_path(source, name)
        if path.exists():
            data = load_json(path)
            if not isinstance(data, dict):
                raise PlanError(f'{name}: expected object')
            if 'milestone_plan' in data:
                pointers.add(str(safe_path(source, data['milestone_plan'])))
    for name in ('README.md', 'IMPLEMENTATION_PROMPT.md'):
        path = safe_path(source, name)
        if path.exists():
            if path.stat().st_size > 1024 * 1024:
                raise PlanError(f'{name}: exceeds 1 MiB')
            for pointer in re.findall(r'\[[^\]]*\]\(([^)]+milestone-plan\.json)\)', path.read_text()):
                pointers.add(str(safe_path(source, pointer)))
    if len(pointers) > 1:
        raise PlanError('conflicting source plan candidates', 'ambiguous')
    if pointers:
        return {'state': 'found', 'path': pointers.pop(), 'origin': 'source-pointer'}
    conventional = safe_path(source, 'milestone-plan.json')
    if conventional.exists():
        return {'state': 'found', 'path': str(conventional), 'origin': 'root'}
    legacy = [str(safe_path(source, name)) for name in ('MILESTONES.md', 'IMPLEMENTATION_ORDER.md')
              if (source / name).exists()]
    if len(legacy) > 1:
        raise PlanError('multiple legacy plans need reconciliation', 'ambiguous')
    return {'state': 'needs-normalization', 'path': legacy[0]} if legacy else {'state': 'absent'}


def requirement_text(raw, matter):
    body = ''.join(matter.lines[matter.end + 1:])
    # Acceptance body includes headings and evidence requirements but excludes
    # mutable execution records; status and lane paths are never identities.
    match = re.search(r'^## (?:Acceptance|.*Acceptance.*|.*Verification and acceptance.*)\s*$', body, re.M | re.I)
    if match:
        body = body[match.start():]
        end = re.search(r'^## (?:Verification and execution record|Execution record|Risks.*)\s*$', body, re.M)
        if end:
            body = body[:end.start()]
    return body.strip()


def resolve_binding(repo_root, plan_path, milestone_id):
    ctx = project_config.resolve_context(repo_root=repo_root)
    root = ctx.repo_root
    path = safe_path(root, str(plan_path))
    plan = load_plan(path)
    milestones = {m['id']: m for m in plan['milestones']}
    if milestone_id not in milestones:
        raise PlanError(f'unknown milestone: {milestone_id}')
    milestone = milestones[milestone_id]
    docs = documents(root, ctx.config)
    catalog = {'rfcs': [i for i in docs if i.startswith('RFC-')],
               'issues': {i: row[2].values for i, row in docs.items() if not i.startswith('RFC-')}}
    errors = validate_plan(plan, catalog)
    obligations = []
    for ref in milestone['work']:
        source = ref.get('issue', ref.get('rfc'))
        if source not in docs:
            continue
        _, raw, matter = docs[source]
        body = requirement_text(raw, matter)
        for selector in ref.get('criteria', [None]):
            selected = body
            if selector is not None:
                label = (r'(?:' + re.escape(source) + r'-)?' if re.fullmatch(r'AC[0-9]+', selector) else '') + re.escape(selector)
                matches = list(re.finditer(r'(?<![\w-])' + label + r'(?![\w-])', body))
                if len(matches) != 1:
                    errors.append(f'{source}: missing or ambiguous criterion {selector}')
                    continue
                # Bind the complete source acceptance section: an adjacent
                # requirement amendment can change the selected obligation.
            obligations.append({'id': source + ':' + (selector or '*'), 'source': source,
                'selector': selector, 'source_fingerprint': digest(selected)})
    prerequisites = {}
    def collect(mid):
        for dep in milestones[mid]['depends_on']:
            if dep not in prerequisites:
                prerequisites[dep] = milestones[dep]
                collect(dep)
    collect(milestone_id)
    exits = [{'id': f'{milestone_id}:exit:{i+1}', 'text': text}
             for i, text in enumerate(milestone['exit_criteria'])]
    return {'plan_id': plan['id'], 'plan_path': str(plan_path), 'milestone_id': milestone_id,
        'definition_fingerprint': digest(milestone), 'obligations': obligations,
        'obligation_fingerprint': digest({'obligations': obligations, 'exit_criteria': exits}),
        'exit_criteria': exits, 'prerequisite_fingerprint': digest(prerequisites),
        'structural': 'valid', 'references': 'unresolved' if errors else 'resolved',
        'semantic_coverage': 'unknown', 'diagnostics': [e[:1024] for e in sorted(set(errors))[:32]],
        'diagnostics_truncated': len(set(errors)) > 32 or any(len(e) > 1024 for e in errors)}


def select_milestone(plan, accepted=()):
    """Accepted IDs are caller evidence facts, never inferred from card lanes."""
    known = {m['id'] for m in plan['milestones']}
    if set(accepted) - known:
        raise PlanError('accepted milestone IDs are not in this plan')
    return next((m for m in plan['milestones'] if m['id'] not in accepted
                 and set(m['depends_on']) <= set(accepted)), None)


def guarded_write(path, expected, new):
    current = path.read_bytes() if path.exists() else None
    if current != expected:
        raise PlanError(f'changed during adoption: {path}', 'stale')
    if current == new:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.milestone-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(new)
        if (path.read_bytes() if path.exists() else None) != expected:
            raise PlanError(f'changed during adoption: {path}', 'stale')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def adopt(root, config, source, mapping):
    if not isinstance(mapping, dict):
        raise PlanError('ID map must be an object')
    plan = remap_plan(load_plan(source), mapping)
    relative = f"{config['rfc_root']}/plans/{plan['id']}/milestone-plan.json"
    destination = safe_path(root, relative)
    existing = destination.read_bytes() if destination.exists() else None
    if existing is not None and load_plan(destination) != normalize(plan):
        raise PlanError('existing live plan conflicts with authored intent', 'ambiguous')
    docs = documents(root, config)
    catalog = {'rfcs': [i for i in docs if i.startswith('RFC-')],
               'issues': {i: row[2].values for i, row in docs.items() if not i.startswith('RFC-')}}
    errors = validate_plan(plan, catalog)
    if errors:
        raise PlanError('; '.join(errors))
    references = set(plan['scope'].get('issues', []) + plan['scope'].get('rfcs', []))
    for work in [m['work'] for m in plan['milestones']] + [plan.get('unplanned_work', [])]:
        references.update(r.get('issue', r.get('rfc')) for r in work)
    updates = []
    link = {'id': plan['id'], 'path': relative}
    for identity in sorted(references):
        if identity not in docs:
            raise PlanError(f'unresolved adoption reference: {identity}')
        path, raw, matter = docs[identity]
        metadata = matter.values.get('metadata', {})
        if not isinstance(metadata, dict):
            raise PlanError(f'{identity}: metadata must be an object')
        metadata = dict(metadata)
        if metadata.get('milestone_plan', link) != link:
            raise PlanError(f'conflicting linkage: {identity}', 'ambiguous')
        metadata['milestone_plan'] = link
        updates.append((path, raw, matter.updated({'metadata': metadata})))
    # Record immutable raw provenance separately, without extending plan schema.
    provenance = safe_path(root, str(destination.parent.relative_to(root) / 'source.json'))
    receipt = {'schema': 'implement-rfc.plan-source.v1', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'mapping': mapping, 'plan_path': relative}
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
    old_receipt = provenance.read_bytes() if provenance.exists() else None
    if old_receipt is not None and old_receipt != receipt_bytes:
        raise PlanError('source provenance conflicts', 'ambiguous')
    guarded_write(provenance, old_receipt, receipt_bytes)
    guarded_write(destination, existing, (json.dumps(normalize(plan), indent=2) + '\n').encode())
    for path, old, new in updates:
        guarded_write(path, old, new)
    return {'state': 'adopted', 'plan_id': plan['id'], 'plan_path': relative,
            'structural': 'valid', 'references': 'unchecked',
            'semantic_coverage': 'unknown', 'next': 'bind selected milestone to resolve criteria'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['discover', 'check', 'adopt', 'render', 'bind', 'inspect'])
    parser.add_argument('--repo-root', required=True)
    parser.add_argument('--source-root')
    parser.add_argument('--plan')
    parser.add_argument('--target', action='append', default=[])
    parser.add_argument('--milestone')
    parser.add_argument('--accepted-milestone', action='append', default=[],
                        help='previously accepted milestone ID (requires caller evidence)')
    parser.add_argument('--id-map', help='relative JSON ID map in source root')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        ctx = project_config.resolve_context(repo_root=args.repo_root)
        result = discover(ctx.repo_root, ctx.config, source_root=args.source_root,
                          plan=args.plan, targets=args.target)
        if result['state'] == 'found':
            path = Path(result['path'])
            plan = load_plan(path)
            result.update(plan_id=plan['id'], structural='valid', semantic_coverage='unknown',
                          milestone_ids=[m['id'] for m in plan['milestones']])
            if args.operation == 'adopt':
                mapping = load_json(safe_path(Path(args.source_root or ctx.repo_root).resolve(), args.id_map)) if args.id_map else {}
                result = adopt(ctx.repo_root, ctx.config, path, mapping)
            elif args.operation in ('bind', 'inspect'):
                selected = next((m for m in plan['milestones'] if m['id'] == args.milestone), None) if args.milestone else select_milestone(plan, args.accepted_milestone)
                if selected is None:
                    raise PlanError('no eligible milestone or unknown selected milestone', 'unresolved')
                result = resolve_binding(ctx.repo_root, path.relative_to(ctx.repo_root).as_posix(),
                                         selected['id'])
                result['work'] = selected['work']
            elif args.operation == 'render':
                view = render(plan)
                if not args.json:
                    print(view, end='')
                    return 0
                result['view'] = view
        elif args.operation != 'discover':
            raise PlanError('operation requires a structured plan', result['state'])
        print(json.dumps(result, ensure_ascii=False) if args.json else
              f"Plan: {result.get('plan_id', 'none')} — {result.get('state', result.get('references'))}; semantic coverage unknown")
        return 2 if result.get('references') == 'unresolved' else 0
    except (ValueError, OSError, TypeError, RecursionError) as exc:
        message = str(exc)
        result = {'state': getattr(exc, 'state', 'invalid'), 'diagnostic': message[:8192],
                  'truncated': len(message) > 8192}
        print(json.dumps(result) if args.json else f"Plan: {result['state']} — {exc}")
        return 2


if __name__ == '__main__':
    sys.exit(main())
