"""Run the retained packet checker with the owner's explicit role rename only."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / 'docs/rfcs/assets/agent-skills-standard-worker-review'
spec = importlib.util.spec_from_file_location('standard_worker_target', PACK / 'tools/check_target_routes.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class StandardWorkerTargetTests(unittest.TestCase):
    def test_exact_target_and_native_requests(self):
        config = ROOT / 'skills/implement-rfc/config'
        roles = json.loads((config / 'roles.json').read_text())
        routing = json.loads((config / 'routing.json').read_text())
        target = json.loads((PACK / 'fixtures/target-routing.json').read_text().replace(
            'rfc-critical-reviewer', 'rfc-reviewer-critical'))
        integrator = roles['roles'].pop('rfc-integrator')
        implementer = roles['roles'].pop('rfc-implementer')
        self.assertEqual(set(integrator['delegation']['allowed_roles']), set(target['roles']))
        self.assertEqual(integrator['mutation'], 'workspace-write')
        self.assertEqual(implementer['delegation']['allowed_roles'], [])
        self.assertEqual(routing['assignments'].pop('rfc-integrator'), 'integration')
        self.assertEqual(routing['assignments'].pop('rfc-implementer'), 'implementation')
        for provider, expected in [('codex', {'model':'gpt-5.6-sol','effort':'xhigh'}),
                                   ('claude', {'model':'claude-opus-5','effort':'xhigh'})]:
            self.assertEqual(routing['providers'][provider]['classes'].pop('integration'), expected)
            implementation = routing['providers'][provider]['classes'].pop('implementation')
            self.assertEqual(implementation['effort'], 'max' if provider == 'codex' else 'xhigh')
        self.assertEqual(checker.configuration_findings(roles, routing, target), [])
        self.assertEqual(checker.rendering_findings(ROOT, roles, routing, target), [])
