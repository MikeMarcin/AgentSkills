---
schema: "implement-rfc.card.v1"
id: "ASK-0061"
title: "Bind assignments and returns to milestone obligations"
status: "Done"
rfcs: ["RFC-ASK-0012"]
depends_on: ["ASK-0060"]
metadata: {"packet": "agent-skills-milestone-handling", "provisional_id": false, "criterion_coverage": ["RFC-ASK-0012-AC04", "RFC-ASK-0012-AC05", "RFC-ASK-0012-AC08"], "milestone_plan": {"id": "agent-skills-milestone-handling", "path": "docs/rfcs/plans/agent-skills-milestone-handling/milestone-plan.json"}}
acceptance: [{"criterion":"Bound assignment and obligation completion","outcome":"pass","revision":"f3d92842302e94e68d3151de3aa854eaaf27abdf","evidence":{"kind":"observation","detail":"Public two-consumer raw fixture binds all three first-group cards and exits; reduced obligation and target lists, intermediate-card complete and missing exits refuse. Current source arrays and fingerprints are reconciled."}},{"criterion":"Explicit continuation and recovery","outcome":"pass","revision":"f3d92842302e94e68d3151de3aa854eaaf27abdf","evidence":{"kind":"command","detail":"10 continuation tests cover separate continue/fresh/wait/stop, related reuse, same-producer renewed dispatch and mid-milestone recovery. Public composed test validates boundary selection and affected vs future-only amendment."}},{"criterion":"Safeguards and historical compatibility","outcome":"pass","revision":"f3d92842302e94e68d3151de3aa854eaaf27abdf","evidence":{"kind":"observation","detail":"12 historical handoff tests and 3 schema tests pass; stale/duplicate/native execution/cancellation/review relay preserved. Independent rfc-reviewer-critical corrected-counterexample recheck reports no blocking findings; 9 plan tests include interrupted publication recovery. Native qualification and full first milestone instruction criterion remain pending."}}]
---

# ASK-0061: Bind assignments and returns to milestone obligations

Governing RFC: [RFC-ASK-0012](../../rfcs/RFC-ASK-0012-authored-milestone-plans-and-continuation.md).

## Objective and owned paths

Make an intermediate card completion stay within the assigned milestone, and make actual replacement a separate checked decision.

Owned surfaces (reconcile actual names at intake): skills/implement-rfc/scripts/coordinator_handoff.py; schemas/milestone-return.schema.json and any versioned successor; relevant milestone helper seams; test_coordinator_handoff.py and public continuation tests.

## Bounded work

Version the assignment/return extension against live history. Bind plan and obligation identity, preserve same-native-ID resumes with new dispatch IDs, and validate completion against all assigned obligations and current evidence references. Preserve cancellation, duplicate/stale handling, no-grandchildren review relay and safe writer recovery. V1 historical records remain readable; missing plan identity in an active legacy run requires scoped reconciliation, not automatic redispatch.

## Acceptance

- The versioned assignment/return helper binds plan, selected milestone, resolved obligations and exact producer/dispatch/mandate identity. An intermediate-card completion cannot satisfy outstanding assigned obligations.
- Continuation explicitly distinguishes continue/fresh/wait/stop from work disposition. Focused deterministic tests cover a justified new boundary, related reuse and mid-milestone recovery without marking unfinished work complete.
- Existing active-writer, stale/duplicate, cancellation and review-relay safeguards survive; supported same-producer resumes renew dispatch authority. Historical v1 handling cannot bypass new-plan binding.

Contributes to: RFC-ASK-0012-AC04, RFC-ASK-0012-AC05, RFC-ASK-0012-AC08. These are card-scope acceptance checks; full RFC criteria are established by the combined milestone/closeout evidence, not repeated as prerequisite work on every contributing card.

## Verification and execution record

Use the direct tests named by the governing RFC and the retained pack's VERIFICATION.md. The live milestone plan, not this card's completion, defines the integration boundary. Preserve dependency-ready claims, explicit path commits, existing routing and required acceptance. No worker may acquire board/commit authority.

Not started. No implementation result, native qualification, source revision or quota saving is asserted by this packet.
