---
schema: "implement-rfc.card.v1"
id: "ASK-0033"
title: "Implement the capability-checked Codex event-driven adapter"
status: "Backlog"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0032"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "codex-event-adapter"}
---

# ASK-0033: Implement the capability-checked Codex event-driven adapter

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Bind the runner to installed app-server operations and exact owned thread/turn identities. Preserve authentication, user-selected routes, permission requests and supported structured completion. Keep startup/version/protocol capability independent. Do not treat an arbitrary native subagent ID as a top-level resumable thread. Where native embedded sessions cannot be controlled, expose a supported companion or explicit handoff instead of pretending zero-poll orchestration.

Own only: `skills/implement-rfc/scripts/slice_codex.py`; `skills/implement-rfc/tests/test_slice_codex.py`; `skills/implement-rfc/references/bounded-execution.md`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- The adapter wakes the integrator for decisions/gates, not every status interval.
- Runtime errors, quota blocks and unsupported operations preserve partial evidence and cannot fall through to API billing or approvals.

Criterion coverage: RFC-ASK-0005-AC05.

## Focused verification

Fake protocol transcripts assert exact launch/cancel/notification joins and unsupported behavior. Record a bounded live installed-CLI smoke only with approved capacity and permissions.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
