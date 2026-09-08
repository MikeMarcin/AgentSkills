from datetime import date, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'role_usage.py'
spec = importlib.util.spec_from_file_location('role_usage', SCRIPT)
usage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage)
DAY = date(2026, 9, 5)
STAMP = '2026-09-05T12:00:00Z'


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
    return path


def codex(kind, payload, stamp=STAMP):
    return {'type': kind, 'timestamp': stamp, 'payload': payload}


def meta(identity='child', cwd='/project', created=STAMP, role='rfc-worker-routine'):
    return codex('session_meta', {'id': identity, 'cwd': cwd, 'timestamp': created,
        'source': {'subagent': {'thread_spawn': {'parent_thread_id': 'parent', 'agent_role': role}}}})


def context(turn='turn', model='gpt-5.6-sol', effort='high'):
    return codex('turn_context', {'turn_id': turn, 'model': model, 'effort': effort})


def owned(turn='turn', identity='child', stamp=STAMP, text=''):
    return codex('event_msg', {'type': 'item_completed', 'thread_id': identity, 'turn_id': turn,
        'item': {'type': 'AgentMessage', 'content': [{'type': 'Text', 'text': text}]}}, stamp)


def claude(response='message', stamp=STAMP, model='claude-opus-5', content='', **kwargs):
    return {'type': 'assistant', 'agentId': 'agent', 'sessionId': 'session', 'cwd': '/project',
        'timestamp': stamp, 'effort': 'high', 'message': {'id': response, 'model': model,
        'content': [{'type': 'text', 'text': content}]}, **kwargs}


class RoleUsageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.audit = usage.Audit(DAY, timezone.utc)

    def test_codex_inherited_history_followups_and_duplicate_contexts(self):
        path = write(self.root / 'rollout.jsonl', [meta(), context('parent-turn', 'gpt-6-astra'),
            owned('parent-turn', 'parent'), context(), context(), owned(), owned(),
            context('follow-up'), owned('follow-up'),
            context('tomorrow'), owned('tomorrow', stamp='2026-09-06T00:00:00Z')])
        self.audit.codex_file(path)
        report = self.audit.report()
        self.assertEqual(report['status'], 'ok')
        row = report['summary'][0]
        self.assertEqual((row['agents_created'], row['agents_active'], row['activity_count']), (1, 1, 2))
        self.assertEqual(row['models'], [{'model': 'gpt-5.6-sol', 'effort': 'high', 'observations': 2}])

    def test_old_child_active_today_not_counted_as_new(self):
        path = write(self.root / 'rollout.jsonl', [meta(created='2026-09-04T12:00:00Z'), context(), owned()])
        self.audit.codex_file(path)
        row = self.audit.report()['summary'][0]
        self.assertEqual((row['agents_created'], row['agents_active']), (0, 1))

    def test_missing_owned_activity_is_unknown_not_parent_execution(self):
        path = write(self.root / 'rollout.jsonl', [meta(), context('parent'), owned('parent', 'parent')])
        self.audit.codex_file(path)
        report = self.audit.report()
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['summary'][0]['activity_count'], 0)
        self.assertEqual(report['summary'][0]['agents_created'], 1)

    def test_codex_multiple_models_preserved_but_one_turn(self):
        path = write(self.root / 'rollout.jsonl', [meta(), context(), owned(), context(model='gpt-6-astra'), owned()])
        self.audit.codex_file(path)
        row = self.audit.report()['summary'][0]
        self.assertEqual(row['activity_count'], 1)
        self.assertEqual(len(row['models']), 2)

    def test_codex_primary_excluded_and_duplicate_child_flagged(self):
        primary = write(self.root / 'primary.jsonl', [codex('session_meta', {'id': 'parent', 'source': 'cli'})])
        self.audit.codex_file(primary)
        self.assertFalse(self.audit.records)
        for name in ('live', 'archive'):
            self.audit.codex_file(write(self.root / (name + '.jsonl'), [meta(), context(), owned()]))
        self.assertEqual(len(self.audit.records), 1)
        self.assertEqual(self.audit.report()['status'], 'partial')

    def test_claude_metadata_model_stream_dedup_and_missing_effort(self):
        path = write(self.root / 'agent-agent.jsonl', [claude(), claude(content='another chunk'),
            claude('second', effort=None)])
        write(path.with_suffix('.meta.json'), [{'agentType': 'rfc-worker-routine', 'model': 'configured-alias'}])
        self.audit.claude_file(path)
        row = self.audit.report()['summary'][0]
        self.assertEqual(row['activity_count'], 2)
        self.assertEqual(row['role'], 'rfc-worker-routine')
        self.assertEqual({r['model'] for r in row['models']}, {'claude-opus-5'})
        self.assertIn(None, [r['effort'] for r in row['models']])

    def test_claude_user_prompt_cannot_assign_role(self):
        banner = 'Role: rfc-worker | Model: fake | Effort: high'
        user = claude(content=banner)
        user['type'] = 'user'
        path = write(self.root / 'agent-agent.jsonl', [user, claude(content='No role banner')])
        self.audit.claude_file(path)
        self.assertEqual(self.audit.records[0]['role'], '<unknown>')

    def test_claude_banner_fallback_and_routing_reasons_are_self_reported(self):
        banner = 'Role: rfc-worker-routine | Model: wrong-banner | Effort: high'
        decision = 'Routing: routine | Reason: Follow existing benchmark registration'
        path = write(self.root / 'agent-agent.jsonl', [claude(content=banner+'\n'+decision),
            claude('second', content=decision)])
        self.audit.claude_file(path)
        record = self.audit.records[0]
        self.assertEqual(record['role_evidence'], 'assistant-banner (self-report)')
        self.assertEqual(len(record['routing_decisions']), 1)
        self.assertEqual(record['activity'][0]['observations'][0]['model'], 'claude-opus-5')
        self.assertEqual(self.audit.report()['summary'][0]['agents_without_routing_reason'], 0)

    def test_new_standard_deep_and_ambiguous_generic_history(self):
        for index, (role, choice) in enumerate((('rfc-worker', 'standard'),
                ('rfc-worker-deep', 'deep'), ('rfc-worker', None))):
            identity = f'worker-{index}'
            banner = '' if choice is None else f'Routing: {choice} | Reason: supplied problem'
            path = write(self.root / f'{identity}.jsonl', [meta(identity=identity, role=role),
                context(model='same-model', effort=None), owned(identity=identity, text=banner),
                owned(identity=identity, text=banner)])
            self.audit.codex_file(path)
        records = self.audit.records
        self.assertEqual([r['role'] for r in records], ['rfc-worker', 'rfc-worker-deep', 'rfc-worker'])
        self.assertEqual(records[0]['routing_decisions'][0]['choice'], 'standard')
        self.assertEqual(records[1]['routing_decisions'][0]['choice'], 'deep')
        self.assertEqual(len(records[0]['routing_decisions']), 1)
        self.assertEqual(records[2]['routing_decisions'], [])
        self.assertIsNone(records[2]['activity'][0]['observations'][0]['effort'])

    def test_codex_routing_from_owned_assistant_only_and_no_transcript_dump(self):
        secret = 'PRIVATE PROMPT MUST NOT APPEAR'
        path = write(self.root / 'rollout.jsonl', [meta(), context(),
            codex('response_item', {'role': 'user', 'content': [{'type': 'input_text', 'text': secret}]}),
            owned(identity='parent', text='Routing: deep | Reason: copied parent'),
            owned(text='Routing: routine | Reason: existing test pattern'),
            owned(text='Routing: routine | Reason: existing test pattern')])
        self.audit.codex_file(path)
        record = self.audit.records[0]
        self.assertEqual(len(record['routing_decisions']), 1)
        self.assertEqual(record['routing_decisions'][0]['choice'], 'routine')
        self.assertNotIn(secret, json.dumps(self.audit.report()))

    def test_unknown_response_id_and_damaged_tail_report_partial(self):
        path = write(self.root / 'agent-agent.jsonl', [claude(response=None)])
        with path.open('a') as f:
            f.write('{"unfinished":')
        self.audit.claude_file(path)
        report = self.audit.report()
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['summary'][0]['activity_count'], 0)
        self.assertEqual(len(report['issues']), 2)

    def test_claude_ids_scoped_to_parent_session(self):
        for session in ('one', 'two'):
            path = write(self.root / session / 'agent-agent.jsonl', [claude(sessionId=session)])
            self.audit.claude_file(path)
        self.assertEqual(len(self.audit.records), 2)
        self.assertFalse(self.audit.issues)

    def test_companion_attempts_separate_from_native_counts(self):
        path = write(self.root / 'lanes.jsonl', [{'timestamp': STAMP, 'role': 'rfc-worker',
            'cwd': '/project', 'runtime': 'codex', 'model': 'gpt-6-astra', 'effort': 'high'}])
        self.audit.lanes([path])
        report = self.audit.report()
        self.assertFalse(report['summary'])
        self.assertEqual(report['launch_attempts'][0]['driver'], 'claude')
        self.assertEqual(report['launch_attempts'][0]['executor'], 'codex')
        self.assertIn('not established', report['launch_attempts'][0]['evidence'])

    def test_project_filter_windows_and_posix(self):
        self.assertTrue(usage.same_project(r'C:\work\Repo', 'c:/work/repo'))
        self.assertFalse(usage.same_project('/work/repo', '/work/repo-worktree'))
        audit = usage.Audit(DAY, timezone.utc, '/different')
        audit.codex_file(write(self.root / 'rollout.jsonl', [meta(), context(), owned()]))
        self.assertFalse(audit.records)

    def test_timezone_boundary(self):
        from datetime import timedelta
        audit = usage.Audit(DAY, timezone(timedelta(hours=-7)))
        self.assertTrue(audit.on_day('2026-09-06T06:59:59Z'))
        self.assertFalse(audit.on_day('2026-09-06T07:00:00Z'))
        self.assertFalse(audit.on_day('2026-09-05T00:00:00'))

    def test_public_cli_both_drivers_through_two_consumer_links_read_only(self):
        codex_home, claude_home = self.root / 'codex', self.root / 'claude'
        write(codex_home / 'sessions/2026/09/05/rollout.jsonl', [meta(cwd='/one'), context(), owned()])
        child = write(claude_home / 'projects/project/session/subagents/agent-agent.jsonl', [claude(cwd='/two')])
        write(child.with_suffix('.meta.json'), [{'agentType': 'rfc-scout'}])
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for project in ('one', 'two'):
            consumer = self.root / project
            consumer.mkdir()
            link = consumer / 'shared'
            try:
                link.symlink_to(SCRIPT.parents[1], target_is_directory=True)
            except OSError as exc:
                self.skipTest(f'Native symlinks unavailable: {exc}')
            proc = subprocess.run([sys.executable, '-B', str(link / 'scripts/role_usage.py'),
                '--codex-home', str(codex_home), '--claude-home', str(claude_home),
                '--date', str(DAY), '--repo-root', '/' + project,
                '--role', 'rfc-worker-routine' if project == 'one' else 'rfc-scout', '--json'],
                cwd=consumer, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            result = json.loads(proc.stdout)
            self.assertEqual(len(result['agents']), 1)
            self.assertEqual(result['agents'][0]['project'], '/' + project)
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_pretty_printed_claude_metadata(self):
        path = write(self.root / 'agent-agent.jsonl', [claude()])
        path.with_suffix('.meta.json').write_text(json.dumps({'agentType': 'rfc-scout'}, indent=2))
        self.audit.claude_file(path)
        self.assertEqual(self.audit.records[0]['role'], 'rfc-scout')
        self.assertFalse(self.audit.issues)

    def test_banner_example_is_not_role_identity(self):
        example = 'Example output:\n```text\nRole: rfc-worker | Model: example | Effort: high\n```'
        path = write(self.root / 'agent-agent.jsonl', [claude(content=example)])
        self.audit.claude_file(path)
        self.assertEqual(self.audit.records[0]['role'], '<unknown>')

    def test_empty_and_invalid_timestamp_histories_are_partial(self):
        self.audit.claude_file(write(self.root / 'empty.jsonl', []))
        self.audit.claude_file(write(self.root / 'agent-agent.jsonl', [claude(stamp='invalid')]))
        path = write(self.root / 'rollout.jsonl', [meta(created='2026-09-04T00:00:00Z'),
            context(), owned(stamp='invalid')])
        self.audit.codex_file(path)
        self.assertEqual(self.audit.report()['status'], 'partial')
        self.assertEqual(len(self.audit.issues), 3)
        self.assertFalse(self.audit.records)

    def test_routing_quote_cannot_become_a_decision(self):
        path = write(self.root / 'rollout.jsonl', [meta(), context(),
            owned(text='Example:\n```text\nRouting: routine | Reason: example\n```')])
        self.audit.codex_file(path)
        self.assertFalse(self.audit.records[0]['routing_decisions'])

    def test_unsupported_field_shapes_keep_scan_partial(self):
        path = write(self.root / 'codex/sessions/rollout.jsonl', [meta(),
            codex('turn_context', {'turn_id': [], 'model': 'model'}),
            codex('event_msg', {'thread_id': 'child', 'turn_id': ['bad']})])
        self.audit.codex(self.root / 'codex')
        self.assertEqual(self.audit.report()['status'], 'partial')
        self.assertTrue(any('Unsupported history field shape' in i['detail'] for i in self.audit.issues))

    def test_public_cli_missing_source_is_partial_json(self):
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), '--driver', 'claude',
            '--claude-home', str(self.root / 'absent'), '--json'], text=True, capture_output=True)
        self.assertEqual(proc.returncode, 1)
        report = json.loads(proc.stdout)
        self.assertEqual(report['status'], 'partial')
        self.assertFalse(report['sources'][0]['available'])
        self.assertFalse((self.root / 'absent').exists())


if __name__ == '__main__':
    unittest.main()
