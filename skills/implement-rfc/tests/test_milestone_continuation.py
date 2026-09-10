import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from coordinator_handoff import continuation, IDENTITY
"""Candidate continuation cases, integrated after prerequisite acceptance."""
import copy
import unittest

class BoundReturnTests(unittest.TestCase):
    def setUp(self):
        self.binding = dict(plan_id='demo', plan_path='docs/rfcs/plans/demo/milestone-plan.json',
            milestone_id='first', definition_fingerprint='sha256:'+'a'*64, obligation_fingerprint='sha256:'+'b'*64,
            prerequisite_fingerprint='sha256:'+'c'*64, obligations=[{'id':key,'source':key,'selector':None,'source_fingerprint':'sha256:'+'d'*64} for key in ('card-a','card-b')],
            structural='valid',references='resolved',semantic_coverage='unknown',diagnostics=[],diagnostics_truncated=False,
            exit_criteria=[{'id':'exit:1','text':'Composed public path works'}])
        self.reply = dict(schema='implement-rfc.milestone-return.v2', run_id='run',
            dispatch_id='one', producer_id='native-one', mandate_revision='1', milestone='first',
            disposition='milestone-complete', summary='composed result', candidate_revision='a'*40,
            handoff_ref='docs/closeout.md', ownership='quiescent', next_objective='second',
            required_pending=[], evidence_refs=['docs/evidence.md'], binding=self.binding,
            acceptance_records=[{'id':key,'outcome':'pass','evidence_refs':['docs/evidence.md']}
                for key in ('card-a','card-b','exit:1')],
            continuation={'intent':'fresh','next_milestone':'second','reason':'integrated-boundary',
                          'detail':'First public composition accepted; next outcome is independent design.'})
        self.assignment={key:self.reply[key] for key in IDENTITY}
        self.assignment['binding']=copy.deepcopy(self.binding)
        self.assignment.update(schema='implement-rfc.milestone-assignment.v1',consumer_root='/fixture',
                               branch='main',target_milestones=['first','second'])

    def action(self, reply=None, **kwargs):
        return continuation(reply or self.reply, self.assignment, execution='quiescent',
                            current_binding=self.binding, **kwargs)['action']

    def test_intermediate_card_and_missing_exit_refuse_complete(self):
        for records in (self.reply['acceptance_records'][:1], self.reply['acceptance_records'][:2]):
            self.assertEqual(self.action(dict(self.reply,acceptance_records=records)), 'clarify')

    def test_boundary_and_related_reuse_are_separate_from_completion(self):
        self.assertEqual(self.action(), 'fresh-integrator')
        reuse=copy.deepcopy(self.reply)
        reuse['continuation'].update(intent='continue',reason='related-continuation',
                                     detail='Small next output uses the same loaded interface.')
        self.assertEqual(self.action(reuse),'resume-integrator')

    def test_partial_resume_and_recovery_preserve_obligations(self):
        partial=copy.deepcopy(self.reply)
        partial.update(disposition='continue-milestone',acceptance_records=[],required_pending=['card-b'])
        partial['continuation'].update(intent='continue',next_milestone='first',reason='current-milestone')
        self.assertEqual(self.action(partial),'resume-integrator')
        partial['continuation'].update(intent='fresh',reason='producer-unavailable',detail='Native producer cannot resume.')
        self.assertEqual(self.action(partial),'fresh-integrator')
        partial['continuation']['next_milestone']='second'
        self.assertEqual(self.action(partial),'reconcile')

    def test_pending_records_and_self_reduced_binding_cannot_complete(self):
        pending=copy.deepcopy(self.reply)
        pending['acceptance_records'][0]['outcome']='pending'
        self.assertEqual(self.action(pending),'clarify')
        reduced=copy.deepcopy(self.reply)
        reduced['binding']['obligations'].pop()
        reduced['acceptance_records'].pop(1)
        self.assertEqual(self.action(reduced),'ignore-stale')

    def test_legacy_reply_cannot_bypass_plan_binding(self):
        legacy={key:value for key,value in self.reply.items()
                if key not in ('binding','acceptance_records','continuation')}
        legacy['schema']='implement-rfc.milestone-return.v1'
        self.assertEqual(self.action(legacy),'reconcile')

    def test_current_observation_and_affected_requirements(self):
        self.assertEqual(continuation(self.reply,self.assignment,execution='quiescent')['action'],'reconcile')
        changed=copy.deepcopy(self.binding);changed['obligation_fingerprint']='d'*64
        self.assertEqual(continuation(self.reply,self.assignment,execution='quiescent',current_binding=changed)['action'],'reconcile')

    def test_identity_duplicate_and_native_execution_guards(self):
        accepted=continuation(self.reply,self.assignment,execution='quiescent',current_binding=self.binding)
        self.assertEqual(self.action(consumed=[accepted['consume_key']]),'ignore-duplicate')
        for execution,action in [('active','wait'),('unknown','reconcile')]:
            self.assertEqual(continuation(self.reply,self.assignment,execution=execution,current_binding=self.binding)['action'],action)
        stale=dict(self.reply,dispatch_id='old')
        self.assertEqual(self.action(stale),'ignore-stale')

    def test_same_native_resume_renews_dispatch_and_partial_selector_can_finish(self):
        self.reply['dispatch_id']='two'; self.assignment['dispatch_id']='two'
        self.reply['binding']['obligations'][0]['selector']='AC01'
        self.assignment['binding']=copy.deepcopy(self.reply['binding'])
        self.assertEqual(self.action(),'fresh-integrator')
        self.assertEqual(self.reply['producer_id'],'native-one')
        self.assertEqual(self.action(consumed=[('run','one','native-one','1','first')]),'fresh-integrator')

    def test_pending_cancel_and_review_relay_remain_explicit(self):
        pending=copy.deepcopy(self.reply)
        pending.update(disposition='human-pending',required_pending=['native evidence'])
        pending['continuation'].update(intent='wait',reason='pending-obligation')
        self.assertEqual(self.action(pending),'pending')
        self.assertEqual(self.action(cancelled=True),'stop')
        review=copy.deepcopy(self.reply)
        review.update(disposition='review-request',review_request={'role':'rfc-reviewer','candidate_ref':'a'*40,'assignment':'Check the bounded candidate'})
        review['continuation'].update(intent='wait',reason='pending-obligation')
        self.assertEqual(self.action(review),'clarify')
        self.assertEqual(self.action(review,review_relay=True),'relay-review')

    def test_closed_binding_and_card_only_replacement_refuse(self):
        for key,value in [('invented',True),('references','unresolved'),('diagnostics_truncated',True)]:
            malformed=copy.deepcopy(self.reply); malformed['binding'][key]=value
            self.assertEqual(self.action(malformed),'clarify')
        bad=copy.deepcopy(self.reply);bad['continuation']['reason']='card-done'
        self.assertEqual(self.action(bad),'clarify')
        self.assertEqual(self.action(consumed={'invented':True}),'reconcile')
        self.assertEqual(self.action(accepted_milestones={'second':True}),'reconcile')
        self.assignment['unexpected']=True
        self.assertEqual(self.action(),'reconcile')
