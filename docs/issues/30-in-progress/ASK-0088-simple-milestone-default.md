---
schema: "implement-rfc.card.v1"
id: "ASK-0088"
title: "Default to one fresh Astra Max implementer per milestone"
status: "In Progress"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0085"]
---

# ASK-0088: Simple milestone default

Owner-directed follow-up to [RFC-ASK-0014](../../rfcs/RFC-ASK-0014-selectable-execution-strategies.md).
This is a workflow preference, not a finding that the M4 experiment established a
universal strategy winner.

## Outcome and acceptance

- **AC1:** Unspecified new runs select a lightweight coordinator and one fresh
  Astra Max implementer at every accepted milestone boundary. Explicit and preserved
  strategies retain precedence. No worker, scout, utility, tester or reviewer is
  automatically dispatched.
- **AC2:** The implementer owns planning, implementation, verification, self-review,
  authorized integration/commits, tracker and documentation upkeep, and cleanup.
  Corrections stay with the current milestone owner; the next milestone always
  starts with a fresh context after safe handoff.
- **AC3:** Public selection, host settings and MASK readiness work in separate
  disposable consumers. Activate the default through supported local deployment
  for personal scope and the named AgentSkills, MASK and aito source checkouts;
  preserve the frozen FWB-0231 candidates and study evidence.

## Authority

Edit canonical skill source and focused tests directly, without subagents. Preserve
existing acceptance and publication boundaries. No push, external publication,
permission changes or migration of other consumers. Live role loading is reported
separately from filesystem and fixture checks.
