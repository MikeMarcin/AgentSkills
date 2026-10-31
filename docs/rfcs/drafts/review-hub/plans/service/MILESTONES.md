# Milestones

> Generated from `milestone-plan.json`; edit the JSON, not this view.

Plan: **review-hub-service** · Coverage: **complete**

These are integration outcomes, not compulsory agent-launch boundaries.

## hub-service

The owner can open one tailnet-only page on the NAS that lists every active review across machines and links to each.

**Work:** `RFC-DRAFT-0002` [AC01, AC02, AC03, AC04, AC05, AC08]

**Prerequisites:** None

**Completion:**

- The standalone stack provides the authorized, capability-protecting index with ordered durable records, stale handling and no review control; required NAS deployment evidence is recorded.

**Boundary:** A verified hub on the NAS with push disabled. Fixture-only results leave deployment acceptance open.

## hub-push

The owner receives Android notifications for qualifying ready-count increases through the self-hosted tailnet service, without sending summaries or capabilities to external notification providers.

**Work:** `RFC-DRAFT-0002` [AC06, AC07]

**Prerequisites:** hub-service

**Completion:**

- Persistent throttling, account restrictions and failure isolation pass fixture checks, and an authorized screen-off Android observation demonstrates delivery of the summary and hub link.

**Boundary:** The defined hub and optional push outcome with actual closeout evidence; iOS remains deferred.
