---
schema: "implement-rfc.card.v1"
id: "ASK-0145"
title: "Rename frontend-design to ux-design and deploy it to the fleet"
status: "In Progress"
rfcs: []
depends_on: []
metadata: {"baseline":"315940154e4db5036b2d5727a58c31ec4c363f07","requested_on":"2026-11-27"}
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
