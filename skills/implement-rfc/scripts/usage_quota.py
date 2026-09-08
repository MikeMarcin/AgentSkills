#!/usr/bin/env python3
"""Allowlisted account-quota snapshots, not task-level billing. Python 3.11+.

codex: explicitly launches the installed CLI app server and requests rate limits.
claude-stdin: reads a status-line JSON payload from stdin, offline.
manual: records values the user reads from a provider's usage UI.
No mode starts a model turn, changes routing, redeems resets, or installs hooks.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
sys.dont_write_bytecode = True
from usage_capture import atom, dt, number, obj, quota_buckets, stamp

UTC = timezone.utc
WINDOWS = {'primary', 'secondary', 'five_hour', 'seven_day', 'spend_limit',
           'seven_day_opus', 'seven_day_sonnet', 'seven_day_fable'}
SOURCES = {'codex_app_server', 'claude_statusline', 'manual'}


def percent(value):
    n = number(value)
    return n if n is not None and n <= 100 else None


def sanitize_snapshot(value):
    """Rebuild allowlisted schema; never trust an arbitrary input JSON file."""
    v = obj(value)
    if v.get('schema') != 'rfc-quota.v1' or v.get('provider') not in ('claude', 'codex'):
        raise ValueError('Unsupported quota snapshot schema/provider')
    if not dt(v.get('observed_at')) or v.get('source') not in SOURCES:
        raise ValueError('Snapshot requires an explicit time and source')
    data = obj(v.get('data')); buckets = []
    for raw in data.get('buckets', []) if isinstance(data.get('buckets'), list) else []:
        b = obj(raw); windows = []
        for raw_w in b.get('windows', []) if isinstance(b.get('windows'), list) else []:
            w = obj(raw_w)
            if w.get('window') not in WINDOWS: continue
            windows.append({'window': w['window'], 'used_percent': number(w.get('used_percent')) if w['window'] == 'spend_limit' else percent(w.get('used_percent')),
                            'resets_at': stamp(w.get('resets_at')), 'window_minutes': number(w.get('window_minutes'))})
        buckets.append({'pool': atom(b.get('pool')), 'plan_type': atom(b.get('plan_type')),
                        'windows': windows, 'credit_balance': number(b.get('credit_balance')),
                        'has_credits': b.get('has_credits') if isinstance(b.get('has_credits'), bool) else None,
                        'unlimited_credits': b.get('unlimited_credits') if isinstance(b.get('unlimited_credits'), bool) else None})
    return {'schema': 'rfc-quota.v1', 'provider': v['provider'], 'source': v['source'],
            'observed_at': stamp(v['observed_at']), 'account_label': atom(v.get('account_label')),
            'machine': atom(v.get('machine')), 'data_freshness': 'provider_sample_time_unknown',
            'data': {'buckets': buckets, 'available_reset_count': number(data.get('available_reset_count'))}}


def codex_rates(binary, timeout):
    """Stdio JSON-RPC handshake + the one read endpoint; no thread/turn calls."""
    executable = shutil.which(binary)
    if not executable: raise RuntimeError('Codex CLI was not found; supply --codex-bin with its installed path')
    messages = queue.Queue(maxsize=256)
    stop = threading.Event()
    with tempfile.TemporaryDirectory(prefix='quota-read-') as cwd:
        proc = subprocess.Popen([executable, 'app-server'], cwd=cwd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        def read():
            try:
                while not stop.is_set():
                    raw = proc.stdout.readline(2 * 1024 * 1024 + 1)
                    if not raw: break
                    if len(raw) > 2 * 1024 * 1024:
                        messages.put({'collector_error': 'app_server_response_too_large'}, timeout=1); return
                    try: msg = json.loads(raw)
                    except ValueError:
                        messages.put({'collector_error':'invalid_json'},timeout=1);return
                    if isinstance(msg, dict): messages.put(msg, timeout=1)
            except (OSError, ValueError, queue.Full): pass
            finally:
                try: messages.put({'collector_eof': True}, timeout=0.1)
                except queue.Full: pass
        reader = threading.Thread(target=read, daemon=True); reader.start()
        deadline = time.monotonic() + timeout
        def send(value):
            proc.stdin.write((json.dumps(value) + '\n').encode()); proc.stdin.flush()
        def response(request_id):
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0: raise RuntimeError('App-server quota request timed out; no snapshot inferred')
                try: msg = messages.get(timeout=remaining)
                except queue.Empty: raise RuntimeError('App-server quota request timed out; no snapshot inferred') from None
                if msg.get('collector_error') or msg.get('collector_eof'):
                    raise RuntimeError('App-server stopped or returned an oversized record; no snapshot inferred')
                if msg.get('id') == request_id and ('result' in msg or 'error' in msg):
                    if 'error' in msg:
                        code = obj(msg.get('error')).get('code')
                        safe_code = code if isinstance(code, int) else 'unknown'
                        raise RuntimeError(f'App-server quota read failed (code {safe_code}); check login and CLI support')
                    return obj(msg.get('result'))
                if 'method' in msg and 'id' in msg:
                    # No external auth-token refresh, permission approval, or tool calls.
                    raise RuntimeError('Native interactive request requires host attention; quota read stopped without answering')
        try:
            send({'id': 0, 'method': 'initialize', 'params': {'clientInfo': {
                'name': 'implement_rfc_quota_audit', 'title': 'Local quota audit', 'version': '1.0.0'}}})
            response(0)
            send({'method': 'initialized', 'params': {}})
            send({'id': 1, 'method': 'account/rateLimits/read'})
            return response(1)
        finally:
            stop.set()
            try: proc.stdin.close()
            except OSError: pass
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=3)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=3)
            reader.join(timeout=1)
            proc.stdout.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('codex', 'claude-stdin', 'manual'))
    p.add_argument('--account-label', required=True, help='Same pseudonym on all machines sharing this provider account')
    p.add_argument('--machine', default='local')
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--codex-bin', default='codex')
    p.add_argument('--timeout', type=float, default=25)
    p.add_argument('--provider', choices=('codex', 'claude'), help='For manual mode')
    p.add_argument('--pool', default='default', help='Manual provider bucket, not project name')
    p.add_argument('--window', choices=sorted(WINDOWS))
    p.add_argument('--used-percent', type=float)
    p.add_argument('--resets-at', help='ISO timestamp with timezone, e.g. 2026-09-08T10:00:00-07:00')
    p.add_argument('--window-minutes', type=float)
    p.add_argument('--credit-balance', type=float)
    p.add_argument('--observed-at', help='Manual observations only; otherwise capture time is used')
    args = p.parse_args()
    for label in (args.account_label, args.machine, args.pool):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}', label): p.error('Labels must use letters, numbers, dashes, or underscores')
    if not 0 < args.timeout <= 120: p.error('--timeout must be between 0 and 120 seconds')
    if args.observed_at and (args.mode != 'manual' or not dt(args.observed_at)): p.error('--observed-at requires manual mode and a timezone')
    if args.mode == 'codex':
        provider, source = 'codex', 'codex_app_server'
        data = quota_buckets(codex_rates(args.codex_bin, args.timeout))
    elif args.mode == 'claude-stdin':
        provider, source = 'claude', 'claude_statusline'
        raw = sys.stdin.buffer.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024: p.error('Status-line input exceeds size bound')
        try: payload = obj(json.loads(raw))
        except ValueError: p.error('Expected the native Claude status-line JSON on stdin')
        data = quota_buckets(obj(payload.get('rate_limits')))
    else:
        provider, source = args.provider, 'manual'
        if not provider: p.error('Manual mode requires --provider')
        if args.used_percent is not None and ((number(args.used_percent) if args.window == 'spend_limit' else percent(args.used_percent)) is None or not args.window):
            p.error('--used-percent requires --window and 0..100 (spend_limit may exceed 100); enter USED, not remaining')
        if args.resets_at and not dt(args.resets_at): p.error('--resets-at requires a timezone')
        if args.credit_balance is not None and number(args.credit_balance) is None: p.error('Invalid credit balance')
        if args.used_percent is None and args.credit_balance is None: p.error('Provide --used-percent or --credit-balance')
        windows = [] if args.used_percent is None else [{'window': args.window, 'used_percent': args.used_percent,
                     'resets_at': stamp(args.resets_at), 'window_minutes': number(args.window_minutes)}]
        data = {'buckets': [{'pool': args.pool, 'windows': windows, 'credit_balance': args.credit_balance}]}
    snap = sanitize_snapshot({'schema': 'rfc-quota.v1', 'provider': provider, 'source': source,
            'observed_at': args.observed_at or datetime.now(UTC).isoformat(), 'data': data,
            'account_label': args.account_label, 'machine': args.machine})
    out = args.out_dir.expanduser(); out.mkdir(parents=True, exist_ok=True)
    path = out / f'{provider}-{datetime.now(UTC):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:10]}.json'
    with path.open('x', encoding='utf-8') as f: json.dump(snap, f, indent=2); f.write('\n')
    if snap['data']['buckets']: print(f'Quota snapshot saved: {path}')
    else: print(f'Quota unavailable/unsupported; recorded as unknown, not zero: {path}')
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (RuntimeError, OSError) as e: raise SystemExit(str(e))
    except KeyboardInterrupt: raise SystemExit('Quota read interrupted; no model turn was started.')
