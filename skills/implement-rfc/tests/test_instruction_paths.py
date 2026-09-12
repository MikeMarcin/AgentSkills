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
    def test_plan_first_projection_and_checked_continuation_in_both_hosts(self):
        skill=(ROOT/'SKILL.md').read_text()
        self.assertLess(skill.index('Before implementation dispatch'),skill.index('**Dispatched:**'))
        rules=(ROOT/'references/milestone-plans.md').read_text()
        self.assertIn('same context',rules)
        self.assertIn('Card completion, commits and headings are progress',rules)
        self.assertIn('Required human',rules)
        roles=renderer.validate_roles(json.loads((ROOT/'config/roles.json').read_text()))
        for host_render in (renderer.render_codex_agent,renderer.render_claude_agent):
            for name in ('rfc-integrator','rfc-worker','rfc-worker-deep'):
                rendered=host_render(name,roles[name],{'model':'fixture','effort':'low'},CONFIG,'test')
                if name=='rfc-integrator':
                    self.assertIn('assigned authored plan',rendered)
                    self.assertIn('explicit continue/fresh/wait/stop',rendered)
                    self.assertIn('bound obligations and exit evidence',rendered)
                else:
                    self.assertIn('several named cards',rendered)
                    self.assertIn('Do not independently select unassigned work',rendered)
                    self.assertNotIn('current issue-card slice',rendered)
                    self.assertIn('commit, or push',rendered)
                    self.assertEqual(roles[name]['delegation']['allowed_roles'],[])

    def test_verdicts_go_to_the_integrator_and_resume_has_a_fallback(self):
        skill=(ROOT/'SKILL.md').read_text()
        self.assertIn('Record whether this host exposes `SendMessage`',skill)
        self.assertIn('Do not\nsummarise or interpret the note',skill)
        self.assertLess(skill.index('A human verdict is engineering input'),skill.index('**Closed:**'))
        self.assertIn('otherwise dispatch a fresh integrator',skill)
        attendance=(ROOT/'references/attendance.md').read_text()
        self.assertIn('it forwards\nthe session id, the event cursor and the candidate ids',attendance)
        self.assertIn('may delegate to `rfc-worker-deep`',attendance)
        handoff=(ROOT/'references/coordination-handoff.md').read_text()
        self.assertIn('## Hosts without SendMessage',handoff)
        self.assertIn('fresh-dispatch-ready',handoff)
        self.assertIn('confirm its children and task commands\nare quiescent',handoff)
        for row in ('continue-milestone','review-request'):
            line=next(l for l in handoff.splitlines() if l.startswith(f'| {row} |'))
            self.assertIn('without `SendMessage`',line)
        compatibility=(ROOT/'references/runtime-compatibility.md').read_text()
        self.assertIn('### Desktop app Code tab observation',compatibility)
        self.assertIn('coordination-handoff.md#hosts-without-sendmessage',compatibility)

    def test_recovery_and_behavioral_acceptance_reach_operation_references(self):
        delegation=(ROOT/'references/delegated-execution.md').read_text()
        handoff=(ROOT/'references/coordination-handoff.md').read_text()
        verification=(ROOT/'references/verification-and-closeout.md').read_text()
        attendance=(ROOT/'references/attendance.md').read_text()
        self.assertIn("assignment's existing evidence location",delegation)
        self.assertLess(delegation.index("collect the child's available result"),
                        delegation.index('Resume the same owner'))
        self.assertIn('every unsatisfied obligation',delegation)
        self.assertIn('followup_task',handoff)
        self.assertIn('active child from resuming an idle child',handoff)
        self.assertIn('collect its available result and checkpoint/artifact',handoff)
        self.assertIn('terminal observable result',verification)
        self.assertIn('negative control',verification)
        self.assertIn('qualification-guard.md',verification)
        self.assertIn('Before marking each candidate ready',attendance)
        self.assertIn('independent judgeable candidates can proceed',attendance)
        self.assertIn('digest identifies',attendance)

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
