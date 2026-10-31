# Review hub publisher live import

Source: the owner-reviewed [review hub pack](../../drafts/review-hub/README.md),
draft revision 2 (2026-10-30), retained in place as provenance with its supplied
revision 1 at [review-hub-draft-v1](../../assets/review-hub-draft-v1/README.md).
Both are immutable after this import; the live RFC, cards and adopted plan are
authoritative. Imported through the pack's
[publisher plan](../../drafts/review-hub/plans/publisher/milestone-plan.json)
(`milestone_plan.py adopt` with [id-map.json](id-map.json); receipt in
[source.json](source.json)).

| Pack ID | Live destination | Notes |
|---|---|---|
| RFC-DRAFT-0001 | [RFC-ASK-0018](../../RFC-ASK-0018-review-hub-session-publication.md) | Session publication; SHA-256 of the draft `c0900de7a1062d49313349af4092c7bbc8cb710f4792be396cdaa589f333ff09` |
| DRAFT-0001 | [ASK-0129](../../../issues/30-in-progress/ASK-0129-optional-hub-publication.md) | session-publication milestone |
| DRAFT-0004 | [ASK-0130](../../../issues/10-backlog/ASK-0130-close-review-hub-publication-rfc.md) | Closeout for RFC-ASK-0018 |
| RFC-DRAFT-0002 | External (standalone service repository, D4) | Not imported here |
| DRAFT-0002, DRAFT-0003, DRAFT-0005 | External (standalone service repository) | Not imported here; DRAFT-0002's prerequisite on the publisher becomes an `external_depends_on` on `AgentSkills:ASK-0129`/ASK-0130 with the recorded completion commit |

IDs were reserved on main as `ASK-0129--ASK-0130--2a17285558ef` (NEXT_ID now
ASK-0131). RFC_BASE_SHA: `ff6b40727e673cf4defd9a6cbaca7816558eb1de` (the reservation
commit, before any source edit). The owner's 2026-10-30 mandate records acceptance.

Deliberate changes on import: links were rebased from the pack to the live tree;
the publisher RFC's sentence saying the hub authorizes proxy identity/capability
headers was replaced with D8's settled answer (tailnet reachability is the only
hub access boundary; the client still sends no credential). The RFC text is
otherwise unchanged. The umbrella plan and service plan are not adopted here.
