"""Invocation-owned project discovery and read-only MASK registry adapter.

No MASK internals are read. Registry entries are selection evidence, not a grant
of execution authority. This module never initializes/registers/updates a project.
"""
from __future__ import annotations

import json
import ntpath
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from usage_capture import Projects, git, ident, norm, within

MAX_MASK_BYTES = 8 * 1024 * 1024
MAX_PROJECTS = 4096


def infer_root(cwd: Path) -> Path:
    cwd = cwd.resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError('Invocation directory must exist')
    top = git(cwd, 'rev-parse', '--show-toplevel')
    boundary = Path(top).resolve() if top else None
    for candidate in (cwd, *cwd.parents):
        if (candidate / '.mask.json').is_file():
            return candidate
        if boundary is not None and candidate == boundary:
            return boundary
    raise ValueError('No project found from cwd; enter a Git project or pass --project LABEL=PATH')


def label_for(root: Path) -> str:
    # The declaration's project key is metadata only, never executable config.
    config = root / '.mask/skill-config/implement-rfc/project.json'
    name = root.name
    try:
        if config.is_file() and not config.is_symlink() and config.stat().st_size <= 65536:
            value = json.loads(config.read_bytes()).get('project')
            if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,60}', value):
                name = value
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return re.sub('[^A-Za-z0-9_-]', '-', name).strip('-')[:48] or 'project'


def validate_mask(document: object) -> list[dict]:
    if not isinstance(document, dict) or document.get('schema_version') != 1 or document.get('tool') != 'mask':
        raise ValueError('Unsupported MASK JSON envelope; expected schema_version=1, tool=mask')
    if document.get('command') != 'project.list' or document.get('ok') is not True or document.get('changed') is not False or document.get('error') is not None:
        raise ValueError('MASK project.list did not return a successful read-only result')
    data = document.get('data')
    rows = data.get('projects') if isinstance(data, dict) else None
    if not isinstance(rows, list) or len(rows) > MAX_PROJECTS:
        raise ValueError('MASK data.projects must be a bounded list')
    seen = set()
    result = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('root'), str) or not Path(row['root']).is_absolute():
            raise ValueError('MASK project row requires an absolute native root')
        if not isinstance(row.get('available'), bool):
            raise ValueError('MASK project row requires an available boolean')
        root = norm(row['root'])
        if root in seen:
            raise ValueError('Duplicate physical root in MASK project.list')
        seen.add(root)
        # Do not copy last_manifest, lock contents, sources, URLs or other registry data.
        identity = row.get('root_identity')
        if identity is not None:
            if not isinstance(identity, dict) or any(type(identity.get(k)) is not int or identity[k] < 0 for k in ('device', 'inode')):
                raise ValueError('Unrecognized MASK root identity')
            identity = {k: identity[k] for k in ('device', 'inode')}
        result.append({'root': root, 'available': row['available'], 'identity': identity})
    return result


def windows_launcher_argv(content: str) -> list[str]:
    """Recognize only MASK's exact v1 launcher; do not interpret batch syntax."""
    pattern = (r'@echo off\nrem MASK owned launcher v1\nsetlocal DisableDelayedExpansion\n'
               r'"([^"\r\n]+)" "([^"\r\n]+)" %\*\nexit /b %errorlevel%\n')
    match = re.fullmatch(pattern, content.replace('\r\n', '\n'))
    if not match:
        raise ValueError('Unrecognized MASK Windows launcher; use --mask-python-entrypoint')
    values = list(match.groups())
    for value in values:
        if not ntpath.isabs(value) or re.search(r'%(?!%)', value.replace('%%', '')):
            raise ValueError('Unrecognized path in MASK Windows launcher')
    values = [v.replace('%%', '%') for v in values]
    if ntpath.basename(values[1]).lower() != 'mask.py':
        raise ValueError('MASK launcher does not name mask.py')
    return [values[0], '-B', values[1]]


def mask_projects(*, executable: str = 'mask', python_entrypoint: Path | None = None,
                  home: Path | None = None, timeout: float = 30) -> tuple[list[dict], dict]:
    if python_entrypoint is not None:
        if not python_entrypoint.is_file():
            raise ValueError('--mask-python-entrypoint must name the installed mask.py')
        command = [sys.executable, '-B', str(python_entrypoint.resolve())]
    else:
        resolved = shutil.which(executable)
        if not resolved:
            raise ValueError('MASK was not found; supply --mask-executable or --mask-python-entrypoint')
        if os.name == 'nt' and Path(resolved).suffix.lower() in ('.cmd', '.bat'):
            launcher = Path(resolved)
            if launcher.stat().st_size > 65536:
                raise ValueError('MASK launcher is too large')
            command = windows_launcher_argv(launcher.read_text(encoding='utf-8'))
        else:
            command = [resolved]
    command += ['project', 'list', '--json']
    if home is not None:
        command += ['--home', str(home.expanduser().resolve())]
    # Output files avoid unbounded pipe capture; output size is checked before decoding.
    # Timeout bounds execution. No payload returned by MASK is executed.
    try:
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            proc = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                  timeout=timeout, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            size = out.tell()
            if proc.returncode:
                raise ValueError(f'MASK project.list failed (exit {proc.returncode}); no wider fallback was attempted')
            if size > MAX_MASK_BYTES:
                raise ValueError('MASK output exceeds the supported limit')
            out.seek(0)
            document = json.loads(out.read())
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith('MASK'):
            raise
        raise ValueError('MASK project.list failed or returned invalid JSON; no wider fallback was attempted') from None
    rows = validate_mask(document)
    return rows, {'source': 'mask project list --json', 'tool_version': str(document.get('tool_version', 'unknown'))[:60],
                  'registry_scope': 'local_machine_projects_only', 'registered_count': len(rows)}


