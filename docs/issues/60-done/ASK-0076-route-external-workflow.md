---
schema: "implement-rfc.card.v1"
id: "ASK-0076"
title: "Route shared planning and board helpers to external workflow root"
status: "Done"
rfcs: ["RFC-ASK-0013"]
depends_on: ["ASK-0075"]
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC03","RFC-ASK-0013-AC08"]}
acceptance: [{"criterion":"Shared plan and board route documents to the external tracker while evidence targets the source","outcome":"pass","revision":"190892f77e8b51ee592c6ad62c5d3cf528354ff5","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0076.public.json"}},{"criterion":"Public plan intake, claim, partial acceptance, stale return, human pending, resume and closeout work in both modes","outcome":"pass","revision":"190892f77e8b51ee592c6ad62c5d3cf528354ff5","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0076.public.json"}},{"criterion":"Portable tracker records exclude local paths, process state, locks and logs","outcome":"pass","revision":"190892f77e8b51ee592c6ad62c5d3cf528354ff5","evidence":{"kind":"observation","detail":"Public disposable path wrote plan/card only to tracker, kept assignment/return and board lock under runtime, and left source HEAD/status unchanged; see ASK-0076.public.json."}}]
---

# ASK-0076: Route shared planning and board helpers to external workflow root

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: project context and shared board/plan helpers; focused public lifecycle tests. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- The shared planner and board read tracker documents while product inspection and baseline refer to the source checkout.
- Public plan intake, claim, partial acceptance, stale return, human-pending, interrupt, resume and closeout scenarios pass in both modes.
- Portable tracker records exclude machine-local paths, process state, locks and logs.

Contributes to: RFC-ASK-0013-AC03, RFC-ASK-0013-AC08. The mandate remains binding beyond this card summary.

## Verification and execution record

Not started. No source or native acceptance asserted.
