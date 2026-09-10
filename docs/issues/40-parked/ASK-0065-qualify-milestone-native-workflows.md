---
schema: "implement-rfc.card.v1"
id: "ASK-0065"
title: "Qualify raw-input milestones on both native drivers"
status: "Parked"
rfcs: ["RFC-ASK-0012"]
depends_on: ["ASK-0064"]
metadata: {"packet": "agent-skills-milestone-handling", "provisional_id": false, "criterion_coverage": ["RFC-ASK-0012-AC10", "RFC-ASK-0012-AC11", "RFC-ASK-0012-AC12"], "milestone_plan": {"id": "agent-skills-milestone-handling", "path": "docs/rfcs/plans/agent-skills-milestone-handling/milestone-plan.json"}}
parked_on: "human-review"
acceptance: [{"criterion":"raw-public-regressions","outcome":"pass","revision":"4938be2a68b3f74bedb0129a197cf352496218b9","evidence":{"kind":"command","detail":"38 milestone/schema tests pass through two linked consumers; original authored course plus adaptive/refusal/recovery paths."}},{"criterion":"actual-claude-and-codex-courses","outcome":"pending","revision":"4938be2a68b3f74bedb0129a197cf352496218b9","evidence":{"kind":"observation","detail":"Neither native course was run. Coordinator confirms no approved capacity/time ceiling or native driver/operator instruction in the mandate. Prepared decision page /tmp/agent-skills-m2-adoption.rqZw9U/native-course-review.html; source/adoption artifacts retained."}},{"criterion":"native-identities-and-boundaries","outcome":"pending","revision":"4938be2a68b3f74bedb0129a197cf352496218b9","evidence":{"kind":"observation","detail":"Neither native course was run. Coordinator confirms no approved capacity/time ceiling or native driver/operator instruction in the mandate. Prepared decision page /tmp/agent-skills-m2-adoption.rqZw9U/native-course-review.html; source/adoption artifacts retained."}},{"criterion":"approved-capacity-and-native-driver","outcome":"pending","revision":"4938be2a68b3f74bedb0129a197cf352496218b9","evidence":{"kind":"observation","detail":"Neither native course was run. Coordinator confirms no approved capacity/time ceiling or native driver/operator instruction in the mandate. Prepared decision page /tmp/agent-skills-m2-adoption.rqZw9U/native-course-review.html; source/adoption artifacts retained."}}]
---

# ASK-0065: Qualify raw-input milestones on both native drivers

Governing RFC: [RFC-ASK-0012](../../rfcs/RFC-ASK-0012-authored-milestone-plans-and-continuation.md).

## Objective and owned paths

Prove actual agents discover and preserve grouping from raw inputs rather than merely accepting a prepared handoff fixture.

Owned surfaces (reconcile actual names at intake): skills/implement-rfc/tests/ focused regressions and instruction tests; disposable qualification consumers; selected AgentSkills adapter/source qualification records; compact evidence on this card.

## Bounded work

Complete offline/refusal tests first. Verify the exact candidate instructions/roles used by fixtures. Within the owner-approved existing capacity ceiling run the two short courses in NATIVE_QUALIFICATION.md, one per supported interactive driver, with no external supervisor/API substitution. Keep actual failures and missing capability visible. Reuse the active engineer for corrections; no unconditional retries or per-case agent matrix.

## Acceptance

- The full raw-input/public-loop regression course passes through two linked disposable consumers, including misleading per-card headings, renumbering/resume, dependency chains and refusal/recovery cases.
- Within the approved capacity ceiling, one compact actual Claude interactive course and one actual Codex interactive course observe authored multi-card grouping, a justified integration transition, safe resume behavior and a planless follow-up.
- Exact candidate/role/route/native identities, outcomes and limitations are recorded. Failed native behavior or unavailable mandatory capacity stays pending; schemas, mock events and banners do not substitute for native proof.
- Qualification uses existing configured routes and task-owned fixtures, no paid per-scenario matrix, unapproved billing fallback, unrelated product mutation or fabricated economics.

Contributes to: RFC-ASK-0012-AC10, RFC-ASK-0012-AC11, RFC-ASK-0012-AC12. These are card-scope acceptance checks; full RFC criteria are established by the combined milestone/closeout evidence, not repeated as prerequisite work on every contributing card.

## Verification and execution record

Use the direct tests named by the governing RFC and the retained pack's VERIFICATION.md. The live milestone plan, not this card's completion, defines the integration boundary. Preserve dependency-ready claims, explicit path commits, existing routing and required acceptance. No worker may acquire board/commit authority.

Not started. No implementation result, native qualification, source revision or quota saving is asserted by this packet.
