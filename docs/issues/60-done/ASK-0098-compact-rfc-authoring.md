---
schema: "implement-rfc.card.v1"
id: "ASK-0098"
title: "Default to compact RFC authoring"
status: "Done"
rfcs: ["RFC-ASK-0015"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"rfc-authoring-skills","path":"docs/rfcs/plans/rfc-authoring-skills/milestone-plan.json"}}
acceptance: [{"criterion":"AC06","outcome":"pass","revision":"d1ef57c8b6817b0f6340f01ecafd7cea1b380239","evidence":{"kind":"artifact","detail":"Independent compact authoring and changed-answer/handoff resumes preserve actual decisions, uncertainty, numeric draft IDs and unique criteria without unsolicited pack/report artifacts or blanket confirmation. Failed initial observations and repairs are retained.","path":"docs/development/compact-rfc-authoring-evidence.json"}},{"criterion":"AC07","outcome":"pass","revision":"d1ef57c8b6817b0f6340f01ecafd7cea1b380239","evidence":{"kind":"artifact","detail":"Requested partial pack preserves exact constraints and typed future work; revised generated pack completes six public discovery/adoption/binding commands in two linked consumers. Final packages and portable source pass; historical handoff negatives remain verified.","path":"docs/development/compact-rfc-authoring-evidence.json"}}]
---

# Default to compact RFC authoring

Implement RFC-ASK-0015's owner-authorized compact-authoring amendment, AC06–AC07.
Own author-rfc, relevant grill-rfc guidance, clean implement-rfc companion pointers,
and this follow-up's design, board and evidence records. Preserve existing unrelated
changes and historical acceptance. No MASK implementation, publication or deployment.

The owner selected this existing agent for direct implementation. Baseline:
`5a6c64d167b65b7ff52b9b2e347ba2412baa6c03`. Resolve direct strategy and retain its
checkpoint beside temporary verification receipts. The parent supplies independent
small-request, changed-answer and explicit-pack observations; the implementation
session stays non-delegating. Reuse the portable handoff test and focused source checks.
