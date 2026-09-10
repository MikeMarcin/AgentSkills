---
schema: "implement-rfc.card.v1"
id: "ASK-0063"
title: "Handle partial plans, legacy plans and ad-hoc targets"
status: "Done"
rfcs: ["RFC-ASK-0012"]
depends_on: ["ASK-0062"]
metadata: {"packet": "agent-skills-milestone-handling", "provisional_id": false, "criterion_coverage": ["RFC-ASK-0012-AC06", "RFC-ASK-0012-AC07", "RFC-ASK-0012-AC08"], "milestone_plan": {"id": "agent-skills-milestone-handling", "path": "docs/rfcs/plans/agent-skills-milestone-handling/milestone-plan.json"}}
acceptance: [{"criterion":"legacy-normalization","outcome":"pass","revision":"68a4825d05bdc4f52024417fd3203846953c81fe","evidence":{"kind":"observation","detail":"Raw legacy preparation retains source text/hash; explicit adoption and target-only assignment/resume run through two linked consumers. Evidence: 32 milestone/schema tests and 12 historical handoff tests passed; independent critical review corrections rechecked."}},{"criterion":"planless-and-partial","outcome":"pass","revision":"68a4825d05bdc4f52024417fd3203846953c81fe","evidence":{"kind":"observation","detail":"Planless RFC and loose issue collections, disjoint large-card criteria and partial remainder formation pass in test_milestone_adaptive.py. Evidence: 32 milestone/schema tests and 12 historical handoff tests passed; independent critical review corrections rechecked."}},{"criterion":"dependency-and-subset","outcome":"pass","revision":"68a4825d05bdc4f52024417fd3203846953c81fe","evidence":{"kind":"observation","detail":"Public projected acceptance leaves whole card open, rejects parent closeout and missing prerequisites; transitive dependency observations preserve excluded/unknown obligations. Evidence: 32 milestone/schema tests and 12 historical handoff tests passed; independent critical review corrections rechecked."}},{"criterion":"amendment-and-recovery","outcome":"pass","revision":"68a4825d05bdc4f52024417fd3203846953c81fe","evidence":{"kind":"observation","detail":"Amendment checks reject deleted selectors/exits; public recovery preserves bound projection and prerequisite evidence; stale dispatch, partial remainder and pending native obligations refuse false completion. Evidence: 32 milestone/schema tests and 12 historical handoff tests passed; independent critical review corrections rechecked."}}]
---

# ASK-0063: Handle partial plans, legacy plans and ad-hoc targets

Governing RFC: [RFC-ASK-0012](../../rfcs/RFC-ASK-0012-authored-milestone-plans-and-continuation.md).

## Objective and owned paths

Use the same runtime contract for supplied legacy plans, partially planned work, one RFC, issue collections, subset requests and recovery.

Owned surfaces (reconcile actual names at intake): skills/implement-rfc/scripts/milestone_plan.py and existing resolver/board seams; references/milestone-integration.md and pack-lifecycle.md; focused plan normalization, projection and amendment tests.

## Bounded work

Normalize authored Markdown once; do not invent a universal Markdown parser. Form missing detail with the first integrator and preserve useful supplied detail. Plan through not-yet-ready dependencies, resolve criterion selectors, and account for uncovered work. Explicitly project narrowed user scope without mutating global plan completion. Amend only affected future milestones; preserve active assignment identity and pending human/native obligations.

## Acceptance

- Legacy Markdown/stage inputs normalize once without discarding authored grouping; invalid supplied plans do not silently become planless execution.
- Planless single-RFC/issue/loose-collection and partial plans receive a concrete current outcome from the same engineer who implements it, without a disposable planner or synthetic RFC.
- Relevant dependency look-ahead, subset projections and disjoint large-card criteria preserve eligibility and pending obligations. Completing a projection never closes its broader card/RFC.
- Future-only amendments preserve unaffected active work; affected amendments renew the binding and carry all unsatisfied work. Recovery and pending human/native evidence never create false completion.

Contributes to: RFC-ASK-0012-AC06, RFC-ASK-0012-AC07, RFC-ASK-0012-AC08. These are card-scope acceptance checks; full RFC criteria are established by the combined milestone/closeout evidence, not repeated as prerequisite work on every contributing card.

## Verification and execution record

Use the direct tests named by the governing RFC and the retained pack's VERIFICATION.md. The live milestone plan, not this card's completion, defines the integration boundary. Preserve dependency-ready claims, explicit path commits, existing routing and required acceptance. No worker may acquire board/commit authority.

Not started. No implementation result, native qualification, source revision or quota saving is asserted by this packet.
