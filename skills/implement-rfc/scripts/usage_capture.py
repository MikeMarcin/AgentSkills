#!/usr/bin/env python3
"""Offline, allowlisted Claude/Codex history collector. Python 3.11+, standard library.

This is an evidence collector, NOT a subscription meter. It does not execute
transcript commands, invoke models, read auth files, or modify agent settings.
Token observations deliberately remain unsummed: counters and forked history
require reconciliation before they can be turned into trustworthy totals.
"""
from __future__ import annotations

import argparse
import sqlite3
from collections.abc import MutableMapping
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import ntpath
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

VERSION = '2.0.0'
UTC = timezone.utc
TOKEN_KEYS = ('input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens',
              'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens',
              'total_tokens', 'ephemeral_5m_input_tokens', 'ephemeral_1h_input_tokens')
KNOWN_TOOLS = {'Agent', 'Task', 'SendMessage', 'TaskOutput', 'TaskStop', 'Read', 'Grep',
               'Glob', 'Bash', 'Edit', 'Write', 'Skill', 'spawn_agent', 'send_input',
               'resume_agent', 'wait', 'close_agent', 'exec_command', 'write_stdin',
               'apply_patch', 'shell', 'shell_command', 'update_plan', 'wait_agent',
               'list_agents', 'send_message', 'exec', 'parallel', 'multi_tool_use', 'yield'}
AGENT_TOOLS = {'Agent', 'Task', 'spawn_agent'}
CONTROL_TOOLS = {'SendMessage', 'send_input', 'resume_agent', 'wait', 'close_agent',
                 'TaskOutput', 'TaskStop', 'wait_agent', 'list_agents', 'send_message'}
EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'unknown'}
LIMIT_RE = re.compile(r'(?:max(?:imum)?[ _-]?(?:turns?|iterations?)|turn[ -]limit|'
                      r'reached[^\n]{0,60}(?:turn|iteration)|exceeded[^\n]{0,60}(?:turn|iteration))', re.I)
ROLE_RE = re.compile(r'\ARole:\s*(rfc-[a-z-]+)\s*\|')
SECRETS = re.compile(r'(?:sk[-_]|gh[pousr]_|github_pat_|AKIA)[A-Za-z0-9_-]{8,}|'
                     r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+')
SECRET_ASSIGN = re.compile(r'(?i)((?:api[_-]?key|access[_-]?token|password|secret|authorization)'
                           r'\s*[=:]\s*)[^\s,;]+')


def atom(value, default='unknown'):
    if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.<>:-]{1,100}', value) and not SECRETS.search(value):
        return value
    return default


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0 else None


def dt(value):
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return datetime.fromtimestamp(value, UTC)
        if not isinstance(value, str): return None
        out = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return out.astimezone(UTC) if out.tzinfo else None
    except (ValueError, TypeError, OverflowError, OSError): return None


def stamp(value):
    parsed = dt(value)
    return parsed.isoformat() if parsed else None


def obj(value): return value if isinstance(value, dict) else {}


def text(value):
    if isinstance(value, str): return value
    if isinstance(value, list):
        return '\n'.join(v.get('text', '') for v in value if isinstance(v, dict)
                         and v.get('type') in ('text', 'output_text', 'input_text', 'Text')
                         and isinstance(v.get('text'), str))
    return ''


def error_class_candidate(value):
    s = text(value).lower()
    for tag, pattern in [('quota_or_rate_limit', r'rate.limit|usage.limit|hit.{0,20}limit|quota|credit.{0,20}exhaust'),
                         ('overload_or_unavailable', r'overload|unavailable|capacity'),
                         ('auth', r'unauthorized|authentication|invalid.{0,12}key'),
                         ('request_size', r'context.{0,15}(?:large|long|limit)|request.{0,15}size'),
                         ('refusal_or_policy', r'policy|refus|flagged')]:
        if re.search(pattern, s): return tag
    return 'unknown'


def text_info(value):
    s = text(value)
    return {'chars': len(s), 'sha256': digest(s)}


def tokens(value):
    value = obj(value)
    out = {k: value[k] for k in TOKEN_KEYS if number(value.get(k)) is not None}
    # These are subcategories, not extra charges. Keep them nested.
    for k in ('cache_creation', 'input_tokens_details', 'output_tokens_details'):
        details = obj(value.get(k))
        allowed = set(TOKEN_KEYS) | {'cached_tokens', 'reasoning_tokens'}
        picked = {x: v for x, v in details.items() if x in allowed and number(v) is not None}
        if picked: out[k] = picked
    return out


