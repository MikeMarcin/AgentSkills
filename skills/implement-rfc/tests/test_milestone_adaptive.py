"""Adaptive preparation starts with raw inputs through installed helper links."""
import copy
import json
import unittest
import test_milestone_plan as fixtures
import test_milestone_adaptive_public as public


class AdaptiveTests(unittest.TestCase):
    setUp = fixtures.PlanTests.setUp
    write = fixtures.PlanTests.write
    save = fixtures.PlanTests.save
    cli = fixtures.PlanTests.cli
    adopt = fixtures.PlanTests.adopt
    handoff = public.AdaptivePublicTests.handoff

    def test_legacy_normalization_adoption_and_target_only_resume(self):
        (self.source / 'milestone-plan.json').unlink()
        legacy = '# Stage: usable\nDeliver the public path as one outcome.\n'
        self.write(self.source / 'MILESTONES.md', legacy)
        proposal = copy.deepcopy(self.plan)
        proposal['scope']['issues'] = ['ONE-0001']
        proposal['milestones'][0]['work'] = [{'issue': 'ONE-0001'}]
        self.write(self.source / 'proposal.json', json.dumps(proposal))
        for root in self.roots:
            prepared = self.cli(root, 'prepare', '--source-root', str(self.source),
                '--proposal', 'proposal.json', '--target', 'ONE-0001')
            self.assertEqual(prepared['origin'], 'needs-normalization')
            receipt = root / 'docs/rfcs/plans/demo/preparation.json'
            self.write(receipt, json.dumps(prepared))
            adopted = self.cli(root, 'adopt', '--source-root', str(self.source), '--plan', 'proposal.json')
            original_receipt = (root / 'docs/rfcs/plans/demo/source.json').read_bytes()
            for dispatch in ('initial', 'resumed'):
                assignment = self.handoff(root, 'assign', '--target', 'ONE-0001',
                    '--run-id', root.name, '--dispatch-id', dispatch, '--producer-id', 'same-engineer',
                    '--mandate-revision', '1')
                self.assertEqual(assignment['binding']['plan_path'], adopted['plan_path'])
                self.assertEqual(assignment['binding']['milestone_id'], 'usable')
                if dispatch == 'initial':
                    first_binding = assignment['binding']
                else:
                    self.assertEqual(first_binding, assignment['binding'])
            # Even an attached original source cannot supersede target-only live linkage.
            discovered = self.cli(root, 'discover', '--target', 'ONE-0001', '--source-root', str(self.source))
            self.assertEqual(discovered['origin'], 'live')
            self.assertEqual(json.loads(receipt.read_text())['source_evidence']['text'], legacy)
            self.assertEqual(original_receipt, (root / 'docs/rfcs/plans/demo/source.json').read_bytes())
        self.assertEqual((self.source / 'MILESTONES.md').read_text(), legacy)

    def test_planless_rfc_and_loose_issues_with_disjoint_large_card(self):
        (self.source / 'milestone-plan.json').unlink()
        for root in self.roots:
            proposal = copy.deepcopy(self.plan)
            if root == self.roots[0]:
                target = 'RFC-ONE-0001'
                self.write(root / 'docs/rfcs/RFC-ONE-0001-demo.md',
                    '---\nid: "RFC-ONE-0001"\n---\n## Acceptance\nAC01: public path works.\n')
                proposal['scope'] = {'rfcs': [target]}
                proposal['milestones'][0]['work'] = [{'rfc': target, 'criteria': ['AC01']}]
                expected = [target + ':AC01']
            else:
                target = 'ONE-0001'
                card = root / 'docs/issues/20-ready/ONE-0001-demo.md'
                self.write(card, card.read_text().replace('AC01: works.', 'AC01: works.\nAC02: integration reviewed.'))
                self.write(root / 'docs/issues/20-ready/ONE-0002-demo.md', card.read_text().replace('ONE-0001', 'ONE-0002'))
                proposal['scope'] = {'issues': ['ONE-0001', 'ONE-0002']}
                proposal['milestones'][0]['work'] = [
                    {'issue': 'ONE-0001', 'criteria': ['AC01']}, {'issue': 'ONE-0002'}]
                later = copy.deepcopy(proposal['milestones'][0])
                later.update(id='integration', depends_on=['usable'],
                    work=[{'issue': 'ONE-0001', 'criteria': ['AC02']}])
                proposal['milestones'].append(later)
                expected = ['ONE-0001:AC01', 'ONE-0002:*']
            self.write(self.source / 'proposal.json', json.dumps(proposal))
            targets = [item for identity in proposal['scope'].get('issues', [target]) for item in ('--target', identity)]
            prepared = self.cli(root, 'prepare', '--source-root', str(self.source), '--proposal', 'proposal.json', *targets)
            self.assertEqual(prepared['origin'], 'absent')
            self.cli(root, 'adopt', '--source-root', str(self.source), '--plan', 'proposal.json')
            bound = self.cli(root, 'bind', '--target', target)
            self.assertEqual(bound['references'], 'resolved')
            self.assertEqual([o['id'] for o in bound['obligations']], expected)
            if root == self.roots[1]:
                later = self.cli(root, 'bind', '--target', target, '--milestone', 'integration')
                self.assertEqual([o['id'] for o in later['obligations']], ['ONE-0001:AC02'])
                self.assertIn('status: "Ready"', card.read_text())
                self.assertEqual(list((root / 'docs/rfcs').glob('RFC-*.md')), [])

    def test_legacy_and_planless_preparation_retains_evidence(self):
        proposal = copy.deepcopy(self.plan)
        proposal['scope']['issues'] = ['ONE-0001']
        proposal['milestones'][0]['work'] = [{'issue': 'ONE-0001'}]
        (self.source / 'milestone-plan.json').unlink()
        self.write(self.source / 'proposal.json', json.dumps(proposal))
        for root in self.roots:
            prepared = self.cli(root, 'prepare', '--source-root', str(self.source),
                '--proposal', 'proposal.json', '--target', 'ONE-0001')
            self.assertEqual(prepared['origin'], 'absent')
            self.assertEqual(prepared['plan'], dict(proposal, coverage='complete', unplanned_work=[]))
            self.assertFalse((root / 'docs/rfcs/plans').exists())
        legacy = '# Stage one\nDeliver a usable outcome, then review the public path.\n'
        self.write(self.source / 'MILESTONES.md', legacy)
        result = self.cli(self.roots[0], 'prepare', '--source-root', str(self.source), '--proposal', 'proposal.json')
        self.assertEqual(result['source_evidence']['text'], legacy)
        self.assertEqual(result['origin'], 'needs-normalization')
        self.write(self.source / 'milestone-plan.json', '{bad')
        self.cli(self.roots[0], 'prepare', '--source-root', str(self.source), '--proposal', 'proposal.json', code=2)

    def test_projection_and_pending_dependency_observations(self):
        root = self.roots[0]
        self.adopt(root)
        card = root / 'docs/issues/20-ready/ONE-0001-demo.md'
        self.write(card, card.read_text().replace('depends_on: []', 'depends_on: ["ONE-0002"]'))
        self.write(root / 'docs/issues/50-blocked/ONE-0002-dependency.md',
            '---\nid: "ONE-0002"\nstatus: "Blocked"\ndepends_on: ["ONE-0003"]\n---\nPending human review.\n')
        self.write(root / 'selection.json', json.dumps([{'issue': 'ONE-0001', 'criteria': ['AC01']}]))
        result = self.cli(root, 'inspect', '--target', 'ONE-0001', '--projection', 'selection.json')
        self.assertEqual([o['id'] for o in result['obligations']], ['ONE-0001:AC01'])
        self.assertEqual(result['references'], 'resolved')
        self.assertEqual(result['exit_criteria'][0]['text'], 'Public path works')
        self.assertEqual(result['planning']['issues'][0]['excluded_prerequisites'], ['ONE-0002'])
        self.assertEqual(result['planning']['issues'][1]['status'], 'Blocked')
        self.assertEqual(result['planning']['issues'][2]['status'], 'unknown')
        self.write(root / 'selection.json', json.dumps([{'issue': 'ONE-0001'}]))
        whole_current = self.cli(root, 'bind', '--target', 'ONE-0001', '--projection', 'selection.json')
        self.assertEqual(whole_current['projection'], [{'issue': 'ONE-0001'}])
        for selection in ([], [{'issue': 'ONE-9999'}], [{'issue': 'ONE-0001'}, {'issue': 'ONE-0001'}]):
            self.write(root / 'selection.json', json.dumps(selection))
            self.cli(root, 'bind', '--target', 'ONE-0001', '--projection', 'selection.json', code=2)

    def test_partial_amendment_preserves_pending_work_and_exits(self):
        self.plan['coverage'] = 'partial'
        self.plan['milestones'][0]['work'][0]['criteria'] = ['AC01']
        self.plan['unplanned_work'] = [{'issue': 'OLD-0001', 'criteria': ['AC02']}]
        self.save(self.plan)
        proposed = copy.deepcopy(self.plan)
        proposed['coverage'] = 'complete'
        proposed['unplanned_work'] = []
        later = copy.deepcopy(proposed['milestones'][0])
        later.update(id='review', work=[{'issue': 'OLD-0001', 'criteria': ['AC02']}],
                     depends_on=['usable'], exit_criteria=['Human decision accepted'])
        proposed['milestones'].append(later)
        self.write(self.source / 'proposal.json', json.dumps(proposed))
        args = ('--source-root', str(self.source), '--proposal', 'proposal.json',
                '--reason', 'Refine review remainder', '--source-basis', 'Existing AC02')
        result = self.cli(self.roots[0], 'check-amendment', *args)
        self.assertEqual(result['affected_milestones'], ['review'])
        self.cli(self.roots[0], 'check-amendment', *args[:-4], code=2)
        proposed['milestones'][1]['work'][0]['criteria'] = ['AC03']
        self.write(self.source / 'proposal.json', json.dumps(proposed))
        self.cli(self.roots[0], 'check-amendment', *args, code=2)
        proposed['milestones'][1]['work'][0]['criteria'] = ['AC02']
        proposed['milestones'][0]['exit_criteria'] = ['Weaker substitute']
        self.write(self.source / 'proposal.json', json.dumps(proposed))
        self.cli(self.roots[0], 'check-amendment', *args, code=2)


if __name__ == '__main__':
    unittest.main()
