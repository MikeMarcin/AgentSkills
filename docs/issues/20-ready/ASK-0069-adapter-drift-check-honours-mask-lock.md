---
schema: "implement-rfc.card.v1"
id: "ASK-0069"
title: "Judge consumer adapters against the MASK lock, not the legacy render manifest"
status: "Ready"
rfcs: []
depends_on: []
priority: "P2"
metadata: {"origin": "mask ensure --all --repair on 2026-09-11 left validate_portable_agents --repo-root red in two consumers", "skills": ["implement-rfc"]}
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

Run `python3 -B -m unittest discover -s skills/implement-rfc/tests -p 'test_render_runtime_adapters.py'`, then the two consumer checks and the documentation gate. Not started.
