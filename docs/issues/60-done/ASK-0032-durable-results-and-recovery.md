---
schema: "implement-rfc.card.v1"
id: "ASK-0032"
title: "Add durable dispatch, report collection and bounded recovery"
status: "Done"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0031", "ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "durable-results-and-recovery"}
acceptance: [{"criterion":"RFC-ASK-0005-AC03/AC04 durable core","outcome":"pass","revision":"5f272132e70c05ce60e5464d475c24baa42fd267","evidence":{"kind":"command","command":"python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_slice_recovery.py","exit_code":0,"detail":"9 tests pass: crash intent refuses redispatch, both child/scout schedules, exact identity rejection, report/completion order, single report-only recovery, cancellation refusal, locking, torn tail, privacy projection, and 1000 idle/duplicate events without model polling. Native driver qualification remains separate."}}]
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
