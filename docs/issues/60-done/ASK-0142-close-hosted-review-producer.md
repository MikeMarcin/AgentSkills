---
schema: "implement-rfc.card.v1"
id: "ASK-0142"
title: "Close out RFC-ASK-0020"
status: "Done"
rfcs: ["RFC-ASK-0020"]
depends_on: ["ASK-0141"]
closeout_for: ["RFC-ASK-0020"]
metadata: {"milestone_plan":{"id":"hosted-review-producer","path":"docs/rfcs/plans/hosted-review-producer/milestone-plan.json"}}
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"a4785fe662f8201c98e4107a4989e54795cc11b3","evidence":{"kind":"observation","detail":"test_explicit_mode_isolated_through_two_consumer_links and test_actual_hub_offline_publication_and_durable_handback: selected package, lost media and commit replies, mode isolation, immutable binding."}},{"criterion":"AC02","outcome":"pass","revision":"a4785fe662f8201c98e4107a4989e54795cc11b3","evidence":{"kind":"observation","detail":"test_actual_hub_offline_publication_and_durable_handback and test_binding_conflicts_and_transport_refusals: actual hub offline freeze, storage failure, crash after archive fsync, conflict preservation, wrong binding and dropped ACK replay."}},{"criterion":"AC03","outcome":"pass","revision":"a4785fe662f8201c98e4107a4989e54795cc11b3","evidence":{"kind":"observation","detail":"Native tests opened the Unicode archive through the unchanged d06e564 reader, refused wrong TLS hostname and redirect before credential delivery, and exercised existing pass-through publication tests."}}]
---

# Close out RFC-ASK-0020

RFC_BASE_SHA: f2bb69050737615a519ca836adbeed237eb66474

Planned local cards: ASK-0141 and ASK-0142. Record local native producer evidence
and the source revision usable for the AttendedReviewHub ARH-0012 handoff.

| Criterion | Check | Outcome | Implementation commit |
|---|---|---|---|
| AC01 | Public CLI from two symlinked consumers. Package preserves selected order and exact bytes across lost asset and commit replies and refuses local writers or mode conversion. | Pass | `a4785fe662f8201c98e4107a4989e54795cc11b3` |
| AC02 | Actual hub over private sockets and loopback HTTPS. Offline freeze, incorrect binding and fingerprints, failed export, process death after archive fsync, preserved conflict, omitted and selected answers, replay and lost ACK. | Pass | `a4785fe662f8201c98e4107a4989e54795cc11b3` |
| AC03 | The pre-change d06e564 JSON reader opened the exact archive with Unicode, inline media, prior events and the Hand Back marker. TLS rejected a wrong hostname and redirect. Existing pass-through regression suite passed. | Pass | `a4785fe662f8201c98e4107a4989e54795cc11b3` |

## Verification and execution record

The assignment was `native-hosted-producer` on AgentSkills main, starting at
`d06e564f94697d2f2419d27fd4fbce97f4472c17`. Run
`hosted-producer-local-20261124`, segment
`local-coordinator-implementer-1`, mandate `2026-11-24-native-local-only`.
The counterpart is AttendedReviewHub
`c9e38c56ae9902baa57850a5e5b64d90a16fb5b0`.

The [native implementation](../../../skills/attended-review/scripts/hosted_review.py)
adds `init --hosted`, `hosted-publish` and `hosted-poll` through
`attended_review.py`, with native SQLite writes and archive recovery in
[review_store.py](../../../skills/attended-review/scripts/review_store.py).
The [operator instructions](../../../skills/attended-review/references/hosted-review.md)
document enrollment inputs and retries. The
[native integration tests](../../../skills/attended-review/tests/test_hosted_review.py)
cover the public commands against the hub. The
[pass-through tests](../../../skills/attended-review/tests/test_hub_publication.py)
run in the same suite.

- From AgentSkills, `ATTENDED_REVIEW_HUB_ROOT=../AttendedReviewHub python3 -B -m unittest discover -s skills/attended-review/tests -v`.
  PASS, 67 tests on Darwin arm64 with Python 3.15.0.
- From AttendedReviewHub, `AGENTSKILLS_ROOT=../AgentSkills python3 -B -m unittest tests.test_hosted_handback tests.test_handback_origin`.
  PASS, five tests. The optional browser case skipped without `HUB_TEST_BROWSER`.
- `python3 -B scripts/verify_documentation.py --root .` and scoped board validation.
  PASS. BetterLeaks staged product scan found zero findings.

Early fixture runs caught a test context manager error and a missing `observe --evidence` argument. Both fixture issues
were corrected and the suite rerun against the product candidate. Closeout
review runtime was the implementing agent's self-review.

The native local scope has no outstanding acceptance or protected candidate.
The tests used temporary consumer state and sockets. All task-owned test
processes stopped. The next action is hub-side reconciliation of ARH-0012 and
ARH-0013 using this native candidate. Hub deployment, consumer installation and
real Serve or tailnet qualification are separate owner scopes.
