---
schema: "implement-rfc.card.v1"
id: "ASK-0143"
title: "Configure hosted attended-review routing per project"
status: "Done"
rfcs: ["RFC-ASK-0021"]
depends_on: ["ASK-0142"]
closeout_for: ["RFC-ASK-0021"]
metadata: {"milestone_plan":{"id":"hosted-project-routing","path":"docs/rfcs/plans/hosted-project-routing/milestone-plan.json"}}
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"ca77d92a9f80cca38be2d2948baacfbdb5e938aa","evidence":{"kind":"observation","detail":"Two disposable consumer links, read-only route inspection, explicit mode, existing SQLite/JSON mode, missing and malformed files, outside-checkout link refusal and first-init recovery."}},{"criterion":"AC02","outcome":"pass","revision":"ca77d92a9f80cca38be2d2948baacfbdb5e938aa","evidence":{"kind":"observation","detail":"Actual loopback Hub accepted two distinct enrolled routes. Missing material and partial route conflicts sent zero requests. Dropped receipt, invalidated config and durable Hand Back reused the saved route. The hosted and pass-through TLS and redirect checks passed."}}]
---

# Configure hosted attended-review routing per project

RFC_BASE_SHA: 51e5c633d1cd925fa5b99ec6b2695b61ac465030

Planned local card: ASK-0143. Verify RFC-ASK-0021 AC01 and AC02 through the
public helper with linked disposable consumers and the loopback hub fixture.

Assignment `project_routing`, run `hosted-project-routing-20261124`, segment
`local-coordinator-implementer-1`, mandate `2026-11-24-project-routing-local-only`.
Source handoff was AgentSkills `3ecb86e458fcc2a96fdc7a6d7b9471c8a71b75b5`.

## Verification and execution record

| Criterion | Public check | Outcome | Implementation commit |
|---|---|---|---|
| AC01 | Two linked fixture checkouts used `project-config` and `init`. The helper reported each checkout's own settings without opening state. Missing config kept legacy behavior. Malformed fields and a link into the other checkout were refused. Explicit mode flags and existing SQLite or archived JSON state retained their mode rules. | Pass | `ca77d92a9f80cca38be2d2948baacfbdb5e938aa` |
| AC02 | Two enrolled fixture projects published selected candidates to the real hub. Missing title, selection or installation and conflicting partial routing sent zero requests. Full explicit routing published successfully. A dropped commit reply and later invalid profile still yielded the same publication revision and durable Hand Back through the original binding. The existing wrong-certificate and redirect checks passed. | Pass | `ca77d92a9f80cca38be2d2948baacfbdb5e938aa` |

From AgentSkills on Darwin arm64 with Python 3.15.0:

- `ATTENDED_REVIEW_HUB_ROOT=../AttendedReviewHub python3 -B -m unittest discover -s skills/attended-review/tests -v`
  passed all 77 tests against Hub runtime and test bytes at
  `4530e3b295664086f28a7fec5f672b4a1c788f4f`. The SQLite lifecycle fixture emitted
  one unclosed-connection ResourceWarning while passing. The hub checkout moved
  during verification through tracker-only changes.
- The same discovery command with `-p test_hosted_review.py -k project -v`
  passed all four routing tests at the final product revision. The first
  project-mode regression failed on the baseline helper because it initialized
  the configured project as legacy.
- `node --test skills/attended-review/tests/review_page.test.js` and
  `python3 -B -m unittest discover -s skills/concept-art-approval-pipeline/scripts -p 'test_*.py' -v`
  passed. The art suite ran seven tests.
- Repository documentation, scoped board validation, the implement-rfc
  portable-source digest and the staged BetterLeaks check passed. The
  milestone checkpoint matched the plan and exact product revision.

The [operator contract](../../../skills/attended-review/references/hosted-review.md)
documents the checked settings and CLI precedence. The product commit contains
the native CLI, its storage initialization check, the regression fixtures and
companion instructions. The shared art pass-through recipe selects legacy mode
explicitly to retain original media, including video. Hub-stored v1 accepts
bounded inline PNG and PCM WAV, so a migration of the full art workflow needs
separate integration evidence.

Closeout review runtime was implementer self-review. The assigned local
acceptance is complete with no pending human decision or protected candidate.
All fixture hosts, commands and task-owned writers stopped. The next optional
rollout step is to authorize a selected consumer's MASK upgrade and verify
its private local routing profile through the installed helper. This assignment
did not change a consumer checkout or qualify live deployment.
