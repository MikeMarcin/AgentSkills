"""Tests of the packet checker, not tests of an implemented RFC."""
import copy
import json
import unittest
from pathlib import Path
from check_target_routes import configuration_findings, version

TARGET = json.loads((Path(__file__).resolve().parents[1] / 'fixtures/target-routing.json').read_text())

class TargetCheckerTests(unittest.TestCase):
    def setUp(self):
        self.roles = {'roles': copy.deepcopy(TARGET['roles'])}
        self.routing = {
            'assignments': copy.deepcopy(TARGET['assignments']),
            'providers': {p: {'classes': copy.deepcopy(c)} for p, c in TARGET['provider_classes'].items()},
        }
        self.routing['providers']['claude']['minimum_cli_version'] = '2.1.255'

    def findings(self):
        return configuration_findings(self.roles, self.routing, TARGET)

    def test_exact_target_passes(self):
        self.assertEqual(self.findings(), [])

    def test_old_generic_worker_is_rejected(self):
        self.routing['assignments']['rfc-worker'] = 'deep'
        self.assertTrue(self.findings())

    def test_coupled_reviewer_is_rejected(self):
        self.routing['assignments']['rfc-reviewer'] = 'deep'
        self.assertTrue(self.findings())

    def test_claude_standard_xhigh_is_required(self):
        self.routing['providers']['claude']['classes']['standard']['effort'] = 'high'
        self.assertTrue(self.findings())

    def test_fable_critical_high_is_required(self):
        self.routing['providers']['claude']['classes']['critical']['effort'] = 'xhigh'
        self.assertTrue(self.findings())

    def test_unrelated_route_change_is_rejected(self):
        self.routing['providers']['codex']['classes']['balanced']['effort'] = 'medium'
        self.assertTrue(self.findings())

    def test_retired_role_is_rejected(self):
        self.roles['roles']['rfc-worker-routine'] = copy.deepcopy(TARGET['roles']['rfc-worker'])
        self.assertTrue(self.findings())

    def test_leaf_boundary_is_preserved(self):
        self.roles['roles']['rfc-worker']['may_spawn_utility'] = True
        self.assertTrue(self.findings())

    def test_limits_are_preserved(self):
        self.roles['roles']['rfc-reviewer']['max_turns'] = 400
        self.assertTrue(self.findings())

    def test_old_cli_floor_is_rejected(self):
        self.routing['providers']['claude']['minimum_cli_version'] = '2.1.219'
        self.assertTrue(self.findings())

    def test_higher_existing_cli_floor_is_allowed(self):
        self.routing['providers']['claude']['minimum_cli_version'] = '2.2.0'
        self.assertEqual(self.findings(), [])

    def test_version_format_is_strict(self):
        with self.assertRaises(ValueError):
            version('latest')

if __name__ == '__main__':
    unittest.main()
