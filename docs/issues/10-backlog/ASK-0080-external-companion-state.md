---
schema: "implement-rfc.card.v1"
id: "ASK-0080"
title: "Route attended, wizard and remote runtime state externally"
status: "Backlog"
rfcs: ["RFC-ASK-0013"]
depends_on: ["ASK-0076", "ASK-0077"]
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC10"]}
---

# ASK-0080: Route attended, wizard and remote runtime state externally

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: attended-review and wizard state resolvers; remote handoff compatibility. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- Companion execution logs, progress, leases and optional lane/station metadata use explicit external runtime state while candidate protection targets source.
- Remote handoffs carry both roots/revisions; incompatible adapters refuse before source-local metadata writes.

Contributes to: RFC-ASK-0013-AC10. The mandate remains binding beyond this card summary.

## Verification and execution record

Not started. No source or native acceptance asserted.
