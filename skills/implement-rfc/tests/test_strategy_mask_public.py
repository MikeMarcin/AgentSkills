"""Real MASK handoff in two disposable consumers; opt in with MASK_TEST_PROGRAM."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from project_fixtures import init_repo, git

SKILL = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('MASK_TEST_PROGRAM'), 'explicit local MASK program required')
class StrategyMaskPublicTests(unittest.TestCase):
    def test_canonical_skill_profiles_through_installed_links(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory).resolve(); source=base/'source'; source.mkdir()
            git(source,'init','-b','main');git(source,'config','user.name','fixture');git(source,'config','user.email','fixture@example.invalid')
            shutil.copytree(SKILL,source/'skills/implement-rfc',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            git(source,'add','skills');git(source,'commit','-m','Canonical candidate')
            remote=base/'tap.git';git(base,'clone','--bare',str(source),str(remote))
            env={**os.environ,'MASK_HOME':str(base/'machine'),'PYTHONDONTWRITEBYTECODE':'1'}
            def mask(*args):
                done=subprocess.run([sys.executable,'-B',os.environ['MASK_TEST_PROGRAM'],*map(str,args),'--json'],
                                    env=env,cwd=base,capture_output=True,text=True)
                self.assertEqual(done.stderr,'',done.stderr)
                return json.loads(done.stdout)
            self.assertTrue(mask('tap','add','fixture',remote)['ok'])
            for name in ('one','two'):
                root=base/name;init_repo(root,token=name)
                installed=mask('install','implement-rfc','--project',root)
                self.assertEqual(installed['error']['code'],'workflow.incomplete',installed)
                self.assertTrue(mask('integration','approve','--project',root)['ok'])
                script=root/'.agents/skills/implement-rfc/scripts/workflow_preflight.py'
                self.assertTrue(script.is_file())
                before=(base/'machine/state.json').read_bytes()
                for strategy in ('direct','native'):
                    done=subprocess.run([sys.executable,'-B',str(script),'--repo-root',str(root),'--mask',os.environ['MASK_TEST_PROGRAM'],
                                         '--strategy',strategy,'--json'],env=env,capture_output=True,text=True)
                    self.assertEqual(done.returncode,0,done.stdout+done.stderr)
                    result=json.loads(done.stdout)
                    self.assertEqual((result['state'],result['roles'],result['host_load']),('ready',[],'not_verified'))
                default=mask('ensure','--project',root,'--check')
                self.assertFalse(default['ok'])
                self.assertEqual((base/'machine/state.json').read_bytes(),before)
                self.assertFalse((root/'.codex/agents').exists())
                (root/'.mask/skill-config/implement-rfc/project.md').unlink()
                self.assertFalse(mask('ensure','--project',root,'--check','--workflow-profile','implement-rfc=direct')['ok'])
