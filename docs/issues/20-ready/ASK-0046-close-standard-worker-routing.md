---
schema: "implement-rfc.card.v1"
id: "ASK-0046"
title: "Integrate and close the standard-worker routing change"
status: "Ready"
rfcs: ["RFC-ASK-0009"]
depends_on: ["ASK-0045"]
closeout_for: ["RFC-ASK-0009"]
metadata: {"packet":"agent-skills-standard-worker-review", "provisional_id":true}
---

# ASK-0046: Integrate and close the standard-worker routing change

Governing RFC: [RFC-ASK-0009](../../rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md).

Criterion coverage: RFC-ASK-0009-AC01, RFC-ASK-0009-AC02, RFC-ASK-0009-AC03, RFC-ASK-0009-AC04, RFC-ASK-0009-AC05, RFC-ASK-0009-AC06.

## Objective and owned paths

Sole closeout for RFC-ASK-0009. Own this card, the new RFC/status/index row, and the
small live import/adoption record. Preserve all older RFCs, cards and retained evidence.

## Work and acceptance

Inspect the integrated scoped diff against the real RFC_BASE_SHA, consume one focused
review of changed policy/migration behavior where warranted, and reconcile all six
criteria. Confirm all three implementation cards are Done. Record effective target
settings and source revision separately from observed runtime execution. Run the
repository structure gate once at integration and missing/invalidated focused checks only.

Configuration adoption is owner-directed. A missing live quota comparison is a disclosed
limitation, not a blocker or a reason to claim a saving. Record any explicitly authorized
consumer adoption separately; leave unrelated projects, pins, sessions and paid usage
untouched. Document rollback and remove only task-created temporary fixture roots after
results are retained. No push or automatic registry-wide update.

## Durable closeout anchor

RFC_BASE_SHA: 52aa2bb016d92b3d3fc881a8e6b4c2d1390df900

Capture the actual pre-source-work Git SHA at intake; the pack cannot supply it.
Planned cards: ASK-0043, ASK-0044, ASK-0045, ASK-0046 (remap with live allocation).

## Closeout checklist

| Acceptance | Direct check / evidence | Outcome | Implementation revision |
|---|---|---|---|
| RFC-ASK-0009-AC01 | Default/deep policy and selected instruction cases | Not run | Not recorded |
| RFC-ASK-0009-AC02 | Exact routes, independent overrides and native request rendering | Not run | Not recorded |
| RFC-ASK-0009-AC03 | Adapter/addenda/active-assignment migration and recovery fixtures | Not run | Not recorded |
| RFC-ASK-0009-AC04 | Old/new/ambiguous audit histories; unchanged capture behavior | Not run | Not recorded |
| RFC-ASK-0009-AC05 | Focused suites, source manifest and integration checks | Not run | Not recorded |
| RFC-ASK-0009-AC06 | Active docs and scoped adoption/rollback handoff | Not run | Not recorded |

## Limits and owner decision

Requested routes are selected by the owner in this conversation. Runtime serving,
model-quality equivalence and subscription savings are unmeasured by this pack.
Keep those statements distinct from the configuration acceptance above.
