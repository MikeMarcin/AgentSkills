#!/usr/bin/env python3
"""Validate issue cards, report RFC queues, and move one card with its live links.

Uses the portable project config. Mutations require explicit bookkeeping policy.
Claim and finish commit explicit scope; agents retain acceptance judgment.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
import fnmatch
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit, urlunsplit

if sys.version_info < (3, 10):
    sys.exit(f'issue_board.py requires Python 3.10+; found {sys.version.split()[0]} at {sys.executable}')

sys.path.insert(0, str(Path(__file__).resolve().parent))
import board_model as board
import project_config

# Match inline links and reference definitions, retaining offsets into the
# original text. Code fences and inline code are masked before searching.
LINK_RE = re.compile(r'!?\[[^\]\n]*\]\(\s*(?P<inline><[^>\n]+>|[^\s()]+)'
                     r'(?:\s+["\'][^\n]*?["\'])?\s*\)'
                     r'|^ {0,3}\[[^\]\n]+\]:\s*(?P<reference><[^>\n]+>|\S+)', re.M)
def mask_code(text: str) -> str:
    """Keep character offsets while hiding fenced, indented, and inline code."""
    def blank(value: str) -> str:
        return ''.join('\n' if char == '\n' else ' ' for char in value)

    fence = None
    lines = []
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)', line)
        if fence is not None:
            lines.append(blank(line))
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
            lines.append(blank(line))
        elif line.startswith(('    ', '\t')):
            lines.append(blank(line))
        else:
            lines.append(line)
    masked = ''.join(lines)
    return re.sub(r'(?<!`)(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)', lambda m: blank(m[0]), masked)


def require_valid(root: Path, config: dict, overrides: dict | None = None, scope=None) -> dict:
    cards, errors = board.validate_board(root, config, overrides, scope=scope)
    if errors:
        raise board.ValidationError(root, errors)
    return cards


def queue(root: Path, config: dict, rfcs: list[str], platform: str, include: list[str],
          all_cards: bool, areas: list[str] | None = None, human_waiting=False, history=False) -> dict:
    areas = areas or []
    if not (rfcs or areas or include or all_cards or human_waiting):
        raise board.BoardError(root, 'scope', 'select --rfc, --area, --include, --human-waiting or explicit --all')
    def selected(card):
        scope_match = all_cards or bool(set(rfcs) & set(card.rfcs)) or card.id in include or (card.fields.get('area') in areas or card.id.split('-')[0] in areas)
        human = card.fields.get('parked_on') in {'human-review', 'human-attendance', 'attended-review'}
        return (scope_match or (human_waiting and not (rfcs or areas or include))) and (not human_waiting or human)
    scope = lambda cards: board.dependency_scope(cards, {c.id for c in cards.values() if selected(c)})
    cards = require_valid(root, config, scope=scope)
    for rfc in rfcs:
        if not board.RFC_RE.fullmatch(rfc) or len(list((root / config['rfc_root']).glob(rfc + '-*.md'))) != 1:
            raise board.BoardError(root, 'rfc', f'unknown or ambiguous RFC {rfc}')
    for card_id in include:
        if card_id not in cards:
            raise board.BoardError(root, 'include', f'unknown card {card_id}')
    chosen = [c for c in cards.values() if selected(c)]
    order = {}
    if config.get('sequencing') == 'ordered-index':
        index = root / config['rfc_root'] / 'README.md'
        for rid in re.findall(r'RFC-[A-Z]{2,8}(?:-[A-Z]{2,8})?-\d{4}', index.read_text(encoding='utf-8')):
            order.setdefault(rid, len(order))
    chosen.sort(key=lambda c: (min((order.get(r, 999999) for r in c.rfcs), default=999999), c.fields.get('priority', 'P2'), c.id))
    lanes = config['lanes']
    rows = []
    for card in chosen:
        unmet = [dep for dep in card.deps if dep not in cards or cards[dep].lane != lanes['done']]
        platforms = card.fields.get('platforms', [])
        if card.lane == lanes['done']:
            disposition = 'done'
        elif platforms and platform not in platforms:
            disposition = 'deferred_platform'
        elif card.lane == lanes['in_progress']:
            disposition = 'in_progress'
        elif card.lane == lanes['parked']:
            disposition = 'parked'
        elif card.lane == lanes['blocked']:
            disposition = 'blocked'
        elif unmet:
            disposition = 'waiting_dependencies'
        elif card.lane in {lanes['inbox'], lanes['backlog']}:
            disposition = 'backlog_candidate'
        else:
            disposition = 'ready'
        rows.append({'id': card.id, 'title': card.fields['title'], 'path': card.path.relative_to(root).as_posix(),
                     'rfcs': card.rfcs, 'status': card.fields['status'], 'unmet_dependencies': unmet,
                     'external_depends_on': card.fields.get('external_depends_on', []),
                     'disposition': disposition, 'reason': card.fields.get('parked_on', card.fields.get('blocked_by'))})
    active = [r['id'] for r in rows if r['disposition'] == 'in_progress']
    ready = [r['id'] for r in rows if r['disposition'] == 'ready']
    return {'schema': 'implement-rfc.queue.v1', 'rfcs': rfcs, 'areas': areas, 'platform': platform,
            'next': active[0] if len(active) == 1 else (ready[0] if not active and ready else None),
            'ambiguous_in_progress': active if len(active) > 1 else [],
            'closeout_paths': [c.path.relative_to(root).as_posix() for c in chosen if c.fields.get('closeout_for')],
            'selected_count': len(rows), 'done_count': sum(r['disposition'] == 'done' for r in rows),
            'cards': [r for r in rows if history or r['disposition'] != 'done']}


def markdown_paths(root: Path, rules: dict) -> list[Path]:
    paths = set()
    for relative in rules['link_roots']:
        path = board.safe_path(root, root / relative)
        if path.is_file() and path.suffix == '.md':
            paths.add(path)
        elif path.is_dir():
            paths.update(path.rglob('*.md'))
    return sorted(board.safe_path(root, path) for path in paths)


def protected(root: Path, path: Path, rules: dict) -> bool:
    relative = path.relative_to(root).as_posix()
    return (any(fnmatch.fnmatchcase(relative, pattern) for pattern in rules['protected_globs'])
            and not any(fnmatch.fnmatchcase(relative, pattern) for pattern in rules['editable_globs']))


def rewrite_links(data: bytes, path: Path, new_path: Path, source: Path, destination: Path, root: Path) -> bytes:
    if source == destination and path == new_path:
        return data
    text = data.decode('utf-8')
    masked = mask_code(text)
    edits = []
    for match in LINK_RE.finditer(masked):
        group = 'inline' if match.group('inline') is not None else 'reference'
        begin, end = match.span(group)
        original = text[begin:end]
        angled = original.startswith('<')
        target = original[1:-1] if angled else original
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            continue
        decoded = unquote(url.path)
        resolved = ((root / decoded.lstrip('/')) if decoded.startswith('/') else path.parent / decoded).resolve()
        if not resolved.is_relative_to(root):
            continue
        new_target = destination if resolved == source else resolved
        if resolved != source and path.parent == new_path.parent:
            continue
        if decoded.startswith('/'):
            rewritten = '/' + new_target.relative_to(root).as_posix()
        else:
            rewritten = Path(os.path.relpath(new_target, new_path.parent)).as_posix()
        if '%' in url.path or not angled:
            rewritten = quote(rewritten, safe='/._~-')
        rewritten = urlunsplit(('', '', rewritten, url.query, url.fragment))
        if angled:
            rewritten = '<' + rewritten + '>'
        if rewritten != original:
            edits.append((begin, end, rewritten))
    for begin, end, value in reversed(edits):
        text = text[:begin] + value + text[end:]
    return text.encode('utf-8')


def plan_move(root: Path, config: dict, card_id: str, lane: str,
              parked_on: str | None, blocked_by: str | None) -> tuple[dict, dict]:
    if 'bookkeeping' not in config:
        raise board.BoardError(root, 'bookkeeping', 'configure bookkeeping policy before moving cards')
    scope = lambda cards: board.dependency_scope(cards, {card_id})
    cards = require_valid(root, config, scope=scope)
    if card_id not in cards:
        raise board.BoardError(root, 'id', f'unknown card {card_id}')
    if lane not in project_config.lane_names(config):
        raise board.BoardError(root, 'lane', f'unknown lane {lane}')
    card = cards[card_id]
    lanes = config['lanes']
    if card.lane == lanes['done'] and lane != card.lane:
        raise board.BoardError(card.path, 'lane', 'Done is terminal; create follow-up work')
    for value, allowed, key in ((parked_on, lanes['parked'], 'parked_on'), (blocked_by, lanes['blocked'], 'blocked_by')):
        if value is not None and (lane != allowed or not board.TOKEN_RE.fullmatch(value)):
            raise board.BoardError(card.path, key, 'invalid token or destination lane')
    updates = {'status': config['lane_statuses'][lane],
               'parked_on': (parked_on or card.fields.get('parked_on')) if lane == lanes['parked'] else None,
               'blocked_by': (blocked_by or card.fields.get('blocked_by')) if lane == lanes['blocked'] else None}
    source = card.path
    destination = board.safe_path(root, source.parent.parent / lane / source.name)
    if source != destination and destination.exists():
        raise board.BoardError(destination, 'path', 'destination already exists')
    rules = config['bookkeeping']
    paths = set(markdown_paths(root, rules)) | {source}
    originals = {path: path.read_bytes() for path in paths}
    changes: dict[Path, bytes | None] = {}
    for path in sorted(paths):
        new_path = destination if path == source else path
        data = card.matter.updated(updates) if path == source else originals[path]
        updated = rewrite_links(data, path, new_path, source, destination, root)
        if new_path != path or updated != originals[path]:
            if protected(root, path, rules) or protected(root, new_path, rules):
                raise board.BoardError(path, 'link', 'move would change protected content')
            changes[new_path] = updated
    if source != destination:
        changes[source] = None
        originals[destination] = None
    require_valid(root, config, changes, scope=scope)
    return changes, originals


@contextmanager
def board_lock(root: Path, runtime_root: Path | None = None):
    if runtime_root is None:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--absolute-git-dir'],
                                capture_output=True, text=True, check=True, env=project_config.git_environment())
        path = Path(result.stdout.strip()) / 'implement-rfc-board.lock'
    else:
        runtime_root.mkdir(parents=True, exist_ok=True)
        path = runtime_root / 'board.lock'
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise board.BoardError(path, 'lock', 'another move is active; after interruption confirm its process ended before removing this lock') from None
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(str(os.getpid()) + '\n')
        yield
    finally:
        path.unlink()


def write_file(path: Path, data: bytes, *, create: bool, mode: int = 0o644) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix='.issue-board-', dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        if create:
            os.link(temporary_path, path)  # Atomic publication that refuses overwrite.
        else:
            os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def apply_changes(changes: dict, originals: dict) -> None:
    for path, original in originals.items():
        if path.is_symlink() or (path.read_bytes() if path.exists() else None) != original:
            raise board.BoardError(path, 'concurrency', 'file changed since preflight')
    applied = []
    created_dirs = []
    modes = {p: stat.S_IMODE(p.stat().st_mode) for p in changes if p.exists()}
    source_mode = next((modes[p] for p, data in changes.items() if data is None), 0o644)
    try:
        for path, data in sorted(changes.items(), key=lambda item: item[1] is None):
            original = originals.get(path)
            if (path.read_bytes() if path.exists() else None) != original:
                raise board.BoardError(path, 'concurrency', 'file changed during move')
            if not path.parent.exists():
                path.parent.mkdir()  # Only a configured lane may be absent.
                created_dirs.append(path.parent)
            applied.append(path)
            if data is None:
                path.unlink()
            else:
                write_file(path, data, create=original is None, mode=modes.get(path, source_mode))
    except (OSError, board.BoardError) as exc:
        failures = []
        for path in reversed(applied):
            try:
                current = path.read_bytes() if path.exists() else None
                original = originals.get(path)
                if current == original:
                    continue  # The failing operation did not publish its write.
                if current != changes[path]:
                    raise OSError('file changed externally; not overwritten by rollback')
                if original is None:
                    path.unlink()
                else:
                    write_file(path, original, create=not path.exists(), mode=modes.get(path, 0o644))
            except OSError as rollback_error:
                failures.append(f'{path}: {rollback_error}')
        for directory in reversed(created_dirs):
            try:
                directory.rmdir()
            except OSError as rollback_error:
                failures.append(f'{directory}: {rollback_error}')
        if failures:
            raise board.BoardError('move', 'rollback', f'{exc}; incomplete rollback: ' + '; '.join(failures)) from exc
        raise


def move(root: Path, config: dict, args, runtime_root: Path | None = None) -> dict:
    def perform() -> dict:
        changes, originals = plan_move(root, config, args.id, args.to, args.parked_on, args.blocked_by)
        if not args.dry_run:
            apply_changes(changes, originals)
        return {'schema': 'implement-rfc.move.v1', 'id': args.id, 'lane': args.to,
                'dry_run': args.dry_run, 'changed_paths': sorted(p.relative_to(root).as_posix() for p in changes)}
    if args.dry_run:
        return perform()
    with board_lock(root, runtime_root):
        return perform()


def commit_transition(root: Path, config: dict, args, runtime_root: Path | None = None) -> dict:
    """Agent selects acceptance; this command owns only the explicit Git slice."""
    from allocation import git
    with board_lock(root, runtime_root):
        if git(root, 'diff', '--cached', '--name-only').stdout.strip():
            raise board.BoardError(root, 'git', 'index must be empty; preserve or commit existing staged work first')
        revision = git(root, 'rev-parse', 'HEAD').stdout.strip()
        if args.expect_revision and args.expect_revision != revision:
            raise board.BoardError(root, 'revision', 'HEAD changed since supplied expectation')
        explicit = set()
        for relative in getattr(args, 'paths', []):
            path = board.safe_path(root, root / relative)
            if Path(relative).is_absolute() or path.is_dir() or any(c in relative for c in '*?[') or relative.startswith(':'):
                raise board.BoardError(path, 'paths', 'supply individual repository-relative files')
            explicit.add(path)
        cards = require_valid(root, config, scope=lambda cs: board.dependency_scope(cs, {args.id}))
        if args.id not in cards:
            raise board.BoardError(root, 'id', f'unknown card {args.id}')
        card = cards[args.id]
        records = None
        if args.command == 'claim':
            if card.lane != config['lanes']['ready']:
                raise board.BoardError(card.path, 'claim', 'claim requires an eligible Ready card')
            if card.fields.get('platforms') and args.platform not in card.fields['platforms']:
                raise board.BoardError(card.path, 'platforms', 'card is not eligible on selected platform')
            lane, parked = config['lanes']['in_progress'], None
        else:
            decision = json.loads(args.acceptance.read_text(encoding='utf-8'))
            if decision.get('approved') is not True or decision.get('decision') not in {'done', 'human-pending'}:
                raise board.BoardError(args.acceptance, 'acceptance', 'agent-approved decision must be done or human-pending')
            records = decision.get('records')
            candidate = dict(card.fields, acceptance=records)
            errors = board.schema_errors(candidate, card.path, config)
            if errors or not records:
                raise board.BoardError(args.acceptance, 'acceptance', 'supply nonempty criterion/outcome/revision/evidence records')
            if decision['decision'] == 'done' and any(r['outcome'] != 'pass' for r in records):
                raise board.BoardError(args.acceptance, 'acceptance', 'Done requires all supplied criteria passing')
            lane = config['lanes']['done'] if decision['decision'] == 'done' else config['lanes']['parked']
            parked = 'human-review' if decision['decision'] == 'human-pending' else None
        changes, originals = plan_move(root, config, args.id, lane, parked, None)
        destination = card.path.parent.parent / lane / card.path.name
        if records is not None:
            data = changes.get(destination, card.path.read_bytes())
            changes[destination] = board.parse_matter(data, destination).updated({'acceptance': records})
            originals.setdefault(destination, destination.read_bytes() if destination.exists() else None)
        # Implicit bookkeeping files must be pristine. Explicitly supplied source
        # files may be dirty: their inclusion is the agent's deliberate decision.
        for path in changes:
            if path in explicit:
                continue
            status = git(root, 'status', '--porcelain', '--', str(path.relative_to(root))).stdout
            if status.strip():
                raise board.BoardError(path, 'git', 'bookkeeping path has uncommitted edits; supply it explicitly with finish --paths or commit first')
        commit_paths = sorted(p.relative_to(root).as_posix() for p in set(changes) | explicit)
        if not commit_paths:
            raise board.BoardError(root, 'git', 'no changes to commit')
        if not args.dry_run:
            apply_changes(changes, originals)
            git(root, 'add', '--', *commit_paths)
            # --only protects against an unrelated index addition by another process.
            identity = ('-c', 'user.name=implement-rfc', '-c', 'user.email=implement-rfc@localhost') if runtime_root else ()
            git(root, *identity, 'commit', '--only', '-m', args.message or f'{args.command.title()} {args.id}', '--', *commit_paths)
        return {'schema': f'implement-rfc.{args.command}.v1', 'id': args.id, 'lane': lane,
                'changed_paths': commit_paths, 'dry_run': args.dry_run,
                'commit': None if args.dry_run else git(root, 'rev-parse', 'HEAD').stdout.strip()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path)
    parser.add_argument('--mode', choices=('project', 'personal'))
    parser.add_argument('--workflow-root', type=Path)
    parser.add_argument('--project-config', type=Path, help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest='command', required=True)
    vp = commands.add_parser('validate', help='Check structure globally and workflow in selected dependency closure')
    qp = commands.add_parser('queue', help='Compact scoped work and human waits; never promote cards')
    for sub in (vp, qp):
        sub.add_argument('--rfc', action='append', default=[])
        sub.add_argument('--area', action='append', default=[])
        sub.add_argument('--include', nargs='+', default=[])
        sub.add_argument('--all', action='store_true')
    qp.add_argument('--platform', choices=['mac', 'win', 'linux'], default={'darwin':'mac','win32':'win'}.get(sys.platform,'linux'))
    qp.add_argument('--human-waiting', action='store_true')
    qp.add_argument('--history', action='store_true', help='Include selected Done cards')
    ip = commands.add_parser('inspect', help='Inspect one card and its dependencies; body is opt-in')
    ip.add_argument('id'); ip.add_argument('--body', action='store_true')
    mp = commands.add_parser('move', help='Move one card and repair live links without committing')
    cp = commands.add_parser('claim', help='Claim and commit an eligible card')
    fp = commands.add_parser('finish', help='Commit explicitly approved acceptance and named source paths')
    for sub in (mp, cp, fp):
        sub.add_argument('id'); sub.add_argument('--dry-run', action='store_true')
    mp.add_argument('--to', required=True); mp.add_argument('--parked-on'); mp.add_argument('--blocked-by')
    for sub in (cp, fp):
        sub.add_argument('--expect-revision'); sub.add_argument('--message')
    cp.add_argument('--platform', choices=['mac','win','linux'], default={'darwin':'mac','win32':'win'}.get(sys.platform,'linux'))
    fp.add_argument('--acceptance', type=Path, required=True)
    fp.add_argument('--paths', nargs='+', default=[])
    ap = commands.add_parser('allocate', help='Reserve IDs using the same board/history model')
    ap.add_argument('--area'); ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--reserve-for', required=True); ap.add_argument('--purpose', default=''); ap.add_argument('--dry-run', action='store_true')
    for sub in (vp, qp, ip, mp, cp, fp, ap):
        sub.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        context = project_config.resolve_context(repo_root=args.repo_root, project_config_path=args.project_config,
                                                 mode=args.mode, workflow_root=args.workflow_root)
        root, config = context.workflow_root, context.config
        if context.mode == 'personal' and args.command in {'move', 'claim', 'finish', 'allocate'}:
            import personal_lanes
            personal_lanes.validate_pair(context)
            if args.command == 'finish' and args.paths:
                raise ValueError('personal product paths require personal_commit.py begin/finish; tracker-only finish omits --paths')
            if args.command == 'allocate':
                personal_lanes.assert_reservation_authority(context)
        if args.command == 'validate':
            scope = None
            if args.rfc or args.area or args.include:
                scope = lambda cs: board.dependency_scope(cs, {c.id for c in cs.values() if set(args.rfc)&set(c.rfcs) or c.id in args.include or (c.fields.get('area') in args.area or c.id.split('-')[0] in args.area)})
            cards, errors = board.validate_board(root, config, scope=scope)
            result = {'schema': 'implement-rfc.validation.v1', 'valid': not errors,
                      'card_count':len(cards), 'errors':[asdict(e) for e in errors]}
            code = bool(errors)
        elif args.command == 'queue':
            result = queue(root, config, args.rfc, args.platform, args.include, args.all, args.area, args.human_waiting, args.history)
            code = 0
        elif args.command == 'inspect':
            cards = require_valid(root, config, scope=lambda cs: board.dependency_scope(cs, {args.id}))
            if args.id not in cards:
                raise board.BoardError(root, 'id', f'unknown card {args.id}')
            card = cards[args.id]
            result = {'schema':'implement-rfc.inspect.v1', 'path':card.path.relative_to(root).as_posix(),
                      'fields':card.fields, 'dependencies':[{ 'id':d, 'path':cards[d].path.relative_to(root).as_posix(), 'status':cards[d].fields['status']} for d in card.deps]}
            if args.body: result['body'] = card.body
            code = 0
        elif args.command == 'allocate':
            import allocation
            result = allocation.allocate(root, config, area=args.area, count=args.count, reserve_for=args.reserve_for, purpose=args.purpose, dry_run=args.dry_run)
            code = 0
        elif args.command in {'claim', 'finish'}:
            result = commit_transition(root, config, args,
                context.runtime_root if context.mode == 'personal' else None); code = 0
        else:
            result = move(root, config, args,
                context.runtime_root if context.mode == 'personal' else None); code = 0
    except (board.BoardError, project_config.ProjectConfigError, OSError, subprocess.SubprocessError, ValueError) as exc:
        diagnostics = [asdict(e) for e in exc.diagnostics] if isinstance(exc, board.ValidationError) else [asdict(exc.diagnostic)] if isinstance(exc, board.BoardError) else [{'path':'','field':'command','reason':str(exc)}]
        result = {'schema':f'implement-rfc.{args.command}.v1', 'errors':diagnostics}
        code = 1
    if args.json:
        print(json.dumps(result, separators=(',', ':')))
    elif result.get('errors'):
        for e in result['errors']: print(f"{e['path']}: {e['field']}: {e['reason']}", file=sys.stderr)
    elif args.command == 'queue':
        print(f"Next: {result['next'] or 'none'}; selected {result['selected_count']}, done {result['done_count']}")
        if result['ambiguous_in_progress']: print('Ambiguous claims: '+', '.join(result['ambiguous_in_progress']))
        for path in result['closeout_paths']: print('Closeout: '+path)
        for row in result['cards']: print(f"{row['id']} {row['disposition']} {row['path']} {row['reason'] or ', '.join(row['unmet_dependencies'])}")
    else:
        print(json.dumps(result, indent=2))
    return int(code)


if __name__ == '__main__':
    sys.exit(main())
