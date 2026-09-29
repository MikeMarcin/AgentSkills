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
            git(source,'remote','add','origin',str(remote))
            env={**os.environ,'MASK_HOME':str(base/'machine'),'PYTHONDONTWRITEBYTECODE':'1'}
            def mask(*args):
                done=subprocess.run([sys.executable,'-B',os.environ['MASK_TEST_PROGRAM'],*map(str,args),'--json'],
                                    env=env,cwd=base,capture_output=True,text=True)
                self.assertEqual(done.stderr,'',done.stderr)
                return json.loads(done.stdout)
            self.assertTrue(mask('tap','fixture',remote,'--checkout',source)['ok'])
            for name in ('one','two'):
                root=base/name;init_repo(root,token=name)
                installed=mask('install','implement-rfc','--project',root,'--no-update')
                self.assertEqual(installed['error']['code'],'confirmation.required',installed)
                preview = mask('install', 'implement-rfc', '--project', root, '--dry-run')
                self.assertTrue(preview['ok'], preview)
                setup = mask('install', 'implement-rfc', '--project', root, '--no-update',
                             '--approve-plan', preview['data']['plan_hash'])
                self.assertTrue(setup['ok'], setup)
                script=root/'.agents/skills/implement-rfc/scripts/workflow_preflight.py'
                self.assertTrue(script.is_file())
                before=(base/'machine/state.json').read_bytes()
                for strategy in ('direct','native','coordinator-implementer'):
                    done=subprocess.run([sys.executable,'-B',str(script),'--repo-root',str(root),'--mask',os.environ['MASK_TEST_PROGRAM'],
                                         '--strategy',strategy,'--json'],env=env,capture_output=True,text=True)
                    self.assertEqual(done.returncode,0,done.stdout+done.stderr)
                    result=json.loads(done.stdout)
                    self.assertEqual((result['state'], result['host_load']), ('ready', 'not_verified'))
                    if strategy == 'coordinator-implementer':
                        roles = {(row['agent'], row['name']): row for row in result['roles']}
                        self.assertEqual(set(roles), {('codex', 'rfc-implementer'),
                                                      ('claude', 'rfc-implementer')})
                        self.assertTrue(all(row['state'] == 'ok' for row in roles.values()))
                        self.assertEqual(roles[('codex', 'rfc-implementer')]['route'],
                                         {'model': 'gpt-6.1-sol', 'model_reasoning_effort': 'xhigh'})
                        self.assertEqual(roles[('claude', 'rfc-implementer')]['route'],
                                         {'model': 'claude-opus-5-5', 'effort': 'high'})
                    else:
                        self.assertEqual(result['roles'], [])
                selected_roles = mask('status', '--project', root, '--check', '--workflow-profile', 'implement-rfc=planner-worker')
                self.assertTrue(selected_roles['ok'], selected_roles)
                default=mask('status','--project',root,'--check')
                self.assertTrue(default['ok'], default)
                self.assertEqual((base/'machine/state.json').read_bytes(),before)
                self.assertTrue((root/'.codex/agents/rfc-implementer.toml').is_file())
                self.assertTrue((root/'.claude/agents/rfc-implementer.md').is_file())
                # A plain invocation selects the provider-neutral default with its native role.
                command=[sys.executable,'-B',str(script),'--repo-root',str(root),'--mask',os.environ['MASK_TEST_PROGRAM'],'--json']
                done=subprocess.run(command,env=env,capture_output=True,text=True)
                self.assertEqual(done.returncode,0,done.stdout+done.stderr)
                result=json.loads(done.stdout)
                self.assertEqual(result['selection']['strategy'],'coordinator-implementer')
                self.assertEqual(result['deployment_readiness'],'ready_pinned')
                # Approved local authoring is explicitly unpinned, still observationally ready.
                preview=mask('skill','dev-link','fixture/implement-rfc','--project',root,'--authoring-root',source,'--dry-run')
                self.assertTrue(preview['ok'],preview)
                applied=mask('skill','dev-link','fixture/implement-rfc','--project',root,'--authoring-root',source,
                             '--approve-plan',preview['data']['plan_hash'])
                self.assertTrue(applied['ok'],applied)
                before=(base/'machine/state.json').read_bytes()
                done=subprocess.run(command,env=env,capture_output=True,text=True)
                self.assertEqual(done.returncode,0,done.stdout+done.stderr)
                result=json.loads(done.stdout)
                self.assertEqual(result['state'], 'ready')
                self.assertEqual(result['deployment_readiness'], 'ready_dev_link')
                self.assertEqual({(row['agent'], row['name']) for row in result['roles']},
                                 {('codex', 'rfc-implementer'), ('claude', 'rfc-implementer')})
                self.assertEqual((base/'machine/state.json').read_bytes(),before)
                (root/'.mask/skill-config/implement-rfc/project.md').unlink()
                self.assertFalse(mask('status','--project',root,'--check','--workflow-profile','implement-rfc=direct')['ok'])
