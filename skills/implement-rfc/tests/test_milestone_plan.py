"""Raw authored plans through two installed links, from unrelated cwd."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import init_repo

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import milestone_plan as mp


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.roots = [self.base / name for name in ('one', 'two')]
        for root in self.roots:
            init_repo(root, token=root.name)
            link = root / '.agents/skills/implement-rfc'
            link.parent.mkdir(parents=True)
            link.symlink_to(SKILL, target_is_directory=True)
            self.write(root / 'docs/issues/20-ready/ONE-0001-demo.md',
                '---\nschema: "implement-rfc.card.v1"\ntitle: "Demo"\ndepends_on: []\nid: "ONE-0001"\nrfcs: []\nstatus: "Ready"\n---\n# Card\n\n## Acceptance\nAC01: works.\n\n## Verification and execution record\nPending.\n')
        self.source = self.base / 'pack'
        self.source.mkdir()
        self.plan = {'schema': 'implement-rfc.milestone-plan.v1', 'id': 'demo',
            'scope': {'issues': ['OLD-0001']}, 'milestones': [
            {'id': 'usable', 'outcome': 'Usable outcome', 'work': [{'issue': 'OLD-0001'}],
             'depends_on': [], 'exit_criteria': ['Public path works'], 'boundary': 'Usable result'}]}
        self.save(self.plan)
        self.write(self.source / 'map.json', json.dumps({'OLD-0001': 'ONE-0001'}))

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def save(self, plan):
        self.write(self.source / 'milestone-plan.json', json.dumps(plan))

    def cli(self, root, operation, *args, code=0):
        result = subprocess.run([sys.executable, '-B', str(root / '.agents/skills/implement-rfc/scripts/milestone_plan.py'),
            operation, '--repo-root', str(root), '--json', *args], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def adopt(self, root):
        return self.cli(root, 'adopt', '--source-root', str(self.source), '--id-map', 'map.json')

    def test_raw_linked_consumers_adoption_resume_and_binding(self):
        other_before = (self.roots[1] / 'docs/issues/20-ready/ONE-0001-demo.md').read_bytes()
        for root in self.roots:
            discovered = self.cli(root, 'discover', '--source-root', str(self.source))
            self.assertEqual(discovered['milestone_ids'], ['usable'])
            self.assertEqual(discovered['semantic_coverage'], 'unknown')
            self.assertFalse((root / 'docs/rfcs/plans').exists())
        adopted = self.adopt(self.roots[0])
        self.assertEqual(other_before, (self.roots[1] / 'docs/issues/20-ready/ONE-0001-demo.md').read_bytes())
        self.assertEqual(adopted, self.adopt(self.roots[0]))
        root = self.roots[0]
        first = self.cli(root, 'bind', '--target', 'ONE-0001')
        self.assertEqual(first['references'], 'resolved')
        old = root / 'docs/issues/20-ready/ONE-0001-demo.md'
        moved = root / 'docs/issues/60-done/ONE-0001-demo.md'
        self.write(moved, old.read_text().replace('Ready', 'Done').replace('Pending.', 'Test passed.'))
        old.unlink()
        second = self.cli(root, 'bind', '--target', 'ONE-0001')
        self.assertEqual(first, second)
        self.write(moved, moved.read_text().replace('works.', 'works differently.'))
        third = self.cli(root, 'bind', '--target', 'ONE-0001')
        self.assertNotEqual(first['obligation_fingerprint'], third['obligation_fingerprint'])
        self.adopt(self.roots[1])

    def test_duplicate_unknown_escape_conflict_and_missing(self):
        self.write(self.source / 'milestone-plan.json', '{"schema":1,"schema":2}')
        self.assertEqual(self.cli(self.roots[0], 'check', '--source-root', str(self.source), code=2)['state'], 'invalid')
        self.save(dict(self.plan, schema='future'))
        self.assertEqual(self.cli(self.roots[0], 'check', '--source-root', str(self.source), code=2)['state'], 'unsupported-version')
        self.save(self.plan)
        self.cli(self.roots[0], 'check', '--source-root', str(self.source), '--plan', '../pack/milestone-plan.json', code=2)
        self.write(self.source / 'PACK_MANIFEST.json', json.dumps({'milestone_plan': 'missing.json'}))
        self.cli(self.roots[0], 'check', '--source-root', str(self.source), code=2)
        self.write(self.source / 'packet-index.json', json.dumps({'milestone_plan': 'different.json'}))
        self.assertEqual(self.cli(self.roots[0], 'discover', '--source-root', str(self.source), code=2)['state'], 'ambiguous')

    def test_collision_and_partial_retry(self):
        self.adopt(self.roots[0])
        card = self.roots[0] / 'docs/issues/20-ready/ONE-0001-demo.md'
        matter = mp.board_model.parse_matter(card.read_bytes(), card)
        card.write_bytes(matter.updated({'metadata': None}))
        self.adopt(self.roots[0])
        self.assertIn('milestone_plan', card.read_text())
        self.plan['milestones'][0]['outcome'] = 'Changed intent'
        self.save(self.plan)
        self.cli(self.roots[0], 'adopt', '--source-root', str(self.source), '--id-map', 'map.json', code=2)

    def test_structural_partial_overlap_cycle_and_ambiguous_criterion(self):
        bad = copy.deepcopy(self.plan)
        bad['milestones'].append(copy.deepcopy(bad['milestones'][0]))
        self.assertTrue(mp.validate_plan(bad))
        bad['milestones'][1]['id'] = 'second'
        bad['milestones'][0]['depends_on'] = ['second']
        bad['milestones'][1]['depends_on'] = ['usable']
        self.assertTrue(any('cycle' in e for e in mp.validate_plan(bad)))
        partial = copy.deepcopy(self.plan)
        partial['coverage'] = 'partial'
        partial['milestones'][0]['work'][0]['criteria'] = ['AC01']
        partial['unplanned_work'] = [{'issue': 'OLD-0001', 'criteria': ['AC02']}]
        self.assertEqual(mp.validate_plan(partial), [])
        partial['unplanned_work'][0]['criteria'] = ['AC01']
        self.assertTrue(mp.validate_plan(partial))
        self.plan['milestones'][0]['work'][0]['criteria'] = ['absent']
        self.save(self.plan)
        self.adopt(self.roots[0])
        self.assertEqual(self.cli(self.roots[0], 'bind', '--target', 'ONE-0001', code=2)['references'], 'unresolved')

    def test_bounds_links_mapping_and_eligible_order(self):
        linked = self.source / 'linked.json'
        linked.symlink_to(self.source / 'milestone-plan.json')
        self.cli(self.roots[0], 'check', '--source-root', str(self.source), '--plan', 'linked.json', code=2)
        self.write(self.source / 'huge.json', ' ' * (1024 * 1024 + 1))
        self.cli(self.roots[0], 'check', '--source-root', str(self.source), '--plan', 'huge.json', code=2)
        typed = copy.deepcopy(self.plan)
        typed['scope'] = {'rfcs': ['RFC-OLD-0001']}
        typed['milestones'][0]['work'] = [{'rfc': 'RFC-OLD-0001', 'criteria': ['RFC-OLD-0001-AC01']}]
        remapped = mp.remap_plan(typed, {'RFC-OLD-0001': 'RFC-NEW-0002'})
        self.assertEqual(remapped['milestones'][0]['work'][0]['criteria'], ['RFC-NEW-0002-AC01'])
        second = copy.deepcopy(self.plan['milestones'][0])
        second.update(id='second', depends_on=['usable'], work=[{'issue': 'OLD-0002'}])
        self.plan['scope']['issues'].append('OLD-0002')
        self.plan['milestones'].insert(0, second)
        self.assertEqual(mp.validate_plan(self.plan), [])
        self.assertEqual(mp.select_milestone(self.plan)['id'], 'usable')
        self.assertEqual(mp.select_milestone(self.plan, ['usable'])['id'], 'second')

    def test_rfc_only_metadata_resume(self):
        self.plan['scope']['rfcs'] = ['RFC-ONE-0001']
        self.save(self.plan)
        root = self.roots[0]
        self.write(root / 'docs/rfcs/RFC-ONE-0001-demo.md',
                   '---\nid: "RFC-ONE-0001"\n---\n## Acceptance\nAC01: usable.\n')
        self.adopt(root)
        self.assertEqual(self.cli(root, 'discover', '--target', 'RFC-ONE-0001')['origin'], 'live')

    def test_future_amendment_does_not_change_active_binding(self):
        root = self.roots[0]
        self.adopt(root)
        first = self.cli(root, 'bind', '--target', 'ONE-0001')
        path = root / first['plan_path']
        live = json.loads(path.read_text())
        live['coverage'] = 'partial'
        live['milestones'][0]['work'][0]['criteria'] = ['AC01']
        live['unplanned_work'] = [{'issue': 'ONE-0001', 'criteria': ['AC02']}]
        path.write_text(json.dumps(live))
        selected = self.cli(root, 'bind', '--target', 'ONE-0001')
        live['unplanned_work'][0]['criteria'] = ['AC03']
        path.write_text(json.dumps(live))
        self.assertEqual(selected, self.cli(root, 'bind', '--target', 'ONE-0001'))
        card = root / 'docs/issues/20-ready/ONE-0001-demo.md'
        card.write_text(card.read_text().replace('AC01: works.', 'AC01: works.\nAC01: ambiguous.'))
        result = self.cli(root, 'bind', '--target', 'ONE-0001', code=2)
        self.assertTrue(any('ambiguous' in d for d in result['diagnostics']))

    def test_generated_view_drift_and_invalid_metadata(self):
        self.write(self.source / 'MILESTONES.md', mp.render(self.plan))
        self.cli(self.roots[0], 'check', '--source-root', str(self.source))
        self.write(self.source / 'MILESTONES.md', mp.render(self.plan) + 'Drift\n')
        result = self.cli(self.roots[0], 'check', '--source-root', str(self.source), code=2)
        self.assertEqual(result['state'], 'stale')
        card = self.roots[0] / 'docs/issues/20-ready/ONE-0001-demo.md'
        card.write_text(card.read_text().replace('rfcs: []', 'rfcs: []\nmetadata: []'))
        result = self.cli(self.roots[0], 'discover', '--target', 'ONE-0001', code=2)
        self.assertIn('metadata must be an object', result['diagnostic'])

    def populate_live_plans(self, root, count=256):
        unrelated = copy.deepcopy(self.plan)
        unrelated['scope'] = {'issues': ['OTHER-0001']}
        unrelated['milestones'][0]['work'] = [{'issue': 'OTHER-0001'}]
        for index in range(count):
            unrelated['id'] = f'unrelated-{index}'
            self.write(root / f'docs/rfcs/plans/unrelated-{index}/milestone-plan.json', json.dumps(unrelated))

    def test_linked_target_resume_above_live_lookup_bound(self):
        for root in self.roots:
            self.adopt(root)
            self.populate_live_plans(root)
            result = self.cli(root, 'discover', '--target', 'ONE-0001')
            self.assertEqual(result['origin'], 'live')
            self.assertEqual(Path(result['path']), root / 'docs/rfcs/plans/demo/milestone-plan.json')
            self.assertEqual(self.cli(root, 'bind', '--target', 'ONE-0001'),
                             self.cli(root, 'bind', '--plan', 'docs/rfcs/plans/demo/milestone-plan.json'))

    def test_unlinked_recovery_keeps_live_lookup_bound(self):
        root = self.roots[0]
        self.adopt(root)
        self.populate_live_plans(root)
        card = root / 'docs/issues/20-ready/ONE-0001-demo.md'
        matter = mp.board_model.parse_matter(card.read_bytes(), card)
        card.write_bytes(matter.updated({'metadata': None}))
        result = self.cli(root, 'discover', '--target', 'ONE-0001', code=2)
        self.assertIn('lookup exceeds 256 plans', result['diagnostic'])
        self.assertEqual(self.cli(root, 'discover', '--plan', 'docs/rfcs/plans/demo/milestone-plan.json')['origin'], 'explicit')

    def test_linked_large_repository_still_rejects_incomplete_adoption(self):
        root = self.roots[0]
        self.plan['scope']['rfcs'] = ['RFC-ONE-0001']
        self.save(self.plan)
        self.write(root / 'docs/rfcs/RFC-ONE-0001-demo.md',
                   '---\nid: "RFC-ONE-0001"\n---\n## Acceptance\nAC01: usable.\n')
        self.adopt(root)
        self.populate_live_plans(root)
        card = root / 'docs/issues/20-ready/ONE-0001-demo.md'
        matter = mp.board_model.parse_matter(card.read_bytes(), card)
        card.write_bytes(matter.updated({'metadata': None}))
        result = self.cli(root, 'discover', '--target', 'RFC-ONE-0001', code=2)
        self.assertEqual(result['state'], 'stale')
        self.assertIn('missing linkage', result['diagnostic'])

    def test_interrupted_adoption_target_only_resume_refuses_until_retry(self):
        self.plan['scope']['rfcs'] = ['RFC-ONE-0001']
        self.save(self.plan)
        for root, failure in zip(self.roots, (3, 4)):
            self.write(root / 'docs/rfcs/RFC-ONE-0001-demo.md',
                       '---\nid: "RFC-ONE-0001"\n---\n## Acceptance\nAC01: usable.\n')
            script = '''import sys
sys.path.insert(0, sys.argv.pop(1))
import milestone_plan as mp
original = mp.os.replace
calls = 0
failure = int(sys.argv.pop(1))
def replace(source, destination):
    global calls
    calls += 1
    if calls == failure:
        raise OSError('injected metadata publication failure')
    return original(source, destination)
mp.os.replace = replace
sys.exit(mp.main())
'''
            result = subprocess.run([sys.executable, '-B', '-c', script,
                str(root / '.agents/skills/implement-rfc/scripts'), str(failure), 'adopt',
                '--repo-root', str(root), '--source-root', str(self.source), '--id-map', 'map.json', '--json'],
                cwd=self.base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            receipt = root / 'docs/rfcs/plans/demo/source.json'
            before = receipt.read_bytes()
            for target in ('ONE-0001', 'RFC-ONE-0001'):
                result = self.cli(root, 'discover', '--target', target, code=2)
                self.assertEqual(result['state'], 'stale')
                self.assertIn('original --source-root', result['diagnostic'])
            self.cli(root, 'bind', '--plan', 'docs/rfcs/plans/demo/milestone-plan.json', code=2)
            self.adopt(root)
            self.assertEqual(receipt.read_bytes(), before)
            self.assertEqual(self.cli(root, 'bind', '--target', 'RFC-ONE-0001')['references'], 'resolved')


if __name__ == '__main__':
    unittest.main()
