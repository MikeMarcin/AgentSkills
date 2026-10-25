from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_remote_station_guard as fixtures

PACK = fixtures.PACK
sys.path.insert(0, str(PACK / 'scripts'))
import station_control as control
import station_lifecycle as lifecycle
import station_lease
import project_config


class StationControlTests(fixtures.RemoteStationGuardTests):
    def setUp(self):
        super().setUp()
        # Exercise a consumer link, rather than a per-consumer copied script bundle.
        import shutil
        target = self.repo / '.agents/skills/implement-rfc'
        shutil.rmtree(target)
        target.symlink_to(PACK, target_is_directory=True)

    def proof(self, station):
        return dict(endpoints=lifecycle.endpoints(station), writer_stopped=True, commands_stopped=True,
                    kind='fixture-owner-runtime')

    def release(self):
        self.holder.kill()
        self.holder.wait()
        self.holder.stdout.close()
        self.holder.stderr.close()

    def run_control(self, operation, *args):
        return subprocess.run([sys.executable, str(self.repo / '.agents/skills/implement-rfc/scripts/station_control.py'),
                               operation, '--repo-root', str(self.repo), '--json', *args],
                              capture_output=True, text=True)

    def test_status_reports_held_and_stale_lease_without_inactivity_guess(self):
        first = json.loads(self.run_control('status').stdout)
        self.assertTrue(first['supervisor_lease']['held'])
        self.assertEqual(first['activity']['state'], 'unknown')
        self.release()
        self.station['environment'] = 'fixture'
        self._write_station()
        second = json.loads(self.run_control('status').stdout)
        self.assertFalse(second['supervisor_lease']['held'])
        self.assertTrue(second['supervisor_lease']['stale_holder'])
        refused = self.run_control('takeover', '--mode', 'local', '--stop-previous')
        self.assertEqual(refused.returncode, 75)
        self.assertIn('owning host', refused.stdout)
        self.assertEqual(lifecycle.load(self.repo)['mode'], 'transferring')

    def test_public_launcher_inspects_without_hidden_root_flags_and_preserves_binding(self):
        launcher = self.repo / '.agents/skills/implement-rfc/scripts/launch_remote_station.py'
        before = (self.repo / '.remote-station.json').read_bytes()
        result = subprocess.run([sys.executable, '-B', str(launcher), 'status', '--json'],
                                cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(observed['mode'], 'managed')
        self.assertTrue(observed['supervisor_lease']['held'])
        self.assertEqual((self.repo / '.remote-station.json').read_bytes(), before)
        self.assertIsNone(lifecycle.load(self.repo))

    def test_public_launcher_takeover_keeps_stop_observation_required(self):
        self.release()
        self.station['environment'] = 'fixture'
        self._write_station()
        launcher = self.repo / '.agents/skills/implement-rfc/scripts/launch_remote_station.py'
        refused = subprocess.run([sys.executable, '-B', str(launcher), 'takeover', '--json'],
                                cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(refused.returncode, 75, refused.stdout)
        self.assertEqual(lifecycle.load(self.repo)['mode'], 'transferring')
        done = subprocess.run([sys.executable, '-B', str(launcher), 'takeover',
                               '--confirm-runtime-stopped', '--json'], cwd=self.repo,
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(json.loads(done.stdout)['mode'], 'local')

    def test_project_prefixed_registry_preserves_existing_lifecycle_identity(self):
        state = lifecycle.initial(self.repo, self.station)
        lifecycle.save(self.repo, state)
        self.station['schema'] = 'aito.implement-rfc.remote-station.v2'
        self._write_station()
        registry = (self.repo / '.remote-station.json').read_bytes()
        state_bytes = lifecycle.paths(self.repo)[0].read_bytes()
        result = self.run_control('status')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(observed['mode'], 'managed')
        self.assertEqual(observed['generation'], state['generation'])
        self.assertEqual(observed['endpoint'], state['endpoints'])
        self.assertTrue(observed['supervisor_lease']['held'])
        accepted = self._run_guard(self._event('UserPromptSubmit', prompt=self._envelope()))
        self.assertIn('accepted', accepted.stdout, accepted.stderr)
        self.assertEqual((self.repo / '.remote-station.json').read_bytes(), registry)
        self.assertEqual(lifecycle.paths(self.repo)[0].read_bytes(), state_bytes)

    def test_paused_or_crashed_takeover_preserves_dirty_work_and_fences_retired_endpoint(self):
        self.release()
        dirty = self.repo / 'seed.txt'
        dirty.write_text('owner dirty edit\n')
        checkpoint = self.repo / 'checkpoint.json'
        checkpoint.write_text('{"pending":["acceptance"],"strategy":"coordinator-implementer"}')
        registry = (self.repo / '.remote-station.json').read_bytes()
        result = control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        self.assertEqual(result['mode'], 'local')
        self.assertEqual(dirty.read_text(), 'owner dirty edit\n')
        self.assertIn('acceptance', checkpoint.read_text())
        self.assertEqual((self.repo / '.remote-station.json').read_bytes(), registry)
        allowed = self._run_guard(self._event('PreToolUse', session_id='replacement', tool_name='apply_patch'))
        self.assertEqual(allowed.stdout, '')
        denied = self._run_guard(self._event('PreToolUse', tool_name='apply_patch'))
        self.assertIn('retired', denied.stdout)
        (self.repo / '.remote-station.json').unlink()
        self.assertIn('retired', self._run_guard(self._event('PreToolUse', tool_name='Write')).stdout)

    def test_repeated_takeover_is_idempotent_and_requires_no_second_stop(self):
        self.release()
        control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        before = lifecycle.paths(self.repo)[0].read_bytes()
        result = control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=lambda unused: self.fail('second stop'))
        self.assertEqual(result['mode'], 'local')
        self.assertEqual(lifecycle.paths(self.repo)[0].read_bytes(), before)

    def test_interrupted_transfer_recovers_original_proof_and_generation(self):
        self.release()
        original = lifecycle.save
        def interrupted(root, state):
            if state['mode'] == 'local':
                raise OSError('fixture publication interruption')
            original(root, state)
        with patch.object(lifecycle, 'save', side_effect=interrupted), self.assertRaises(OSError):
            control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        pending = lifecycle.load(self.repo)
        self.assertEqual(pending['mode'], 'transferring')
        result = control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=lambda unused: self.fail('proof was durable'))
        self.assertEqual(result['generation'], 2)
        self.assertEqual(len(result['retired']), 1)

    def test_competing_takeover_is_serialized_by_kernel_lock(self):
        self.release()
        with lifecycle.locked(self.repo):
            refused = self.run_control('takeover', '--mode', 'local', '--stop-previous', '--confirm-runtime-stopped')
        self.assertEqual(refused.returncode, 75)
        self.assertIn('transfer lock', refused.stdout)
        self.assertIsNone(lifecycle.load(self.repo))
        self.assertEqual(self.run_control('takeover', '--mode', 'local', '--stop-previous', '--confirm-runtime-stopped').returncode, 0)

    def test_sidecar_null_and_identity_changes_cannot_bypass_durable_binding(self):
        lifecycle.save(self.repo, lifecycle.initial(self.repo, self.station))
        self.station['codex'] = None
        self._write_station()
        result = self._run_guard(self._event('PreToolUse', tool_name='Write', session_id='replacement'))
        self.assertIn('deny', result.stdout)
        self.assertIn('lifecycle identity', result.stdout)
        self.assertEqual(self.run_control('takeover', '--mode', 'local', '--stop-previous').returncode, 75)

    def test_replacement_prompt_and_exact_recovery_argv(self):
        event = self._event('UserPromptSubmit', session_id='replacement', prompt='resume this work here')
        self.assertNotIn('"decision": "block"', self._run_guard(event).stdout)
        script = self.repo / '.agents/skills/implement-rfc/scripts/station_control.py'
        command = shlex.join([sys.executable, str(script), 'status', '--repo-root', str(self.repo), '--json'])
        def tool(command):
            return self._run_guard(self._event('PreToolUse', session_id='replacement', tool_name='Bash', tool_input={'command': command}))
        self.assertEqual(tool(command).stdout, '')
        for suffix in ('; touch stolen', ' && git commit -am stolen', ' | sh', ' $(touch stolen)'):
            self.assertIn('deny', tool(command + suffix).stdout)
        self.assertIn('deny', tool('python3 -c "open(\'stolen\',\'w\')"').stdout)
        self.assertEqual(tool(shlex.join(['git', '-C', str(self.repo), 'status', '--short'])).stdout, '')

    def test_wrong_runtime_receipt_cannot_release_writes(self):
        self.release()
        with self.assertRaises(lifecycle.LifecycleError):
            control.takeover(self.repo, stop_previous=True,
                             runtime_stop_adapter=lambda unused: dict(endpoints={'codex': 'another'}, writer_stopped=True, commands_stopped=True))
        self.assertEqual(lifecycle.load(self.repo)['mode'], 'transferring')

    @unittest.skipUnless(os.name == 'posix', 'controlled process group adapter is POSIX only')
    def test_active_controlled_supervisor_stops_only_owned_fixture_group(self):
        self.release()
        self.holder = subprocess.Popen([sys.executable, str(PACK / 'scripts/station_lease.py'), 'run',
            '--repo-root', str(self.repo), '--role', 'project-integrator', '--station', self.station['station'],
            '--controlled', '--', sys.executable, '-c', "import time; print('held', flush=True); time.sleep(60)"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(self.holder.stdout.readline().strip(), 'held')
        result = control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        self.assertEqual(result['mode'], 'local')
        self.holder.wait(timeout=10)
        self.assertFalse(station_lease.snapshot(self.repo, 'project-integrator', project_config.resolve_context(repo_root=self.repo))['held'])
        self.assertIn('[redacted]', json.dumps(result['supervisor_lease']))

    def test_fresh_generation_keeps_retired_endpoint_fence(self):
        self.release()
        control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        with lifecycle.locked(self.repo):
            with self.assertRaises(lifecycle.LifecycleError): lifecycle.activate(self.repo, self.station)
            self.station['codex']['thread_id'] = 'fresh-runtime'
            lifecycle.activate(self.repo, self.station)
            self._write_station()
        self.assertIn('retired', self._run_guard(self._event('PreToolUse', tool_name='apply_patch')).stdout)

    def test_unmanaged_second_linked_consumer_is_unrestricted_and_isolated(self):
        second = self.repo.parent / 'other-consumer'
        second.mkdir()
        fixtures._git(second, 'init', '-b', 'main')
        from project_fixtures import write_context
        write_context(second, token='other')
        link = second / '.agents/skills/implement-rfc'
        link.parent.mkdir(parents=True)
        link.symlink_to(PACK, target_is_directory=True)
        result = subprocess.run([sys.executable, str(link / 'scripts/station_control.py'), 'status', '--repo-root', str(second), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['mode'], 'unmanaged')
        event = self._event('PreToolUse', cwd=str(second), session_id='ordinary-local', tool_name='Write')
        self.assertEqual(self._run_guard(event).stdout, '')
        self.assertIsNone(lifecycle.load(second))

    def test_stop_receipt_survives_runtime_failure_and_default_cli_recovery(self):
        import io
        from contextlib import redirect_stdout
        self.release()
        calls = []
        def stopped(*unused):
            calls.append('stop')
            return {'controlled_stop': True}
        def unavailable(*unused):
            raise lifecycle.LifecycleError('fixture runtime temporarily unavailable')
        with patch.object(station_lease, 'stop_supervisor', side_effect=stopped), \
                patch.object(control, 'runtime_stop', side_effect=unavailable), self.assertRaises(lifecycle.LifecycleError):
            control.takeover(self.repo, stop_previous=True)
        self.assertTrue(lifecycle.load(self.repo)['transfer']['supervisor_proof']['controlled_stop'])
        def recovered(root, station, supervisor):
            self.assertTrue(supervisor['controlled_stop'])
            return self.proof(station)
        output = io.StringIO()
        with patch.object(control, 'runtime_stop', side_effect=recovered), \
                patch.object(station_lease, 'stop_supervisor', return_value={'held':False}), redirect_stdout(output):
            result = control.main(['takeover','--repo-root',str(self.repo),'--json','--mode','local','--stop-previous'])
        self.assertEqual(result, 0, output.getvalue())
        self.assertEqual(calls, ['stop'])

    def test_control_tokens_are_redacted_in_status_and_competing_writer_diagnostics(self):
        holder_path = station_lease._holder_path(station_lease._lock_path('project-integrator', self.repo,
                                                    project_config.resolve_context(repo_root=self.repo).config))
        holder = json.loads(holder_path.read_text())
        secret = 'a' * 64
        holder['control'] = {'port':1234,'protocol':'implement-rfc.supervisor-stop.v1','token':secret}
        holder_path.write_text(json.dumps(holder))
        status = self.run_control('status')
        self.assertNotIn(secret, status.stdout)
        conflict = subprocess.run([sys.executable, str(PACK / 'scripts/station_lease.py'), 'run',
            '--repo-root', str(self.repo), '--role','project-integrator','--',sys.executable,'-c','pass'],
            capture_output=True,text=True)
        self.assertEqual(conflict.returncode,75)
        self.assertNotIn(secret,conflict.stderr)
        self.assertIn('[redacted]',conflict.stderr)
        script = self.repo / '.agents/skills/implement-rfc/scripts/station_control.py'
        self.assertTrue(fixtures.GUARD.exists())
        import remote_station_guard as guard
        command=shlex.join(['py','-3',str(script),'status','--repo-root',str(self.repo),'--json'])
        self.assertTrue(guard._bounded_recovery_command(self.repo.resolve(),command))

    def test_launcher_composition_after_takeover_provisions_fresh_generation(self):
        import contextlib
        import launch_remote_station as launcher
        from test_launch_remote_station import arguments
        self.release()
        control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        context = launcher.StationContext(root=self.repo.resolve(), workstream='main', branch='main',
            name=self.station['station'], environment='macos', authority='lane-commit',
            lease_role='project-integrator', station_file=self.repo / '.remote-station.json',
            project_context=project_config.resolve_context(repo_root=self.repo))
        with patch.object(launcher, 'provision_codex', return_value=contextlib.nullcontext({
            'thread_id':'fresh-thread', 'thread_name':self.station['station'], 'cli_version':'0.151.0'})), \
                patch.object(launcher, 'run_claude', return_value=0):
            self.assertEqual(launcher.supervise(arguments(new_codex_session=True), context), 0)
        self.assertEqual(lifecycle.load(self.repo)['mode'], 'managed')
        self.assertIn('retired', self._run_guard(self._event('PreToolUse', tool_name='Write')).stdout)

    def test_fresh_outer_launcher_recovers_interrupted_takeover_before_publication(self):
        import contextlib
        import launch_remote_station as launcher
        from test_launch_remote_station import arguments
        self.release()
        original = lifecycle.save
        def interrupted(root, state):
            if state['mode'] == 'local':
                raise OSError('interrupted local publication')
            original(root, state)
        with patch.object(lifecycle, 'save', side_effect=interrupted), self.assertRaises(OSError):
            control.takeover(self.repo, stop_previous=True, runtime_stop_adapter=self.proof)
        pending = lifecycle.load(self.repo)
        registry = (self.repo / '.remote-station.json').read_bytes()
        context = launcher.StationContext(root=self.repo.resolve(), workstream='main', branch='main',
            name=self.station['station'], environment='macos', authority='lane-commit',
            lease_role='project-integrator', station_file=self.repo / '.remote-station.json',
            project_context=project_config.resolve_context(repo_root=self.repo))
        options = arguments(new_codex_session=True, new_claude_session=True)
        original_run = subprocess.run
        def start_new_supervisor(command, **kwargs):
            if len(command) < 2 or not str(command[1]).endswith('station_lease.py'):
                return original_run(command, **kwargs)
            self.assertEqual(lifecycle.load(self.repo)['mode'], 'local')
            self.assertEqual((self.repo / '.remote-station.json').read_bytes(), registry)
            with patch.object(launcher, 'provision_codex', return_value=contextlib.nullcontext({
                'thread_id':'fresh-thread', 'thread_name':self.station['station'], 'cli_version':'0.151.0'})), \
                    patch.object(launcher, 'run_claude', return_value=0):
                result = launcher.supervise(options, context)
            return subprocess.CompletedProcess([], result)
        with patch.object(launcher.subprocess, 'run', side_effect=start_new_supervisor):
            self.assertEqual(launcher.run_under_lease(options, context), 0)
        current = lifecycle.load(self.repo)
        self.assertEqual(current['mode'], 'managed')
        self.assertEqual(current['generation'], pending['generation'] + 2)
        self.assertEqual(current['history'][-1]['transfer']['id'], pending['transfer']['id'])
        self.assertTrue(lifecycle.retired(current, self.station['codex']['thread_id']))

    def test_takeover_retry_refreshes_negative_supervisor_proof(self):
        self.release()
        with patch.object(station_lease, 'stop_supervisor', return_value={'controlled_stop': False}), \
                patch.object(control, 'runtime_stop', side_effect=lifecycle.LifecycleError('not stopped')), \
                self.assertRaises(lifecycle.LifecycleError):
            control.takeover(self.repo, stop_previous=True)
        pending = lifecycle.load(self.repo)
        self.assertFalse(pending['transfer']['supervisor_proof']['controlled_stop'])
        def stop_runtime(root, station, supervisor):
            self.assertTrue(supervisor['controlled_stop'])
            return self.proof(station)
        with patch.object(station_lease, 'stop_supervisor', return_value={'controlled_stop': True}), \
                patch.object(control, 'runtime_stop', side_effect=stop_runtime):
            result = control.takeover(self.repo, stop_previous=True)
        self.assertEqual(result['mode'], 'local')
        self.assertEqual(lifecycle.load(self.repo)['history'][-1]['transfer']['id'], pending['transfer']['id'])

    def test_negative_retry_with_only_a_free_lease_keeps_stop_unproven(self):
        self.release()
        for unused in range(2):
            with patch.object(control, 'runtime_stop', side_effect=lifecycle.LifecycleError('runtime unproven')), \
                    self.assertRaises(lifecycle.LifecycleError):
                control.takeover(self.repo, stop_previous=True)
        pending = lifecycle.load(self.repo)
        self.assertFalse(pending['transfer']['supervisor_proof']['controlled_stop'])
        self.assertIsNone(pending['transfer']['runtime_proof'])


class OwnerRuntimeAdapterTests(unittest.TestCase):
    class Client:
        def __init__(self, root, *, state='active', terminals=True, descendants=False):
            import types
            self.context = types.SimpleNamespace(source_root=root)
            self.state, self.active, self.terminals, self.descendants = state, state == 'active', terminals, descendants
            self.calls = []
        def __enter__(self): return self
        def __exit__(self, *unused): pass
        def request(self, method, params, *, timeout=None):
            self.calls.append((method, params))
            if method == 'thread/read':
                items = ([{'type':'collabAgentToolCall','receiverThreadIds':['child']}] if self.descendants else [])
                return {'thread':{'id':'recorded-thread', 'cwd':str(self.context.source_root), 'name':'fixture-station',
                        'status':{'type':self.state}, 'turns':[{'id':'recorded-turn', 'status':'inProgress' if self.active else 'interrupted', 'items':items}]}}
            if method == 'turn/interrupt': self.active=False; self.state='idle'; return {}
            if method == 'thread/backgroundTerminals/list':
                return {'data':[{'processId':'recorded-process'}] if self.terminals else [], 'nextCursor':None}
            if method == 'thread/backgroundTerminals/terminate': self.terminals=False; return {'terminated':True}
            raise AssertionError(method)

    def setUp(self):
        self.root = Path('/fixture').resolve()
        self.station = {'environment':'macos','codex':{'thread_id':'recorded-thread', 'thread_name':'fixture-station'}}

    def test_real_adapter_uses_exact_recorded_rpc_identities_and_command_inventory(self):
        client = self.Client(self.root)
        with patch.object(control, '_owner_client', return_value=client):
            result = control.runtime_stop(self.root, self.station, {})
        self.assertTrue(result['writer_stopped'])
        self.assertTrue(result['commands_stopped'])
        self.assertIn(('turn/interrupt', {'threadId':'recorded-thread','turnId':'recorded-turn'}), client.calls)
        self.assertIn(('thread/backgroundTerminals/terminate', {'threadId':'recorded-thread','processId':'recorded-process'}), client.calls)
        self.assertFalse(any(method in ('thread/archive','thread/unsubscribe') for method, unused in client.calls))

    def test_terminal_status_without_loaded_idle_or_descendant_reconciliation_refuses(self):
        import codex_station
        for state, descendants in (('notLoaded',False),('systemError',False),('idle',True)):
            client = self.Client(self.root, state=state, terminals=False, descendants=descendants)
            with self.subTest(state=state), self.assertRaises(codex_station.CodexStationError):
                codex_station.stop_station_turns(client, self.station, timeout=0)

    def test_status_observation_never_interrupts_or_terminates(self):
        client = self.Client(self.root)
        with patch.object(control, '_owner_client', return_value=client):
            observed = control.runtime_activity(self.root, self.station)
        self.assertEqual(observed['state'], 'observed')
        self.assertEqual(observed['codex']['active_turns'], ['recorded-turn'])
        self.assertEqual([method for method, unused in client.calls], ['thread/read','thread/backgroundTerminals/list'])

    def test_incomplete_terminals_and_wrong_checkout_never_supply_proof(self):
        import codex_station
        client = self.Client(Path('/different-root'))
        client.context.source_root = self.root
        original = client.request
        def request(method, params, *, timeout=None):
            result = original(method, params)
            if method == 'thread/read': result['thread']['cwd'] = '/different-root'
            return result
        client.request = request
        with self.assertRaises(codex_station.CodexStationError): codex_station.station_activity(client, self.station)
        client = self.Client(self.root)
        original = client.request
        def partial(method, params, *, timeout=None):
            result = original(method, params)
            if method.endswith('/list'): result['nextCursor'] = 'more'
            return result
        client.request = partial
        with self.assertRaises(codex_station.CodexStationError): codex_station.station_activity(client, self.station)


if __name__ == '__main__': unittest.main()
