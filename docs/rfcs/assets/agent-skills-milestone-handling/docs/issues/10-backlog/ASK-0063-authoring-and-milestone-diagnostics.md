---
schema: "implement-rfc.card.v1"
id: "ASK-0063"
title: "Publish offline authoring guidance and compact milestone diagnostics"
status: "Backlog"
rfcs: ["RFC-ASK-0011"]
depends_on: ["ASK-0062"]
metadata: {"packet": "agent-skills-milestone-handling", "provisional_id": true, "criterion_coverage": ["RFC-ASK-0011-AC02", "RFC-ASK-0011-AC09", "RFC-ASK-0011-AC12"]}
---

# ASK-0063: Publish offline authoring guidance and compact milestone diagnostics

Governing RFC: [RFC-ASK-0011](../../rfcs/RFC-ASK-0011-authored-milestone-plans-and-continuation.md).

## Objective and owned paths

Make the intended plan shape easy to author outside the repository and make the active plan/generation boundary visible without transcript inspection.

Owned surfaces (reconcile actual names at intake): skills/implement-rfc/references/milestone-plans.md or integrated authoritative reference; examples/milestone-plans/; skill/repository README and source-dump inclusion; scripts/role_usage.py or existing usage linkage only as needed; focused rendering/report tests.

## Bounded work

Publish a small copyable plan/template and schema, a generated MILESTONES.md rendering, legacy normalization guidance and missing-plan fallback. Link the authoring kit from normal pack creation guidance and source exports. Reuse existing assignment records/usage helpers for plan ID, milestone ID, generation and replacement reason; unknown history stays unknown. No daemon, new planner role, extra polling, numeric quota promise or mandatory diagnostic gate.

## Acceptance

- New-pack authoring guidance, a consumer-independent minimal template and an implementation-entrypoint pointer make the structured plan the default. Generated MILESTONES.md is checked from the canonical data, not hand maintained.
- Normal source exports/manifests include the new schema, examples and current plan linkage without leaking local session logs. An offline author can write a valid plan without the repository scripting stack.
- Existing execution/usage reporting exposes plan/milestone and concrete generation reasons from actual records; missing historical reasons remain unknown. Response counts or generation counts never become quota-savings claims.
- Common-path instructions remain compact and role-specific. Focused render/example and diagnostic regression checks pass; no new scheduler, planner role, compulsory capture or generation budget is introduced.

Contributes to: RFC-ASK-0011-AC02, RFC-ASK-0011-AC09, RFC-ASK-0011-AC12. These are card-scope acceptance checks; full RFC criteria are established by the combined milestone/closeout evidence, not repeated as prerequisite work on every contributing card.

## Verification and execution record

Use the direct tests named by the governing RFC and the retained pack's VERIFICATION.md. The live milestone plan, not this card's completion, defines the integration boundary. Preserve dependency-ready claims, explicit path commits, existing routing and required acceptance. No worker may acquire board/commit authority.

Not started. No implementation result, native qualification, source revision or quota saving is asserted by this packet.
