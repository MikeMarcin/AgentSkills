---
schema: "implement-rfc.card.v1"
id: "ASK-0079"
title: "Render personal native roles and integrate MASK readiness"
status: "Done"
rfcs: ["RFC-ASK-0013"]
depends_on: ["ASK-0076"]
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC09","RFC-ASK-0013-AC11"]}
acceptance: [{"criterion":"Canonical personal roles retain provider routes and use assignment-provided project facts without changing project role addenda","outcome":"pass","revision":"9b47f12861c33f1f02b3aa4aaa7d848e37c2b094","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0079.host.json"}},{"criterion":"Selected personal preflight verifies role files and source/tracker binding while keeping native host loading unverified","outcome":"pass","revision":"9b47f12861c33f1f02b3aa4aaa7d848e37c2b094","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0079.host.json"}},{"criterion":"Fresh-agent instruction tabletop reaches one shared milestone path for first use, resume, small fix, status-only and paired worktrees in both modes","outcome":"pass","revision":"9b47f12861c33f1f02b3aa4aaa7d848e37c2b094","evidence":{"kind":"artifact","detail":"docs/rfcs/plans/personal-implement-rfc/ASK-0079.host.json"}}]
---

# ASK-0079: Render personal native roles and integrate MASK readiness

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: canonical role rendering and personal-scope instructions; MASK-0098 program handoff. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- Personal roles use the canonical routing definitions and bound assignment facts, preserving project routes/addenda.
- Personal preflight distinguishes files from actual host loading and checks the source/tracker binding.
- Fresh-agent tabletop checks cover first use, resume, small fix, status-only and paired worktree behavior in both modes.

Contributes to: RFC-ASK-0013-AC09, RFC-ASK-0013-AC11. The mandate remains binding beyond this card summary.

## Verification and execution record

AgentSkills source `9b47f12861c33f1f02b3aa4aaa7d848e37c2b094` and MASK program `78cc57cdac4ea493a3e0ba38ca0e51218af7991a` passed the [personal host evidence](../../rfcs/plans/personal-implement-rfc/ASK-0079.host.json): a fresh disposable public user setup and bound preflight reported 16 role files ready with `host_load=not_verified` and a clean source checkout. The independent instruction tabletop covered five paths in both modes, and focused rendering/preflight tests passed. This card accepts offline role and instruction integration only; RFC-ASK-0013-AC09 still requires actual fresh Codex and Claude Code personal-role loading and a bounded native course under ASK-0081.
