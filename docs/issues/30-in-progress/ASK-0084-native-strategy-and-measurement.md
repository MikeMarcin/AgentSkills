---
schema: "implement-rfc.card.v1"
id: "ASK-0084"
title: "Native strategy and multi-arm measurement"
status: "In Progress"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0083"]
metadata: {"packet":"implement-rfc-execution-strategies-v2","milestone":"M2","milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
---

# ASK-0084: Native strategy and multi-arm measurement

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Native instructions exclude custom coordination; scoped configuration and partial/inclusive telemetry are fixture-verified. Live qualification is omitted by explicit owner amendment.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.
