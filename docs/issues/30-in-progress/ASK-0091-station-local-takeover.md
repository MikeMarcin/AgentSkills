---
schema: "implement-rfc.card.v1"
id: "ASK-0091"
title: "Managed station local takeover"
status: "In Progress"
rfcs: []
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"station-local-takeover","path":"docs/rfcs/plans/station-local-takeover/milestone-plan.json"}}
---

# Managed station local takeover

Owner-authorized on 2026-09-29; assignment `/root/station_takeover`, mandate
`station-local-takeover-20260929-v1`, selected coordinator-implementer strategy.
RFC_BASE_SHA: acc7ac56a588e5b818ee99a117b6e917b07f1930 (pre-source baseline).
No existing RFC is amended or closed by this bounded follow-up.

Keep hooks for explicitly managed stations. Accept replacement prompts and bounded
inspection/recovery while restricting mutations until the prior writer is quiescent.
Provide JSON status and `takeover --mode local --stop-previous`, with scoped runtime
stop evidence and supervisor proof. A human instruction to resume here authorizes
that operation without another confirmation; the hook itself never parses prose as
mutation authority. Retain history, dirty edits, checkpoints, obligations and strategy.
Fence retired endpoints, serialize competing transfers, recover interruptions and
preserve launcher fresh contexts. Metadata age is never inactivity evidence. No
automatic old-chat archive, arbitrary sidecar PID kill, live runtime launch, station
stop, deployment, push or MASK changes.

## Acceptance

AC1: Ordinary unbound local chats remain unrestricted; managed replacement prompts and exact bounded inspection/recovery commands work while writes require quiescence.

AC2: JSON status and authorized local takeover preserve history, dirty edits, checkpoints, obligations and strategy, fence retired endpoints durably, serialize transfers and recover interrupted operations.

AC3: Project, branch, endpoint, envelope and supervisor lease guards remain enforced; fresh launcher contexts work and unsupported stop adapters provide precise manual recovery without guessing inactivity.

AC4: Focused fixture-process and mocked-runtime tests cover paused, crashed, active, stale, repeated, concurrent, interrupted, dirty and retired writes; two linked consumer compositions, package and documentation gates pass.

[Plan](../../rfcs/plans/station-local-takeover/milestone-plan.json).
[Durable checkpoint](../../development/station-takeover.md).
