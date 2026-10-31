"""Hub publication through public commands, against disposable local HTTPS fixture hubs.

No real network, Tailscale or hub is contacted: the fake Tailscale CLI models Serve,
and ATTENDED_REVIEW_HUB_FIXTURE_CONNECT routes the TCP connection to a loopback
fixture while TLS still verifies the configured ts.net name against a fixture CA.
"""
import concurrent.futures
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "attended_review.py"
FAKE_TAILSCALE = Path(__file__).parent / "fixtures" / "fake_tailscale.py"
HUB = "https://hub.example.ts.net"
RECORD_KEYS = {"schema", "session_id", "repo", "machine", "harness", "url", "state", "counts",
               "sequence", "publication_revision", "updated_at"}


def openssl(*args, cwd):
    subprocess.run(["openssl", *args], cwd=cwd, check=True, capture_output=True)


def issue(directory, ca, name):
    """A fixture CA and a server certificate it signs, accepted by strict verification."""
    openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", f"{ca}.key", "-out", f"{ca}.pem",
            "-days", "2", "-subj", f"/CN={ca}", "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign", cwd=directory)
    (directory / f"{name}.ext").write_text(
        "subjectAltName=DNS:hub.example.ts.net,DNS:second.example.ts.net\nbasicConstraints=CA:FALSE\n"
        "keyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n"
        "authorityKeyIdentifier=keyid\nsubjectKeyIdentifier=hash\n")
    openssl("req", "-newkey", "rsa:2048", "-nodes", "-keyout", f"{name}.key", "-out", f"{name}.csr",
            "-subj", "/CN=hub.example.ts.net", cwd=directory)
    openssl("x509", "-req", "-in", f"{name}.csr", "-CA", f"{ca}.pem", "-CAkey", f"{ca}.key", "-CAcreateserial",
            "-out", f"{name}.pem", "-days", "2", "-extfile", f"{name}.ext", cwd=directory)


