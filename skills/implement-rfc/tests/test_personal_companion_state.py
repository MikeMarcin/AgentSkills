"""Disposable personal runtime roots and legacy adapter refusal."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_personal_binding as fixtures
sys.path.insert(0, str(fixtures.SCRIPT.parent))
import personal_state
import project_config
import run_slice
import station_lease
import progress_trail
import launch_remote_station
import codex_lane
import codex_station


class CompanionStateTests(unittest.TestCase):
    source = fixtures.PersonalBindingTests.source

    def setUp(self):
        fixtures.PersonalBindingTests.setUp(self)
        self.enterContext(patch.dict(os.environ, self.env))
        self.root = self.source('product')
        personal_state.initialize(self.root)
        self.context = project_config.resolve_context(repo_root=self.root)

    def test_runtime_and_observational_lease_leave_source_untouched(self):
        before = fixtures.snapshot(self.root)
        self.assertEqual(run_slice.runs_root(self.root), self.context.runtime_root / 'runs')
        lock = station_lease._lock_path('station-writer', self.root, self.context.config)
        self.assertTrue(lock.is_relative_to(self.context.runtime_root))
        result = subprocess.run([sys.executable, '-B', str(Path(station_lease.__file__)), 'status', '--repo', str(self.root), '--role', 'station-writer'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(lock.parent.exists())
        self.assertEqual(before, fixtures.snapshot(self.root))
        result = subprocess.run([sys.executable, '-B', str(Path(station_lease.__file__)), 'run', '--repo', str(self.root), '--', sys.executable, '-c', 'print("leased")'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(lock.exists())
        self.assertEqual(before, fixtures.snapshot(self.root))

    def test_redirected_lease_directory_refuses(self):
        self.context.runtime_root.mkdir(parents=True, exist_ok=True)
        (self.context.runtime_root / 'leases').symlink_to(self.root, target_is_directory=True)
        before = fixtures.snapshot(self.root)
        with self.assertRaises(ValueError):
            station_lease._lock_path('station-writer', self.root, self.context.config)
        self.assertEqual(before, fixtures.snapshot(self.root))

    def test_linked_run_cannot_write_cancellation_into_source(self):
        runs = run_slice.runs_root(self.root)
        runs.mkdir(parents=True)
        (runs / "linked-run").symlink_to(self.root, target_is_directory=True)
        before = fixtures.snapshot(self.root)
        command = [sys.executable, "-B", str(Path(run_slice.__file__)), "--repo-root", str(self.root),
                   "cancel", "--run", "linked-run", "--json"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Path escapes", result.stderr)
        self.assertEqual(before, fixtures.snapshot(self.root))

    def test_progress_uses_tracker_board_and_source_dirty_paths(self):
        (self.root / 'product.txt').write_text('changed')
        trail = progress_trail.Trail(str(self.root))
        self.assertEqual(trail.root, self.context.workflow_root)
        self.assertEqual(trail.working_set()[1], {'product.txt'})

    def test_incompatible_launchers_refuse_without_source_metadata(self):
        before = fixtures.snapshot(self.root)
        with self.assertRaisesRegex(launch_remote_station.LaunchRefusal, 'paired'):
            launch_remote_station.resolve_context(argparse.Namespace(repo_root=self.root))
        with self.assertRaisesRegex(codex_lane.LaunchError, 'paired'):
            codex_lane.cmd_launch(argparse.Namespace(context=self.context))
        for client in (codex_station.AppServerClient, codex_station.ProxyAppServerClient):
            with self.assertRaisesRegex(codex_station.CodexStationError, 'paired'):
                client(cwd=self.root, context=self.context)
        with self.assertRaisesRegex(codex_station.CodexStationError, 'paired'):
            codex_station.provision_named_thread(None, cwd=self.root, name='fixture', expected_thread_id=None, context=self.context)
        for script, extra in ((launch_remote_station.__file__, []), (codex_lane.__file__, ['launch', '--role', 'rfc-worker', '--task', 'fixture'])):
            result = subprocess.run([sys.executable, '-B', script, '--repo-root', str(self.root), *extra], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('paired source/tracker', result.stdout + result.stderr)
        self.assertEqual(before, fixtures.snapshot(self.root))
