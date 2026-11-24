---
schema: "implement-rfc.card.v1"
id: "ASK-0141"
title: "Integrate the native hosted review producer"
status: "Done"
rfcs: ["RFC-ASK-0020"]
depends_on: []
metadata: {"milestone_plan":{"id":"hosted-review-producer","path":"docs/rfcs/plans/hosted-review-producer/milestone-plan.json"}}
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"a4785fe662f8201c98e4107a4989e54795cc11b3","evidence":{"kind":"observation","detail":"test_explicit_mode_isolated_through_two_consumer_links and test_actual_hub_offline_publication_and_durable_handback: selected package, lost media and commit replies, mode isolation, immutable binding."}},{"criterion":"AC02","outcome":"pass","revision":"a4785fe662f8201c98e4107a4989e54795cc11b3","evidence":{"kind":"observation","detail":"test_actual_hub_offline_publication_and_durable_handback and test_binding_conflicts_and_transport_refusals: actual hub offline freeze, storage failure, crash after archive fsync, conflict preservation, wrong binding and dropped ACK replay."}},{"criterion":"AC03","outcome":"pass","revision":"a4785fe662f8201c98e4107a4989e54795cc11b3","evidence":{"kind":"observation","detail":"Native tests opened the Unicode archive through the unchanged d06e564 reader, refused wrong TLS hostname and redirect before credential delivery, and exercised existing pass-through publication tests."}}]
---

# Integrate the native hosted review producer

Implement and exercise the native producer against the local hub. The hub
publication contract is verified in AttendedReviewHub ARH-0010 and its durable
freeze and delivery are verified in ARH-0011, both present at `c9e38c56ae9902baa57850a5e5b64d90a16fb5b0`.
Verify RFC-ASK-0020 AC01–AC03 using disposable loopback fixtures.
