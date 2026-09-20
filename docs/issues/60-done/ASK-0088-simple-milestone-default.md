---
schema: "implement-rfc.card.v1"
id: "ASK-0088"
title: "Default to one fresh Astra Max implementer per milestone"
status: "Done"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0085"]
acceptance: [{"criterion":"AC1: complete default selection, explicit/preserved precedence, no additional orchestration","outcome":"pass","revision":"5a40143","evidence":{"kind":"artifact","detail":"docs/development/simple-milestone-default.md: Resolver and scoped host tests pass; default selects Sol Low and a leaf Astra Max implementer without bespoke role requirements."}},{"criterion":"AC2: full-cycle milestone ownership and fresh boundary handoff","outcome":"pass","revision":"5a40143","evidence":{"kind":"artifact","detail":"docs/development/simple-milestone-default.md: Recipe inspected for complete planning/implementation/verification/upkeep ownership, same-milestone correction, fresh next-milestone context and existing independent acceptance boundaries. Native behavior is not claimed."}},{"criterion":"AC3: public installed surfaces and scoped local activation","outcome":"pass","revision":"5a40143","evidence":{"kind":"artifact","detail":"docs/development/simple-milestone-default.md: 26 AgentSkills and 32 MASK tests pass, including two disposable installed/development consumers. Guarded personal/AgentSkills/MASK/aito links activated. Personal, AgentSkills and aito readiness pass; MASK retains its pre-existing approval requirement. Frozen experiment candidates remain unchanged."}}]
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
