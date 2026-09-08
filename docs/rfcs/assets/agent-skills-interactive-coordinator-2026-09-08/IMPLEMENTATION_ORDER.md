# Implementation order: three usable milestones

The live board controls dependencies after import. These groupings guide coherent
integration; they are not extra cards or a second scheduler.

| Milestone | Cards | Demonstrable result |
|---|---|---|
| Intake | ASK-0050 | Imported agreed scope, live IDs and immutable baseline |
| M1 — Native coordination path | ASK-0051–0053 | Independently routed coordinator dispatches an authorized integrator; a complete result yields a safe fresh-milestone continuation; common paths have clear role-specific instructions |
| M2 — Qualified behavior and honest measurement | ASK-0054–0056 | Each named native driver continues two milestones; focused failure scenarios and complete family accounting are exercised, with limitations explicit |
| M3 — Adopt or retain candidate, then close | ASK-0057–0058 | Evidence-backed activation/rollback decision, preserved quality, truthful RFC state |

Implement a thin end-to-end slice in ASK-0051 before expanding conditional branches.
ASK-0052 and ASK-0053 share instruction surfaces: schedule explicit ownership and
integrate them together, rather than launch competing writers. ASK-0056 can run
in parallel when it owns only the independent measurement seam. Native driver
qualifications may use distinct fixture roots; do not run both in one writable
checkout or increase concurrency merely to exhaust both allowances equally.

A milestone can cover multiple linked cards. Claim cards before their source
changes and retain their individual criteria. Do not wait to integrate all role,
helper and instruction components at the end of this pack.
