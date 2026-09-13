"""Focused public-command tests; run with python -m unittest discover -s this_dir."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib import error, request
from urllib.parse import urlsplit, parse_qs

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wizard.py"


class WizardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / "state with spaces"
        self.definition = {
            "schema_version": 1, "id": "setup", "title": "Device setup",
            "steps": [
                {"id": "choose", "title": "Size", "instruction": "Choose a size", "expected": "Your preference", "response": "choice", "options": ["Small", "Large"]},
                {"id": "connect", "title": "Connect", "instruction": "Connect device", "expected": "Device is listed", "response": "observation"},
                {"id": "finish", "title": "Physical step", "instruction": "Move the device onto the stand", "expected": "Device on stand", "response": "ack"},
            ]}
        self.definition_file = self.root / "definition.json"
        self.definition_file.write_text(json.dumps(self.definition), encoding="utf-8")
        self.run_cli("init", "--definition", str(self.definition_file))

    def run_cli(self, command, *args, state=None, success=True, stdin=None):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), command, "--state", str(state or self.state), *args], input=stdin, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_external_state_from_source_checkout_leaves_source_empty(self):
        source = self.root / "source"
        source.mkdir()
        external = self.root / "runtime" / "wizard"
        for command, extra in (("init", ["--definition", str(self.definition_file)]), ("status", [])):
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), command, "--state", str(external),
                                     "--source-root", str(source), *extra], cwd=source, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((external / "state.json").exists())
        self.assertEqual(list(source.iterdir()), [])

    def test_linked_external_state_refuses_source_write(self):
        source = self.root / "source"
        source.mkdir()
        runtime = self.root / "runtime" / "wizard"
        runtime.mkdir(parents=True)
        linked = runtime / "linked-session"
        linked.symlink_to(source, target_is_directory=True)
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "init", "--state", str(linked),
                                 "--source-root", str(source), "--definition", str(self.definition_file)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("symlinks", result.stdout)
        self.assertEqual(list(source.iterdir()), [])

    def test_linked_external_lock_refuses_source_write(self):
        source = self.root / "source"
        source.mkdir()
        external = self.root / "runtime" / "wizard" / "session"
        external.mkdir(parents=True)
        (external / "state.lock").symlink_to(source / "state.lock")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "init", "--state", str(external),
                                 "--source-root", str(source), "--definition", str(self.definition_file)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("wizard lock path cannot be a symlink", result.stdout)
        self.assertEqual(list(source.iterdir()), [])

    def record(self, step, value, actor="human", **kwargs):
        return self.run_cli("record", "--step", step, "--actor", actor, "--value", json.dumps(value), **kwargs)

    def packet(self, answers, state=None):
        stored = json.loads(((state or self.state) / "state.json").read_text())
        return {"schema_version": 1, "session_id": stored["session_id"], "definition_digest": stored["definition_digest"], "answers": answers}

    def import_answers(self, answers, **kwargs):
        return self.run_cli("import", "--file", "-", stdin=json.dumps(self.packet(answers)), **kwargs)

    def host(self, state=None):
        process = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "serve", "--state", str(state or self.state)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def cleanup():
            if process.poll() is None:
                process.terminate()
            process.communicate(timeout=5)
        self.addCleanup(cleanup)
        endpoint = json.loads(process.stdout.readline())
        self.assertTrue(endpoint["serving"])
        return process, endpoint

    def http(self, endpoint, path, data=None, authenticated=True, origin=None):
        parsed = urlsplit(endpoint["url"])
        headers = {"Content-Type": "application/json"}
        if authenticated:
            headers["Authorization"] = "Bearer " + parse_qs(parsed.fragment)["token"][0]
        if origin:
            headers["Origin"] = origin
        req = request.Request(f"http://{parsed.netloc}{path}", data=None if data is None else json.dumps(data).encode(), headers=headers)
        with request.build_opener(request.ProxyHandler({})).open(req, timeout=3) as response:
            return json.load(response)

    def test_resume_agent_capture_and_incremental_events(self):
        first = self.record("choose", "Small")
        self.assertEqual(first["completed"], 1)
        self.assertEqual(self.run_cli("pause")["status"], "paused")
        self.record("connect", {"summary": "Listed", "evidence": "device list"}, "agent", success=False)
        self.run_cli("resume")
        self.record("connect", {"summary": "Listed", "evidence": "device list"}, "agent")
        self.record("finish", True)
        result = self.run_cli("status", "--since", str(first["revision"]))
        self.assertEqual(result["status"], "complete")
        self.assertEqual([e["kind"] for e in result["events"]], ["paused", "resumed", "answered", "answered"])
        self.assertNotIn("answers", result)

    def test_partial_offline_export_atomic_intake_and_identity(self):
        result = self.import_answers({"choose": "Large"})
        self.assertEqual(result["completed"], 1)
        self.assertEqual(self.import_answers({"choose": "Large"})["revision"], result["revision"])
        self.import_answers({"choose": "Small"}, success=False)
        self.import_answers({"connect": {"summary": "Fake", "evidence": "Fake"}}, success=False)
        wrong = self.packet({})
        wrong["session_id"] = "another session"
        self.run_cli("import", "--file", "-", stdin=json.dumps(wrong), success=False)
        self.assertEqual(self.run_cli("status")["completed"], 1)

    def test_batch_failure_rolls_back_all_new_answers(self):
        self.import_answers({"choose": "Small", "finish": True}, success=False)
        self.assertEqual(self.run_cli("status")["completed"], 0)

    def test_definition_immutable_and_no_executable_fields(self):
        original = self.run_cli("init", "--definition", str(self.definition_file))
        self.definition["steps"][0]["instruction"] = "Changed candidate"
        self.definition_file.write_text(json.dumps(self.definition), encoding="utf-8")
        self.run_cli("init", "--definition", str(self.definition_file), success=False)
        self.assertEqual(self.run_cli("status")["session_id"], original["session_id"])
        self.definition["steps"][0]["command"] = ["rm", "anything"]
        self.definition_file.write_text(json.dumps(self.definition), encoding="utf-8")
        self.run_cli("init", "--definition", str(self.definition_file), state=self.root / "other", success=False)

    def test_ordered_steps_actor_boundary_and_racing_answers(self):
        self.record("finish", True, success=False)
        self.record("choose", "Small", "agent", success=False)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            commands = [[sys.executable, "-B", str(SCRIPT), "record", "--state", str(self.state), "--step", "choose", "--actor", "human", "--value", json.dumps(value)] for value in ("Small", "Large")]
            results = list(pool.map(lambda cmd: subprocess.run(cmd, capture_output=True, text=True, timeout=10), commands))
        self.assertEqual(sorted(r.returncode for r in results), [0, 1])
        self.assertEqual(self.run_cli("status")["completed"], 1)

    def test_cli_pauses_without_answer_and_resumes(self):
        result = self.run_cli("cli", stdin="/pause\n")
        self.assertEqual(result["status"], "paused")
        result = self.run_cli("cli", stdin="2\n")
        self.assertEqual(result["completed"], 1)
        self.assertEqual(result["next"]["response"], "observation")

    def test_standalone_html_escapes_definition_and_retains_partial_export(self):
        self.definition["title"] = "</script><script>unsafe()</script>"
        self.definition_file.write_text(json.dumps(self.definition), encoding="utf-8")
        other = self.root / "escaped"
        self.run_cli("init", "--definition", str(self.definition_file), state=other)
        output = self.root / "offline page.html"
        self.run_cli("html", "--output", str(output), state=other)
        page = output.read_text(encoding="utf-8")
        self.assertNotIn("</script><script>unsafe()", page)
        self.assertIn("Copy partial responses", page)
        self.assertIn("Download partial responses", page)
        self.assertNotIn("__WIZARD_STATE__", page)
        self.run_cli("html", "--output", str(output), state=other, success=False)

    def test_live_save_no_driver_attach_and_host_isolation(self):
        process, endpoint = self.host()
        attached = self.run_cli("serve")
        self.assertTrue(attached["attached"])
        self.assertEqual(attached["url"], endpoint["url"])
        fresh = self.http(endpoint, "/state")
        self.http(endpoint, "/record", {"step": "choose", "value": "Large", "revision": fresh["revision"]})
        self.assertEqual(self.run_cli("status")["completed"], 1)
        with self.assertRaises(error.HTTPError) as stale:
            self.http(endpoint, "/pause", {"revision": fresh["revision"]})
        self.assertEqual(stale.exception.code, 409)
        stale.exception.close()
        with self.assertRaises(error.HTTPError) as unauthorized:
            self.http(endpoint, "/record", {"step": "finish", "value": True, "revision": 1}, authenticated=False)
        self.assertEqual(unauthorized.exception.code, 403)
        unauthorized.exception.close()
        with self.assertRaises(error.HTTPError) as origin:
            self.http(endpoint, "/pause", {"revision": 1}, origin="https://elsewhere.example")
        self.assertEqual(origin.exception.code, 403)
        origin.exception.close()
        with self.assertRaises(error.HTTPError) as fake_observation:
            self.http(endpoint, "/record", {"step": "connect", "value": {"summary": "Fake", "evidence": "Fake"}, "revision": 1})
        self.assertEqual(fake_observation.exception.code, 409)
        fake_observation.exception.close()
        other = self.root / "second checkout"
        self.run_cli("init", "--definition", str(self.definition_file), state=other)
        _, second = self.host(other)
        self.assertNotEqual(urlsplit(endpoint["url"]).netloc, urlsplit(second["url"]).netloc)
        self.assertTrue(self.run_cli("stop")["stopped"])
        process.wait(timeout=5)
        self.assertEqual(self.http(second, "/state")["answers"], {})
        self.run_cli("stop", state=other)


if __name__ == "__main__":
    unittest.main()
