---
schema: "implement-rfc.card.v1"
id: "ASK-0109"
title: "Finalize public-preview reporting and delivered-state documentation"
status: "Done"
rfcs: []
depends_on: []
metadata: {"mandate":"public-prep-final-reconciliation-v1","baseline":"8c9c80f05e02e0cbaca56edfde5dab8859f2f932","external_input":"ManageAgentSkills 4ba72a7235d8a94d0d8cb386a672a51e671702bc","milestone_plan":{"id":"public-source-finalization","path":"docs/rfcs/plans/public-source-finalization/milestone-plan.json"}}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"3359319ba3f43338ac8f8ed19070e5bb867600e5","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"SECURITY c444f55 prohibits live credential transfer through any channel and requests sanitized private reproduction details."}},{"criterion":"AC2","outcome":"pass","revision":"3359319ba3f43338ac8f8ed19070e5bb867600e5","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"Public-preview delivered state, pending owner/license/native boundaries and both manual post-public Source checks dispatches reviewed against unchanged workflow triggers."}},{"criterion":"AC3","outcome":"pass","revision":"3359319ba3f43338ac8f8ed19070e5bb867600e5","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"Documentation/source/link gates pass; examples2/2; Gitleaks history/exported-tree/new-metadata zero at3359319 and companion7a97e94. Unchanged broad evidence and CI repair limits retained in the public evidence record."}},{"criterion":"AC4","outcome":"pass","revision":"3359319ba3f43338ac8f8ed19070e5bb867600e5","evidence":{"kind":"artifact","path":"docs/development/public-source-finalization.md","detail":"Input ancestry and unrelated lock SHA-256 retained; source/evidence committed explicit paths, latest origin reconciled, ordinary push completed and ls-remote confirms3359319/7a97e94. All verification commands complete; final bookkeeping/push/handoff remain the M3 owner obligation before release."}}]
---

# Final public-preparation reconciliation

M3 owns this bounded follow-up under the owner's cleanup, reconciliation and
ordinary push authorization. ASK-0108 and MASK-0140 retain the unanswered owner
license choice. Their pending acceptance and the native RFC boundaries are not
prerequisites for this independent reporting correction and are not closed here.

## Acceptance

- AC1: SECURITY prohibits sending live credentials through any channel and asks
  for sanitized reproduction details through an established private channel.
- AC2: Public-preview documentation describes the delivered technical preparation,
  pending license/native boundaries and separate owner visibility action. After
  both repositories become public, the owner manually dispatches both Source checks
  workflows; local composition, private CI and post-switch public CI stay distinct.
- AC3: Focused documentation/link/policy checks and exact-candidate scans pass.
  Relevant unchanged broad-suite and companion evidence is reused with its actual
  failures, corrections, skips and privacy limits stated.
- AC4: Exact-path commits, final fetch/reconciliation and ordinary push are complete;
  input ancestry, preserved unrelated lock bytes, command state and remaining owner
  decisions are bound in a durable handoff. No visibility/access, license adoption,
  history rewrite, real deployment or model experiment is inferred.

## Scope and continuation

Plan: public-source-finalization, milestone m3. Preserve both accepted input commits,
the pre-existing consumer lock edit and the separately protected license candidate.
M3 may correct a newly observed final CI failure before writer release. The
coordinator observes final CI; public companion CI remains a switch-time owner step.
