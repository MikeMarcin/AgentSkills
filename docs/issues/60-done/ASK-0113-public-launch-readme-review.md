---
schema: "implement-rfc.card.v1"
id: "ASK-0113"
title: "Review the README for public launch"
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"12e4e17ce3a9eee7d0758d56fe1db4bb2d282f5f","evidence":{"kind":"observation","detail":"Reviewed README against fetched-tap validation and mask-workflow profiles; corrected unnecessary source clone, missing committed lockfile, default role requirement and fetched-versus-uncommitted validation guidance."}},{"criterion":"AC2","outcome":"pass","revision":"12e4e17ce3a9eee7d0758d56fe1db4bb2d282f5f","evidence":{"kind":"observation","detail":"Documentation: 15 RFCs / 113 cards / zero structural violations; portable source valid. Both README link sets: 59 targets and anchors, zero failures. Canonical public CLI/setup scenarios and selected package installation through both adapters/two consumers pass. git diff --check passes."}}]
---

The owner requested a final README review followed by making AgentSkills and
ManageAgentSkills public. Correct onboarding and authoring guidance without
changing skills, consumer selections or outstanding native acceptance.

- AC1: The README accurately describes tap-based installation, committed lockfiles,
  strategy-dependent native roles and validation of fetched package content.
- AC2: Documentation, local README links and focused public CLI checks pass.

Publication and post-switch Source checks are authorized owner operations after
the review. The unrelated consumer lockfile edit stays outside these commits.
