#!/usr/bin/env python3
"""Fixture-only tests for the offline art review package."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import build_art_review as review  # noqa: E402


PNG_A = b"\x89PNG\r\n\x1a\nfixture-isolation-a"
PNG_B = b"\x89PNG\r\n\x1a\nfixture-context-b"


class ArtReviewPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "isolation.png").write_bytes(PNG_A)
        (self.root / "context.png").write_bytes(PNG_B)
        (self.root / "model.glb").write_bytes(b"fixture glb identity")
        self.source = {
            "schema_name": review.INPUT_SCHEMA,
            "schema_version": 1,
            "project_id": "fixture-project",
            "title": "Fixture <script>alert(1)</script> Review",
            "review_gate": "generated_model",
            "candidates": [
                {
                    "candidate_id": "art-candidate:/fixture/chair/v001",
                    "asset_key": "fixture-chair",
                    "display_name": "Fixture Chair",
                    "description": "A test-only chair.",
                    "scene_role": "Exercises the review renderer.",
                    "acceptance_criteria": ["Readable silhouette", "Matches the fixture"],
                    "known_concerns": ["Not real art"],
                    "isolation_media": [{"label": "Front", "path": "isolation.png"}],
                    "context_media": [{"label": "Scene", "path": "context.png"}],
                    "identity_files": [{"label": "Model", "path": "model.glb"}],
                }
            ],
        }
        self.input_path = self.root / "batch.json"
        self.write_source()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_source(self) -> None:
        self.input_path.write_text(json.dumps(self.source), encoding="utf-8")

    def test_build_is_deterministic_and_path_local(self) -> None:
        first = self.root / "out-a"
        second = self.root / "out-b"
        manifest = review.build(self.input_path, first)
        review.build(self.input_path, second)

        first_files = sorted(path.relative_to(first) for path in first.rglob("*") if path.is_file())
        second_files = sorted(path.relative_to(second) for path in second.rglob("*") if path.is_file())
        self.assertEqual(first_files, second_files)
        for relative in first_files:
            self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())

        page = (first / "index.html").read_text(encoding="utf-8")
        manifest_text = (first / "art-review-manifest.json").read_text(encoding="utf-8")
        self.assertNotIn(str(self.root), page)
        self.assertNotIn(str(self.root), manifest_text)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("Fixture &lt;script&gt;alert(1)&lt;/script&gt; Review", page)
        self.assertIn("Copy verdict for Codex", page)
        self.assertIn('class="review-controls" aria-label="Review progress and export"', page)
        self.assertIn('class="review-controls-row"', page)
        self.assertIn('id="review-status" role="status" aria-live="polite" aria-atomic="true"', page)
        self.assertIn("Show pending only", page)
        self.assertIn("position: sticky", page)
        self.assertNotIn(".review-controls { position: static; }", page)
        toolbar_start = page.index('<section class="review-controls"')
        toolbar_end = page.index("</section>", toolbar_start)
        self.assertIn('id="review-status"', page[toolbar_start:toolbar_end])
        self.assertIn("<h2>Final result</h2>", page)
        self.assertFalse(any(line and not line.strip() for line in page.splitlines()))
        self.assertEqual(manifest["review_scope"], review.REVIEW_SCOPE)
        self.assertEqual(manifest["downstream_claims"], review.DOWNSTREAM_CLAIMS)
        candidate = manifest["candidates"][0]
        self.assertTrue(candidate["candidate_digest"].startswith("sha256:"))
        self.assertEqual(
            (first / candidate["isolation_media"][0]["path"]).read_bytes(), PNG_A
        )
        self.assertEqual(
            (first / candidate["context_media"][0]["path"]).read_bytes(), PNG_B
        )

    def test_rejects_duplicate_ids_and_missing_review_context(self) -> None:
        self.source["candidates"].append(copy.deepcopy(self.source["candidates"][0]))
        self.write_source()
        with self.assertRaisesRegex(review.ReviewError, "candidate_id values must be unique"):
            review.build(self.input_path, self.root / "duplicate-output")

        self.source["candidates"] = [self.source["candidates"][0]]
        self.source["candidates"][0]["context_media"] = []
        self.write_source()
        with self.assertRaisesRegex(review.ReviewError, "context_media must contain"):
            review.build(self.input_path, self.root / "missing-output")

    def test_verdict_requires_an_exact_complete_partition_and_false_claims(self) -> None:
        manifest = review.build(self.input_path, self.root / "review-output")
        candidate = manifest["candidates"][0]
        identity = {
            "candidate_id": candidate["candidate_id"],
            "candidate_digest": candidate["candidate_digest"],
        }
        verdict = {
            "schema_name": review.VERDICT_SCHEMA,
            "schema_version": 1,
            "batch_id": manifest["batch_id"],
            "review_gate": manifest["review_gate"],
            "review_scope": review.REVIEW_SCOPE,
            "accepted_candidates": [identity],
            "rejected_candidates": [],
            "notes_by_candidate_identity": {
                f"{identity['candidate_id']}@{identity['candidate_digest']}": "fixture note"
            },
            "downstream_claims": review.DOWNSTREAM_CLAIMS,
        }
        review.validate_verdict(manifest, verdict)

        incomplete = copy.deepcopy(verdict)
        incomplete["accepted_candidates"] = []
        with self.assertRaisesRegex(review.ReviewError, "partition is not exact"):
            review.validate_verdict(manifest, incomplete)

        mismatched = copy.deepcopy(verdict)
        mismatched["accepted_candidates"][0]["candidate_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(review.ReviewError, "partition is not exact"):
            review.validate_verdict(manifest, mismatched)

        elevated = copy.deepcopy(verdict)
        elevated["downstream_claims"]["runtime_promotion_approved"] = True
        with self.assertRaisesRegex(review.ReviewError, "false-only claim set"):
            review.validate_verdict(manifest, elevated)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for the browserless runtime test")
    def test_browserless_runtime(self) -> None:
        runtime = SCRIPT_DIR.parent / "assets" / "art_review_runtime.js"
        runner = self.root / "runtime-test.js"
        runner_source = r"""
