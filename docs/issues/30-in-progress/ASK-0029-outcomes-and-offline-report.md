---
schema: "implement-rfc.card.v1"
id: "ASK-0029"
title: "Join task outcomes and produce offline comparison reports"
status: "In Progress"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0027", "ASK-0028"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "outcomes-and-offline-report"}
---

# ASK-0029: Join task outcomes and produce offline comparison reports

Governing RFCs: [RFC-ASK-0007](../../rfcs/RFC-ASK-0007-usage-accounting-outcomes-and-experiments.md).

## Objective and owned paths

Join captured operational events to existing acceptance references without a second task board. Produce REPORT.md, summary.json and compact CSVs by project/worktree/task/role/route and primary/child. Keep unassigned sessions, account readings, unknown ownership and possible copied-history duplication visible. Separate wait/list from messaging/spawning and mixed control/engineering requests. Include all attempts/reviews/repair and reopened outcomes in comparisons. Supply treatment IDs and a small experiment configuration independent of provider model calls.

Own only: `skills/implement-rfc/scripts/usage_report.py`; `skills/implement-rfc/scripts/usage_outcomes.py`; `skills/implement-rfc/tests/test_usage_report.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Report-produced, collected and accepted are distinguishable; zero accepted tasks is not a misleading zero-cost success.
- A corrupt/traversing/oversized/duplicate-entry archive is rejected; different-schema evidence remains immutable and explained.

Criterion coverage: RFC-ASK-0007-AC04, RFC-ASK-0007-AC05, RFC-ASK-0007-AC06.

## Focused verification

Run deterministic valid/invalid archive fixtures, hand-checked all-in task totals, mixed-account and reopened-outcome comparisons. Review a redacted sample report for understandable unknowns.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
