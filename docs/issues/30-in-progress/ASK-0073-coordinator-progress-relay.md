---
schema: "implement-rfc.card.v1"
id: "ASK-0073"
title: "Coordinator progress relay with a bounded wake budget"
status: "In Progress"
rfcs: []
depends_on: []
priority: "P2"
---

# ASK-0073: Coordinator progress relay with a bounded wake budget

## Design and scope

Authorized by the owner on 2026-09-11 from
[the relay plan](../../development/coordinator-progress-relay-plan.md). Owner-selected
direct mode in the main session; no integrator family was started. Baseline:
3070ea00086375e6b5519b2660a540df52eb9e58.

One integrated outcome: while a milestone runs, an owner who asks for a visible run
sees one coalesced burst of slice-trail lines per wake gap in the coordinator chat, the
coordinator spends no wake the trail did not earn, and the same helper serves an owner
terminal and a Codex driver without a second mechanism. Owned paths: the trail helper
and its tests, `references/progress-relay.md`, one sentence in `SKILL.md` step 3, one
dated observation in `references/runtime-compatibility.md`, the instruction-path test,
the portable manifest and this card. No routes, permissions, board schema, milestone
selection or Codex lane-log changes.

## Acceptance

- AC1: The coordinator entrypoint gains one sentence selecting background dispatch and
  the trail digest for an owner-requested visible run, pointing at the disclosed
  reference; static coordinator reading grows by no more than 250 UTF-8 bytes and the
  status-only, review-only and usage-only branches load no additional material.
- AC2: `scripts/progress_trail.py` reports one line per committed lane transition,
  scoped commit, pending lane move and changed in-flight set for an explicitly supplied
  consumer root, resolves the consumer through the project config contract, refuses an
  unreadable, unmanaged or non-root path and a non-ancestor cursor with exit 2, and
  leaves the consumer byte-identical including Git internals. Two differently configured
  linked fixture consumers exercise a claim, a scoped commit, a rewritten finish, a
  pending park, an idle interval and the refusals.
- AC3: Follow mode holds events and emits them as one burst no more than once per
  `--min-gap`, emits nothing while the trail and in-flight set are unchanged, and adds a
  heartbeat only when `--quiet-after` is set and the in-flight set changed. One-shot mode
  carries its cursor in `--since` and prints the next cursor, so a host without
  `Monitor` relays on the wakes its bounded wait already produces.
- AC4: Dated observations in `runtime-compatibility.md` state that `Monitor` events
  queue behind a foreground dispatch and that a background `rfc-integrator` dispatched a
  leaf on this host, and the adopted dispatch mode follows them.
- AC5: On one real milestone with a visible run, relay turns forward bursts and end with
  no tool use, no board query, no second dispatch and no acceptance statement from the
  coordinator.

## Verification and continuation

Focused public helper tests, the instruction-path test, source manifest validation and
the repository structure gate. AC5 needs a real milestone observed end to end in a
linked consumer; a fixture cannot supply it and it remains open at filing. Static
reading growth is a reading-size observation, not a measured token or billing result.
Exit: AC1 to AC4 accepted here, AC5 recorded from the first visible run.

## Current execution evidence

Host observations (desktop app Code tab, Claude Code 2.1.266, 2026-09-11): five
`Monitor` ticks emitted during a 95-second foreground `Agent` call arrived as one batch
after it returned; a background `rfc-integrator` listed `Agent` (without `Grep`/`Glob`),
dispatched an `rfc-utility` leaf and returned its reply. Both recorded under
`### Foreground dispatch and Monitor events (2026-09-11)`.

Helper: `skills/implement-rfc/scripts/progress_trail.py`. Tests:
`skills/implement-rfc/tests/test_progress_trail.py` (3 courses, two linked consumers,
byte-identical digest over the whole consumer tree including `.git`). Reference:
`skills/implement-rfc/references/progress-relay.md`. Step 3 sentence: 177 UTF-8 bytes
including its newline. AC5 open: no visible run has been observed yet.
