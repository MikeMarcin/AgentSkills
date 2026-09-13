---
schema: "implement-rfc.card.v1"
id: "ASK-0075"
title: "Bind personal mode and external tracker"
status: "In Progress"
rfcs: ["RFC-ASK-0013"]
depends_on: []
metadata: {"milestone_plan":{"id":"personal-implement-rfc","path":"docs/rfcs/plans/personal-implement-rfc/milestone-plan.json"},"criterion_coverage":["RFC-ASK-0013-AC01","RFC-ASK-0013-AC02"]}
---

# ASK-0075: Bind personal mode and external tracker

Governing RFC: [RFC-ASK-0013](../../rfcs/RFC-ASK-0013-personal-implement-rfc-storage.md).

## Objective and ownership

Owned surfaces: skills/implement-rfc/scripts/project_config.py; personal binding/setup public helper; focused context and footprint tests. Source ownership is assigned by the integrator before edits; workers have no board/commit authority.

## Acceptance

- Explicit selection creates or binds a managed/supplied tracker and records one source Git common repository identity locally.
- An observational public status command resolves the stored binding and explicit mode override without creating state.
- Project-mode context remains valid; overlap, unsafe path redirection, absent binding and independent clone guessing refuse; target checkout and Git metadata stay untouched.

Contributes to: RFC-ASK-0013-AC01, RFC-ASK-0013-AC02. The mandate remains binding beyond this card summary.

## Verification and execution record

Not started. No source or native acceptance asserted.
