---
schema: "implement-rfc.card.v1"
id: "ASK-0069"
title: "Judge consumer adapters against the MASK lock, not the legacy render manifest"
status: "Done"
rfcs: []
depends_on: []
priority: "P2"
metadata: {"origin": "mask ensure --all --repair on 2026-09-11 left validate_portable_agents --repo-root red in two consumers", "skills": ["implement-rfc"]}
acceptance: [{"criterion":"consumer-checks-pass-under-mask-lock","outcome":"pass","revision":"a70b4f1561d4f7527e971d936f438513c05a408c","evidence":{"kind":"command","detail":"validate_portable_agents.py --repo-root passes for SampleReview and SamplePlanner after mask ensure --all --repair re-staged the roles; legacy manifest reported as ignored."}},{"criterion":"drifted-adapter-still-fails-under-lock","outcome":"pass","revision":"a70b4f1561d4f7527e971d936f438513c05a408c","evidence":{"kind":"command","detail":"test_mask_locked_consumer_is_judged_by_lock_and_fresh_render: an appended line makes --check exit 1 with stale generated file and lock drift."}},{"criterion":"direct-render-refused-under-lock","outcome":"pass","revision":"a70b4f1561d4f7527e971d936f438513c05a408c","evidence":{"kind":"command","detail":"Same test: render without --check exits 2 naming mask ensure; the 19 fixture renderer tests are unchanged and pass."}},{"criterion":"manifest-and-gates","outcome":"pass","revision":"a70b4f1561d4f7527e971d936f438513c05a408c","evidence":{"kind":"command","detail":"--write-source-manifest regenerated; --source-only valid; documentation gate 0 violations; full suite 462 tests OK."}}]
---

# ASK-0069: Judge consumer adapters against the MASK lock, not the legacy render manifest

## Problem

`validate_portable_agents.py --repo-root CONSUMER` and `render_runtime_adapters.py --check` judge a consumer's `.claude/agents` and `.codex/agents` files against `.mask/generated/implement-rfc/runtime-adapters.json`, the publication manifest the renderer writes when it renders directly into a consumer. MASK does not use that path: `prepare_mask_roles.py` stages role files and MASK publishes them under `.mask/skill-config/implement-rfc/native-roles.lock.json`. In SampleReview and SamplePlanner every installed adapter is byte-identical to a fresh render and matches the lock, yet the check reports "stale generated file or unrecognized existing adapter" because the manifest still carries the 2026-09-08 digests.

## Objective and owned paths

Owned surfaces: `skills/implement-rfc/scripts/render_runtime_adapters.py` (`publish_adapters` check path and direct-render guard), `skills/implement-rfc/scripts/validate_portable_agents.py` if its reporting needs the distinction, `skills/implement-rfc/tests/test_render_runtime_adapters.py`, `skills/implement-rfc/README.md` where the drift check is described.

## Bounded work

- When the consumer carries a MASK lock, the check compares each installed adapter against the fresh render and against the lock's recorded digest. A file equal to the fresh render is current; one that differs is stale; a lock that disagrees with the files is lock drift that names `mask ensure`. The legacy manifest is reported as ignored, never as the verdict.
- Without a lock, behaviour is unchanged: the manifest remains the publication record.
- Direct rendering (no `--check`) into a MASK-managed consumer refuses with a message naming `mask ensure`, so the two publication records cannot diverge again.
- Tests cover: lock present and files current; lock present and one file stale; lock disagreeing with files; no lock (existing behaviour); direct render refused under a lock.

## Acceptance

- `validate_portable_agents.py --repo-root` passes for SampleReview and SamplePlanner with their committed locks and installed adapters unchanged.
- A consumer whose installed adapter differs from the fresh render still fails the check under a lock.
- Direct render into a locked consumer is refused; the fixture-based renderer tests keep passing.
- Portable source manifest regenerated; documentation gate and portable validation pass.

## Verification and execution record

Source revision a70b4f1561d4f7527e971d936f438513c05a408c. Renderer tests: 20 pass, including the new locked-consumer test (current files pass with a stale legacy manifest; a drifted file reports stale and lock drift; a lock disagreeing with current files reports lock drift only; direct render refused with a `mask ensure` message). Full implement-rfc discovery: 462 tests, 8 skipped, 0 failures. Portable source manifest regenerated and valid; documentation gate 12 RFCs, 69 cards, 0 violations.

Consumer checks, 2026-09-11: the renderer edit itself changes every adapter's header digest, so MASK's doctor reported setup required and `mask ensure --all --repair` re-staged the roles (102 backups). After that, `validate_portable_agents.py --repo-root` passes for SampleReview (17 files, source ea04ecde) and SamplePlanner (17 files, source 373ca930), each noting the ignored legacy manifest. SamplePlanner also carried four gitignored retired adapters (rfc-critical-reviewer and rfc-worker-routine, both providers) that MASK does not remove; they were deleted by hand. Adapters are gitignored in both consumers; only the locks are tracked and were committed after the re-stage.
