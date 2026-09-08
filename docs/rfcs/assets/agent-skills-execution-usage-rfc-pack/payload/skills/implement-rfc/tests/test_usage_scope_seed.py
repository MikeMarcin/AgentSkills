"""Focused portable collector tests; no production credentials or model requests."""
from __future__ import annotations
from argparse import Namespace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import usage
import usage_capture as c
import usage_scope as s


class ScopeTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        self.base = Path(t.name); self.root = self.base/'repo'; self.root.mkdir()
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.sub = self.root/'src'; self.sub.mkdir()

    def document(self, roots):
        return {'schema_version':1,'tool':'mask','tool_version':'0.2.0','command':'project.list',
                'ok':True,'changed':False,'error':None,'data':{'projects':[
                    {'root':str(p),'available':p.is_dir(),'root_identity':
                        {'device':p.stat().st_dev,'inode':p.stat().st_ino} if p.exists() else {'device':0,'inode':0}}
                    for p in roots]}}

    def test_infer_nested_cwd(self):
        self.assertEqual(s.infer_root(self.sub),self.root)

    def test_nearest_mask_declaration(self):
        (self.sub/'.mask.json').write_text('{}')
        child=self.sub/'deep'; child.mkdir()
        self.assertEqual(s.infer_root(child),self.sub)

    def test_does_not_cross_git_boundary(self):
        (self.base/'.mask.json').write_text('{}')
        self.assertEqual(s.infer_root(self.sub),self.root)

    def test_outside_project_refuses(self):
        empty=self.base/'unrelated'; empty.mkdir()
        with self.assertRaises(ValueError): s.infer_root(empty)

    def test_mask_missing_retained(self):
        missing=self.base/'missing'
        rows=s.validate_mask(self.document([self.root,missing]))
        scope=s.ScopedProjects(rows)
        self.assertEqual(len(scope.records),2)
        self.assertIsNotNone(scope.match(str(missing/'old.py')))
        self.assertEqual(scope.records[1]['attribution'],'historical_path_unverified')

    def test_mask_root_identity_mismatch_excluded(self):
        d=self.document([self.root]); d['data']['projects'][0]['root_identity']['inode']+=1
        scope=s.ScopedProjects(s.validate_mask(d))
        self.assertIsNone(scope.match(str(self.root/'a')))
        self.assertEqual(scope.records[0]['identity_check'],'mismatch')

    def test_mask_envelope_rejections(self):
        for key,value in [('tool','other'),('schema_version',2),('ok',False),('changed',True),('command','project.register')]:
            d=self.document([self.root]); d[key]=value
            with self.assertRaises(ValueError): s.validate_mask(d)

    def test_mask_duplicate_and_relative_refuse(self):
        d=self.document([self.root,self.root])
        with self.assertRaises(ValueError): s.validate_mask(d)
        d=self.document([self.root]); d['data']['projects'][0]['root']='relative'
        with self.assertRaises(ValueError): s.validate_mask(d)

    def test_all_registered_not_filtered_by_skill(self):
        other=self.base/'other';other.mkdir()
        d=self.document([self.root,other])
        for row in d['data']['projects']:row['last_manifest']={'skills':[]}
        self.assertEqual(len(s.ScopedProjects(s.validate_mask(d)).records),2)

    def test_public_mask_subprocess(self):
        program=self.base/'fake_mask.py'
        program.write_text('import json,sys\nassert sys.argv[1:]==["project","list","--json"]\nprint('+repr(json.dumps(self.document([self.root])))+')\n')
        rows,provenance=s.mask_projects(python_entrypoint=program)
        self.assertEqual(len(rows),1)
        self.assertEqual(provenance['registered_count'],1)

    def test_mask_failure_does_not_fallback(self):
        program=self.base/'fake_mask.py';program.write_text('raise SystemExit(4)\n')
        with self.assertRaises(ValueError):s.mask_projects(python_entrypoint=program)

    def test_windows_launcher_data_only(self):
        content='@echo off\r\nrem MASK owned launcher v1\r\nsetlocal DisableDelayedExpansion\r\n"C:\\Program Files\\Python\\python.exe" "C:\\100%% work\\ManageAgentSkills\\mask.py" %*\r\nexit /b %errorlevel%\r\n'
        self.assertEqual(s.windows_launcher_argv(content),['C:\\Program Files\\Python\\python.exe','-B','C:\\100% work\\ManageAgentSkills\\mask.py'])
        with self.assertRaises(ValueError):s.windows_launcher_argv(content+'echo malicious\n')

    def test_default_dryrun_no_writes(self):
        command=[sys.executable,'-B',str(Path(usage.__file__)),'--dry-run']
        r=subprocess.run(command,cwd=self.sub,text=True,capture_output=True,check=True)
        d=json.loads(r.stdout)
        self.assertEqual(d['selection']['source'],'invocation_cwd')
        self.assertEqual(d['projects'][0]['root'],str(self.root))
        self.assertEqual(list(self.sub.iterdir()),[])

    def test_empty_mask_not_machine_fallback(self):
        rows=s.validate_mask(self.document([])); scope=s.ScopedProjects(rows)
        self.assertIsNone(scope.match(str(self.root)));self.assertEqual(scope.records,[])

    def test_scopes_longest_path(self):
        scope=s.ScopedProjects([{'root':str(self.root),'label':'outer'},{'root':str(self.sub),'label':'inner'}])
        self.assertEqual(scope.match(str(self.sub/'x')),'inner')
        self.assertIsNone(scope.match(str(self.root)+'-other'))

    def test_zip_exclusive(self):
        stage=self.base/'stage';stage.mkdir();(stage/'x.txt').write_text('ok')
        target=self.base/'out.zip';target.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):usage.publish(stage,target)
        self.assertEqual(target.read_bytes(),b'preserve')

    def test_new_control_targets_preserved_no_message(self):
        out=self.base/'data';out.mkdir();scope=s.ScopedProjects([{'root':str(self.root),'label':'test'}])
        a=c.Collector(scope,c.dt('2026-09-07T00:00:00Z'),c.dt('2026-09-08T00:00:00Z'),out,0,4096)
        session=a.session('codex','s',None,'test','unknown',None,self.root/'log')
        a.tool_call(session,self.root/'log',1,'2026-09-07T12:00:00Z','c','functions.wait_agent',{'agent_ids':['secret-child'],'message':'SECRET'})
        a.writer.close();e=json.loads((out/'events.jsonl').read_text())
        self.assertEqual(e['tool'],'wait_agent');self.assertEqual(e['targets'],[c.ident('secret-child')])
        self.assertNotIn('SECRET',(out/'events.jsonl').read_text())

    def test_large_stream_and_unterminated_tail(self):
        out=self.base/'data';out.mkdir();scope=s.ScopedProjects([{'root':str(self.root),'label':'test'}])
        a=c.Collector(scope,c.dt('2026-09-07T00:00:00Z'),c.dt('2026-09-08T00:00:00Z'),out,0,4096)
        path=self.base/'log';path.write_bytes(b'{"type":"first"}\n{"type":"tail"}')
        self.assertEqual([row['type'] for _,row in a.rows(path)],['first'])
        self.assertEqual(a.problems[0]['code'],'unterminated_snapshot_tail');a.writer.close()

    def test_counter_baseline_not_counted(self):
        out=self.base/'data';out.mkdir();scope=s.ScopedProjects([{'root':str(self.root),'label':'test'}])
        a=c.Collector(scope,c.dt('2026-09-07T00:00:00Z'),c.dt('2026-09-08T00:00:00Z'),out,0,4096)
        session=a.session('codex','s',None,'test','unknown',None,self.root/'log')
        a.emit(session,'token_observation','2026-09-06T23:59:00Z',self.root/'log',1,cumulative={'input_tokens':123})
        self.assertEqual(session['events'],0);self.assertEqual(len(a.counter_baselines),1);a.writer.close()

    def test_actual_linked_worktree_separate(self):
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','base'],check=True)
        other=self.base/'linked'
        subprocess.run(['git','-C',str(self.root),'worktree','add','-q','-b','linked',str(other)],check=True)
        scope=s.ScopedProjects([{'root':str(self.root)},{'root':str(other)}])
        self.assertNotEqual(scope.match(str(self.root)),scope.match(str(other)))
        self.assertEqual(scope.records[0]['git_common_dir_group_id'],scope.records[1]['git_common_dir_group_id'])
        self.assertEqual(len(s.ScopedProjects([{'root':str(self.root)}]).records),1)
        self.assertEqual(len(s.ScopedProjects([{'root':str(self.root)}],include_worktrees=True).records),2)

if __name__=='__main__':unittest.main()
