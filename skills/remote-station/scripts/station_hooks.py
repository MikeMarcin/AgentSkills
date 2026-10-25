#!/usr/bin/env python3
"""Inspect or remove only station guard commands from project hooks."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

SCHEMA = 'implement-rfc.station-hooks.v1'
# The guard moved from implement-rfc to remote-station; hooks written for
# either location are station commands.
GUARD_PATHS = ('remote-station/scripts/remote_station_guard.py',
               'implement-rfc/scripts/remote_station_guard.py')


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate hook configuration key: {key}')
        result[key] = value
    return result


def station_command(value):
    if not isinstance(value, dict) or value.get('type') != 'command':
        return False
    commands = [value[key] for key in ('command', 'command_windows') if key in value]
    owned = [isinstance(command, str) and
             any(guard in command.replace('\\', '/') for guard in GUARD_PATHS)
             for command in commands]
    if any(owned) and not all(owned):
        raise ValueError('station hook has an unrelated platform command; preserve it for manual review')
    return any(owned)


def linked(path):
    try:
        observed = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(observed.st_mode) or bool(
        getattr(observed, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))


def checkout_root(cwd):
    """The Git root of cwd; hook inspection needs no station configuration."""
    completed = subprocess.run(['git', '-C', str(cwd), 'rev-parse', '--show-toplevel'],
                               capture_output=True, text=True, check=False)
    return Path(completed.stdout.strip()) if completed.returncode == 0 else cwd


def inspect(root, *, off=False, dry_run=False):
    root = Path(root).resolve()
    directory = root / '.codex'
    path = directory / 'hooks.json'
    if linked(directory) or linked(path):
        raise ValueError('project hook configuration is linked; inspect its owner before editing')
    if not path.exists():
        return dict(schema=SCHEMA, path=str(path), station_commands=0,
                    would_change=False, changed=False, dry_run=dry_run)
    if not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ValueError('project hook configuration must be a regular file of at most 1 MiB')
    original = path.read_bytes()
    data = json.loads(original.decode('utf-8'), object_pairs_hook=_object)
    if not isinstance(data, dict) or not isinstance(data.get('hooks'), dict):
        raise ValueError('project hook configuration requires a hooks object')
    edited = copy.deepcopy(data)
    count = 0
    for event, groups in data['hooks'].items():
        if not isinstance(groups, list):
            raise ValueError(f'{event} hook groups must be an array')
        kept = []
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get('hooks'), list):
                raise ValueError(f'{event} hook group requires a hooks array')
            commands = group['hooks']
            removed = sum(station_command(command) for command in commands)
            count += removed
            if not removed:
                kept.append(group)
            else:
                remaining = [command for command in commands if not station_command(command)]
                if remaining:
                    kept.append(dict(group, hooks=remaining))
        if kept:
            edited['hooks'][event] = kept
        else:
            # Preserve originally empty event arrays too.
            if groups:
                edited['hooks'].pop(event)
    change = off and count > 0
    if change and not dry_run:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                             dir=directory, prefix='.station-hooks-', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(json.dumps(edited, indent=2, ensure_ascii=False) + '\n')
            os.chmod(temporary, path.stat().st_mode)
            if linked(directory) or linked(path) or path.read_bytes() != original:
                raise ValueError('project hooks changed during removal; inspect and retry')
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return dict(schema=SCHEMA, path=str(path), station_commands=count,
                would_change=change, changed=change and not dry_run, dry_run=dry_run,
                detail='Removing hooks does not stop a runtime or transfer station ownership.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('status', 'off'), nargs='?', default='status')
    parser.add_argument('--repo-root', type=Path, help='consumer checkout root; defaults to the Git root of the current directory')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = inspect(args.repo_root or checkout_root(Path.cwd()), off=args.operation == 'off', dry_run=args.dry_run)
        if args.json:
            print(json.dumps(dict(result, ok=True)))
        else:
            print(f"Station hook commands: {result['station_commands']} ({result['path']})")
            if result['would_change']:
                print('Would remove station hooks.' if args.dry_run else 'Removed station hooks. Reload project hooks in the host.')
            print('Removing hooks does not stop a runtime or transfer station ownership.')
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps(dict(schema=SCHEMA, ok=False, error=str(error))))
        return 75


if __name__ == '__main__':
    raise SystemExit(main())
