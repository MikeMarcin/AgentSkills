"""Public command paths, portable temporary fixtures and real loopback HTTP."""
import concurrent.futures
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
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
        self.assertEqual(self.intake(self.decision(state, outcome="reject"), success=False).returncode, 1)

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
