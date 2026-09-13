"""Composed offline qualification through public helpers and disposable Git remotes.

Detailed hostile-input and crash-boundary checks remain in test_personal_commit,
_binding and _lanes; this course checks their lifecycle composition.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import git, write_context
from test_personal_binding import snapshot

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


class QualificationCourseTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.env = {**os.environ, 'IMPLEMENT_RFC_HOME': str(self.base / 'home')}

    def cli(self, root, script, *args, code=0):
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / script),
            '--repo-root', str(root), *args], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout) if result.stdout else {'error': result.stderr}

    def repository(self, name):
        root = self.base / name
        root.mkdir()
        git(root, 'init', '-b', 'main')
        git(root, 'config', 'user.name', 'fixture')
        git(root, 'config', 'user.email', 'fixture@example.invalid')
        (root / 'product.txt').write_text('original\n')
        (root / 'unrelated.txt').write_text('original\n')
        self.commit(root, 'Initial product')
        return root

    def commit(self, root, message):
        git(root, 'add', '.')
        git(root, '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-m', message)

    def intake(self, source, tracker, count=1):
        self.cli(source, 'issue_board.py', 'allocate', '--count', str(count),
                 '--reserve-for', 'course', '--json')
        self.commit(tracker, 'Reserve private work')
        rfc = tracker / 'docs/rfcs/RFC-PRS-0001-demo.md'
        rfc.parent.mkdir(parents=True, exist_ok=True)
        rfc.write_text('---\nid: "RFC-PRS-0001"\ntitle: "Demo"\nstatus: "Accepted"\n---\n')
        for number in range(1, count + 1):
            card = tracker / f'docs/issues/10-backlog/PRS-{number:04}-demo.md'
            card.parent.mkdir(parents=True, exist_ok=True)
            card.write_text(f'---\nschema: "implement-rfc.card.v1"\nid: "PRS-{number:04}"\n'
                'title: "Demo"\nstatus: "Backlog"\nrfcs: ["RFC-PRS-0001"]\n'
                'depends_on: []\n---\n\n## Acceptance\n\nAC01: Product improves.\nAC02: Review completes.\n')
        self.commit(tracker, 'Private intake')
        raw = self.base / ('raw-' + source.name)
        raw.mkdir()
        (raw / 'milestone-plan.json').write_text(json.dumps({
            'schema': 'implement-rfc.milestone-plan.v1', 'id': 'course',
            'scope': {'rfcs': ['RFC-PRS-0001'], 'issues': [f'PRS-{n:04}' for n in range(1, count + 1)]},
            'milestones': [{'id': 'usable', 'outcome': 'Product improves',
                'work': [{'issue': f'PRS-{n:04}'} for n in range(1, count + 1)],
                'depends_on': [], 'exit_criteria': ['Product and review complete'],
                'boundary': 'One offline course'}]}))
        self.assertEqual(self.cli(source, 'milestone_plan.py', 'adopt', '--source-root',
            str(raw), '--json')['state'], 'adopted')
        self.commit(tracker, 'Adopt private plan')

    def claim(self, source, tracker, card):
        self.cli(source, 'issue_board.py', 'move', card, '--to', '20-ready', '--json')
        self.commit(tracker, 'Promote work')
        self.cli(source, 'issue_board.py', 'claim', card, '--json')

    def acceptance(self, pending=False):
        path = self.base / 'acceptance.json'
        path.write_text(json.dumps({'approved': True, 'decision': 'human-pending' if pending else 'done',
            'records': [{'criterion': criterion, 'outcome': 'pending' if pending and criterion == 'AC02' else 'pass',
                'revision': 'fixture', 'evidence': {'kind': 'observation', 'detail': 'Disposable course check'}}
                for criterion in ('AC01', 'AC02')]}))
        return path

    def test_private_course_with_paired_lanes_recovery_and_separate_remotes(self):
        source = self.repository('source')
        baseline = git(source, 'rev-parse', 'HEAD')
        untouched = snapshot(source)
        bound = self.cli(source, 'personal_tracker.py', '--json', 'init')
        tracker = Path(bound['workflow_root'])
        for script, args in [('personal_tracker.py', ('--json', 'status')),
                             ('project_config.py', ('--json',)),
                             ('personal_lanes.py', ('status',))]:
            self.cli(source, script, *args)
        self.assertEqual(snapshot(source), untouched)
        self.intake(source, tracker, count=4)
        self.assertEqual(snapshot(source), untouched)
        self.assertEqual(self.cli(source, 'personal_lanes.py', 'sync')['status'], 'local-only')
        self.assertEqual(git(tracker, 'remote'), '')

        # All four crash boundaries occur in the same ongoing private run.
        expected_revisions = []
        for number, point in enumerate(('before-source-commit', 'after-source-commit',
                'before-tracker-commit', 'after-tracker-commit'), 1):
            self.claim(source, tracker, f'PRS-{number:04}')
            operation = self.cli(source, 'personal_commit.py', 'begin', '--id',
                f'PRS-{number:04}', '--paths', 'product.txt')['operation']
            (source / 'product.txt').write_text(f'Improvement {number}\n')
            (source / 'unrelated.txt').write_text('staged unrelated\n')
            git(source, 'add', 'unrelated.txt')
            (source / 'unrelated.txt').write_text('unstaged unrelated\n')
            verified = self.cli(source, 'record_evidence.py', '--criterion', 'AC01',
                '--output', f'verify-{number}.json', '--', 'git', 'diff', '--check')
            self.assertEqual(verified['evidence']['exit_code'], 0)
            self.cli(source, 'personal_commit.py', 'finish', '--operation', operation,
                '--message', f'Improve product step {number}', '--acceptance', str(self.acceptance()),
                '--inject-failure', point, code=2)
            self.assertNotEqual(self.cli(source, 'personal_commit.py', 'status',
                '--operation', operation)['status'], 'complete')
            finished = self.cli(source, 'personal_commit.py', 'resume', '--operation', operation)
            self.assertEqual(finished['status'], 'complete')
            expected_revisions.append(finished['source']['revision'])
            self.cli(source, 'personal_commit.py', 'resume', '--operation', operation)
            self.assertEqual(git(source, 'rev-parse', 'HEAD'), expected_revisions[-1])
            self.assertEqual(git(source, 'show', ':unrelated.txt'), 'staged unrelated')
            self.assertEqual((source / 'unrelated.txt').read_text(), 'unstaged unrelated\n')
            self.assertEqual(self.cli(source, 'issue_board.py', 'inspect', f'PRS-{number:04}',
                '--json')['fields']['acceptance'][0]['revision'], expected_revisions[-1])
        # Fixture-only cleanup of deliberately created unrelated edits before lane operations.
        git(source, 'restore', '--staged', '--worktree', 'unrelated.txt')
        self.assertEqual(self.cli(source, 'issue_board.py', 'queue', '--rfc', 'RFC-PRS-0001',
            '--history', '--json')['done_count'], 4)

        lanes = []
        for name in ('feature-one', 'feature-two'):
            lane = self.base / name
            git(source, 'worktree', 'add', '-b', name, str(lane))
            pair = self.cli(lane, 'personal_lanes.py', 'bind', '--tracker-branch', name + '-records')
            lane_tracker = Path(pair['local']['workflow_root'])
            self.assertEqual(git(lane_tracker, 'show', 'HEAD:docs/issues/NEXT_ID'),
                             git(tracker, 'show', 'HEAD:docs/issues/NEXT_ID'))
            self.cli(lane, 'personal_lanes.py', 'status')
            lanes.append((lane, lane_tracker))
        self.assertNotEqual(lanes[0][1], lanes[1][1])
        lane, lane_tracker = lanes[0]
        git(lane, 'branch', '-m', 'renamed-feature')
        self.assertIn('branch changed', self.cli(lane, 'personal_lanes.py', 'status', code=2)['error'])
        self.cli(lane, 'personal_lanes.py', 'rebind', '--source-branch', 'renamed-feature',
            '--tracker-branch', 'feature-one-records', '--source-revision', git(lane, 'rev-parse', 'HEAD'),
            '--tracker-revision', git(lane_tracker, 'rev-parse', 'HEAD'))
        # A second clone is never associated merely because its remote matches.
        clone = self.base / 'clone'
        git(source, 'clone', str(source), str(clone))
        self.cli(clone, 'project_config.py', '--mode', 'personal', '--json', code=2)
        self.cli(clone, 'personal_tracker.py', '--workflow-root', str(tracker), '--json', 'init')
        self.cli(clone, 'personal_lanes.py', 'bind', '--tracker-branch', 'clone-records')
        self.cli(clone, 'personal_lanes.py', 'status')

        for name, root in [('source', source), ('tracker', tracker)]:
            remote = self.base / (name + '.git')
            remote.mkdir()
            git(remote, 'init', '--bare', '-b', 'main')
            git(root, 'remote', 'add', 'sync', str(remote))
        sync = ('sync', '--source-remote', 'sync', '--tracker-remote', 'sync',
                '--source-branch', 'main', '--tracker-branch', 'main')
        self.cli(source, 'personal_lanes.py', *sync, code=2)
        completed = self.cli(source, 'personal_lanes.py', *sync, '--authorize-push')
        self.assertEqual(completed['completed'], ['source', 'tracker'])
        self.assertEqual(git(self.base / 'source.git', 'rev-parse', 'main'), expected_revisions[-1])
        self.assertEqual(git(self.base / 'tracker.git', 'rev-parse', 'main'), git(tracker, 'rev-parse', 'HEAD'))
        divergent = self.base / 'divergent'
        git(tracker, 'clone', str(self.base / 'tracker.git'), str(divergent))
        git(divergent, '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '--allow-empty', '-m', 'Other tracker progress')
        git(divergent, 'push', 'origin', 'main')
        before_conflict = git(tracker, 'rev-parse', 'HEAD')
        self.cli(source, 'personal_lanes.py', *sync, '--authorize-push', code=2)
        self.assertEqual(git(tracker, 'rev-parse', 'HEAD'), before_conflict)

        # Inspect every generated source commit, its entire tree, and all source Git metadata.
        self.assertEqual(git(source, 'rev-list', '--reverse', baseline + '..HEAD').splitlines(), expected_revisions)
        forbidden = ('PRS-000', 'RFC-PRS', str(tracker), str(Path(bound['runtime_root'])),
                     'implement-rfc.card', 'milestone-plan', 'workflow_root')
        for revision in expected_revisions:
            self.assertEqual(git(source, 'diff-tree', '--no-commit-id', '--name-only', '-r', revision), 'product.txt')
            self.assertEqual(set(git(source, 'ls-tree', '-r', '--name-only', revision).splitlines()),
                             {'product.txt', 'unrelated.txt'})
            for token in forbidden:
                self.assertNotIn(token, git(source, 'show', '--format=fuller', revision))
        for path in (source / '.git').rglob('*'):
            if path.is_file() and 'objects' not in path.relative_to(source / '.git').parts:
                for token in forbidden:
                    self.assertNotIn(token.encode(), path.read_bytes(), str(path))
        self.assertEqual(git(source, 'status', '--porcelain'), '')
        print(json.dumps({'course': 'private', 'baseline': baseline,
            'source_commits': [{'revision': revision,
                'message': git(source, 'show', '-s', '--format=%B', revision),
                'paths': git(source, 'diff-tree', '--no-commit-id', '--name-only', '-r', revision).splitlines()}
                for revision in expected_revisions],
            'source_remote_revision': git(self.base / 'source.git', 'rev-parse', 'main'),
            'tracker_revision': before_conflict, 'setup_snapshot_entries': len(untouched),
            'paired_lanes': len(lanes), 'conflict_preserved': True}), flush=True)

    def test_literal_rebase_requires_committed_reference_repair(self):
        source = self.repository('rebase-source')
        bound = self.cli(source, 'personal_tracker.py', '--json', 'init')
        tracker = Path(bound['workflow_root'])
        lane = self.base / 'rebase-lane'
        git(source, 'worktree', 'add', '-b', 'improve-feature', str(lane))
        pair = self.cli(lane, 'personal_lanes.py', 'bind', '--tracker-branch', 'feature-records')
        lane_tracker = Path(pair['local']['workflow_root'])
        (lane / 'feature.txt').write_text('Feature improvement\n')
        self.commit(lane, 'Add feature behavior')
        retired = git(lane, 'rev-parse', 'HEAD')
        evidence = lane_tracker / 'docs/issues/rebase-evidence.md'
        evidence.write_text('Verified product revision: ' + retired + '\n')
        self.commit(lane_tracker, 'Record feature evidence')
        self.cli(lane, 'personal_lanes.py', 'reconcile', '--source-revision', retired,
            '--tracker-revision', git(lane_tracker, 'rev-parse', 'HEAD'))
        (source / 'foundation.txt').write_text('Independent foundation\n')
        self.commit(source, 'Add foundation behavior')
        foundation = git(source, 'rev-parse', 'HEAD')
        git(lane, 'rebase', 'main')
        rebased = git(lane, 'rev-parse', 'HEAD')
        self.assertNotEqual(retired, rebased)
        self.assertEqual(git(lane, 'rev-parse', 'HEAD^'), foundation)
        self.assertIn('history rewritten', self.cli(lane, 'personal_lanes.py', 'status', code=2)['error'])
        args = ('reconcile', '--source-revision', rebased,
                '--tracker-revision', git(lane_tracker, 'rev-parse', 'HEAD'))
        self.assertIn('stale source revision', self.cli(lane, 'personal_lanes.py', *args, code=2)['error'])
        evidence.write_text('Verified product revision: ' + rebased + '\n')
        self.assertIn('commit reconciled', self.cli(lane, 'personal_lanes.py', *args, code=2)['error'])
        self.commit(lane_tracker, 'Reconcile feature evidence')
        repaired = self.cli(lane, 'personal_lanes.py', 'reconcile', '--source-revision', rebased,
            '--tracker-revision', git(lane_tracker, 'rev-parse', 'HEAD'))
        self.assertEqual(repaired['portable']['source']['revision'], rebased)
        self.assertEqual(git(lane_tracker, 'show', 'HEAD:docs/issues/rebase-evidence.md'),
                         'Verified product revision: ' + rebased)
        self.cli(lane, 'personal_lanes.py', 'status')
        # Include the retired commit, which is no longer reachable from a branch.
        commits = []
        for revision in (retired, foundation, rebased):
            text = git(source, 'show', '--format=fuller', revision)
            for forbidden in ('PRS-', 'feature-records', str(tracker), 'workflow_root'):
                self.assertNotIn(forbidden, text)
            commits.append({'revision': revision, 'message': git(source, 'show', '-s', '--format=%B', revision)})
        print(json.dumps({'course': 'literal-rebase', 'source_commits': commits,
            'repaired_revision': rebased}), flush=True)

    def test_shared_plan_partial_acceptance_stale_return_and_closeout_parity(self):
        outcomes = []
        for mode in ('project', 'personal'):
            source = self.repository(mode)
            if mode == 'personal':
                bound = self.cli(source, 'personal_tracker.py', '--json', 'init')
                tracker = Path(bound['workflow_root'])
            else:
                tracker = source
                config = write_context(source)
                config['bookkeeping'] = {
                    'deferring_lanes': ['00-inbox', '10-backlog', '50-blocked'],
                    'parked_on': ['human-review'], 'blocked_by_forbidden_prefixes': [],
                    'link_roots': ['docs/issues', 'docs/rfcs'],
                    'protected_globs': [], 'editable_globs': []}
                write_context(source, config=config)
                (source / 'docs/issues').mkdir(parents=True)
                (source / 'docs/issues/NEXT_ID').write_text('PRS-0001\n')
                self.commit(source, 'Configure project workflow')
            self.intake(source, tracker)
            self.claim(source, tracker, 'PRS-0001')
            assignment = self.cli(source, 'coordinator_handoff.py', 'assign', '--target', 'RFC-PRS-0001',
                '--run-id', 'course', '--dispatch-id', 'one', '--producer-id', 'fixture',
                '--mandate-revision', '1', '--json')
            reply = {key: assignment[key] for key in ('run_id', 'dispatch_id', 'producer_id', 'mandate_revision', 'milestone')}
            reply.update(schema='implement-rfc.milestone-return.v2', disposition='continue-milestone',
                summary='Partial course', candidate_revision=git(source, 'rev-parse', 'HEAD'),
                handoff_ref='docs/rfcs/RFC-PRS-0001-demo.md', ownership='quiescent', next_objective='Review',
                required_pending=['AC02'], evidence_refs=['docs/rfcs/RFC-PRS-0001-demo.md'],
                binding=assignment['binding'], acceptance_records=[],
                continuation={'intent': 'continue', 'next_milestone': 'usable', 'reason': 'current-milestone', 'detail': 'Review pending'})
            if 'repository_state' in assignment:
                reply['repository_state'] = assignment['repository_state']
            state_root = Path(bound['runtime_root']) if mode == 'personal' else source
            state_root.mkdir(parents=True, exist_ok=True)
            afile, rfile = state_root / 'assignment.json', state_root / 'return.json'
            afile.write_text(json.dumps(assignment))
            rfile.write_text(json.dumps(reply))
            check = lambda: self.cli(source, 'coordinator_handoff.py', 'check', '--assignment', afile.name,
                '--return-file', rfile.name, '--execution', 'quiescent', '--json')['action']
            actions = [check()]
            reply['dispatch_id'] = 'stale'
            rfile.write_text(json.dumps(reply))
            actions.append(check())
            actions.append(self.cli(source, 'issue_board.py', 'finish', 'PRS-0001', '--acceptance',
                str(self.acceptance(pending=True)), '--json')['lane'])
            actions.append(self.cli(source, 'issue_board.py', 'queue', '--human-waiting', '--json')['cards'][0]['id'])
            actions.append(self.cli(source, 'issue_board.py', 'finish', 'PRS-0001', '--acceptance',
                str(self.acceptance()), '--json')['lane'])
            actions.append(self.cli(source, 'issue_board.py', 'queue', '--rfc', 'RFC-PRS-0001', '--history', '--json')['done_count'])
            outcomes.append(actions)
        self.assertEqual(outcomes[0], outcomes[1])
        self.assertEqual(outcomes[0], ['resume-integrator', 'ignore-stale', '40-parked', 'PRS-0001', '60-done', 1])


if __name__ == '__main__':
    unittest.main()
