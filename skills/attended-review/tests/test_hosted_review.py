"""Exercise the native CLI using isolated consumers and the actual hub backends."""

import base64
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import hashlib
import http.server
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest

from test_hub_publication import issue

SKILL = Path(__file__).resolve().parents[1]
HUB_ROOT = os.environ.get("ATTENDED_REVIEW_HUB_ROOT")
BASELINE = "d06e564f94697d2f2419d27fd4fbce97f4472c17"
UNBOUND_HOSTED_BASELINE = "8bdb8ea8e05bae4affe68f0b48f9c12d36601c94"
TOKEN_ENV = "ATTENDED_REVIEW_HOSTED_TOKEN"
CONNECTION_ENV = "ATTENDED_REVIEW_HOSTED_FIXTURE_CONNECT"
PROJECT_CONFIG = ".mask/skill-config/attended-review/project.json"

if HUB_ROOT:
    sys.path.insert(0, str(Path(HUB_ROOT).resolve()))
    from tests.test_hosted_access import COLLABORATION, OWNER, PRODUCER, REVIEWER, VIEWER
    from tests.test_hosted_handback import HandbackFixture as HubFixture
    from tests.test_hosted_publication import png, wav
else:
    HubFixture = unittest.TestCase


class Consumer:
    def __init__(self, fixture, name, candidates, hosted=True, version=1, initializer=None, config=None):
        self.fixture = fixture
        self.directory = fixture.root / name
        self.directory.mkdir()
        self.checkout = self.directory / "checkout"
        self.checkout.mkdir()
        self.state = self.directory / "state"
        self.link = self.checkout / "attended-review"
        self.link.symlink_to(SKILL, target_is_directory=True)
        self.env = {**os.environ, "ATTENDED_REVIEW_HUB_CONFIG": str(self.directory / "machine-hub.json"),
                    TOKEN_ENV: fixture.tokens["alpha"] if hasattr(fixture, "tokens") else secrets.token_urlsafe(32)}
        self.config = self.checkout / PROJECT_CONFIG
        if config is not None:
            self.configure(config)
        self.manifest = self.directory / "manifest.json"
        self.manifest.write_text(json.dumps({"schema_version": version, "candidates": candidates}))
        self.init = ["init", "--manifest", str(self.manifest)]
        self.initial = self.run(*self.init, *(["--hosted"] if hosted else []), script=initializer)

    def configure(self, config):
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_text(json.dumps(config))

    def invoke(self, *args, code=0, script=None, state=None, env=None):
        helper = script or self.link / "scripts" / "attended_review.py"
        command = [sys.executable, "-B", str(helper), "--repo-root", str(self.checkout),
                   "--state", str(state or self.state), "--registry", str(self.directory / "registry"), *args]
        trial = subprocess.run(command, capture_output=True, text=True, timeout=15,
                               env={**self.env, **(env or {})})
        case = self.fixture
        case.assertNotIn((env or {}).get(TOKEN_ENV, self.env[TOKEN_ENV]), trial.stdout + trial.stderr)
        case.assertEqual(trial.returncode, code, trial.stderr or trial.stdout)
        return trial

    def run(self, *args, code=0, **kwargs):
        trial = self.invoke(*args, code=code, **kwargs)
        return json.loads(trial.stdout if code == 0 else trial.stderr)

    def publish(self, *ids, **kwargs):
        picks = [word for cid in ids for word in ("--candidate", cid)]
        return self.run("hosted-publish", "--origin", "https://" + PRODUCER, "--project", "alpha",
                        "--installation", "desk", "--owner", OWNER, "--title", "Synthetic review",
                        "--include-media", *picks, **kwargs)

    def database(self):
        return closing(sqlite3.connect(self.state / "session.sqlite3"))


def card(cid, **values):
    return {"id": cid, "title": "Check the draft", "revision": "fixture-v1",
            "criteria": ["Check that the caption is legible."], **values}


def routing(project="alpha", origin="https://producer.example.ts.net", owner="owner@example.invalid", **defaults):
    return {"schema": "attended-review.project.v1", "mode": "hosted",
            "hosted": {"origin": origin, "project": project, "owner": owner, **defaults}}


def sqlite_backup(source, destination):
    with closing(sqlite3.connect(source)) as original, closing(sqlite3.connect(destination)) as copy:
        original.backup(copy)


