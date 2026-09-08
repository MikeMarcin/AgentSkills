---
schema: "implement-rfc.card.v1"
id: "ASK-0032"
title: "Add durable dispatch, report collection and bounded recovery"
status: "In Progress"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0031", "ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "durable-results-and-recovery"}
---

# ASK-0032: Add durable dispatch, report collection and bounded recovery

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Persist attempt identities, dispatch intent and exactly correlated native events before/after effects. Distinguish execution/report/collection/acceptance. Implement single-writer cooperative recovery and completion_unknown, plus one preapproved report-only recovery budget. Expose safe usage event projection. Reproduce both observed scout schedules, including utilities completing before the scout stops, without relying on the discarded late-spawn explanation.

Own only: `skills/implement-rfc/scripts/slice_runtime.py`; `skills/implement-rfc/scripts/slice_events.py`; `skills/implement-rfc/tests/test_slice_recovery.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Crashes and duplicate/reordered events neither silently relaunch mutations nor leave child results owned only by an expired agent.
- User cancellation remains cancelled; unsupported resumption stops clearly; reports and edits survive failure.

Criterion coverage: RFC-ASK-0005-AC03, RFC-ASK-0005-AC04.

## Focused verification

Use fake native adapters with deterministic replay, crash injection and owned subprocess cancellation. Verify 1,000 idle/completion duplicates cause no model polling or duplicate task dispatch.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
