"""One counter model for validation and allocation; branches, remotes and tags count."""
from __future__ import annotations

import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import board_model as board
import project_config


def git(root: Path, *args: str, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(root), *args], env=project_config.git_environment(),
                          capture_output=True, text=True, check=check, timeout=30)


def inspect_counters(root: Path, config: dict, cards: dict) -> tuple[dict, list, dict]:
    location = board.safe_path(root, root / config['next_id']['path'])
    paths = [location] if config['next_id']['mode'] == 'single-file' else sorted(location.glob('*'))
    counters, errors = {}, []
    def error(path, reason):
        errors.append(board.Diagnostic(str(path), 'next_id', reason))
    for path in paths:
        if path.name.startswith('_'):
            continue
        board.safe_path(root, path)
        if not path.is_file():
            error(path, 'counter file missing')
            continue
        value = path.read_text(encoding='utf-8').strip()
        if not board.ID_RE.fullmatch(value):
            error(path, f'malformed counter {value!r}')
            continue
        area, n = value.rsplit('-', 1)
        if config['next_id']['mode'] == 'per-area' and path.name != area:
            error(path, 'per-area counter filename must match its ID prefix')
        if area in counters:
            error(path, f'duplicate area {area}')
        counters[area] = (int(n), path)
    high = {}
    for cid in cards:
        area, n = cid.rsplit('-', 1)
        high[area] = max(high.get(area, 0), int(n))
    receipts = board.safe_path(root, root / config['reservations_dir'])
    for path in receipts.rglob('*.json') if receipts.exists() else []:
        board.safe_path(root, path)
        try:
            receipt = json.loads(path.read_text(encoding='utf-8'))
            ids = receipt.get('ids', [])
            if not isinstance(ids, list):
                raise ValueError('reservation ids must be an array')
            for cid in ids:
                if not isinstance(cid, str) or not board.ID_RE.fullmatch(cid):
                    raise ValueError('malformed reserved ID')
                area, n = cid.rsplit('-', 1)
                high[area] = max(high.get(area, 0), int(n))
        except (ValueError, AttributeError) as exc:
            error(path, f'invalid reservation: {exc}')
    for area, n in high.items():
        if area not in counters:
            error(location, f'missing counter for {area}')
        elif counters[area][0] <= n:
            error(counters[area][1], f'next {area}-{counters[area][0]:04d} <= highest used/reserved {area}-{n:04d}')
    if not counters and config['next_id']['mode'] == 'single-file':
        error(location, 'no counter found')
    limit = config.get('allocation', {}).get('history_limit', 2000)
    info = {'limit': limit, 'commits': 0, 'truncated': False, 'refs': ['branches', 'remotes', 'tags', 'HEAD'], 'high_water': {}}
    if git(root, 'rev-parse', '--verify', 'HEAD', check=False).returncode == 0:
        history = git(root, 'log', '--branches', '--remotes', '--tags', 'HEAD', '--full-history',
                      '--no-renames', '--no-ext-diff', '--no-textconv', f'--max-count={limit+1}',
                      '-p', '--unified=0', '--format=%x00%H', '--', config['next_id']['path'])
        info['commits'] = history.stdout.count('\x00')
        info['truncated'] = info['commits'] > limit
        if info['truncated']:
            error(location, f'counter history exceeds configured {limit}-commit bound; explicitly increase allocation.history_limit')
        for area, n in re.findall(r'^[+\- ]([A-Z]{2,8})-(\d{4})\s*$', history.stdout, re.M):
            info['high_water'][area] = max(info['high_water'].get(area, 0), int(n))
        for area, historic in info['high_water'].items():
            if area not in counters:
                error(location, f'missing historically allocated counter {area}')
                continue
            current, path = counters[area]
            waived = any(o['area'] == area and historic <= o['waived_through'] and current >= o['floor']
                         for o in config.get('allocation', {}).get('rewind_overrides', []))
            if current < historic and not waived:
                error(path, f'{area}-{current:04d} rewinds historical high water {area}-{historic:04d}')
    return counters, errors, info


def allocate(root: Path, config: dict, *, area: str | None, count: int, reserve_for: str, dry_run=False) -> dict:
    from issue_board import board_lock, apply_changes
    if not 1 <= count <= 64 or not board.TOKEN_RE.fullmatch(reserve_for):
        raise board.BoardError(root, 'allocation', 'count must be 1..64 and reserve-for a token')
    if git(root, 'branch', '--show-current').stdout.strip() != config['workstreams']['main']['branch']:
        raise board.BoardError(root, 'allocation', 'only the configured main integrator may reserve IDs')
    with board_lock(root):
        cards, errors = board.read_cards(root, config)
        counters, counter_errors, history = inspect_counters(root, config, cards)
        if errors or counter_errors:
            raise board.ValidationError(root, errors + counter_errors)
        if area is None and len(counters) == 1:
            area = next(iter(counters))
        if area not in counters:
            raise board.BoardError(root, 'area', 'select an existing counter area explicitly')
        start, path = counters[area]
        if start + count > 9999:
            raise board.BoardError(path, 'counter', 'ID space exhausted')
        ids = [f'{area}-{n:04d}' for n in range(start, start + count)]
        receipt = board.safe_path(root, root / config['reservations_dir'] / f'{ids[0]}--{ids[-1]}--{uuid.uuid4().hex[:12]}.json')
        record = {'schema': 'implement-rfc.reservation.v1', 'ids': ids, 'reserve_for': reserve_for,
                  'created': datetime.now(timezone.utc).isoformat(), 'base': git(root, 'rev-parse', 'HEAD').stdout.strip()}
        changes = {path: f'{area}-{start+count:04d}\n'.encode(), receipt: (json.dumps(record, indent=2)+'\n').encode()}
        if not dry_run:
            receipt.parent.mkdir(parents=True, exist_ok=True)
            apply_changes(changes, {path: path.read_bytes(), receipt: None})
        return {'schema': 'implement-rfc.allocation.v1', 'ids': ids, 'next_id': f'{area}-{start+count:04d}',
                'changed_paths': [p.relative_to(root).as_posix() for p in changes], 'history': history, 'dry_run': dry_run}
