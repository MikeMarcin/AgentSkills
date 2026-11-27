---
schema: "implement-rfc.card.v1"
id: "ASK-0145"
title: "Rename frontend-design to ux-design and deploy it to the fleet"
status: "Blocked"
rfcs: []
depends_on: []
metadata: {"baseline":"315940154e4db5036b2d5727a58c31ec4c363f07","requested_on":"2026-11-27"}
blocked_by: "mask-dev-link-identity-repair"
---

# Rename frontend-design to ux-design and deploy it to the fleet

The owner asked to rename `frontend-design` so it is not confused with
Anthropic's `frontend-design` plugin skill, and to make it explicitly cover
Roblox, custom-engine game UI, engine editors and developer tools, websites and
Qt applications without being specific to any project. The owner approved the
name `ux-design`, asked for lessons from their own UX iteration to be
generalized into the skill, and required progressive disclosure so a session
loads only the guidance for its surface. The owner also asked to add the
already-catalogued `clang-split-refactor` package to the source manifest, then
to commit, push and deploy to the fleet.

Own the package rename and content, the README catalog, source manifest,
provenance and preview references, and this maintenance record. Historical
records keep the original name. Deploy through official MASK previews and exact
plan approval to authorized personal scopes on enrolled devices. Migrate only
existing project `frontend-design` selections in their primary checkouts, after
the replacement is verified, without committing consumer repositories. Leave
temporary lanes and agent worktrees untouched. Do not expand credentials,
grants, host-key trust or forwarding, and do not broadly upgrade skills.

Acceptance:

- AC1: `ux-design` carries the original design workflow with platform-neutral
  core guidance and routed references for web, mobile, desktop, Qt, game UI,
  Roblox experiences, Roblox Studio plugins, editors and tools, and
  immediate-mode UI; the package names no consumer project.
- AC2: Live references use the new name, `clang-split-refactor` is in the
  source manifest, MASK validates both packages from a disposable tap, and
  documentation, portable-source and offline test checks pass.
- AC3: The source is pushed to `origin/main` without unrelated work.
- AC4: Fleet personal scopes and existing primary project consumers are
  deployed or migrated and verified per scope; unavailable targets remain
  explicit, not reported complete.

## Verified source and partial deployment, 2026-11-27

Source revision `59096491d3a70726be03e99735bf95341a919bd3` was pushed to
`origin/main`. The outgoing history contained only this card's reservation,
record, claim and source commits.

AC1 passes. The package has 12 files, payload digest
`sha256:7139eb892ec65fd57f811850560d4ceccce15220cfc70944903dd8fe1c306b2a`.
The core routes to nine references, and a search of the package found no
consumer project names. Lessons from the owner's iteration on two projects were
generalized. A fresh-agent tabletop of five tasks (Roblox shop, Qt review
panel, immediate-mode inspector, web landing-page critique, Studio plugin)
selected the intended references; its three wording fixes were applied.

AC2 passes. The README catalog, source manifest, provenance and preview record
use the new name; historical records are unchanged. `clang-split-refactor` is
now in the manifest, so manifest entries, package directories and README rows
agree. MASK validated both packages from a disposable local bare tap and again
from the published tap, with the same `ux-design` digest. Documentation,
portable-source and skill-metadata checks passed. The offline suite ran 469
tests: 463 passed, 4 skipped, and two `implement-rfc` tests failed
(`test_attended_review_is_a_watched_fresh_context_boundary` and
`test_historical_target_boundaries_and_native_requests`). Both fail identically
at the untouched baseline `3159401`, so they predate this change.

AC3 passes: `3159401..5909649` was pushed.

AC4 remains incomplete:

- The controller's tap cache refused to fetch after the data volume's device
  number changed. `tap repair-cache` retained the old cache, and a fresh fetch
  resolved `5909649`.
- Fleet operation `b717b78da4910d7f40a259111c6b42a7` was additive. Personal
  scopes on this-mac, intel-mac, jaegaw-windows and jaegaw-wsl reported
  `applied_verified`, and each binds `ux-design` at `5909649` for Claude and
  Codex. Existing packages kept their locked commits. MASK reports host loading
  as not verified; the controller's running session listed the new skill.
- In the aito primary checkout, `ux-design` was installed and verified, then
  `frontend-design` was removed; `status --check` passes. The declaration and
  lock changes are uncommitted, and its name-based `.gitignore` has no
  `ux-design` link entries yet. Its `main` is far ahead of `origin`, so nothing
  was pushed there.
- The Athens primary checkout is blocked. Its `attended-review` is dev-linked to
  the AgentSkills authoring checkout. MASK refuses install, repair, return to
  pinned and re-linking with `source.identity_mismatch`, because the recorded
  authoring-root device number predates the volume change. MASK has no supported
  repair for development-link identity. Athens keeps its working pinned
  `frontend-design`.
- Temporary lanes and agent worktrees that still select `frontend-design` were
  left untouched. Project checkouts on other devices were not inspected.

Remaining work: add or obtain a MASK repair for development-link identity, then
swap Athens to `ux-design` and restore its dev link. Commit aito's control
changes when the owner approves. Do not mark this card Done until both scopes are
migrated or explicitly retired.
