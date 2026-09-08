---
schema: "implement-rfc.card.v1"
id: "ASK-0023"
title: "Harden streaming provider capture, provenance and archive bounds"
status: "Backlog"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0022"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": true, "packet_key": "capture-core-and-bounds"}
---

# ASK-0023: Harden streaming provider capture, provenance and archive bounds

Governing RFCs: [RFC-ASK-0006](../../rfcs/RFC-ASK-0006-project-aware-turnkey-usage-capture.md).

## Objective and owned paths

Adopt the parser/wrapper seed and remove duplicated legacy entrypoints after compatibility review. Preserve older audit records and current tools/target aliases; capture primaries, children, structured native results and pre-window counter baselines. Stream initial file sizes with visible invalid/torn tails, avoid large-file blind spots and bound dedup/call/session indexes using stdlib temporary storage. Add project-conflict handling and explicit per-event ownership where source metadata allows it. Capture configuration hashes without treating them as injected token counts.

Own only: `skills/implement-rfc/scripts/usage.py`; `skills/implement-rfc/scripts/usage_capture.py`; `skills/implement-rfc/tests/test_usage_capture.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- No raw source/commands/reasoning in default output; unknown fields and roles remain unknown.
- Archive generation is streaming, validates a new destination, never unlinks existing files, and declares gaps instead of claiming complete bills.

Criterion coverage: RFC-ASK-0006-AC03, RFC-ASK-0006-AC04, RFC-ASK-0006-AC05.

## Focused verification

Run parser regression plus hostile-size/malformed/fork/counter-reset fixtures and a large-history generated stress fixture; report scan bytes/time and working-set behavior. Test concurrent append and output interruption.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
