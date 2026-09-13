#!/usr/bin/env python3
"""Explicit paired lane binding, reconciliation, and authorized handoff pushes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

import personal_state as state


def _path(source: Path) -> Path:
    home = state.home_for(source)
    state.ensure_home_separate(home, source)
    token = hashlib.sha256(str(source.absolute()).encode()).hexdigest()[:24]
    path = home / 'runtime' / state.binding_key(source) / 'pairs' / (token + '.json')
    state._check_local_path(home, path)
    return path


def _write(path: Path, data: dict, *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as stream:
        tmp = Path(stream.name)
        json.dump(data, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    try:
        if create:
            os.link(tmp, path)
        else:
            os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


class PairOccupiedError(state.PersonalStateError):
    """Another source lane already owns this tracker checkout."""


def _load_record(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
        if (not isinstance(data, dict) or set(data) != {'schema', 'portable', 'local'}
                or data['schema'] != 'implement-rfc.pair.v1'
                or not isinstance(data['local'], dict)
                or set(data['local']) != {'source_root', 'workflow_root'}
                or any(not isinstance(value, str) or not Path(value).is_absolute()
                       for value in data['local'].values())
                or not isinstance(data['portable'], dict)
                or set(data['portable']) != {'source', 'tracker'}):
            raise ValueError('invalid pair structure')
        for side in data['portable'].values():
            if (not isinstance(side, dict)
                    or set(side) != {'repository_id', 'branch', 'revision'}
                    or any(not isinstance(value, str) or not value for value in side.values())):
                raise ValueError('invalid portable identity')
        return data
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise state.PersonalStateError(f'invalid paired lane record: {path}') from exc


def _read(source: Path) -> dict | None:
    path = _path(source)
    return _load_record(path) if path.exists() else None


def _assert_available(source: Path, tracker: Path) -> None:
    home = state.home_for(source)
    # Inspect all common-repository bindings, including explicitly associated clones.
    for path in (home / 'runtime').glob('*/pairs/*.json'):
        if path.name.endswith('.sync.json'):
            continue
        state._check_local_path(home, path)
        other = _load_record(path)
        if path != _path(source) and Path(other['local']['workflow_root']).resolve() == tracker.resolve():
            raise PairOccupiedError('tracker worktree is already paired to another source lane')


def _identity(root: Path) -> dict:
    root = state.git_root(root)
    return {'repository_id': state.binding_key(root),
            'branch': state.git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD'),
            'revision': state.git(root, 'rev-parse', 'HEAD')}


def paired_root(source_root: Path, default_tracker: Path) -> Path:
    """Observational root lookup; validation is required before mutation."""
    record = _read(source_root)
    return Path(record['local']['workflow_root']) if record else default_tracker


def _current(record: dict, source: Path, tracker: Path, *, revisions: bool) -> dict:
    if record['local'] != {'source_root': str(source), 'workflow_root': str(tracker)}:
        raise state.PersonalStateError('paired checkout roots changed; explicit reconciliation required')
    actual = {'source': _identity(source), 'tracker': _identity(tracker)}
    for side in actual:
        before, now = record['portable'][side], actual[side]
        if any(before[key] != now[key] for key in ('repository_id', 'branch')):
            raise state.PersonalStateError(f'{side} repository or branch changed; explicit rebind required')
        if revisions and before['revision'] != now['revision']:
            try:
                state.git(source if side == 'source' else tracker, 'merge-base', '--is-ancestor',
                          before['revision'], now['revision'])
            except state.PersonalStateError as exc:
                raise state.PersonalStateError(f'{side} history rewritten; reconcile revision references first') from exc
    return {'portable': actual, 'local': record['local'], 'recorded': record['portable']}


def validate_pair(context) -> dict:
    if context.mode != 'personal':
        return {}
    source, tracker = Path(context.source_root), Path(context.workflow_root)
    binding = state.read_binding(state.home_for(source), source)
    if binding is None or state.common_dir(tracker) != Path(binding['tracker_common_dir']):
        raise state.PersonalStateError('tracker does not match source binding')
    record = _read(source)
    if record is None:
        raise state.PersonalStateError('source lane has no tracker pair; run personal_lanes.py bind')
    _assert_available(source, tracker)
    return _current(record, source, tracker, revisions=True)


def bind_pair(source_root: Path, tracker_root: Path | None = None,
              tracker_branch: str | None = None) -> dict:
    source = state.git_root(source_root)
    home = state.home_for(source)
    state.ensure_home_separate(home, source)
    lock = home / 'runtime' / 'pair-binding.lock'
    state._check_local_path(home, lock)
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise state.PersonalStateError('pair binding is locked; inspect interrupted operation before retry') from exc
    try:
        return _bind_pair(source, tracker_root, tracker_branch)
    finally:
        lock.rmdir()


def _bind_pair(source_root: Path, tracker_root: Path | None,
               tracker_branch: str | None) -> dict:
    source = state.git_root(source_root)
    binding = state.read_binding(state.home_for(source), source)
    if binding is None:
        raise state.PersonalStateError('initialize or explicitly associate this source repository first')
    existing = _read(source)
    if existing:
        tracker = Path(existing['local']['workflow_root'])
        if tracker_root is not None and state.git_root(tracker_root) != tracker:
            raise state.PersonalStateError('lane already paired to another worktree')
        _assert_available(source, tracker)
        result = _current(existing, source, tracker, revisions=True)
        if tracker_branch is not None and result['portable']['tracker']['branch'] != tracker_branch:
            raise state.PersonalStateError('lane already paired to another branch')
        return result
    primary = Path(binding['tracker_root'])
    if tracker_root is None and tracker_branch is not None:
        state.git(primary, 'check-ref-format', '--branch', tracker_branch)
        if tracker_branch == 'main':
            raise state.PersonalStateError('bind main explicitly; lane creation cannot allocate main')
        tracker = state.home_for(source) / 'worktrees' / state.binding_key(primary) / hashlib.sha256(tracker_branch.encode()).hexdigest()[:24]
        state._check_local_path(state.home_for(source), tracker)
        if tracker.exists():
            raise state.PersonalStateError('tracker worktree destination already exists')
        if state.git(primary, 'status', '--porcelain'):
            raise state.PersonalStateError('tracker must be clean before creating a lane')
        _assert_available(source, tracker)
        tracker.parent.mkdir(parents=True, exist_ok=True)
        state.git(primary, 'worktree', 'add', '-b', tracker_branch, str(tracker), 'main')
    else:
        tracker = state.git_root(tracker_root or primary)
    if state.common_dir(tracker) != Path(binding['tracker_common_dir']):
        raise state.PersonalStateError('tracker belongs to another repository')
    state.ensure_separate(source, tracker)
    _assert_available(source, tracker)
    record = {'schema': 'implement-rfc.pair.v1',
              'portable': {'source': _identity(source), 'tracker': _identity(tracker)},
              'local': {'source_root': str(source), 'workflow_root': str(tracker)}}
    _write(_path(source), record, create=True)
    return _current(record, source, tracker, revisions=True)


def reconcile_pair(context, expected_source_revision: str, expected_tracker_revision: str) -> dict:
    """Acknowledge explicit current revisions after caller reconciles evidence."""
    source, tracker = Path(context.source_root), Path(context.workflow_root)
    record = _read(source)
    if record is None:
        raise state.PersonalStateError('no pair to reconcile')
    result = _current(record, source, tracker, revisions=False)
    if (result['portable']['source']['revision'] != expected_source_revision
            or result['portable']['tracker']['revision'] != expected_tracker_revision):
        raise state.PersonalStateError('reconciliation revisions do not match current heads')
    _assert_available(source, tracker)
    record['portable'] = result['portable']
    _write(_path(source), record)
    return validate_pair(context)


def rebind_pair(context, expected_source_branch: str, expected_tracker_branch: str,
                expected_source_revision: str, expected_tracker_revision: str) -> dict:
    """Explicitly acknowledge a branch switch/rename on the same paired worktrees."""
    source, tracker = Path(context.source_root), Path(context.workflow_root)
    record = _read(source)
    if record is None or record['local'] != {'source_root': str(source), 'workflow_root': str(tracker)}:
        raise state.PersonalStateError('no matching checkout pair to rebind')
    actual = {'source': _identity(source), 'tracker': _identity(tracker)}
    for side in actual:
        if actual[side]['repository_id'] != record['portable'][side]['repository_id']:
            raise state.PersonalStateError('repository identity changed; rebind refused')
    if ((actual['source']['branch'], actual['tracker']['branch'],
         actual['source']['revision'], actual['tracker']['revision']) !=
        (expected_source_branch, expected_tracker_branch,
         expected_source_revision, expected_tracker_revision)):
        raise state.PersonalStateError('explicit rebind branches and revisions must match current state')
    _assert_available(source, tracker)
    record['portable'] = actual
    _write(_path(source), record)
    return validate_pair(context)


def assert_reservation_authority(context) -> None:
    pair = validate_pair(context)
    if pair and pair['portable']['tracker']['branch'] != 'main':
        raise state.PersonalStateError('reservations require tracker integrator on main')


def synchronize_pair(context, *, authorized: bool = False, source_remote: str | None = None,
                     tracker_remote: str | None = None, source_branch: str | None = None,
                     tracker_branch: str | None = None) -> dict:
    pair = validate_pair(context)
    if not pair:
        raise state.PersonalStateError('paired synchronization requires personal mode')
    if not source_remote and not tracker_remote:
        return {'status': 'local-only', 'pair': pair}
    if not authorized or not source_remote or not tracker_remote:
        raise state.PersonalStateError('both remote destinations and explicit push authorization required')
    roots = {'source': Path(context.source_root), 'tracker': Path(context.workflow_root)}
    remotes = {'source': source_remote, 'tracker': tracker_remote}
    branches = {'source': source_branch, 'tracker': tracker_branch}
    destinations = {}
    for side, root in roots.items():
        branch = pair['portable'][side]['branch']
        if branches[side] != branch:
            raise state.PersonalStateError('explicit synchronization branches must match paired branches')
        if remotes[side] not in state.git(root, 'remote').splitlines():
            raise state.PersonalStateError('synchronization requires an existing named remote')
        destinations[side] = state.git(root, 'remote', 'get-url', '--push', '--all', remotes[side])
        if len(destinations[side].splitlines()) != 1:
            raise state.PersonalStateError('synchronization requires exactly one push destination per repository')
    if destinations['source'] == destinations['tracker']:
        raise state.PersonalStateError('source and tracker require separate remote destinations')
    receipt = {'status': 'pending', 'portable': pair['portable'], 'completed': []}
    receipt_path = _path(Path(context.source_root)).with_suffix('.sync.json')
    _write(receipt_path, receipt)
    for side, root in roots.items():
        # Exact branch refspec, no force, no reset: rejection preserves both histories.
        try:
            state.git(root, 'push', remotes[side],
                      f"{pair['portable'][side]['revision']}:refs/heads/{branches[side]}")
        except state.PersonalStateError:
            receipt['status'] = 'pending-reconciliation'
            _write(receipt_path, receipt)
            raise
        receipt['completed'].append(side)
        _write(receipt_path, receipt)
    receipt['status'] = 'synchronized'
    _write(receipt_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('bind', 'status', 'reconcile', 'rebind', 'sync'))
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--tracker-root', type=Path)
    parser.add_argument('--tracker-branch')
    parser.add_argument('--source-branch')
    parser.add_argument('--source-revision')
    parser.add_argument('--tracker-revision')
    parser.add_argument('--source-remote')
    parser.add_argument('--tracker-remote')
    parser.add_argument('--authorize-push', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'bind':
            result = bind_pair(args.repo_root, args.tracker_root, args.tracker_branch)
        else:
            import project_config
            context = project_config.resolve_context(repo_root=args.repo_root, mode='personal')
            if args.command == 'status':
                result = validate_pair(context)
            elif args.command == 'rebind':
                result = rebind_pair(context, args.source_branch, args.tracker_branch,
                                     args.source_revision, args.tracker_revision)
            elif args.command == 'reconcile':
                result = reconcile_pair(context, args.source_revision, args.tracker_revision)
            else:
                result = synchronize_pair(context, authorized=args.authorize_push,
                    source_remote=args.source_remote, tracker_remote=args.tracker_remote,
                    source_branch=args.source_branch, tracker_branch=args.tracker_branch)
        print(json.dumps({'ok': True, **result}))
        return 0
    except (state.PersonalStateError, ValueError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
