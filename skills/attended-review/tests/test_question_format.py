"""Manifest version 3: named parts, kinds, checks, waivers, shared setup and the
build launch check, through the public CLI in disposable checkouts."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "scripts" / "attended_review.py"
spec = importlib.util.spec_from_file_location("attended_question_format", SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
sys.path.insert(0, str(PACKAGE / "examples"))
import question_kinds  # noqa: E402

_machine_config = tempfile.TemporaryDirectory()


def setUpModule():
    patcher = mock.patch.dict(os.environ, {"ATTENDED_REVIEW_HUB_CONFIG": str(Path(_machine_config.name) / "absent" / "hub.json")})
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)
    unittest.addModuleCleanup(_machine_config.cleanup)


class QuestionFormatTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "checkout"
        self.root.mkdir()

    def cli(self, *args, success=True):
        process = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo-root", str(self.root), "--registry", str(self.base / "registry"), *args],
                                 capture_output=True, text=True, timeout=30)
        if success:
            self.assertEqual(process.returncode, 0, process.stderr)
            return json.loads(process.stdout)
        return process

    def write(self, value, name="manifest.json"):
        path = self.base / name
        path.write_text(json.dumps(value))
        return str(path)

    def session_bytes(self):
        path = self.root / ".mask/attended-review/session.json"
        return path.read_bytes() if path.exists() else None

    def test_each_kind_is_admitted_and_its_parts_render_in_order_live_and_offline(self):
        result = self.cli("init", "--manifest", self.write(question_kinds.passing()))
        self.assertEqual(result["checks"]["format"], "checked")
        self.assertEqual(result["checks"]["violations"], [])
        self.assertEqual(result["schema_version"], 3)
        state = json.loads(self.session_bytes())
        self.assertEqual((state["runtime_format"], state["minimum_helper_version"]), ("attended-review.state.v3", 3))
        self.assertEqual({c["kind"] for c in state["candidates"].values()}, {"build", "design", "decision", "audio"})
        self.cli("prepare")
        self.cli("ready", "import-preview-b", "--evidence", "Launch check: started, stayed open, landed on Settings")
        # A live refresh leaves out the images the page already holds for this fingerprint.
        lean = {c["id"]: c for c in review.Session(self.root, self.base / "registry").page_status(material=False)["candidates"]}
        self.assertEqual(lean["import-preview-b"]["material_omitted"], ["now", "reference"])
        self.assertNotIn("now", lean["import-preview-b"])
        node = shutil.which("node")
        if not node:
            self.skipTest("Node is used only for deterministic page tests, not the runtime")
        snapshot = self.base / "snapshot.json"
        snapshot.write_text(json.dumps(self.cli("status", "--full")))
        result = subprocess.run([node, str(PACKAGE / "tests/review_page.test.js"), "--parts", str(snapshot)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        # The offline file embeds the same parts the live page reads.
        page = self.base / "review.html"
        self.cli("html", "--output", str(page))
        embedded = json.loads(re.search(r"const embedded=(\{.*?\});\n", page.read_text(), re.S).group(1).replace("\\u003c", "<"))
        build = next(c for c in embedded["candidates"] if c["id"] == "import-preview-b")
        self.assertEqual([build[k] for k in ("why", "not_in_round")], [question_kinds.IMPORT_PREVIEW["why"], question_kinds.IMPORT_PREVIEW["not_in_round"]])

    def test_a_build_question_waits_for_its_launch_check(self):
        build = {**question_kinds.IMPORT_PREVIEW, "id": "static"}
        checked = {**build, "id": "checked", "prepare": {"argv": [sys.executable, "-c", "pass"]}}
        failing = {**build, "id": "failing", "prepare": {"argv": [sys.executable, "-c", "raise SystemExit(3)"]}}
        self.cli("init", "--manifest", self.write({"schema_version": 3, "candidates": [build, checked, failing]}))
        phases = {c["id"]: c for c in self.cli("prepare")["candidates"]}
        self.assertEqual(phases["static"]["phase"], "waiting")
        self.assertFalse(phases["static"]["protected"])
        self.assertIn("launch check", phases["static"]["error"])
        self.assertEqual(phases["checked"]["phase"], "ready")
        self.assertEqual(phases["failing"]["phase"], "waiting")
        # Static preparation again changes nothing and adds no event.
        sequence = self.cli("status")["sequence"]
        self.cli("prepare")
        self.assertNotIn("static", [e.get("candidate") for e in self.cli("status", "--after", str(sequence))["events"]])
        self.cli("ready", "static", "--evidence", "Launch check: opened on the import dialog with the sample file")
        current = {c["id"]: c for c in self.cli("status")["candidates"]}
        self.assertEqual((current["static"]["phase"], current["static"]["protected"]), ("ready", True))
        # A version-2 question with a launch is still made ready by static preparation.
        legacy = {"id": "legacy", "title": "Legacy", "revision": "r", "criteria": ["c"], "launch": {"command": "open x"}}
        self.cli("init", "--manifest", self.write({"schema_version": 2, "candidates": [legacy]}))
        self.assertEqual({c["id"]: c["phase"] for c in self.cli("prepare")["candidates"]}["legacy"], "ready")

    def test_a_manifest_breaking_several_rules_is_refused_whole_and_check_reports_the_same(self):
        manifest = question_kinds.failing()
        manifest["candidates"].append({**question_kinds.IMPORT_PREVIEW, "id": "fine"})
        manifest["candidates"].append({"id": "pick", "kind": "design", "title": "Pick one", "revision": "r", "criteria": ["c"],
                                       "options": ["A", "B", "C", "D", "E", "F", "G"]})
        path = self.write(manifest)
        refused = self.cli("init", "--manifest", path, success=False)
        self.assertEqual(refused.returncode, 1)
        error = json.loads(refused.stderr)
        rules = sorted((v["candidate"], v["rule"]) for v in error["violations"])
        self.assertEqual(rules, sorted([
            ("BPR-2032-import-preview-b", "no-long-hex"), ("BPR-2032-import-preview-b", "no-tracker-id"),
            ("BPR-2032-import-preview-b", "no-tracker-id"), ("BPR-2032-import-preview-b", "no-path-or-url"),
            ("BPR-2032-import-preview-b", "title-words"), ("BPR-2032-import-preview-b", "build-now-image"),
            ("BPR-2032-import-preview-b", "build-reference"), ("pick", "option-count"), ("pick", "design-image"),
            *[("pick", "design-option-image")] * 7]))
        for violation in error["violations"]:
            self.assertIn(violation["rule"], review.RULES)
            self.assertTrue(violation["fix"])
            self.assertIn(violation["rule"], error["error"])
        self.assertIsNone(self.session_bytes(), "nothing was saved")
        # An existing session is untouched by a refused manifest.
        self.cli("init", "--manifest", self.write(question_kinds.passing(), "passing.json"))
        before = self.session_bytes()
        self.assertEqual(self.cli("init", "--manifest", path, success=False).returncode, 1)
        self.assertEqual(self.session_bytes(), before)
        checked = self.cli("check", "--manifest", path, success=False)
        self.assertEqual(checked.returncode, 1)
        report = json.loads(checked.stdout)
        self.assertEqual(report["violations"], error["violations"])
        self.assertEqual((report["format"], report["refused"]), ("checked", True))
        self.assertEqual(self.session_bytes(), before)
        # check needs no session at all.
        elsewhere = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo-root", str(self.base / "missing"), "check",
                                    "--manifest", self.base / "passing.json"], capture_output=True, text=True, timeout=30)
        self.assertEqual(elsewhere.returncode, 0, elsewhere.stderr)
        self.assertFalse(json.loads(elsewhere.stdout)["refused"])

    def test_a_waiver_admits_the_question_shows_its_reason_and_binds_the_fingerprint(self):
        question = {"id": "shortcut", "kind": "build", "title": "Does Ctrl+I open the import dialog?", "revision": "r",
                    "criteria": ["It opens from the main window."], "launch": {"command": "open x"}, "reference": "none"}
        self.assertEqual(self.cli("init", "--manifest", self.write({"schema_version": 3, "candidates": [question]}), success=False).returncode, 1)
        waived = {**question, "waivers": {"build-now-image": "No screenshot: the change is a keyboard shortcut."}}
        result = self.cli("init", "--manifest", self.write({"schema_version": 3, "candidates": [waived]}))
        self.assertEqual(result["checks"]["waivers"], 1)
        self.assertEqual([(w["rule"], w["reason"]) for w in result["checks"]["waived"]],
                         [("build-now-image", "No screenshot: the change is a keyboard shortcut.")])
        first = result["candidates"][0]["fingerprint"]
        self.cli("ready", "shortcut", "--evidence", "Launch check: done")
        page = self.base / "review.html"
        self.cli("html", "--output", str(page))
        self.assertIn("No screenshot: the change is a keyboard shortcut.", page.read_text())
        self.cli("resume-development", "--all")
        reworded = {**question, "waivers": {"build-now-image": "No screenshot: only a key press changes."}}
        second = self.cli("init", "--manifest", self.write({"schema_version": 3, "candidates": [reworded]}))["candidates"][0]["fingerprint"]
        self.assertNotEqual(first, second)
        for waivers in ({"build-now-image": " "}, {"no-such-rule": "reason"}, {"kind-required": "reason"}):
            bad = {**question, "id": "bad", "waivers": waivers}
            self.assertEqual(self.cli("check", "--manifest", self.write({"schema_version": 3, "candidates": [bad]}), success=False).returncode, 1)
        long_reason = {**question, "id": "long", "waivers": {"build-now-image": " ".join(["word"] * 26)}}
        report = json.loads(self.cli("check", "--manifest", self.write({"schema_version": 3, "candidates": [long_reason]}), success=False).stdout)
        self.assertEqual([v["rule"] for v in report["violations"]], ["waiver-reason-words"])

    def test_shared_setup_is_stated_once_and_every_question_keeps_its_launch(self):
        manifest = question_kinds.passing()
        result = self.cli("init", "--manifest", self.write(manifest))
        state = json.loads(self.session_bytes())["candidates"]
        group = [c for c in state.values() if c.get("setup")]
        self.assertEqual(len(group), 2)
        setup = manifest["setups"]["frozen-build"]
        for item in group:
            self.assertEqual(item["setup"], {"id": "frozen-build", "note": setup["note"]})
            self.assertEqual(item["launch"], setup["launch"])
        before = {c["id"]: c["fingerprint"] for c in result["candidates"]}
        manifest["setups"]["frozen-build"]["note"] = "One frozen build for both questions."
        changed = review.Session(self.root, self.base / "registry")
        changed.initialize(json.loads(json.dumps(manifest)))
        after = {c["id"]: c["fingerprint"] for c in changed.status()["candidates"]}
        self.assertNotEqual(before["import-shortcut"], after["import-shortcut"], "the setup note binds the fingerprint")
        self.assertEqual(before["toolbar-icons"], after["toolbar-icons"])
        manifest["setups"]["frozen-build"]["note"] = " ".join(["word"] * 41)
        report = json.loads(self.cli("check", "--manifest", self.write(manifest), success=False).stdout)
        self.assertEqual([v["rule"] for v in report["violations"]], ["setup-note-words"])
        for invalid in ({"schema_version": 3, "candidates": [{**question_kinds.IMPORT_PREVIEW, "setup": "missing"}]},
                        {"schema_version": 2, "setups": {}, "candidates": []}):
            self.assertEqual(self.cli("check", "--manifest", self.write(invalid), success=False).returncode, 1)

    def test_legacy_manifests_are_admitted_with_violations_reported(self):
        legacy = {"id": "APP-0042-layout", "title": "Review the layout for BPR-2032 at /Users/reviewer/app",
                  "revision": "prepared-build-2026-09-05.2", "criteria": ["Labels are readable"],
                  "content": "Open the prepared build.", "launch": {"label": "Open", "command": "open /Applications/Thing.app"},
                  "copy": [{"label": "PR", "value": "https://example.test/pull/7"}], "options": ["A", "B"]}
        audio = {"id": "death-C", "title": "Death C", "revision": "synthetic-2", "criteria": ["Judge"], "question_type": "audio",
                 "comparison_group": "death", "audio": {"url": "data:audio/wav;base64,UklGRg==", "purpose": "Death cue", "scope": "Creative fit only"},
                 "media": [{"kind": "image", "url": "data:image/png;base64,AA", "label": "waveform"}]}
        # Golden fingerprints captured from the RFC_BASE_SHA helper (5fd9ad3).
        golden = {"APP-0042-layout": "5dbe21154f2e0608279e367179243c69b07964941a1ce7b2d88aab7cdc270777",
                  "death-C": "cd46adaf6988dbbee16413ef0472a1ccce7b486d6743db68437fcb49b679af78"}
        for version, candidates in ((1, [legacy]), (2, [legacy, audio])):
            with self.subTest(version=version):
                self.root = self.base / f"checkout-{version}"
                self.root.mkdir()
                result = self.cli("init", "--manifest", self.write({"schema_version": version, "candidates": candidates}))
                checks = result["checks"]
                self.assertEqual((checks["format"], checks["refused"]), ("unchecked legacy format", False))
                self.assertEqual({v["rule"] for v in checks["violations"]}, {"no-tracker-id", "no-path-or-url", "build-now-image"})
                self.assertEqual({c["id"]: c["fingerprint"] for c in result["candidates"]}, {c["id"]: golden[c["id"]] for c in candidates})
                state = json.loads(self.session_bytes())
                self.assertEqual(state["schema_version"], version)
                self.assertNotIn("checks", json.dumps(state))
                self.assertFalse(self.cli("check", "--manifest", self.write({"schema_version": version, "candidates": candidates}))["refused"])
        # Version 3 fields are unknown to earlier versions, so their identity cannot change.
        self.assertEqual(self.cli("check", "--manifest", self.write({"schema_version": 2, "candidates": [{**legacy, "kind": "build"}]}),
                                  success=False).returncode, 1)

    def test_the_guide_example_passes_within_eighty_words(self):
        guide = (PACKAGE / "references/question-authoring.md").read_text()
        after = guide.split("## Before and after", 1)[1]
        example = json.loads(re.search(r"```json\n(.*?)```", after, re.S).group(1))
        report = self.cli("check", "--manifest", self.write(example))
        self.assertEqual((report["refused"], report["violations"], report["waived"]), (False, [], []))
        question = example["candidates"][0]
        self.assertLessEqual(report["words"][question["id"]], 80)
        self.assertEqual(report["words"][question["id"]], 75)
        self.assertEqual(question["kind"], "build")
        shared = {k: v for k, v in question_kinds.IMPORT_PREVIEW.items() if k not in ("reference", "now")}
        self.assertEqual({k: v for k, v in question.items() if k not in ("reference", "now")}, shared,
                         "the portable example carries the guide's question")

    def test_text_patterns(self):
        for text in ("open /Users/reviewer/app", "see https://example.test", "~/build/x", "C:\\Users\\x", "(/tmp/a/b)"):
            self.assertTrue(review.PATH_OR_URL.search(text), text)
        for text in ("and/or", "Update / Leave out", "1/2 done", "/help"):
            self.assertFalse(review.PATH_OR_URL.search(text), text)
        for text in ("BPR-2032", "RFC-BPR-0112", "ASK-0134 done"):
            self.assertTrue(review.TRACKER_ID.search(text), text)
        for text in ("SHA-256 digest", "ISO-8601 date", "UTF-8 text", "AC02", "x86-64"):
            self.assertFalse(review.TRACKER_ID.search(text), text)
        self.assertTrue(review.LONG_HEX.search("frozen 18a70bb96087"))
        self.assertFalse(review.LONG_HEX.search("build 8af4a4501 and acceptability"))

    def test_documents_name_the_same_parts_kinds_limits_and_rules(self):
        guide = (PACKAGE / "references/question-authoring.md").read_text()
        contract = (PACKAGE / "references/session-contract.md").read_text()
        skill = (PACKAGE / "SKILL.md").read_text()
        examples = (PACKAGE / "examples/README.md").read_text()
        rules = guide.split("## Rules", 1)[1].split("\n### ", 1)[0]
        table = set(re.findall(r"^\| `([a-z-]+)` \|", rules, re.M))
        self.assertEqual(table, set(review.RULES), "the guide's rule table is the helper's rule set")
        section = contract.split("## Question format (manifest version 3)", 1)[1].split("\n## ", 1)[0]
        for rule in review.RULES:
            self.assertIn(f"`{rule}`", section, rule)
        limits = {"title-words": 12, "why-words": 25, "check-count": 3, "check-words": 20, "step-count": 5, "step-words": 20,
                  "not-in-round-count": 3, "not-in-round-words": 15, "note-words": 60, "option-count": 6, "option-words": 15,
                  "image-label-words": 12, "waiver-reason-words": 25, "setup-note-words": 40}
        for rule, limit in limits.items():
            self.assertRegex(section, rf"`{rule}` {limit}\b", rule)
            self.assertRegex(review.RULES[rule][0], rf"\b{limit}\b", rule)
        for kind in review.KINDS:
            self.assertIn(f"`{kind}`", guide)
            self.assertIn(f"`{kind}`", section)
        for field in ("why", "reference", "now", "steps", "links", "not_in_round", "note", "document", "waivers", "setup"):
            self.assertIn(f"`{field}`", guide, field)
            self.assertIn(f"`{field}`", section, field)
        self.assertEqual(review.UNWAIVABLE, {"kind-required", "setup-note-words", "waiver-reason-words"})
        self.assertIn("references/question-authoring.md", skill)
        self.assertIn("question_kinds.py", examples)
        for text in (skill, guide, section, examples):
            self.assertNotRegex(text, r"(?i)migrat(ed|es) (a|the) consumer")


if __name__ == "__main__":
    unittest.main()
