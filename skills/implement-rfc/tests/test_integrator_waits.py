import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_runtime_adapters as renderer
from project_fixtures import CONFIG


def words(text):
    return ' '.join(text.split())


class IntegratorWaits(unittest.TestCase):
    def test_integrator_collects_children_inside_its_turn(self):
        text=(ROOT/'references/milestone-integration.md').read_text()
        section=words(text[text.index('## 3. Assign complete slices'):text.index('## 4. ')])
        self.assertLess(section.index('Collect children inside your turn'),section.index('**Assigned:**'))
        self.assertIn('Your final message is your return',section)
        self.assertIn('dispatch leaves in the foreground (`run_in_background: false`)',section)
        self.assertIn('`TaskOutput` does not exist inside subagents',section)

    def test_claude_adapter_notes_record_nested_child_results(self):
        compatibility=words((ROOT/'references/runtime-compatibility.md').read_text())
        self.assertNotIn('leave foreground/background selection',compatibility)
        self.assertIn('dispatch leaf roles in the foreground',compatibility)
        self.assertIn('### Nested child results (2026-09-11)',compatibility)
        self.assertIn('(#nested-child-results-2026-09-11)',compatibility)
        self.assertIn('(milestone-integration.md#3-assign-complete-slices)',compatibility)
        self.assertIn('result verbatim',compatibility)

    def test_role_prompts_carry_the_waiting_contract(self):
        roles=renderer.validate_roles(json.loads((ROOT/'config/roles.json').read_text()))
        route={'model':'fixture','effort':'low'}
        integrator=renderer.role_prompt('rfc-integrator',roles['rfc-integrator'],route,CONFIG,provider='claude')
        self.assertIn('collect every child inside your turn',integrator)
        # TaskOutput is stripped from every subagent, so the adapter must not grant it.
        self.assertNotIn('TaskOutput',renderer.COORDINATION_TOOLS)
        rendered=renderer.render_claude_agent('rfc-integrator',roles['rfc-integrator'],route,CONFIG,'test')
        self.assertNotIn('TaskOutput',rendered)
        self.assertIn('SendMessage',rendered)
        for name in renderer.LEAF_ROLES:
            with self.subTest(role=name):
                prompt=renderer.role_prompt(name,roles[name],route,CONFIG,provider='claude')
                self.assertIn('finish your own background commands before you return',prompt)


if __name__=='__main__':
    unittest.main()
