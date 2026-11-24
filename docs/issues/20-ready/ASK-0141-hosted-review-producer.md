---
schema: "implement-rfc.card.v1"
id: "ASK-0141"
title: "Integrate the native hosted review producer"
status: "Ready"
rfcs: ["RFC-ASK-0020"]
depends_on: []
metadata: {"milestone_plan":{"id":"hosted-review-producer","path":"docs/rfcs/plans/hosted-review-producer/milestone-plan.json"}}
---

# Integrate the native hosted review producer

Implement and exercise the native producer against the local hub. The hub
publication contract is verified in AttendedReviewHub ARH-0010 and its durable
freeze and delivery are verified in ARH-0011, both present at `c9e38c56ae9902baa57850a5e5b64d90a16fb5b0`.
Verify RFC-ASK-0020 AC01–AC03 using disposable loopback fixtures.
