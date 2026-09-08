---
schema: "implement-rfc.card.v1"
id: "ASK-0023"
title: "Harden streaming provider capture, provenance and archive bounds"
status: "Done"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0022"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "capture-core-and-bounds"}
acceptance: [{"criterion":"RFC-ASK-0006-AC03/AC04/AC05 capture core","outcome":"pass","revision":"da9724ebf12b4cb7e8ece991178c51f74312f264","evidence":{"kind":"observation","detail":"51 scope/capture tests pass (python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_usage_*.py). Generated stress: 29,557,929 bytes fully scanned, 30,000 events, 3.799 seconds, 244,499-byte tracemalloc peak, 16,357,788 output bytes. SQLite indexes and streamed session arrays; torn/oversized records, concurrent append, newest baseline, private sentinels, exclusive output and interrupted publish exercised. Native qualification remains ASK-0024/0025. Temporary fixtures cleaned."}}]
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
