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

## Preparation handoff

The [M4 kit](../../../skills/implement-rfc/references/strategy-study/README.md) was
delivered with M3 at `9c29dd8` and validated using synthetic records only. It defaults
to Direct Astra Max, Native Astra Ultra and the existing coordinated baseline;
planner-worker is optional. Task, baselines, budgets, exact judge routes and source/
tracker worktree locations remain unset. No experiment or comparative verdict exists.

This card is deliberately unclaimed. A future owner mandate must select/freeze the
study inputs and authorize its arm/judge execution. Native behavior remains unverified;
the present delivery intentionally skipped live qualification.