from usage_scope import ScopedProjects, digest, ident, norm, within, git


class Projects(ScopedProjects):
    def __init__(self, specs, aliases=()):
        entries = []
        for spec in specs:
            label, sep, path = spec.partition('=')
            if not sep or not Path(path).is_dir():
                raise ValueError('Use --project LABEL=EXISTING_PATH')
            entries.append({'label': label, 'root': path})
        super().__init__(entries, aliases)

    def preview(self, value, limit):
        s = text(value)
        for name, root in self.roots: s = s.replace(root, f'<{name}>')
        s = s.replace(str(Path.home()), '<HOME>')
        s = SECRETS.sub('<REDACTED_TOKEN>', s)
        s = SECRET_ASSIGN.sub(r'\1<REDACTED>', s)
        # Scrub remaining absolute local paths and URL credentials, best effort only.
        s = re.sub(r'(?i)(https?://)[^\s/@:]+:[^\s/@]+@', r'\1<REDACTED>@', s)
        s = re.sub(r'(?:/Users/|/home/|[A-Za-z]:\\Users\\)[^\s"\']+', '<LOCAL_PATH>', s)
        return s[:limit]

def quota_buckets(value):
    """Allowlist provider quota data. Never export reset credit IDs or account IDs."""
    value = obj(value)
    out = []
    by_id = obj(value.get('rateLimitsByLimitId'))
    roots = list(by_id.items()) if by_id else []
    if not roots:
        root = obj(value.get('rateLimits')) or obj(value.get('rate_limits')) or value
        roots = [(root.get('limitId', root.get('limit_id', 'default')), root)]
    for pool, raw in roots:
        raw = obj(raw)
        windows = []
        for key in ('primary', 'secondary', 'five_hour', 'seven_day', 'spend_limit',
                    'seven_day_opus', 'seven_day_sonnet', 'seven_day_fable'):
            item = obj(raw.get(key))
            if not item: continue
            pct = item.get('usedPercent', item.get('used_percent', item.get('used_percentage', item.get('utilization'))))
            reset = item.get('resetsAt', item.get('resets_at'))
            windows.append({'window': key, 'used_percent': number(pct), 'resets_at': stamp(reset),
                            'window_minutes': number(item.get('windowDurationMins', item.get('window_minutes', item.get('window_duration_mins'))))})
        credits = obj(raw.get('credits'))
        balance = credits.get('balance')
        try: balance = float(balance) if balance is not None else None
        except (TypeError, ValueError): balance = None
        clean = {'pool': atom(pool), 'windows': windows, 'plan_type': atom(raw.get('planType', raw.get('plan_type'))),
                 'credit_balance': number(balance),
                 'has_credits': credits.get('hasCredits', credits.get('has_credits')) if isinstance(credits.get('hasCredits', credits.get('has_credits')), bool) else None,
                 'unlimited_credits': credits.get('unlimited') if isinstance(credits.get('unlimited'), bool) else None}
        if windows or credits: out.append(clean)
    return {'buckets': out,
            'available_reset_count': number(obj(value.get('rateLimitResetCredits')).get('availableCount'))}


class DiskMap(MutableMapping):
    """Temporary SQLite index with one mutable value cached; never exported."""
    def __init__(self):
        self.directory = tempfile.TemporaryDirectory(prefix='rfc-usage-index-')
        self.db = sqlite3.connect(str(Path(self.directory.name) / 'index.sqlite'))
        self.db.execute('PRAGMA cache_size=-2048')
        self.db.execute('CREATE TABLE entries (key TEXT PRIMARY KEY, value TEXT)')
        self.cached = None

    def flush(self):
        if self.cached is not None:
            key, value = self.cached
            self.db.execute('INSERT OR REPLACE INTO entries VALUES (?, ?)', (key, json.dumps(value)))
            self.cached = None

    def __getitem__(self, key):
        encoded = json.dumps(key, sort_keys=True)
        if self.cached is not None and self.cached[0] == encoded:
            return self.cached[1]
        self.flush()
        row = self.db.execute('SELECT value FROM entries WHERE key=?', (encoded,)).fetchone()
        if row is None:
            raise KeyError(key)
        value = json.loads(row[0])
        self.cached = (encoded, value)
        return value

    def __setitem__(self, key, value):
        self.flush()
        self.cached = (json.dumps(key, sort_keys=True), value)

    def __delitem__(self, key):
        self.flush()
        self.db.execute('DELETE FROM entries WHERE key=?', (json.dumps(key, sort_keys=True),))

    def __iter__(self):
        self.flush()
        for row in self.db.execute('SELECT key FROM entries ORDER BY key'):
            yield json.loads(row[0])

    def __len__(self):
        self.flush()
        return self.db.execute('SELECT count(*) FROM entries').fetchone()[0]

    def add(self, key):
        self[key] = True

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
            self.directory.cleanup()

    def __del__(self):
        self.close()


