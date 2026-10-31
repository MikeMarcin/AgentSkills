---
schema: "implement-rfc.card.v1"
id: "ASK-0130"
title: "Close out RFC-ASK-0018"
status: "Done"
rfcs: ["RFC-ASK-0018"]
depends_on: ["ASK-0129"]
closeout_for: ["RFC-ASK-0018"]
priority: "P1"
metadata: {"milestone_plan":{"id":"review-hub-publisher","path":"docs/rfcs/plans/review-hub-publisher/milestone-plan.json"},"original_id":"DRAFT-0004"}
acceptance: [{"criterion":"RFC-ASK-0018-AC01","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: Never-enabled serve/browser/CLI: no hub files, fields, output or requests; differential against RFC_BASE_SHA helper identical after normalizing random/time fields."}},{"criterion":"RFC-ASK-0018-AC02","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: Exact v1 record keys at host start, CLI and browser publication points; unserved/loopback and private review content absent."}},{"criterion":"RFC-ASK-0018-AC03","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: 6 s and unreachable fixture hubs and broken hub.json: answers saved, browser under 1.5 s, unchanged exit semantics, non-overlapping coalesced attempts, warning appears and clears."}},{"criterion":"RFC-ASK-0018-AC04","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: Invalid origins refused before configuration; impostor certificate and 307 redirect receive/forward no capability; diagnostics carry no payload/token."}},{"criterion":"RFC-ASK-0018-AC05","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: Identical heartbeat records at the interval without advancing sequence or revision; constants 300 s and 3 s."}},{"criterion":"RFC-ASK-0018-AC06","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: Disjoint counts/states across mixed phases, withdrawal, pause, partial handback and resume; stop/restart and 6 concurrent CLI callers preserve revision ordering."}},{"criterion":"RFC-ASK-0018-AC07","outcome":"pass","revision":"3cb685646a09f454fd407a5596c036683db261a2","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Verified together at closeout: Flag over environment over saved; reuse across shells and host attachment; --no-hub clears and cancels; no browser network wait; symlinked skill in two consumers."}}]
---

# Close out RFC-ASK-0018

Imported from DRAFT-0004 of the [review hub pack](../../rfcs/drafts/review-hub/README.md).

RFC_BASE_SHA: ff6b40727e673cf4defd9a6cbaca7816558eb1de

Planned local cards: ASK-0129 (session-publication), ASK-0130 (closeout).

## Scope and acceptance

Close out [RFC-ASK-0018](../../rfcs/RFC-ASK-0018-review-hub-session-publication.md)
in AgentSkills by verifying AC01–AC07 together. Baseline and criterion/evidence/
outcome/implementation-revision rows come from authorized execution.

Record the integrated publisher/contract revision for the standalone service's
external dependency. This handoff does not claim the hub is deployed or that a
managed consumer has loaded the new publisher.

Closeout review runtime: local implementer self-review (claude-opus-5-5); no
independent or human gate is required by the RFC.

## Acceptance checklist

Checked together at `3cb685646a09f454fd407a5596c036683db261a2` with
`python3 -B -m unittest discover -s skills/attended-review/tests` (52 OK) and the
[criterion checklist](../../rfcs/plans/review-hub-publisher/verification.md).

| Criterion | Check/command | Outcome | Implementation commit |
|---|---|---|---|
| AC01 | Never-enabled hub test; [AC01 differential](../../rfcs/plans/review-hub-publisher/ac01_differential.py) against RFC_BASE_SHA | pass | 3cb685646a09f454fd407a5596c036683db261a2 |
| AC02 | Exact wire contract at publication points, private material absent | pass | 3cb685646a09f454fd407a5596c036683db261a2 |
| AC03 | Slow/unreachable hub and broken metadata isolation | pass | 3cb685646a09f454fd407a5596c036683db261a2 |
| AC04 | Invalid origins, impostor certificate, refused redirect | pass | 3cb685646a09f454fd407a5596c036683db261a2 |
| AC05 | Identical heartbeat; 300 s / 3 s constants | pass | 3cb685646a09f454fd407a5596c036683db261a2 |
| AC06 | Disjoint counts/states; restart and concurrent ordering | pass | 3cb685646a09f454fd407a5596c036683db261a2 |
| AC07 | Configuration precedence, reuse, attachment, disabling; two symlinked consumers | pass | 3cb685646a09f454fd407a5596c036683db261a2 |

Structure gate: `python3 -B scripts/verify_documentation.py --root .` (0 violations).

## Service handoff

Integrated publisher/wire-contract revision for the standalone service's external
dependency: **AgentSkills `3cb685646a09f454fd407a5596c036683db261a2`**, contract
in `skills/attended-review/references/session-contract.md` § Optional hub
publication, with [fixture records](../../rfcs/plans/review-hub-publisher/fixture-records.json).
The service imports RFC-DRAFT-0002 and DRAFT-0002/0003/0005 from the retained
[pack](../../rfcs/drafts/review-hub/README.md) and records
`external_depends_on: ["AgentSkills:ASK-0130"]` against that completion commit.
This handoff does not claim a hub is deployed or that any managed consumer has
loaded the new publisher. See the [continuation](../../rfcs/plans/review-hub-publisher/continuation.md).
