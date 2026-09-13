#!/usr/bin/env python3
"""Explicit paired lane binding, reconciliation, and authorized handoff pushes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import uuid
from pathlib import Path
import tempfile

import personal_state as state


def _lane_token(source: Path) -> str:
    return hashlib.sha256(str(source.absolute()).encode()).hexdigest()[:24]


def _path(source: Path) -> Path:
    home = state.home_for(source)
    state.ensure_home_separate(home, source)
    token = _lane_token(source)
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


def _private_branch_guard(source: Path, tracker: Path) -> None:
    from types import SimpleNamespace
    import personal_privacy
    import project_config
    context = SimpleNamespace(source_root=source, workflow_root=tracker,
        runtime_root=state.home_for(source) / 'runtime' / state.binding_key(source),
        config=project_config.load(tracker / project_config.CONTEXT_DIR / 'project.json'))
    personal_privacy.validate_branch(context, _identity(source)['branch'])


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
        _private_branch_guard(source, tracker)
        if tracker_root is not None and state.git_root(tracker_root) != tracker:
            raise state.PersonalStateError('lane already paired to another worktree')
        _assert_available(source, tracker)
        result = _current(existing, source, tracker, revisions=True)
        if tracker_branch is not None and result['portable']['tracker']['branch'] != tracker_branch:
            raise state.PersonalStateError('lane already paired to another branch')
        return result
    primary = Path(binding['tracker_root'])
    _private_branch_guard(source, primary)
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
    _private_branch_guard(source, tracker)
    _assert_available(source, tracker)
    record = {'schema': 'implement-rfc.pair.v1',
              'portable': {'source': _identity(source), 'tracker': _identity(tracker)},
              'local': {'source_root': str(source), 'workflow_root': str(tracker)}}
    _write(_path(source), record, create=True)
    return _current(record, source, tracker, revisions=True)


def _check_reconciled_references(source: Path, tracker: Path, old_revision: str,
                                 new_revision: str, side: str = 'source') -> None:
    if old_revision == new_revision:
        return
    try:
        state.git(source, 'merge-base', '--is-ancestor', old_revision, new_revision)
        return
    except state.PersonalStateError:
        pass
    if state.git(tracker, 'status', '--porcelain', '--untracked-files=all'):
        raise state.PersonalStateError('commit reconciled tracker records before acknowledging rewritten history')
    # Retired commits from either repository can appear in evidence or handoffs.
    retired = state.git(source, 'rev-list', old_revision, '--not', new_revision).splitlines()
    for filename in state.git(tracker, 'ls-tree', '-r', '--name-only', 'HEAD').splitlines():
        content = state.git(tracker, 'show', 'HEAD:' + filename)
        references = re.findall(r'(?<![0-9a-f])[0-9a-f]{7,64}(?![0-9a-f])', content)
        if any(revision.startswith(reference) for revision in retired for reference in references):
            raise state.PersonalStateError(f'stale {side} revision reference in tracked tracker record: ' + filename)


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
    _check_reconciled_references(source, tracker, record['portable']['source']['revision'],
                                 result['portable']['source']['revision'])
    _check_reconciled_references(tracker, tracker, record['portable']['tracker']['revision'],
                                 result['portable']['tracker']['revision'], 'tracker')
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
    _private_branch_guard(source, tracker)
    for side in actual:
        if actual[side]['repository_id'] != record['portable'][side]['repository_id']:
            raise state.PersonalStateError('repository identity changed; rebind refused')
    if ((actual['source']['branch'], actual['tracker']['branch'],
         actual['source']['revision'], actual['tracker']['revision']) !=
        (expected_source_branch, expected_tracker_branch,
         expected_source_revision, expected_tracker_revision)):
        raise state.PersonalStateError('explicit rebind branches and revisions must match current state')
    _assert_available(source, tracker)
    _check_reconciled_references(source, tracker, record['portable']['source']['revision'],
                                 actual['source']['revision'])
    _check_reconciled_references(tracker, tracker, record['portable']['tracker']['revision'],
                                 actual['tracker']['revision'], 'tracker')
    record['portable'] = actual
    _write(_path(source), record)
    return validate_pair(context)


def release_pair(source_repository_root: Path, pair_record: Path, expected_pair: dict,
                 *, remove_source: bool = False, remove_tracker: bool = False,
                 task_owned_source: bool = False, task_owned_tracker: bool = False) -> dict:
    from types import SimpleNamespace
    from personal_commit import operation_lock
    anchor = state.git_root(source_repository_root)
    home = state.home_for(anchor)
    state.ensure_home_separate(home, anchor)
    context = SimpleNamespace(source_root=anchor,
        runtime_root=home / 'runtime' / state.binding_key(anchor))
    # Serialize receipt inspection/removal with product start, finish and recovery.
    with operation_lock(context):
        return _release_pair(anchor, pair_record, expected_pair, remove_source=remove_source,
            remove_tracker=remove_tracker, task_owned_source=task_owned_source,
            task_owned_tracker=task_owned_tracker)


def _release_pair(source_repository_root: Path, pair_record: Path, expected_pair: dict,
                 *, remove_source: bool = False, remove_tracker: bool = False,
                 task_owned_source: bool = False, task_owned_tracker: bool = False) -> dict:
    """Release an integrated pair; optional removal requires explicit task ownership."""
    anchor = state.git_root(source_repository_root)
    home = state.home_for(anchor)
    directory = home / 'runtime' / state.binding_key(anchor) / 'pairs'
    pair_record = pair_record.absolute()
    state._check_local_path(home, pair_record)
    if pair_record.parent != directory or pair_record.name.endswith('.sync.json'):
        raise state.PersonalStateError('release record must belong to the selected source repository')
    lock = home / 'runtime' / 'pair-binding.lock'
    state._check_local_path(home, lock)
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise state.PersonalStateError('pair binding is locked') from exc
    try:
        record = _load_record(pair_record)
        canonical = directory / (_lane_token(Path(record['local']['source_root'])) + '.json')
        if pair_record != canonical:
            raise state.PersonalStateError('release requires the canonical pair-record path')
        if expected_pair != record['portable']:
            raise state.PersonalStateError('release requires exact recorded pair identities and revisions')
        binding = state.read_binding(home, anchor)
        if binding is None:
            raise state.PersonalStateError('missing source binding')
        roots = {'source': anchor, 'tracker': Path(binding['tracker_root'])}
        remove = {'source': remove_source, 'tracker': remove_tracker}
        owned = {'source': task_owned_source, 'tracker': task_owned_tracker}
        for side, root in roots.items():
            identity = record['portable'][side]
            checkout = Path(record['local']['source_root' if side == 'source' else 'workflow_root'])
            if state.binding_key(root) != identity['repository_id']:
                raise state.PersonalStateError('release repository identity mismatch')
            if state.git(root, 'rev-parse', 'refs/heads/' + identity['branch']) != identity['revision']:
                raise state.PersonalStateError('release branch revision changed; reconcile pair first')
            state.git(root, 'merge-base', '--is-ancestor', identity['revision'], 'refs/heads/main')
            if checkout.exists():
                if _identity(checkout) != identity:
                    raise state.PersonalStateError('release checkout identity changed')
                if state.git(checkout, 'status', '--porcelain', '--untracked-files=all', '--ignored'):
                    raise state.PersonalStateError('release requires clean worktrees')
                if remove[side] and (not owned[side] or state.common_dir(checkout) == checkout / '.git'
                                     or checkout == anchor):
                    raise state.PersonalStateError('removal requires an explicitly task-owned secondary worktree')
            elif remove[side]:
                raise state.PersonalStateError('worktree already removed; release without removal flags')
        for receipt_path in (home / 'runtime').glob('*/product-commits/*.json'):
            state._check_local_path(home, receipt_path)
            try:
                receipt = json.loads(receipt_path.read_text())
                if (not isinstance(receipt, dict) or receipt.get('schema') != 'implement-rfc.personal-commit.v1'
                        or receipt.get('status') not in {'editing', 'prepared', 'source-committed', 'tracker-committed', 'complete'}
                        or 'pair' not in receipt):
                    raise ValueError('invalid receipt')
                if receipt['pair']['local'] == record['local'] and receipt['status'] != 'complete':
                    raise state.PersonalStateError('pending product receipt prevents release')
            except (ValueError, KeyError, TypeError) as exc:
                raise state.PersonalStateError('pending or invalid product receipt prevents release') from exc
        sync = pair_record.with_suffix('.sync.json')
        state._check_local_path(home, sync)
        if sync.exists():
            try:
                sync_receipt = json.loads(sync.read_text())
                if not isinstance(sync_receipt, dict) or sync_receipt.get('status') != 'synchronized':
                    raise ValueError('pending synchronization')
            except (ValueError, OSError) as exc:
                raise state.PersonalStateError('pending or invalid synchronization prevents release') from exc
        # All checks precede effects. Git refuses changed/locked worktrees without force.
        for side, root in roots.items():
            if remove[side]:
                checkout = record['local']['source_root' if side == 'source' else 'workflow_root']
                state.git(root, 'worktree', 'remove', checkout)
        archive = directory.parent / 'released-pairs' / pair_record.name
        state._check_local_path(home, archive)
        archive.parent.mkdir(parents=True, exist_ok=True)
        if archive.exists():
            archive = archive.with_name(archive.stem + '-' + uuid.uuid4().hex + '.json')
        _write(archive, record, create=True)
        pair_record.unlink()
        return {'status': 'released', 'portable': record['portable']}
    finally:
        lock.rmdir()


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
    # This receipt is machine-local. Carry both checkout roots and exact paired
    # revisions across a Git synchronization handoff without recording URLs that
    # might contain credentials.
    receipt = {'status': 'pending', 'portable': pair['portable'],
               'local': pair['local'], 'remote_names': remotes,
               'branches': branches, 'completed': []}
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
    parser.add_argument('command', choices=('bind', 'status', 'reconcile', 'rebind', 'sync', 'release'))
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--tracker-root', type=Path)
    parser.add_argument('--tracker-branch')
    parser.add_argument('--source-branch')
    parser.add_argument('--source-revision')
    parser.add_argument('--tracker-revision')
    parser.add_argument('--source-remote')
    parser.add_argument('--tracker-remote')
    parser.add_argument('--authorize-push', action='store_true')
    parser.add_argument('--pair-record', type=Path)
    parser.add_argument('--expected-pair', type=Path, help='JSON containing exact portable pair identities')
    parser.add_argument('--remove-source', action='store_true')
    parser.add_argument('--remove-tracker', action='store_true')
    parser.add_argument('--task-owned-source', action='store_true')
    parser.add_argument('--task-owned-tracker', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'release':
            if args.pair_record is None or args.expected_pair is None:
                raise state.PersonalStateError('release requires --pair-record and --expected-pair')
            result = release_pair(args.repo_root, args.pair_record, json.loads(args.expected_pair.read_text()),
                remove_source=args.remove_source, remove_tracker=args.remove_tracker,
                task_owned_source=args.task_owned_source, task_owned_tracker=args.task_owned_tracker)
        elif args.command == 'bind':
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
