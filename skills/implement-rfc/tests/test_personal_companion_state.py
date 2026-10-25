"""Disposable personal runtime roots and companion lane refusal."""
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
import progress_trail
import codex_lane


class CompanionStateTests(unittest.TestCase):
    source = fixtures.PersonalBindingTests.source

    def setUp(self):
        fixtures.PersonalBindingTests.setUp(self)
        self.enterContext(patch.dict(os.environ, self.env))
        self.root = self.source('product')
        personal_state.initialize(self.root)
        self.context = project_config.resolve_context(repo_root=self.root)

    def test_runs_root_is_in_the_personal_runtime(self):
        self.assertEqual(run_slice.runs_root(self.root), self.context.runtime_root / 'runs')

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

    def test_incompatible_lane_launcher_refuses_without_source_metadata(self):
        before = fixtures.snapshot(self.root)
        with self.assertRaisesRegex(codex_lane.LaunchError, 'paired'):
            codex_lane.cmd_launch(argparse.Namespace(context=self.context))
        for script, extra in ((codex_lane.__file__, ['launch', '--role', 'rfc-worker', '--task', 'fixture']),):
            result = subprocess.run([sys.executable, '-B', script, '--repo-root', str(self.root), *extra], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('paired source/tracker', result.stdout + result.stderr)
        self.assertEqual(before, fixtures.snapshot(self.root))
