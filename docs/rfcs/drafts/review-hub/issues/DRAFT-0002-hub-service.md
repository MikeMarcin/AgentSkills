---
schema: "implement-rfc.card.v1"
id: "DRAFT-0002"
title: "NAS review hub service and compose stack"
status: "Backlog"
rfcs: ["RFC-DRAFT-0002"]
depends_on: []
external_depends_on: ["AgentSkills:DRAFT-0004"]
---

# NAS review hub service and compose stack

## Scope and acceptance

Implement [RFC-DRAFT-0002](../rfcs/RFC-DRAFT-0002-review-hub-service.md)
AC01–AC05 and AC08 in the **new standalone repository** selected in
[D4](../DECISIONS.md): hub, Compose/Tailscale configuration, access, API, page,
ordering, retention and capability protection, with tailnet-only access per D8.
The hub-only stack must work with the push profile disabled.

Adopt the [service plan](../plans/service/milestone-plan.json). During import, remap
the provisional external dependency to the actual AgentSkills publisher closeout
card; record its integrated contract revision and run a local handoff check. Do
not allocate this service card on AgentSkills' board.

Use a disposable fixture stack for engineering checks. The owner supplies keys and
access setup; actual NAS deployment observations require authorized deployment
scope. Keep those required observations open until obtained.
