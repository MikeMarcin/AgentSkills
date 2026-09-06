#!/usr/bin/env python3
"""Read local Codex/Claude subagent history without modifying runtime state."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
import ntpath
import os
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA = 'implement-rfc.role-usage.v1'
BANNER = re.compile(r'\ARole: (rfc-[a-z-]+) \| Model: ([^|\n]+) \| Effort: ([^\n]+)(?:\n|$)')
DECISION = re.compile(r'^Routing: (routine|deep|unknown) \| Reason: ([^\n]+)$', re.M)
UNKNOWN = '<unknown>'


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed if parsed.tzinfo else None
    except ValueError:
        return None


def same_project(left, right):
    if not left:
        return False
    if ntpath.splitdrive(left)[0] or ntpath.splitdrive(right)[0]:
        return ntpath.normcase(ntpath.normpath(left)) == ntpath.normcase(ntpath.normpath(right))
    return Path(left).resolve() == Path(right).expanduser().resolve()


def text_blocks(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ''
    return '\n'.join(b.get('text', '') for b in content
                     if isinstance(b, dict) and isinstance(b.get('text'), str)
                     and b.get('type') in ('text', 'Text', 'output_text'))


class Audit:
    def __init__(self, day, tz, repo=None, role=None):
        self.day, self.tz, self.repo, self.role = day, tz, repo, role
        self.records, self.issues, self.sources, self.attempts = [], [], [], []
        self.identities = set()

    def issue(self, path, detail, line=None):
        self.issues.append({'path': str(path), 'line': line, 'detail': detail})

    def events(self, path):
        try:
            with path.open(encoding='utf-8') as stream:
                for line, raw in enumerate(stream, 1):
                    try:
                        value = json.loads(raw)
                        if not isinstance(value, dict):
                            raise ValueError('not an object')
                    except ValueError:
                        self.issue(path, 'Invalid JSON object; line skipped', line)
                        continue
                    yield line, value
        except (OSError, UnicodeError):
            self.issue(path, 'History file could not be read')

    def on_day(self, value):
        parsed = timestamp(value)
        return bool(parsed and parsed.astimezone(self.tz).date() == self.day)

    def markers(self, record, text, path, line):
        if record['role'] not in ('rfc-worker', 'rfc-worker-routine'):
            return
        # Decisions belong beside the startup identity or final Status, not in
        # quoted examples later in an assistant's prose.
        opening = text.strip().splitlines()[:6]
        opening = opening[:next((i for i, value in enumerate(opening)
                                 if value.lstrip().startswith(('```', '~~~'))), len(opening))]
        for match in DECISION.finditer('\n'.join(opening)):
            decision = {'choice': match[1], 'reason': match[2][:500], 'path': str(path), 'line': line}
            if not any((d['choice'], d['reason']) == (decision['choice'], decision['reason'])
                       for d in record['routing_decisions']):
                record['routing_decisions'].append(decision)

    def base(self, driver, identity, path, role=None, parent=None, cwd=None, created=None):
        return {'driver': driver, 'executor': driver, 'id': identity, 'parent_id': parent,
                'role': role or UNKNOWN, 'role_evidence': 'metadata' if role else 'unknown',
                'project': cwd, 'created': created, 'source': str(path),
                'activity_unit': 'turn' if driver == 'codex' else 'response',
                'activity': [], 'routing_decisions': []}

    def keep(self, record):
        if self.repo and not same_project(record['project'], self.repo):
            return
        if self.role and record['role'] != self.role:
            return
        born = self.on_day(record['created'])
        if not born and not record['activity']:
            return
        identity = (record['driver'], record['id'])
        if identity in self.identities:
            self.issue(record['source'], 'Duplicate agent identity; inspect both histories (not counted twice)')
            return
        self.identities.add(identity)
        record['created_on_date'] = born
        self.records.append(record)

    def read_agent(self, reader, path):
        try:
            reader(path)
        except (TypeError, ValueError, AttributeError):
            self.issue(path, 'Unsupported history field shape; agent skipped')

    def codex(self, home):
        roots = [home / 'sessions', home / 'archived_sessions']
        present = [root for root in roots if root.is_dir()]
        self.sources.append({'driver': 'codex', 'roots': [str(p) for p in roots],
                             'available': bool(present)})
        if not present:
            self.issue(home, 'Codex session directories unavailable; coverage unknown')
        for root in present:
            for path in sorted(root.rglob('*.jsonl')):
                self.read_agent(self.codex_file, path)

    def codex_file(self, path):
        events = self.events(path)
        first = next(events, None)
        if first is None:
            self.issue(path, 'Empty or unreadable Codex history')
            return
        _, meta = first
        payload = meta.get('payload') or {}
        if meta.get('type') != 'session_meta' or not isinstance(payload, dict):
            self.issue(path, 'Missing Codex session metadata')
            return
        source = payload.get('source')
        subagent = source.get('subagent') if isinstance(source, dict) else None
        if not subagent and payload.get('thread_source') != 'subagent':
            return  # Primary work is outside the role census.
        spawn = subagent.get('thread_spawn', {}) if isinstance(subagent, dict) else {}
        identity = payload.get('id')
        if not identity:
            self.issue(path, 'Missing Codex child identity')
            return
        record = self.base('codex', identity, path,
                           payload.get('agent_role') or spawn.get('agent_role'),
                           payload.get('parent_thread_id') or spawn.get('parent_thread_id'),
                           payload.get('cwd'), payload.get('timestamp') or meta.get('timestamp'))
        if self.repo and not same_project(record['project'], self.repo):
            return
        if self.role and record['role'] != self.role:
            return
        if not timestamp(record['created']):
            self.issue(path, 'Invalid or missing Codex creation timestamp')
        contexts, owned = {}, {}
        for line, event in events:
            p = event.get('payload') or {}
            if not isinstance(p, dict):
                self.issue(path, 'Invalid Codex payload', line)
                continue
            turn = p.get('turn_id')
            if event.get('type') == 'turn_context' and turn:
                context = {'model': p.get('model'), 'effort': p.get('effort'), 'line': line}
                previous = contexts.setdefault(turn, [])
                if not any((c['model'], c['effort']) == (context['model'], context['effort']) for c in previous):
                    previous.append(context)
            # Forked history carries parent turns with fresh serialization dates.
            # Only explicit child-owned events establish that this child ran.
            if p.get('thread_id') != identity or not turn:
                continue
            if not timestamp(event.get('timestamp')):
                self.issue(path, 'Invalid or missing child-owned event timestamp', line)
                continue
            if not self.on_day(event.get('timestamp')):
                continue
            owned.setdefault(turn, {'id': turn, 'timestamp': event['timestamp'], 'line': line})
            item = p.get('item') or {}
            if p.get('type') == 'item_completed' and isinstance(item, dict) and item.get('type') == 'AgentMessage':
                self.markers(record, text_blocks(item.get('content')), path, line)
        for turn, activity in owned.items():
            activity['observations'] = contexts.get(turn, [])
            if not activity['observations']:
                self.issue(path, f'Owned turn {turn} has no recorded model context')
            record['activity'].append(activity)
        if self.on_day(record['created']) and not owned:
            self.issue(path, 'Child created on date, but no child-owned activity found; execution unknown')
        self.keep(record)

    def claude(self, home):
        root = home / 'projects'
        self.sources.append({'driver': 'claude', 'roots': [str(root)], 'available': root.is_dir()})
        if not root.is_dir():
            self.issue(root, 'Claude projects directory unavailable; coverage unknown')
            return
        paths = set(root.glob('*/**/subagents/agent-*.jsonl'))
        # Older Claude Code versions kept sidechains directly under the project.
        paths.update(root.glob('*/agent-*.jsonl'))
        for path in sorted(paths):
            self.read_agent(self.claude_file, path)

    def claude_file(self, path):
        meta_path = path.with_suffix('.meta.json')
        metadata = {}
        if meta_path.exists():
            try:
                metadata = json.loads(meta_path.read_text(encoding='utf-8'))
                if not isinstance(metadata, dict):
                    raise ValueError('metadata is not an object')
            except (OSError, UnicodeError, ValueError):
                self.issue(meta_path, 'Claude metadata is not a readable JSON object')
                metadata = {}
        identity = path.stem.removeprefix('agent-')
        record = self.base('claude', identity, path, metadata.get('agentType'))
        if self.role and record['role'] not in (UNKNOWN, 'general-purpose', self.role):
            return
        observations = {}
        seen_identity, session_id, event_count = None, None, 0
        for line, event in self.events(path):
            event_count += 1
            session_id = session_id or event.get('sessionId')
            if event.get('agentId'):
                if seen_identity and seen_identity != event['agentId']:
                    self.issue(path, 'Conflicting Claude agent identity', line)
                    continue
                seen_identity = event['agentId']
                record['id'] = seen_identity
            record['parent_id'] = metadata.get('parentAgentId') or event.get('sessionId') or record['parent_id']
            record['project'] = record['project'] or event.get('cwd')
            stamp = event.get('timestamp')
            if event.get('type') in ('user', 'assistant') and not timestamp(stamp):
                self.issue(path, 'Invalid or missing Claude message timestamp', line)
            if timestamp(stamp) and (not record['created'] or timestamp(stamp) < timestamp(record['created'])):
                record['created'] = stamp
            if event.get('type') != 'assistant':
                continue
            message = event.get('message') or {}
            if not isinstance(message, dict):
                self.issue(path, 'Invalid Claude assistant message', line)
                continue
            text = text_blocks(message.get('content'))
            # Never identify roles from prompts, tool output, task descriptions or model names.
            banners = BANNER.findall(text.strip())
            if record['role'] in (UNKNOWN, 'general-purpose') and banners:
                roles = {b[0] for b in banners}
                if len(roles) == 1:
                    record['role'] = roles.pop()
                    record['role_evidence'] = 'assistant-banner (self-report)'
            if not self.on_day(stamp):
                continue
            self.markers(record, text, path, line)
            response = message.get('id')
            if not response:
                self.issue(path, 'Claude assistant message has no response ID; not counted', line)
                continue
            observation = {'model': message.get('model'), 'effort': event.get('effort'), 'line': line}
            # Streaming records can repeat a response ID for multiple content blocks.
            activity = observations.setdefault(response, {'id': response, 'timestamp': stamp,
                                                          'line': line, 'observations': []})
            if not any((o['model'], o['effort']) == (observation['model'], observation['effort'])
                       for o in activity['observations']):
                activity['observations'].append(observation)
        if not event_count:
            self.issue(path, 'Empty or unreadable Claude history')
        record['activity'] = list(observations.values())
        # Agent IDs are scoped to their parent session, not globally unique.
        record['id'] = f"{session_id or path.parent}:{record['id']}"
        self.keep(record)

    def lanes(self, paths):
        for path in paths:
            for line, event in self.events(path):
                if not timestamp(event.get('timestamp')):
                    self.issue(path, 'Invalid or missing companion attempt timestamp', line)
                    continue
                if not self.on_day(event.get('timestamp')):
                    continue
                if self.repo and not same_project(event.get('cwd'), self.repo):
                    continue
                if self.role and event.get('role') != self.role:
                    continue
                self.attempts.append({'driver': 'claude', 'executor': 'codex',
                    'role': event.get('role'), 'timestamp': event.get('timestamp'),
                    'project': event.get('cwd'), 'configured_model': event.get('model'),
                    'configured_effort': event.get('effort'), 'path': str(path), 'line': line,
                    'evidence': 'companion launch attempt; execution not established'})

    def report(self):
        groups = {}
        for record in self.records:
            key = record['driver'], record['role']
            group = groups.setdefault(key, {'driver': key[0], 'role': key[1], 'agents_created': 0,
                'agents_active': 0, 'activity_count': 0, 'activity_unit': record['activity_unit'],
                'models': Counter(), 'agents_without_routing_reason': 0})
            group['agents_created'] += int(record['created_on_date'])
            group['agents_active'] += bool(record['activity'])
            group['activity_count'] += len(record['activity'])
            if record['role'] in ('rfc-worker', 'rfc-worker-routine'):
                group['agents_without_routing_reason'] += not any(d['choice'] != 'unknown' for d in record['routing_decisions'])
            for activity in record['activity']:
                for observation in activity['observations']:
                    group['models'][observation['model'], observation['effort']] += 1
        summary = []
        for _, group in sorted(groups.items()):
            group['models'] = [{'model': model, 'effort': effort, 'observations': count}
                               for (model, effort), count in group['models'].items()]
            summary.append(group)
        return {'schema': SCHEMA, 'date': self.day.isoformat(), 'timezone': str(self.tz),
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'status': 'partial' if self.issues else 'ok', 'sources': self.sources,
                'scope': 'Local retained subagent history only. Primary work and remote hosts excluded. '
                         'Codex turns and Claude responses are different units, not billing. '
                         'Model observations come from runtime records; reasons/banners are self-reports. '
                         'No current-route comparison implies historical correctness.',
                'summary': summary, 'agents': self.records, 'launch_attempts': self.attempts,
                'issues': self.issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--driver', choices=['codex', 'claude', 'both'], default='both')
    parser.add_argument('--date', type=date.fromisoformat, help='YYYY-MM-DD; default today in selected timezone')
    parser.add_argument('--timezone', default='UTC', help='IANA zone, e.g. America/Los_Angeles; default UTC')
    parser.add_argument('--repo-root', help='Exact recorded project root filter; no consumer config required')
    parser.add_argument('--role', help='Exact role filter')
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    parser.add_argument('--claude-home', type=Path, default=Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home() / '.claude'))))
    parser.add_argument('--lane-log', action='append', type=Path, default=[], help='Explicit Claude-driven Codex companion log; repeatable, attempts only')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        tz = timezone.utc if args.timezone == 'UTC' else ZoneInfo(args.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        parser.error('timezone unavailable; use UTC or install system IANA timezone data/tzdata')
    if args.lane_log and args.driver == 'codex':
        parser.error('--lane-log describes Claude-driven launches; select claude or both')
    audit = Audit(args.date or datetime.now(tz).date(), tz, args.repo_root, args.role)
    if args.driver in ('codex', 'both'):
        audit.codex(args.codex_home.expanduser())
    if args.driver in ('claude', 'both'):
        audit.claude(args.claude_home.expanduser())
    audit.lanes(list(dict.fromkeys(p.expanduser().resolve() for p in args.lane_log)))
    report = audit.report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Role usage {report['date']} ({report['timezone']}): {report['status']}")
        print('Driver  Role                       New  Active  Activity')
        for r in report['summary']:
            print(f"{r['driver']:7} {r['role']:26} {r['agents_created']:4} {r['agents_active']:7}  {r['activity_count']} {r['activity_unit']}s")
            for model in r['models']:
                print(f"         {model['model'] or UNKNOWN} / {model['effort'] or UNKNOWN}: {model['observations']} observations")
        print(f"Separate companion launch attempts: {len(report['launch_attempts'])}")
        print(f"Coverage issues: {len(report['issues'])}. Use --json for identities, reasons and evidence.")
        print(report['scope'])
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
