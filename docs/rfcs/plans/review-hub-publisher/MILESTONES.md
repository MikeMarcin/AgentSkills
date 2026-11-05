# Milestones

> Generated from `milestone-plan.json`; edit the JSON, not this view.

Plan: **review-hub-publisher** · Coverage: **complete**

These are integration outcomes, not compulsory agent-launch boundaries.

## session-publication

Attended-review sessions can publish private, ordered summaries to a configured hub while preserving local review behavior when delivery is unavailable.

**Work:** `RFC-ASK-0018` [AC01, AC02, AC03, AC04, AC05, AC06, AC07]

**Prerequisites:** None

**Completion:**

- The publisher meets the record, configuration, lifecycle and failure-isolation contract against disposable fixtures; the integrated contract revision is ready for the standalone service handoff.

**Boundary:** A verified optional AgentSkills publisher and versioned record contract, usable before a real hub exists; no publication or consumer upgrade is implied.

## machine-hub-default

Every attended-review session on a configured machine publishes to the owner's hub without per-session flags, from any harness or shell, while explicit session choices keep precedence.

**Work:** `ASK-0131`

**Prerequisites:** session-publication

**Completion:**

- RFC-ASK-0018 AC08 passes against disposable config paths and fixture hubs; AC01-AC07 still pass, and a missing machine file keeps the never-enabled invariants.

**Boundary:** Owner amendment 2026-11-04: per-user machine default file and a hub-config helper; no real user config, consumer upgrade, push or hub deployment.
