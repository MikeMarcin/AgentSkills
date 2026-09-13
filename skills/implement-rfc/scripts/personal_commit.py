#!/usr/bin/env python3
"""Commit explicit product files and private acceptance with durable recovery."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid

import board_model
import issue_board
import personal_lanes as lanes
import personal_privacy as privacy
import personal_state as state
import project_config

SCHEMA = 'implement-rfc.personal-commit.v1'
FAILURES = ('before-source-commit', 'after-source-commit', 'after-source-receipt',
            'before-tracker-commit', 'after-tracker-commit', 'after-tracker-receipt')


def git(root: Path, *args: str, index: Path | None = None, data: bytes | None = None) -> bytes:
    env = project_config.git_environment()
    if index is not None:
        env['GIT_INDEX_FILE'] = str(index)
    result = subprocess.run(['git', '--literal-pathspecs', '-C', str(root), *args],
                            input=data, capture_output=True, env=env)
    if result.returncode:
        raise state.PersonalStateError(result.stderr.decode(errors='replace').strip())
    return result.stdout


def sync_directory(path: Path) -> None:
    if os.name != 'nt':
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def save(path: Path, receipt: dict) -> None:
    state._check_local_path(state.home_for(Path(receipt['pair']['local']['source_root'])), path)
    lanes._write(path, receipt)
    sync_directory(path.parent)


@contextmanager
def operation_lock(context):
    directory = context.runtime_root / 'product-commits'
    state._check_local_path(state.home_for(context.source_root), directory / 'lock')
    directory.mkdir(parents=True, exist_ok=True)
    sync_directory(directory.parent)
    # Kernel-held locks release on process death; receipt recovery needs no PID guessing.
    with (directory / 'lock').open('a+b') as stream:
        try:
            if os.name == 'nt':
                import msvcrt
                stream.seek(0)
                if not stream.read(1):
                    stream.write(b'0'); stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise state.PersonalStateError('another product operation is active') from exc
        try:
            yield directory
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def owned_paths(root: Path, paths: list[str]) -> list[str]:
    if not paths or len(set(paths)) != len(paths):
        raise state.PersonalStateError('supply distinct explicit product files')
    for relative in paths:
        path = Path(relative)
        if (path.is_absolute() or path.as_posix() != relative or '..' in path.parts
                or any(part.casefold().rstrip(' .') == '.git' for part in path.parts) or relative.startswith(':')
                or any(c in relative for c in '*?[\n\r\t\\') or relative == '.'):
            raise state.PersonalStateError('supply individual repository-relative files')
        current = root / path
        while current != root:
            if current.is_symlink():
                raise state.PersonalStateError('owned paths must not traverse symlinks')
            current = current.parent
        if (root / path).exists() and not (root / path).is_file():
            raise state.PersonalStateError('owned paths must be regular files or deletions')
        if git(root, 'ls-files', '--stage', '--', relative).startswith(b'160000 '):
            raise state.PersonalStateError('submodules need a separately reviewed commit path')
    return sorted(paths)


def claim(context, card_id: str):
    root, config = context.workflow_root, context.config
    cards = issue_board.require_valid(root, config,
        scope=lambda cs: board_model.dependency_scope(cs, {card_id}))
    card = cards.get(card_id)
    if card is None or card.lane != config['lanes']['in_progress']:
        raise state.PersonalStateError('begin requires an already committed In Progress claim')
    relative = card.path.relative_to(root).as_posix()
    if (git(root, 'status', '--porcelain', '--', relative)
            or git(root, 'show', f'HEAD:{relative}') != card.path.read_bytes()):
        raise state.PersonalStateError('private claim must be committed before source edits')
    return card


def begin(context, card_id: str, paths: list[str], directory: Path) -> dict:
    pair = lanes.validate_pair(context)
    privacy.validate_branch(context, pair['portable']['source']['branch'])
    card = claim(context, card_id)
    paths = owned_paths(context.source_root, paths)
    for relative in paths:
        privacy.validate_text(context, relative, 'product path')
    if git(context.source_root, 'status', '--porcelain', '--untracked-files=all', '--', *paths):
        raise state.PersonalStateError('owned product paths must be clean at begin, before editing')
    for other in directory.glob('*.json'):
        state._check_local_path(state.home_for(context.source_root), other)
        previous = json.loads(other.read_text())
        if (previous['status'] != 'complete' and
                previous['pair']['local']['source_root'] == str(context.source_root)):
            raise state.PersonalStateError('source lane has an unfinished product operation; resume it')
    token = uuid.uuid4().hex
    receipt = {'schema': SCHEMA, 'operation': token, 'status': 'editing',
               'pair': {'portable': pair['portable'], 'local': pair['local']},
               'id': card_id, 'paths': paths,
               'claim_path': card.path.relative_to(context.workflow_root).as_posix(),
               'claim_bytes': encode(card.path.read_bytes()), 'source': None, 'tracker': None}
    save(directory / (token + '.json'), receipt)
    return receipt


def encode(value: bytes | None) -> str | None:
    return base64.b64encode(value).decode() if value is not None else None


def decode(value: str | None) -> bytes | None:
    return base64.b64decode(value, validate=True) if value is not None else None


def head(root: Path) -> str:
    return git(root, 'rev-parse', 'HEAD').decode().strip()


def contributor_contract(root: Path) -> None:
    settings = git(root, 'config', '--null', '--list').decode().split('\0')
    signing = [item.partition('\n')[2] for item in settings
               if item.partition('\n')[0].casefold() == 'commit.gpgsign']
    if signing and signing[-1].casefold() not in ('false', 'no', 'off', '0'):
        raise state.PersonalStateError('required commit signing is unsupported; source remains pending')
    hooks = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks').decode().strip())
    for name in ('pre-commit', 'prepare-commit-msg', 'commit-msg', 'post-commit'):
        path = hooks / name
        if path.is_file() and (os.name == 'nt' or os.access(path, os.X_OK)):
            raise state.PersonalStateError('active commit hooks require a compatible commit adapter; source remains pending')


def check_pair(context, receipt: dict) -> dict:
    pair = lanes.validate_pair(context)
    if pair['local'] != receipt['pair']['local']:
        raise state.PersonalStateError('operation checkout pair changed')
    for side in ('source', 'tracker'):
        if any(pair['portable'][side][key] != receipt['pair']['portable'][side][key]
               for key in ('repository_id', 'branch')):
            raise state.PersonalStateError('operation branch or repository identity changed')
    privacy.validate_branch(context, pair['portable']['source']['branch'])
    return pair


@contextmanager
def temporary_index(directory: Path, root: Path, revision: str):
    with tempfile.TemporaryDirectory(prefix='index-', dir=directory) as name:
        path = Path(name) / 'index'
        git(root, 'read-tree', revision, index=path)
        yield path


def entries(root: Path, revision: str, paths: list[str]) -> bytes:
    # ls-tree's mode/type/hash rows become update-index stage-zero rows.
    output = []
    present = set()
    for row in git(root, 'ls-tree', '-z', revision, '--', *paths).split(b'\0'):
        if not row:
            continue
        metadata, name = row.split(b'\t', 1)
        mode, kind, oid = metadata.split()
        if kind != b'blob':
            raise state.PersonalStateError('commit scope contains a non-file entry')
        present.add(name.decode())
        output.append(mode + b' ' + oid + b' 0\t' + name + b'\0')
    zero = b'0' * len(revision)
    output.extend(b'0 ' + zero + b'\t' + p.encode() + b'\0' for p in paths if p not in present)
    return b''.join(output)


def create_commit(root: Path, parent: str, index: Path, message: str, *, tracker=False) -> dict:
    tree = git(root, 'write-tree', index=index).decode().strip()
    if tree == git(root, 'rev-parse', parent + '^{tree}').decode().strip():
        raise state.PersonalStateError('no selected changes to commit')
    identity = ('-c', 'user.name=implement-rfc', '-c', 'user.email=implement-rfc@localhost') if tracker else ()
    revision = git(root, *identity, 'commit-tree', tree, '-p', parent,
                   data=(message.rstrip() + '\n').encode()).decode().strip()
    return {'parent': parent, 'revision': revision, 'tree': tree, 'message': message.rstrip(),
            'recorded': False}


def adopted_commit(context, receipt: dict, revision: str) -> dict:
    root = context.source_root
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', revision) or head(root) != revision:
        raise state.PersonalStateError('adoption requires the exact current full source revision')
    parent = git(root, 'show', '-s', '--format=%P', revision).decode().strip()
    if parent != receipt['pair']['portable']['source']['revision']:
        raise state.PersonalStateError('adopted commit must have exactly the begin baseline as its parent')
    changed = git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', parent, revision)
    paths = {path.decode() for path in changed.split(b'\0') if path}
    if not paths or not paths.issubset(receipt['paths']):
        raise state.PersonalStateError('adopted commit contains no product changes or paths outside explicit ownership')
    message = git(root, 'show', '-s', '--format=%B', revision).decode().rstrip()
    privacy.validate_text(context, message, 'adopted commit message')
    for relative in receipt['paths']:
        privacy.validate_text(context, relative, 'product path')
        row = git(root, 'ls-tree', revision, '--', relative)
        if row:
            mode, kind, oid = row.split(b'\t')[0].split()
            if kind != b'blob' or mode not in (b'100644', b'100755'):
                raise state.PersonalStateError('adopted product entries must be regular files')
            privacy.validate_bytes(context, git(root, 'cat-file', 'blob', oid.decode()),
                                  'adopted product content')
    return {'parent': parent, 'revision': revision,
            'tree': git(root, 'rev-parse', revision + '^{tree}').decode().strip(),
            'message': message, 'recorded': True}


def prepare(context, receipt: dict, directory: Path, message: str | None, decision: dict,
            pr_text: str | None, adopted_revision: str | None = None) -> None:
    check_pair(context, receipt)
    source, tracker = context.source_root, context.workflow_root
    source_baseline = receipt['pair']['portable']['source']['revision']
    tracker_baseline = head(tracker)
    contributor_contract(tracker)
    if adopted_revision is None and head(source) != source_baseline:
        raise state.PersonalStateError('source advanced after begin; reconcile rather than guessing a base')
    card = claim(context, receipt['id'])
    if encode(card.path.read_bytes()) != receipt['claim_bytes']:
        raise state.PersonalStateError('private claim changed after begin')
    if pr_text is not None:
        privacy.validate_text(context, pr_text, 'proposed PR text')
    paths = owned_paths(source, receipt['paths'])
    if adopted_revision is not None:
        product = adopted_commit(context, receipt, adopted_revision)
    else:
        contributor_contract(source)
        if not message or not message.strip():
            raise state.PersonalStateError('supply an ordinary product commit message')
        privacy.validate_text(context, message, 'commit message')
        if git(source, 'diff', '--cached', '--name-only', '--', *paths):
            raise state.PersonalStateError('owned paths must be unstaged; preserve staged work before finish')
        with temporary_index(directory, source, source_baseline) as index:
            git(source, 'add', '--all', '--', *paths, index=index)
            for relative in paths:
                privacy.validate_text(context, relative, 'product path')
                row = git(source, 'ls-files', '--stage', '--', relative, index=index)
                if row:
                    oid = row.split()[1].decode()
                    privacy.validate_bytes(context, git(source, 'cat-file', 'blob', oid),
                                          'product content')
            product = create_commit(source, source_baseline, index, message)
    records = decision.get('records')
    if (decision.get('approved') is not True or decision.get('decision') not in ('done', 'human-pending')
            or not isinstance(records, list) or not records or any(not isinstance(r, dict) for r in records)):
        raise state.PersonalStateError('supply approved done or human-pending acceptance records')
    records = [dict(record, revision=product['revision']) for record in records]
    if board_model.schema_errors(dict(card.fields, acceptance=records), card.path, context.config):
        raise state.PersonalStateError('invalid acceptance criterion/outcome/evidence records')
    if decision['decision'] == 'done' and any(r['outcome'] != 'pass' for r in records):
        raise state.PersonalStateError('Done requires all supplied criteria passing')
    # Local paths belong only in this receipt; evidence committed to the tracker is portable.
    local_paths = [*receipt['pair']['local'].values(), str(context.runtime_root),
                   str(state.home_for(source)), str(state.common_dir(source)), str(state.common_dir(tracker))]
    def strings(value):
        if isinstance(value, str):
            yield value.casefold().replace('\\', '/')
        elif isinstance(value, dict):
            for item in value.values():
                yield from strings(item)
        elif isinstance(value, list):
            for item in value:
                yield from strings(item)
    if any(path.casefold().replace('\\', '/') in text for text in strings(records) for path in local_paths):
        raise state.PersonalStateError('tracker acceptance must use portable evidence, not local checkout/runtime paths')
    lane = context.config['lanes']['done' if decision['decision'] == 'done' else 'parked']
    changes, originals = issue_board.plan_move(tracker, context.config, receipt['id'], lane,
        'human-review' if decision['decision'] == 'human-pending' else None, None)
    destination = card.path.parent.parent / lane / card.path.name
    changes[destination] = board_model.parse_matter(changes.get(destination, card.path.read_bytes()),
                                                   destination).updated({'acceptance': records})
    originals.setdefault(destination, destination.read_bytes() if destination.exists() else None)
    tracker_paths = sorted(path.relative_to(tracker).as_posix() for path in changes)
    if git(tracker, 'status', '--porcelain', '--', *tracker_paths):
        raise state.PersonalStateError('tracker completion paths have uncommitted edits')
    with temporary_index(directory, tracker, tracker_baseline) as index:
        for path, content in changes.items():
            relative = path.relative_to(tracker).as_posix()
            if content is None:
                git(tracker, 'update-index', '--force-remove', '--', relative, index=index)
            else:
                oid = git(tracker, 'hash-object', '-w', '--stdin', data=content).decode().strip()
                git(tracker, 'update-index', '--add', '--cacheinfo', '100644', oid, relative, index=index)
        completion = create_commit(tracker, tracker_baseline, index, 'Record acceptance for ' + receipt['id'], tracker=True)
    completion.update(paths=tracker_paths,
        originals={p.relative_to(tracker).as_posix(): encode(originals[p]) for p in changes},
        changes={p.relative_to(tracker).as_posix(): encode(v) for p, v in changes.items()})
    receipt.update(source=product, tracker=completion, status='prepared',
                   proposal={'message': message, 'acceptance': decision, 'pr_text': pr_text,
                             'adopted_revision': adopted_revision})


def inject(selected: str | None, point: str) -> None:
    if selected == point:
        raise state.PersonalStateError('injected failure: ' + point)


def advance(root: Path, operation: dict, branch: str) -> None:
    actual = head(root)
    if actual == operation['revision']:
        return
    if actual != operation['parent'] or operation['recorded']:
        raise state.PersonalStateError('ambiguous recovery: branch differs from the recorded parent and commit')
    git(root, 'update-ref', '-m', 'commit: ' + operation['message'].splitlines()[0],
        'refs/heads/' + branch, operation['revision'], operation['parent'])


def sync_index(root: Path, operation: dict, paths: list[str], directory: Path) -> None:
    if head(root) != operation['revision']:
        raise state.PersonalStateError('HEAD changed before index reconciliation; preserve concurrent work')
    index_path = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    if index_path.is_symlink():
        raise state.PersonalStateError('Git index is redirected by a symlink; reconciliation refused')
    lock_path = index_path.with_name(index_path.name + '.lock')
    try:
        descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise state.PersonalStateError('Git index is locked; preserve it and resume after its owner ends') from exc
    try:
        with os.fdopen(descriptor, 'wb') as lock_stream:
            with tempfile.TemporaryDirectory(prefix='sync-index-', dir=directory) as name:
                index = Path(name) / 'index'
                if index_path.exists():
                    shutil.copyfile(index_path, index)
                else:
                    git(root, 'read-tree', operation['parent'], index=index)
                for relative in paths:
                    current = git(root, 'ls-files', '--stage', '-z', '--', relative, index=index)
                    allowed = []
                    for revision in (operation['parent'], operation['revision']):
                        value = entries(root, revision, [relative])
                        allowed.append(b'' if value.startswith(b'0 ') else value)
                    if current not in allowed:
                        raise state.PersonalStateError('owned index entry changed; preserve staged work and reconcile')
                git(root, 'update-index', '-z', '--index-info', index=index,
                    data=entries(root, operation['revision'], paths))
                lock_stream.write(index.read_bytes())
                lock_stream.flush()
                os.fsync(lock_stream.fileno())
        os.replace(lock_path, index_path)
        sync_directory(index_path.parent)
    finally:
        lock_path.unlink(missing_ok=True)


def sync_tracker_files(root: Path, operation: dict) -> None:
    changes, originals = {}, {}
    for relative, encoded in operation['changes'].items():
        path = board_model.safe_path(root, root / relative)
        wanted, before = decode(encoded), decode(operation['originals'][relative])
        actual = path.read_bytes() if path.exists() else None
        if actual == wanted:
            continue
        if actual != before:
            raise state.PersonalStateError('tracker completion path changed; preserve edits and reconcile')
        changes[path], originals[path] = wanted, before
    issue_board.apply_changes(changes, originals)


def tree_content(root: Path, revision: str, relative: str) -> bytes | None:
    rows = git(root, 'ls-tree', '-z', revision, '--', relative).split(b'\0')
    if rows == [b'']:
        return None
    if len(rows) != 2:
        raise state.PersonalStateError('tracker receipt path does not name one committed file')
    metadata, name = rows[0].split(b'\t', 1)
    mode, kind, oid = metadata.split()
    if name.decode() != relative or kind != b'blob' or mode not in (b'100644', b'100755'):
        raise state.PersonalStateError('tracker receipt contains a non-regular committed entry')
    return git(root, 'cat-file', 'blob', oid.decode())


def validate_payloads(context, receipt: dict) -> None:
    """The Git objects authenticate recovery bytes; local receipt text is not authority."""
    tracker = receipt['tracker']
    paths = tracker['paths']
    if (not isinstance(paths, list) or len(paths) != len(set(paths))
            or set(paths) != set(tracker['changes']) or not set(paths).issubset(tracker['originals'])):
        raise state.PersonalStateError('tracker receipt payload paths disagree')
    for relative in paths:
        board_model.safe_path(context.workflow_root, context.workflow_root / relative)
        for field, revision in (('changes', tracker['revision']), ('originals', tracker['parent'])):
            if decode(tracker[field][relative]) != tree_content(context.workflow_root, revision, relative):
                raise state.PersonalStateError('tracker receipt payload differs from its committed tree')
    for side, root, allowed in (('source', context.source_root, receipt['paths']),
                                ('tracker', context.workflow_root, paths)):
        operation = receipt[side]
        changed = git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z',
                      operation['parent'], operation['revision'])
        actual = {path.decode() for path in changed.split(b'\0') if path}
        if not actual or not actual.issubset(allowed):
            raise state.PersonalStateError('prepared commit changes paths outside its explicit receipt scope')


def verify_synchronized(context, receipt: dict) -> None:
    for side, root, paths in (('source', context.source_root, receipt['paths']),
                              ('tracker', context.workflow_root, receipt['tracker']['paths'])):
        operation = receipt[side]
        if head(root) != operation['revision']:
            raise state.PersonalStateError('HEAD changed before completion verification')
        for relative in paths:
            expected = entries(root, operation['revision'], [relative])
            if expected.startswith(b'0 '):
                expected = b''
            if git(root, 'ls-files', '--stage', '-z', '--', relative) != expected:
                raise state.PersonalStateError('owned index differs from the prepared commit after synchronization')
            if side == 'tracker':
                path = board_model.safe_path(root, root / relative)
                actual = path.read_bytes() if path.exists() else None
                if actual != tree_content(root, operation['revision'], relative):
                    raise state.PersonalStateError('tracker worktree differs from the prepared commit after synchronization')
        if side == 'tracker' and git(root, 'diff', '--no-ext-diff', '--no-textconv', '--raw',
                                     operation['revision'], '--', *paths):
            raise state.PersonalStateError('tracker worktree metadata differs from the prepared commit after synchronization')


def resume(context, receipt: dict, path: Path, failure: str | None = None) -> dict:
    check_pair(context, receipt)
    if receipt['status'] == 'editing':
        return receipt
    validate_payloads(context, receipt)
    if receipt['status'] == 'complete':
        for side, root in (('source', context.source_root), ('tracker', context.workflow_root)):
            git(root, 'merge-base', '--is-ancestor', receipt[side]['revision'], 'HEAD')
        return receipt
    # Refuse both unexpected heads before creating any further effect.
    for side, root in (('source', context.source_root), ('tracker', context.workflow_root)):
        if head(root) not in (receipt[side]['parent'], receipt[side]['revision']):
            raise state.PersonalStateError('ambiguous recovery: unexpected ' + side + ' history')
        if head(root) == receipt[side]['parent']:
            contributor_contract(root)
    source = receipt['source']
    inject(failure, 'before-source-commit')
    advance(context.source_root, source, receipt['pair']['portable']['source']['branch'])
    inject(failure, 'after-source-commit')
    source['recorded'] = True
    receipt['status'] = 'source-committed'
    save(path, receipt)
    sync_index(context.source_root, source, receipt['paths'], path.parent)
    inject(failure, 'after-source-receipt')
    tracker = receipt['tracker']
    # Validate all tracker bytes before the ref effect; no completion on an attempted write.
    for relative, encoded in tracker['changes'].items():
        candidate = board_model.safe_path(context.workflow_root, context.workflow_root / relative)
        actual = candidate.read_bytes() if candidate.exists() else None
        if actual not in (decode(encoded), decode(tracker['originals'][relative])):
            raise state.PersonalStateError('tracker completion path changed; preserve edits and reconcile')
    inject(failure, 'before-tracker-commit')
    advance(context.workflow_root, tracker, receipt['pair']['portable']['tracker']['branch'])
    inject(failure, 'after-tracker-commit')
    tracker['recorded'] = True
    receipt['status'] = 'tracker-committed'
    save(path, receipt)
    inject(failure, 'after-tracker-receipt')
    sync_tracker_files(context.workflow_root, tracker)
    sync_index(context.workflow_root, tracker, tracker['paths'], path.parent)
    verify_synchronized(context, receipt)
    receipt['status'] = 'complete'
    save(path, receipt)
    return receipt


def load(directory: Path, token: str, context) -> tuple[Path, dict]:
    if not re.fullmatch('[0-9a-f]{32}', token):
        raise state.PersonalStateError('invalid operation token')
    path = directory / (token + '.json')
    state._check_local_path(state.home_for(context.source_root), path)
    receipt = json.loads(path.read_text())
    if (not isinstance(receipt, dict) or receipt.get('schema') != SCHEMA
            or receipt.get('operation') != token
            or receipt.get('status') not in ('editing', 'prepared', 'source-committed', 'tracker-committed', 'complete')):
        raise state.PersonalStateError('invalid product operation receipt')
    check_pair(context, receipt)
    if receipt['status'] != 'editing':
        for side, root in (('source', context.source_root), ('tracker', context.workflow_root)):
            operation = receipt[side]
            if (not isinstance(operation, dict)
                    or any(not isinstance(operation.get(key), str) for key in ('parent', 'revision', 'tree', 'message'))
                    or not isinstance(operation.get('recorded'), bool)):
                raise state.PersonalStateError('invalid prepared commit in receipt')
            actual = git(root, 'show', '-s', '--format=%P%n%T%n%B', operation['revision']).decode().rstrip()
            expected = operation['parent'] + '\n' + operation['tree'] + '\n' + operation['message'].rstrip()
            if actual != expected:
                raise state.PersonalStateError('prepared commit no longer matches receipt identity')
        validate_payloads(context, receipt)
    return path, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    start = commands.add_parser('begin', help='Record committed claim and clean owned paths before editing')
    start.add_argument('--id', required=True)
    start.add_argument('--paths', required=True, nargs='+')
    finish = commands.add_parser('finish', help='Prepare and commit product plus approved private acceptance')
    finish.add_argument('--message', required=True)
    adopt = commands.add_parser('adopt', help='Adopt an exact normal Git commit made after begin; complete tracker only')
    adopt.add_argument('--source-revision', required=True)
    for command in (finish, adopt):
        command.add_argument('--acceptance', required=True, type=Path)
        command.add_argument('--pr-text', type=Path)
    recover = commands.add_parser('resume', help='Reconcile exact durable commits; never guess or reset')
    status = commands.add_parser('status', help='Read the operation without mutation')
    for command in (finish, adopt, recover, status):
        command.add_argument('--operation', required=True)
    for command in (finish, adopt, recover):
        command.add_argument('--inject-failure', choices=FAILURES, help=argparse.SUPPRESS)
    validate = commands.add_parser('validate-text', help='Check proposed source branch, message and PR text')
    validate.add_argument('--branch')
    validate.add_argument('--message')
    validate.add_argument('--pr-text', type=Path)
    args = parser.parse_args()
    try:
        context = project_config.resolve_context(repo_root=args.repo_root, mode='personal')
        if args.command == 'validate-text':
            lanes.validate_pair(context)
            if args.branch is not None:
                privacy.validate_branch(context, args.branch)
            if args.message is not None:
                privacy.validate_text(context, args.message, 'commit message')
            if args.pr_text is not None:
                privacy.validate_text(context, args.pr_text.read_text(), 'proposed PR text')
            result = {'valid': True}
        elif args.command == 'status':
            _, result = load(context.runtime_root / 'product-commits', args.operation, context)
        else:
            with operation_lock(context) as directory:
                if args.command == 'begin':
                    result = begin(context, args.id, args.paths, directory)
                else:
                    path, receipt = load(directory, args.operation, context)
                    if args.command in ('finish', 'adopt'):
                        decision = json.loads(args.acceptance.read_text())
                        pr_text = args.pr_text.read_text() if args.pr_text else None
                        message = args.message if args.command == 'finish' else None
                        adopted_revision = args.source_revision if args.command == 'adopt' else None
                        proposal = {'message': message, 'acceptance': decision, 'pr_text': pr_text,
                                    'adopted_revision': adopted_revision}
                        if receipt['status'] == 'editing':
                            prepare(context, receipt, directory, message, decision, pr_text, adopted_revision)
                            save(path, receipt)
                        elif receipt.get('proposal') != proposal:
                            raise state.PersonalStateError('finish proposal differs from durable receipt; inspect status and use resume')
                    result = resume(context, receipt, path, args.inject_failure)
        print(json.dumps({'ok': True, **result}))
        return 0
    except (state.PersonalStateError, project_config.ProjectConfigError, board_model.BoardError,
            ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
