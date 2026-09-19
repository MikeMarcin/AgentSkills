---
schema: "implement-rfc.card.v1"
id: "ASK-0083"
title: "Shared contract, strategy selection and direct execution"
status: "Ready"
rfcs: ["RFC-ASK-0014"]
depends_on: []
metadata: {"packet":"implement-rfc-execution-strategies-v2","milestone":"M1","milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
---

# ASK-0083: Shared contract, strategy selection and direct execution

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Direct claim, change, check, evidence and permitted commit work in two disposable consumers without custom roles; resume and shared acceptance guards remain intact.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.
