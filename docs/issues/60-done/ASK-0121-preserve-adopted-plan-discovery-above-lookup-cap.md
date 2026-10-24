---
schema: "implement-rfc.card.v1"
id: "ASK-0121"
title: "Preserve adopted plan discovery above the live lookup cap"
status: "Done"
rfcs: ["RFC-ASK-0012"]
depends_on: []
metadata: {"discovered_by":"Grapho headless-text-foundation integration", "baseline":"73676198110acaaa788a8895dcc574aac4c0b10b"}
acceptance: [{"criterion":"bounded-adopted-discovery","outcome":"pass","revision":"1fbe6652a06b87b6ecfc52fb1e2a4227db9d4cb3","evidence":{"kind":"command","detail":"Reproduced the 257-plan refusal before correction; all 12 plan tests pass after correction, including two symlinked consumer contexts, unlinked-bound refusal and stale linkage. Two primary-checkpoint, one public-composition and 11 continuation tests also pass (26 total)."}},{"criterion":"portable-source-and-scope","outcome":"pass","revision":"1fbe6652a06b87b6ecfc52fb1e2a4227db9d4cb3","evidence":{"kind":"command","detail":"Regenerated portable digest from canonical inputs. Portable source and documentation gates pass; only helper/tests/generated digest changed, and the unrelated lock edit is preserved."}},{"criterion":"selected-consumer-deployment","outcome":"pass","revision":"1fbe6652a06b87b6ecfc52fb1e2a4227db9d4cb3","evidence":{"kind":"observation","detail":"Applied a reviewed MASK dev-link for only the authorized consumer binding. The actual target-only milestone checkpoint now succeeds in its 300-plan repository. No store edit, publication, unrelated binding upgrade or native-role replacement. Existing recipe changes were reconciled in a new same-route segment; broad native-role readiness/host loading remain unclaimed."}}]
---

# Preserve adopted plan discovery above the live lookup cap

## Scope and acceptance

Repair target-only discovery in `skills/implement-rfc/scripts/milestone_plan.py` when a fully adopted live linkage exists in a consumer with more than 256 plans. Preserve the bounded refusal for unlinked recovery and the stale/ambiguous linkage checks. Own only that helper, its focused tests and this follow-up bookkeeping; original RFC-ASK-0012 native qualification and closeout remain pending.

Reproduce the 257-plan failure, verify linked consumers resolve their adopted plan without increasing the unlinked scan bound, and verify interrupted/stale linkage remains refused. Run focused milestone-plan/checkpoint/public composition tests plus portable source and documentation gates. Deploy only the explicitly authorized AITO binding through MASK; do not publish or edit an immutable store payload.

## Execution record

Mandate: resume Grapho first-milestone integration only. This bounded repair supplies its missing supported checkpoint path. Original RFC_BASE_SHA and acceptance history remain on [ASK-0066](../10-backlog/ASK-0066-close-milestone-handling.md).
