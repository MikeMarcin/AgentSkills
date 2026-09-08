#!/usr/bin/env python3
"""Create an attachment-ready, metadata-only Claude/Codex usage ZIP.

With no scope options, infer the project from the invoking working directory.
--mask-projects selects every local MASK project registration, not user scope,
remote hosts, or all history on this machine. No model calls or network calls
are made; the separate usage_quota.py explicitly opts into native quota reads.
Python 3.11+, standard library, Git for Git-project inference.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
import uuid
import zipfile

# Running through a MASK link may import from a read-only content-addressed store.
sys.dont_write_bytecode = True
from usage_capture import Collector, VERSION, UTC, boundary, digest, dt, inventory
from usage_scope import choose


def state_root() -> Path:
    if sys.platform == 'win32':
        root = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local')))
    elif sys.platform == 'darwin':
        root = Path.home() / 'Library/Application Support'
    else:
        root = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state')))
    return root / 'implement-rfc/usage'


def write_json(root: Path, name: str, value: object) -> None:
    (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def write_array(root, name, rows):
    count = 0
    with (root / name).open('w', encoding='utf-8') as stream:
        stream.write('[')
        for row in rows:
            if count:
                stream.write(',')
            json.dump(row, stream, sort_keys=True)
            count += 1
        stream.write(']\n')
    return count


def sha_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def publish(root: Path, target: Path) -> None:
    """Construct before publishing; exclusive target open never removes someone else's file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as stage:
        with zipfile.ZipFile(stage, 'w', zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(root.iterdir()):
                if item.is_file() and not item.is_symlink():
                    archive.write(item, item.name)
        stage.seek(0)
        # Deliberately outside try: FileExistsError must not trigger cleanup of an existing archive.
        output = target.open('xb')
        try:
            with output:
                shutil.copyfileobj(stage, output, length=1024*1024)
                output.flush()
                os.fsync(output.fileno())
        except BaseException:
            # Cooperative-writer guarantee, not protection against hostile replacement by same user.
            target.unlink(missing_ok=True)
            raise


def parse(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    scopes = parser.add_mutually_exclusive_group()
    scopes.add_argument('--project', action='append', help='LABEL=PATH; repeat for explicit projects')
    scopes.add_argument('--mask-projects', action='store_true', help='All projects registered with local MASK')
    parser.add_argument('--mask-executable', default='mask', help='Installed MASK executable (not a shell command)')
    parser.add_argument('--mask-python-entrypoint', type=Path, help='Direct installed mask.py; useful on Windows')
    parser.add_argument('--mask-home', type=Path, help='Forward public MASK --home; otherwise respect MASK_HOME')
    parser.add_argument('--include-worktrees', action='store_true', help='Explicitly expand cwd/--project scope to linked worktrees')
    parser.add_argument('--alias', action='append', default=[], help='SELECTED_LABEL=OLD_ABSOLUTE_PATH')
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--since', type=boundary, help='YYYY-MM-DD means UTC; timestamps require timezone')
    parser.add_argument('--until', type=boundary)
    parser.add_argument('--machine', default='local', help='Non-sensitive device label; use distinct labels across machines')
    parser.add_argument('--claude-home', type=Path, default=Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home()/'.claude'))))
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))))
    parser.add_argument('--out', type=Path, help='New ZIP path; default is the user-local capture directory')
    parser.add_argument('--quota-dir', type=Path, help='Previously saved sanitized native quota snapshots')
    parser.add_argument('--max-file-mib', type=int, default=0, help='0 streams complete initial file size; positive value explicitly limits each file')
    parser.add_argument('--max-line-mib', type=int, default=16)
    parser.add_argument('--include-task-text', action='store_true', help='OPT-IN sensitive short previews; inspect carefully before sharing')
    parser.add_argument('--dry-run', action='store_true', help='Resolve scope only; read-only MASK/Git calls allowed, no output written')
    parser.add_argument('--json', action='store_true', help='Machine-readable final summary; scan progress stays on stderr')
    parser.add_argument('--strict', action='store_true', help='Exit 3 on coverage gaps, retaining the valid partial ZIP')
    args = parser.parse_args(argv)
    if args.days < 1 or args.max_file_mib < 0 or args.max_line_mib < 1:
        parser.error('days and max-line-mib must be positive; max-file-mib must be nonnegative')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}', args.machine):
        parser.error('Use a simple non-sensitive --machine label')
    if not args.mask_projects and (args.mask_home or args.mask_python_entrypoint or args.mask_executable != 'mask'):
        parser.error('MASK-specific options require --mask-projects')
    return args


