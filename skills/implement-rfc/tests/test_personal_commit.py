"""Public disposable source/tracker commits, privacy and crash reconciliation."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from project_fixtures import git

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import personal_commit


class PersonalCommitTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.source = self.base / 'source'
        self.source.mkdir()
        self.env = {**os.environ, 'IMPLEMENT_RFC_HOME': str(self.base / 'home')}
        git(self.source, 'init', '-b', 'main')
        git(self.source, 'config', 'user.name', 'fixture')
        git(self.source, 'config', 'user.email', 'fixture@example.invalid')
        for name in ('product.txt', 'unrelated.txt', 'remove.txt'):
            (self.source / name).write_text('original\n')
        git(self.source, 'add', '.')
        git(self.source, 'commit', '-m', 'Initial product')
        self.source_base = git(self.source, 'rev-parse', 'HEAD')
        bound = self.cli('personal_tracker.py', '--json', 'init')
        self.tracker = Path(bound['workflow_root'])
        self.runtime = Path(bound['runtime_root'])
        card = self.tracker / 'docs/issues/20-ready/PRS-0001-demo.md'
        card.parent.mkdir(parents=True)
        card.write_text('---\nschema: "implement-rfc.card.v1"\nid: "PRS-0001"\n'
            'title: "Demo"\nstatus: "Ready"\nrfcs: ["RFC-PRS-0001"]\n'
            'depends_on: []\n---\n\n## Acceptance\n\n- Product improves.\n')
        (self.tracker / 'docs/rfcs/RFC-PRS-0001-demo.md').write_text(
            '---\nid: "RFC-PRS-0001"\ntitle: "Demo"\nstatus: "Accepted"\n---\n')
        (self.tracker / 'docs/issues/NEXT_ID').write_text('PRS-0002\n')
        git(self.tracker, 'add', 'docs')
        git(self.tracker, '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-m', 'Private intake')
        self.acceptance = self.base / 'acceptance.json'
        self.acceptance.write_text(json.dumps({'approved': True, 'decision': 'done',
            'records': [{'criterion': 'product-improves', 'outcome': 'pass',
                'revision': 'replace-with-actual', 'evidence': {'kind': 'observation', 'detail': 'Fixture checked'}}]}))

    def cli(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / script),
            '--repo-root', str(self.source), *args], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def start(self, *paths):
        self.cli('issue_board.py', 'claim', 'PRS-0001', '--json')
        self.tracker_base = git(self.tracker, 'rev-parse', 'HEAD')
        return self.cli('personal_commit.py', 'begin', '--id', 'PRS-0001',
                        '--paths', *(paths or ('product.txt',)))['operation']

    def finish(self, operation, *args, expected=0):
        return self.cli('personal_commit.py', 'finish', '--operation', operation,
            '--message', 'Improve product', '--acceptance', str(self.acceptance), *args, expected=expected)

    def test_public_complete_explicit_files_and_unrelated_index(self):
        operation = self.start('product.txt', 'new.txt', 'remove.txt')
        (self.source / 'product.txt').write_text('better\n')
        (self.source / 'new.txt').write_text('new\n')
        (self.source / 'remove.txt').unlink()
        (self.source / 'unrelated.txt').write_text('staged unrelated\n')
        git(self.source, 'add', 'unrelated.txt')
        staged = git(self.source, 'show', ':unrelated.txt')
        (self.source / 'unrelated.txt').write_text('unstaged unrelated\n')
        (self.source / 'untracked.txt').write_text('untracked unrelated\n')
        result = self.finish(operation)
        self.assertEqual(result['status'], 'complete')
        revision = result['source']['revision']
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), revision)
        self.assertEqual(git(self.source, 'diff', '--name-only', '--', 'product.txt', 'new.txt', 'remove.txt'), '')
        self.assertEqual(git(self.source, 'diff', '--cached', '--name-only'), 'unrelated.txt')
        self.assertEqual(git(self.source, 'show', ':unrelated.txt'), staged)
        self.assertEqual((self.source / 'unrelated.txt').read_text(), 'unstaged unrelated\n')
        self.assertTrue((self.source / 'untracked.txt').exists())
        self.assertEqual(git(self.source, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines(),
                         ['new.txt', 'product.txt', 'remove.txt'])
        card = self.cli('issue_board.py', 'inspect', 'PRS-0001', '--json')
        self.assertEqual(card['fields']['status'], 'Done')
        self.assertEqual(card['fields']['acceptance'][0]['revision'], revision)
        self.assertEqual(git(self.tracker, 'status', '--porcelain'), '')
        self.assertNotIn(str(self.base), git(self.tracker, 'show', 'HEAD'))
        for forbidden in ('PRS-0001', 'RFC-PRS', 'implement-rfc', str(self.tracker)):
            self.assertNotIn(forbidden, git(self.source, 'log', '-1', '-p'))
        self.assertFalse((self.source / '.mask').exists())
        self.assertFalse(any('implement-rfc' in p.name for p in (self.source / '.git').rglob('*')))
        repeated = self.finish(operation)
        self.assertEqual(repeated['source']['revision'], revision)
        self.assertEqual(git(self.source, 'rev-list', '--count', self.source_base + '..HEAD'), '1')

    def test_every_commit_failure_resumes_exactly_once(self):
        # Each boundary starts with an independent disposable checkout and tracker.
        for point in personal_commit.FAILURES:
            with self.subTest(point=point):
                fixture = PersonalCommitTests()
                fixture.setUp()
                try:
                    operation = fixture.start()
                    (fixture.source / 'product.txt').write_text('improvement\n')
                    fixture.finish(operation, '--inject-failure', point, expected=2)
                    pending = fixture.cli('personal_commit.py', 'status', '--operation', operation)
                    self.assertNotEqual(pending['status'], 'complete')
                    if point == 'after-source-commit':
                        self.assertFalse(pending['source']['recorded'])
                        self.assertEqual(git(fixture.source, 'rev-parse', 'HEAD'), pending['source']['revision'])
                        self.assertEqual(git(fixture.tracker, 'rev-parse', 'HEAD'), fixture.tracker_base)
                    result = fixture.cli('personal_commit.py', 'resume', '--operation', operation)
                    self.assertEqual(result['status'], 'complete')
                    self.assertEqual(git(fixture.source, 'status', '--porcelain'), '')
                    self.assertEqual(git(fixture.tracker, 'status', '--porcelain'), '')
                    self.assertEqual(git(fixture.source, 'rev-list', '--count', fixture.source_base + '..HEAD'), '1')
                    self.assertEqual(git(fixture.tracker, 'rev-list', '--count', fixture.tracker_base + '..HEAD'), '1')
                    fixture.cli('personal_commit.py', 'resume', '--operation', operation)
                    self.assertEqual(git(fixture.source, 'rev-parse', 'HEAD'), result['source']['revision'])
                finally:
                    fixture.doCleanups()

    def test_claim_and_before_edits_are_required(self):
        error = self.cli('personal_commit.py', 'begin', '--id', 'PRS-0001', '--paths', 'product.txt', expected=2)
        self.assertIn('committed In Progress', error['error'])
        self.cli('issue_board.py', 'claim', 'PRS-0001', '--json')
        (self.source / 'product.txt').write_text('too early\n')
        error = self.cli('personal_commit.py', 'begin', '--id', 'PRS-0001', '--paths', 'product.txt', expected=2)
        self.assertIn('before editing', error['error'])
        error = self.cli('issue_board.py', 'finish', 'PRS-0001', '--paths', 'product.txt',
                        '--acceptance', str(self.acceptance), '--json', expected=1)
        self.assertIn('personal_commit.py', error['errors'][0]['reason'])

    def test_private_messages_branches_pr_paths_and_content_refuse(self):
        operation = self.start()
        for value in ('Fix PRS-0001', 'RFC-PRS-0001 improvement', 'Update docs/issues/20-ready/PRS-0001-demo.md',
                      'Record RFC_BASE_SHA', 'Improve ' + str(self.tracker)):
            self.cli('personal_commit.py', 'validate-text', '--message', value, expected=2)
        self.cli('personal_commit.py', 'validate-text', '--branch', 'fix/prs-0001', expected=2)
        pr = self.base / 'pr.txt'
        pr.write_text('Complete PRS-0001')
        self.cli('personal_commit.py', 'validate-text', '--pr-text', str(pr), expected=2)
        (self.source / 'product.txt').write_text('private tracker docs/issues/PRS-0001\n')
        self.finish(operation, expected=2)
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)
        (self.source / 'product.txt').write_text('valid improvement\n')
        self.finish(operation, '--pr-text', str(pr), expected=2)
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)

    def test_ordinary_workflow_documentation_is_valid_product_content(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('The implement-rfc skill reads docs/rfcs and docs/issues.\n')
        result = self.finish(operation)
        self.assertEqual(result['status'], 'complete')

    def test_repeated_finish_rejects_a_changed_proposal(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'before-source-commit', expected=2)
        decision = json.loads(self.acceptance.read_text())
        decision['records'][0]['evidence']['detail'] = 'Changed assessment'
        self.acceptance.write_text(json.dumps(decision))
        self.assertIn('proposal differs', self.finish(operation, expected=2)['error'])
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)
        self.assertEqual(self.cli('personal_commit.py', 'resume', '--operation', operation)['status'], 'complete')

    def test_ambiguous_history_refuses_and_preserves_edits(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'after-source-commit', expected=2)
        revision = git(self.source, 'rev-parse', 'HEAD')
        # Advance with ordinary empty commit after repairing only the stale owned index.
        git(self.source, 'add', 'product.txt')
        git(self.source, 'commit', '--allow-empty', '-m', 'Independent work')
        (self.source / 'product.txt').write_text('later edit\n')
        error = self.cli('personal_commit.py', 'resume', '--operation', operation, expected=2)
        self.assertIn('ambiguous recovery', error['error'])
        self.assertEqual((self.source / 'product.txt').read_text(), 'later edit\n')
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)
        self.assertEqual(git(self.source, 'rev-list', '--count', revision + '..HEAD'), '1')

    def test_hooks_and_signing_refuse_without_ref_effect(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        hook = self.source / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        self.assertIn('hooks', self.finish(operation, expected=2)['error'])
        hook.unlink()
        custom = self.base / 'custom-hooks'
        custom.mkdir()
        git(self.source, 'config', 'core.hooksPath', str(custom))
        hook = custom / 'commit-msg'
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        self.assertIn('hooks', self.finish(operation, expected=2)['error'])
        hook.unlink()
        git(self.source, 'config', 'commit.gpgsign', 'true')
        self.assertIn('signing', self.finish(operation, expected=2)['error'])
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)
        self.assertEqual(self.cli('personal_commit.py', 'status', '--operation', operation)['status'], 'editing')

    def test_tracker_acceptance_local_path_refuses_before_source_effect(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        decision = json.loads(self.acceptance.read_text())
        decision['records'][0]['evidence']['detail'] = 'Observed in ' + str(self.source)
        self.acceptance.write_text(json.dumps(decision))
        self.assertIn('portable evidence', self.finish(operation, expected=2)['error'])
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)

    def test_tracker_conflict_and_source_staged_owned_changes_preserved(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'after-source-commit', expected=2)
        (self.source / 'product.txt').write_text('concurrent staged\n')
        git(self.source, 'add', 'product.txt')
        self.assertIn('index entry changed', self.cli('personal_commit.py', 'resume',
            '--operation', operation, expected=2)['error'])
        self.assertEqual(git(self.source, 'show', ':product.txt'), 'concurrent staged')
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)

    def test_human_pending_records_actual_revision(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('candidate\n')
        decision = json.loads(self.acceptance.read_text())
        decision['decision'] = 'human-pending'
        decision['records'][0]['outcome'] = 'pending'
        self.acceptance.write_text(json.dumps(decision))
        result = self.finish(operation)
        card = self.cli('issue_board.py', 'inspect', 'PRS-0001', '--json')['fields']
        self.assertEqual(card['status'], 'Parked')
        self.assertEqual(card['acceptance'][0]['revision'], result['source']['revision'])

    def test_tracker_conflict_preserves_successful_product(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'before-tracker-commit', expected=2)
        revision = git(self.source, 'rev-parse', 'HEAD')
        card = self.tracker / 'docs/issues/30-in-progress/PRS-0001-demo.md'
        card.write_text(card.read_text() + '\nConcurrent tracker note\n')
        error = self.cli('personal_commit.py', 'resume', '--operation', operation, expected=2)
        self.assertIn('tracker completion path changed', error['error'])
        self.assertIn('Concurrent tracker note', card.read_text())
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), revision)
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)

    def test_unsafe_paths_and_uncommitted_claim_refuse(self):
        self.cli('issue_board.py', 'claim', 'PRS-0001', '--json')
        for path in ('../outside', '.git/config', '.', 'new/../product.txt', ':product.txt'):
            self.cli('personal_commit.py', 'begin', '--id', 'PRS-0001', '--paths', path, expected=2)
        link = self.source / 'linked'
        link.symlink_to(self.base, target_is_directory=True)
        self.cli('personal_commit.py', 'begin', '--id', 'PRS-0001', '--paths', 'linked/file', expected=2)
        card = self.tracker / 'docs/issues/30-in-progress/PRS-0001-demo.md'
        card.write_text(card.read_text() + '\nUncommitted claim edit\n')
        error = self.cli('personal_commit.py', 'begin', '--id', 'PRS-0001', '--paths', 'product.txt', expected=2)
        self.assertIn('claim must be committed', error['error'])

    def test_private_branch_rebind_refuses_before_pair_write(self):
        git(self.source, 'branch', '-m', 'fix/PRS-0001')
        error = self.cli('personal_lanes.py', 'rebind', '--source-branch', 'fix/PRS-0001',
            '--tracker-branch', 'main', '--source-revision', self.source_base,
            '--tracker-revision', git(self.tracker, 'rev-parse', 'HEAD'), expected=2)
        self.assertIn('private identifier', error['error'])

    def adopt(self, operation, revision, *args, expected=0):
        return self.cli('personal_commit.py', 'adopt', '--operation', operation,
            '--source-revision', revision, '--acceptance', str(self.acceptance), *args, expected=expected)

    def test_adopt_normal_custom_hook_commit_and_tracker_recovery(self):
        operation = self.start()
        custom = self.base / 'custom-hooks'
        custom.mkdir()
        git(self.source, 'config', 'core.hooksPath', str(custom))
        hook = custom / 'pre-commit'
        hook.write_text('#!/bin/sh\ngit diff --cached --quiet -- product.txt && exit 1\n'
                       'touch "$(dirname "$0")/ran"\nexit 0\n')
        hook.chmod(0o755)
        (self.source / 'product.txt').write_text('normally committed\n')
        # Ordinary Git itself runs the configured hook. The helper does not claim to run it.
        git(self.source, 'add', '--', 'product.txt')
        git(self.source, 'commit', '--only', '-m', 'Improve product normally', '--', 'product.txt')
        self.assertTrue((custom / 'ran').exists())
        revision = git(self.source, 'rev-parse', 'HEAD')
        self.adopt(operation, revision, '--inject-failure', 'before-tracker-commit', expected=2)
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)
        self.cli('personal_commit.py', 'resume', '--operation', operation,
                 '--inject-failure', 'after-tracker-commit', expected=2)
        pending = self.cli('personal_commit.py', 'status', '--operation', operation)
        self.assertFalse(pending['tracker']['recorded'])
        result = self.cli('personal_commit.py', 'resume', '--operation', operation)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['source']['revision'], revision)
        self.assertEqual(git(self.source, 'rev-list', '--count', self.source_base + '..HEAD'), '1')
        self.assertEqual(git(self.source, 'status', '--porcelain'), '')
        self.assertEqual(git(self.tracker, 'status', '--porcelain'), '')

    def test_adopt_wrong_parent_extra_path_and_private_message_refuse(self):
        for reason in ('wrong-parent', 'extra-path', 'private-message'):
            with self.subTest(reason=reason):
                fixture = PersonalCommitTests()
                fixture.setUp()
                try:
                    operation = fixture.start()
                    if reason == 'wrong-parent':
                        git(fixture.source, 'commit', '--allow-empty', '-m', 'Intermediate work')
                    (fixture.source / 'product.txt').write_text('normally committed\n')
                    paths = ['product.txt']
                    if reason == 'extra-path':
                        (fixture.source / 'unrelated.txt').write_text('also changed\n')
                        paths.append('unrelated.txt')
                    git(fixture.source, 'add', '--', *paths)
                    git(fixture.source, 'commit', '-m',
                        'Complete PRS-0001' if reason == 'private-message' else 'Improve product')
                    revision = git(fixture.source, 'rev-parse', 'HEAD')
                    error = fixture.adopt(operation, revision, expected=2)
                    expected = {'wrong-parent': 'parent', 'extra-path': 'ownership',
                                'private-message': 'private identifier'}[reason]
                    self.assertIn(expected, error['error'])
                    self.assertEqual(git(fixture.source, 'rev-parse', 'HEAD'), revision)
                    self.assertEqual(git(fixture.tracker, 'rev-parse', 'HEAD'), fixture.tracker_base)
                    self.assertEqual(fixture.cli('personal_commit.py', 'status', '--operation', operation)['status'], 'editing')
                finally:
                    fixture.doCleanups()

    def test_corrupt_prepared_identity_refuses_before_effect(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'before-source-commit', expected=2)
        path = self.runtime / 'product-commits' / (operation + '.json')
        receipt = json.loads(path.read_text())
        receipt['source']['tree'] = '0' * 40
        path.write_text(json.dumps(receipt))
        error = self.cli('personal_commit.py', 'resume', '--operation', operation, expected=2)
        self.assertIn('receipt identity', error['error'])
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)

    def test_concurrent_commit_after_snapshot_cannot_revert_unowned_file(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        real_git = personal_commit.git
        concurrent = []

        def interleave(root, *args, **kwargs):
            result = real_git(root, *args, **kwargs)
            if root == self.source and args[0] == 'read-tree' and not concurrent:
                (self.source / 'unrelated.txt').write_text('concurrent improvement\n')
                git(self.source, 'add', '--', 'unrelated.txt')
                git(self.source, 'commit', '--only', '-m', 'Improve unrelated behavior', '--', 'unrelated.txt')
                concurrent.append(git(self.source, 'rev-parse', 'HEAD'))
            return result

        with patch.dict(os.environ, self.env):
            context = personal_commit.project_config.resolve_context(repo_root=self.source, mode='personal')
            with personal_commit.operation_lock(context) as directory:
                path, receipt = personal_commit.load(directory, operation, context)
                with patch.object(personal_commit, 'git', side_effect=interleave):
                    personal_commit.prepare(context, receipt, directory, 'Improve product',
                                            json.loads(self.acceptance.read_text()), None)
                personal_commit.save(path, receipt)
                self.assertEqual(receipt['source']['parent'], self.source_base)
                self.assertEqual(git(self.source, 'diff-tree', '--no-commit-id', '--name-only', '-r',
                                     receipt['source']['revision']), 'product.txt')
                with self.assertRaisesRegex(personal_commit.state.PersonalStateError, 'ambiguous recovery'):
                    personal_commit.resume(context, receipt, path)
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), concurrent[0])
        self.assertEqual(git(self.source, 'show', 'HEAD:unrelated.txt'), 'concurrent improvement')
        self.assertEqual((self.source / 'unrelated.txt').read_text(), 'concurrent improvement\n')
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)

    def test_corrupt_tracker_payloads_refuse_before_any_effect(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'before-source-commit', expected=2)
        path = self.runtime / 'product-commits' / (operation + '.json')
        original = path.read_text()
        for field, lane in (('changes', '60-done'), ('originals', '30-in-progress')):
            with self.subTest(field=field):
                receipt = json.loads(original)
                relative = next(p for p in receipt['tracker'][field] if lane in p)
                receipt['tracker'][field][relative] = personal_commit.encode(b'Corrupted recovery payload\n')
                path.write_text(json.dumps(receipt))
                error = self.cli('personal_commit.py', 'resume', '--operation', operation, expected=2)
                self.assertIn('payload differs', error['error'])
                self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)
                self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)
                self.assertEqual(git(self.tracker, 'status', '--porcelain'), '')

    def test_post_sync_tracker_corruption_cannot_report_complete(self):
        operation = self.start()
        (self.source / 'product.txt').write_text('better\n')
        self.finish(operation, '--inject-failure', 'before-source-commit', expected=2)
        real_sync = personal_commit.sync_index

        def corrupt_after_sync(root, op, paths, directory):
            real_sync(root, op, paths, directory)
            if root == self.tracker:
                card = next(p for p in op['paths'] if '60-done' in p)
                (root / card).write_text('Concurrent corruption after synchronization\n')

        with patch.dict(os.environ, self.env):
            context = personal_commit.project_config.resolve_context(repo_root=self.source, mode='personal')
            with personal_commit.operation_lock(context) as directory:
                path, receipt = personal_commit.load(directory, operation, context)
                with patch.object(personal_commit, 'sync_index', side_effect=corrupt_after_sync):
                    with self.assertRaisesRegex(personal_commit.state.PersonalStateError, 'worktree differs'):
                        personal_commit.resume(context, receipt, path)
                self.assertEqual(json.loads(path.read_text())['status'], 'tracker-committed')
                self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), receipt['source']['revision'])

    def test_encoded_private_product_text_refuses_finish_and_adopt(self):
        operation = self.start()
        for encoding in ('utf-16', 'utf-32', 'utf-16-le', 'utf-16-be'):
            with self.subTest(encoding=encoding):
                (self.source / 'product.txt').write_bytes('Private PRS-0001 RFC-PRS-0001\n'.encode(encoding))
                self.finish(operation, expected=2)
                self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)
        (self.source / 'product.txt').write_bytes('Private PRS-0001 RFC-PRS-0001\n'.encode('utf-16'))
        git(self.source, 'add', '--', 'product.txt')
        git(self.source, 'commit', '-m', 'Improve product normally')
        revision = git(self.source, 'rev-parse', 'HEAD')
        self.assertIn('private identifier', self.adopt(operation, revision, expected=2)['error'])
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)

    def test_ordinary_utf16_product_text_remains_supported(self):
        operation = self.start()
        (self.source / 'product.txt').write_bytes('Ordinary product improvement\n'.encode('utf-16'))
        self.assertEqual(self.finish(operation)['status'], 'complete')

    def test_opaque_binary_product_refuses_without_committing_either_side(self):
        operation = self.start()
        (self.source / 'product.txt').write_bytes(b'\x89PNG\r\n\x1a\n')
        refusal = self.finish(operation, expected=2)
        self.assertIn('unsupported text encoding', refusal['error'])
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), self.source_base)
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)

    def test_opaque_binary_normal_commit_cannot_be_adopted(self):
        operation = self.start()
        (self.source / 'product.txt').write_bytes(b'\x89PNG\r\n\x1a\n')
        git(self.source, 'add', '--', 'product.txt')
        git(self.source, 'commit', '-m', 'Improve product normally')
        revision = git(self.source, 'rev-parse', 'HEAD')
        refusal = self.adopt(operation, revision, expected=2)
        self.assertIn('unsupported text encoding', refusal['error'])
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), revision)
        self.assertEqual(git(self.tracker, 'rev-parse', 'HEAD'), self.tracker_base)


if __name__ == '__main__':
    unittest.main()
