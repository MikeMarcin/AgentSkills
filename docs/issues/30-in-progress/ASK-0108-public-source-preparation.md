---
schema: implement-rfc.card.v1
id: ASK-0108
title: Prepare reconciled AgentSkills for public source preview
status: "In Progress"
rfcs: []
depends_on: []
metadata: {"milestone_plan":{"id":"public-source-preparation","path":"docs/rfcs/plans/public-source-preparation/milestone-plan.json"}}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"1047372e302f1d9680d661e7e204190cc3eb1fe7","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}},{"criterion":"AC2","outcome":"pass","revision":"1047372e302f1d9680d661e7e204190cc3eb1fe7","evidence":{"kind":"artifact","detail":"Corrected CI38525246006 passes at1047372; all36 affected fixture cases pass with MASK absent; docs/development/public-source-preparation-verification.json records original failure and correction."}},{"criterion":"AC3","outcome":"pass","revision":"1047372e302f1d9680d661e7e204190cc3eb1fe7","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}},{"criterion":"AC4","outcome":"pending","revision":"1047372e302f1d9680d661e7e204190cc3eb1fe7","evidence":{"kind":"artifact","detail":"docs/development/public-source-preparation-verification.json; AC4 privacy/provenance complete, repository license selection/adoption pending."}},{"criterion":"AC5","outcome":"pass","revision":"1047372e302f1d9680d661e7e204190cc3eb1fe7","evidence":{"kind":"artifact","detail":"Direct bounded evidence and composed-path results in docs/development/public-source-preparation-verification.json; exact source identities preserved."}}]
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

## CI correction before final handoff

The first private CI run at589d289 failed26 assertions despite the local broad
pass. All26 entries stemmed from the same fixture ownership defect: only one
rendering class activated the disposable MASK capability stub, while profile,
integrator and migration fixtures depended implicitly on an installed `mask`.
Factored that existing stub into a shared non-TestCase mixin for all four classes.
Every assertion and case count remains; genuine real-MASK integration is separate.

Correction1047372: both affected modules (36 cases) pass in a fresh clone outside
the companion repository, with all MASK/IMPLEMENT_RFC variables absent and a
system-only PATH on which `mask` is unavailable. The source manifest and docs
gates pass. Initial acceptance/history remains recorded; this correction is
required for the private-source CI claim, not a waiver or a skipped behavior.
The card was explicitly reopened/claimed for repair; licensing remains pending
and its independent prepared candidate is unaffected by these test-only inputs.

The corrected committed bundle composition also passes at1047372, including
installed usage through both adapters and preserved registry bytes. Ordinary
non-force push of1047372 is confirmed. Corrected CI run
[38525246006](https://github.com/MikeMarcin/AgentSkills/actions/runs/38525246006)
is `success` at this handoff; the coordinator owns later observation.
No known local failure remains. The outgoing exact-candidate Gitleaks default
rules scan reports zero findings; earlier historical blob/ZIP evidence is reused.

## M4 licensing mandate amendment

On 2026-10-14 the owner chose MIT for original material in both AgentSkills and
ManageAgentSkills. Mandate `public-prep-mit-adoption-v1` assigns one implementer
the remaining license adoption, notice preservation, focused source/documentation
checks and ordinary non-force main pushes in both repositories. Earlier pending
license statements and M3 delegation above describe their historical checkpoints;
this amendment supersedes that wait without changing earlier results. Existing
native, experimental and post-visibility public companion CI obligations remain
on their own live records. No visibility or real deployment action is authorized.
