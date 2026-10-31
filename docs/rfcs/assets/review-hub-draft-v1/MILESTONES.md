# Milestones

> Generated from `milestone-plan.json`; edit the JSON, not this view.

Plan: **review-hub** · Coverage: **complete**

These are integration outcomes, not compulsory agent-launch boundaries.

## session-publication

Attended-review sessions can optionally announce themselves to a configured hub without any effect on review when the hub is absent or failing.

**Work:** `RFC-DRAFT-0001` [AC01, AC02, AC03, AC04, AC05]

**Prerequisites:** None

**Completion:**

- The publisher sends the version-1 record at every defined point against a fixture hub, and unchanged behavior holds with no hub or a failing hub.

**Boundary:** A released attended-review client and record contract, usable before any hub exists.

## hub-service

The owner can open one tailnet-only page on the NAS that lists every active review across machines and links to each.

**Work:** `RFC-DRAFT-0002` [AC01, AC02, AC03, AC04, AC05]

**Prerequisites:** session-publication

**Completion:**

- The compose stack serves the identity-restricted hub over Tailscale Serve only, with listing, stale handling and no influence on review state.

**Boundary:** A deployable hub without push.

## hub-push

The owner's Android phone is notified when a session gains ready items, without anything leaving the tailnet.

**Work:** `RFC-DRAFT-0002` [AC06, AC07]

**Prerequisites:** hub-service

**Completion:**

- Throttled, content-free ntfy messages reach a subscribed device through a locked-down tailnet-only ntfy server.

**Boundary:** The complete defined hub outcome with closeout evidence; iOS stays deferred.
