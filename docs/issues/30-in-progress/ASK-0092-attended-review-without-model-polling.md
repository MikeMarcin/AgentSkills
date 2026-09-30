---
schema: "implement-rfc.card.v1"
id: "ASK-0092"
title: "Attended review without model polling"
status: "In Progress"
rfcs: []
depends_on: []
priority: "P1"
metadata: {"related_rfcs":["RFC-ASK-0003","RFC-ASK-0014"],"milestone_plan":{"id":"attended-review-wait","path":"docs/rfcs/plans/attended-review-wait/milestone-plan.json"}}
---

# Attended review without model polling

Follow-up correction; retain the historical acceptance of ASK-0010.

Owned paths: attended-review driver instructions, wait-focused tests and evidence;
implement-rfc attendance and coordinator recipes; this card.

The user approved the plan on 2026-09-30: one pending Codex tool call instead of
recurring model checks, preserve Claude's persistent monitor, qualify the actual
runtime, and pause the named aito heartbeat before replacing its handoff.
Direct strategy; no model delegation, publication, or other consumer deployment.

## Acceptance

- ASK-0092-AC01: canonical instructions select a verified host wait, distinguish
  tool-side polling from model polling, and preserve handback-only intake and
  explicit interruption/manual-resume behavior.
- ASK-0092-AC02: focused public tests and actual Codex-wrapper probes record
  truthful evidence: no idle model requests, handback-only return, and safe
  cancellation. Record the observed duration; overnight reliability remains
  unverified. If the runtime forces intermediate model wakeups, record that
  limitation and use manual resume instead.
- ASK-0092-AC03: pause only the authorized aito heartbeat, preserve the live
  review and pinned engineering workflow, and send its chat one setup message
  describing the qualified wait or the explicit manual-resume fallback.

## Plan and checkpoint

1. Pause the heartbeat; orient and claim this correction.
2. Probe the complete Codex wait stack using disposable review state.
3. Correct canonical instructions and focused tests; verify portable packages.
4. Record actual qualification and send the scoped aito setup message.

The existing Python wait API and session schema remain unchanged. A configured
timeout is not evidence of an uninterrupted wait. A runtime capability failure
ends automatic qualification rather than falling back to recurring inference.

Amendment on 2026-09-30: the user cancelled the extended test and waived the
six-hour prerequisite, choosing to observe overnight behavior during ordinary
use. Preserve the bounded proof and interruption evidence without claiming
overnight qualification. The fixture waiter, delayed handback trigger and
temporary keep-awake process were stopped; no fixture handback was injected.
