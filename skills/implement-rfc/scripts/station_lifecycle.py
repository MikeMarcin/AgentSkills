"""Durable checkout-scoped station generations and retired endpoint fencing."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import secrets
import stat

import project_config
import station_lease

SCHEMA = 'implement-rfc.station-lifecycle.v1'


class LifecycleError(ValueError):
    pass


def paths(root):
    gitdir = station_lease._git_dir('station-writer', root)
    return gitdir / 'implement-rfc-station-lifecycle.json', gitdir / 'implement-rfc-station-control.lock'


def _regular(path):
    if path.is_symlink() or (path.exists() and (not stat.S_ISREG(path.stat().st_mode) or path.stat().st_nlink != 1)):
        raise LifecycleError(f'Expected unlinked regular station state: {path}')


@contextmanager
def locked(root):
    _, path = paths(root)
    _regular(path)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    if not station_lease._try_lock(fd):
        os.close(fd)
        raise LifecycleError('Another station launch or takeover owns the transfer lock; retry after it finishes.')
    try:
        yield
    finally:
        station_lease._unlock(fd)
        os.close(fd)


def identity(root, station):
    context = project_config.resolve_context(repo_root=root)
    fields = ('station_id', 'station', 'project', 'branch', 'workstream')
    if station.get('schema') != 'implement-rfc.remote-station.v2' or any(not isinstance(station.get(k), str) or not station[k] for k in fields):
        raise LifecycleError('Station v2 identity is incomplete; preserve it and repair the recorded identity first.')
    if station['project'] != context.config['project']:
        raise LifecycleError('Station project differs from consumer context.')
    branch = project_config._git(root, 'branch', '--show-current')
    if branch != station['branch']:
        raise LifecycleError('Station branch differs from live checkout.')
    return dict(root=str(context.source_root), **{k: station[k] for k in fields})


def endpoints(station):
    result = {}
    for runtime, field in (('codex', 'thread_id'), ('claude', 'session_id')):
        value = station.get(runtime)
        if isinstance(value, dict) and isinstance(value.get(field), str) and value[field]:
            result[runtime] = value[field]
    return result


def load(root):
    path, _ = paths(root)
    _regular(path)
    if not path.exists():
        return None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        with os.fdopen(fd, 'r') as stream:
            observed = os.fstat(stream.fileno())
            if not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1 or observed.st_size > 2 * 1024 * 1024:
                raise LifecycleError('Station lifecycle must be a bounded unlinked regular file.')
            value = json.loads(stream.read(2 * 1024 * 1024 + 1))
    except (OSError, ValueError) as error:
        raise LifecycleError(f'Station lifecycle state is unreadable: {error}') from error
    if (not isinstance(value, dict) or value.get('schema') != SCHEMA
            or value.get('mode') not in ('managed', 'transferring', 'local')
            or type(value.get('generation')) is not int or value['generation'] < 1
            or not isinstance(value.get('identity'), dict)
            or set(value['identity']) != {'root', 'station_id', 'station', 'project', 'branch', 'workstream'}
            or value['identity'].get('root') != str(root.resolve())
            or not isinstance(value.get('endpoints'), dict)
            or any(runtime not in ('codex', 'claude') or not isinstance(endpoint, str) or not endpoint
                   for runtime, endpoint in value['endpoints'].items())
            or not isinstance(value.get('retired'), list)
            or not isinstance(value.get('history'), list)
            or (value['mode'] == 'transferring' and (not isinstance(value.get('transfer'), dict)
                 or value['transfer'].get('target') != 'local'
                 or value['transfer'].get('from_generation') != value['generation']))
            or not all(isinstance(item, dict) and item.get('runtime') in ('codex', 'claude')
                       and isinstance(item.get('id'), str) for item in value['retired'])):
        raise LifecycleError('Invalid station lifecycle state; preserve it for recovery.')
    return value


def validate(root, station, state):
    if state['identity'] != identity(root, station) or state['endpoints'] != endpoints(station):
        raise LifecycleError('Station registry differs from its durable lifecycle identity; restore the recorded registry before recovery.')


def initial(root, station):
    return dict(schema=SCHEMA, mode='managed', generation=1,
                identity=identity(root, station), endpoints=endpoints(station),
                retired=[], transfer=None, history=[])


def save(root, state):
    path, _ = paths(root)
    _regular(path)
    temporary = path.with_name(path.name + '.' + secrets.token_hex(8) + '.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(state, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def retired(state, session):
    return bool(state and any(item['id'] == session for item in state['retired']))


def activate(root, station):
    """Caller holds lifecycle lock and supervisor lease, after provisioning succeeds."""
    prior = load(root)
    state = initial(root, station)
    if prior:
        if prior['mode'] == 'transferring':
            raise LifecycleError('Finish the pending local takeover before launching another managed generation.')
        if prior['identity']['root'] != str(root.resolve()) or prior['identity']['project'] != station['project']:
            raise LifecycleError('Lifecycle belongs to another checkout or project.')
        state['generation'] = prior['generation'] + 1
        state['retired'] = prior['retired'][:]
        state['history'] = prior['history'][:]
        for runtime, endpoint in prior['endpoints'].items():
            if endpoint != state['endpoints'].get(runtime):
                state['retired'].append(dict(runtime=runtime, id=endpoint, generation=prior['generation']))
    if any(retired(state, endpoint) for endpoint in state['endpoints'].values()):
        raise LifecycleError('Provision a fresh runtime context: this endpoint was retired by local takeover.')
    save(root, state)
    return state
