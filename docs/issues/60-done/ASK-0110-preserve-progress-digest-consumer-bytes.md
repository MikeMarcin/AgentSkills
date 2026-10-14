---
schema: "implement-rfc.card.v1"
id: "ASK-0110"
title: "Preserve every consumer byte during the read-only progress digest"
status: "Done"
rfcs: []
depends_on: []
metadata: {"mandate":"public-prep-final-reconciliation-v1","baseline":"652e528ff87b82fe5e227d7b6c6e199336c2a4db","failed_ci":"38532937786","milestone_plan":{"id":"public-source-progress-repair","path":"docs/rfcs/plans/public-source-progress-repair/milestone-plan.json"}}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"18b236bd0f0be7c7f72b415fe418720a6cbfe9a8","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"Original intermittent CI failure retained; unchanged baseline passed20courses each with AppleGit2.50.1/pristineGit2.55.0. Controlled detachedGit worker removed exactly .git/objects/maintenance.lock in alpha/beta and reproduced whole-tree failures. Original CI path attribution remains explicitly inferred."}},{"criterion":"AC2","outcome":"pass","revision":"18b236bd0f0be7c7f72b415fe418720a6cbfe9a8","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"b45c3bb suppresses fixture auto-maintenance before any commit; optional init_repo parameter keeps default semantics elsewhere. Same controlled course passes with no lock or changed byte. AST confirms entire Git-inclusive digest and all3original test bodies unchanged; production progress/context helpers unchanged."}},{"criterion":"AC3","outcome":"pass","revision":"18b236bd0f0be7c7f72b415fe418720a6cbfe9a8","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"Exactb45c3bb fresh clone/empty HOME/pristineGit2.55.0:20focused tests pass (3progress/15context/2checkpoint), no skips; canonical source manifest refreshed; docs15RFCs/110cards, source and exact18b236b Gitleaks history/tree/new-metadata gates pass. Owned source/evidence commits explicit; final ordinary push and quiescent handoff are the retained M3 exit before writer release."}}]
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