class Collector:
    def __init__(self, projects, start, end, out, max_file, max_line, previews=False):
        self.projects, self.start, self.end, self.out = projects, start, end, out
        if previews and not hasattr(projects, 'preview'):
            projects.preview = lambda value, limit: Projects.preview(projects, value, limit)
        self.max_file, self.max_line, self.previews = max_file, max_line, previews
        self.stats, self.problems, self.files = Counter(), [], []
        self.shapes = Counter()
        self.sessions, self.emitted, self.call_map = DiskMap(), DiskMap(), DiskMap()
        self.counter_baselines = DiskMap()
        self.writer = (out / 'events.jsonl').open('w', encoding='utf-8')

    def issue(self, path, why, line=None):
        self.stats['coverage_warnings'] += 1
        if len(self.problems) < 10000:
            self.problems.append({'source_id': ident(str(path)), 'line': line, 'code': why})

    def rows(self, path):
        try:
            descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
            with os.fdopen(descriptor, 'rb') as f:
                before = os.fstat(f.fileno())
                if self.max_file and before.st_size > self.max_file:
                    self.issue(path, 'file_size_limit'); return
                n = 0
                # Read only the size observed at open: never chase an active writer.
                remaining = before.st_size
                while remaining > 0:
                    raw = f.readline(min(self.max_line + 1, remaining))
                    remaining -= len(raw)
                    self.stats['scan_bytes'] += len(raw)
                    if not raw: break
                    n += 1
                    if len(raw) > self.max_line:
                        self.issue(path, 'line_size_limit', n)
                        while raw and not raw.endswith(b'\n') and remaining > 0:
                            raw = f.readline(min(self.max_line + 1, remaining))
                            remaining -= len(raw)
                            self.stats['scan_bytes'] += len(raw)
                        continue
                    if not raw.endswith(b'\n'):
                        self.issue(path, 'unterminated_snapshot_tail', n); continue
                    try:
                        value = json.loads(raw)
                        if not isinstance(value, dict): raise ValueError()
                    except (ValueError, UnicodeError):
                        self.issue(path, 'invalid_json_line', n); continue
                    shape = (atom(value.get('type')), atom(obj(value.get('payload')).get('type')))
                    if len(self.shapes) >= 1024 and shape not in self.shapes:
                        shape = ('other', 'other')
                    self.shapes[shape] += 1
                    yield n, value
            after = path.stat()
            if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
                self.issue(path, 'file_changed_while_reading')
        except OSError: self.issue(path, 'unreadable_history')

    def emit(self, session, kind, when, source, line, **data):
        parsed = dt(when)
        if parsed is None:
            self.issue(source, 'missing_or_invalid_event_timestamp', line); return
        if kind == 'token_observation' and parsed < self.start and parsed >= dt(self.counter_baselines.get(session['key'], {}).get('timestamp', '0001-01-01T00:00:00Z')):
            self.counter_baselines[session['key']] = {
                'session': session['key'], 'provider': session['provider'], 'project': session['project'],
                'timestamp': parsed.isoformat(), 'source_id': ident(str(source)), 'line': line,
                'baseline_only_not_activity': True, **data}
        if not self.start <= parsed < self.end: return
        value = {'session': session['key'], 'provider': session['provider'], 'project': session['project'],
                 'kind': kind, 'timestamp': parsed.isoformat(), **data}
        if session.get('ownership_conflict'):
            value['ownership'] = 'native_session_project_conflict'
        key = digest(value)
        if key in self.emitted:
            self.stats['duplicate_normalized_events'] += 1; return
        self.emitted.add(key)
        value['event_id'] = key
        value['source_id'], value['line'] = ident(str(source)), line
        self.writer.write(json.dumps(value, sort_keys=True) + '\n')
        self.stats['event_' + kind] += 1
        session['first_observed'] = min(session.get('first_observed', value['timestamp']), value['timestamp'])
        session['last_observed'] = max(session.get('last_observed', value['timestamp']), value['timestamp'])
        session['events'] += 1

    def session(self, provider, native, agent, project, role, parent, path):
        key = ident(provider + ':' + str(native) + (':' + str(agent) if agent else ''))
        out = self.sessions.setdefault(key, {'key': key, 'provider': provider, 'project': project,
            'session_id': ident(native), 'agent_id': ident(agent), 'parent_agent_id': ident(parent),
            'kind': 'subagent' if agent or parent else 'primary', 'role': atom(role),
            'role_evidence': 'runtime_metadata' if role else 'unknown', 'events': 0,
            'source_ids': []})
        sid = ident(str(path))
        if sid not in out['source_ids'] and len(out['source_ids']) < 100: out['source_ids'].append(sid)
        if out['project'] != project:
            self.issue(path, 'native_session_project_conflict')
            out = {**out, 'project': project, 'ownership_conflict': True}
        return out

    def tool_call(self, session, source, line, when, cid, name, args, ownership='local', scope=None):
        args = obj(args)
        short = str(name).split('.')[-1]
        canonical = short if short in KNOWN_TOOLS else 'other'
        scope = scope or session['key']
        self.call_map[(scope, str(cid))] = canonical
        values = {'call_id': ident(cid), 'tool': canonical, 'tool_name_id': ident(name),
                  'argument_chars': len(json.dumps(args, ensure_ascii=False)), 'argument_sha256': digest(args),
                  'ownership': ownership}
        for field in ('file_path', 'path', 'workdir', 'cwd'):
            if isinstance(args.get(field), str): values[field] = self.projects.path_info(args[field])
        command = args.get('command', args.get('cmd'))
        if command is not None:
            cmd = command if isinstance(command, str) else json.dumps(command)
            values['command_chars'], values['command_sha256'] = len(cmd), digest(cmd)
            values['instruction_read_hint'] = any(x in cmd for x in ('AGENTS.md', 'CLAUDE.md', 'SKILL.md', 'implement-rfc'))
        if canonical in AGENT_TOOLS:
            prompt = args.get('prompt', args.get('message', ''))
            values.update({'requested_role': atom(args.get('subagent_type', args.get('agent_type'))),
                           'requested_model': atom(args.get('model')),
                           'requested_effort': atom(args.get('effort', args.get('model_reasoning_effort'))),
                           'background': args.get('run_in_background') if isinstance(args.get('run_in_background'), bool) else None,
                           'prompt': text_info(prompt), 'resume_target': ident(args.get('resume'))})
            if self.previews: values['prompt_preview'] = self.projects.preview(prompt, 1500)
        if canonical in CONTROL_TOOLS:
            target = args.get('to', args.get('id', args.get('agent_id', args.get('task_id', args.get('recipient', args.get('receiver', args.get('target')))))))
            values['target'] = ident(target)
            targets = args.get('ids', args.get('agent_ids', args.get('targets', [])))
            values['targets'] = [ident(v) for v in targets[:4096]] if isinstance(targets, list) else []
        # Static observation only: do not evaluate JS, shell, or nested expressions.
        nested = args.get('tool_uses', args.get('calls'))
        if isinstance(nested, list):
            values['nested_tool_names'] = [atom(obj(v).get('recipient_name', obj(v).get('name'))) for v in nested[:256]]
        self.emit(session, 'tool_call', when, source, line, **values)

    def tool_result(self, session, source, line, when, cid, content, error=None, scope=None, ownership='local'):
        scope = scope or session['key']
        name = self.call_map.get((scope, str(cid)), 'unknown')
        s = text(content)
        values = {'call_id': ident(cid), 'tool': name, 'output': text_info(content), 'ownership': ownership,
                  'is_error': error if isinstance(error, bool) else None}
        if name in AGENT_TOOLS:
            # Only an actual Agent/Task tool-result is eligible; a Bash grep of
            # a transcript or an assistant quote is NEVER a lifecycle marker.
            match = re.search(r'(?m)^\s*agentId:\s*([A-Za-z0-9_-]+)', s)
            if match: values['returned_agent_id'] = ident(match.group(1))
            values['turn_limit_text_candidate'] = bool(LIMIT_RE.search(s))
            values['partial_text_candidate'] = bool(re.search(r'\bpartial\b|terminated early|cut off', s, re.I))
            values['marker_confidence'] = 'candidate_only; tool output text can quote other text'
            if self.previews: values['result_preview'] = self.projects.preview(s, 1500)
        self.emit(session, 'tool_result', when, source, line, **values)

    def claude(self, path):
        metadata = {}
        mpath = path.with_suffix('.meta.json')
        if mpath.is_file():
            try:
                if mpath.stat().st_size <= 1024 * 1024: metadata = obj(json.loads(mpath.read_bytes()))
                else: self.issue(mpath, 'metadata_size_limit')
            except (OSError, ValueError): self.issue(mpath, 'invalid_agent_metadata')
        # Detect project from runtime cwd, not the lossy directory-name encoding.
        header = []
        iterator = self.rows(path)
        project, native = None, None
        for n, e in iterator:
            header.append((n, e))
            native = native or e.get('sessionId')
            if e.get('cwd'):
                project = self.projects.match(e['cwd'])
                if project: break
                self.stats['files_outside_selected_projects'] += 1; return
            if len(header) >= 128: break
        if not project:
            self.stats['files_project_unresolved'] += 1; return
        if not native:
            self.issue(path, 'missing_claude_session_id'); native = str(path)
        agent = next((e.get('agentId') for _, e in header if e.get('agentId')), None)
        if not agent and path.stem.startswith('agent-'): agent = path.stem[6:]
        session = self.session('claude', native, agent, project, metadata.get('agentType'), metadata.get('parentAgentId'), path)
        session['launch_tool_use_id'] = ident(metadata.get('toolUseId'))
        session['harness_version'] = atom(next((e.get('version') for _, e in header if e.get('version')), None))
        import itertools
        for line, e in itertools.chain(header, iterator):
            when = e.get('timestamp')
            if e.get('cwd') and self.projects.match(e['cwd']) != project:
                self.issue(path, 'session_changed_project', line); continue
            typ = e.get('type')
            message = obj(e.get('message')); content = message.get('content', [])
            if typ == 'assistant':
                model = message.get('model')
                synthetic = model == '<synthetic>' or e.get('isApiErrorMessage') is True
                msgid = message.get('id')
                if not msgid: self.issue(path, 'assistant_missing_response_id', line)
                self.emit(session, 'assistant_record', when, path, line,
                          response_id=ident(msgid), event_uuid=ident(e.get('uuid')),
                          model=atom(model), effort=atom(e.get('effort')),
                          synthetic_or_api_error=synthetic, stop_reason=atom(message.get('stop_reason')),
                          error_class_text_candidate=error_class_candidate(content) if synthetic else None,
                          usage=tokens(message.get('usage')), visible_text=text_info(content))
                banner = ROLE_RE.search(text(content).strip())
                if session['role'] in ('unknown', 'general-purpose') and banner:
                    session['role'], session['role_evidence'] = banner.group(1), 'assistant_banner_self_report'
                if self.previews and text(content):
                    self.emit(session, 'assistant_text_preview', when, path, line, response_id=ident(msgid),
                              preview=self.projects.preview(content, 1500))
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get('type') == 'tool_use':
                            self.tool_call(session, path, line, when, b.get('id'), b.get('name'), b.get('input'))
            elif typ == 'user':
                tr = obj(e.get('toolUseResult'))
                if tr:
                    self.emit(session, 'harness_tool_summary', when, path, line,
                              returned_agent_id=ident(tr.get('agentId')),
                              total_tokens_inclusive_do_not_add=number(tr.get('totalTokens')),
                              total_duration_ms=number(tr.get('totalDurationMs')),
                              total_tool_uses=number(tr.get('totalToolUseCount')),
                              status=atom(tr.get('status')), usage_inclusive_do_not_add=tokens(tr.get('usage')))
                self.emit(session, 'user_record', when, path, line, event_uuid=ident(e.get('uuid')), visible_text=text_info(content))
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get('type') == 'tool_result':
                            self.tool_result(session, path, line, when, b.get('tool_use_id'), b.get('content'), b.get('is_error'))
            elif typ == 'system':
                self.emit(session, 'system_marker', when, path, line, subtype=atom(e.get('subtype')),
                          event_uuid=ident(e.get('uuid')))
            elif typ == 'result':
                self.emit(session, 'runtime_result', when, path, line,
                          subtype=atom(e.get('subtype')), is_error=e.get('is_error') if isinstance(e.get('is_error'), bool) else None,
                          num_turns=number(e.get('num_turns')), duration_ms=number(e.get('duration_ms')),
                          duration_api_ms=number(e.get('duration_api_ms')),
                          aggregate_usage_do_not_add=tokens(e.get('usage')),
                          model_usage_aggregate_do_not_add={atom(k): tokens(v) for k,v in obj(e.get('modelUsage')).items()},
                          reported_total_cost_usd_not_subscription_debit=number(e.get('total_cost_usd')))
            # Native rates, when actually present; never scrape their textual rendering.
            if isinstance(e.get('rate_limits'), dict):
                self.emit(session, 'quota_observation', when, path, line, data=quota_buckets(e['rate_limits']), observation_source='claude_history')

    def codex(self, path):
        iterator = self.rows(path)
        first = next(iterator, None)
        if first is None: return
        _, e = first
        p = obj(e.get('payload'))
        if e.get('type') != 'session_meta': self.issue(path, 'missing_codex_session_meta'); return
        project = self.projects.match(p.get('cwd'))
        if not project:
            self.stats['files_outside_selected_projects' if p.get('cwd') else 'files_project_unresolved'] += 1; return
        native = p.get('id')
        if not native: self.issue(path, 'missing_codex_session_id'); return
        raw_sub = obj(p.get('source')).get('subagent')
        sub = obj(raw_sub); spawn = obj(sub.get('thread_spawn'))
        parent = p.get('parent_thread_id') or spawn.get('parent_thread_id')
        is_child = bool(raw_sub or parent or p.get('thread_source') == 'subagent')
        session = self.session('codex', native, None, project, p.get('agent_role') or spawn.get('agent_role'), parent, path)
        session['kind'] = 'subagent' if is_child else 'primary'
        session['harness_version'] = atom(p.get('cli_version'))
        session['forked_from'] = ident(p.get('forked_from_id'))
        owned_turns = DiskMap(); turn = None; contexts = DiskMap(); scope_changed = False
        for line, e in iterator:
            p = obj(e.get('payload')); typ = e.get('type'); when = e.get('timestamp')
            t = p.get('turn_id')
            if p.get('thread_id') == native and t: owned_turns.add(t); turn = t
            if typ == 'turn_context':
                if p.get('cwd'):
                    scope_changed = self.projects.match(p['cwd']) != project
                    if scope_changed:
                        self.issue(path, 'codex_session_changed_project', line)
                if scope_changed:
                    continue
                turn = t or turn
                contexts[turn] = {'model': atom(p.get('model')), 'effort': atom(p.get('effort', p.get('reasoning_effort'))),
                                  'service_tier': atom(p.get('service_tier'))}
                self.emit(session, 'model_context', when, path, line, turn_id=ident(turn), **contexts[turn])
                continue
            if scope_changed:
                continue
            ownership = 'explicit' if p.get('thread_id') == native or t in owned_turns else (
                'uncertain_fork_or_child' if is_child or session['forked_from'] else 'primary_log')
            context = contexts.get(t or turn, {'model': 'unknown', 'effort': 'unknown', 'service_tier': 'unknown'})
            if typ == 'event_msg':
                name = p.get('type')
                if name == 'token_count':
                    info = obj(p.get('info'))
                    self.emit(session, 'token_observation', when, path, line, turn_id=ident(t or turn),
                              ownership=ownership, context_is_configuration_not_response=True, **context,
                              cumulative=tokens(info.get('total_token_usage')),
                              last=tokens(info.get('last_token_usage')),
                              context_window=number(info.get('model_context_window')))
                    if isinstance(p.get('rate_limits'), dict):
                        self.emit(session, 'quota_observation', when, path, line, data=quota_buckets(p['rate_limits']), observation_source='codex_history')
                elif name in ('task_started', 'task_complete', 'turn_aborted', 'thread_rolled_back', 'error', 'warning',
                              'item_started', 'item_completed', 'turn_started', 'turn_complete'):
                    self.emit(session, 'runtime_marker', when, path, line, marker=name, turn_id=ident(t or turn),
                              ownership=ownership, item_type=atom(obj(p.get('item')).get('type')),
                              agent_message_text=text_info(obj(p.get('item')).get('content'))
                              if obj(p.get('item')).get('type') == 'AgentMessage' else None)
            elif typ == 'response_item':
                name = p.get('type')
                if name in ('function_call', 'custom_tool_call'):
                    args = p.get('arguments', p.get('input', {}))
                    if isinstance(args, str):
                        try: args = json.loads(args)
                        except ValueError: args = {'opaque_argument_sha256': digest(args), 'opaque_argument_chars': len(args)}
                    self.tool_call(session, path, line, when, p.get('call_id'), p.get('name'), args, ownership)
                elif name in ('function_call_output', 'custom_tool_call_output'):
                    self.tool_result(session, path, line, when, p.get('call_id'), p.get('output'), ownership=ownership)
                elif name == 'message':
                    self.emit(session, 'message_record', when, path, line, message_role=atom(p.get('role')),
                              channel=atom(p.get('channel')), ownership=ownership,
                              visible_text=text_info(p.get('content')))
                # Reasoning content, encrypted blobs, and summaries are never copied.
            elif typ == 'compacted': self.emit(session, 'compaction', when, path, line, ownership=ownership)

    def scan(self, claude_home, codex_home):
        started = time.monotonic()
        def history_paths():
            for provider, roots in (('claude', [claude_home / 'projects']),
                                    ('codex', [codex_home / 'sessions', codex_home / 'archived_sessions'])):
                for root in roots:
                    if not root.is_dir():
                        self.stats[provider + '_missing_roots'] += 1; continue
                    # No following symlink directories. Deduplicate file identities later.
                    for base, dirs, names in os.walk(root, followlinks=False):
                        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules')]
                        for name in sorted(names):
                            if name.endswith('.jsonl') and not name.startswith('._'):
                                yield provider, Path(base) / name
        seen = DiskMap()
        for provider, path in history_paths():
            if path.is_symlink(): self.issue(path, 'symlink_history_skipped'); continue
            try:
                stat = path.stat()
                physical = (stat.st_dev, stat.st_ino) if stat.st_ino else str(path.resolve())
                if physical in seen: self.stats['duplicate_physical_files'] += 1; continue
                seen.add(physical)
            except OSError: self.issue(path, 'unreadable_history'); continue
            self.stats['history_files_visited'] += 1
            if self.stats['history_files_visited'] % 100 == 0:
                print(f"Scanned {self.stats['history_files_visited']} history files", file=sys.stderr)
            if len(self.files) < 10000:
                self.files.append({'id': ident(str(path)), 'provider': provider, 'bytes': stat.st_size})
            else:
                self.stats['file_inventory_rows_omitted'] += 1
            try: getattr(self, provider)(path)
            except (ValueError, TypeError, AttributeError, KeyError, RecursionError):
                self.issue(path, 'unsupported_record_shape')
        seen.close()
        self.stats["scan_seconds"] = time.monotonic() - started
        try:
            import resource
            self.stats['peak_process_rss_native_units'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        except ImportError:
            self.stats['peak_process_rss_unavailable'] = 1
        self.writer.close()


def inventory(projects, claude_home, codex_home):
    """Lengths/hashes and a narrow routing allowlist; no full settings or instructions."""
    rows, config = [], []
    seen = set()
    for label, root in projects.primary:
        candidates = [root / 'AGENTS.md', root / 'CLAUDE.md']
        for relative in ('.agents/skills/implement-rfc', '.claude/agents', '.codex/agents'):
            folder = root / relative
            if folder.is_dir():
                candidates += [p for p in folder.rglob('*') if p.is_file()
                               and p.suffix in ('.md', '.toml', '.json', '.yaml')
                               and '__pycache__' not in p.parts and not p.name.startswith('._')]
        candidates += [root / '.mask/skill-config/implement-rfc/project.json',
                       root / '.mask/skill-config/implement-rfc/project.md']
        for path in candidates:
            if not path.is_file(): continue
            key = (label, str(path))
            if key in seen: continue
            seen.add(key)
            try:
                if path.stat().st_size > 2 * 1024 * 1024: continue
                raw = path.read_bytes(); s = raw.decode('utf-8', errors='replace')
                rel = str(path.relative_to(root)).replace('\\', '/')
                row = {'project': label, 'path': rel, 'bytes': len(raw), 'chars': len(s),
                       'lines': len(s.splitlines()), 'words_whitespace': len(s.split()), 'sha256': digest(raw)}
                if path.suffix in ('.md', '.toml'):
                    fm = {}
                    for field in ('model', 'effort', 'model_reasoning_effort', 'maxTurns', 'name'):
                        m = re.search(r'^' + re.escape(field) + r'\s*[:=]\s*["\']?([^\s"\'\n]+)', s, re.M)
                        if m: fm[field] = atom(m.group(1))
                    row['declared_frontmatter'] = fm
                if path.name == 'routing.json':
                    data = obj(json.loads(s)); clean = {}
                    for provider, pd in obj(data.get('providers')).items():
                        clean[atom(provider)] = {atom(k): {'model': atom(obj(v).get('model')), 'effort': atom(obj(v).get('effort'))}
                                                  for k, v in obj(obj(pd).get('classes')).items()}
                    row['routing'] = clean
                    row['assignments'] = {atom(k): atom(v) for k, v in obj(data.get('assignments')).items()}
                rows.append(row)
            except (OSError, ValueError): rows.append({'project': label, 'path_id': ident(str(path)), 'error': 'unreadable'})
    # User-scope instruction sizes: these may apply even when a project has no local copy.
    for provider, home, names in [('claude', claude_home, ['CLAUDE.md']), ('codex', codex_home, ['AGENTS.md', 'AGENTS.override.md'])]:
        candidates = [home / name for name in names]
        agents = home / 'agents'
        if agents.is_dir(): candidates += [p for p in agents.glob('*') if p.suffix in ('.md', '.toml') and p.is_file()]
        for path in candidates:
            if not path.is_file(): continue
            try:
                if path.stat().st_size > 2 * 1024 * 1024: continue
                raw = path.read_bytes(); st = raw.decode('utf-8', errors='replace')
                rows.append({'project': None, 'provider': provider, 'scope': 'user', 'path_id': ident(str(path)),
                             'basename': path.name if path.name in names or path.stem.startswith('rfc-') else 'custom-agent',
                             'bytes': len(raw), 'chars': len(st), 'lines': len(st.splitlines()), 'sha256': digest(raw)})
            except OSError: rows.append({'provider': provider, 'scope': 'user', 'error': 'unreadable'})
    # Never open auth.json, .credentials.json, the keychain, or environment dumps.
    paths = [('claude', claude_home / 'settings.json'), ('claude', claude_home / 'settings.local.json'),
             ('codex', codex_home / 'config.toml')]
    for label, root in projects.primary:
        paths += [('claude', root / '.claude/settings.json'), ('claude', root / '.claude/settings.local.json'),
                  ('codex', root / '.codex/config.toml')]
    allowed = ('model', 'effortLevel', 'model_reasoning_effort', 'service_tier', 'fallbackModel',
               'switchModelsOnFlag', 'cleanupPeriodDays', 'model_context_window', 'model_auto_compact_token_limit')
    for provider, path in paths:
        if not path.is_file(): continue
        row = {'provider': provider, 'source_id': ident(str(path)), 'project': projects.match(str(path)), 'settings': {}}
        try:
            if path.stat().st_size > 2 * 1024 * 1024: raise ValueError()
            s = path.read_text(encoding='utf-8')
            if path.suffix == '.toml':
                try:
                    import tomllib
                    data = tomllib.loads(s)
                except ImportError:
                    data = {}; row['coverage'] = 'toml_requires_python_3_11; file_presence_only'
            else: data = obj(json.loads(s))
            for field in allowed:
                v = data.get(field)
                if isinstance(v, bool) or number(v) is not None: row['settings'][field] = v
                elif isinstance(v, str): row['settings'][field] = atom(v)
                elif isinstance(v, list): row['settings'][field] = [atom(x) for x in v[:10]]
            row['statusline_configured'] = isinstance(data.get('statusLine'), dict)
            row['hook_event_names'] = [atom(x) for x in obj(data.get('hooks'))]
            row['mcp_server_count'] = len(obj(data.get('mcpServers', data.get('mcp_servers'))))
            row['model_override_count'] = len(obj(data.get('modelOverrides')))
        except (OSError, ValueError): row['coverage'] = 'settings_unreadable'
        config.append(row)
    env = {k: atom(os.environ[k]) for k in ('CLAUDE_CODE_SUBAGENT_MODEL', 'CLAUDE_CODE_EFFORT_LEVEL',
                                          'CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH') if k in os.environ}
    return {'instruction_inventory': rows, 'config_allowlist': config, 'environment_allowlist': env,
            'limitations': 'Shell environment only; live CLI process/managed settings may differ. File size is not injected tokens.'}


def boundary(value):
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value): return datetime.fromisoformat(value).replace(tzinfo=UTC)
    result = dt(value)
    if result is None: raise argparse.ArgumentTypeError('Use YYYY-MM-DD (UTC) or a timestamp with timezone')
    return result

