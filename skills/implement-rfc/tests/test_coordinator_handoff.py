import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from coordinator_handoff import continuation, validate_return


class NativeReturnTests(unittest.TestCase):
    def setUp(self):
        self.reply = dict(schema="implement-rfc.milestone-return.v1", run_id="run",
                          dispatch_id="dispatch-1", producer_id="integrator-1",
                          mandate_revision="mandate-1", milestone="add/list",
                          disposition="milestone-complete", summary="ordered catalog",
                          candidate_revision="a" * 40, handoff_ref="docs/issues/closeout.md",
                          ownership="quiescent", next_objective="rename",
                          required_pending=[], evidence_refs=["docs/check.md"])
        self.assignment = {k: self.reply[k] for k in
                           ("run_id", "dispatch_id", "producer_id", "mandate_revision", "milestone")}

    def test_two_generations_and_same_milestone_correction(self):
        partial = dict(self.reply, disposition="continue-milestone")
        self.assertEqual(continuation(partial, self.assignment, execution="quiescent")["action"],
                         "resume-integrator")
        first = continuation(self.reply, self.assignment, execution="quiescent")
        self.assertEqual(first["action"], "fresh-integrator")
        second = dict(self.reply, producer_id="integrator-2", dispatch_id="dispatch-2", milestone="rename",
                      disposition="pack-complete", next_objective=None)
        assignment = dict(self.assignment, producer_id="integrator-2", dispatch_id="dispatch-2", milestone="rename")
        self.assertEqual(continuation(second, assignment, execution="quiescent")["action"], "report-closeout")
        self.assertEqual(first["engineering_acceptance"], "not-evaluated")

    def test_result_is_not_native_termination(self):
        self.assertEqual(continuation(self.reply, self.assignment, execution="active")["action"], "wait")
        self.assertEqual(continuation(self.reply, self.assignment, execution="unknown")["action"], "reconcile")

    def test_stale_duplicate_and_cancelled(self):
        first = continuation(self.reply, self.assignment, execution="quiescent")
        self.assertEqual(continuation(self.reply, self.assignment, execution="quiescent",
                                      consumed=[list(first["consume_key"])])["action"], "ignore-duplicate")
        current = dict(self.assignment, mandate_revision="amended")
        self.assertEqual(continuation(self.reply, current, execution="quiescent")["action"], "ignore-stale")
        self.assertEqual(continuation(self.reply, self.assignment, execution="active", cancelled=True)["action"], "stop")

    def test_no_false_completion_or_outside_handoff(self):
        bad = dict(self.reply, disposition="pack-complete", required_pending=["native Claude"])
        self.assertTrue(validate_return(bad))
        self.assertTrue(validate_return(dict(self.reply, handoff_ref="../other/closeout.md")))
        self.assertTrue(validate_return(dict(self.reply, schema="unknown")))

    def test_invalid_collections_refuse_without_exception(self):
        for field in ("evidence_refs", "required_pending", "disposition"):
            value = copy.deepcopy(self.reply)
            value[field] = [{}]
            self.assertTrue(validate_return(value))


if __name__ == "__main__":
    unittest.main()
