---
schema: implement-rfc.card.v1
id: ASK-0108
title: Prepare reconciled AgentSkills for public source preview
status: "In Progress"
rfcs: []
depends_on: []
metadata: {"milestone_plan":{"id":"public-source-preparation","path":"docs/rfcs/plans/public-source-preparation/milestone-plan.json"}}
---

# Public source preparation

Mandate revision: `public-prep-user-amendment-push-v1` (2026-10-13).
The owner requested public readiness, then authorized pulling, reconciliation,
cleanup and push. This milestone owns AgentSkills main; the coordinator handles
final cross-repository verification and push. Repository visibility, credentials,
real consumer migrations and destructive history rewriting remain outside scope.
Baseline local `b7f0dca09339bd39cbbfe7cca4af11287c90cc57`; fetched main
`719c1bf`. Reconciled candidate before preparation: `e93d84d`.
The pre-existing `.mask.lock.json` edit is preserved separately and excluded.

## Acceptance

- AC1: Both histories survive and the ASK-0105 collision is resolved through a
  new reserved frontend-design identity, truthful receipts and a monotonic counter.
- AC2: Fresh-clone onboarding, contributor verification and CI expose the supported
  source-preview path, install jsonschema for schema gates and use public MASK
  commands with disposable fixtures. No tokens or private deployment assumptions.
- AC3: Affected helper, instruction-contract, station recovery and public composition
  checks pass against the reconciled candidate, with native skips stated accurately.
- AC4: Current avoidable personal operational metadata is sanitized outside immutable
  packets; useful chronology, revisions and protocol compatibility remain. Third-party
  notices are retained; repository licensing follows the owner's explicit selection.
- AC5: Documentation names experimental scope and open native/human/experiment work,
  accurate security reporting, verification evidence and next steps. No false RFC
  closure; explicit-path commits and a quiescent durable handoff complete the slice.

## Current frontier

Plan preparation and binding precede product changes. ASK-0073's real progress-relay
observation and ASK-0102's bootstrap correction are not claimed. RFC-ASK-0012 native
qualification and RFC-ASK-0014 experiments remain open. No task-owned review server
or protected candidate is active. Required new license selection is pending with
coordinator; it is not inferred from inherited notices.
