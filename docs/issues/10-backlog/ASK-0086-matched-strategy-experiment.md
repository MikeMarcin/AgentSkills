---
schema: "implement-rfc.card.v1"
id: "ASK-0086"
title: "Run one real matched strategy block"
status: "Backlog"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0084"]
metadata: {"packet":"implement-rfc-execution-strategies-v2","milestone":"M4","milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
---

# ASK-0086: Run one real matched strategy block

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Owner selects task and budgets later; freeze candidates, independent blind judgments and repairs, and report quality, adherence, usage and coverage separately.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.
