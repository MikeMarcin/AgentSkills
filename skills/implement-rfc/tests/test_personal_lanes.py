"""Paired lanes use disposable repositories and separate local bare remotes."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_personal_binding as binding_tests
SCRIPT = binding_tests.SCRIPT
sys.path.insert(0, str(SCRIPT.parent))
import personal_lanes as lanes
import personal_state as state
from project_fixtures import git


class PersonalLaneTests(unittest.TestCase):
    source = binding_tests.PersonalBindingTests.source
    def setUp(self):
        binding_tests.PersonalBindingTests.setUp(self)
        self.enterContext(patch.dict(os.environ, self.env))
        self.source_root = self.source('product')
        self.binding = state.initialize(self.source_root)
        self.tracker = Path(self.binding['tracker_root'])
        lanes.bind_pair(self.source_root)
        self.context = SimpleNamespace(mode='personal', source_root=self.source_root,
                                       workflow_root=self.tracker)

    def test_concurrent_lane_and_reservation_authority(self):
        lane = self.base / 'feature'
        git(self.source_root, 'worktree', 'add', '-b', 'feature', str(lane))
        with self.assertRaisesRegex(state.PersonalStateError, 'already paired'):
            lanes.bind_pair(lane, tracker_root=self.tracker)
        pair = lanes.bind_pair(lane, tracker_branch='feature-records')
        context = SimpleNamespace(mode='personal', source_root=lane,
                                  workflow_root=Path(pair['local']['workflow_root']))
        self.assertEqual(lanes.validate_pair(context)['portable']['source']['branch'], 'feature')
        self.assertNotIn(str(self.base), json.dumps(pair['portable']))
        self.assertEqual(git(context.workflow_root, 'show', 'HEAD:docs/issues/NEXT_ID'), 'PRS-0001')
        lanes.assert_reservation_authority(self.context)
        with self.assertRaisesRegex(state.PersonalStateError, 'main'):
            lanes.assert_reservation_authority(context)
        git(lane, 'branch', '-m', 'renamed')
        with self.assertRaisesRegex(state.PersonalStateError, 'branch changed'):
            lanes.validate_pair(context)
        lanes.rebind_pair(context, 'renamed', 'feature-records',
                          git(lane, 'rev-parse', 'HEAD'),
                          git(context.workflow_root, 'rev-parse', 'HEAD'))
        self.assertEqual(lanes.validate_pair(context)['portable']['source']['branch'], 'renamed')
        git(self.source_root, 'worktree', 'remove', str(lane))
        with self.assertRaises(state.PersonalStateError):
            lanes.validate_pair(context)

    def test_rewritten_history_requires_exact_reconciliation(self):
        git(self.source_root, 'commit', '--allow-empty', '-m', 'progress')
        lanes.reconcile_pair(self.context, git(self.source_root, 'rev-parse', 'HEAD'),
                             git(self.tracker, 'rev-parse', 'HEAD'))
        git(self.source_root, 'commit', '--amend', '--allow-empty', '-m', 'revised progress')
        with self.assertRaisesRegex(state.PersonalStateError, 'history rewritten'):
            lanes.validate_pair(self.context)
        with self.assertRaisesRegex(state.PersonalStateError, 'revisions'):
            lanes.reconcile_pair(self.context, 'wrong', 'wrong')
        lanes.reconcile_pair(self.context, git(self.source_root, 'rev-parse', 'HEAD'),
                             git(self.tracker, 'rev-parse', 'HEAD'))
        git(self.source_root, 'checkout', '-b', 'different')
        with self.assertRaisesRegex(state.PersonalStateError, 'branch changed'):
            lanes.validate_pair(self.context)

    def test_authorized_separate_push_and_conflict_preservation(self):
        self.assertEqual(lanes.synchronize_pair(self.context)['status'], 'local-only')
        for name, root in [('source', self.source_root), ('tracker', self.tracker)]:
            remote = self.base / (name + '.git')
            remote.mkdir()
            git(remote, 'init', '--bare', '-b', 'main')
            git(root, 'remote', 'add', 'sync', str(remote))
        kwargs = dict(source_remote='sync', tracker_remote='sync', source_branch='main', tracker_branch='main')
        with self.assertRaisesRegex(state.PersonalStateError, 'authorization'):
            lanes.synchronize_pair(self.context, **kwargs)
        with self.assertRaisesRegex(state.PersonalStateError, 'branches'):
            lanes.synchronize_pair(self.context, **{**kwargs, 'source_branch': 'wrong'}, authorized=True)
        self.assertEqual(lanes.synchronize_pair(self.context, **kwargs, authorized=True)['completed'], ['source', 'tracker'])
        other = self.base / 'other'
        subprocess.run(['git', 'clone', '-q', str(self.base / 'tracker.git'), str(other)], check=True)
        git(other, 'config', 'user.name', 'fixture')
        git(other, 'config', 'user.email', 'fixture@example.invalid')
        git(other, 'commit', '--allow-empty', '-m', 'remote progress')
        git(other, 'push', 'origin', 'main')
        before = git(self.tracker, 'rev-parse', 'HEAD')
        with self.assertRaises(state.PersonalStateError):
            lanes.synchronize_pair(self.context, **kwargs, authorized=True)
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), before)
        receipt = json.loads(lanes._path(self.source_root).with_suffix('.sync.json').read_text())
        self.assertEqual(receipt['completed'], ['source'])
        self.assertEqual(receipt['status'], 'pending-reconciliation')

    def test_public_bind_and_separate_lane_integration(self):
        reservation = self.tracker / 'docs/issues/_reservations/receipt.json'
        reservation.parent.mkdir()
        reservation.write_text('{"reserved": ["PRS-0001"]}\n')
        git(self.tracker, 'add', 'docs/issues/_reservations/receipt.json')
        git(self.tracker, '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-m', 'Reserve work')
        lane = self.base / 'integration'
        git(self.source_root, 'worktree', 'add', '-b', 'improvement', str(lane))
        result = subprocess.run([sys.executable, str(SCRIPT.with_name('personal_lanes.py')),
            'bind', '--repo-root', str(lane), '--tracker-branch', 'improvement-records'],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        tracker_lane = Path(json.loads(result.stdout)['local']['workflow_root'])
        self.assertEqual((tracker_lane / reservation.relative_to(self.tracker)).read_text(), reservation.read_text())
        (lane / 'product.txt').write_text('improved\n')
        git(lane, 'add', 'product.txt')
        git(lane, 'commit', '-m', 'Improve product')
        revision = git(lane, 'rev-parse', 'HEAD')
        (tracker_lane / 'docs/issues/evidence.txt').write_text(revision + '\n')
        git(tracker_lane, 'add', 'docs/issues/evidence.txt')
        git(tracker_lane, '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-m', 'Record acceptance')
        git(self.source_root, 'merge', '--ff-only', 'improvement')
        git(self.tracker, 'merge', '--ff-only', 'improvement-records')
        self.assertEqual((self.tracker / 'docs/issues/evidence.txt').read_text().strip(),
                         git(self.source_root, 'rev-parse', 'HEAD'))
        lanes.validate_pair(self.context)

    def test_cross_clone_association_requires_separate_lane_and_malformed_records_refuse(self):
        clone = self.base / 'associated'
        subprocess.run(['git', 'clone', '-q', str(self.source_root), str(clone)], check=True)
        init = subprocess.run([sys.executable, str(SCRIPT), '--repo-root', str(clone),
            '--workflow-root', str(self.tracker), '--json', 'init'],
            capture_output=True, text=True, env=self.env)
        self.assertEqual(init.returncode, 0, init.stdout)
        observed = subprocess.run([sys.executable, str(SCRIPT), '--repo-root', str(clone),
            '--json', 'status'], capture_output=True, text=True, env=self.env)
        self.assertEqual(observed.returncode, 0, observed.stdout)
        context = SimpleNamespace(mode='personal', source_root=clone, workflow_root=self.tracker)
        with self.assertRaisesRegex(state.PersonalStateError, 'no tracker pair'):
            lanes.validate_pair(context)
        with self.assertRaises(lanes.PairOccupiedError):
            lanes.bind_pair(clone, tracker_root=self.tracker)
        original = lanes._path(self.source_root).read_text()
        for malformed in ('[]', '{"schema": "implement-rfc.pair.v1"}',
                          '{"schema": "implement-rfc.pair.v1", "local": null, "portable": {}}'):
            lanes._path(self.source_root).write_text(malformed)
            with self.assertRaisesRegex(state.PersonalStateError, 'invalid paired lane record'):
                lanes.bind_pair(clone, tracker_branch='associated-records')
            self.assertNotIn('associated-records', git(self.tracker, 'branch', '--list'))
        lanes._path(self.source_root).write_text(original)
        paired = lanes.bind_pair(clone, tracker_branch='associated-records')
        context.workflow_root = Path(paired['local']['workflow_root'])
        lanes.validate_pair(context)
        lanes.validate_pair(self.context)
        self.assertNotEqual(context.workflow_root, self.tracker)

    def test_public_lane_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPT.with_name('personal_lanes.py')),
                                 'status', '--repo-root', str(self.source_root)],
                                capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)['portable']['tracker']['branch'], 'main')


if __name__ == '__main__':
    unittest.main()
