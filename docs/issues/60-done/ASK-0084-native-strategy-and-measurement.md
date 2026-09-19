---
schema: "implement-rfc.card.v1"
id: "ASK-0084"
title: "Native strategy and multi-arm measurement"
status: "Done"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0083"]
metadata: {"packet":"implement-rfc-execution-strategies-v2","milestone":"M2","milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
acceptance: [{"criterion":"RFC-ASK-0014-AC02","outcome":"pass","revision":"d12abc1b4700cc4b52ec95c29c1f9454623521c3","evidence":{"kind":"artifact","detail":"docs/development/execution-strategies-m1-m3.md: native selection/controls, actual MASK profile handoff, 7 multi-arm cases and 66 existing usage cases. Live qualification explicitly excluded; native runtime stays unverified."}}]
---

# ASK-0084: Native strategy and multi-arm measurement

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Native instructions exclude custom coordination; scoped configuration and partial/inclusive telemetry are fixture-verified. Live qualification is omitted by explicit owner amendment.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.