const assert = require("assert");
require(__RUNTIME_PATH__);
const api = globalThis.SampleArtIsolationReview;
const candidateA = {candidate_id: "candidate-a", candidate_digest: "sha256:aaa"};
const candidateB = {candidate_id: "candidate-b", candidate_digest: "sha256:bbb"};
const config = {batch_id: "batch-one", review_gate: "concept_source", candidates: [candidateA, candidateB]};
const storage = api.createMemoryStorage();
assert.notStrictEqual(api.storageKey("batch-one", candidateA), api.storageKey("batch-two", candidateA));
assert.notStrictEqual(api.storageKey("batch-one", candidateA), api.storageKey("batch-one", {...candidateA, candidate_digest: "sha256:changed"}));
const controller = new api.ReviewController(config, storage);
controller.setDecision("candidate-a", "sha256:aaa", "accept");
controller.setNotes("candidate-a", "sha256:aaa", "Keep this exact candidate");
assert.throws(() => controller.buildVerdict(), /remain pending/);
const reloaded = new api.ReviewController(config, storage);
assert.strictEqual(reloaded.state(candidateA).decision, "accept");
assert.strictEqual(reloaded.state(candidateA).notes, "Keep this exact candidate");
const changed = new api.ReviewController({...config, candidates: [{...candidateA, candidate_digest: "sha256:changed"}]}, storage);
assert.strictEqual(changed.summary().pending, 1);
reloaded.setDecision("candidate-b", "sha256:bbb", "reject");
const verdict = reloaded.buildVerdict();
assert.strictEqual(verdict.review_scope, "human_visual_isolation_only");
assert.deepStrictEqual(verdict.accepted_candidates, [candidateA]);
assert.deepStrictEqual(verdict.rejected_candidates, [candidateB]);
assert.ok(Object.values(verdict.downstream_claims).every((value) => value === false));

(async () => {
  let clipboardValue = null;
  assert.strictEqual(await api.copyText("one", {navigator: {clipboard: {writeText: async (value) => { clipboardValue = value; }}}}), "clipboard");
  assert.strictEqual(clipboardValue, "one");
  let selected = false;
  const textarea = {style: {}, setAttribute() {}, select() { selected = true; }};
  const document = {
    createElement: () => textarea,
    body: {appendChild() {}, removeChild() {}},
    execCommand: (command) => command === "copy"
  };
  assert.strictEqual(await api.copyText("two", {document}), "execCommand");
  assert.strictEqual(textarea.value, "two");
  assert.ok(selected);
  selected = false;
  assert.strictEqual(await api.copyText("three", {
    navigator: {clipboard: {writeText: async () => { throw new Error("file origin denied"); }}},
    document
  }), "execCommand");
  assert.strictEqual(textarea.value, "three");
  assert.ok(selected);
})().catch((error) => { console.error(error); process.exit(1); });
"""
        runner.write_text(
            runner_source.replace("__RUNTIME_PATH__", json.dumps(str(runtime))),
            encoding="utf-8",
        )
        completed = subprocess.run(
            ["node", str(runner)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)


if __name__ == "__main__":
    unittest.main()
