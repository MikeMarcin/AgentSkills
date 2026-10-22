---
schema: implement-rfc.card.v1
id: ASK-0120
title: Default private review transport and schedule waits around useful work
status: "In Progress"
rfcs: []
depends_on: ["ASK-0119"]
priority: P1
metadata: {"milestone_plan":{"id":"remote-review-standard","path":"docs/rfcs/plans/remote-review-standard/milestone-plan.json"}}
---

# Default private review transport and schedule waits around useful work

Mandate `remote-review-standard-v2` amends the completed v1 instruction policy:
Tailscale Serve is the default for every review, while blocking handback waits
start only when human input is the task's sole remaining dependency. Assignment
`/root/remote_review_standard`; run `remote-review-standard-2026-10-21`, initial
segment `amendment-1`; baseline `a52e04287e3d469bcdb67e2601d63cf502be2283`.
ASK-0119 remains terminal historical acceptance; this successor owns the amendment.

- **DEF01:** Explicit `serve --tailscale` is standard even at the source computer.
  Loopback/offline are explicit choices or deliberate fallbacks after missing setup.
  Session authorization covers temporary scoped transport; preserve user-owned
  installation/HTTPS/access decisions, no Funnel, and all existing token/origin,
  candidate, port and process ownership boundaries. Bare CLI `serve` is unchanged.
- **DEF02:** Publish the full usable HTTPS link while useful independent protected
  work continues; inspect durable intake at natural task boundaries, without model
  polling or heartbeat. A pending outer wait parks the coordinator and cannot
  service results/integration. When idle with only human input pending, release
  writers, persist exact ownership/session/cursor, read status from the consumed
  cursor and reconcile any existing handback. Otherwise wait from the checked cursor
  so racing handback is caught. Consume cursor after reconciliation before dispatch;
  preserve qualified automatic return, manual fallback, partial decisions and limits.
- **DEF03:** Local tabletop covers default-at-source, explicit local/offline, busy
  agents, pre-wait handback, status/wait race, idle return, unavailable runtime and
  duplicates. Focused docs/package/board/portable checks pass. Reuse unchanged awake
  evidence; no runtime, deployment, setup, live session, extra agents or new ceremony.

Own the same bounded instruction and tracker paths as ASK-0119. Preserve unrelated
`.mask.lock.json`; commit explicit paths, leave commands and ownership quiescent,
and report the source candidate and final integration revision. No publication/push.
