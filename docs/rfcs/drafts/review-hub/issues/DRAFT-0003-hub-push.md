---
schema: "implement-rfc.card.v1"
id: "DRAFT-0003"
title: "Android push through self-hosted ntfy"
status: "Backlog"
rfcs: ["RFC-DRAFT-0002"]
depends_on: ["DRAFT-0002"]
---

# Android push through self-hosted ntfy

## Scope and acceptance

Implement [RFC-DRAFT-0002](../rfcs/RFC-DRAFT-0002-review-hub-service.md)
AC06–AC07 in the standalone service repository: optional ntfy profile, separate
publish/subscribe permissions, persistent quiet period and best-effort delivery.
Follow the [service plan](../plans/service/milestone-plan.json).

Verify failures and duplicate/reordered records with fixtures. Obtain an authorized
Android delivery observation with the screen off; a simulated subscriber is not
phone acceptance. Document required phone/tailnet setup and keep iOS deferred.
