# Review hub publisher continuation

Run `review-hub-2026-10-30`, segment `session-publication-1`, mandate revision
`review-hub-v1` (owner, 2026-10-30: "Implement docs/rfcs/drafts/review-hub/README.md.
Resolve D8 before implementing the hub milestones."; D8 settled). Strategy
coordinator-implementer ([selection](execution-selection.json)); implementer
claude-opus-5-5, medium effort, non-delegating leaf.

## State

- Milestone `session-publication`: complete. ASK-0129 and ASK-0130 Done;
  RFC-ASK-0018 Auto-Verified (fixture-level acceptance is its whole boundary).
- Commits: reservation `ff6b407` (RFC_BASE_SHA), import `daa6e5f`, claim `a0f57e0`,
  implementation `156b32b` and `3cb6856`, finish `f13f4d5`, promotion `bbe0e48`,
  claim `cb84545`, closeout finish `ab99baa3976ea77de6690922ca0e9696988dbcfa`
  (RFC Auto-Verified; the service's external-dependency completion commit), then
  the completion-check record commit.
- Candidate/integrated contract revision: `3cb685646a09f454fd407a5596c036683db261a2`.
- Changed source: `skills/attended-review/scripts/attended_review.py`,
  `tests/test_hub_publication.py`, `references/session-contract.md`,
  `references/tailscale-serve.md`, `README.md`, `SKILL.md`.
- Verification: [checklist](verification.md), [suite](focused-tests.json),
  [AC01 differential](ac01-differential.json), [structure](documentation.json),
  [completion check](completion-check.json) (`report-closeout`). The initial
  [binding](checkpoint.json) was renewed as [checkpoint-final.json](checkpoint-final.json)
  because the binding fingerprints the whole RFC body; only status, card links and
  the implementation record changed, not requirement text.
- Commands and writers: none running. Fixture hosts, fixture hubs and temporary
  roots are torn down by the tests; the AC01 differential removes its own root.
  No Tailscale, network or consumer state was changed.

## Pending and next

- Nothing pending in AgentSkills. No push or publication was performed.
- Next eligible scope: the `hub-service` milestone in the standalone service
  repository (D4). It is outside this repository: create/select that repository
  under authorized setup, import RFC-DRAFT-0002 with DRAFT-0002/0003/0005 from
  `docs/rfcs/drafts/review-hub/` using `plans/service/milestone-plan.json`, and
  record `external_depends_on: ["AgentSkills:ASK-0130"]` with completion commit
  `ab99baa3976ea77de6690922ca0e9696988dbcfa` and wire-contract revision
  `3cb685646a09f454fd407a5596c036683db261a2`.
- NAS deployment and Android phone observations remain owner/deployment-scoped
  acceptance for the service RFC.

## Machine hub default amendment (2026-11-04)

Owner amendment, verbatim intent: "make sure all the registered mask repos are
putting their reviews in the hub"; owner chose "Machine config file (Recommended)".
Milestone `machine-hub-default`, card ASK-0131, criterion AC08. Strategy
coordinator-implementer; implementer claude-opus-5-5, medium effort, non-delegating leaf.

- Commits: reservation `b3e1fea` (amendment baseline), adoption `47ad165`, claim
  `2d62092`, implementation `5f770a6a18650b9414621098663e8e6436dc1f53`, then the
  ASK-0131 finish commit (RFC back to Auto-Verified).
- Changed source: `skills/attended-review/scripts/attended_review.py`,
  `tests/test_hub_publication.py`, `tests/test_attended_review.py`,
  `references/session-contract.md`, `references/tailscale-serve.md`, `README.md`,
  `SKILL.md`.
- Verification: [AC08 checklist](verification.md#ac08-machine-hub-default-ask-0131-owner-amendment-2026-11-04),
  [suite](ASK-0131-focused-tests.json), [AC01 differential](ASK-0131-ac01-differential.json),
  [structure](ASK-0131-documentation.json).
- Commands and writers: none running; tests tear down their hosts, fixture hubs and
  temporary roots. No real user config, Tailscale, network or consumer state changed.

Pending (owner/deployment, outside this repository's acceptance): run
`python3 <attended-review>/scripts/attended_review.py hub-config set https://HUB.ts.net`
once per machine and user; managed consumers pick up the publisher only after their
MASK deployment links resolve to this revision. No push was performed.
