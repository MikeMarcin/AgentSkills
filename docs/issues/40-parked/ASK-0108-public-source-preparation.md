---
schema: implement-rfc.card.v1
id: ASK-0108
title: Prepare reconciled AgentSkills for public source preview
status: "Parked"
rfcs: []
depends_on: []
metadata: {"milestone_plan":{"id":"public-source-preparation","path":"docs/rfcs/plans/public-source-preparation/milestone-plan.json"}}
parked_on: "human-review"
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"10d588824042a42cf2e29cbf3791c359d99bd501","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}},{"criterion":"AC2","outcome":"pass","revision":"10d588824042a42cf2e29cbf3791c359d99bd501","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}},{"criterion":"AC3","outcome":"pass","revision":"10d588824042a42cf2e29cbf3791c359d99bd501","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}},{"criterion":"AC4","outcome":"pending","revision":"10d588824042a42cf2e29cbf3791c359d99bd501","evidence":{"kind":"artifact","detail":"docs/development/public-source-preparation-verification.json; AC4 privacy/provenance complete, repository license selection/adoption pending."}},{"criterion":"AC5","outcome":"pass","revision":"10d588824042a42cf2e29cbf3791c359d99bd501","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}}]
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

## Initial frontier

Plan preparation and binding precede product changes. ASK-0073's real progress-relay
observation and ASK-0102's bootstrap correction are not claimed. RFC-ASK-0012 native
qualification and RFC-ASK-0014 experiments remain open. No task-owned review server
or protected candidate is active. Required new license selection is pending with
coordinator; it is not inferred from inherited notices.

## Verification and execution record

Technical source candidate: `10d588824042a42cf2e29cbf3791c359d99bd501`. Both histories were reconciled at
`e93d84d`; ASK-0107 resolves the frontend-design collision.

- Helper suite: 679 cases, zero failures/errors, two native Windows skips;
  jsonschema and real disposable MASK composition are enabled.
- Other shipped skill suites: 57 cases, all pass. The initial author package
  dependency skip was rerun with its explicit MASK checkout and passes.
- Public MASK examples, committed RFC bundle and selected-import paths pass.
  Installed usage runs through both adapters without registry changes.
- Fresh local clone: documentation and portable source gates pass. Test
  dependencies include jsonschema and Pillow; missing dependency/program controls
  refuse. The aggregate driver composes the separately verified suites and was
  not redundantly rerun end to end. GitHub CI execution remains unobserved.
- Current metadata sanitization preserves21 mutable document paths, correlated
  placeholders, chronology and outcomes. Immutable packets and history stay intact.
- Self-review checked v1/v2 JSON scope, missing/replaced-root refusal, personal-scope
  exclusion, explicit fixture roots, source revision binding, CLI examples,
  contributor paths, CI privacy gating and third-party notice preservation.

See [the public evidence record](../../development/public-source-preparation-verification.json)
for exact source/check identities and limitations. Full command logs, active
checkpoint and private correlation map are retained in the coordinator handoff.
The unrelated lock edit remains byte-identical and excluded from commits.

AC1, AC2, AC3 and AC5 pass within this bounded source-preparation scope. AC4's
privacy and provenance work is complete, but repository license selection is
still pending. No repository-wide license has been granted. Keep this card
human-pending until the owner chooses and the next engineering round applies
that choice. Source preview/push/final audit remain conditional M3 obligations.

## Coordinator sequencing amendment

Mandate revision `public-prep-agent-skills-push-v2`: within the owner's explicit
"and push too" authority, the coordinator delegated the ordinary non-force
AgentSkills main push after technical checks, upkeep and a redacted outgoing
Gitleaks scan. Safely fetch/reconcile newer main first. CI can then run while
M2 prepares MASK. This does not certify licensing or public readiness and does
not change visibility. The authored boundary was checked and amended, preserving
all work selectors and exits; current binding is renewed for this mandate.
Final cross-repository scan, license adoption and readiness remain M3 obligations.
