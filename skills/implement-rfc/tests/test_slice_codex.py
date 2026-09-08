"""Native protocol fixtures; account/key and approval boundaries stay explicit."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from slice_codex import CodexDriver


class RpcFixture:
    def __init__(self):self.calls=[];self.auth='chatgpt';self.messages=[]
    def request(self,method,params):
        self.calls.append((method,params))
        if method=='account/read':return {'account':{'type':self.auth}}
        if method=='thread/start':return {'thread':{'id':'owned-thread'}}
        if method=='turn/start':return {'turn':{'id':'owned-turn'}}
        return {}
    def notifications(self,seconds):yield from self.messages
    def close(self):pass


class CodexTests(unittest.TestCase):
    def setUp(self):
        self.rpc=RpcFixture();self.driver=CodexDriver(rpc=self.rpc,capabilities={'launch':True})
        self.packet={'cwd':str(Path.cwd()),'prompt':'bounded work','model':'explicit-model','effort':'high',
                     'approval_policy':'on-request','sandbox':'read-only','timeout_seconds':30}
    def test_exact_native_route_permissions_and_completion(self):
        receipt=self.driver.launch(self.packet,'task-1')
        self.assertEqual([x[0] for x in self.rpc.calls],['account/read','thread/start','turn/start'])
        self.assertEqual(self.rpc.calls[1][1]['approvalPolicy'],'on-request')
        self.assertEqual(self.rpc.calls[2][1]['model'],'explicit-model')
        self.rpc.messages=[{'method':'item/completed','params':{'threadId':'owned-thread','turnId':'owned-turn','item':{'id':'item','type':'agentMessage','text':'report'}}},
                           {'method':'turn/completed','params':{'threadId':'owned-thread','turn':{'id':'owned-turn','status':'completed'}}}]
        events=list(self.driver.events(receipt))
        self.assertEqual([e['kind'] for e in events],['partial','completed'])
        self.assertEqual(events[-1]['report'],'report')
    def test_api_auth_never_starts_turn(self):
        self.rpc.auth='apiKey'
        with self.assertRaises(ValueError):self.driver.launch(self.packet,'task')
        self.assertEqual(len(self.rpc.calls),1)
    def test_wrong_turn_and_arbitrary_resume_refuse(self):
        receipt=self.driver.launch(self.packet,'task')
        wrong={**receipt,'driver_turn_id':'other'}
        with self.assertRaises(ValueError):self.driver.cancel(wrong)
        with self.assertRaises(ValueError):self.driver.recover_report(receipt)
        self.rpc.messages=[{'method':'turn/completed','params':{'threadId':'someone-else','turn':{'id':'owned-turn','status':'completed'}}}]
        with self.assertRaises(ValueError):list(self.driver.events(receipt))
    def test_owned_cancel_uses_exact_ids(self):
        receipt=self.driver.launch(self.packet,'task')
        self.assertTrue(self.driver.cancel(receipt))
        self.assertEqual(self.rpc.calls[-1],('turn/interrupt',{'threadId':'owned-thread','turnId':'owned-turn'}))
    def test_unsupported_driver_and_permissions_refuse(self):
        self.driver._capabilities={'launch':False}
        with self.assertRaises(ValueError):self.driver.launch(self.packet,'task')
        self.assertEqual(self.rpc.calls,[])
        self.driver._capabilities={'launch':True};self.packet['sandbox']='danger-full-access'
        with self.assertRaises(ValueError):self.driver.launch(self.packet,'task')


if __name__=='__main__':unittest.main()
