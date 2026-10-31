---
schema: "implement-rfc.card.v1"
id: "ASK-0129"
title: "Optional hub publication from attended-review"
status: "Ready"
rfcs: ["RFC-ASK-0018"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"review-hub-publisher","path":"docs/rfcs/plans/review-hub-publisher/milestone-plan.json"},"original_id":"DRAFT-0001"}
---

# Optional hub publication from attended-review

Imported from DRAFT-0001 of the [review hub pack](../../rfcs/drafts/review-hub/README.md).

## Scope and acceptance

Implement [RFC-ASK-0018](../../rfcs/RFC-ASK-0018-review-hub-session-publication.md)
AC01–AC07 in AgentSkills' `skills/attended-review`: configuration lifetime, exact
record projection, ordered publication, heartbeat and failure isolation. Update
the skill's session/transport documentation and README. Use disposable session
roots and a fixture hub, including TLS/error injection; do not connect real review
capabilities to a test service or alter installed consumers.

Adopt the [publisher plan](../../rfcs/plans/review-hub-publisher/milestone-plan.json).
Provide the standalone service with the versioned wire contract and fixture records
through the closeout handoff.