class FixtureHub:
    """Records every request it receives; behaviour is switched per test."""

    def __init__(self, certificate, key):
        self.requests, self.mode = [], {"status": 200}
        self.mutex = threading.Lock()
        hub = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_PUT(self):
                try:
                    body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                    with hub.mutex:
                        hub.requests.append({"path": self.path, "headers": dict(self.headers), "raw": body,
                                             "body": json.loads(body), "time": time.monotonic()})
                    time.sleep(hub.mode.get("delay", 0))
                    self.send_response(hub.mode["status"])
                    if "location" in hub.mode:
                        self.send_header("Location", hub.mode["location"])
                    self.send_header("Content-Length", "2")
                    self.end_headers()
                    self.wfile.write(b"{}")
                except (BrokenPipeError, ConnectionResetError):
                    pass

        class Server(ThreadingHTTPServer):
            daemon_threads = True

            def handle_error(self, *_):
                pass  # Refused handshakes are the point of some tests.

        self.server = Server(("127.0.0.1", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certificate, key)
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .05}, daemon=True)
        self.thread.start()

    @property
    def port(self):
        return self.server.server_address[1]

    def bodies(self):
        with self.mutex:
            return [entry["body"] for entry in self.requests]

    def wait_for(self, predicate, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            bodies = self.bodies()
            if predicate(bodies):
                return bodies
            time.sleep(.05)
        raise AssertionError(f"fixture hub never saw the expected records: {bodies}")

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@unittest.skipIf(os.name == "nt", "Executable Tailscale fixture uses a POSIX shebang; native Windows remains unqualified")
@unittest.skipIf(shutil.which("openssl") is None, "openssl is needed to issue fixture certificates")
class HubPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pki = tempfile.TemporaryDirectory()
        directory = Path(cls.pki.name)
        issue(directory, "trusted-ca", "hub")
        issue(directory, "untrusted-ca", "impostor")
        cls.ca = directory / "trusted-ca.pem"
        cls.hub = FixtureHub(directory / "hub.pem", directory / "hub.key")
        cls.impostor = FixtureHub(directory / "impostor.pem", directory / "impostor.key")

    @classmethod
    def tearDownClass(cls):
        cls.hub.close(); cls.impostor.close(); cls.pki.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "checkout"
        self.root.mkdir()
        self.registry = self.base / "registry"
        self.fake = self.base / "fake-tailscale"
        self.fake.mkdir()
        (self.fake / "config.json").write_text("{}")
        self.tailscale = self.fake / "tailscale"
        self.tailscale.write_text(f"#!{sys.executable}\n" + FAKE_TAILSCALE.read_text())
        self.tailscale.chmod(0o700)
        self.hub.requests.clear(); self.hub.mode = {"status": 200}
        self.impostor.requests.clear()
        self.env = self.environment()
        self.hosts = []
        self.addCleanup(self.cleanup_hosts)

    def environment(self, hub=None, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "CODEX_", "ATTENDED_REVIEW_"))}
        env.update(FAKE_TAILSCALE_ROOT=str(self.fake), SSL_CERT_FILE=str(self.ca),
                   ATTENDED_REVIEW_HUB_FIXTURE_CONNECT=f"127.0.0.1:{(hub or self.hub).port}")
        env.update(extra)
        return env

    def cleanup_hosts(self):
        for process in self.hosts:
            if process.poll() is None:
                self.cli("stop", success=False)
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def args(self, *args):
        return [sys.executable, "-B", str(SCRIPT), "--repo-root", str(self.root), "--registry", str(self.registry), *args]

    def cli(self, *args, env=None, success=True):
        process = subprocess.run(self.args(*args), capture_output=True, text=True, timeout=20, env=env or self.env)
        if success:
            self.assertEqual(process.returncode, 0, process.stderr)
            return json.loads(process.stdout)
        return process

    def candidate(self, cid="A", **fields):
        return {"id": cid, "title": f"Private title {cid}", "revision": "build-1", "content": "Private content",
                "criteria": ["Private criterion"], **fields}

    def init(self, *candidates):
        path = self.base / "manifest.json"
        path.write_text(json.dumps({"schema_version": 1, "candidates": list(candidates)}))
        return self.cli("init", "--manifest", str(path))

    def decision(self, state, cid="A", outcome="accept", decision_id=None):
        item = next(c for c in state["candidates"] if c["id"] == cid)
        return {"schema_version": 1, "session": state["session"], "decisions": [
            {"candidate": cid, "fingerprint": item["fingerprint"], "decision_id": decision_id or f"{cid}-{outcome}",
             "outcome": outcome}]}

    def import_(self, packet):
        path = self.base / "packet.json"
        path.write_text(json.dumps(packet))
        return self.cli("import", "--file", str(path))

    def serve(self, *flags, env=None, tailscale=True):
        args = self.args("serve", *(("--tailscale", "--tailscale-bin", str(self.tailscale)) if tailscale else ()), *flags)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env or self.env)
        self.hosts.append(process)
        return process, json.loads(process.stdout.readline())

    def stop(self, process):
        self.cli("stop")
        process.wait(timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr.read())

    def proxy(self, host):
        """The separate review listener that Serve reaches, with the browser's headers."""
        active = json.loads((self.fake / "config.json").read_text())
        target = active["Foreground"][host["tailscale"]["foreground_session"]]["Web"][
            "review.example.ts.net:" + str(host["tailscale"]["port"])]["Handlers"]["/"]["Proxy"]
        origin = host["tailscale"]["origin"]
        return int(target.rsplit(":", 1)[1]), {"Host": origin.removeprefix("https://"), "Origin": origin}

    def browser(self, host, path, payload):
        port, headers = self.proxy(host)
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(payload).encode(),
            headers={**headers, "Authorization": f"Bearer {host['token']}", "Content-Type": "application/json"})
        started = time.monotonic()
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.load(response), time.monotonic() - started

    def files(self):
        return sorted(p.name for p in (self.root / ".mask" / "attended-review").iterdir())

    def latest(self, predicate, timeout=8):
        """Every received record matching predicate, oldest first, once one exists."""
        bodies = self.hub.wait_for(lambda bodies: any(predicate(b) for b in bodies), timeout)
        return [b for b in bodies if predicate(b)]

    # AC01
    def test_never_enabled_session_gains_no_files_fields_output_or_network(self):
        self.init(self.candidate(), self.candidate("B"))
        state = self.cli("prepare")
        process, host = self.serve()
        self.assertEqual(set(host), {"hosting", "port", "token", "pid", "hostname", "url", "local_url", "tailscale"})
        self.browser(host, "/api/decisions", self.decision(state))
        for command in (("pause",), ("start",), ("hand-back",), ("observe", "B", "--evidence", "seen")):
            self.cli(*command)
        self.assertNotIn("hub", self.cli("status"))
        self.stop(process)
        self.cli("ready", "B", "--evidence", "after host")
        time.sleep(.5)
        self.assertEqual(self.hub.bodies(), [])
        self.assertEqual(self.files(), ["session.json"])
        status = self.cli("status")
        self.assertNotIn("hub", status)
        # An environment destination alone, outside serve, enables nothing.
        self.cli("observe", "B", "--evidence", "again", env=self.environment(ATTENDED_REVIEW_HUB=HUB))
        time.sleep(.3)
        self.assertEqual(self.hub.bodies(), [])
        self.assertEqual(self.files(), ["session.json"])

    # AC02
    def test_exact_wire_contract_at_publication_points_without_private_material(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "remote", "add", "origin",
                        "https://reviewer:remote-secret@git.example.com/org/remote-repo.git"], check=True)
        self.init(self.candidate(), self.candidate("B"),
                  self.candidate("C", prepare={"argv": [sys.executable, "-c", "raise SystemExit(3)"]}))
        # A loopback host publishes nothing for a never-served session.
        process, _ = self.serve("--hub", HUB, tailscale=False)
        self.cli("prepare", "--candidate", "A")
        self.stop(process)
        time.sleep(.3)
        self.assertEqual(self.hub.bodies(), [])
        host_env = self.environment(CLAUDECODE="1")
        process, host = self.serve(env=host_env)
        first = self.latest(lambda b: b["url"] is not None)[0]
        session = self.cli("status")["session"]
        self.assertEqual(set(first), RECORD_KEYS)
        self.assertEqual(first["schema"], "attended-review.hub-record.v1")
        self.assertEqual(first["session_id"], session)
        self.assertEqual(first["url"], host["url"])
        self.assertTrue(first["url"].startswith("https://review.example.ts.net:") and "#token=" in first["url"])
        self.assertEqual(first["repo"], "checkout (remote-repo)")
        self.assertEqual(first["harness"], "claude")
        self.assertEqual((first["state"], first["counts"]), ("ready", {"waiting": 2, "ready": 1, "answered": 0, "total": 3}))
        request = self.hub.requests[0]
        self.assertEqual(request["path"], f"/api/sessions/{session}")
        self.assertEqual(request["headers"]["Content-Type"], "application/json")
        self.assertEqual(request["headers"]["Host"], "hub.example.ts.net")
        self.assertNotIn("Origin", request["headers"]); self.assertNotIn("Authorization", request["headers"])
        # CLI changes while the host runs, including a failed preparation.
        self.cli("prepare", "--candidate", "C")
        failed = self.latest(lambda b: b["sequence"] == first["sequence"] + 2)[-1]
        self.assertEqual(failed["counts"]["waiting"], 2)
        state = self.cli("prepare", "--candidate", "B")
        self.latest(lambda b: b["counts"]["ready"] == 2)
        # Browser answers reach the hub through the host's worker.
        self.browser(host, "/api/decisions", self.decision(state))
        self.latest(lambda b: b["counts"]["answered"] == 1)
        self.cli("pause"); self.latest(lambda b: b["state"] == "paused")
        self.cli("start"); self.latest(lambda b: b["state"] == "ready" and b["sequence"] > failed["sequence"] + 3)
        self.cli("hand-back"); self.latest(lambda b: b["state"] == "handed-back")
        self.stop(process)
        stopped = self.latest(lambda b: b["state"] == "stopped")[-1]
        self.assertIsNone(stopped["url"])
        # A later CLI caller reuses the saved destination and does not relabel the harness.
        self.cli("observe", "B", "--evidence", "after stop", env=self.environment(CODEX_THREAD_ID="x"))
        after = self.latest(lambda b: b["sequence"] == stopped["sequence"] + 1)[-1]
        self.assertEqual((after["state"], after["harness"], after["url"]), ("stopped", "claude", None))
        self.init(self.candidate("D"))
        added = self.latest(lambda b: b["counts"]["total"] == 4)[-1]
        self.assertEqual((added["state"], added["counts"]["waiting"]), ("stopped", 2))
        raw = b"".join(entry["raw"] for entry in self.hub.requests).decode()
        for private in ("Private title", "Private content", "Private criterion", str(self.root), "127.0.0.1",
                        host["local_url"], "remote-secret", "git.example.com", "reviewer", "build-1"):
            self.assertNotIn(private, raw)
        for body in self.hub.bodies():
            self.assertEqual(set(body), RECORD_KEYS)
            self.assertEqual(sum(body["counts"][k] for k in ("waiting", "ready", "answered")), body["counts"]["total"])

    # AC03
    def test_slow_unreachable_and_broken_metadata_preserve_review_behaviour(self):
        self.init(self.candidate(), self.candidate("B"), self.candidate("C"))
        state = self.cli("prepare")
        process, host = self.serve("--hub", HUB)
        self.latest(lambda b: b["url"] is not None)
        self.hub.mode = {"status": 200, "delay": 6}
        count = len(self.hub.requests)
        started = time.monotonic()
        for cid in ("A", "B", "C"):
            result, elapsed = self.browser(host, "/api/decisions", self.decision(state, cid))
            self.assertEqual(result["accepted"], [cid])
            self.assertLess(elapsed, 1.5)
        item = next(c for c in state["candidates"] if c["id"] == "A")
        for n in range(12):
            result, elapsed = self.browser(host, "/api/decisions", {"schema_version": 2, "session": state["session"],
                "decisions": [], "feedback": [{"candidate": "A", "fingerprint": item["fingerprint"],
                                               "feedback_id": f"burst-{n}", "note": f"note {n}"}]})
            self.assertLess(elapsed, 1.5)
        time.sleep(7)
        # One worker: attempts never overlap, each waits out its deadline, and a
        # burst of changes coalesces instead of queueing one request per change.
        arrivals = [entry["time"] for entry in self.hub.requests[count:]]
        self.assertTrue(all(later - earlier > 2.8 for earlier, later in zip(arrivals, arrivals[1:])), arrivals)
        self.assertLessEqual(len(arrivals), 2 + (time.monotonic() - started) / 3)
        warning = None
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not warning:
            warning = self.cli("status").get("hub", {}).get("warning")
            time.sleep(.2)
        self.assertIn("3-second deadline", warning["message"])
        self.assertTrue(all(c["decision"] for c in self.cli("status")["candidates"]))
        started = time.monotonic()
        self.stop(process)  # Final delivery spends at most one deadline.
        self.assertLess(time.monotonic() - started, 6)
        # No host: one bounded CLI attempt, unchanged output and exit status.
        started = time.monotonic()
        ok = self.cli("observe", "A", "--evidence", "slow hub")
        self.assertLess(time.monotonic() - started, 6)
        self.assertEqual(ok["candidates"][0]["id"], "A")
        refused = self.cli("ready", "missing", "--evidence", "x", success=False)
        self.assertEqual(refused.returncode, 1)
        self.assertIn("Unknown candidate", refused.stderr)
        self.assertEqual(refused.stdout, "")
        # Unreachable, then recovery clears the warning.
        unreachable = self.environment(ATTENDED_REVIEW_HUB_FIXTURE_CONNECT="127.0.0.1:9")
        self.cli("observe", "A", "--evidence", "unreachable", env=unreachable)
        self.assertEqual(self.cli("status")["hub"]["warning"]["message"], f"hub {HUB}: connection refused")
        self.hub.mode = {"status": 200}
        self.cli("observe", "A", "--evidence", "recovered")
        self.assertNotIn("hub", self.cli("status"))
        # Broken publisher metadata never changes review results.
        metadata = self.root / ".mask" / "attended-review" / "hub.json"
        saved = metadata.read_bytes()
        metadata.unlink(); metadata.mkdir()
        before = len(self.hub.requests)
        self.assertEqual(self.cli("observe", "A", "--evidence", "broken metadata")["candidates"][0]["id"], "A")
        self.assertNotIn("hub", self.cli("status"))
        self.assertEqual(len(self.hub.requests), before)
        metadata.rmdir(); metadata.write_bytes(saved)

    # AC04
    def test_invalid_origins_certificates_and_redirects_never_leak_the_capability(self):
        self.init(self.candidate()); self.cli("prepare")
        for bad in ("http://hub.example.ts.net", "https://user@hub.example.ts.net", "https://hub.example.ts.net/reviews",
                    "https://hub.example.ts.net/?q=1", "https://hub.example.ts.net/#x", "https://hub.example.com",
                    "https://127.0.0.1", "https://hub.example.ts.net:99999", "https://hub.example.ts.net.", ""):
            for env, flags in ((self.env, ("--hub", bad)), (self.environment(ATTENDED_REVIEW_HUB=bad), ())):
                if not bad and not flags:
                    continue  # An empty environment value means unset.
                result = subprocess.run(self.args("serve", "--tailscale", "--tailscale-bin", str(self.tailscale), *flags),
                                        capture_output=True, text=True, timeout=10, env=env)
                self.assertEqual(result.returncode, 1, (bad, result.stdout))
                self.assertIn("hub must be a Tailscale Serve HTTPS origin", result.stderr)
        self.assertEqual(self.files(), ["session.json"])
        self.assertEqual(self.hub.bodies(), [])
        # A certificate the configured name cannot verify gets no request at all.
        process, host = self.serve("--hub", HUB, env=self.environment(hub=self.impostor))
        token = host["token"]
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and "hub" not in self.cli("status"):
            time.sleep(.1)
        self.assertEqual(self.cli("status")["hub"]["warning"]["message"], f"hub {HUB}: certificate verification failed")
        self.assertEqual(self.impostor.requests, [])
        self.stop(process)
        # A redirect is refused, never followed.
        self.hub.mode = {"status": 307, "location": "https://elsewhere.example.ts.net/capture"}
        process, host = self.serve()
        self.hub.wait_for(lambda b: len(b) >= 1)
        time.sleep(.5)
        self.assertTrue(all(entry["headers"]["Host"] == "hub.example.ts.net" for entry in self.hub.requests))
        message = self.cli("status")["hub"]["warning"]["message"]
        self.assertEqual(message, f"hub {HUB}: redirect refused (HTTP 307)")
        self.stop(process)
        metadata = (self.root / ".mask" / "attended-review" / "hub.json").read_text()
        warning = json.loads(metadata)["warning"]["message"]
        for secret in (token, host["token"], "#token="):
            self.assertNotIn(secret, warning)

    # AC05
    def test_heartbeat_resends_the_identical_snapshot_without_advancing_order(self):
        self.init(self.candidate()); self.cli("prepare")
        process, _ = self.serve("--hub", HUB, env=self.environment(ATTENDED_REVIEW_HUB_FIXTURE_HEARTBEAT="0.5"))
        bodies = self.hub.wait_for(lambda b: len(b) >= 3, timeout=6)
        self.assertEqual(bodies[1], bodies[0]); self.assertEqual(bodies[2], bodies[0])
        times = [entry["time"] for entry in self.hub.requests[:3]]
        self.assertTrue(all(.3 < later - earlier < 2 for earlier, later in zip(times, times[1:])))
        status = self.cli("status")
        self.assertEqual(status["sequence"], bodies[0]["sequence"])
        self.stop(process)
        import importlib.util
        spec = importlib.util.spec_from_file_location("hub_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual((module.HUB_HEARTBEAT_SECONDS, module.HUB_DEADLINE_SECONDS), (300, 3))

    # AC06
    def test_disjoint_counts_states_and_ordering_across_restart_and_concurrency(self):
        self.init(self.candidate(), self.candidate("B"), self.candidate("C"),
                  self.candidate("D", prepare={"argv": [sys.executable, "-c", "pass"], "speed": "slow"}))
        state = self.cli("prepare")
        self.cli("observe", "A", "--evidence", "x")
        process, host = self.serve("--hub", HUB)
        def current(**expected):
            def match(body):
                return all(body[k] == v for k, v in expected.items())
            return self.latest(match)[-1]
        ready = current(state="ready")
        self.assertEqual(ready["counts"], {"waiting": 1, "ready": 3, "answered": 0, "total": 4})
        self.import_(self.decision(state, "A"))
        self.import_(self.decision(state, "B", "reject"))
        # Saved feedback alone is not an answer.
        item = next(c for c in state["candidates"] if c["id"] == "C")
        self.import_({"schema_version": 2, "session": state["session"], "decisions": [], "feedback": [
            {"candidate": "C", "fingerprint": item["fingerprint"], "feedback_id": "f1", "note": "later"}]})
        current(counts={"waiting": 1, "ready": 1, "answered": 2, "total": 4})
        self.import_(self.decision(state, "B", "withdrawn", "B-withdraw"))
        current(counts={"waiting": 1, "ready": 2, "answered": 1, "total": 4})
        self.cli("pause"); current(state="paused")
        self.cli("hand-back")
        partial = current(state="handed-back")
        self.assertEqual(partial["counts"]["ready"], 2)
        self.cli("start"); current(state="ready", counts=partial["counts"])
        self.cli("resume-development", "--candidate", "B", "--candidate", "C")
        current(state="preparing", counts={"waiting": 3, "ready": 0, "answered": 1, "total": 4})
        self.import_({"schema_version": 1, "session": state["session"], "decisions": []})
        # Shutdown and restart keep the review sequence but advance the publication revision.
        before = current(state="preparing")
        self.stop(process)
        stopped = current(state="stopped")
        process, restarted = self.serve()
        again = current(url=restarted["url"])
        self.assertNotEqual(restarted["url"], host["url"])
        self.assertEqual({before["sequence"], stopped["sequence"], again["sequence"]}, {before["sequence"]})
        self.assertLess(before["publication_revision"], stopped["publication_revision"])
        self.assertLess(stopped["publication_revision"], again["publication_revision"])
        self.stop(process)
        final = current(state="stopped", publication_revision=again["publication_revision"] + 1)
        # Concurrent CLI callers never number an older snapshot higher.
        with concurrent.futures.ThreadPoolExecutor(6) as pool:
            list(pool.map(lambda n: self.cli("observe", "A", "--evidence", f"concurrent {n}"), range(6)))
        sequence = self.cli("status")["sequence"]
        self.latest(lambda b: b["sequence"] == sequence)
        by_revision = {}
        for body in self.hub.bodies():
            self.assertEqual(by_revision.setdefault(body["publication_revision"], body), body)
        ordered = [by_revision[r] for r in sorted(by_revision) if r > final["publication_revision"]]
        sequences = [b["sequence"] for b in ordered]
        self.assertEqual(sequences, sorted(set(sequences)))
        self.assertEqual(sequences[-1], sequence)

    # AC07
    def test_configuration_precedence_reuse_attachment_and_disabling(self):
        self.init(self.candidate(), self.candidate("B")); self.cli("prepare")
        second = "https://second.example.ts.net:8443"
        hosts = lambda: [entry["headers"]["Host"] for entry in self.hub.requests]
        # The flag overrides the environment, and both flags together are refused.
        both = subprocess.run(self.args("serve", "--hub", HUB, "--no-hub"), capture_output=True, text=True, env=self.env)
        self.assertEqual(both.returncode, 2)
        self.assertIn("not allowed with argument", both.stderr)
        process, host = self.serve("--hub", second, env=self.environment(ATTENDED_REVIEW_HUB=HUB))
        self.hub.wait_for(lambda b: len(b) >= 1)
        self.assertEqual(set(hosts()), {"second.example.ts.net:8443"})
        # Attaching with a new destination redirects the running host's publication.
        attached = self.cli("serve", "--hub", HUB)
        self.assertTrue(attached["attached"])
        self.hub.wait_for(lambda b: "hub.example.ts.net" in hosts())
        self.cli("ready", "B", "--evidence", "x")  # from a shell without the environment variable
        self.hub.wait_for(lambda b: b[-1]["sequence"] > b[0]["sequence"] and hosts()[-1] == "hub.example.ts.net")
        # Explicit disabling overrides the environment, clears the saved destination and cancels pending work.
        self.assertTrue(self.cli("serve", "--no-hub", env=self.environment(ATTENDED_REVIEW_HUB=HUB))["attached"])
        time.sleep(.6)
        count = len(self.hub.requests)
        self.cli("observe", "A", "--evidence", "disabled")
        self.stop(process)
        self.cli("observe", "A", "--evidence", "disabled after stop")
        time.sleep(.5)
        self.assertEqual(len(self.hub.requests), count)
        metadata = json.loads((self.root / ".mask" / "attended-review" / "hub.json").read_text())
        self.assertIsNone(metadata["hub"])
        # The environment applies at serve when no flag is given; later commands reuse it.
        revision = metadata["publication_revision"]
        process, _ = self.serve(env=self.environment(ATTENDED_REVIEW_HUB=second))
        resumed = self.hub.wait_for(lambda b: len(b) > count)[-1]
        self.assertGreater(resumed["publication_revision"], revision)
        self.assertEqual(hosts()[-1], "second.example.ts.net:8443")
        self.stop(process)
        self.cli("observe", "A", "--evidence", "reuse saved")
        self.hub.wait_for(lambda b: b[-1]["state"] == "stopped" and b[-1]["sequence"] == self.cli("status")["sequence"])
        self.assertEqual(hosts()[-1], "second.example.ts.net:8443")

    def test_symlinked_skill_in_two_consumers_publishes_independent_sessions(self):
        roots, processes = [self.root, self.base / "second-consumer"], []
        roots[1].mkdir()
        original = self.root
        for root in roots:
            link = root / ".agents" / "skills" / "attended-review"
            link.parent.mkdir(parents=True)
            link.symlink_to(SCRIPT.parent.parent, target_is_directory=True)
            self.root = root
            self.init(self.candidate()); self.cli("prepare")
            args = [sys.executable, "-B", str(link / "scripts" / "attended_review.py"), "--repo-root", str(root),
                    "--registry", str(self.registry), "serve", "--tailscale", "--tailscale-bin", str(self.tailscale), "--hub", HUB]
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env)
            processes.append((root, process, json.loads(process.stdout.readline())))
        bodies = self.hub.wait_for(lambda b: len({x["session_id"] for x in b}) == 2)
        labels = {b["session_id"]: (b["repo"], b["url"]) for b in bodies}
        self.assertEqual(sorted(label for label, _ in labels.values()), ["checkout", "second-consumer"])
        self.assertEqual({url for _, url in labels.values()}, {host["url"] for _, _, host in processes})
        for root, process, _ in processes:
            self.root = root
            self.assertTrue((root / ".mask" / "attended-review" / "hub.json").is_file())
            self.cli("stop"); process.wait(timeout=10)
            self.assertEqual(process.returncode, 0, process.stderr.read())
            process.stdout.close(); process.stderr.close()
        self.root = original
        self.hub.wait_for(lambda b: sum(x["state"] == "stopped" for x in b) == 2)


if __name__ == "__main__":
    unittest.main()