def main(argv=None) -> int:
    args = parse(argv)
    end = args.until or datetime.now(UTC)
    start = args.since or end - timedelta(days=args.days)
    if start >= end:
        raise ValueError('--since must precede --until')
    projects, selection = choose(args, Path.cwd())
    # Console/dry-run may show chosen paths. They are never copied to the shareable archive.
    if args.dry_run:
        print(json.dumps({'dry_run': True, 'selection': selection,
              'projects': [{**record, 'root': str(root)} for record, (_, root) in zip(projects.records, projects.primary)]}, indent=2))
        return 0
    target = (args.out or state_root()/'captures'/f'rfc-usage-{args.machine}-{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}.zip').expanduser().absolute()
    if target.exists() or target.is_symlink():
        raise ValueError('Refusing to overwrite --out')
    with tempfile.TemporaryDirectory(prefix='implement-rfc-capture-') as temporary:
        root = Path(temporary)
        audit = Collector(projects, start, end, root, args.max_file_mib*1024**2,
                          args.max_line_mib*1024**2, args.include_task_text)
        try:
            audit.scan(args.claude_home.expanduser(), args.codex_home.expanduser())
        finally:
            audit.writer.close()
        session_count = write_array(root, 'sessions.json', (s for s in audit.sessions.values() if s['events']))
        write_array(root, 'counter_baselines.json', (v for k, v in audit.counter_baselines.items()
                    if audit.sessions.get(k, {}).get('events')))
        scope_gaps = [r for r in projects.records if r['identity_check'] == 'mismatch' or not r['available_now']]
        write_json(root, 'scopes.json', {'selection': selection, 'projects': projects.records})
        write_json(root, 'coverage.json', {'stats': dict(audit.stats), 'warnings': audit.problems,
            'scope_gaps': scope_gaps, 'files': audit.files,
            'all_scanned_record_shapes_not_project_usage': [{'type': k[0], 'payload_type': k[1], 'count': v} for k,v in sorted(audit.shapes.items())]})
        # Exclude registry identity mismatches from current configuration inspection too.
        rejected = {r['label'] for r in projects.records if r['identity_check'] == 'mismatch'}
        good = type('InventoryScopes', (), {'primary': [(n,p) for n,p in projects.primary if n not in rejected], 'match': staticmethod(projects.match)})()
        write_json(root, 'configuration.json', inventory(good, args.claude_home.expanduser(), args.codex_home.expanduser()))
        quota_warnings = []
        if args.quota_dir:
            from usage_quota import sanitize_snapshot
            snapshots = []
            directory = args.quota_dir.expanduser()
            if not directory.is_dir():
                quota_warnings.append('quota_directory_unavailable')
            for path in sorted(directory.glob('*.json')):
                try:
                    if path.is_symlink() or path.stat().st_size > 1024*1024:
                        quota_warnings.append('quota_snapshot_skipped'); continue
                    value = sanitize_snapshot(json.loads(path.read_bytes()))
                    if value is None:
                        quota_warnings.append('invalid_snapshot'); continue
                    moment = dt(value.get('observed_at'))
                    if moment and start <= moment < end:
                        snapshots.append(value)
                except (ValueError, OSError, TypeError, KeyError):
                    quota_warnings.append('invalid_snapshot')
            write_json(root, 'quota_snapshots.json', snapshots)
            write_json(root, 'quota_import_coverage.json', {'warnings': quota_warnings, 'accepted': len(snapshots)})
        gaps = bool(audit.stats['coverage_warnings'] or scope_gaps or quota_warnings or any(v for k,v in audit.stats.items() if k.endswith('_missing_roots')))
        if not session_count:
            gaps = True
        summary = {'schema': 'implement-rfc.usage-summary.v1', 'archive': str(target),
                   'project_count': len(projects.records), 'session_count': session_count,
                   'coverage': 'partial_or_empty' if gaps else 'no_detected_gaps',
                   'coverage_warnings': audit.stats['coverage_warnings'], 'scope_gaps': len(scope_gaps),
                   'billing_estimated': False, 'network_calls': False, 'model_calls': False}
        (root/'SUMMARY.md').write_text('# Local usage capture\n\n'
            f"Projects: {len(projects.records)}. Sessions: {session_count}. Coverage: {summary['coverage']}.\n\n"
            'Raw observations are not additive. Reconcile request IDs, forks, cumulative epochs and counter baselines.\n'
            'No task success or subscription spending is inferred. Account pools are not project budgets.\n'
            'Missing projects/providers/fields are unknown, not zero. Retained local history only; remote devices excluded.\n'
            'Tool-name allowlists are versioned; unknown names remain hashed. Code embedded in exec is not evaluated.\n'
            'Metadata, project labels, timestamps and stable hashes can identify work. Inspect before sharing.\n', encoding='utf-8')
        manifest = {'schema': 'rfc-usage-evidence.v2', 'collector_version': VERSION,
            'machine': args.machine, 'platform': platform.system(), 'generated_at': datetime.now(UTC).isoformat(),
            'since_inclusive': start.isoformat(), 'until_exclusive': end.isoformat(),
            'project_labels': [r['label'] for r in projects.records], 'session_count': session_count,
            'text_previews_included': args.include_task_text, 'billing_or_quota_estimates': False,
            'scope': selection, 'coverage': summary['coverage'],
            'files': {p.name: {'bytes': p.stat().st_size, 'sha256': sha_file(p)} for p in sorted(root.iterdir())}}
        write_json(root, 'manifest.json', manifest)
        publish(root, target)
        for index in (audit.sessions, audit.emitted, audit.call_map, audit.counter_baselines):
            index.close()
    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(f"Created {target}\nProjects: {summary['project_count']}; sessions: {session_count}; coverage: {summary['coverage']}.")
        print('Inspect the ZIP, then attach that ZIP only. No model requests, account operations or uploads were made.')
    return 3 if args.strict and gaps else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(f'usage: {error}', file=sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print('Collection interrupted; agent runtimes were not changed.', file=sys.stderr)
        raise SystemExit(130)
