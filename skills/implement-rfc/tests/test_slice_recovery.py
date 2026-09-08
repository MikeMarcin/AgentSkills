"""Fake-driver delivery schedules; no live sessions, accounts or model requests."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from slice_runtime import Runtime
from slice_events import usage_projection


class Driver:
    def __init__(self):self.launches=0;self.recoveries=0;self.crash=False;self.support=True
    def capabilities(self):return {'launch':True,'read_only_report_resume':self.support}
    def validate(self,packet):pass
    def launch(self,packet,attempt_id):
        self.launches+=1
        if self.crash:raise RuntimeError('crash after effect')
        return {'driver_session_id':attempt_id,'driver_turn_id':'turn'}
    def cancel(self,receipt):return True
    def inspect_attempt(self,receipt):return {'owned':True,'model_requests':0}
    def recover_report(self,receipt,budget_seconds):
        self.recoveries+=1
        return {'driver_session_id':receipt['driver_session_id'],'report':'Existing findings only'}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='rfc-recovery-');self.addCleanup(self.tmp.cleanup)
        self.driver=Driver();self.runtime=Runtime(Path(self.tmp.name),self.driver,'run')
    def event(self,task,kind,**data):return {'kind':kind,'event_id':task+'-'+kind,'driver_session_id':task+'-1','driver_turn_id':'turn',**data}
    def test_crash_intent_never_relaunches(self):
        self.driver.crash=True
        with self.assertRaises(RuntimeError):self.runtime.dispatch('task',{})
        with self.assertRaises(ValueError):self.runtime.dispatch('task',{})
        self.assertEqual(self.driver.launches,1)
        self.assertFalse(self.runtime.inspect('task-1')['automatic_relaunch'])
    def test_both_child_report_schedules_survive_scout_limit(self):
        for i,before in enumerate((True,False)):
            scout='scout'+str(i);child='utility'+str(i)
            self.runtime.dispatch(scout,{},recovery_budget=10);self.runtime.dispatch(child,{})
            complete=lambda:self.runtime.consume(child+'-1',[self.event(child,'completed',report='Useful findings')])
            if before:complete()
            self.runtime.consume(scout+'-1',[self.event(scout,'max_turns')])
            if not before:complete()
            self.runtime.recover_report(scout+'-1')
            self.assertTrue((Path(self.tmp.name)/(child+'-1.report.txt')).is_file())
            self.assertTrue((Path(self.tmp.name)/(scout+'-1.recovery-report.txt')).is_file())
        self.assertEqual(self.driver.recoveries,2)
    def test_one_recovery_and_no_cancelled_recovery(self):
        self.runtime.dispatch('task',{},recovery_budget=10)
        self.runtime.consume('task-1',[self.event('task','max_turns')])
        self.runtime.recover_report('task-1')
        with self.assertRaises(ValueError):self.runtime.recover_report('task-1')
        self.runtime.dispatch('cancel',{},recovery_budget=10)
        self.runtime.consume('cancel-1',[self.event('cancel','max_turns')])
        self.runtime.cancel('cancel-1')
        with self.assertRaises(ValueError):self.runtime.recover_report('cancel-1')
        self.assertEqual(self.driver.recoveries,1)
    def test_idle_and_duplicate_completion_have_no_model_polling(self):
        self.runtime.dispatch('task',{})
        event=self.event('task','completed',report='report')
        self.runtime.consume('task-1',[{'kind':'idle'}]*1000+[event]*1000)
        records=self.runtime.records('task-1')
        self.assertEqual(sum(r['event']=='collected' for r in records),1)
        self.assertEqual(self.driver.launches,1);self.assertEqual(self.driver.recoveries,0)
    def test_wrong_session_rejected_and_partial_preserved(self):
        self.runtime.dispatch('task',{})
        self.runtime.consume('task-1',[self.event('task','partial',text='partial')])
        event=self.event('task','completed',report='report');event['driver_turn_id']='wrong'
        with self.assertRaises(ValueError):self.runtime.consume('task-1',[event])
        self.assertEqual(len(list(Path(self.tmp.name).glob('*.partial-*.txt'))),1)
    def test_unsupported_resume_blocks(self):
        self.driver.support=False;self.runtime.dispatch('task',{},recovery_budget=10)
        self.runtime.consume('task-1',[self.event('task','max_turns')])
        self.assertEqual(self.runtime.recover_report('task-1')['event'],'blocked')
        self.assertEqual(self.driver.recoveries,0)
    def test_lock_exclusion_and_privacy_projection(self):
        self.runtime.dispatch('task',{})
        with self.runtime.store.writer():
            with self.assertRaises(OSError):
                with self.runtime.store.writer():pass
        projected=list(usage_projection(self.runtime.store.read()[0]))
        self.assertNotIn('driver_session_id": "task',str(projected))
        self.assertTrue(projected)
    def test_torn_tail_refuses_mutation(self):
        self.runtime.dispatch('task',{})
        with self.runtime.store.path.open('ab') as stream:stream.write(b'{')
        self.assertEqual(self.runtime.store.read()[1],'torn_final_event')
        with self.assertRaises(ValueError):self.runtime.dispatch('other',{})

    def test_report_and_completion_are_distinct_in_either_order(self):
        for task,kinds in [('early',('report','completed')),('late',('completed','report'))]:
            self.runtime.dispatch(task,{})
            self.runtime.consume(task+'-1',[self.event(task,kinds[0],text='findings')])
            self.assertFalse(any(r['event']=='awaiting_integration' for r in self.runtime.records(task+'-1')))
            self.runtime.consume(task+'-1',[self.event(task,kinds[1],text='findings')])
            self.assertTrue(any(r['event']=='awaiting_integration' for r in self.runtime.records(task+'-1')))
            self.assertEqual(sum(r['event']=='execution_completed' for r in self.runtime.records(task+'-1')),1)


if __name__=='__main__':unittest.main()