class ScopedProjects(Projects):
    """Compatible parser scope with separate physical registrations and no implicit fan-out."""
    def __init__(self, entries: list[dict], aliases=(), include_worktrees=False):
        self.roots, self.primary, self.records = [], [], []
        used = set()
        expanded = list(entries)
        if include_worktrees:
            for entry in entries:
                root = Path(entry['root'])
                top = git(root, 'rev-parse', '--show-toplevel')
                if not top:
                    continue
                relative = root.relative_to(Path(top).resolve())
                for line in (git(root, 'worktree', 'list', '--porcelain') or '').splitlines():
                    if line.startswith('worktree '):
                        path = Path(line[9:]) / relative
                        if norm(path) not in {norm(e['root']) for e in expanded}:
                            expanded.append({'root': str(path), 'origin': 'explicit_worktree_expansion'})
        for entry in expanded:
            root = Path(entry['root']).expanduser().resolve()
            normalized = norm(root)
            if normalized in used:
                continue
            used.add(normalized)
            name = entry.get('label') or label_for(root)
            # Physical-root suffix disambiguates same project names and survives record order.
            label = name if entry.get('label') else name + '-' + ident(normalized)[:8]
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}', label):
                raise ValueError('Project labels must use letters, numbers, dash or underscore, max 60 chars')
            if label in {n for n, _ in self.primary}:
                raise ValueError('Different project roots require distinct labels')
            exists = root.is_dir()
            identity_state = 'not_supplied'
            registered = entry.get('identity')
            if registered is not None:
                try:
                    stat = root.stat()
                    identity_state = 'matched' if (stat.st_dev, stat.st_ino) == (registered['device'], registered['inode']) else 'mismatch'
                except OSError:
                    identity_state = 'unavailable'
            common = git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir') if exists and identity_state != 'mismatch' else None
            self.primary.append((label, root))
            # Unavailable roots still select retained historical logs; record that identity is unverified.
            # A reused root must not attribute the replacement checkout to an old registration.
            if identity_state != 'mismatch':
                self.roots.append((label, normalized))
            self.records.append({'label': label, 'physical_root_id': ident(normalized),
                                 'git_common_dir_group_id': ident(norm(common)) if common else None,
                                 'selection_origin': entry.get('origin', 'explicit'),
                                 'available_now': exists, 'registered_available': entry.get('available'),
                                 'identity_check': identity_state,
                                 'attribution': 'excluded_identity_mismatch' if identity_state == 'mismatch' else
                                     'historical_path_unverified' if not exists else 'physical_root'})
        for value in aliases:
            label, sep, path = value.partition('=')
            if not sep or label not in {n for n, _ in self.primary} or not Path(path).is_absolute():
                raise ValueError('--alias must be SELECTED_LABEL=OLD_ABSOLUTE_PATH')
            self.roots.append((label, norm(path)))
        owners = {}
        for label, root in self.roots:
            if root in owners and owners[root] != label:
                raise ValueError('Conflicting project aliases')
            owners[root] = label
        self.roots = sorted(set(self.roots), key=lambda p: len(p[1]), reverse=True)


def choose(args, cwd: Path) -> tuple[ScopedProjects, dict]:
    if args.mask_projects:
        if args.include_worktrees:
            raise ValueError('--mask-projects selects registered roots only; do not combine --include-worktrees')
        rows, provenance = mask_projects(executable=args.mask_executable,
            python_entrypoint=args.mask_python_entrypoint, home=args.mask_home)
        entries = [{**row, 'origin': 'mask_registered'} for row in rows]
    elif args.project:
        entries = []
        for value in args.project:
            label, sep, path = value.partition('=')
            if not sep or not Path(path).expanduser().is_dir():
                raise ValueError('--project requires LABEL=EXISTING_PATH')
            entries.append({'label': label, 'root': str(Path(path).expanduser().resolve()), 'origin': 'explicit'})
        provenance = {'source': 'explicit_project_selection'}
    else:
        root = infer_root(cwd)
        entries = [{'root': str(root), 'origin': 'invocation_cwd'}]
        provenance = {'source': 'invocation_cwd', 'script_location_used_for_scope': False}
    return ScopedProjects(entries, args.alias, args.include_worktrees), provenance
