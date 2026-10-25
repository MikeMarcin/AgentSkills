---
schema: "implement-rfc.card.v1"
id: "ASK-0128"
title: "Compact station message passing"
status: "In Progress"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124"]
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
---

# Compact station message passing

Milestone M4 `compact-station-messaging` of RFC-ASK-0017, added by the owner
amendment of 2026-10-24: "the remote-station message format is token inefficient,
with boilerplate re-sent on every turn."

Boundary: `skills/remote-station` plus the implement-rfc dispatch rules that build
station prompts. No push, publication or credential change.

Acceptance: RFC-ASK-0017 AC09, AC10 and AC11.

1. **Measure first (AC09).** Measure per-turn tokens on recorded `aito-main-win`
   turns: the Codex thread history and the Claude session transcript. Record the
   method and keep the measurement as evidence before any design. After the change,
   measure the same turns again with the same method.
2. **Design from the measurement.** Change only what the measurement attributes
   cost to.
3. **Keep every refusal (AC10).** Replayed or reused `task_id`, project mismatch,
   authority exceeded and expired must still refuse for v1 and v2 envelopes.
4. **Keep compatibility (AC11).** v1 envelopes from existing dispatchers are still
   admitted during the compatibility release. Station identity rules do not change.

Hypotheses, unmeasured: the RFC's "Owner amendment 2026-10-24" section lists the
suspected causes and a likely shape. Neither is binding; the measurement decides.
