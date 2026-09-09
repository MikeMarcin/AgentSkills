import json
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_runtime_adapters as renderer
from project_fixtures import CONFIG


class InstructionPaths(unittest.TestCase):
    def test_all_selected_role_branch_links_resolve(self):
        selected=['SKILL.md','references/milestone-integration.md',
                  'references/delegated-execution.md','references/verification-and-closeout.md',
                  'references/attendance.md','references/model-routing.md']
        for rel in selected:
            file=ROOT/rel
            for target in re.findall(r'\]\(([^\s)]+)\)',file.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                with self.subTest(file=rel,target=target):
                    self.assertTrue((file.parent/target.split('#')[0]).exists())

    def test_integrator_enters_engineering_without_coordinator_loop(self):
        roles=renderer.validate_roles(json.loads((ROOT/'config/roles.json').read_text()))
        self.assertEqual(roles['rfc-integrator']['entrypoint'],'references/milestone-integration.md')
        for name in renderer.LEAF_ROLES:
            self.assertEqual(roles[name]['delegation']['allowed_roles'],[])
            self.assertNotIn('entrypoint',roles[name])
        # Discovery roots are host-specific; an ordinary role does not acquire the
        # coordinator entrypoint just because it can use the shared skill.
        project=CONFIG
        role=roles['rfc-integrator'];route={'model':'fixture','effort':'high'}
        codex=renderer.render_codex_agent('rfc-integrator',role,route,project,'test')
        claude=renderer.render_claude_agent('rfc-integrator',role,route,project,'test')
        self.assertIn('.agents/skills/implement-rfc/references/milestone-integration.md',codex)
        self.assertIn('.claude/skills/implement-rfc/references/milestone-integration.md',claude)
        self.assertNotIn('permissionMode:',claude)


if __name__=='__main__':
    unittest.main()
