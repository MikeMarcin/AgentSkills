#!/usr/bin/env python3
"""Inspect an explicitly managed station or transfer it to owner-authorized local work."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import sys

import project_config
import remote_station_guard as guard
import station_lease
import codex_station
import station_lifecycle as lifecycle

SCHEMA = 'implement-rfc.station-control.v1'


def lease_role(station):
    return 'project-integrator' if station['workstream'] == 'main' else 'station-writer'


def manual_step(station):
    steps = []
    for runtime, endpoint in lifecycle.endpoints(station).items():
        steps.append(f'On the owning host, open {runtime} endpoint {endpoint}, stop its active turn and all terminal/background commands, and confirm its writer has stopped.')
    steps.append('Stop the station supervisor in its owning terminal (Ctrl+C) if its lease remains held.')
    steps.append('After observing those stops, rerun takeover --mode local --stop-previous --confirm-runtime-stopped.')
    return ' '.join(steps)


def _station(root, state):
    station = guard._load_station(root)
    if station is None:
        if state is not None:
            raise lifecycle.LifecycleError('Restore .remote-station.json from the recorded identity before station recovery.')
        return None
    guard._validate_live_checkout(root, station, project_config.resolve_context(repo_root=root).config)
    lifecycle.identity(root, station)
    if state is not None:
        lifecycle.validate(root, station, state)
    return station


def _owner_client(root, station):
    # Attach only to an existing managed owner. Never start a daemon, standalone
    # App Server, model turn or Desktop app to manufacture stop capability.
    if station.get('environment') not in ('macos', 'linux-native', 'wsl2'):
        raise lifecycle.LifecycleError('Existing managed owner proxy is unavailable on this host.')
    return codex_station.ProxyAppServerClient(cwd=root, context=project_config.resolve_context(repo_root=root),
                                              timeout=3, connect_timeout=1)


def runtime_activity(root, station):
    try:
        if not lifecycle.endpoints(station).get('codex'):
            return dict(state='no-codex-endpoint')
        with _owner_client(root, station) as client:
            observation = codex_station.station_activity(client, station)
        return dict(state='observed', codex=observation)
    except (codex_station.CodexStationError, lifecycle.LifecycleError, OSError) as error:
        return dict(state='unavailable', detail=str(error))


def runtime_stop(root, station, supervisor):
    proof = dict(kind='scoped-owner-stop', endpoints=lifecycle.endpoints(station),
                 writer_stopped=True, commands_stopped=True, observations={})
    if 'codex' in proof['endpoints']:
        with _owner_client(root, station) as client:
            proof['observations']['codex'] = codex_station.stop_station_turns(client, station)
    if 'claude' in proof['endpoints'] and supervisor.get('controlled_stop') is not True:
        raise lifecycle.LifecycleError('Claude stop is unproven: stop its recorded Remote Control session and commands on the owning host.')
    if 'claude' in proof['endpoints']:
        proof['observations']['claude'] = 'controlled-supervisor-process-group-stop'
    return proof


def status(root, *, observe_runtime=False):
    state = lifecycle.load(root)
    station = _station(root, state)
    if station is None:
        return dict(schema=SCHEMA, mode='unmanaged', endpoint=None, supervisor_lease=None,
                    activity={'state': 'unrestricted-local'}, recovery=None)
    observed = station_lease.snapshot(root, lease_role(station), project_config.resolve_context(repo_root=root))
    holder = observed.get('holder')
    if isinstance(holder, dict):
        holder = dict(holder)
        if isinstance(holder.get('control'), dict):
            holder['control'] = dict(holder['control'], token='[redacted]')
    mode = state['mode'] if state else 'managed'
    return dict(schema=SCHEMA, mode=mode, station_id=station['station_id'],
                generation=state['generation'] if state else 0, endpoint=lifecycle.endpoints(station),
                supervisor_lease=dict(observed, role=lease_role(station), holder=holder),
                activity=(runtime_activity(root, station) if observe_runtime and mode != 'local'
                          else dict(state='unknown' if mode != 'local' else 'retired',
                                    detail='Use status --observe-runtime for measured owner activity; lease metadata never proves runtime quiescence.')),
                recovery=dict(pending=state.get('transfer') if state else None,
                              runtime_stop_adapter=('existing-managed-proxy' if station.get('environment') in ('macos', 'linux-native', 'wsl2') else 'manual'), manual_step=manual_step(station)),
                retired=state['retired'] if state else [])


def takeover(root, *, stop_previous, confirm_runtime_stopped=False, runtime_stop_adapter=None):
    """An explicit human resume instruction authorizes this scoped stop and transfer."""
    if not stop_previous:
        raise lifecycle.LifecycleError('Local takeover requires --stop-previous under the human instruction to resume here.')
    context = project_config.resolve_context(repo_root=root)
    if context.mode == 'personal':
        raise lifecycle.LifecycleError('Station takeover does not support paired source/tracker identity; personal mode refused before writes.')
    with lifecycle.locked(root):
        state = lifecycle.load(root)
        station = _station(root, state)
        if station is None:
            return status(root)
        state = state or lifecycle.initial(root, station)
        if state['mode'] == 'local':
            return status(root)
        if state['mode'] != 'transferring':
            state['mode'] = 'transferring'
            state['transfer'] = dict(id=secrets.token_hex(16), target='local',
                                     from_generation=state['generation'], runtime_proof=None, supervisor_proof=None)
            for runtime, endpoint in state['endpoints'].items():
                state['retired'].append(dict(runtime=runtime, id=endpoint, generation=state['generation']))
            lifecycle.save(root, state)
        proof = state['transfer'].get('runtime_proof')
        if proof is None:
            if runtime_stop_adapter is not None:
                proof = runtime_stop_adapter(station)
                if (not isinstance(proof, dict) or proof.get('endpoints') != state['endpoints']
                        or proof.get('writer_stopped') is not True or proof.get('commands_stopped') is not True):
                    raise lifecycle.LifecycleError('Runtime adapter supplied no endpoint-bound writer and command stop proof. ' + manual_step(station))
            elif confirm_runtime_stopped:
                proof = dict(kind='human-observation', endpoints=state['endpoints'],
                             writer_stopped=True, commands_stopped=True)
            elif not state['endpoints']:
                proof = dict(kind='no-runtime-endpoint', endpoints={}, writer_stopped=True, commands_stopped=True)
            else:
                # Stop a trusted supervisor if possible, but its released lease alone
                # cannot stand in for an independently owned Desktop/runtime writer.
                supervisor = state['transfer'].get('supervisor_proof')
                if supervisor is None or supervisor.get('controlled_stop') is not True:
                    stopped = station_lease.stop_supervisor(root, lease_role(station), context, station['station'])
                    supervisor = dict(controlled_stop=stopped.get('controlled_stop') is True,
                                      endpoints=state['endpoints'], generation=state['generation'])
                    state['transfer']['supervisor_proof'] = supervisor
                    lifecycle.save(root, state)
                try:
                    proof = runtime_stop(root, station, supervisor)
                except (codex_station.CodexStationError, lifecycle.LifecycleError, OSError) as error:
                    raise lifecycle.LifecycleError(str(error) + ' ' + manual_step(station)) from error
            state['transfer']['runtime_proof'] = proof
            lifecycle.save(root, state)
        station_lease.stop_supervisor(root, lease_role(station), context, station['station'])
        # Holding the same OS lease closes the free-status/new-supervisor race.
        path = station_lease._lock_path(lease_role(station), root, context.config)
        fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        if not station_lease._try_lock(fd):
            os.close(fd)
            raise lifecycle.LifecycleError('Supervisor lease was reacquired; reconcile its owner and retry.')
        try:
            lifecycle.validate(root, guard._load_station(root), state)
            state['history'].append(dict(transfer=state['transfer'], result='local'))
            state['mode'] = 'local'
            state['generation'] += 1
            state['transfer'] = None
            lifecycle.save(root, state)
        finally:
            station_lease._unlock(fd)
            os.close(fd)
    return status(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('status', 'takeover'))
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--observe-runtime', action='store_true', help='measure activity through the existing owning proxy without starting a runtime')
    parser.add_argument('--mode', choices=('local',))
    parser.add_argument('--stop-previous', action='store_true')
    parser.add_argument('--confirm-runtime-stopped', action='store_true', help='record actual human observation after stopping the listed runtime writers and commands')
    args = parser.parse_args(argv)
    if args.operation == 'takeover' and args.observe_runtime:
        parser.error('--observe-runtime is a status option')
    if args.operation == 'takeover' and args.mode != 'local':
        parser.error('takeover requires --mode local')
    if args.operation == 'status' and (args.mode or args.stop_previous or args.confirm_runtime_stopped):
        parser.error('status accepts only --repo-root and --json')
    try:
        root = project_config.resolve_context(repo_root=args.repo_root).source_root
        value = status(root, observe_runtime=args.observe_runtime) if args.operation == 'status' else takeover(
            root, stop_previous=args.stop_previous, confirm_runtime_stopped=args.confirm_runtime_stopped)
        if args.json:
            print(json.dumps(dict(value, ok=True)))
        else:
            print(f"Station: {value.get('station_id', 'none')} ({value['mode']})")
            lease = value.get('supervisor_lease')
            if lease is not None:
                print('Supervisor lease: ' + ('held' if lease['held'] else 'free'))
            print('Runtime activity: ' + value['activity']['state'])
            if value['mode'] == 'managed':
                print('Use status --observe-runtime for measured activity; takeover only transfers ownership to a different chat.')
            if value['mode'] == 'transferring':
                print(value['recovery']['manual_step'])
        return 0
    except (ValueError, OSError, guard.GuardRefusal, project_config.ProjectConfigError) as error:
        print(json.dumps(dict(schema=SCHEMA, ok=False, error=str(error), writes='deferred')))
        return 75


if __name__ == '__main__':
    raise SystemExit(main())
