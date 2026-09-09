---
schema: "implement-rfc.card.v1"
id: "ASK-0053"
title: "Make milestone handoff, native waiting and interruption safe"
status: "Ready"
rfcs: ["RFC-ASK-0010"]
depends_on: ["ASK-0051", "ASK-0052"]
metadata: {"packet": "agent-skills-interactive-coordinator-2026-09-08", "provisional_id": false, "packet_key": "handoff-wait-and-recovery", "milestone": "M1"}
---

# ASK-0053: Make milestone handoff, native waiting and interruption safe

Governing RFC: [RFC-ASK-0010](../../rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md).

## Objective and owned paths

Implement the compact logical dispatch/return contract with exact identity, mandate revision, candidate/evidence pointers, quiescence and next action. Use current native wait/resume/cancel tools; ordinary timeout waits again on the same child. Add duplicate/stale/partial/cancelled/unknown-writer cases and genuine recovery without replaying mutation. Keep user amendments separate from summaries. If native grandchildren are unavailable, preserve integrator-local work and the narrowly specified native review relay; do not build a sibling worker broker. Reconcile local handoff versus optional push and main/lane authority. A helper, if useful, validates data only and never drives models or maintains a second board.

Owned paths:

- `skills/implement-rfc/references/coordination-handoff.md`
- `skills/implement-rfc/references/runtime-compatibility.md`
- `skills/implement-rfc/references/pack-lifecycle.md`
- `skills/implement-rfc/references/bookkeeping.md authority/pointer corrections only`
- `small return-validation/formatting helper and focused tests only if needed`
- `skills/implement-rfc/SKILL.md and integrator entrypoint coordinated changes`

## Acceptance

- A completed milestone yields a fresh successor only after current writers/commands and effects are accounted for.
- Current-problem partial returns resume the current integrator; no new approval is required merely to continue.
- Duplicate/late results cannot undo user amendments, revive cancelled work or start duplicate writers.
- Native result availability, execution completion and semantic acceptance remain distinct; repeated no-progress partials do not loop indefinitely.
- Unknown effects and unavailable required capabilities stay explicit, with no external supervisor fallback.

Criterion coverage: RFC-ASK-0010-AC01, RFC-ASK-0010-AC03, RFC-ASK-0010-AC05, RFC-ASK-0010-AC06, RFC-ASK-0010-AC08.

## Focused verification

- Adversarial coordination fixture set, including delivery/completion order, duplicate events, stale mandate, active descendants, unknown exit and cancellation.
- No-grandchildren review relay fixture where the integrator retains adjudication; negative courtesy-resume and wrong-producer cases.
- Only changed native mechanics are qualified in the following two cards.

## Run record

Not started. No native run, source implementation, reservation, accepted work or
measured saving is claimed by this packet. Claim the live card before source work,
preserve unrelated changes and commit only explicit owned paths.