@unittest.skipIf(os.name == "nt", "Temporary consumer links use the local POSIX fixture")
class HostedModeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="ask-hosted-mode-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_explicit_mode_isolated_through_two_consumer_links(self):
        hosted = Consumer(self, "hosted", [card("Proof")])
        local = Consumer(self, "local", [card("Proof")], hosted=False)
        self.assertNotEqual(hosted.initial["session"], local.initial["session"])
        self.assertEqual(hosted.initial["mode"], "hosted")
        self.assertNotIn("mode", local.initial)
        for consumer in (hosted, local):
            self.assertEqual(consumer.run("prepare")["candidates"][0]["phase"], "ready")
        self.assertIn("mode is fixed", hosted.run(*hosted.init, "--legacy", code=1)["error"])
        self.assertIn("mode is fixed", local.run(*local.init, "--hosted", code=1)["error"])
        for args in [("serve",), ("html", "--output", str(self.root / "offline.html")), ("hand-back",)]:
            hosted.run(*args, code=1)
        self.assertFalse((self.root / "offline.html").exists())
        payload = self.root / "intake.json"
        payload.write_text(json.dumps({"schema_version": 2, "session": hosted.initial["session"], "decisions": []}))
        self.assertIn("collaboration", hosted.run("import", "--file", str(payload), code=1)["error"])
        self.assertTrue(local.run("hand-back")["handed_back"])
        self.assertFalse((hosted.state / "session.json").exists())
        self.assertFalse((hosted.state / "hub.json").exists())
        self.assertEqual(hosted.run("status")["checkout"], str(hosted.checkout.resolve()))

    def test_project_mode_defaults_and_existing_modes_through_two_links(self):
        hosted = Consumer(self, "configured", [card("Proof")], hosted=False, config=routing())
        legacy = Consumer(self, "unconfigured", [card("Proof")], hosted=False)
        self.assertEqual(hosted.initial["mode"], "hosted")
        self.assertNotIn("mode", legacy.initial)
        self.assertNotEqual(hosted.initial["session"], legacy.initial["session"])
        inspect_state = hosted.directory / "inspection-only"
        self.assertEqual(hosted.run("project-config", state=inspect_state),
                         {"mode": "hosted", "hosted": routing()["hosted"], "path": str(hosted.config.resolve())})
        self.assertFalse(inspect_state.exists())
        self.assertEqual(legacy.run("project-config"),
                         {"mode": "legacy", "hosted": None, "path": str(legacy.config.resolve())})
        fallback = hosted.directory / "legacy"
        self.assertNotIn("mode", hosted.run(*hosted.init, "--legacy", state=fallback))
        self.assertNotIn("mode", hosted.run(*hosted.init, state=fallback))
        legacy.configure(routing(project="beta"))
        self.assertNotIn("mode", legacy.run(*legacy.init))
        self.assertTrue(legacy.run("hand-back")["handed_back"])
        archive_state = legacy.directory / "existing-json"
        archive_state.mkdir()
        shutil.copyfile(legacy.state / "session.json", archive_state / "session.json")
        self.assertNotIn("mode", legacy.run(*legacy.init, state=archive_state))
        self.assertFalse((archive_state / "session.sqlite3").exists())
        self.assertEqual(legacy.run(*legacy.init, state=legacy.directory / "fresh")["mode"], "hosted")
        hosted.config.unlink()
        self.assertEqual(hosted.run(*hosted.init)["mode"], "hosted")
        hosted.configure({"schema": "attended-review.project.v1", "mode": "legacy"})
        self.assertNotIn("mode", hosted.run(*hosted.init, state=hosted.directory / "declared-legacy"))
        self.assertEqual(hosted.run(*hosted.init, "--hosted", state=hosted.directory / "explicit")["mode"], "hosted")
        refusal = hosted.invoke(*hosted.init, "--hosted", "--legacy", code=2)
        self.assertIn("not allowed with", refusal.stderr)

    def test_malformed_and_cross_project_config_fail_when_consulted(self):
        consumer = Consumer(self, "source", [card("Proof")], hosted=False)
        other = Consumer(self, "neighbor", [card("Proof")], hosted=False, config=routing(project="beta"))
        fresh = consumer.directory / "fresh"
        marker = secrets.token_urlsafe(32)
        invalid = [
            b"not JSON",
            b'{"schema":"attended-review.project.v1","mode":"hosted","mode":"legacy"}',
            b" " * (64 * 1024 + 1),
            json.dumps(routing(project="Invalid Project")).encode(),
            json.dumps(routing(origin="http://producer.example.ts.net")).encode(),
            json.dumps(routing(origin="https://[invalid")).encode(),
            json.dumps(routing(owner=False)).encode(),
            json.dumps(routing(installation=None)).encode(),
            json.dumps(routing(token=marker)).encode(),
        ]
        consumer.config.parent.mkdir(parents=True)
        for raw in invalid:
            consumer.config.write_bytes(raw)
            result = consumer.run(*consumer.init, state=fresh, code=1)
            self.assertIn("project config", result["error"])
            self.assertNotIn(marker, result["error"])
            self.assertFalse((fresh / "session.sqlite3").exists())
        refusal = consumer.run("project-config", code=1)
        self.assertIn("project config", refusal["error"])
        self.assertNotIn(marker, refusal["error"])
        self.assertNotIn("mode", consumer.run(*consumer.init))
        self.assertNotIn("mode", consumer.run(*consumer.init, "--legacy", state=consumer.directory / "fallback"))
        self.assertEqual(consumer.run(*consumer.init, "--hosted", state=consumer.directory / "explicit")["mode"], "hosted")
        consumer.config.unlink()
        consumer.config.symlink_to(other.config)
        self.assertIn("inside the checkout", consumer.run(*consumer.init, state=fresh, code=1)["error"])
        self.assertFalse((fresh / "session.sqlite3").exists())
        self.assertEqual(other.run("status")["mode"], "hosted")
        consumer.config.unlink()
        consumer.configure(routing())
        fresh.mkdir(exist_ok=True)
        (fresh / "session.sqlite3").touch()
        self.assertEqual(consumer.run(*consumer.init, state=fresh)["mode"], "hosted")


