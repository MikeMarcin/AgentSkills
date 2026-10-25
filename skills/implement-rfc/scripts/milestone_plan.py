#!/usr/bin/env python3
"""Discover, check and explicitly adopt authored plans; never execute pack code.

JSON inputs are limited to 1 MiB and plans to 256 milestones. Consumer roots are
explicit; source pointers are relative to --source-root (default: consumer).
Adoption is compare-before-write and retryable, not a multi-file transaction.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
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
        text = view.read_text(encoding='utf-8')
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


def plan_references(plan):
    refs = set(plan['scope'].get('issues', []) + plan['scope'].get('rfcs', []))
    for work in [m['work'] for m in plan['milestones']] + [plan.get('unplanned_work', [])]:
        refs.update(r.get('issue', r.get('rfc')) for r in work)
    return refs


def require_live_linkage(root, path, plan, docs):
    """A published definition is not ready until every scoped link is durable."""
    expected = {'id': plan['id'], 'path': path.relative_to(root).as_posix()}
    missing = []
    for identity in sorted(plan_references(plan)):
        if identity not in docs:
            missing.append(identity)
            continue
        document, raw, matter = docs[identity]
        metadata = matter.values.get('metadata', {})
        linked = isinstance(metadata, dict) and metadata.get('milestone_plan') == expected
        if not linked and identity.startswith('RFC-'):
            for pointer in re.findall(r'\[[^\]]*\]\(([^)]+milestone-plan\.json)\)', raw.decode()):
                candidate = document.parent / pointer
                relative = candidate.relative_to(root).as_posix()
                if safe_path(root, relative) == path:
                    linked = True
        if not linked:
            missing.append(identity)
    if missing:
        raise PlanError('incomplete adoption at ' + expected['path'] + ': missing linkage for '
            + ', '.join(missing[:16]) + '; retry adopt with the original --source-root and --id-map; '
            'the existing source receipt and live plan will be preserved', 'stale')


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
    # Bounded live-directory lookup recovers target-only resume even when an
    # interrupted adoption has published no document metadata yet.
    if targets:
        live_paths = list(itertools.islice((root / config['rfc_root'] / 'plans').glob('*/milestone-plan.json'), 257))
        if len(live_paths) > 256:
            if not links:
                raise PlanError('live plan lookup exceeds 256 plans; select --plan explicitly')
            # Adopted linkage remains authoritative; only unlinked recovery needs
            # the bounded directory scan. Full linkage is checked below.
            live_paths = []
        for candidate in live_paths:
            candidate = safe_path(root, candidate.relative_to(root).as_posix())
            live = load_plan(candidate)
            if set(targets) & plan_references(live):
                links.add(str(candidate))
    if len(links) > 1:
        raise PlanError('conflicting live plan candidates', 'ambiguous')
    if links:
        path = Path(links.pop())
        require_live_linkage(root, path, load_plan(path), docs)
        return {'state': 'found', 'path': str(path), 'origin': 'live'}
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


def project_work(milestone, projection):
    if projection is None:
        return milestone['work']
    probe = {'schema': 'implement-rfc.milestone-plan.v1', 'id': 'projection',
             'scope': {'rfcs': ['RFC-CHECK-1']},
             'milestones': [dict(milestone, work=projection, depends_on=[])]}
    # Validate reference syntax and overlap using the common contract.
    errors = validate_plan(probe)
    if errors:
        raise PlanError('; '.join(errors))
    selected = []
    for original in milestone['work']:
        kind = 'issue' if 'issue' in original else 'rfc'
        matches = [r for r in projection if r.get(kind) == original[kind]]
        for ref in matches:
            if 'criteria' in original and ('criteria' not in ref or
                    not set(ref['criteria']) <= set(original['criteria'])):
                continue
            selected.append(dict(ref, criteria=[c for c in original['criteria'] if c in ref['criteria']])
                            if 'criteria' in original else ref)
    if len(selected) != len(projection):
        raise PlanError('projection must select only work in the current milestone')
    return selected


def planning_observations(root, config, plan, work):
    docs = documents(root, config)
    selected = {r['issue'] for r in work if 'issue' in r}
    pending = list(sorted(selected))
    rows = {}
    while pending:
        identity = pending.pop(0)
        if identity in rows:
            continue
        values = docs[identity][2].values if identity in docs else {}
        deps = values.get('depends_on', [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            raise PlanError(f'{identity}: invalid dependencies')
        rows[identity] = {'id': identity, 'status': values.get('status', 'unknown'),
            'depends_on': deps, 'excluded_prerequisites': [d for d in deps if d not in selected],
            'unresolved_prerequisites': [d for d in deps if d not in docs or
                docs[d][2].values.get('status') != 'Done'],
            'external_depends_on': values.get('external_depends_on', [])}
        pending.extend(d for d in deps if d not in rows)
    return {'issues': list(rows.values()), 'unplanned_work': plan.get('unplanned_work', []),
            'acceptance': 'unknown'}


def check_amendment(before, after, reason, source_basis):
    if not reason or not reason.strip() or not source_basis or not source_basis.strip():
        raise PlanError('amendment requires a reason and source basis')
    if before['id'] != after['id'] or before['scope'] != after['scope']:
        raise PlanError('amendment cannot change plan identity or authorized scope')
    def atoms(plan):
        return {(r.get('issue', r.get('rfc')), c)
                for refs in [m['work'] for m in plan['milestones']] + [plan.get('unplanned_work', [])]
                for r in refs for c in r.get('criteria', ['*'])}
    if atoms(before) != atoms(after):
        raise PlanError('amendment must preserve every obligation; reconcile changed requirements separately')
    old_exits = {e for m in before['milestones'] for e in m['exit_criteria']}
    new_exits = {e for m in after['milestones'] for e in m['exit_criteria']}
    if not old_exits <= new_exits:
        raise PlanError('amendment must preserve all exit criteria, including pending decisions')
    old = {m['id']: m for m in before['milestones']}
    new = {m['id']: m for m in after['milestones']}
    return {'state': 'amendment-checked', 'reason': reason, 'source_basis': source_basis,
            'before_fingerprint': fingerprint(before), 'after_fingerprint': fingerprint(after),
            'affected_milestones': sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k)),
            'semantic_coverage': 'unknown', 'next': 'reconcile affected assignments before publication'}


def resolve_binding(repo_root, plan_path, milestone_id, projection=None):
    ctx = project_config.resolve_context(repo_root=repo_root)
    if ctx.mode == 'personal':
        import personal_lanes
        personal_lanes.validate_pair(ctx)
    root = ctx.workflow_root
    path = safe_path(root, str(plan_path))
    plan = load_plan(path)
    milestones = {m['id']: m for m in plan['milestones']}
    if milestone_id not in milestones:
        raise PlanError(f'unknown milestone: {milestone_id}')
    milestone = milestones[milestone_id]
    docs = documents(root, ctx.config)
    require_live_linkage(root, path, plan, docs)
    catalog = {'rfcs': [i for i in docs if i.startswith('RFC-')],
               'issues': {i: row[2].values for i, row in docs.items() if not i.startswith('RFC-')}}
    errors = validate_plan(plan, catalog)
    obligations = []
    work = project_work(milestone, projection)
    for ref in work:
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
    result = {'plan_id': plan['id'], 'plan_path': str(plan_path), 'milestone_id': milestone_id,
        'definition_fingerprint': digest(milestone), 'obligations': obligations,
        'obligation_fingerprint': digest({'obligations': obligations, 'exit_criteria': exits}),
        'exit_criteria': exits, 'prerequisite_fingerprint': digest(prerequisites),
        'structural': 'valid', 'references': 'unresolved' if errors else 'resolved',
        'semantic_coverage': 'unknown', 'diagnostics': [e[:1024] for e in sorted(set(errors))[:32]],
        'diagnostics_truncated': len(set(errors)) > 32 or any(len(e) > 1024 for e in errors)}
    if projection is not None:
        result['projection'] = work
    return result


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
    provenance = safe_path(root, (destination.parent.relative_to(root) / 'source.json').as_posix())
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
    parser.add_argument('operation', choices=['discover', 'check', 'adopt', 'render', 'bind', 'inspect', 'prepare', 'check-amendment'])
    parser.add_argument('--repo-root', required=True)
    parser.add_argument('--mode', choices=('project', 'personal'))
    parser.add_argument('--workflow-root')
    parser.add_argument('--source-root')
    parser.add_argument('--plan')
    parser.add_argument('--target', action='append', default=[])
    parser.add_argument('--milestone')
    parser.add_argument('--projection', help='consumer-relative JSON selected work list')
    parser.add_argument('--proposal', help='source-relative engineer-authored plan JSON')
    parser.add_argument('--reason')
    parser.add_argument('--source-basis')
    parser.add_argument('--accepted-milestone', action='append', default=[],
                        help='previously accepted milestone ID (requires caller evidence)')
    parser.add_argument('--id-map', help='relative JSON ID map in source root')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        ctx = project_config.resolve_context(repo_root=args.repo_root, mode=args.mode,
                                             workflow_root=args.workflow_root)
        root = ctx.workflow_root
        if ctx.mode == 'personal' and args.operation == 'adopt':
            import personal_lanes
            personal_lanes.assert_reservation_authority(ctx)
        result = discover(root, ctx.config, source_root=args.source_root,
                          plan=args.plan, targets=args.target)
        if args.operation in ('prepare', 'check-amendment'):
            if not args.proposal:
                raise PlanError('preparation/amendment requires an engineer-authored --proposal')
            source = Path(args.source_root or root).resolve()
            proposal = load_plan(safe_path(source, args.proposal))
            if result['state'] == 'found':
                result = check_amendment(load_plan(Path(result['path'])), proposal, args.reason, args.source_basis)
            elif args.operation == 'check-amendment':
                raise PlanError('amendment requires an existing structured plan')
            else:
                evidence = None
                if result['state'] == 'needs-normalization':
                    legacy = Path(result['path'])
                    if legacy.stat().st_size > 1024 * 1024:
                        raise PlanError('legacy source exceeds 1 MiB')
                    raw = legacy.read_bytes()
                    evidence = {'path': legacy.relative_to(source).as_posix(),
                        'sha256': hashlib.sha256(raw).hexdigest(), 'text': raw.decode('utf-8')}
                if not set(args.target) <= plan_references(proposal):
                    raise PlanError('proposal omits selected targets')
                result = {'state': 'prepared', 'origin': result['state'], 'source_evidence': evidence,
                    'plan': proposal, 'semantic_coverage': 'unknown',
                    'next': 'engineer reconciles intent, retains this receipt, adopts and implements'}
            print(json.dumps(result) if args.json else f"Plan: {proposal['id']} — {result['state']}; semantic coverage unknown")
            return 0
        if result['state'] == 'found':
            path = Path(result['path'])
            plan = load_plan(path)
            result.update(plan_id=plan['id'], structural='valid', semantic_coverage='unknown',
                          milestone_ids=[m['id'] for m in plan['milestones']])
            if args.operation == 'adopt':
                mapping = load_json(safe_path(Path(args.source_root or root).resolve(), args.id_map)) if args.id_map else {}
                result = adopt(root, ctx.config, path, mapping)
            elif args.operation in ('bind', 'inspect'):
                selected = next((m for m in plan['milestones'] if m['id'] == args.milestone), None) if args.milestone else select_milestone(plan, args.accepted_milestone)
                if selected is None:
                    raise PlanError('no eligible milestone or unknown selected milestone', 'unresolved')
                result = resolve_binding(ctx.source_root, path.relative_to(root).as_posix(),
                                         selected['id'], load_json(safe_path(root, args.projection)) if args.projection else None)
                result['work'] = result.get('projection', selected['work'])
                if args.operation == 'inspect':
                    result['planning'] = planning_observations(root, ctx.config, plan, result['work'])
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
