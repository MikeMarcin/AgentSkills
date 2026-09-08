---
schema: "implement-rfc.card.v1"
id: "ASK-0027"
title: "Implement conservative request and counter reconciliation"
status: "In Progress"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "consumption-reconciliation"}
---

# ASK-0027: Implement conservative request and counter reconciliation

Governing RFCs: [RFC-ASK-0007](../../rfcs/RFC-ASK-0007-usage-accounting-outcomes-and-experiments.md).

## Objective and owned paths

Create an offline reconciler for v1/v2 captures. Deduplicate Claude response fragments without counting harness aggregates twice; retain incomplete output. Reconcile Codex last/cumulative series with pre-window baseline, reset/fork/ownership and compaction distinctions. Separate role/session grouping from actual assignment attribution. Add dated optional decimal rate cards without labelling rate-equivalent amounts subscription use.

Own only: `skills/implement-rfc/scripts/usage_accounting.py`; `skills/implement-rfc/tests/test_usage_accounting.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Known duplicates, streaming aggregates, cached input subsets and reasoning output subsets do not inflate totals.
- Uncertain ownership, absent baselines/rates or conflicting records produce explicit unknown/aggregate buckets, not guessed exact costs.

Criterion coverage: RFC-ASK-0007-AC01, RFC-ASK-0007-AC02.

## Focused verification

Use hand-calculated ledger fixtures with exact expected totals and deliberately inconsistent records; compare both legacy and new capture shapes. Test all-zero/no-data separately.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
