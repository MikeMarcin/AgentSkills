# Review hub proposal

An unadopted portable pack for collecting served attended-review sessions across
projects, harnesses and machines into one tailnet-only page on the owner's NAS,
with optional Android push. Three outcomes, in order: session publication, hub
service, hub push. The publisher belongs in AgentSkills; the hub belongs in a new
standalone repository selected by the owner during review.

- [RFC-DRAFT-0001: session publication](rfcs/RFC-DRAFT-0001-review-hub-session-publication.md)
- [RFC-DRAFT-0002: hub service](rfcs/RFC-DRAFT-0002-review-hub-service.md)
- [Design record](DECISIONS.md), including checks, readiness and confirmation
- [Proposed cards](issues/)
- [Canonical cross-repository plan](milestone-plan.json) and [generated view](MILESTONES.md)
- Consumer adoption plans: [AgentSkills publisher](plans/publisher/milestone-plan.json)
  and [standalone service](plans/service/milestone-plan.json)
- [Implementation entrypoint](IMPLEMENTATION_PROMPT.md)
- [Plan schema](milestone-plan.schema.json), copied from the implement-rfc kit

The consumer plans retain the canonical outcomes and criterion coverage. The
workflow binds one repository at a time: use those plans for import and preserve
the publisher prerequisite as an external service-card dependency. The umbrella
plan is not directly adoptable into either repository.

Review findings, current readiness and outstanding choices are recorded in the
[design record](DECISIONS.md). The supplied revision is preserved unchanged at
[review-hub-draft-v1](../../assets/review-hub-draft-v1/README.md).
