---
schema: implement-rfc.card.v1
id: ASK-0119
title: Standard remote attended review with automatic handback continuation
status: Ready
rfcs: []
depends_on: []
priority: P1
metadata: {"milestone_plan":{"id":"remote-review-standard","path":"docs/rfcs/plans/remote-review-standard/milestone-plan.json"}}
---

# Standard remote attended review with automatic handback continuation

Mandate `remote-review-standard-v1`: make Tailscale Serve and automatic handback
continuation the standard remote attended-review instructions. Assignment
`/root/remote_review_standard`; run `remote-review-standard-2026-10-21`, segment
`instructions-1`; baseline `38d0715610fa9255fdf990067c43b669c7d54191`, AgentSkills main.

Own attended-review instructions, minimal contradictory implement-rfc caller
wording, catalog alignment and bounded plan/evidence upkeep. Preserve unrelated
`.mask.lock.json`. No runtime, tests, setup, configuration, deployment, live server,
tailnet/access changes, new acceptance ceremony, publication or push.

- **RS01:** Remote/phone/another-device and SSH/remote-control/Dot reviews route to
  existing-tailnet `serve --tailscale`; local-at-computer review retains loopback.
  Requested remote review authorizes its temporary scoped session without repeated
  transport approval. Missing setup remains explicit and user-owned; retain unused
  already-permitted ports, tokens, origins, process ownership and scoped cleanup.
- **RS02:** Before handover, read Driver waiting, save exact source/state/registry,
  session/cursor/candidates/server/waiter/owner, release engineering writers and arm
  a handback-only wait. Present the full capability link and retain one outer Codex
  tool call without a final answer. Reuse matching qualification; preserve Claude's
  qualified persistent monitor. Validate return/session/candidates and persist the
  consumed cursor before dispatch. Unavailable/changed/failed hosts get explicit
  manual resume with awake-host/tool-connection limits.
- **RS03:** Retain historical failures and record sanitized observed phone/awake
  Codex evidence accurately. Remote/local/unavailable-host local tabletop and
  focused skill, documentation, board and portable-source checks pass. Commit
  explicit paths and hand off quiescent ownership; no runtime or deployment claim.

The existing [prototype verification](../../rfcs/plans/attended-review-tailscale/verification.md)
retains transport history. Current continuation and checks belong in the linked
compact milestone plan directory.
