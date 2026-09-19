---
schema: "implement-rfc.card.v1"
id: "ASK-0083"
title: "Shared contract, strategy selection and direct execution"
status: "Done"
rfcs: ["RFC-ASK-0014"]
depends_on: []
metadata: {"packet":"implement-rfc-execution-strategies-v2","milestone":"M1","milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
acceptance: [{"criterion":"RFC-ASK-0014-AC01","outcome":"pass","revision":"b1db75db1153ae4bf14a88b7f67c962fe2a1bce5","evidence":{"kind":"artifact","detail":"docs/development/execution-strategies-m1-m3.md: two direct linked consumer courses, two real MASK installed consumers, personal interrupted commit/recovery, 23 coordinated continuation/handoff tests, 22 adapter tests, 11 workflow tests and source/documentation validation. Live qualification excluded by owner."}}]
---

# ASK-0083: Shared contract, strategy selection and direct execution

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Direct claim, change, check, evidence and permitted commit work in two disposable consumers without custom roles; resume and shared acceptance guards remain intact.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.
