"""Adaptive projections and pending transitions through installed public commands."""
import copy
import json
import subprocess
import sys
import unittest

import test_milestone_plan as fixtures


class AdaptivePublicTests(unittest.TestCase):
    setUp = fixtures.PlanTests.setUp
    write = fixtures.PlanTests.write
    save = fixtures.PlanTests.save
    cli = fixtures.PlanTests.cli
    adopt = fixtures.PlanTests.adopt

    def handoff(self, root, operation, *args, code=0):
        run = subprocess.run([sys.executable, '-B', str(root / '.agents/skills/implement-rfc/scripts/coordinator_handoff.py'),
            operation, '--repo-root', str(root), '--json', *args], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        return json.loads(run.stdout)

    def assign(self, root, *args):
        return self.handoff(root, 'assign', '--target', 'ONE-0001', '--run-id', 'adaptive',
            '--dispatch-id', 'one', '--producer-id', 'native-one', '--mandate-revision', '1', *args)

    def reply(self, assignment):
        reply = {key: assignment[key] for key in ('run_id','dispatch_id','producer_id','mandate_revision','milestone')}
        reply.update(schema='implement-rfc.milestone-return.v2', disposition='milestone-complete',
            summary='Selected public path accepted', candidate_revision='a'*40,
            handoff_ref='evidence.md', ownership='quiescent', next_objective=None,
            required_pending=[], evidence_refs=['evidence.md'], binding=assignment['binding'],
            acceptance_records=[dict(id=item['id'],outcome='pass',evidence_refs=['evidence.md'])
                for field in ('obligations','exit_criteria') for item in assignment['binding'][field]],
            continuation=dict(intent='stop',next_milestone=None,reason='target-complete',detail='Explicit subset satisfied; parent acceptance remains open.'))
        return reply

    def check(self, root, assignment, reply, code=0, accepted=()):
        self.write(root/'assignment.json', json.dumps(assignment))
        self.write(root/'return.json', json.dumps(reply))
        return self.handoff(root, 'check', '--assignment', 'assignment.json', '--return-file', 'return.json',
                            '--execution', 'quiescent',
                            *[arg for mid in accepted for arg in ('--accepted-milestone', mid)], code=code)

    def test_partial_card_subset_remains_open_and_cannot_close_parent(self):
        source_bytes=(self.source/'milestone-plan.json').read_bytes()
        for root in self.roots:
            card=root/'docs/issues/20-ready/ONE-0001-demo.md'
            self.write(card,card.read_text().replace('AC01: works.', 'AC01: works.\nAC02: later behavior.'))
            self.adopt(root)
            self.write(root/'projection.json',json.dumps([{'issue':'ONE-0001','criteria':['AC01']}]))
            assignment=self.assign(root,'--projection','projection.json')
            self.assertEqual([o['id'] for o in assignment['binding']['obligations']],['ONE-0001:AC01'])
            reply=self.reply(assignment)
            self.assertEqual(self.check(root,assignment,reply)['action'],'stop')
            self.assertIn('status: "Ready"',card.read_text())
            reply['disposition']='pack-complete'
            self.assertEqual(self.check(root,assignment,reply,code=2)['action'],'clarify')
            reply=self.reply(assignment)
            reply.update(disposition='continue-milestone',acceptance_records=[],required_pending=['Public check'])
            reply['continuation'].update(intent='fresh',next_milestone='usable',reason='producer-unavailable',detail='Native context unavailable; preserve current obligations.')
            self.assertEqual(self.check(root,assignment,reply)['action'],'fresh-integrator')
            renewed=copy.deepcopy(assignment);renewed['dispatch_id']='two'
            self.assertEqual(self.check(root,renewed,reply)['action'],'ignore-stale')
            reply['dispatch_id']='two'
            self.assertEqual(self.check(root,renewed,reply)['action'],'fresh-integrator')
        self.assertEqual(source_bytes,(self.source/'milestone-plan.json').read_bytes())

    def test_pending_independent_outcome_preserves_missing_native_obligation(self):
        root=self.roots[0]
        self.write(root/'docs/issues/20-ready/ONE-0002-demo.md',
            (root/'docs/issues/20-ready/ONE-0001-demo.md').read_text().replace('ONE-0001','ONE-0002'))
        self.plan['scope']['issues'].append('ONE-0002')
        second=copy.deepcopy(self.plan['milestones'][0])
        second.update(id='independent',work=[{'issue':'ONE-0002'}])
        self.plan['milestones'].append(second);self.save(self.plan)
        self.adopt(root)
        assignment=self.assign(root);reply=self.reply(assignment)
        reply.update(disposition='human-pending',required_pending=['Actual native course'],acceptance_records=[],next_objective='Independent outcome')
        reply['continuation'].update(intent='fresh',next_milestone='independent',reason='independent-work',detail='Native course remains on evidence.md; independent outcome is authorized.')
        self.assertEqual(self.check(root,assignment,reply)['action'],'fresh-integrator')
        second_card=root/'docs/issues/20-ready/ONE-0002-demo.md'
        original=second_card.read_text()
        self.write(second_card,original.replace('depends_on: []','depends_on: ["ONE-0001"]'))
        self.assertEqual(self.check(root,assignment,reply,code=2)['action'],'reconcile')
        self.write(second_card,original)
        path=root/assignment['binding']['plan_path'];plan=json.loads(path.read_text())
        plan['milestones'][1]['depends_on']=['usable'];self.write(path,json.dumps(plan))
        self.assertEqual(self.check(root,assignment,reply,code=2)['action'],'reconcile')
        self.write(root/'projection.json',json.dumps([{'issue':'ONE-0002','criteria':['AC01']}]))
        projected=self.assign(root,'--milestone','independent','--accepted-milestone','usable',
                              '--projection','projection.json')
        progress=self.reply(projected)
        progress.update(disposition='continue-milestone',acceptance_records=[],required_pending=['Current evidence'])
        progress['continuation'].update(intent='continue',next_milestone='independent',reason='current-milestone')
        self.assertEqual(self.check(root,projected,progress,accepted=['usable'])['action'],'resume-integrator')
        self.assertEqual(self.check(root,projected,[],code=2)['action'],'clarify')

    def test_unplanned_remainder_prevents_pack_closeout(self):
        root=self.roots[0]
        card=root/'docs/issues/20-ready/ONE-0001-demo.md'
        self.write(card,card.read_text().replace('AC01: works.', 'AC01: works.\nAC02: later behavior.'))
        self.plan.update(coverage='partial',unplanned_work=[{'issue':'OLD-0001','criteria':['AC02']}])
        self.plan['milestones'][0]['work'][0]['criteria']=['AC01'];self.save(self.plan)
        self.adopt(root)
        assignment=self.assign(root);reply=self.reply(assignment)
        reply['disposition']='pack-complete'
        result=self.check(root,assignment,reply,code=2)
        self.assertEqual(result['action'],'reconcile')
        self.assertIn('unplanned work',result['reason'])


if __name__ == '__main__':
    unittest.main()
