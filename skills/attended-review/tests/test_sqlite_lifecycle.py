"""Qualify SQLite through the deployed CLI, HTTP and the legacy archive reader."""

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "attended_review.py"


class SQLiteLifecycleTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.checkout = self.base / "checkout"
        self.checkout.mkdir()
        self.runtime = self.checkout / ".mask" / "attended-review"
        self.db = self.runtime / "session.sqlite3"
        self.archive = self.runtime / "session.json"
        self.registry = self.base / "registry"
        self.env = {**os.environ, "ATTENDED_REVIEW_HUB_CONFIG": str(self.base / "no-hub.json")}
        self.args = [sys.executable, "-B", str(SCRIPT), "--repo-root", str(self.checkout),
                     "--registry", str(self.registry)]

    def cli(self, *args, input=None):
        result = subprocess.run([*self.args, *args], env=self.env, capture_output=True,
                                text=True, encoding="utf-8", input=input, timeout=25)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    @staticmethod
    def candidate(cid, **fields):
        return {"id": cid, "title": f"Review {cid}", "revision": "first",
                "criteria": ["Check the rendered result."], **fields}

    def init(self, *cards):
        path = self.base / "manifest.json"
        path.write_text(json.dumps({"schema_version": 1, "candidates": cards}), encoding="utf-8")
        return self.cli("init", "--manifest", str(path))

    def packet(self, state, cid, **decision):
        card = next(c for c in state["candidates"] if c["id"] == cid)
        return {"schema_version": 1, "session": state["session"], "decisions": [
            {"candidate": cid, "fingerprint": card["fingerprint"], "decision_id": "answer-" + cid,
             "outcome": "accept", **decision}]}

    def start(self, argv):
        process = subprocess.Popen(argv, env=self.env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding="utf-8")

        def cleanup():
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            process.stdout.close()
            process.stderr.close()

        self.addCleanup(cleanup)
        return process

    def export_process(self, code, *extra):
        return self.start([sys.executable, "-B", "-c", code, str(SCRIPT.parent),
                           str(self.checkout), str(self.registry), *map(str, extra)])

    @staticmethod
    def archive_reader():
        return """
import sys
sys.path.insert(0, sys.argv[1])
from attended_review import open_session
session = open_session(sys.argv[2], sys.argv[3])
"""

    def test_handback_recovers_after_rename_and_before_receipt_across_processes(self):
        media = {"kind": "image", "url": "data:image/png;base64,YQ=="}
        image = {"name": "evidence.png", "data": "data:image/png;base64,Yg=="}
        note = "Critical follow-up: prüfen the café layout."
        self.init(self.candidate("accept", media=[media], resources=["fixture:shared"]),
                  self.candidate("reject"))
        prepared = self.cli("prepare")
        packet = self.packet(prepared, "accept", note=note, attachments=[image])
        accepted = self.cli("import", "--file", "-", input=json.dumps(packet))
        rejected = self.cli("import", "--file", "-", input=json.dumps(
            self.packet(prepared, "reject", outcome="reject")))
        self.assertEqual(accepted["accepted"], ["accept"])
        before = self.cli("status", "--full")
        saved = next(c for c in before["candidates"] if c["id"] == "accept")
        self.assertEqual(saved["decision"]["attachments"], [image])
        self.assertFalse(self.archive.exists())
        writer = self.export_process(self.archive_reader() + """
import time
original = session.store.write_archive
def interrupt(path, header):
    original(path, header)
    print(header["sequence"], flush=True)
    time.sleep(60)
session.store.write_archive = interrupt
session.hand_back()
""")
        marker = int(writer.stdout.readline())
        first_bytes = self.archive.read_bytes()
        self.assertIn(note.encode(), first_bytes)
        first = json.loads(first_bytes)
        self.assertEqual(first["sequence"], marker)
        self.assertEqual(first["host"], None)
        self.assertEqual(first["candidates"]["accept"], saved)
        self.assertEqual(first["candidates"]["reject"]["decision"]["outcome"], "reject")
        self.assertEqual(self.cli("status")["sequence"], rejected["sequence"])
        # These commands take the active DB through later card and lease changes
        # while the exporter holds its separate cross-process ownership lock.
        self.cli("resume-development", "--candidate", "accept")
        with sqlite3.connect(self.db) as db:
            body, = db.execute("SELECT body FROM cards WHERE id='accept'").fetchone()
        released = {**json.loads(body), "media": [media]}
        self.init(self.candidate("accept", revision="second"))
        self.cli("prepare")
        self.assertEqual(self.archive.read_bytes(), first_bytes)
        writer.kill()
        writer.wait(timeout=10)
        # Public wait replays the original archive and returns the old marker.
        observed = self.cli("wait", "--after", str(marker - 1), "--kind", "handed-back", "--timeout", "3")
        self.assertEqual(observed["events"][-1]["sequence"], marker)
        self.assertEqual(self.archive.read_bytes(), first_bytes)
        self.assertIsNone(self.cli("status")["handed_back"])
        second = self.cli("hand-back")
        self.assertEqual(second["pending"], ["accept"])
        later_bytes = self.archive.read_bytes()
        later = json.loads(later_bytes)
        self.assertGreater(later["sequence"], first["sequence"])
        self.assertEqual(later["history"], [released])
        self.assertEqual(later["history"][0]["decision"], saved["decision"])
        self.assertEqual(later["events"][:marker], first["events"])
        self.assertEqual(self.cli("hand-back"), second)
        replay = self.export_process(self.archive_reader() + """
import json
print(json.dumps(session.export(int(sys.argv[4]))))
""", marker)
        stdout, stderr = replay.communicate(timeout=10)
        self.assertEqual(replay.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)["decided"], ["accept", "reject"])
        self.assertEqual(self.archive.read_bytes(), later_bytes)
        old = self.export_process(self.archive_reader() + """
import json
from attended_review import Session
print(json.dumps(Session(sys.argv[2], sys.argv[3]).load()))
""")
        stdout, stderr = old.communicate(timeout=10)
        self.assertEqual(old.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout), later)

    def test_indexed_http_status_and_actions_ignore_unrelated_large_payloads(self):
        raw_image = "QUFB" * 196608
        cards = [self.candidate(f"bulk-{i:03}", content="isolated " * 400,
                                media=[{"kind": "image", "url": "data:image/png;base64," + raw_image,
                                        "label": f"frame {i}"}]) for i in range(56)]
        self.init(self.candidate("focus"), *cards)
        state = self.cli("prepare", "--candidate", "focus")
        self.assertGreater(self.db.stat().st_size, 40 * 1024 * 1024)
        host = self.start([*self.args, "serve", "--no-hub"])
        descriptor = json.loads(host.stdout.readline())
        origin = f"http://127.0.0.1:{descriptor['port']}"
        headers = {"Authorization": "Bearer " + descriptor["token"], "Content-Type": "application/json",
                   "Origin": origin}

        def request(route, value=None, auth=headers):
            data = json.dumps(value).encode() if value is not None else None
            req = urllib.request.Request(origin + route, headers=auth, data=data)
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read()
                return len(body), json.loads(body)

        # The prior material path is unusable. Compact and delta reads and
        # mutations of another card must still exercise their normal API.
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE cards SET body='unreadable' WHERE id='bulk-000'")
            db.execute("UPDATE versions SET body='unreadable' WHERE id='bulk-000'")
            db.execute("UPDATE material SET payload='unreadable'")
        size, lean = request("/api/status?material=omit")
        self.assertLess(size, 250000)
        self.assertEqual(len(lean["candidates"]), 57)
        self.assertEqual(self.cli("status")["sequence"], state["sequence"])
        with self.assertRaises(urllib.error.HTTPError) as denied:
            request("/api/changes?after=0", auth={})
        self.assertEqual(denied.exception.code, 403)
        denied.exception.close()
        size, no_change = request("/api/changes?after=" + str(state["sequence"]))
        self.assertEqual(no_change["candidates"], [])
        self.assertLess(size, 300)
        packet = self.packet(state, "focus", note="keep initial note")
        size, answer = request("/api/decisions", packet)
        self.assertLess(size, 300)
        self.assertEqual(answer["accepted"], ["focus"])
        feedback = {"schema_version": 2, "session": state["session"], "decisions": [], "feedback": [
            {"candidate": "focus", "fingerprint": packet["decisions"][0]["fingerprint"],
             "feedback_id": "followup", "note": "keep revised note"}]}
        request("/api/decisions", feedback)
        self.assertEqual(request("/api/decisions", packet)[1]["accepted"], [])
        self.assertEqual(request("/api/decisions", feedback)[1]["feedback_saved"], [])
        size, delta = request(f"/api/changes?after={state['sequence']}&limit=1")
        self.assertLess(size, 2500)
        self.assertEqual([c["id"] for c in delta["candidates"]], ["focus"])
        self.assertEqual(delta["candidates"][0]["decision"]["note"], "keep initial note")
        self.assertTrue(delta["has_more"])
        _, delta = request(f"/api/changes?after={delta['cursor']}")
        self.assertEqual(delta["candidates"][0]["decision"]["note"], "keep revised note")
        self.assertFalse(delta["has_more"])
        self.assertTrue(self.cli("stop")["stopped"])
        host.wait(timeout=10)
        self.assertIsNone(self.cli("status").get("host"))
