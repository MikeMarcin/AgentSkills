---
schema: "implement-rfc.card.v1"
id: "ASK-0077"
title: "Pair tracker lanes and reconcile repository identities"
status: "Done"
rfcs: ["RFC-ASK-0013"]
depends_on: ["ASK-0075"]
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC04","RFC-ASK-0013-AC07"]}
acceptance: [{"criterion":"Source lanes have corresponding tracker branches/worktrees and both repository identities in handoffs","outcome":"pass","revision":"190892f77e8b51ee592c6ad62c5d3cf528354ff5","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0077.lanes.json"}},{"criterion":"Branch switch, rename, removed worktree, mismatches and rewritten history refuse until explicit reconciliation; reservations remain main-authorized","outcome":"pass","revision":"190892f77e8b51ee592c6ad62c5d3cf528354ff5","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0077.lanes.json"}},{"criterion":"Local-only and authorized separate bare-remote synchronization retain branch and conflict restrictions","outcome":"pass","revision":"190892f77e8b51ee592c6ad62c5d3cf528354ff5","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0077.lanes.json"}}]
---

# ASK-0077: Pair tracker lanes and reconcile repository identities

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: paired worktree/lane binding; reservation and synchronization tests. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- Each source lane binds a tracker branch/worktree with both identities, roots, branches and revisions in handoffs.
- Branch switch, rename, removed worktree and mismatches refuse or reconcile without guessing; reservations remain main-authorized.
- Local-only behavior and authorized separate local-bare-remote synchronization preserve branch restrictions and conflicts.

Contributes to: RFC-ASK-0013-AC04, RFC-ASK-0013-AC07. The mandate remains binding beyond this card summary.

## Verification and execution record

Not started. No source or native acceptance asserted.
