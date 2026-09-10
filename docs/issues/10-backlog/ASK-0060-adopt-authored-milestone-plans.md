---
schema: "implement-rfc.card.v1"
id: "ASK-0060"
title: "Adopt authored milestone plans through consumer intake"
status: "Backlog"
rfcs: ["RFC-ASK-0012"]
depends_on: []
metadata: {"packet": "agent-skills-milestone-handling", "provisional_id": false, "criterion_coverage": ["RFC-ASK-0012-AC01", "RFC-ASK-0012-AC02", "RFC-ASK-0012-AC03"], "milestone_plan": {"id": "agent-skills-milestone-handling", "path": "docs/rfcs/plans/agent-skills-milestone-handling/milestone-plan.json"}}
---

# ASK-0060: Adopt authored milestone plans through consumer intake

Governing RFC: [RFC-ASK-0012](../../rfcs/RFC-ASK-0012-authored-milestone-plans-and-continuation.md).

## Objective and owned paths

Import this pack and its actual milestone grouping, establish the real baseline, then implement the first plan-reading/adoption path. This is engineering work with intake included, not a standalone import milestone.

Owned surfaces (reconcile actual names at intake): skills/implement-rfc/schemas/milestone-plan.schema.json; scripts/milestone_plan.py (new or current equivalent); plan-related board/project resolver integration; focused discovery/adoption tests; this RFC/cards/import record.

## Bounded work

Implement structural plan validation, deterministic discovery, source-versus-live distinction, stable typed ID remapping, scoped linkage and compact human/JSON output. Preserve authored groups and avoid executing attached scripts. Start with the supplied plan through a disposable linked consumer; do not build a second scheduler. Coordinate shared helper/schema ownership with ASK-0061.

## Acceptance

- The packet is imported with real noncolliding IDs and baseline; its two authored groups survive typed remapping and live linkage. Intake remains inside the first engineering milestone.
- The public plan helper reads and checks the proposed schema from a disposable linked consumer, resolves authored sources, and distinguishes invalid/ambiguous/absent input without executing package code.
- Adoption is idempotent for unchanged intent, preserves collisions and unrelated consumer bytes, and makes the live plan discoverable after issue lane moves. Schema data supports partial references; adaptive execution follows in ASK-0063.

Contributes to: RFC-ASK-0012-AC01, RFC-ASK-0012-AC02, RFC-ASK-0012-AC03. These are card-scope acceptance checks; full RFC criteria are established by the combined milestone/closeout evidence, not repeated as prerequisite work on every contributing card.

## Verification and execution record

Use the direct tests named by the governing RFC and the retained pack's VERIFICATION.md. The live milestone plan, not this card's completion, defines the integration boundary. Preserve dependency-ready claims, explicit path commits, existing routing and required acceptance. No worker may acquire board/commit authority.

Not started. No implementation result, native qualification, source revision or quota saving is asserted by this packet.
