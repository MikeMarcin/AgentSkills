---
schema: "implement-rfc.card.v1"
id: "ASK-0110"
title: "Preserve every consumer byte during the read-only progress digest"
status: "In Progress"
rfcs: []
depends_on: []
metadata: {"mandate":"public-prep-final-reconciliation-v1","baseline":"652e528ff87b82fe5e227d7b6c6e199336c2a4db","failed_ci":"38532937786","milestone_plan":{"id":"public-source-progress-repair","path":"docs/rfcs/plans/public-source-progress-repair/milestone-plan.json"}}
---

# Intermittent read-only digest CI correction

CI on `3359319` reports one failure in the linked beta consumer's whole-tree
preservation assertion after a one-shot progress digest. Later same-input CI on
`652e528` passes. Neither result erases the failure. M3 retains writer ownership
until the changed bytes and cause are identified, corrected and narrowly verified.

## Acceptance

- AC1: Diagnosis records which consumer bytes change and the responsible action;
  baseline failure, intermittent passes and platform/version limits remain explicit.
- AC2: The read-only digest preserves every consumer byte, including Git internals.
  Its existing preservation and emitted-trail assertions remain intact; deterministic
  coverage exposes the identified cause rather than excluding affected paths.
- AC3: Focused linked-consumer digest and relevant context checks pass against the
  exact correction. Documentation, scans, explicit-path commits, ordinary push and
  command-quiescent M3 handoff retain the existing license/native boundaries.

The real visible-run acceptance of ASK-0073 remains separate and open. This fixture
and helper correction does not provide native progress-relay acceptance.
