"""Public workflow contracts for scopes, Git boundaries, and counter history."""
import json
from pathlib import Path
import sys
import unittest

import test_issue_board as fixtures
from project_fixtures import git, write_context

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import board_model as board


class UnifiedTests(unittest.TestCase):
    setUp = fixtures.BoardTests.setUp
    card = fixtures.BoardTests.card
    public = fixtures.BoardTests.public
    errors = fixtures.BoardTests.errors

    def commit_fixture(self):
        git(self.root, 'config', 'user.name', 'Fixture')
        git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        git(self.root, 'checkout', '-B', 'main')
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-m', 'fixture')

    def acceptance(self, outcome='pass', decision='done'):
        path = self.root / 'decision.json'
        path.write_text(json.dumps({'approved': True, 'decision': decision, 'records':[
            {'criterion':'AC1', 'outcome':outcome, 'revision':git(self.root,'rev-parse','HEAD'),
             'evidence':{'kind':'observation','detail':'Fixture exercised through selected public path'}}]}))
        return str(path)

    def test_multi_rfc_metadata_and_scoped_historical_findings(self):
        selected = self.card(lane='ready', extra='metadata: {"custom":{"array":[1,true,null,"comma,colon:"]}}\n')
        self.card(2, lane='backlog')
        historical = self.card(3, lane='done', deps=('XYZ-0002',))
        historical.write_text(historical.read_text().replace('["RFC-XYZ-0001"]','[]'))
        self.public('validate', expected=1)
        self.assertEqual(self.public('queue','--rfc','RFC-XYZ-0001')['next'],'XYZ-0001')
        second = self.root/'tracker/rfcs/RFC-XYZ-0002-second.md'
        second.write_text('---\nid: RFC-XYZ-0002\nstatus: Implemented\n---\n')
        selected.write_text(selected.read_text().replace('["RFC-XYZ-0001"]','["RFC-XYZ-0001","RFC-XYZ-0002"]'))
        self.assertEqual(self.public('queue','--rfc','RFC-XYZ-0002')['next'],'XYZ-0001')
        self.assertEqual(self.public('inspect','XYZ-0001')['fields']['metadata']['custom']['array'][3], 'comma,colon:')

    def test_human_queue_reuses_done_prerequisites_without_replaying_history(self):
        self.config['bookkeeping']['parked_on'] = []
        write_context(self.root,config=self.config)
        self.card(1,lane='parked',deps=('XYZ-0002',),extra='parked_on: human-review\n')
        self.card(2,lane='done',deps=('XYZ-0003',))
        self.card(3,lane='blocked',extra='blocked_by: historical-defect\n')
        self.public('validate',expected=1)
        result=self.public('queue','--human-waiting')
        self.assertEqual([c['id'] for c in result['cards']],['XYZ-0001'])

    def test_explicit_scope_priority_and_human_waits(self):
        self.card(1,lane='ready',extra='priority: P3\n')
        self.card(2,lane='ready',extra='priority: P1\narea: descriptive-name\n')
        self.config['bookkeeping']['parked_on'] = []
        write_context(self.root, config=self.config)
        self.card(3,lane='parked',extra='parked_on: human-review\n')
        self.public('queue',expected=1)
        self.assertEqual(self.public('queue','--all')['next'],'XYZ-0002')
        self.assertEqual(self.public('queue','--area','XYZ')['next'],'XYZ-0002')
        self.assertEqual(self.public('queue','--area','descriptive-name')['next'],'XYZ-0002')
        waiting = self.public('queue','--human-waiting')
        self.assertEqual([c['id'] for c in waiting['cards']],['XYZ-0003'])
        self.assertIsNone(waiting['next'])

    def test_claim_finish_preserve_unrelated_work_and_bind_evidence(self):
        self.card(lane='ready'); self.commit_fixture()
        (self.root/'unrelated.txt').write_text('user edits')
        claimed = self.public('claim','XYZ-0001')
        self.assertEqual(git(self.root,'show','--no-renames','--format=','--name-only',claimed['commit']).count('XYZ-0001'),2)
        (self.root/'feature.txt').write_text('implemented')
        result = self.public('finish','XYZ-0001','--acceptance',self.acceptance(),'--paths','feature.txt')
        self.assertIn('unrelated.txt',git(self.root,'status','--short'))
        self.assertNotIn('unrelated.txt',git(self.root,'show','--format=','--name-only',result['commit']))
        self.assertEqual(self.public('inspect','XYZ-0001')['fields']['acceptance'][0]['outcome'],'pass')
        self.assertEqual(self.public('inspect','XYZ-0001')['fields']['status'],'Done')

    def test_claim_refuses_staged_work_and_stale_revision(self):
        source = self.card(lane='ready'); self.commit_fixture()
        (self.root/'staged.txt').write_text('pending'); git(self.root,'add','staged.txt')
        self.public('claim','XYZ-0001',expected=1)
        self.assertTrue(source.exists())
        self.assertEqual(git(self.root,'diff','--cached','--name-only'),'staged.txt')
        git(self.root,'reset','HEAD','--','staged.txt')
        self.public('claim','XYZ-0001','--expect-revision','0'*40,expected=1)
        self.assertTrue(source.exists())

    def test_finish_rejects_pending_done_and_dirty_implicit_links(self):
        source = self.card(lane='ready'); self.commit_fixture()
        self.public('finish','XYZ-0001','--acceptance',self.acceptance('pending'),expected=1)
        source.write_text(source.read_text()+'user changed card\n')
        self.public('finish','XYZ-0001','--acceptance',self.acceptance(),expected=1)
        self.assertTrue(source.exists())
        self.assertIn('user changed card',source.read_text())

    def test_human_pending_is_parked_without_done_claim(self):
        self.config['bookkeeping']['parked_on'] = []
        write_context(self.root,config=self.config)
        self.card(lane='ready'); self.commit_fixture()
        self.public('finish','XYZ-0001','--acceptance',self.acceptance('pending','human-pending'))
        self.assertEqual(self.public('queue','--human-waiting')['cards'][0]['reason'],'human-review')

    def test_reservation_high_water_branches_tags_and_checkpoint_exclusion(self):
        self.card(); self.commit_fixture()
        counter = self.root/'tracker/cards/NEXT_ID'
        git(self.root,'checkout','-b','counter-branch')
        counter.write_text('XYZ-0200\n'); git(self.root,'add',str(counter));git(self.root,'commit','-m','reserve elsewhere')
        git(self.root,'tag','counter-tag');git(self.root,'checkout','main')
        self.assertIn('historical high water',self.public('allocate','--reserve-for','test',expected=1)['errors'][0]['reason'])
        git(self.root,'branch','-D','counter-branch')
        self.public('allocate','--reserve-for','test',expected=1)  # tag still protects
        git(self.root,'update-ref','refs/checkpoints/transient','counter-tag')
        git(self.root,'tag','-d','counter-tag')
        result = self.public('allocate','--count','2','--reserve-for','test')
        self.assertEqual(result['ids'],['XYZ-0099','XYZ-0100'])
        counter.write_text('XYZ-0099\n')
        self.assertIn('reserved',self.errors())

    def test_area_counters_scoped_queue_and_visible_history_bound(self):
        self.card(); self.commit_fixture()
        (self.root/'tracker/cards/NEXT_ID').unlink()
        folder=self.root/'tracker/cards/_next_id';folder.mkdir()
        (folder/'XYZ').write_text('XYZ-0099\n'); (folder/'AAA').write_text('AAA-0001\n')
        self.config['next_id']={'mode':'per-area','path':'tracker/cards/_next_id'}
        self.config['allocation']={'history_limit':1}
        write_context(self.root,config=self.config)
        self.commit_fixture()
        result=self.public('allocate','--area','AAA','--count','2','--reserve-for','area-worker')
        self.assertEqual(result['ids'],['AAA-0001','AAA-0002'])
        fresh=self.public('allocate','--area','NEW','--reserve-for','new-area','--purpose','new component')
        self.assertEqual(fresh['ids'],['NEW-0001'])
        self.commit_fixture()
        result=self.public('allocate','--area','AAA','--reserve-for','area-worker',expected=1)
        self.assertTrue(any('bound' in e['reason'] for e in result['errors']))

    def test_scoped_mutation_does_not_ignore_own_dependency_defect(self):
        self.card(1,lane='backlog',deps=('XYZ-0002',)); self.card(2,lane='backlog')
        self.public('move','XYZ-0001','--to','ready',expected=1)
        self.public('validate','--include','XYZ-0001')  # deferred dependency is honest


