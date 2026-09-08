---
schema: "implement-rfc.card.v1"
id: "ASK-0034"
title: "Implement the capability-checked Claude companion adapter"
status: "In Progress"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0032"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "claude-stream-adapter"}
---

# ASK-0034: Implement the capability-checked Claude companion adapter

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Use supported print/stream-json sessions with exact runner-owned native session IDs and observed final result/usage. Translate role read/write/build constraints explicitly; a child process does not automatically inherit interactive tool policies. Keep same-context report recovery distinct from native interactive Agent/SendMessage capabilities. No transcript-tail ingestion into the parent, screen scraping, or silently broadened allowed tools.

Own only: `skills/implement-rfc/scripts/slice_claude.py`; `skills/implement-rfc/tests/test_slice_claude.py`; `skills/implement-rfc/references/bounded-execution.md`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Structured result/error/max-turn markers are distinguished from quoted text and missing reports.
- One bounded permitted recovery is possible for the controlled session path; unsupported native subagents return a truthful limitation.

Criterion coverage: RFC-ASK-0005-AC04, RFC-ASK-0005-AC05.

## Focused verification

Fake stream tests cover final aggregate usage, partial and failed result, malformed/oversized stream, cancellation and session mismatch. Add one approved installed-CLI smoke before claiming support.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
