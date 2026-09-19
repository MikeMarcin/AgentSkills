---
schema: "implement-rfc.card.v1"
id: "ASK-0085"
title: "Strict planner-worker recipe, conformance and M4 kit"
status: "Done"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0084"]
metadata: {"packet":"implement-rfc-execution-strategies-v2","milestone":"M3","milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
acceptance: [{"criterion":"AC03 / M3 exit: strict ownership, extensibility and reusable M4 kit","outcome":"pass","revision":"9c29dd821089e2950be2a161b852e3b5197f1c5f","evidence":{"kind":"artifact","detail":"docs/development/execution-strategies-m1-m3.md: 148 integrated tests passed plus 11 affected route/host/study checks after final refinement; fifth registered recipe uses common board/checkpoint/usage paths. M4 kit validates synthetically, all future task/run inputs remain unset; no live qualification."}}]
---

# ASK-0085: Strict planner-worker recipe, conformance and M4 kit

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Strict ownership and route policy, fifth-recipe conformance and a synthetic-validated reusable M4 kit work without live agents.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.
