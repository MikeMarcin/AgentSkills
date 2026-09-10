"""Execution diagnostics report recorded decisions without inventing generations."""
import copy
import unittest

import test_milestone_continuation as fixtures
from coordinator_handoff import decision_diagnostics, human_report


class MilestoneDiagnosticsTests(unittest.TestCase):
    setUp = fixtures.BoundReturnTests.setUp

    def test_matching_records_expose_actual_reason_and_unknown_index(self):
        diagnostics=decision_diagnostics(self.assignment,self.reply,'fresh-integrator')
        self.assertEqual(diagnostics['plan_id'],'demo')
        self.assertEqual(diagnostics['producer_id'],'native-one')
        self.assertEqual(diagnostics['dispatch_id'],'one')
        self.assertEqual(diagnostics['requested_reason'],'integrated-boundary')
        self.assertIsNone(diagnostics['generation_index'])
        self.assertEqual(diagnostics['economics'],'not inferred')
        report=human_report(dict(action='fresh-integrator',reason='Accepted boundary',diagnostics=diagnostics),'Public result')
        self.assertIn('Current: first — Public result',report)
        self.assertIn('generation index unknown',report)
        self.assertIn('Recorded continuation reason: integrated-boundary',report)

    def test_missing_or_stale_history_stays_unknown(self):
        for reply in ({}, [], dict(self.reply,dispatch_id='old')):
            diagnostics=decision_diagnostics(self.assignment,reply,'reconcile')
            self.assertIsNone(diagnostics['requested_reason'])
            self.assertIsNone(diagnostics['requested_detail'])
        legacy=copy.deepcopy(self.reply);legacy.pop('continuation')
        self.assertIsNone(decision_diagnostics(self.assignment,legacy,'reconcile')['requested_reason'])

    def test_assignment_report_is_compact_and_does_not_claim_completion(self):
        report=human_report(self.assignment,'Usable result')
        self.assertIn('Plan: demo',report)
        self.assertIn('Assigned: 2 obligations; 1 exits',report)
        self.assertNotIn('accepted',report)


if __name__ == '__main__':
    unittest.main()
