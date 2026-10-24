---
schema: "implement-rfc.card.v1"
id: "ASK-0121"
title: "Preserve adopted plan discovery above the live lookup cap"
status: "Ready"
rfcs: ["RFC-ASK-0012"]
depends_on: []
metadata: {"discovered_by":"Grapho headless-text-foundation integration", "baseline":"73676198110acaaa788a8895dcc574aac4c0b10b"}
---

# Preserve adopted plan discovery above the live lookup cap

## Scope and acceptance

Repair target-only discovery in `skills/implement-rfc/scripts/milestone_plan.py` when a fully adopted live linkage exists in a consumer with more than 256 plans. Preserve the bounded refusal for unlinked recovery and the stale/ambiguous linkage checks. Own only that helper, its focused tests and this follow-up bookkeeping; original RFC-ASK-0012 native qualification and closeout remain pending.

Reproduce the 257-plan failure, verify linked consumers resolve their adopted plan without increasing the unlinked scan bound, and verify interrupted/stale linkage remains refused. Run focused milestone-plan/checkpoint/public composition tests plus portable source and documentation gates. Deploy only the explicitly authorized AITO binding through MASK; do not publish or edit an immutable store payload.

## Execution record

Mandate: resume Grapho first-milestone integration only. This bounded repair supplies its missing supported checkpoint path. Original RFC_BASE_SHA and acceptance history remain on [ASK-0066](../10-backlog/ASK-0066-close-milestone-handling.md).
