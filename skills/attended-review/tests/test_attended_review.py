"""Public command paths, portable temporary fixtures and real loopback HTTP."""
import concurrent.futures
from contextlib import contextmanager
import importlib.util
import json
import re
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import urllib.error
import urllib.request

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "attended_review.py"

spec = importlib.util.spec_from_file_location("attended_under_test", SCRIPT)
review_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review_module)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "checkout"
        self.root.mkdir()
        self.registry = self.base / "registry"
        self.hosts = []
        self.addCleanup(self.cleanup_hosts)

    def cleanup_hosts(self):
        for process, root in self.hosts:
            if process.poll() is None:
                self.cli("stop", root=root, success=False)
                try:
                    process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def args(self, *args, root=None):
        return [sys.executable, "-B", str(SCRIPT), "--repo-root", str(root or self.root), "--registry", str(self.registry), *args]

    def cli(self, *args, root=None, success=True):
        process = subprocess.run(self.args(*args, root=root), capture_output=True, text=True, timeout=15)
        if success:
            self.assertEqual(process.returncode, 0, process.stderr)
            return json.loads(process.stdout)
        return process

    def candidate(self, cid="A", **fields):
        return {"id": cid, "title": f"Review {cid}", "revision": "build-1", "content": "Inspect appearance", "criteria": ["Legible at normal size"], **fields}

    def init(self, *candidates, root=None):
        path = self.base / "manifest.json"
        path.write_text(json.dumps({"schema_version": 1, "candidates": list(candidates)}))
        return self.cli("init", "--manifest", str(path), root=root)

    def init_v2(self, *candidates):
        path = self.base / "manifest-v2.json"
        path.write_text(json.dumps({"schema_version": 2, "candidates": list(candidates)}))
        return self.cli("init", "--manifest", str(path))

    def audio(self, cid="A", **fields):
        return self.candidate(cid, question_type="audio", comparison_group="death",
            audio={"url": "data:audio/wav;base64,UklGRg==", "purpose": "Death cue",
                   "scope": "Creative fit only", "context": "Once on death"}, **fields)

    def feedback_packet(self, state, cid="A", feedback_id="feedback-1", **fields):
        item = next(c for c in state["candidates"] if c["id"] == cid)
        return {"schema_version": 2, "session": state["session"], "decisions": [],
                "feedback": [{"candidate": cid, "fingerprint": item["fingerprint"],
                              "feedback_id": feedback_id, "note": "Consider for pain", **fields}]}

    def test_v2_unanswered_feedback_survives_restart_and_partial_handback(self):
        self.init_v2(self.audio(), self.audio("B"), self.candidate("brief"))
        state = self.cli("prepare")
        payload = self.feedback_packet(state, note="Reject for death; consider for pain")
        self.assertEqual(self.intake(payload)["feedback_saved"], ["A"])
        self.assertEqual(self.intake(payload)["feedback_saved"], [])
        self.cli("pause")
        current = self.cli("status", "--after", str(state["sequence"]))
        a = next(c for c in current["candidates"] if c["id"] == "A")
        self.assertIsNone(a["decision"])
        self.assertIn("consider for pain", a["feedback"]["note"])
        self.assertTrue(any(e["kind"] == "feedback" for e in current["events"]))
        result = self.cli("hand-back")
        self.assertEqual(result["decided"], [])
        self.assertEqual(result["feedback_pending"], ["A"])
        self.assertEqual(set(result["pending"]), {"A", "B", "brief"})
        self.assertTrue(all(c["protected"] for c in self.cli("status")["candidates"]))

    def test_v2_feedback_revision_retains_answer_and_withdrawal_retains_feedback(self):
        self.init_v2(self.audio(), self.audio("B")); state = self.cli("prepare")
        decision = self.decision(state, outcome="reject", note="Reject for death")
        decision["schema_version"] = 2
        self.intake(decision)
        self.intake(self.feedback_packet(state, feedback_id="revised", note="Reject for death; consider for pain"))
        item = next(c for c in self.cli("status", "--full")["candidates"] if c["id"] == "A")
        self.assertEqual(item["decision"]["outcome"], "reject")
        self.assertEqual(item["decision"]["note"], "Reject for death; consider for pain")
        self.assertTrue(any(d.get("note") == "Reject for death" for d in item["superseded"]))
        # Replaying the original answer after a feedback edit cannot revert it.
        self.assertEqual(self.intake(decision)["accepted"], [])
        withdrawal = self.decision(state, outcome="withdrawn", decision_id="withdraw-v2")
        withdrawal["schema_version"] = 2
        self.intake(withdrawal)
        self.assertEqual(self.intake(withdrawal)["accepted"], [])
        item = next(c for c in self.cli("status", "--full")["candidates"] if c["id"] == "A")
        self.assertIsNone(item["decision"])
        self.assertIn("consider for pain", item["feedback"]["note"])
        self.intake(self.feedback_packet(state, feedback_id="clear", note="", attachments=[]))
        item = next(c for c in self.cli("status", "--full")["candidates"] if c["id"] == "A")
        self.assertEqual(item["feedback"]["note"], "")
        self.assertTrue(any("pain" in f.get("note", "") for f in item["feedback_history"]))

    def test_v2_atomic_mixed_intake_retry_and_stale_feedback_conflict(self):
        self.init_v2(self.audio(), self.audio("B")); state = self.cli("prepare")
        packet = self.feedback_packet(state, expected_feedback_id=None)
        packet["decisions"] = self.decision(state, "B")["decisions"]
        packet["feedback"].append({"candidate": "missing"})
        self.assertEqual(self.intake(packet, success=False).returncode, 1)
        self.assertTrue(all(c["feedback"] is None and c["decision"] is None for c in self.cli("status")["candidates"]))
        packet["feedback"].pop(); self.intake(packet)
        self.assertEqual(self.intake(packet)["accepted"], [])
        old = self.feedback_packet(state, feedback_id="older-tab", expected_feedback_id=None, note="Stale edit")
        self.assertEqual(self.intake(old, success=False).returncode, 1)
        self.assertIn("Consider for pain", json.dumps(self.cli("status")))
        altered = self.feedback_packet(state, note="ID reused with different words")
        self.assertEqual(self.intake(altered, success=False).returncode, 1)

    def test_v2_audio_material_identity_and_legacy_identity_remain_distinct(self):
        legacy = self.candidate()
        # Captured from the pre-implementation helper at RFC_BASE_SHA 7cc31bb.
        expected = "be5163de18a49e2a5ff8dbf9fb6750939090980c8e24ee5382eff0040be94f71"
        self.init(legacy); state = self.cli("prepare")
        self.assertEqual(state["candidates"][0]["fingerprint"], expected)
        self.intake(self.decision(state))  # Existing version-1 import.
        self.cli("resume-development", "--all")
        candidate = self.audio(); self.init_v2(candidate); old = self.cli("prepare")
        self.intake(self.feedback_packet(old))
        changed = {**candidate, "comparison_group": "another-navigation-group"}
        self.assertEqual(self.init_v2(changed)["candidates"][0]["fingerprint"], old["candidates"][0]["fingerprint"])
        for field, value in (("purpose", "Pain cue"), ("url", "data:audio/wav;base64,bmV3")):
            replacement = {**changed, "audio": {**changed["audio"], field: value}}
            path = self.base / "replacement.json";path.write_text(json.dumps({"schema_version": 2, "candidates": [replacement]}))
            self.assertEqual(self.cli("init", "--manifest", str(path), success=False).returncode, 1)
            self.cli("resume-development", "--candidate", "A")
            self.init_v2(replacement); self.cli("prepare")
            self.assertEqual(self.intake(self.feedback_packet(old), success=False).returncode, 1)
            self.assertIsNone(self.cli("status")["candidates"][0]["feedback"])
            changed = replacement
        self.assertTrue(review_module.Session(self.root, self.registry).load()["history"])

    def test_v2_http_feedback_diagnostics_and_handback_only_wait(self):
        self.init_v2(self.audio(), self.audio("B")); state = self.cli("prepare")
        _, host = self.host()
        packet = self.feedback_packet(state)
        packet["diagnostics"] = [{"candidate": "A", "fingerprint": state["candidates"][0]["fingerprint"],
                                  "diagnostic_id": "decode-1", "message": "Could not decode clip"}]
        with self.handback_waiter(state["sequence"]) as waiter:
            with self.request(host, "/api/decisions", packet) as response:
                self.assertEqual(json.load(response)["feedback_saved"], ["A"])
            with self.assertRaises(subprocess.TimeoutExpired):
                waiter.communicate(timeout=0.3)
            self.cli("hand-back")
            out, err = waiter.communicate(timeout=5)
        self.assertEqual(waiter.returncode, 0, err)
        self.assertEqual(json.loads(out)["events"][0]["feedback_pending"], ["A"])
        self.cli("stop")
        current = self.cli("status")
        self.assertIsNone(current["candidates"][0]["decision"])
        self.assertEqual(current["candidates"][0]["playback_errors"][0]["message"], "Could not decode clip")
        self.assertEqual(self.intake(packet)["diagnostics_saved"], [])

    def test_v2_offline_page_packet_imports_through_public_cli(self):
        import shutil
        node = shutil.which("node")
        if not node:
            self.skipTest("Node is used only for deterministic page tests, not the runtime")
        self.init_v2(self.audio(), self.audio("B")); self.cli("prepare")
        snapshot = self.cli("status", "--full")
        snapshot_path = self.base / "snapshot.json";snapshot_path.write_text(json.dumps(snapshot))
        packet_path = self.base / "offline-export.json"
        result = subprocess.run([node, str(SCRIPT.parents[1] / "tests/review_page.test.js"),
                                 str(snapshot_path), str(packet_path)], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("import", "--file", str(packet_path))
        self.assertEqual(result["feedback_saved"], ["A"])
        self.assertEqual(result["accepted"], [])
        self.assertEqual(self.cli("import", "--file", str(packet_path))["feedback_saved"], [])
        self.assertIsNone(self.cli("status")["candidates"][0]["decision"])

    def test_live_page_keeps_the_note_across_accept_and_reject(self):
        import shutil
        node = shutil.which("node")
        if not node:
            self.skipTest("Node is used only for deterministic page tests, not the runtime")
        names = ("typed", "quick", "switched", "revised", "after")
        self.init_v2(*(self.candidate(name) for name in names)); self.cli("prepare")
        _, host = self.host()
        result = subprocess.run([node, str(SCRIPT.parents[1] / "tests/review_page.test.js"), "--host",
                                 f"http://127.0.0.1:{host['port']}", host["token"]],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = {c["id"]: c for c in self.cli("status", "--full")["candidates"]}
        expected = {"typed": ("reject", "Limit the edit to the selected lines"),
                    "quick": ("reject", "Rejected before the save timer ran"),
                    "switched": ("reject", "On reflection, only the selected lines"),
                    "revised": ("reject", "Second thought"),
                    "after": ("accept", "Written after rejecting, then revised")}
        for name, (outcome, note) in expected.items():
            self.assertEqual((saved[name]["decision"]["outcome"], saved[name]["decision"]["note"]), (outcome, note), name)
            self.assertEqual(saved[name]["feedback"]["note"], note, name)

    def test_live_page_answers_and_moves_on_over_loopback_and_tailnet_listener(self):
        # The owner's tailnet review: Accept/Reject questions with inline images
        # that make the session megabytes long. Each answer must save and leave
        # Accept, Reject and Next usable without reading the images again.
        import shutil
        node = shutil.which("node")
        if not node:
            self.skipTest("Node is used only for deterministic page tests, not the runtime")
        image = "data:image/png;base64," + "QUFB" * 200000
        names = [f"{prefix}-{n}" for prefix in ("loop", "tail") for n in (1, 2, 3)]
        self.init_v2(*(self.candidate(name, media=[{"kind": "image", "url": image, "label": name}]) for name in names))
        self.cli("prepare")
        page = str(SCRIPT.parents[1] / "tests/review_page.test.js")
        _, host = self.host()
        result = subprocess.run([node, page, "--answers", f"http://127.0.0.1:{host['port']}", host["token"], "loop"],
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.cli("stop")
        fake, executable, env = self.fake_tailscale()
        _, tailnet = self.tailhost(executable, env, port=8443)
        active = json.loads((fake / "config.json").read_text())
        target = active["Foreground"][tailnet["tailscale"]["foreground_session"]]["Web"]["review.example.ts.net:8443"]["Handlers"]["/"]["Proxy"]
        result = subprocess.run([node, page, "--answers", target, tailnet["token"], "tail",
                                 "review.example.ts.net:8443", "https://review.example.ts.net:8443"],
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("through the tailnet review listener", result.stdout)
        # A query string does not open the local control endpoints to the tailnet.
        external = {"Host": "review.example.ts.net:8443", "Origin": "https://review.example.ts.net:8443"}
        for endpoint in ("/api/ping?token=1", "/api/stop?now=1"):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.request({**tailnet, "port": int(target.rsplit(":", 1)[1])}, endpoint,
                             {} if "stop" in endpoint else None, **external)
            self.assertEqual(caught.exception.code, 403, endpoint); caught.exception.close()
        saved = {c["id"]: (c["decision"] or {}).get("outcome") for c in self.cli("status")["candidates"]}
        for prefix in ("loop", "tail"):
            self.assertEqual([saved[f"{prefix}-{n}"] for n in (1, 2, 3)], ["accept", "reject", "reject"], prefix)

    def test_page_status_polls_short_and_leaves_out_held_material(self):
        image = "data:image/png;base64," + "QUFB" * 1000
        self.init_v2(self.candidate(media=[{"kind": "image", "url": image}]), self.audio("B"))
        state = self.cli("prepare")
        _, host = self.host()
        self.intake(self.decision(state))
        self.intake(self.decision(state, outcome="reject", decision_id="verdict-A-revised"))
        with self.request(host, "/api/status") as response:
            full = json.load(response)
        held = {c["id"]: c for c in full["candidates"]}
        self.assertEqual(held["A"]["media"][0]["url"], image)
        with self.request(host, f"/api/status?after={full['sequence']}") as response:
            self.assertEqual(json.load(response), {"session": full["session"], "sequence": full["sequence"], "unchanged": True})
        with self.request(host, f"/api/status?material=omit&after={full['sequence'] - 1}") as response:
            lean = {c["id"]: c for c in json.load(response)["candidates"]}
        self.assertEqual(lean["A"]["material_omitted"], ["media"])
        self.assertEqual(lean["B"]["material_omitted"], ["audio"])
        for key in ("media", "audio", "decision_history", "feedback_history", "superseded"):
            self.assertNotIn(key, lean["A"])
        self.assertEqual(lean["A"]["decision"]["outcome"], "reject")
        self.assertEqual(lean["A"]["fingerprint"], held["A"]["fingerprint"])
        for query in ("material=all", "after=-1", "after=x", "after=1&after=2", "other=1"):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.request(host, "/api/status?" + query)
            self.assertEqual(caught.exception.code, 400, query); caught.exception.close()

    def test_v2_formats_refuse_silent_loss_and_keep_bounds(self):
        self.init(self.candidate()); state = self.cli("prepare")
        packet = self.feedback_packet(state);packet["schema_version"] = 1
        self.assertEqual(self.intake(packet, success=False).returncode, 1)
        for invalid in (self.audio(options=["A", "B"]), self.candidate(question_type="audio")):
            path = self.base / "invalid.json";path.write_text(json.dumps({"schema_version": 2, "candidates": [invalid]}))
            self.assertEqual(self.cli("init", "--manifest", str(path), success=False).returncode, 1)
        packet = self.feedback_packet(state, attachments=[{"name": "bad", "data": "data:image/png;base64," + "a" * (4 * 1024 * 1024)}])
        self.assertEqual(self.intake(packet, success=False).returncode, 1)
        old_path = self.root / ".mask/attended-review/session.json"
        old = json.loads(old_path.read_text());old["schema_version"] = 1
        old.pop("runtime_format", None);old.pop("minimum_helper_version", None)
        old_path.write_text(json.dumps(old));before = old_path.read_bytes()
        self.cli("status");self.assertEqual(old_path.read_bytes(), before)
        self.intake(self.feedback_packet(state))
        self.assertEqual(json.loads(old_path.read_text())["runtime_format"], "attended-review.state.v2")

    def test_external_state_keeps_preparation_and_protection_on_source(self):
        state = self.base / "external"
        manifest = self.base / "external-manifest.json"
        candidate = self.candidate(paths=["product.txt"], prepare={"argv": [sys.executable, "-c", "from pathlib import Path; assert Path('product.txt').read_text() == 'source'"]})
        (self.root / "product.txt").write_text("source")
        manifest.write_text(json.dumps({"schema_version": 1, "candidates": [candidate]}))
        self.cli("--state", str(state), "init", "--manifest", str(manifest))
        self.cli("--state", str(state), "prepare")
        conflicts = self.cli("--state", str(state), "conflicts", "--paths", "product.txt")
        self.assertIn("protected paths", json.dumps(conflicts))
        self.assertTrue((state / "session.json").exists())
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["product.txt"])
        other = self.base / "other"; other.mkdir()
        result = self.cli("--state", str(state), "init", "--manifest", str(manifest), root=other, success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another source checkout", result.stderr)
        result = self.cli("--state", str(self.root / "state"), "status", success=False)
        self.assertNotEqual(result.returncode, 0)

    def test_external_state_rejects_other_source_worktree_and_git_metadata(self):
        main = self.base / "git-main"
        lane = self.base / "git-lane"
        main.mkdir()
        for args in (("init", "-b", "main"), ("config", "user.name", "fixture"),
                     ("config", "user.email", "fixture@example.invalid")):
            subprocess.run(["git", "-C", str(main), *args], check=True, capture_output=True)
        (main / "README.md").write_text("source\n")
        subprocess.run(["git", "-C", str(main), "add", "README.md"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(main), "commit", "-m", "source"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(main), "worktree", "add", "-b", "lane", str(lane)], check=True, capture_output=True)
        manifest = self.base / "worktree-manifest.json"
        manifest.write_text(json.dumps({"schema_version": 1, "candidates": [self.candidate()]}))
        for location in (main / ".git" / "private-review-state", main / "review-state"):
            result = self.cli("--state", str(location), "--registry", str(self.base / "registry"),
                              "init", "--manifest", str(manifest), root=lane, success=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(location.exists())

    def decision(self, state, cid="A", **fields):
        candidate = next(c for c in state["candidates"] if c["id"] == cid)
        return {"schema_version": 1, "session": state["session"], "decisions": [{"candidate": cid, "fingerprint": candidate["fingerprint"], "decision_id": "verdict-"+cid, "outcome": "accept", **fields}]}

    def intake(self, value, success=True):
        path = self.base / "decisions.json"
        path.write_text(json.dumps(value))
        return self.cli("import", "--file", str(path), success=success)

    def host(self, root=None):
        process = subprocess.Popen(self.args("serve", root=root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.hosts.append((process, root))
        value = json.loads(process.stdout.readline())
        return process, value

    def request(self, host, path, value=None, **headers):
        req = urllib.request.Request(f"http://127.0.0.1:{host['port']}{path}", data=None if value is None else json.dumps(value).encode(), headers={"Authorization": "Bearer "+host["token"], "Origin": f"http://127.0.0.1:{host['port']}", **headers})
        return urllib.request.urlopen(req, timeout=3)

    def test_partial_import_persistence_and_events(self):
        self.init(self.candidate(), self.candidate("B"))
        state = self.cli("prepare")
        result = self.intake(self.decision(state))
        self.assertEqual(result["accepted"], ["A"])
        self.assertEqual(self.intake(self.decision(state))["accepted"], [])
        current = self.cli("status", "--after", str(state["sequence"]))
        self.assertEqual(len(current["events"]), 1)
        self.assertEqual(current["events"][0]["kind"], "decision")
        self.assertIsNone(next(c for c in current["candidates"] if c["id"] == "B")["decision"])
        # A reviewer who pressed the wrong button says so; the verdict they land
        # on is the record and the one they replaced is kept beside it.
        self.assertEqual(self.intake(self.decision(state, outcome="reject", decision_id="verdict-A2"))["accepted"], ["A"])
        after = self.cli("status", "--full")
        decided = next(c for c in after["candidates"] if c["id"] == "A")
        self.assertEqual(decided["decision"]["outcome"], "reject")
        self.assertEqual([v["outcome"] for v in decided["superseded"]], ["accept"])

    def test_a_verdict_carries_its_note_and_images_and_can_be_withdrawn(self):
        self.init(self.candidate())
        state = self.cli("prepare")
        image = "data:image/png;base64,iVBORw0KGgo="
        self.intake(self.decision(state, outcome="reject", note="the box is unreadable",
                                  attachments=[{"name": "shot.png", "data": image}]))
        recorded = next(c for c in self.cli("status", "--full")["candidates"] if c["id"] == "A")["decision"]
        self.assertEqual(recorded["note"], "the box is unreadable")
        self.assertEqual(recorded["attachments"], [{"name": "shot.png", "data": image}])
        # Withdrawing leaves the candidate undecided and keeps what was said.
        self.intake(self.decision(state, outcome="withdrawn", decision_id="withdraw-A"))
        cleared = next(c for c in self.cli("status", "--full")["candidates"] if c["id"] == "A")
        self.assertIsNone(cleared["decision"])
        self.assertEqual(cleared["superseded"][-1]["note"], "the box is unreadable")
        self.assertEqual(self.intake(self.decision(state, decision_id="verdict-A3"))["accepted"], ["A"])
        self.assertEqual(next(c for c in self.cli("status")["candidates"] if c["id"] == "A")["decision"]["outcome"], "accept")
        # An attachment that is not an inline image, or too many, is refused.
        self.assertEqual(self.intake(self.decision(state, decision_id="bad-1", attachments=[{"name": "n", "data": "https://example.test/x.png"}]), success=False).returncode, 1)
        self.assertEqual(self.intake(self.decision(state, decision_id="bad-2", attachments=[{"name": str(i), "data": image} for i in range(5)]), success=False).returncode, 1)

    def test_handing_back_tells_the_driver_what_was_decided_and_what_was_not(self):
        self.init(self.candidate(), self.candidate("B"))
        state = self.cli("prepare")
        self.intake(self.decision(state, outcome="reject", note="not yet"))
        result = self.cli("hand-back")
        self.assertEqual(result["decided"], ["A"])
        self.assertEqual(result["pending"], ["B"])
        after = self.cli("status", "--after", str(state["sequence"]))
        self.assertIsNotNone(after["handed_back"])
        self.assertEqual(after["events"][-1]["kind"], "handed-back")
        # Handing back decides nothing: B is still open and A keeps its answer.
        self.assertIsNone(next(c for c in after["candidates"] if c["id"] == "B")["decision"])
        self.assertEqual(next(c for c in after["candidates"] if c["id"] == "A")["decision"]["note"], "not yet")

    def test_wait_wakes_the_driver_on_hand_back_or_decision_and_not_before(self):
        self.init(self.candidate(), self.candidate("B"))
        state = self.cli("prepare")
        # Nothing has happened: a bounded wait gives up and names the sequence it watched.
        quiet = self.cli("wait", "--after", str(state["sequence"]), "--timeout", "0.3", success=False)
        self.assertEqual(quiet.returncode, 1)
        self.assertEqual(json.loads(quiet.stderr)["sequence"], state["sequence"])
        # Events older than the cursor never satisfy it.
        self.intake(self.decision(state))
        later = self.cli("status")
        self.assertEqual(self.cli("wait", "--after", str(later["sequence"]), "--timeout", "0.3", success=False).returncode, 1)
        # A driver blocked in wait is released by the hand-back click, with the event in hand,
        # printed as one line so a host turns it into one notification.
        process = subprocess.Popen(self.args("wait", "--after", str(later["sequence"]), "--timeout", "10"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            time.sleep(0.5)
            self.assertIsNone(process.poll())
            self.cli("hand-back")
            out, err = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
        self.assertEqual(process.returncode, 0, err)
        self.assertEqual(out.count("\n"), 1)
        woke = json.loads(out)
        self.assertEqual([e["kind"] for e in woke["events"]], ["handed-back"])
        self.assertEqual(woke["events"][0]["decided"], ["A"])
        self.assertIsNotNone(woke["handed_back"])
        # A decision alone also wakes the default wait; a wait for hand-back only ignores it.
        process = subprocess.Popen(self.args("wait", "--after", str(woke["sequence"]), "--timeout", "10"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            time.sleep(0.5)
            self.intake(self.decision(later, "B"))
            out, err = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
        self.assertEqual(process.returncode, 0, err)
        decided = json.loads(out)
        self.assertEqual([(e["kind"], e["candidate"]) for e in decided["events"]], [("decision", "B")])
        self.assertEqual(self.cli("wait", "--after", str(woke["sequence"]), "--kind", "handed-back", "--timeout", "0.3", success=False).returncode, 1)

    @contextmanager
    def handback_waiter(self, after, root=None):
        process = subprocess.Popen(
            self.args("wait", "--after", str(after), "--kind", "handed-back", "--timeout", "10", root=root),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            yield process
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
            process.stdout.close()
            process.stderr.close()

    def test_handback_only_wait_ignores_old_handback_and_partial_decision(self):
        self.init(self.candidate(), self.candidate("B"))
        self.cli("prepare")
        self.cli("hand-back")
        state = self.cli("start")
        with self.handback_waiter(state["sequence"]) as process:
            with self.assertRaises(subprocess.TimeoutExpired):
                process.communicate(timeout=0.3)
            self.intake(self.decision(state))
            with self.assertRaises(subprocess.TimeoutExpired):
                process.communicate(timeout=0.3)
            self.cli("hand-back")
            out, err = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0, err)
        woke = json.loads(out)
        self.assertEqual(woke["session"], state["session"])
        self.assertEqual([e["kind"] for e in woke["events"]], ["handed-back"])
        self.assertEqual(woke["events"][0]["decided"], ["A"])
        self.assertEqual(woke["events"][0]["pending"], ["B"])
        self.assertEqual(out.count("\n"), 1)

    def test_cancelled_wait_preserves_decisions_protection_and_can_resume(self):
        self.init(self.candidate(paths=["product.txt"], resources=["install:fixture"]), self.candidate("B"))
        state = self.cli("prepare")
        self.intake(self.decision(state))
        before = self.cli("status")
        with self.handback_waiter(before["sequence"]) as process:
            with self.assertRaises(subprocess.TimeoutExpired):
                process.communicate(timeout=0.3)
            process.terminate()
            process.communicate(timeout=5)
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(self.cli("status"), before)
        self.assertIn("protected paths", json.dumps(self.cli("conflicts", "--paths", "product.txt")))
        with self.handback_waiter(before["sequence"]) as resumed:
            self.cli("hand-back")
            out, err = resumed.communicate(timeout=5)
        self.assertEqual(resumed.returncode, 0, err)
        self.assertEqual(json.loads(out)["events"][0]["decided"], ["A"])

    def test_wait_does_not_consume_another_checkout_handback(self):
        other = self.base / "other-checkout"
        other.mkdir()
        self.init(self.candidate())
        state = self.cli("prepare")
        self.init(self.candidate("B"), root=other)
        other_state = self.cli("prepare", root=other)
        self.assertNotEqual(state["session"], other_state["session"])
        with self.handback_waiter(state["sequence"]) as process:
            self.cli("hand-back", root=other)
            with self.assertRaises(subprocess.TimeoutExpired):
                process.communicate(timeout=0.3)
            self.cli("hand-back")
            out, err = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0, err)
        self.assertEqual(json.loads(out)["session"], state["session"])
        self.assertEqual(json.loads(out)["events"][0]["pending"], ["A"])

    def test_new_work_clears_the_previous_hand_back(self):
        self.init(self.candidate())
        state = self.cli("prepare")
        self.intake(self.decision(state, outcome="reject", decision_id="verdict-A-revised"))
        self.cli("hand-back")
        self.assertIsNotNone(self.cli("status")["handed_back"])
        # Releasing the candidate for more development means the queue will change.
        self.cli("resume-development", "--candidate", "A")
        self.assertIsNone(self.cli("status")["handed_back"])
        self.cli("hand-back")
        # A new revision is work the reviewer has not seen.
        self.init(self.candidate(revision="build-2"))
        self.assertIsNone(self.cli("status")["handed_back"])
        self.cli("hand-back")
        self.cli("prepare")
        self.assertIsNone(self.cli("status")["handed_back"])
        self.cli("hand-back")
        # Starting review again, or adding a candidate, likewise.
        self.cli("start")
        self.assertIsNone(self.cli("status")["handed_back"])
        self.cli("hand-back")
        self.init(self.candidate(revision="build-2"), self.candidate("B"))
        self.assertIsNone(self.cli("status")["handed_back"])
        # Re-supplying unchanged material is not new work.
        self.cli("hand-back")
        self.init(self.candidate(revision="build-2"), self.candidate("B"))
        self.assertIsNotNone(self.cli("status")["handed_back"])

    def test_a_candidate_offers_the_values_it_asks_to_be_pasted(self):
        self.init({**self.candidate(), "copy": [{"label": "Pull request", "value": "https://example.test/owner/name/pull/7"}]})
        self.cli("prepare")
        page = self.base / "copy.html"
        self.cli("html", "--output", str(page))
        embedded = json.loads(re.search(r"const embedded=(\{.*?\});\n", page.read_text(), re.S).group(1).replace("\\u003c", "<"))
        self.assertEqual(embedded["candidates"][0]["copy"][0]["value"], "https://example.test/owner/name/pull/7")
        # A value without a label, or an empty one, is refused.
        path = self.base / "bad.json"
        path.write_text(json.dumps({"schema_version": 1, "candidates": [{**self.candidate("C"), "copy": [{"value": "x"}]}]}))
        self.assertEqual(self.cli("init", "--manifest", str(path), success=False).returncode, 1)

    def test_the_offline_file_says_when_it_was_written_and_a_launch_command_reaches_it(self):
        self.init({**self.candidate(), "launch": {"label": "Open the build", "command": "open /Applications/Thing.app"}})
        self.cli("prepare")
        page = self.base / "review.html"
        self.cli("html", "--output", str(page))
        text = page.read_text()
        embedded = json.loads(re.search(r"const embedded=(\{.*?\});\n", text, re.S).group(1).replace("\\u003c", "<"))
        self.assertRegex(embedded["generated_at"], r"^\d{4}-\d\d-\d\dT")
        self.assertEqual(embedded["candidates"][0]["launch"], {"label": "Open the build", "command": "open /Applications/Thing.app"})
        self.assertIn("This file was written at", text)

    def test_same_checkout_drivers_attach_and_hosts_stop_independently(self):
        self.init(self.candidate()); self.cli("prepare")
        p1, h1 = self.host()
        p2, h2 = self.host()
        p2.wait(timeout=4)
        self.assertTrue(h2["attached"])
        self.assertEqual(h1["port"], h2["port"])
        other = self.base / "other"; other.mkdir()
        self.init(self.candidate(), root=other)
        p3, h3 = self.host(root=other)
        self.assertNotEqual(h1["port"], h3["port"])
        self.cli("stop"); p1.wait(timeout=4)
        with self.request(h3, "/api/status") as r:
            self.assertEqual(r.status, 200)
        self.assertIsNone(p3.poll())

    def test_http_intake_without_driver_and_security(self):
        self.init(self.candidate()); state = self.cli("prepare")
        _, host = self.host()
        with self.request(host, "/api/decisions", self.decision(state)) as response:
            self.assertEqual(json.load(response)["accepted"], ["A"])
        for headers in ({"Authorization": "Bearer wrong"}, {"Origin": "https://evil.invalid"}, {"Host": "evil.invalid"}):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.request(host, "/api/decisions", self.decision(state), **headers)
            self.assertEqual(caught.exception.code, 403)
            caught.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request(host, "/api/prepare", {})
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()
        self.cli("stop")
        self.assertTrue(self.cli("status")["candidates"][0]["decision"])

    def fake_tailscale(self, config=None, mode=""):
        if os.name == "nt":
            self.skipTest("Executable fixture uses a POSIX shebang; native Windows remains unqualified")
        root = self.base / "fake-tailscale"
        root.mkdir()
        (root / "config.json").write_text(json.dumps(config or {}))
        (root / "mode").write_text(mode)
        fixture = Path(__file__).parent / "fixtures" / "fake_tailscale.py"
        executable = root / "tailscale"
        executable.write_text(f"#!{sys.executable}\n" + fixture.read_text())
        executable.chmod(0o700)
        return root, executable, {**os.environ, "FAKE_TAILSCALE_ROOT": str(root)}

    def tailhost(self, executable, env, root=None, port=None, script=SCRIPT):
        args = self.args("serve", "--tailscale", "--tailscale-bin", str(executable), root=root)
        args[2] = str(script)
        if port is not None:
            args += ["--tailscale-port", str(port)]
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        self.hosts.append((process, root))
        value = json.loads(process.stdout.readline())
        return process, value

    def test_tailscale_isolated_review_listener_partial_intake_and_local_control(self):
        fake, executable, env = self.fake_tailscale({"TCP": {"443": {"HTTPS": True}},
            "Web": {"review.example.ts.net:443": {"Handlers": {"/existing": {"Text": "keep"}}}}})
        original = json.loads((fake / "config.json").read_text())
        self.init(self.candidate(), self.candidate("B")); state = self.cli("prepare")
        process, host = self.tailhost(executable, env, port=8443)
        self.assertTrue(host["url"].startswith("https://review.example.ts.net:8443/#token="))
        self.assertTrue(host["local_url"].startswith("http://127.0.0.1:"))
        active = json.loads((fake / "config.json").read_text())
        target = active["Foreground"][host["tailscale"]["foreground_session"]]["Web"]["review.example.ts.net:8443"]["Handlers"]["/"]["Proxy"]
        proxy_port = int(target.rsplit(":", 1)[1])
        proxy = {**host, "port": proxy_port}
        external = {"Host": "review.example.ts.net:8443", "Origin": "https://review.example.ts.net:8443"}
        with self.request(proxy, "/", **external) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        with self.request(proxy, "/api/decisions", self.feedback_packet(state), **external):
            pass
        # Reconnect and read durable unanswered feedback without assigning a verdict.
        with self.request(proxy, "/api/status", **external) as response:
            current = json.load(response)
        self.assertEqual(current["candidates"][0]["feedback"]["note"], "Consider for pain")
        self.assertIsNone(current["candidates"][0]["decision"])
        for changed in ({"Host": f"127.0.0.1:{proxy_port}"}, {"Origin": "http://review.example.ts.net:8443"},
                        {"Origin": "https://evil.invalid"}, {"Authorization": "Bearer wrong"},
                        {"Host": "evil.invalid", "X-Forwarded-Host": "review.example.ts.net:8443"}):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.request(proxy, "/api/decisions", self.decision(state), **{**external, **changed})
            self.assertEqual(caught.exception.code, 403); caught.exception.close()
        req = urllib.request.Request(target + "/api/decisions", data=json.dumps(self.decision(state)).encode(),
            headers={"Host": external["Host"], "Authorization": "Bearer " + host["token"]})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(req, timeout=3)
        self.assertEqual(caught.exception.code, 403); caught.exception.close()
        for endpoint in ("/api/ping", "/api/stop"):
            for authority in (external["Host"], f"127.0.0.1:{host['port']}"):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.request(proxy, endpoint, {} if endpoint.endswith("stop") else None,
                                 **{**external, "Host": authority})
                self.assertEqual(caught.exception.code, 403); caught.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request(host, "/api/status", **external)
        self.assertEqual(caught.exception.code, 403); caught.exception.close()
        with self.request(proxy, "/api/hand-back", {}, **external) as response:
            self.assertEqual(json.load(response)["feedback_pending"], ["A"])
        self.assertTrue(self.cli("serve")["attached"])
        mismatch = subprocess.run(self.args("serve", "--tailscale", "--tailscale-port", "8444", "--tailscale-bin", str(executable)),
                                  capture_output=True, text=True, env=env, timeout=5)
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn("different transport", mismatch.stderr)
        self.assertIsNone(process.poll())
        attached_process, attached = self.tailhost(executable, env, port=8443)
        attached_process.wait(timeout=3)
        self.assertTrue(attached["attached"])
        self.cli("stop"); process.wait(timeout=4)
        self.assertEqual(process.returncode, 0, process.stderr.read())
        self.assertEqual(json.loads((fake / "config.json").read_text()), original)
        self.assertEqual(self.cli("status")["candidates"][0]["feedback"]["note"], "Consider for pain")

    def test_tailscale_collision_and_setup_failure_preserve_config_and_reap(self):
        fake, executable, env = self.fake_tailscale({"Foreground": {"other": {"TCP": {"8443": {"HTTPS": True}}}}})
        original = json.loads((fake / "config.json").read_text())
        self.init(self.candidate()); self.cli("prepare")
        args = self.args("serve", "--tailscale", "--tailscale-port", "8443", "--tailscale-bin", str(executable))
        collision = subprocess.run(args, env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(collision.returncode, 1)
        self.assertIn("already has a mapping", collision.stderr)
        self.assertEqual(json.loads((fake / "config.json").read_text()), original)
        commands = [json.loads(line) for line in (fake / "commands.jsonl").read_text().splitlines()]
        self.assertTrue(all(command == ["serve", "status", "--json"] for command in commands))
        for mode in ("consent", "fail"):
            (fake / "mode").write_text(mode)
            failed = subprocess.run(self.args("serve", "--tailscale", "--tailscale-port", "8444", "--tailscale-bin", str(executable)),
                                    env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(failed.returncode, 1, failed.stdout)
            self.assertIn("human consent" if mode == "consent" else "fixture startup failure", failed.stderr)
            if mode == "consent":
                self.assertIn("https://login.tailscale.com/f/serve?node=disposable", failed.stderr)
            self.assertEqual(json.loads((fake / "config.json").read_text()), original)
            self.assertIsNone(json.loads((self.root / ".mask/attended-review/session.json").read_text()).get("host"))

    def test_tailscale_concurrent_port_claim_refuses_and_preserves_other_owner(self):
        fake, executable, env = self.fake_tailscale(mode="race")
        self.init(self.candidate()); self.cli("prepare")
        result = subprocess.run(self.args("serve", "--tailscale", "--tailscale-port", "8443", "--tailscale-bin", str(executable)),
                                env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIn("claimed concurrently", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads((fake / "config.json").read_text()),
                         {"Foreground": {"racing-owner": {"TCP": {"8443": {"HTTPS": True}}}}})
        self.assertIsNone(self.cli("status").get("host"))

    def test_tailscale_stop_waits_for_delayed_mapping_after_child_exit(self):
        original = {"Foreground": {"other": {"TCP": {"8444": {"HTTPS": True}}}}}
        fake, executable, env = self.fake_tailscale(original, mode="delayed-cleanup")
        self.init(self.candidate()); self.cli("prepare")
        process, _ = self.tailhost(executable, env, port=8443)
        self.assertTrue(self.cli("stop")["stopped"])
        process.wait(timeout=12)
        self.assertEqual(process.returncode, 0, process.stderr.read())
        self.assertEqual(json.loads((fake / "config.json").read_text()), original)
        self.assertFalse((fake / "pending-cleanup.json").exists())
        self.assertIsNone(self.cli("status").get("host"))

    def test_tailscale_stop_interrupts_child_for_graceful_cleanup(self):
        fake, executable, env = self.fake_tailscale(mode="requires-interrupt")
        # Match the native macOS launcher, which waits for its child without exec.
        launcher = fake / "launcher"
        launcher.write_text(f'#!/bin/sh\n{shlex.quote(str(executable))} "$@"\n')
        launcher.chmod(0o700)
        self.init(self.candidate()); self.cli("prepare")
        process, _ = self.tailhost(launcher, env, port=8443)
        self.assertTrue(self.cli("stop")["stopped"])
        process.wait(timeout=12)
        self.assertEqual(process.returncode, 0, process.stderr.read())
        self.assertEqual(json.loads((fake / "config.json").read_text()), {})
        self.assertIsNone(self.cli("status").get("host"))

    def test_tailscale_stop_reports_genuinely_lingering_owned_mapping(self):
        original = {"Foreground": {"other": {"TCP": {"8444": {"HTTPS": True}}}}}
        fake, executable, env = self.fake_tailscale(original, mode="lingering-cleanup")
        self.init(self.candidate()); self.cli("prepare")
        process, host = self.tailhost(executable, env, port=8443)
        self.assertTrue(self.cli("stop")["stopped"])
        process.wait(timeout=12)
        self.assertEqual(process.returncode, 1)
        self.assertIn(f"foreground session {host['tailscale']['foreground_session']} still appears", process.stderr.read())
        current = json.loads((fake / "config.json").read_text())
        self.assertIn(host["tailscale"]["foreground_session"], current["Foreground"])
        self.assertEqual(current["Foreground"]["other"], original["Foreground"]["other"])
        commands = [json.loads(line) for line in (fake / "commands.jsonl").read_text().splitlines()]
        self.assertTrue(all(command == ["status", "--json"] or command == ["serve", "status", "--json"]
                            or command[:2] == ["serve", "--bg=false"] for command in commands))
        self.assertIsNone(self.cli("status").get("host"))

    def test_tailscale_symlinked_consumers_attach_stop_signal_and_runtime_exit(self):
        fake, executable, env = self.fake_tailscale()
        roots = [self.root, self.base / "other-consumer"]
        roots[1].mkdir()
        hosts = []
        for root in roots:
            link = root / ".agents" / "skills" / "attended-review"
            link.parent.mkdir(parents=True)
            link.symlink_to(SCRIPT.parent.parent, target_is_directory=True)
            installed = link / "scripts" / "attended_review.py"
            self.init(self.candidate(), root=root); self.cli("prepare", root=root)
            hosts.append(self.tailhost(executable, env, root=root, script=installed))
        (p1, h1), (p2, h2) = hosts
        self.assertNotEqual(h1["tailscale"]["port"], h2["tailscale"]["port"])
        self.assertNotEqual(h1["port"], h2["port"])
        self.cli("stop", root=roots[0]); p1.wait(timeout=4)
        self.assertIsNone(p2.poll())
        with self.request(h2, "/api/status") as response:
            self.assertEqual(json.load(response)["checkout"], str(roots[1].resolve()))
        p2.terminate(); p2.wait(timeout=4)
        self.assertEqual(p2.returncode, 0, p2.stderr.read())
        self.assertEqual(json.loads((fake / "config.json").read_text()), {})
        # A disappeared transport ends the local host instead of advertising a dead URL.
        (fake / "mode").write_text("runtime-exit")
        process, host = self.tailhost(executable, env)
        process.wait(timeout=4)
        self.assertEqual(process.returncode, 1)
        self.assertIn("Tailscale Serve stopped", process.stderr.read())
        self.assertIsNone(json.loads((self.root / ".mask/attended-review/session.json").read_text()).get("host"))
        self.assertEqual(json.loads((fake / "config.json").read_text()), {})

    def test_selective_release_preserves_static_and_completed_verdict(self):
        self.init(self.candidate(paths=["src/ui/**"], resources=["device:phone"]), self.candidate("B"), self.candidate("C", paths=["src/core"]))
        state = self.cli("prepare")
        self.intake(self.decision(state, "C"))
        self.cli("pause")
        self.assertTrue(all(c["protected"] for c in self.cli("status")["candidates"]))
        result = self.cli("resume-development", "--paths", "src/ui/button.py", "src/core/main.py")
        self.assertEqual(set(result["affected"]), {"A", "C"})
        current = {c["id"]: c for c in result["status"]["candidates"]}
        self.assertEqual(current["A"]["phase"], "waiting")
        self.assertTrue(current["B"]["protected"])
        self.assertIsNotNone(current["C"]["decision"])
        self.assertFalse(current["C"]["protected"])

    def test_shared_resource_conflict_and_explicit_release(self):
        self.init(self.candidate(resources=["install:product"])); self.cli("prepare")
        other = self.base / "worktree"; other.mkdir()
        self.init(self.candidate(resources=["install:product"]), root=other)
        waiting = self.cli("prepare", root=other)["candidates"][0]
        self.assertEqual(waiting["phase"], "waiting")
        self.assertIn("protected", waiting["error"])
        self.cli("resume-development", "--resources", "install:product")
        self.assertEqual(self.cli("prepare", root=other)["candidates"][0]["phase"], "ready")

    def test_same_checkout_exclusive_resource_and_versioned_static_sharing(self):
        self.init(self.candidate(resources=["phone"]), self.candidate("B", resources=["phone"]))
        current = self.cli("prepare")
        self.assertEqual([c["phase"] for c in current["candidates"]], ["ready", "waiting"])
        self.cli("resume-development", "--all")
        self.init(self.candidate(resources=["phone"], resource_versions={"phone":"immutable-install-1"}), self.candidate("B", resources=["phone"], resource_versions={"phone":"immutable-install-1"}))
        self.assertTrue(all(c["phase"] == "ready" for c in self.cli("prepare")["candidates"]))

    def test_unrelated_revision_does_not_invalidate_and_stale_packet_rejected(self):
        candidate = self.candidate(paths=["src/ui"])
        self.init(candidate); old = self.cli("prepare")
        (self.root / "unrelated.txt").write_text("Changed")
        fresh = self.init({**candidate, "metadata": {"head": "different"}})
        self.assertEqual(old["candidates"][0]["fingerprint"], fresh["candidates"][0]["fingerprint"])
        path = self.base / "manifest.json"
        path.write_text(json.dumps({"schema_version":1,"candidates":[{**candidate,"revision":"build-2"}]}))
        self.assertEqual(self.cli("init", "--manifest", str(path), success=False).returncode, 1)
        self.cli("resume-development", "--candidate", "A")
        self.init({**candidate, "revision": "build-2"}); self.cli("prepare")
        self.assertEqual(self.intake(self.decision(old), success=False).returncode, 1)

    def test_group_is_one_bounded_decision(self):
        self.init(self.candidate(options=["A", "B"]))
        state = self.cli("prepare")
        self.assertEqual(self.intake(self.decision(state), success=False).returncode, 1)
        self.assertEqual(self.intake(self.decision(state, outcome="select", selected=["A","B"]))["accepted"], ["A"])

    def test_quick_first_and_interruption_retains_ready_items(self):
        self.init(self.candidate(), self.candidate("B", prepare={"speed":"slow", "argv":[sys.executable,"-c","import time; time.sleep(10)"]}))
        current = self.cli("prepare")
        self.assertEqual([c["phase"] for c in current["candidates"]], ["ready", "waiting"])
        process = subprocess.Popen(self.args("prepare", "--include-slow"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic()+5
            while time.monotonic()<deadline:
                if any(c["phase"]=="preparing" for c in self.cli("status")["candidates"]): break
                time.sleep(.05)
            self.cli("start")
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            states = {c["id"]: c for c in json.loads(stdout)["candidates"]}
            self.assertEqual(states["A"]["phase"], "ready")
            self.assertEqual(states["B"]["phase"], "waiting")
            self.assertFalse(states["B"]["protected"])
        finally:
            if process.poll() is None: process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def test_start_cancels_remaining_preparation_commands(self):
        slow = {"argv": [sys.executable, "-c", "import time; time.sleep(10)"]}
        marker = self.root / "must-not-run.txt"
        later = {"argv": [sys.executable, "-c", "from pathlib import Path; Path('must-not-run.txt').write_text('ran')"]}
        self.init(self.candidate("A", prepare=slow), self.candidate("B", prepare=later))
        process = subprocess.Popen(self.args("prepare"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                state = self.cli("status")
                if any(c["phase"] == "preparing" for c in state["candidates"]):
                    break
                time.sleep(.05)
            else:
                self.fail("Preparation did not start")
            self.cli("start")
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertFalse(marker.exists(), "start must cancel this entire prepare invocation")
            self.assertTrue(all(c["phase"] == "waiting" for c in json.loads(stdout)["candidates"]))
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def test_start_after_acquisition_before_publication_releases_candidate(self):
        self.init(self.candidate("A", resources=["install"]), self.candidate("B"))
        session = review_module.Session(self.root, self.registry)
        original = session.transaction
        interrupted = False

        @contextmanager
        def interrupt_between_transactions():
            nonlocal interrupted
            with original() as values:
                yield values
                should_interrupt = not interrupted and values[0]["candidates"]["A"]["phase"] == "preparing"
            if should_interrupt:
                interrupted = True
                session.pause(False, interrupt=True)

        with mock.patch.object(session, "transaction", interrupt_between_transactions):
            result = session.prepare()
        self.assertTrue(interrupted)
        self.assertTrue(all(c["phase"] == "waiting" for c in result["candidates"]))
        self.assertFalse(any(c["protected"] for c in result["candidates"]))
        self.assertEqual(self.cli("conflicts", "--resources", "install")["conflicts"], [])

    def test_static_version_cannot_share_mutating_preparation(self):
        owner = self.candidate("A", resources=["shared-install"], resource_versions={"shared-install": "build-v1"}, prepare={"argv": [sys.executable, "-c", "import time; time.sleep(10)"]})
        self.init(owner)
        other = self.base / "other"; other.mkdir()
        self.init(self.candidate("B", resources=["shared-install"], resource_versions={"shared-install": "build-v1"}), root=other)
        process = subprocess.Popen(self.args("prepare"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if self.cli("status")["candidates"][0]["phase"] == "preparing":
                    break
                time.sleep(.05)
            else:
                self.fail("Preparation did not start")
            result = self.cli("prepare", root=other)
            self.assertEqual(result["candidates"][0]["phase"], "waiting")
            self.assertIn("protected", result["candidates"][0]["error"])
            with self.assertRaises(review_module.ReviewError):
                review_module.Session(other, self.registry).intake(self.decision(result, "B"))
            self.cli("start"); process.communicate(timeout=5)
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def test_release_write_failure_never_exposes_resource_before_invalidation(self):
        self.init(self.candidate(resources=["shared-install"]))
        prepared = self.cli("prepare")
        session = review_module.Session(self.root, self.registry)
        real_write = review_module.atomic_json
        other = self.base / "other"; other.mkdir()
        self.init(self.candidate("B", resources=["shared-install"]), root=other)

        def fail_session(path, value):
            if path == session.path:
                raise OSError("Injected session publication failure")
            real_write(path, value)

        with mock.patch.object(review_module, "atomic_json", fail_session):
            with self.assertRaises(OSError):
                session.resume_development(selected=["A"])
        self.assertEqual(self.cli("prepare", root=other)["candidates"][0]["phase"], "waiting")
        self.assertTrue(self.cli("conflicts", "--resources", "shared-install")["conflicts"])

        def fail_registry(path, value):
            if path == session.registry / "resources.json":
                raise OSError("Injected registry release failure")
            real_write(path, value)

        with mock.patch.object(review_module, "atomic_json", fail_registry):
            with self.assertRaises(OSError):
                session.resume_development(selected=["A"])
        self.assertEqual(self.cli("status")["candidates"][0]["phase"], "waiting")
        self.assertEqual(self.intake(self.decision(prepared), success=False).returncode, 1)
        self.assertEqual(self.cli("prepare", root=other)["candidates"][0]["phase"], "waiting")
        self.cli("resume-development", "--candidate", "A")
        self.assertEqual(self.cli("prepare", root=other)["candidates"][0]["phase"], "ready")

    def test_offline_packet_escapes_and_partial_import_matches_live(self):
        self.init(self.candidate(content="</script><script>window.BAD=1</script>"), self.candidate("B"))
        state = self.cli("prepare")
        dest = self.base / "review.html"
        self.cli("html", "--output", str(dest))
        text = dest.read_text()
        self.assertNotIn("</script><script>window.BAD", text)
        self.assertIn("Local file", text)
        self.assertNotIn("http://127.0.0.1:", text)
        self.assertEqual(self.intake(self.decision(state))["accepted"], ["A"])

    def test_concurrent_independent_decisions_not_lost(self):
        self.init(self.candidate(), self.candidate("B")); state = self.cli("prepare")
        files=[]
        for cid in ("A", "B"):
            path=self.base / f"{cid}.json";path.write_text(json.dumps(self.decision(state,cid)));files.append(path)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            list(pool.map(lambda p:self.cli("import", "--file",str(p)),files))
        self.assertTrue(all(c["decision"] for c in self.cli("status")["candidates"]))

    def test_invalid_input_does_not_overwrite_runtime_state(self):
        self.init(self.candidate()); self.cli("prepare")
        path=self.base / "bad.json";path.write_text(json.dumps({"schema_version":1,"candidates":[self.candidate(decision={"outcome":"accept"})]}))
        self.assertEqual(self.cli("init", "--manifest",str(path),success=False).returncode,1)
        self.assertIsNone(self.cli("status")["candidates"][0]["decision"])
        state=self.cli("status")
        bad=self.decision(state);bad["decisions"].append({"candidate":"missing"})
        self.assertEqual(self.intake(bad,success=False).returncode,1)
        self.assertIsNone(self.cli("status")["candidates"][0]["decision"])


if __name__ == "__main__":
    unittest.main()