if __name__=='__main__': unittest.main()

class SelectedInstructionTests(unittest.TestCase):
    def test_leaf_packets_preserve_selected_authority_and_uncertainty(self):
        import render_runtime_adapters as renderer
        from project_fixtures import CONFIG
        import copy
        root = Path(__file__).resolve().parents[1]
        roles = renderer.load_json(root / 'config/roles.json')['roles']
        project = copy.deepcopy(CONFIG)
        project['role_addenda'] = {'rfc-worker':['Preserve fixture-owner constraint exactly.']}
        route = {'model':'fixture-model','effort':'high'}
        utility = renderer.role_prompt('rfc-utility', roles['rfc-utility'], route, project)
        runner = renderer.role_prompt('rfc-test-runner', roles['rfc-test-runner'], route, project)
        worker = renderer.role_prompt('rfc-worker', roles['rfc-worker'], route, project)
        self.assertIn('do not broaden the question or infer architecture', utility)
        self.assertIn('Distinguish not-found from not-searched', utility)
        self.assertNotIn('Preserve fixture-owner constraint exactly.', utility)
        self.assertNotIn('Preserve fixture-owner constraint exactly.', runner)
        self.assertIn('Preserve fixture-owner constraint exactly.', worker)
        self.assertIn('Do not diagnose root cause, choose additional tests', runner)
        self.assertIn('exclusive list of allowed files or path scopes', worker)
        self.assertIn('Uncertainties', worker)
        for packet in (utility, runner, worker):
            self.assertIn('do not spawn agents', packet)
            self.assertNotIn('assets/', packet)
            self.assertNotIn('bounded-execution.md', packet)
        core = (root / 'SKILL.md').read_text()
        core += (root / 'references/verification-and-closeout.md').read_text()
        self.assertIn('A delivered report or successful command never approves acceptance', core)
        self.assertNotIn('slice-order.v1', core)
