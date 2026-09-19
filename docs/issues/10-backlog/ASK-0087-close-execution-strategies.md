---
schema: "implement-rfc.card.v1"
id: "ASK-0087"
title: "Close execution strategies pack"
status: "Backlog"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0083", "ASK-0084", "ASK-0085", "ASK-0086"]
metadata: {"packet": "implement-rfc-execution-strategies-v2", "milestone": "closeout"}
closeout_for: ["RFC-ASK-0014"]
---

# ASK-0087: Close execution strategies pack

Governing RFC: [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).

## Acceptance

Reconcile all M1–M4 evidence. M4 remains outside the current implementation mandate.

## Authority

Primary engineers directly; no subagents or model orchestration for this implementation. Own canonical implement-rfc source, tests, docs and scoped bookkeeping. No push, global settings, consumer migration or live model qualification.

RFC_BASE_SHA: 940f2e937068689316b4ef4663c56fcbd3a27766

Planned cards: ASK-0083, ASK-0084, ASK-0085, ASK-0086.

Current frontier: M1–M3 accepted; M4 preparation delivered, execution not authorized.
The [implementation evidence](../../development/execution-strategies-m1-m3.md) and
[reusable kit](../../../skills/implement-rfc/references/strategy-study/README.md)
preserve the handoff. Task, baselines, budgets, exact judges and experimental worktree
locations remain unset. Live qualification was explicitly omitted; native host
behavior remains unverified until the future experiment. Keep this closeout open.

| Acceptance | Evidence and outcome | Source implementation |
| --- | --- | --- |
| AC01 / M1 | PASS: two disposable linked consumers, direct primary lifecycle, shared acceptance/resume and MASK profile checks | AgentSkills `b1db75d`; MASK `bc387f8` |
| AC02 / M2 | PASS within amended scope: native recipe/config inspection and inclusive/partial telemetry fixtures; no live qualification | AgentSkills `d12abc1`; accounting refinements `9c29dd8` |
| AC03 / M3 | PASS: strict worker ownership/routes, fifth-recipe extension, malformed registration refusal and synthetic M4-kit validation; 148 integrated tests and 11 final focused checks | AgentSkills `9c29dd8` |
| AC04 / M4 | OPEN: no task selected, worktrees created, arms/judges launched or verdict produced | None |

Closeout review runtime: primary-session self-review/code-simplifier; no subagents.
Documentation gates and portable source validation pass. This records selected-scope
acceptance only; RFC-ASK-0014 and the whole packet remain open for M4.
