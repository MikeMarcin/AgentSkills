---
id: "RFC-ASK-0014"
title: "Selectable execution strategies and real-code experiments"
status: "Implementing"
metadata: {"milestone_plan":{"id":"execution-strategies-v2","path":"docs/rfcs/plans/execution-strategies-v2/milestone-plan.json"}}
---

# Selectable execution strategies

Accepted from [the retained revision-2 packet](assets/implement-rfc-execution-strategies-v2/IMPLEMENTATION_BRIEF.md). [ASK-0087](../issues/10-backlog/ASK-0087-close-execution-strategies.md) owns closeout. Preserve authored M1–M4 outcomes and dependencies.

## Owner amendments (2026-09-19)

Implement M1–M3 directly in the primary session, without subagents. Skip live qualification entirely; M4 will establish actual native behavior. Prepare the reusable M4 kit, leaving task selection and budgets to the owner later. No experiment worktrees, arm/judge launches, verdict, push, global configuration edits or unrelated consumer migration.

## Acceptance

- **AC01 (M1):** One shared engineering/acceptance contract, passive recipe selection and direct public consumer paths with no bespoke roles; preserve recovery, authored grouping, storage and authority guards and coordinated defaults.
- **AC02 (M2):** Native/system-owned execution recipe and scoped controls; additive multi-arm provenance and conservative partial/inclusive usage accounting. Fixture evidence is separate from unverified host behavior.
- **AC03 (M3):** Strict planner-worker feedback/ownership and explicit routes, extensible fifth-recipe conformance, safe registration refusal, and a validated reusable M4 kit.
- **AC04 (M4):** One owner-selected real matched block and truthful separate quality, adherence, cost, burden and coverage readout. Not authorized to run in this delivery.

The MASK capability handoff is [RFC-MASK-0023](https://github.com/MikeMarcin/ManageAgentSkills/blob/main/docs/rfcs/RFC-MASK-0023-selected-workflow-requirements.md). Source changes do not deploy other consumers.

## Selected-scope acceptance

M1–M3 pass under the recorded amendments; see [implementation evidence](../development/execution-strategies-m1-m3.md)
and the closeout's criterion/commit rows. The [M4 kit](../../skills/implement-rfc/references/strategy-study/README.md)
is prepared and synthetically validated. AC04 remains open, with no product task or
experiment selected or run. This RFC remains Implementing, not Auto-Verified.
