---
schema: "implement-rfc.card.v1"
id: "DRAFT-0001"
title: "Optional hub publication from attended-review"
status: "Backlog"
rfcs: ["RFC-DRAFT-0001"]
depends_on: []
---

# Optional hub publication from attended-review

## Scope and acceptance

Implement [RFC-DRAFT-0001](../rfcs/RFC-DRAFT-0001-review-hub-session-publication.md)
AC01–AC07 in AgentSkills' `skills/attended-review`: configuration lifetime, exact
record projection, ordered publication, heartbeat and failure isolation. Update
the skill's session/transport documentation and README. Use disposable session
roots and a fixture hub, including TLS/error injection; do not connect real review
capabilities to a test service or alter installed consumers.

Adopt the [publisher plan](../plans/publisher/milestone-plan.json). Provide the
standalone service with the versioned wire contract and fixture records through
the closeout handoff.
