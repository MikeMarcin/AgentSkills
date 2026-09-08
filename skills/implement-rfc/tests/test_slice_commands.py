"""Command runner admission and subprocess checks in disposable consumers."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import slice_model as model
import run_slice as runner


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rfc-slice-command-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        context = self.root/'.mask/skill-config/implement-rfc'
        context.mkdir(parents=True)
        source = Path(__file__).resolve().parents[3]/'.mask/skill-config/implement-rfc'
        for name in ('project.json','project.md'):
            shutil.copyfile(source/name,context/name)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','base'],check=True)
        self.script = self.root/'check.py'
        self.script.write_text('print("Ran 1 test")\n')
        argv = [sys.executable,str(self.script)]
        (self.root/'permission.json').write_text(json.dumps({'schema':'implement-rfc.command-permissions.v1','execution':'local_unsandboxed','allowed_argv':[argv]}))
        (self.root/'route.json').write_text('{}')
        st=self.root.stat()
        self.order = {'schema':'implement-rfc.slice-order.v1','example_only':False,'run_id':'fixture','slice_id':'fixture-card',
                      'consumer_root':str(self.root),'invocation_root':str(self.root),
                      'root_identity':{'device':st.st_dev,'inode':st.st_ino},
                      'base_revision':subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip(),
                      'approved_dirty_paths':[],'profile':'baseline','routing_digest':model.file_hash(self.root/'route.json'),
                      'routing_ref':'route.json','permissions_ref':'permission.json','max_parallel_mutations':1,'max_agent_dispatches':0,
                      'input_hashes':{n:model.file_hash(self.root/n) for n in ('check.py','route.json','permission.json')},
                      'tasks':[{'id':'check','kind':'command','depends_on':[],'cwd':'.','timeout_seconds':2,'owned_paths':[],
                                'retry':'never','argv':argv,'predicate':{'exit_code':0,'required_artifacts':[],'tests':'unittest'}},
                               {'id':'gate','kind':'integration_gate','depends_on':['check'],'cwd':'.','timeout_seconds':2,'owned_paths':[],
                                'retry':'never','acceptance_ref':'live-card integrator decision'}]}

    def execute(self):
        return runner.start(self.order,model.digest(self.order))

    def change_script(self,text):
        self.script.write_text(text)
        self.order['input_hashes']['check.py']=model.file_hash(self.script)

    def test_public_cli_reaches_only_integration_gate(self):
        order=self.root/'order.json';order.write_text(json.dumps(self.order))
        result=subprocess.run([sys.executable,'-B',runner.__file__,'start','--order',str(order),'--approve-order',model.digest(self.order)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data['tasks']['gate']['event'],'awaiting_integration')
        self.assertEqual(data['semantic_acceptance'],'not_decided_by_runner')

    def test_stale_or_unapproved_causes_no_dispatch(self):
        with self.assertRaises(ValueError):runner.start(self.order,'wrong')
        self.script.write_text('raise RuntimeError()')
        with self.assertRaises(ValueError):self.execute()
        self.assertFalse((self.root/'.mask/generated').exists())

    def test_cycles_root_and_inline_shell_refuse(self):
        for edit in ('cycle','root','shell'):
            order=copy.deepcopy(self.order)
            if edit=='cycle':order['tasks'][0]['depends_on']=['gate']
            elif edit=='root':order['root_identity']['inode']+=1
            else:order['tasks'][0]['argv']=[sys.executable,'-c','print(1)']
            with self.assertRaises(ValueError):model.validate(order)

    def test_zero_selected_tests_fails(self):
        self.change_script('print("Ran 0 tests")')
        data=self.execute()
        self.assertEqual(data['tasks']['check']['event'],'execution_failed')
        self.assertNotIn('gate',data['tasks'])

    def test_nonzero_and_missing_artifact_fail(self):
        self.change_script('raise SystemExit(7)')
        self.assertEqual(self.execute()['tasks']['check']['event'],'execution_failed')
        self.order['run_id']='missing'
        self.change_script('print("Ran 1 test")')
        self.order['tasks'][0]['predicate']['required_artifacts']=['missing.txt']
        self.assertEqual(self.execute()['tasks']['check']['event'],'execution_failed')

    def test_timeout_and_run_id_reuse(self):
        self.change_script('import time\ntime.sleep(10)')
        self.order['tasks'][0]['timeout_seconds']=1
        self.assertEqual(self.execute()['tasks']['check']['event'],'execution_failed')
        with self.assertRaises(FileExistsError):self.execute()

    def test_unrelated_change_does_not_invalidate(self):
        (self.root/'unrelated.txt').write_text('unrelated work')
        self.assertEqual(self.execute()['tasks']['gate']['event'],'awaiting_integration')

    def test_torn_tail_visible_and_interior_corruption_refuses(self):
        self.execute();path=runner.run_path(self.root,'fixture')/'events.jsonl'
        with path.open('ab') as stream:stream.write(b'{')
        self.assertEqual(runner.status(path.parent)['warnings'],['torn_final_event'])
        with path.open('ab') as stream:stream.write(b'\n')
        with self.assertRaises(ValueError):runner.status(path.parent)

    def test_cancellation_preserves_report_and_stops_gate(self):
        import threading,time
        self.change_script('import time\ntime.sleep(10)')
        self.order['tasks'][0]['timeout_seconds']=10
        path=runner.run_path(self.root,'fixture')
        def cancel():
            deadline=time.monotonic()+5
            while not (path/'events.jsonl').exists() and time.monotonic()<deadline:
                time.sleep(.01)
            (path/'cancel.request').touch()
        worker=threading.Thread(target=cancel)
        worker.start()
        try:
            data=self.execute()
        finally:
            worker.join()
        self.assertEqual(data['tasks']['check']['event'],'cancelled')
        self.assertNotIn('gate',data['tasks'])

    def test_output_limit_stops_command(self):
        self.change_script('import sys\nsys.stdout.write("x" * (5*1024*1024))')
        self.assertEqual(self.execute()['tasks']['check']['event'],'execution_failed')
        path=runner.run_path(self.root,'fixture')/'check-1.stdout'
        self.assertLessEqual(path.stat().st_size,runner.OUTPUT_LIMIT)

    def test_changed_input_between_stages_blocks_gate(self):
        self.change_script('from pathlib import Path\nPath("route.json").write_text("changed")\nprint("Ran 1 test")')
        data=self.execute()
        self.assertEqual(data['tasks']['gate']['event'],'completion_unknown')

    def test_argv_spaces_remain_one_argument(self):
        self.change_script('import sys\nassert sys.argv[1:] == ["two words ü 100%"]\nprint("Ran 1 test")')
        self.order['tasks'][0]['argv'].append('two words ü 100%')
        policy=self.root/'permission.json'
        document=json.loads(policy.read_text())
        document['allowed_argv']=[self.order['tasks'][0]['argv']]
        policy.write_text(json.dumps(document))
        self.order['input_hashes']['permission.json']=model.file_hash(policy)
        self.assertEqual(self.execute()['tasks']['gate']['event'],'awaiting_integration')


if __name__=='__main__':unittest.main()
