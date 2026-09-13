---
schema: "implement-rfc.card.v1"
id: "ASK-0078"
title: "Commit product changes privately with crash recovery"
status: "Done"
rfcs: ["RFC-ASK-0013"]
depends_on: ["ASK-0076", "ASK-0077"]
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC05","RFC-ASK-0013-AC06"]}
acceptance: [{"criterion":"Private claim commits before edits; explicit product paths and ordinary message commit","outcome":"pass","revision":"f15b8cc390e74ed5288536b1ee454985a3c5dcaf","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0078.commit.json"}},{"criterion":"Known private references refuse in product commit messages, branch names, content and proposed PR text","outcome":"pass","revision":"f15b8cc390e74ed5288536b1ee454985a3c5dcaf","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0078.commit.json"}},{"criterion":"Durable external receipt reconciles pre/post source and tracker failures without reset, duplicate commit, unrelated edit loss or false completion","outcome":"pass","revision":"f15b8cc390e74ed5288536b1ee454985a3c5dcaf","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0078.commit.json"}}]
---

# ASK-0078: Commit product changes privately with crash recovery

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: source commit and tracker receipt integration; failure injection and privacy tests. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- A private claim commits before source edits; product commits stage explicit paths and use ordinary messages.
- Known private identifiers, paths and bookkeeping text are refused in product commit messages, generated branch names and PR text.
- External operation receipts reconcile failures before/after either repository commit without reset, duplicate commit, unrelated edit loss or false completion.

Contributes to: RFC-ASK-0013-AC05, RFC-ASK-0013-AC06. The mandate remains binding beyond this card summary.

## Verification and execution record

Not started. No source or native acceptance asserted.
