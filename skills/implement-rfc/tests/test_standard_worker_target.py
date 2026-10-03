"""Keep the retained role-boundary target renderable after model-only amendments."""
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
    def test_historical_target_boundaries_and_native_requests(self):
        config = ROOT / 'skills/implement-rfc/config'
        roles = json.loads((config / 'roles.json').read_text())
        routing = json.loads((config / 'routing.json').read_text())
        target = json.loads((PACK / 'fixtures/target-routing.json').read_text().replace(
            'rfc-critical-reviewer', 'rfc-reviewer-critical'))
        target['provider_classes']['claude']['critical']['effort'] = 'xhigh'
        integrator = roles['roles'].pop('rfc-integrator')
        implementer = roles['roles'].pop('rfc-implementer')
        self.assertEqual(set(integrator['delegation']['allowed_roles']), set(target['roles']))
        self.assertEqual(integrator['mutation'], 'workspace-write')
        self.assertEqual(implementer['delegation']['allowed_roles'], [])
        self.assertEqual(routing['assignments'].pop('rfc-integrator'), 'integration')
        self.assertEqual(routing['assignments'].pop('rfc-implementer'), 'implementation')
        # The packet is immutable provenance. Current defaults and their emitted
        # requests are checked independently by test_render_runtime_adapters.
        # Reuse the old exact pairs here to verify historical routing readability
        # and the preserved seven leaf roles, permissions, limits and addenda.
        for provider, classes in target['provider_classes'].items():
            routing['providers'][provider]['classes'] = classes
        self.assertEqual(checker.configuration_findings(roles, routing, target), [])
        self.assertEqual(checker.rendering_findings(ROOT, roles, routing, target), [])
