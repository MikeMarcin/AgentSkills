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

    def test_rewritten_references_require_committed_replacement(self):
        git(self.source_root, 'commit', '--allow-empty', '-m', 'original work')
        old = git(self.source_root, 'rev-parse', 'HEAD')
        evidence = self.tracker / 'docs/issues/evidence.txt'
        evidence.write_text(old + '\n')
        def commit_evidence():
            git(self.tracker, 'add', 'docs/issues/evidence.txt')
            git(self.tracker, '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
                'commit', '-m', 'Record revision')
        commit_evidence()
        lanes.reconcile_pair(self.context, old, git(self.tracker, 'rev-parse', 'HEAD'))
        # Rebase/cherry-pick shape: retain base, replay the work as a new commit.
        git(self.source_root, 'checkout', '-b', 'replayed', 'HEAD^')
        git(self.source_root, 'commit', '--allow-empty', '-m', 'new base')
        git(self.source_root, 'cherry-pick', '--allow-empty', old)
        new = git(self.source_root, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(state.PersonalStateError, 'stale source revision'):
            lanes.rebind_pair(self.context, 'replayed', 'main', new, git(self.tracker, 'rev-parse', 'HEAD'))
        evidence.write_text(new + '\n')
        with self.assertRaisesRegex(state.PersonalStateError, 'commit reconciled'):
            lanes.rebind_pair(self.context, 'replayed', 'main', new, git(self.tracker, 'rev-parse', 'HEAD'))
        commit_evidence()
        lanes.rebind_pair(self.context, 'replayed', 'main', new, git(self.tracker, 'rev-parse', 'HEAD'))
        git(self.source_root, 'commit', '--amend', '--allow-empty', '-m', 'rewritten again')
        newest = git(self.source_root, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(state.PersonalStateError, 'stale source revision'):
            lanes.reconcile_pair(self.context, newest, git(self.tracker, 'rev-parse', 'HEAD'))
        evidence.write_text(newest + '\n')
        commit_evidence()
        lanes.reconcile_pair(self.context, newest, git(self.tracker, 'rev-parse', 'HEAD'))

    def test_consumed_release_reuse_dirty_pending_and_removed_worktrees(self):
        source_lane = self.base / 'release-source'
        git(self.source_root, 'worktree', 'add', '-b', 'consumed', str(source_lane))
        pair = lanes.bind_pair(source_lane, tracker_branch='consumed-records')
        tracker_lane = Path(pair['local']['workflow_root'])
        record = lanes._path(source_lane)
        expected = pair['portable']
        from personal_commit import operation_lock
        lock_context = SimpleNamespace(source_root=self.source_root, runtime_root=record.parent.parent)
        with operation_lock(lock_context):
            with self.assertRaisesRegex(state.PersonalStateError, 'operation is active'):
                lanes.release_pair(self.source_root, record, expected)
        (source_lane / 'untracked').write_text('preserve')
        with self.assertRaisesRegex(state.PersonalStateError, 'clean'):
            lanes.release_pair(self.source_root, record, expected)
        (source_lane / 'untracked').unlink()
        receipts = record.parent.parent / 'product-commits'
        receipts.mkdir(exist_ok=True)
        pending = receipts / 'pending.json'
        pending.write_text(json.dumps({'schema': 'implement-rfc.personal-commit.v1', 'status': 'editing', 'pair': pair}))
        with self.assertRaisesRegex(state.PersonalStateError, 'receipt'):
            lanes.release_pair(self.source_root, record, expected)
        pending.write_text(json.dumps({'schema': 'implement-rfc.personal-commit.v1', 'status': 'complete', 'pair': pair}))
        with self.assertRaisesRegex(state.PersonalStateError, 'task-owned'):
            lanes.release_pair(self.source_root, record, expected, remove_tracker=True)
        sync = record.with_suffix('.sync.json')
        sync.write_text('[]')
        with self.assertRaisesRegex(state.PersonalStateError, 'synchronization'):
            lanes.release_pair(self.source_root, record, expected)
        sync.unlink()
        expected_file = self.base / 'expected-pair.json'
        expected_file.write_text(json.dumps(expected))
        released = subprocess.run([sys.executable, str(SCRIPT.with_name('personal_lanes.py')),
            'release', '--repo-root', str(self.source_root), '--pair-record', str(record),
            '--expected-pair', str(expected_file)], capture_output=True, text=True, env=self.env)
        self.assertEqual(released.returncode, 0, released.stdout)
        self.assertEqual(json.loads(released.stdout)['status'], 'released')
        self.assertTrue(source_lane.exists())
        self.assertTrue(tracker_lane.exists())
        lanes.bind_pair(source_lane, tracker_root=tracker_lane)
        lanes.release_pair(self.source_root, record, expected, remove_source=True, remove_tracker=True,
                           task_owned_source=True, task_owned_tracker=True)
        self.assertFalse(source_lane.exists())
        self.assertFalse(tracker_lane.exists())
        self.assertEqual(git(self.tracker, 'rev-parse', 'consumed-records'), expected['tracker']['revision'])
        replacement = self.base / 'removed-source'
        git(self.source_root, 'worktree', 'add', '-b', 'already-removed', str(replacement))
        removed_pair = lanes.bind_pair(replacement, tracker_branch='removed-records')
        removed_record = lanes._path(replacement)
        git(self.source_root, 'worktree', 'remove', str(replacement))
        with self.assertRaisesRegex(state.PersonalStateError, 'already removed'):
            lanes.release_pair(self.source_root, removed_record, removed_pair['portable'],
                               remove_source=True, task_owned_source=True)
        lanes.release_pair(self.source_root, removed_record, removed_pair['portable'])
        self.assertFalse(removed_record.exists())

    def test_release_rejects_primary_removal_and_unintegrated_revision(self):
        record = lanes._path(self.source_root)
        expected = lanes.validate_pair(self.context)['recorded']
        with patch.dict(os.environ, {'IMPLEMENT_RFC_HOME': str(self.source_root)}):
            with self.assertRaisesRegex(state.PersonalStateError, 'overlaps'):
                lanes.release_pair(self.source_root, record, expected)
        self.assertFalse((self.source_root / 'runtime').exists())
        with self.assertRaisesRegex(state.PersonalStateError, 'task-owned'):
            lanes.release_pair(self.source_root, record, expected, remove_source=True,
                               task_owned_source=True)
        with self.assertRaisesRegex(state.PersonalStateError, 'exact recorded'):
            lanes.release_pair(self.source_root, record, {})
        source_lane = self.base / 'unintegrated'
        git(self.source_root, 'worktree', 'add', '-b', 'unintegrated', str(source_lane))
        pair = lanes.bind_pair(source_lane, tracker_branch='unintegrated-records')
        git(source_lane, 'commit', '--allow-empty', '-m', 'unintegrated work')
        context = SimpleNamespace(mode='personal', source_root=source_lane,
                                  workflow_root=Path(pair['local']['workflow_root']))
        pair = lanes.reconcile_pair(context, git(source_lane, 'rev-parse', 'HEAD'),
                                    git(context.workflow_root, 'rev-parse', 'HEAD'))
        with self.assertRaises(state.PersonalStateError):
            lanes.release_pair(self.source_root, lanes._path(source_lane), pair['portable'])
        self.assertTrue(lanes._path(source_lane).exists())
        self.assertTrue(source_lane.exists())

    def test_tracker_rewrite_requires_reconciled_tracker_references(self):
        git(self.tracker, 'config', 'user.name', 'fixture')
        git(self.tracker, 'config', 'user.email', 'fixture@example.invalid')
        git(self.tracker, 'commit', '--allow-empty', '-m', 'tracker progress')
        retired = git(self.tracker, 'rev-parse', 'HEAD')
        evidence = self.tracker / 'docs/issues/handoff.txt'
        evidence.write_text(retired + '\n')
        git(self.tracker, 'add', 'docs/issues/handoff.txt')
        git(self.tracker, 'commit', '-m', 'Record handoff')
        handoff_commit = git(self.tracker, 'rev-parse', 'HEAD')
        source_revision = git(self.source_root, 'rev-parse', 'HEAD')
        lanes.reconcile_pair(self.context, source_revision, handoff_commit)
        git(self.tracker, 'checkout', '-b', 'rewritten-records', 'HEAD~2')
        git(self.tracker, 'cherry-pick', handoff_commit)
        with self.assertRaisesRegex(state.PersonalStateError, 'stale tracker revision'):
            lanes.rebind_pair(self.context, 'main', 'rewritten-records', source_revision,
                              git(self.tracker, 'rev-parse', 'HEAD'))
        evidence.write_text(git(self.tracker, 'rev-parse', 'HEAD') + '\n')
        git(self.tracker, 'add', 'docs/issues/handoff.txt')
        git(self.tracker, 'commit', '-m', 'Reconcile handoff')
        lanes.rebind_pair(self.context, 'main', 'rewritten-records', source_revision,
                          git(self.tracker, 'rev-parse', 'HEAD'))

    def test_partial_removal_keeps_active_pair_until_retry(self):
        source_lane = self.base / 'partial-removal'
        git(self.source_root, 'worktree', 'add', '-b', 'partial-removal', str(source_lane))
        pair = lanes.bind_pair(source_lane, tracker_branch='partial-records')
        tracker_lane = Path(pair['local']['workflow_root'])
        record = lanes._path(source_lane)
        original_git = state.git
        def fail_tracker_removal(root, *args):
            if args == ('worktree', 'remove', str(tracker_lane)):
                raise state.PersonalStateError('injected tracker removal failure')
            return original_git(root, *args)
        with patch.object(state, 'git', side_effect=fail_tracker_removal):
            with self.assertRaisesRegex(state.PersonalStateError, 'injected'):
                lanes.release_pair(self.source_root, record, pair['portable'],
                    remove_source=True, remove_tracker=True, task_owned_source=True, task_owned_tracker=True)
        self.assertFalse(source_lane.exists())
        self.assertTrue(tracker_lane.exists())
        self.assertTrue(record.exists())
        other = self.base / 'other-release'
        git(self.source_root, 'worktree', 'add', '-b', 'other-release', str(other))
        with self.assertRaises(lanes.PairOccupiedError):
            lanes.bind_pair(other, tracker_root=tracker_lane)
        lanes.release_pair(self.source_root, record, pair['portable'],
                           remove_tracker=True, task_owned_tracker=True)
        self.assertFalse(record.exists())
        self.assertFalse(tracker_lane.exists())

    def test_full_sha256_reference_refuses_reconciliation(self):
        retired = 'a' * 64
        replacement = 'b' * 64
        def fake_git(root, *args):
            if args[0] == 'merge-base':
                raise state.PersonalStateError('rewritten history')
            return {'status': '', 'rev-list': retired, 'ls-tree': 'evidence.md',
                    'show': 'Verified revision: ' + retired}[args[0]]
        with patch.object(state, 'git', side_effect=fake_git):
            with self.assertRaisesRegex(state.PersonalStateError, 'stale source revision'):
                lanes._check_reconciled_references(self.source_root, self.tracker, retired, replacement)

    def test_release_refuses_record_under_another_lane_filename(self):
        record = lanes._path(self.source_root)
        wrong = record.with_name('0' * 24 + '.json')
        wrong.write_bytes(record.read_bytes())
        expected = json.loads(record.read_text())['portable']
        with self.assertRaisesRegex(state.PersonalStateError, 'canonical pair-record path'):
            lanes.release_pair(self.source_root, wrong, expected)
        self.assertTrue(wrong.exists())
        self.assertTrue(record.exists())
        self.assertFalse((record.parent.parent / 'released-pairs').exists())

    def test_public_lane_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPT.with_name('personal_lanes.py')),
                                 'status', '--repo-root', str(self.source_root)],
                                capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)['portable']['tracker']['branch'], 'main')


if __name__ == '__main__':
    unittest.main()
