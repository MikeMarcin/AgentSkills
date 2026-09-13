---
schema: "implement-rfc.card.v1"
id: "ASK-0075"
title: "Bind personal mode and external tracker"
status: "Done"
rfcs: ["RFC-ASK-0013"]
depends_on: []
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC01","RFC-ASK-0013-AC02"]}
acceptance: [{"criterion":"Explicit personal selection, shared common-repository binding and supplied tracker association","outcome":"pass","revision":"9ad89cc4bd2854557b210787943557e50541dbfb","evidence":{"kind":"artifact","detail":"ASK-0075.personal.json: nine public subprocess tests exercise unconfigured refusal, managed and supplied setup, persistent status, same-common-dir worktrees, independent clone and reused-path explicit association. Critical reviewer rechecked its reused-path counterexample without a blocker."}},{"criterion":"Observational status and safe external state without source footprint","outcome":"pass","revision":"9ad89cc4bd2854557b210787943557e50541dbfb","evidence":{"kind":"artifact","detail":"ASK-0075.personal.json hashes the complete disposable source worktree and Git directory before/after setup and status. It checks overlap, symlinked local-state parents, external tracker Git common dir, staged unrelated tracker index and malformed binding refusal. Critical review reproduced and then rechecked the corrected public paths."}},{"criterion":"Project-mode context compatibility and interim private-helper isolation","outcome":"pass","revision":"9ad89cc4bd2854557b210787943557e50541dbfb","evidence":{"kind":"artifact","detail":"ASK-0075.project.json records 15 existing context tests; ASK-0075.linked.json records one composed two-linked-consumer public plan test. ASK-0075.personal.json also proves explicit project override, project under IMPLEMENT_RFC_HOME, and unadapted board allocation refusal before source mutation. Full personal board/lifecycle adaptation remains ASK-0076–0078."}}]
---

# ASK-0075: Bind personal mode and external tracker

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: skills/implement-rfc/scripts/project_config.py; personal binding/setup public helper; focused context and footprint tests. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- Explicit selection creates or binds a managed/supplied tracker and records one source Git common repository identity locally.
- An observational public status command resolves the stored binding and explicit mode override without creating state.
- Project-mode context remains valid; overlap, unsafe path redirection, absent binding and independent clone guessing refuse; target checkout and Git metadata stay untouched.

Contributes to: RFC-ASK-0013-AC01, RFC-ASK-0013-AC02. The mandate remains binding beyond this card summary.

## Verification and execution record

Not started. No source or native acceptance asserted.
