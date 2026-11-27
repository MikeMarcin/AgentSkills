---
schema: "implement-rfc.card.v1"
id: "ASK-0145"
title: "Rename frontend-design to ux-design and deploy it to the fleet"
status: "Done"
rfcs: []
depends_on: []
metadata: {"baseline":"315940154e4db5036b2d5727a58c31ec4c363f07","requested_on":"2026-11-27"}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"59096491d3a70726be03e99735bf95341a919bd3","evidence":{"kind":"observation","detail":"The 12-file ux-design package has payload digest sha256:7139eb892ec65fd57f811850560d4ceccce15220cfc70944903dd8fe1c306b2a. Its core routes to nine references, and a package search found no consumer project names. A five-task fresh-agent tabletop selected the intended references, and its three wording fixes were applied."}},{"criterion":"AC2","outcome":"pass","revision":"59096491d3a70726be03e99735bf95341a919bd3","evidence":{"kind":"command","detail":"Live references use ux-design, and clang-split-refactor is in the manifest. MASK validated both packages from a disposable bare tap and from the published tap with the same digest. The documentation, portable-source and skill-metadata checks passed. The offline suite passed 463 of 469 tests with 4 skipped; its two implement-rfc failures reproduce identically at baseline 3159401."}},{"criterion":"AC3","outcome":"pass","revision":"59096491d3a70726be03e99735bf95341a919bd3","evidence":{"kind":"observation","detail":"3159401..5909649 was pushed to origin/main; the outgoing history held only this card's reservation, record, claim and source commits."}},{"criterion":"AC4","outcome":"pass","revision":"59096491d3a70726be03e99735bf95341a919bd3","evidence":{"kind":"observation","detail":"Fleet operation b717b78da4910d7f40a259111c6b42a7 reported applied_verified on this-mac, intel-mac, jaegaw-windows and jaegaw-wsl, each binding ux-design at 5909649 for Claude and Codex. In aito, ux-design replaced frontend-design under status --check, was committed at 4401245266 and pushed with 904b7cf799. In Athens, MASK-0155 enabled a reviewed return to pinned for the renumbered attended-review dev link, which was not restored at the owner's direction; ux-design then replaced frontend-design and status --check reports ready_pinned. Temporary lanes, agent worktrees and other devices' project checkouts were intentionally excluded."}}]
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
  `frontend-design` was removed; `status --check` passes. On the owner's
  instruction, aito commit `4401245266` recorded the declaration, lock and
  `ux-design` link ignores. The owner then authorized pushing aito's main and
  delegated LFS budget growth. Aito commit `904b7cf799` synced its resident
  ledger, raised two scope caps and added exact-OID exceptions under its
  documented policy. Main was pushed `fb60bed610..904b7cf799`, uploading
  313 LFS objects (266 MB). Aito's `docs/lfs-storage.md` records the figures
  and backend-volume capacity evidence.
- The Athens primary checkout was first blocked. Its `attended-review` was
  dev-linked to the AgentSkills authoring checkout, and MASK refused install,
  repair, return to pinned and re-linking with `source.identity_mismatch`. The
  recorded authoring-root device number (16777230) predated the volume change
  (16777231, same inode). ManageAgentSkills MASK-0155 (`7f9b815`, landed on
  local main, not pushed) extended durable identity to dev-link provenance with
  a reviewed rebind exit. With it, `status --check` reported the binding as
  rebindable. The owner then stated that no project should use dev links; a scan
  of all 1,292 registered rows found this one. A reviewed `skill dev-link
  --to-pinned` returned it to its locked payload, and the link was not restored.
  Athens then installed `ux-design` and removed `frontend-design`. Its
  `status --check` reports `ready_pinned`, and the new links match the
  published bytes. Its wildcard `.gitignore` already covers the links; the
  declaration and lock changes are uncommitted.
- Temporary lanes and agent worktrees that still select `frontend-design` were
  left untouched. Project checkouts on other devices were not inspected.

Both primary project consumers and all four personal fleet scopes now use
`ux-design`. Temporary lanes and agent worktrees that still select
`frontend-design` were left untouched by design, as were project checkouts on
other devices.
