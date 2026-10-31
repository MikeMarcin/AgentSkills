---
schema: "implement-rfc.card.v1"
id: "ASK-0129"
title: "Optional hub publication from attended-review"
status: "Done"
rfcs: ["RFC-ASK-0018"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"review-hub-publisher","path":"docs/rfcs/plans/review-hub-publisher/milestone-plan.json"},"original_id":"DRAFT-0001"}
acceptance: [{"criterion":"RFC-ASK-0018-AC01","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Never-enabled serve/browser/CLI: no hub files, fields, output or requests; differential against RFC_BASE_SHA helper identical after normalizing random/time fields."}},{"criterion":"RFC-ASK-0018-AC02","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Exact v1 record keys at host start, CLI and browser publication points; unserved/loopback and private review content absent."}},{"criterion":"RFC-ASK-0018-AC03","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"6 s and unreachable fixture hubs and broken hub.json: answers saved, browser under 1.5 s, unchanged exit semantics, non-overlapping coalesced attempts, warning appears and clears."}},{"criterion":"RFC-ASK-0018-AC04","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Invalid origins refused before configuration; impostor certificate and 307 redirect receive/forward no capability; diagnostics carry no payload/token."}},{"criterion":"RFC-ASK-0018-AC05","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Identical heartbeat records at the interval without advancing sequence or revision; constants 300 s and 3 s."}},{"criterion":"RFC-ASK-0018-AC06","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Disjoint counts/states across mixed phases, withdrawal, pause, partial handback and resume; stop/restart and 6 concurrent CLI callers preserve revision ordering."}},{"criterion":"RFC-ASK-0018-AC07","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Flag over environment over saved; reuse across shells and host attachment; --no-hub clears and cancels; no browser network wait; symlinked skill in two consumers."}}]
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