@unittest.skipUnless(HUB_ROOT and shutil.which("openssl") and os.name != "nt",
                     "Set ATTENDED_REVIEW_HUB_ROOT to the local hub checkout and provide openssl")
class NativeHubTests(HubFixture):
    def setUp(self):
        super().setUp()
        issue(self.root, "test-ca", "producer", hosts=(PRODUCER, "redirect.example.ts.net"))
        self.actions = {}
        self.requests = []
        self.proxies = []
        self.port = self.proxy()

    def proxy(self):
        fixture = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def forward(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                action = self.path.rsplit("/", 1)[-1] if self.command != "GET" else "poll"
                fixture.requests.append((self.server.server_port, self.command, action, self.headers["Host"]))
                headers = [(key, self.headers[key]) for key in
                           ("Authorization", "Content-Type", "Content-Length", "X-Hosted-Revision")
                           if key in self.headers]
                override = fixture.actions.pop(action, None)
                if override == "redirect":
                    self.send_response(307)
                    self.send_header("Location", f"https://redirect.example.ts.net:{fixture.proxies[-1]}/capture")
                    self.end_headers()
                    return
                status, _, result = fixture.via_socket("producer", self.path, self.command, headers, body)
                if override == "drop":
                    self.close_connection = True
                    return
                if callable(override):
                    result = override(result)
                self.send_response(status)
                self.send_header("Content-Length", str(len(result)))
                self.end_headers()
                self.wfile.write(result)

            do_PUT = do_POST = do_GET = forward

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.root / "producer.pem", self.root / "producer.key")
        server.socket = context.wrap_socket(server.socket, server_side=True)
        worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .01})
        worker.start()

        def stop():
            server.shutdown()
            worker.join(timeout=5)
            server.server_close()

        self.addCleanup(stop)
        self.proxies.append(server.server_port)
        return server.server_port

    def consumer(self, name, *candidates, version=1, initializer=None, config=None):
        consumer = Consumer(self, name, list(candidates), hosted=config is None, version=version,
                            initializer=initializer, config=config)
        consumer.env.update({CONNECTION_ENV: f"127.0.0.1:{self.port}", "SSL_CERT_FILE": str(self.root / "test-ca.pem")})
        consumer.run("prepare", script=initializer)
        return consumer

    def endpoints(self, consumer, receipt):
        path = "/api/projects/alpha/reviews/" + receipt["review"]
        return path, self.scope(consumer.initial["session"]) + "/handback/" + receipt["review"]

    def earlier_helper(self, revision, *files):
        upstream = SKILL.parents[1]
        reader = self.root / ("helper-" + revision[:7])
        reader.mkdir()
        for file in ("attended_review.py", "review_store.py", *files):
            old = subprocess.check_output(["git", "-C", str(upstream), "show",
                                           f"{revision}:skills/attended-review/scripts/{file}"])
            (reader / file).write_bytes(old)
        return reader / "attended_review.py"

    def frozen_consumer(self, name):
        consumer = self.consumer(name, card("Proof"))
        receipt = consumer.publish("Proof")
        review, _ = self.endpoints(consumer, receipt)
        self.assertEqual(self.decision(review, "Proof", version=0, outcome="accept", note="Ship café ☕")[0], 200)
        status, _, data = self.freeze(review, receipt["revision"])
        self.assertEqual(status, 200)
        return consumer, review, json.loads(data)["delivery"]

    def restore_hub(self, backup):
        for boundary in ("producer", "collaboration"):
            self.stop(self.processes[boundary])
        sqlite_backup(backup, self.root / "data" / "hosted.sqlite3")
        self.start("producer", PRODUCER)
        self.start("collaboration", COLLABORATION)

    def test_locally_acknowledged_delivery_reconciles_restored_hub(self):
        consumer, review, delivery = self.frozen_consumer("ack-recovery")
        hub_backup = self.root / "hub-before-ack.sqlite3"
        sqlite_backup(self.root / "data" / "hosted.sqlite3", hub_backup)
        first = consumer.run("hosted-poll")
        self.assertEqual((first["state"], first["delivery"]), ("delivered", delivery))
        archive = consumer.state / "session.json"
        saved = archive.read_bytes()
        original_status = consumer.run("status", "--after", "0")
        with consumer.database() as db:
            self.assertEqual(db.execute("SELECT acknowledged FROM hosted_package").fetchone(), (1,))
        self.restore_hub(hub_backup)
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "waiting")
        requests = len(self.requests)
        self.assertEqual(consumer.run("hosted-poll"), first)
        self.assertEqual([request[2] for request in self.requests[requests:]], ["ack"])
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "delivered")
        self.assertEqual(consumer.run("status", "--after", "0"), original_status)
        self.assertEqual(archive.read_bytes(), saved)

    def test_hosted_database_copy_cannot_write_or_ack_in_a_different_state(self):
        consumer, review, delivery = self.frozen_consumer("directory-binding")
        copied = consumer.directory / "copied-state"
        copied.mkdir()
        sqlite_backup(consumer.state / "session.sqlite3", copied / "session.sqlite3")
        requests = len(self.requests)
        for command in ("hosted-poll", "hosted-publish"):
            self.assertIn("original state directory", consumer.run(command, state=copied, code=1)["error"])
        self.assertEqual(len(self.requests), requests)
        self.assertFalse((copied / "session.json").exists())
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "waiting")
        alias = consumer.directory / "original-state-alias"
        alias.symlink_to(consumer.state, target_is_directory=True)
        result = consumer.run("hosted-poll", state=alias)
        self.assertEqual((result["state"], result["delivery"]), ("delivered", delivery))
        self.assertTrue((consumer.state / "session.json").is_file())

    def test_restored_origin_adopts_only_the_exact_existing_archive(self):
        consumer, review, delivery = self.frozen_consumer("archive-recovery")
        native_db = consumer.state / "session.sqlite3"
        native_backup = self.root / "origin-before-poll.sqlite3"
        hub_backup = self.root / "hub-before-ack.sqlite3"
        sqlite_backup(native_db, native_backup)
        sqlite_backup(self.root / "data" / "hosted.sqlite3", hub_backup)
        baseline = consumer.run("status", "--after", "0")
        first = consumer.run("hosted-poll")
        self.assertEqual(first["delivery"], delivery)
        archive = consumer.state / "session.json"
        saved = consumer.directory / "original-archive.json"
        archive.rename(saved)
        original_bytes = saved.read_bytes()
        sqlite_backup(native_backup, native_db)
        self.restore_hub(hub_backup)
        self.assertEqual(consumer.run("status", "--after", "0"), baseline)

        conflict = b'{"other":"local result"}\n'
        archive.write_bytes(conflict)
        self.assertIn("conflicts", consumer.run("hosted-poll", code=1)["error"])
        self.assertEqual(consumer.run("status", "--after", "0"), baseline)
        self.assertEqual(archive.read_bytes(), conflict)
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "needs_attention")
        with consumer.database() as db:
            self.assertEqual(db.execute("SELECT delivery FROM hosted_package").fetchone(), (None,))
            self.assertEqual(db.execute("SELECT count(*) FROM exports").fetchone(), (0,))

        archive.rename(consumer.directory / "preserved-conflict.json")
        saved.rename(archive)
        inode = archive.stat().st_ino
        self.assertEqual(consumer.run("hosted-poll"), first)
        self.assertEqual(archive.read_bytes(), original_bytes)
        self.assertEqual(archive.stat().st_ino, inode)
        current = consumer.run("status", "--after", "0")
        self.assertEqual([event["kind"] for event in current["events"]].count("handed-back"), 1)
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "delivered")

    def test_previous_schema_requires_a_new_session_instead_of_rebinding(self):
        earlier = self.earlier_helper(UNBOUND_HOSTED_BASELINE, "hosted_review.py")
        unpublished = self.consumer("old-unpublished", card("Proof"), initializer=earlier)
        requests = len(self.requests)
        self.assertEqual(unpublished.run("status")["session"], unpublished.initial["session"])
        self.assertIn("no recorded state directory", unpublished.publish("Proof", code=1)["error"])
        self.assertEqual(len(self.requests), requests)
        with unpublished.database() as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone(), (2,))
        replacement = self.consumer("bound-replacement", card("Proof"))
        self.assertNotEqual(replacement.initial["session"], unpublished.initial["session"])
        self.assertEqual(replacement.publish("Proof")["state"], "committed")
        self.assertIn("database version", replacement.run("status", script=earlier, code=1)["error"])

        old_published = self.consumer("old-published", card("Proof"), initializer=earlier)
        receipt = old_published.publish("Proof", script=earlier)
        review, _ = self.endpoints(old_published, receipt)
        self.assertEqual(self.freeze(review, receipt["revision"])[0], 200)
        requests = len(self.requests)
        for args in (("hosted-poll",), ("hosted-publish",), ("wait", "--timeout", "0")):
            self.assertIn("no recorded state directory", old_published.run(*args, code=1)["error"])
        self.assertEqual(len(self.requests), requests)
        self.assertFalse((old_published.state / "session.json").exists())
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "waiting")

    def test_unbound_published_origin_can_release_resources_for_replacement_offline(self):
        earlier = self.earlier_helper(UNBOUND_HOSTED_BASELINE, "hosted_review.py")
        original = self.consumer("old-resource-owner", card("Proof", resources=["fixture-installation"]),
                                 initializer=earlier)
        receipt = original.publish("Proof", script=earlier)
        review, _ = self.endpoints(original, receipt)
        self.assertEqual(self.freeze(review, receipt["revision"])[0], 200)
        requests = len(self.requests)

        replacement_state = original.directory / "replacement-state"
        fallback = original.run(*original.init, "--hosted", state=replacement_state)
        self.assertNotEqual(fallback["session"], original.initial["session"])
        blocked = original.run("prepare", state=replacement_state)["candidates"][0]
        self.assertEqual(blocked["phase"], "waiting")
        self.assertIn("protected", blocked["error"])

        released = original.run("resume-development", "--candidate", "Proof")
        self.assertEqual(released["affected"], ["Proof"])
        self.assertFalse(released["status"]["candidates"][0]["protected"])
        prepared = original.run("prepare", state=replacement_state)["candidates"][0]
        self.assertEqual(prepared["phase"], "ready")
        self.assertTrue(prepared["protected"])
        for args in (("hosted-publish",), ("hosted-poll",), ("wait", "--timeout", "0"),
                     ("observe", "Proof", "--evidence", "fixture observation")):
            self.assertIn("no recorded state directory", original.run(*args, code=1)["error"])
        self.assertEqual(len(self.requests), requests)
        self.assertFalse((original.state / "session.json").exists())
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "waiting")

    def test_unbound_release_reports_current_protection_with_a_pending_export(self):
        earlier = self.earlier_helper(UNBOUND_HOSTED_BASELINE, "hosted_review.py")
        original = self.consumer("pending-legacy-export", card("A", resources=["fixture-a"]),
                                 card("B", resources=["fixture-b"]), initializer=earlier)
        receipt = original.publish("A", "B", script=earlier)
        review, _ = self.endpoints(original, receipt)
        self.assertEqual(self.decision(review, "A", version=0, outcome="accept", note="Pending verdict")[0], 200)
        self.assertEqual(self.freeze(review, receipt["revision"])[0], 200)
        export_lock = original.state / ".export-lock.sqlite3"
        export_lock.mkdir()
        try:
            self.assertIn("archive is pending", original.run("hosted-poll", script=earlier, code=1)["error"])
        finally:
            export_lock.rmdir()
        with original.database() as db:
            self.assertEqual(db.execute("SELECT receipt FROM exports").fetchall(), [(None,)])
            pending = json.loads(db.execute("SELECT body FROM cards WHERE id='A'").fetchone()[0])
            self.assertEqual(pending["decision"]["outcome"], "accept")

        requests = len(self.requests)
        registry = original.directory / "registry" / "resources.json"
        before_claims = json.loads(registry.read_text())
        self.assertEqual(set(before_claims), {"fixture-a", "fixture-b"})
        before_status = original.run("status")
        self.assertIsNone(before_status["handed_back"])
        self.assertTrue(all(candidate["decision"] is None and candidate["feedback"] is None
                            for candidate in before_status["candidates"]))
        full_before = original.run("status", "--after", "0", "--full")
        self.assertTrue(all(event["kind"] not in {"decision", "feedback", "handed-back", "resume-development"}
                            for event in full_before["events"]))
        response = original.run("resume-development", "--candidate", "A")
        self.assertEqual(response["affected"], ["A"])
        expected = {"affected": ["A"], "status": before_status}
        next(candidate for candidate in before_status["candidates"] if candidate["id"] == "A")["protected"] = False
        self.assertEqual(response, expected)
        self.assertEqual(original.run("status"), response["status"])
        next(candidate for candidate in full_before["candidates"] if candidate["id"] == "A")["protected"] = False
        self.assertEqual(original.run("status", "--after", "0", "--full"), full_before)
        self.assertEqual(json.loads(registry.read_text()), {"fixture-b": before_claims["fixture-b"]})
        for args in (("hosted-publish",), ("hosted-poll",), ("wait", "--timeout", "0")):
            self.assertIn("no recorded state directory", original.run(*args, code=1)["error"])
        self.assertEqual(len(self.requests), requests)
        self.assertFalse((original.state / "session.json").exists())
        with original.database() as db:
            self.assertEqual(db.execute("SELECT acknowledged FROM hosted_package").fetchone(), (0,))
            self.assertEqual(db.execute("SELECT receipt FROM exports").fetchall(), [(None,)])
        self.assertEqual(json.loads(self.human(review)[2])["delivery"], "waiting")

    def test_project_routes_publish_to_actual_hub_and_freeze_saved_binding(self):
        alpha = self.consumer("configured-alpha", card("Proof"), card("Unshared"),
                              config=routing(origin="https://" + PRODUCER, owner=OWNER))
        beta = self.consumer("configured-beta", card("Proof"),
                             config=routing(project="beta", origin="https://" + PRODUCER, owner=VIEWER,
                                            installation="desk"))
        beta.env[TOKEN_ENV] = self.tokens["beta"]
        self.assertEqual([alpha.initial["mode"], beta.initial["mode"]], ["hosted", "hosted"])
        before = len(self.requests)
        self.assertEqual(alpha.run("project-config")["hosted"]["project"], "alpha")
        self.assertEqual(beta.run("project-config")["hosted"]["project"], "beta")
        self.assertIn("Create the package", alpha.run("hosted-publish", code=1)["error"])
        self.assertIn("--candidate", alpha.run("hosted-publish", "--installation", "desk",
                                               "--title", "Review caption", code=1)["error"])
        self.assertIn("--title", alpha.run("hosted-publish", "--installation", "desk",
                                           "--candidate", "Proof", code=1)["error"])
        self.assertIn("--installation", alpha.run("hosted-publish", "--title", "Review caption",
                                                  "--candidate", "Proof", code=1)["error"])
        self.assertEqual(len(self.requests), before)

        picks = ("--title", "Review caption", "--candidate", "Proof")
        self.actions["commit"] = "drop"
        self.assertIn("retry", alpha.run("hosted-publish", "--installation", "desk", *picks, code=1)["error"])
        with alpha.database() as db:
            saved = db.execute("SELECT origin, manifest, revision FROM hosted_package").fetchone()
        alpha.configure(routing(project="beta", owner=VIEWER, installation="different"))
        self.assertIn("already exists", alpha.run("hosted-publish", *picks, code=1)["error"])
        alpha.config.write_text("invalid settings")
        receipt = alpha.run("hosted-publish")
        self.assertEqual(receipt["revision"], saved[2])
        with alpha.database() as db:
            self.assertEqual(db.execute("SELECT origin, manifest, revision FROM hosted_package").fetchone(), saved)
        self.assertEqual(saved[0], "https://" + PRODUCER)
        self.assertEqual(set(json.loads(saved[1])["origin"].items()),
                         {("project", "alpha"), ("installation", "desk"), ("session", alpha.initial["session"])})
        self.assertEqual([item["id"] for item in json.loads(saved[1])["items"]], ["Proof"])
        self.assertNotIn(alpha.env[TOKEN_ENV].encode(), saved[1])

        published = beta.run("hosted-publish", "--project", "beta", *picks)
        path, _ = self.endpoints(alpha, receipt)
        beta_path = "/api/projects/beta/reviews/" + published["review"]
        self.assertEqual(self.human(beta_path, actor=VIEWER)[0], 200)
        self.assertEqual(self.human(beta_path.replace("/beta/", "/alpha/"), actor=VIEWER)[0], 404)
        self.assertEqual(self.decision(path, "Proof", version=0, outcome="accept")[0], 200)
        self.assertEqual(self.freeze(path, receipt["revision"])[0], 200)
        self.assertEqual(alpha.run("hosted-poll")["state"], "delivered")
        self.assertFalse((beta.state / "session.json").exists())

    def test_explicit_publication_flags_override_checked_project_defaults(self):
        consumer = self.consumer("config-overrides", card("Proof"),
                                 config=routing(project="beta", origin="https://wrong.example.ts.net",
                                                owner=VIEWER, installation="wrong"))
        picks = ("--title", "Review caption", "--candidate", "Proof")
        before = len(self.requests)
        for option in (("--origin", "https://" + PRODUCER), ("--project", "alpha"),
                       ("--installation", "desk"), ("--owner", OWNER)):
            refusal = consumer.run("hosted-publish", *option, *picks, code=1)
            self.assertIn("Partial routing flags must match", refusal["error"])
        self.assertEqual(len(self.requests), before)
        with consumer.database() as db:
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='hosted_package'").fetchone())
        consumer.config.write_text("full explicit routing bypasses invalid settings")
        result = consumer.run("hosted-publish", "--origin", "https://" + PRODUCER,
                              "--project", "alpha", "--installation", "desk", "--owner", OWNER, *picks)
        path, _ = self.endpoints(consumer, result)
        self.assertEqual(self.decision(path, "Proof", version=0, outcome="accept")[0], 200)

    def test_actual_hub_offline_publication_and_durable_handback(self):
        assets = [("image/png", png(), "image"), ("audio/wav", wav(), "audio")]
        media = [{"kind": kind, "url": f"data:{mime};base64,{base64.b64encode(raw).decode()}", "label": kind}
                 for mime, raw, kind in assets]
        consumer = self.consumer("alpha-origin", card("Verdict", kind="design", paths=["private/file"], media=media,
                                                     note="Café caption", launch={"command": "private-command"}),
                                 card("Pick", kind="decision", options=["First", "Second"]),
                                 card("Pending", kind="decision", document="Draft copy"),
                                 card("Unshared", kind="decision", document="Other draft"), version=3)
        consumer.run("observe", "Verdict", "--evidence", "Origin-only prior observation")
        selected = ("Pick", "Verdict", "Pending")
        self.actions[hashlib.sha256(assets[0][1]).hexdigest()] = "drop"
        self.assertIn("retry", consumer.publish(*selected, code=1)["error"])
        with consumer.database() as db:
            original, revision = db.execute("SELECT manifest, revision FROM hosted_package").fetchone()
        for private in ("private/file", "private-command", "Unshared", consumer.env[TOKEN_ENV]):
            self.assertNotIn(private.encode(), original)
        self.assertEqual(hashlib.sha256(original).hexdigest(), revision)
        self.assertEqual([entry["id"] for entry in json.loads(original)["items"]], list(selected))
        self.actions["commit"] = "drop"
        consumer.run("hosted-publish", code=1)
        receipt = consumer.run("hosted-publish")
        self.assertEqual((receipt["state"], receipt["revision"]), ("committed", revision))
        self.assertEqual(consumer.run("hosted-poll"), {"state": "waiting"})
        self.assertIn("immutable", consumer.run(*consumer.init, "--hosted", code=1)["error"])
        path, endpoint = self.endpoints(consumer, receipt)
        self.stop(self.processes["producer"])
        self.assertEqual(self.sharing(path)[0], 200)
        self.assertEqual(self.human(path + "/items/Pick/feedback", method="PUT", actor=REVIEWER,
                                    payload={"version": 0, "note": "Hub-only collaboration note"})[0], 200)
        self.assertEqual(self.decision(path, "Pick", version=1, outcome="select", selected=["Second"])[0], 200)
        verdict = json.loads(self.decision(path, "Verdict", version=0, outcome="accept", note="Ship café ☕")[2])["decision"]
        frozen = json.loads(self.freeze(path, revision)[2])
        self.assertEqual(frozen["state"], "waiting")
        self.assertIsNone(consumer.run("status")["handed_back"])
        archive = consumer.state / "session.json"
        self.assertFalse(archive.exists())
        self.restart("collaboration", COLLABORATION)
        self.start("producer", PRODUCER)
        exported = self.human(path + "/handback")[2]
        self.assertEqual(self.producer(endpoint, "GET", revision=revision)[2], exported)
        export_lock = consumer.state / ".export-lock.sqlite3"
        export_lock.mkdir()
        try:
            self.assertIn("pending", consumer.run("hosted-poll", code=1)["error"])
            self.assertIsNone(consumer.run("status")["handed_back"])
            self.assertFalse(archive.exists())
            self.assertEqual(json.loads(self.human(path)[2])["delivery"], "waiting")
        finally:
            export_lock.rmdir()
        crash = consumer.directory / "interrupt_after_archive.py"
        crash.write_text(f"""import os, sys
sys.path.insert(0, {str(SKILL / 'scripts')!r})
import attended_review, review_store
install = review_store.install_archive
def interrupt(*args):
    install(*args)
    os._exit(91)
review_store.install_archive = interrupt
raise SystemExit(attended_review.main())
""")
        consumer.invoke("hosted-poll", script=crash, code=91)
        saved = archive.read_bytes()
        self.assertIsNone(consumer.run("status")["handed_back"])
        self.assertEqual(json.loads(self.human(path)[2])["delivery"], "waiting")
        saved_at = consumer.directory / "copied-archive.json"
        archive.rename(saved_at)
        archive.write_text("Unrelated local result")
        self.assertIn("conflicts", consumer.run("hosted-poll", code=1)["error"])
        self.assertEqual(archive.read_text(), "Unrelated local result")
        self.assertEqual(json.loads(self.human(path)[2])["delivery"], "needs_attention")
        archive.unlink()
        saved_at.rename(archive)
        self.actions["ack"] = "drop"
        consumer.run("hosted-poll", code=1)
        self.assertEqual(json.loads(self.human(path)[2])["delivery"], "delivered")
        with ThreadPoolExecutor(max_workers=2) as workers:
            replies = list(workers.map(lambda _: consumer.run("hosted-poll"), range(2)))
        self.assertEqual(replies[0], replies[1])
        self.assertEqual(replies[0]["delivery"], frozen["delivery"])
        self.assertEqual(archive.read_bytes(), saved)
        self.assertEqual([action for _, _, action, _ in self.requests].count("poll"), 2)
        self.assertNotIn(b"Hub-only collaboration note", saved)
        archive_data = json.loads(saved)
        events = archive_data["events"]
        self.assertEqual([event["kind"] for event in events].count("handed-back"), 1)
        self.assertEqual(events[-1]["sequence"], replies[0]["sequence"])
        self.assertEqual(events[-1]["kind"], "handed-back")
        self.assertEqual(events[-1]["decided"], ["Pick", "Verdict"])
        self.assertEqual(events[-1]["pending"], ["Pending", "Unshared"])
        self.assertEqual(archive_data["candidates"]["Pick"]["decision"]["selected"], ["Second"])
        self.assertEqual(archive_data["candidates"]["Verdict"]["decision"]["actor"], verdict["actor"])
        self.assertEqual(archive_data["candidates"]["Verdict"]["media"], media)
        self.assertIn(b"Origin-only prior observation", saved)
        self.assertIn("Ship café ☕".encode(), saved)
        old = self.earlier_helper(BASELINE)
        self.assertIn("database version", consumer.run("status", script=old, code=1)["error"])
        archive_copy = consumer.directory / "legacy-archive"
        archive_copy.mkdir()
        (archive_copy / "session.json").write_bytes(saved)
        old_status = consumer.run("status", "--after", "0", "--full", script=old, state=archive_copy)
        self.assertEqual(old_status["handed_back"], archive_data["handed_back"])
        self.assertEqual(old_status["events"], events)
        self.assertEqual(consumer.run("wait", "--after", "0", "--kind", "handed-back")["events"], [events[-1]])

    def test_binding_conflicts_and_transport_refusals(self):
        consumer = self.consumer("beta-origin", card("Proof"))
        request_count = len(self.requests)
        refusal = consumer.run("hosted-publish", "--origin", "https://" + PRODUCER, "--project", "alpha",
                               "--installation", "desk", "--owner", OWNER, "--title=" + self.tokens["alpha"],
                               "--candidate", "Proof", code=1)
        self.assertIn("contains the producer credential", refusal["error"])
        failed = consumer.run("hosted-publish", "--origin", "https://wrong.example.ts.net", "--project", "alpha",
                              "--installation", "desk", "--owner", OWNER, "--title", "Test connection",
                              "--candidate", "Proof", code=1)
        self.assertIn("certificate verification", failed["error"])
        self.assertEqual(len(self.requests), request_count)
        other = self.consumer("other-origin", card("Proof"))
        redirect_port = self.proxy()
        self.actions[other.initial["session"]] = "redirect"
        self.assertIn("redirect refused", other.publish("Proof", code=1)["error"])
        self.assertFalse(any(port == redirect_port for port, _, _, _ in self.requests))
        self.assertIn("HTTP 404", other.run("hosted-publish", code=1, env={TOKEN_ENV: self.tokens["beta"]})["error"])
        receipt = other.run("hosted-publish")
        path, endpoint = self.endpoints(other, receipt)
        self.assertNotEqual(consumer.initial["session"], other.initial["session"])
        self.assertEqual(self.decision(path, "Proof", version=0, outcome="reject")[0], 200)
        self.assertEqual(self.freeze(path, receipt["revision"])[0], 200)
        archive = other.state / "session.json"

        def alter(raw, field):
            envelope = json.loads(raw)
            snapshot = envelope["snapshot"]
            if field == "target":
                snapshot["target"]["session"] = consumer.initial["session"]
            elif field == "item":
                snapshot["items"][0]["fingerprint"] = "0" * 64
            if field != "digest":
                data = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
                envelope["digest"] = hashlib.sha256(data).hexdigest()
            else:
                envelope["digest"] = "0" * 64
            return json.dumps(envelope).encode()

        for field in ("digest", "target", "item"):
            self.actions["poll"] = lambda raw, field=field: alter(raw, field)
            self.assertIn("snapshot does not match", other.run("hosted-poll", code=1)["error"])
            self.assertEqual(json.loads(self.human(path)[2])["delivery"], "waiting")
        self.assertFalse(archive.exists())
        other.run("resume-development", "--candidate", "Proof")
        self.assertIn("unprotected", other.run("hosted-poll", code=1)["error"])
        self.assertEqual(json.loads(self.human(path)[2])["delivery"], "needs_attention")
        other.run("prepare")
        conflict = b'{"unrelated":true}\n'
        archive.write_bytes(conflict)
        self.assertIn("conflicts", other.run("hosted-poll", code=1)["error"])
        self.assertEqual(archive.read_bytes(), conflict)
        self.assertIsNone(other.run("status")["candidates"][0]["decision"])
        archive.rename(other.directory / "retained.json")
        self.assertEqual(other.run("hosted-poll")["state"], "delivered")
        self.assertEqual(self.producer(endpoint, "GET", revision=receipt["revision"])[0], 204)
        self.assertEqual((other.directory / "retained.json").read_bytes(), conflict)
        self.assertFalse((consumer.state / "session.json").exists())
