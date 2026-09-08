"""Qualification regressions and selected public admission without model calls."""
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch
import test_slice_commands as commands
import test_slice_recovery as recovery
Driver = recovery.Driver
from test_slice_codex import RpcFixture
import slice_model as model
import run_slice as runner
from slice_runtime import Runtime
from slice_codex import CodexDriver


class AdmissionTests(unittest.TestCase):
    setUp = commands.CommandTests.setUp
    execute = commands.CommandTests.execute
    def test_owned_executable_remains_frozen(self):
        self.order['tasks'][0]['owned_paths'] = ['check.py']
        del self.order['input_hashes']['check.py']
        with self.assertRaisesRegex(ValueError,'frozen hash'):
            model.validate(self.order)
        self.assertFalse((self.root/'.mask/generated').exists())

    def agent_order(self):
        task = self.order['tasks'][0]
        task.pop('argv'); task.pop('predicate'); task['kind']='agent'
        task['route']={'provider':'claude','role':'rfc-scout','profile':'baseline',
                       'model':'sonnet','effort':'high','permission_policy':'read-only-leaf'}
        task['task_packet']='packet.json'
        packet={'cwd':str(self.root),'prompt':'Read the assigned file and report established facts.',
                'model':'sonnet','effort':'high','tools':['Read'],'max_turns':1,'timeout_seconds':2}
        (self.root/'packet.json').write_text(json.dumps(packet))
        self.order['input_hashes']['packet.json']=model.file_hash(self.root/'packet.json')
        policy=self.root/'permission.json'
        data=json.loads(policy.read_text());data['allowed_agents']=[task['route']]
        policy.write_text(json.dumps(data))
        self.order['input_hashes']['permission.json']=model.file_hash(policy)
        self.order['max_agent_dispatches']=1
        return task

    def test_public_agent_admission_and_durable_gate(self):
        task=self.agent_order()
        order=self.root/'order.json';order.write_text(json.dumps(self.order))
        result=subprocess.run([sys.executable,'-B',runner.__file__,'validate','--order',str(order)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(json.loads(result.stdout)['execution_authorized'])
        class Companion(Driver):
            def events(self,receipt):
                yield {**receipt,'kind':'completed','event_id':'result','report':'Established fact'}
            def close(self):pass
        driver=Companion()
        with patch.object(runner,'native_driver',return_value=driver):
            result=self.execute()
        self.assertEqual(result['tasks']['gate']['event'],'awaiting_integration')
        self.assertEqual(driver.launches,1)
        report=runner.run_path(self.root,'fixture')/'check-1.report.txt'
        self.assertEqual(report.read_text(),'Established fact')
        self.assertEqual(result['semantic_acceptance'],'not_decided_by_runner')

    def test_agent_budget_packet_and_permissions_refuse(self):
        task=self.agent_order()
        self.order['max_agent_dispatches']=0
        with self.assertRaisesRegex(ValueError,'dispatch budget'):model.validate(self.order)
        self.order['max_agent_dispatches']=1
        task['route']['permission_policy']='workspace-write'
        with self.assertRaisesRegex(ValueError,'read-only'):model.validate(self.order)

    def test_agent_cancel_during_idle_wait(self):
        self.agent_order()
        path=runner.run_path(self.root,'fixture')
        class Companion(Driver):
            def events(self,receipt):
                (path/'cancel.request').touch()
                yield {'kind':'idle'}
            def close(self):pass
        with patch.object(runner,'native_driver',return_value=Companion()):
            result=self.execute()
        self.assertEqual(result['tasks']['check']['event'],'cancelled')
        self.assertNotIn('gate',result['tasks'])


class DeliveryRegressionTests(unittest.TestCase):
    setUp = recovery.RecoveryTests.setUp
    event = recovery.RecoveryTests.event
    def test_crash_before_report_replays_completed_event(self):
        self.runtime.dispatch('task',{})
        event=self.event('task','completed',report='retained report')
        with patch.object(self.runtime,'save_report',side_effect=OSError('injected crash')):
            with self.assertRaises(OSError):self.runtime.consume('task-1',[event])
        self.runtime.consume('task-1',[event])
        records=self.runtime.records('task-1')
        self.assertEqual(sum(r['event']=='execution_completed' for r in records),1)
        self.assertEqual(sum(r['event']=='collected' for r in records),1)
        self.assertEqual((Path(self.tmp.name)/'task-1.report.txt').read_text(),'retained report')

    def test_cancel_acquires_lock_while_stream_waits(self):
        self.runtime.dispatch('task',{})
        waiting=threading.Event();release=threading.Event();errors=[]
        def events():
            waiting.set();release.wait(3)
            yield self.event('task','completed',report='after cancel')
        def consume():
            try:self.runtime.consume('task-1',events())
            except Exception as error:errors.append(error)
        thread=threading.Thread(target=consume);thread.start()
        self.assertTrue(waiting.wait(2))
        try:self.assertEqual(self.runtime.cancel('task-1')['event'],'cancelled')
        finally:release.set();thread.join(3)
        self.assertFalse(errors)
        self.assertFalse((Path(self.tmp.name)/'task-1.report.txt').exists())

    def test_native_identity_survives_failed_dispatch_receipt(self):
        rpc=RpcFixture();driver=CodexDriver(rpc=rpc,capabilities={'launch':True})
        runtime=Runtime(Path(self.tmp.name)/'native',driver,'native')
        packet={'cwd':str(Path(self.tmp.name)),'prompt':'bounded','model':'explicit','effort':'high',
                'sandbox':'read-only','approval_policy':'never','timeout_seconds':2}
        original=runtime.append
        def append(event,*args,**kwargs):
            if event=='dispatched':raise OSError('receipt write crash')
            return original(event,*args,**kwargs)
        with patch.object(runtime,'append',side_effect=append):
            with self.assertRaises(OSError):runtime.dispatch('task',packet)
        self.assertEqual(runtime.receipt('task-1')['driver_turn_id'],'owned-turn')
        self.assertEqual(runtime.cancel('task-1')['event'],'cancelled')
        self.assertEqual(rpc.calls[-1][0],'turn/interrupt')

class RuntimeCaptureTests(unittest.TestCase):
    def test_selected_journals_exclude_report_text_and_preserve_coverage(self):
        import tempfile
        from datetime import datetime, timezone
        from types import SimpleNamespace
        from slice_events import capture_runtime_events
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            run=root/'.mask/generated/implement-rfc/runs/one';run.mkdir(parents=True)
            (run/'events.jsonl').write_text(json.dumps({'event':'collected','timestamp':100,
                'task_id':'private-task','report_path':'secret-report','prompt':'NEVER EXPORT'})+'\n')
            (run/'one.report.txt').write_text('SECRET SOURCE')
            target=root/'captured.jsonl'
            stats=capture_runtime_events(SimpleNamespace(primary=[('selected',root)]),target,
                    datetime.fromtimestamp(0,timezone.utc),datetime.fromtimestamp(200,timezone.utc))
            self.assertEqual(stats,{'files':1,'events':1,'warnings':0})
            value=target.read_text()
            self.assertNotIn('NEVER EXPORT',value);self.assertNotIn('SECRET',value)
            self.assertNotIn('private-task',value);self.assertNotIn('secret-report',value)
            self.assertEqual(json.loads(value)['project'],'selected')
