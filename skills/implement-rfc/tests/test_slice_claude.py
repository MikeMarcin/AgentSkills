"""Structured companion parsing and leaf/recovery contracts."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import slice_claude as c


class Process:
    def __init__(self,rows):self.stdout=io.BytesIO(b''.join(json.dumps(r).encode()+b'\n' for r in rows))
    def poll(self):return 0
    def terminate(self):pass
    def wait(self,timeout):return 0


class ClaudeTests(unittest.TestCase):
    def setUp(self):
        self.receipt={'driver_session_id':'session','driver_turn_id':'assignment:task'}
        self.driver=c.ClaudeDriver(capabilities={'launch':True,'read_only_report_resume':True})
        self.packet={'cwd':str(Path.cwd()),'prompt':'useful task','model':'sonnet','effort':'high','tools':['Read'], 'max_turns':2,'timeout_seconds':30}
    def test_structured_limit_not_quoted_text(self):
        partial=c.normalize({'type':'assistant','session_id':'session','message':{'content':[{'type':'text','text':'Maximum turns reached'}]}},self.receipt,1)
        self.assertEqual(partial['kind'],'partial')
        final=c.normalize({'type':'result','session_id':'session','subtype':'error_max_turns','is_error':True},self.receipt,2)
        self.assertEqual(final['kind'],'max_turns')
    def test_final_usage_allowlisted_and_session_checked(self):
        event=c.normalize({'type':'result','session_id':'session','subtype':'success','result':'report','usage':{'input_tokens':3,'secret':'never'}},self.receipt,1)
        self.assertEqual(event['usage_aggregate_do_not_add'],{'input_tokens':3})
        with self.assertRaises(ValueError):c.normalize({'type':'result','session_id':'wrong','subtype':'success'},self.receipt,2)
    def test_exact_leaf_command_no_bare_or_bypass(self):
        with patch.object(c.subprocess,'Popen',return_value=Process([])) as popen:
            self.driver.spawn(self.packet,'session')
        argv=popen.call_args.args[0]
        self.assertIn('--safe-mode',argv);self.assertNotIn('--bare',argv)
        self.assertNotIn('--dangerously-skip-permissions',argv)
        self.assertEqual(argv[argv.index('--tools')+1],'Read')
        self.assertEqual(argv[argv.index('--disallowedTools')+1],'mcp__*')
    def test_recovery_disables_all_tools_and_keeps_session(self):
        self.driver.owned['session']={'process':Process([]),'packet':self.packet,'attempt':'task','cancelled':False,'recovered':False}
        with patch.object(self.driver,'auth'),patch.object(self.driver,'spawn',return_value=Process([{'type':'result','session_id':'session','subtype':'success','result':'retained'}])) as spawn:
            self.assertEqual(self.driver.recover_report(self.receipt,10)['report'],'retained')
            self.assertEqual(spawn.call_args.args[0]['tools'],[])
            self.assertEqual(spawn.call_args.args[0]['max_turns'],1)
            self.assertTrue(spawn.call_args.kwargs['resume'])
        with self.assertRaises(ValueError):self.driver.recover_report(self.receipt,10)
    def test_oversized_and_malformed_streams_refuse(self):
        for raw in (b'x'*(c.MAX_FRAME+1),b'not json\n'):
            process=Process([]);process.stdout=io.BytesIO(raw)
            with self.assertRaises(ValueError):list(self.driver.stream(process,1))
    def test_cancelled_cannot_resume(self):
        self.driver.owned['session']={'process':Process([]),'packet':self.packet,'attempt':'task','cancelled':False,'recovered':False}
        self.driver.cancel(self.receipt)
        with self.assertRaises(ValueError):self.driver.recover_report(self.receipt,10)


if __name__=='__main__':unittest.main()
