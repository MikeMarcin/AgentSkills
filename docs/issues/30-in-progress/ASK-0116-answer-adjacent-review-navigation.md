---
schema: "implement-rfc.card.v1"
id: "ASK-0116"
title: "Navigate and hand back beside review answers"
status: "In Progress"
rfcs: []
depends_on: ["ASK-0114", "ASK-0115"]
priority: "P1"
metadata: {"milestone_plan":{"id":"attended-review-navigation","path":"docs/rfcs/plans/attended-review-navigation/milestone-plan.json"},"related_rfc":"RFC-ASK-0016"}
---

# Navigate and hand back beside review answers

Owner mandate, 2026-10-19: "aside: I would like to be able to navigate to the next
question and hand back without having to scroll all the way to the top and search
the side bar". Mandate revision: `review-navigation-source-v1`.

Assignment `/root/review_navigation`: one non-delegating implementer on AgentSkills
main. Source-only follow-up; no deployment, consumer migration, Faraday live-state
change or push. Baseline: d19d11a84d841ec1aecf8c44d52cd27bc740e777. Own only
`skills/attended-review/assets/review.html`, its focused page tests, and this
bounded follow-up's tracker/plan/evidence. Original completed audio RFC, plan and
acceptance remain historical and unchanged.

Related completed design: [RFC-ASK-0016](../../rfcs/RFC-ASK-0016-attended-review-audio-questions.md).
This independent follow-up adds no unfinished obligation to its historical closeout.

Acceptance:

- **NAV01:** Next question is available beside the answer controls after answering
  and while leaving a question pending. It moves to a different ready unanswered
  question in queue order, with clear disabled/end-of-queue behavior and no inferred
  verdict. On wide and narrow screens the next question's beginning is in view and
  keyboard focus follows it.
- **NAV02:** Finish and hand back is available beside the same controls and shares
  the masthead's handler, draft flush, playback stop and error behavior. Failed
  saves retain recoverable feedback and prevent a false successful handback.
- **NAV03:** Focused real-page behavior checks preserve audio comparison and shared
  feedback; source and board records are coherent, explicit-path commits are local,
  and task-owned commands are quiescent at handoff.
