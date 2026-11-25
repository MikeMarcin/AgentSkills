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

## Recovery correction after critical review

The owner authorized a local correction round on the same milestone and
mandate. This round started from `8bdb8ea8e05bae4affe68f0b48f9c12d36601c94`
and used AttendedReviewHub `2e7dcd59ea36c597b4eedf6688109964c8138175`.
The corrected native candidate is `24db66b9f10e66d2231703dceecfabcb44304086`.
It supplements the original AC01–AC03 evidence above.

| Finding | Verified behavior |
|---|---|
| Cached local ACK after hub restore | The original producer confirms the stored delivery against the live hub after verifying the durable archive. Restoring a pre-ACK backup left the hub waiting. A fresh matching ACK returned it to delivered without changing the local archive or events. |
| Copied origin database | A backup opened from a different state directory of the same checkout was refused before an archive or producer request. A symlink that resolves to the original directory worked. An earlier unbound hosted database could not publish or ACK. |
| Origin restored before intake | After restoring the origin to before intake and the hub to before ACK, an unrelated archive stayed in place and no decisions, receipts or export rows committed. Restoring the exact archive allowed the original producer to reconcile one Hand Back and ACK without replacing the file. |

The [focused native tests](../../../skills/attended-review/tests/test_hosted_review.py)
passed all seven cases on macOS, including the three regressions above.
Run `ATTENDED_REVIEW_HUB_ROOT=../AttendedReviewHub python3 -B -m unittest discover -s skills/attended-review/tests -p test_hosted_review.py -v`
from the AgentSkills checkout. The two existing SQLite lifecycle tests passed
with `python3 -B -m unittest discover -s skills/attended-review/tests -p test_sqlite_lifecycle.py -v`.
The staged BetterLeaks scan reported zero findings.

Earlier unbound hosted states need a new bound session for publication.
If a previous published review needs recovery, preserve its local files
and use the owner's frozen export for manual reconciliation. An already
acknowledged hub delivery also needs the owner's export if the origin's receipt
is missing. The [operator instructions](../../../skills/attended-review/references/hosted-review.md)
describe these boundaries.

The independent recheck passed the three recovery cases and identified a
replacement-session blocker when an earlier published review owns an exclusive
resource. Candidate `73c6034f971ef56532b5c709dd6565bd5b1d6fef` adds scoped
offline `resume-development` for that earlier origin. The prior helper
prepared and published a candidate with an exclusive named resource. A
replacement using the same checkout and registry waited until the original
released that candidate. The replacement then prepared successfully. The
earlier origin continued to refuse publish, poll and archive recovery with
zero producer requests.

The final candidate passed all eight focused hosted tests and both SQLite
lifecycle tests using the commands above. Documentation, board validation and
the staged BetterLeaks scan passed. The broader 71-case run passed during the
earlier correction round. The final release change was verified by the focused
runs. The worktree is quiescent, and the same independent reviewer recheck is
pending on the final candidate.
