"""Public plan, board, evidence, and continuation use a bound external tracker."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import git


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class PersonalLifecyclePublicTests(unittest.TestCase):
    def test_paired_lane_board_refuses_switched_source_before_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            source = base / "source"
            source.mkdir()
            git(source, "init", "-b", "main")
            git(source, "config", "user.name", "fixture")
            git(source, "config", "user.email", "fixture@example.invalid")
            (source / "product.txt").write_text("product\n")
            git(source, "add", "product.txt")
            git(source, "commit", "-m", "Initial product")
            env = {**os.environ, "IMPLEMENT_RFC_HOME": str(base / "home")}

            def run(script, root, *args, expected=0):
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script),
                    "--repo-root", str(root), *args], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return json.loads(result.stdout)

            bound = run("personal_tracker.py", source, "--json", "init")
            tracker = Path(bound["workflow_root"])
            rfc = tracker / "docs/rfcs/RFC-PRS-0001-demo.md"
            card = tracker / "docs/issues/10-backlog/PRS-0001-demo.md"
            card.parent.mkdir(parents=True)
            rfc.write_text('---\nid: "RFC-PRS-0001"\ntitle: "Demo"\nstatus: "Accepted"\n---\n')
            card.write_text('---\nschema: "implement-rfc.card.v1"\nid: "PRS-0001"\n'
                'title: "Demo"\nstatus: "Backlog"\nrfcs: ["RFC-PRS-0001"]\n'
                'depends_on: []\n---\n\n## Acceptance\n\n- Demonstrate a paired lane.\n')
            (tracker / "docs/issues/NEXT_ID").write_text("PRS-0002\n")
            git(tracker, "add", "docs")
            git(tracker, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-m", "Private intake")
            lane = base / "lane"
            git(source, "worktree", "add", "-b", "feature", str(lane))
            pair = run("personal_lanes.py", lane, "bind", "--tracker-branch", "records-feature")
            tracker_lane = Path(pair["local"]["workflow_root"])
            self.assertEqual(run("issue_board.py", lane, "queue", "--rfc", "RFC-PRS-0001",
                "--json")["cards"][0]["disposition"], "backlog_candidate")

            git(lane, "branch", "-m", "renamed")
            refused = run("issue_board.py", lane, "move", "PRS-0001", "--to", "20-ready",
                "--json", expected=1)
            self.assertIn("branch changed", refused["errors"][0]["reason"])
            self.assertTrue((tracker_lane / "docs/issues/10-backlog/PRS-0001-demo.md").exists())
            source_revision = git(lane, "rev-parse", "HEAD")
            tracker_revision = git(tracker_lane, "rev-parse", "HEAD")
            run("personal_lanes.py", lane, "rebind", "--source-branch", "renamed",
                "--tracker-branch", "records-feature", "--source-revision", source_revision,
                "--tracker-revision", tracker_revision)
            run("issue_board.py", lane, "move", "PRS-0001", "--to", "20-ready", "--json")
            git(tracker_lane, "add", "docs/issues")
            git(tracker_lane, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-m", "Promote private work")
            claimed = run("issue_board.py", lane, "claim", "PRS-0001", "--json")
            self.assertEqual(claimed["lane"], "30-in-progress")
            self.assertTrue((tracker / "docs/issues/10-backlog/PRS-0001-demo.md").exists())
            self.assertEqual(git(lane, "status", "--porcelain=v1", "--untracked-files=all"), "")

    def test_plan_claim_evidence_and_resume_keep_source_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            source = base / "source"
            source.mkdir()
            git(source, "init", "-b", "main")
            git(source, "config", "user.name", "fixture")
            git(source, "config", "user.email", "fixture@example.invalid")
            (source / "product.txt").write_text("product\n")
            git(source, "add", "product.txt")
            git(source, "commit", "-m", "Initial product")
            source_revision = git(source, "rev-parse", "HEAD")
            env = {**os.environ, "IMPLEMENT_RFC_HOME": str(base / "home")}

            def cli(script, *args, expected=0):
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script),
                    "--repo-root", str(source), *args], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return json.loads(result.stdout)

            bound = cli("personal_tracker.py", "--json", "init")
            tracker = Path(bound["workflow_root"])
            rfc = tracker / "docs/rfcs/RFC-PRS-0001-demo.md"
            card = tracker / "docs/issues/10-backlog/PRS-0001-demo.md"
            card.parent.mkdir(parents=True)
            rfc.write_text('---\nid: "RFC-PRS-0001"\ntitle: "Demo"\nstatus: "Accepted"\n---\n\n# Demo\n')
            card.write_text('---\nschema: "implement-rfc.card.v1"\nid: "PRS-0001"\n'
                'title: "Demo"\nstatus: "Backlog"\nrfcs: ["RFC-PRS-0001"]\n'
                'depends_on: []\n---\n\n# Demo\n\n## Acceptance\n\n- The product remains clean while private state advances.\n')
            (tracker / "docs/issues/NEXT_ID").write_text("PRS-0002\n")
            git(tracker, "add", "docs")
            git(tracker, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-m", "Add private intake")

            raw = base / "raw"
            raw.mkdir()
            (raw / "milestone-plan.json").write_text(json.dumps({
                "schema": "implement-rfc.milestone-plan.v1", "id": "demo-personal",
                "scope": {"rfcs": ["RFC-PRS-0001"], "issues": ["PRS-0001"]},
                "milestones": [{"id": "first", "outcome": "Private claim works",
                    "work": [{"issue": "PRS-0001"}], "depends_on": [],
                    "exit_criteria": ["Source remains clean after tracker claim"],
                    "boundary": "One public claim and recovery path"}]}, indent=2) + "\n")
            adopted = cli("milestone_plan.py", "adopt", "--source-root", str(raw), "--json")
            self.assertEqual(adopted["state"], "adopted")
            git(tracker, "add", "docs")
            git(tracker, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-m", "Adopt private plan")
            queue = cli("issue_board.py", "queue", "--rfc", "RFC-PRS-0001", "--json")
            self.assertEqual(queue["cards"][0]["disposition"], "backlog_candidate")
            cli("issue_board.py", "move", "PRS-0001", "--to", "20-ready", "--json")
            git(tracker, "add", "docs/issues")
            git(tracker, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-m", "Promote private work")
            claimed = cli("issue_board.py", "claim", "PRS-0001", "--json")
            self.assertEqual(claimed["lane"], "30-in-progress")
            self.assertEqual(git(source, "rev-parse", "HEAD"), source_revision)
            self.assertEqual(git(source, "status", "--porcelain=v1", "--untracked-files=all"), "")

            evidence = cli("record_evidence.py", "--criterion", "source-clean", "--",
                "git", "status", "--porcelain=v1")
            self.assertEqual(evidence["revision"], source_revision)
            self.assertEqual(evidence["evidence"]["stdout_tail"], "")
            assigned = cli("coordinator_handoff.py", "assign", "--target", "RFC-PRS-0001",
                "--run-id", "demo", "--dispatch-id", "first", "--producer-id", "native",
                "--mandate-revision", "1", "--json")
            self.assertEqual(assigned["repository_state"]["source_root"], str(source))
            self.assertEqual(assigned["repository_state"]["workflow_root"], str(tracker))
            self.assertEqual(assigned["binding"]["obligations"][0]["id"], "PRS-0001:*")
            runtime = Path(bound["runtime_root"])
            self.assertTrue(runtime.is_dir())
            (runtime / "assignment.json").write_text(json.dumps(assigned))
            (runtime / "return.json").write_text(json.dumps({
                **{k: assigned[k] for k in ("run_id", "dispatch_id", "producer_id",
                    "mandate_revision", "milestone")},
                "schema": "implement-rfc.milestone-return.v2", "disposition": "continue-milestone",
                "summary": "Claim complete; product implementation pending", "candidate_revision": source_revision,
                "handoff_ref": "docs/rfcs/RFC-PRS-0001-demo.md", "ownership": "quiescent",
                "repository_state": assigned["repository_state"],
                "next_objective": "Implement product", "required_pending": ["product work"],
                "evidence_refs": ["docs/rfcs/RFC-PRS-0001-demo.md"], "binding": assigned["binding"],
                "acceptance_records": [], "continuation": {"intent": "continue",
                    "next_milestone": "first", "reason": "current-milestone", "detail": "Product pending"}
            }))
            checked = cli("coordinator_handoff.py", "check", "--assignment", "assignment.json",
                "--return-file", "return.json", "--execution", "quiescent", "--json")
            self.assertEqual(checked["action"], "resume-integrator")
            incorrect = json.loads((runtime / "return.json").read_text())
            incorrect["repository_state"]["workflow_revision"] = "0" * 40
            (runtime / "return.json").write_text(json.dumps(incorrect))
            self.assertEqual(cli("coordinator_handoff.py", "check", "--assignment", "assignment.json",
                "--return-file", "return.json", "--execution", "quiescent", "--json",
                expected=2)["action"], "reconcile")
            incorrect["repository_state"] = assigned["repository_state"]
            (runtime / "return.json").write_text(json.dumps(incorrect))
            stale = json.loads((runtime / "return.json").read_text())
            stale["dispatch_id"] = "another-dispatch"
            (runtime / "return.json").write_text(json.dumps(stale))
            self.assertEqual(cli("coordinator_handoff.py", "check", "--assignment", "assignment.json",
                "--return-file", "return.json", "--execution", "quiescent", "--json")["action"], "ignore-stale")

            acceptance = runtime / "acceptance.json"
            acceptance.write_text(json.dumps({"approved": True, "decision": "human-pending",
                "records": [{"criterion": "source-footprint", "outcome": "pass",
                    "revision": source_revision, "evidence": {"kind": "observation",
                        "detail": "Source remained clean after claim"}},
                    {"criterion": "product-work", "outcome": "pending",
                    "revision": source_revision, "evidence": {"kind": "observation",
                        "detail": "Attended judgment remains open"}}]}))
            parked = cli("issue_board.py", "finish", "PRS-0001", "--acceptance", str(acceptance), "--json")
            self.assertEqual(parked["lane"], "40-parked")
            self.assertEqual(cli("issue_board.py", "queue", "--human-waiting", "--json")["cards"][0]["id"], "PRS-0001")
            acceptance.write_text(json.dumps({"approved": True, "decision": "done",
                "records": [{"criterion": "source-footprint", "outcome": "pass",
                    "revision": source_revision, "evidence": {"kind": "observation",
                        "detail": "Source remained clean after claim"}},
                    {"criterion": "product-work", "outcome": "pass",
                    "revision": source_revision, "evidence": {"kind": "observation",
                        "detail": "Accepted fixture result"}}]}))
            finished = cli("issue_board.py", "finish", "PRS-0001", "--acceptance", str(acceptance), "--json")
            self.assertEqual(finished["lane"], "60-done")
            self.assertEqual(cli("issue_board.py", "queue", "--rfc", "RFC-PRS-0001",
                "--history", "--json")["done_count"], 1)
            tracked = git(tracker, "ls-files").splitlines()
            self.assertFalse(any(path.endswith((".lock", ".log")) or "runtime/" in path
                for path in tracked))
            for relative in tracked:
                content = (tracker / relative).read_text()
                self.assertNotIn(str(base), content)
            audit = subprocess.run([sys.executable, "-B", str(SCRIPTS / "audit_board.py"),
                "--repo-root", str(source), "--rfc", "RFC-PRS-0001"],
                env=env, capture_output=True, text=True)
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            self.assertIn("board conforms: no violations", audit.stdout)
            self.assertEqual(git(source, "status", "--porcelain=v1", "--untracked-files=all"), "")


if __name__ == "__main__":
    unittest.main()
