# Implement this pack

Read the [design record](DECISIONS.md) for settled decisions
before selecting scope. Implement only the authorized scope,
preserving the three outcomes in the [canonical plan](milestone-plan.json).
The [milestone view](MILESTONES.md) is generated.

This pack spans two consumers. The current workflow resolves live RFCs/cards from
one consumer, so do not adopt the umbrella plan or import all cards into AgentSkills.

1. In AgentSkills, import RFC-DRAFT-0001 and DRAFT-0001/DRAFT-0004 using the
   [publisher plan](plans/publisher/milestone-plan.json). Reconcile provisional IDs,
   capture the actual baseline and retain the import mapping. Implement and verify
   session-publication, then record its integrated contract revision for handoff.
2. In the new standalone service repository selected in D4, read/configure that
   consumer's workflow, import RFC-DRAFT-0002 and DRAFT-0002/DRAFT-0003/DRAFT-0005,
   and adopt the [service plan](plans/service/milestone-plan.json). Reconcile the
   external AgentSkills dependency with the first import's mapping and completion
   evidence. Preserve milestone IDs/outcomes/exits. Its first local milestone has
   no local predecessor because session-publication is enforced by that external
   prerequisite. Retain both mappings with the pack provenance.
3. Verify the defined milestones and record actual evidence. NAS access changes,
   deployment, phone setup and consumer upgrades require their corresponding task
   scope. Where required deployment/device observations are unavailable, keep the
   affected acceptance open and report the exact remaining step.

The standalone repository's name/path can be selected during authorized setup;
this review creates no repository or deployment. Keep the shared wire contract
authoritative in the publisher RFC and preserve its source revision in the service
handoff. Resolve relative links when importing to each destination.

Read each consumer's applicable instructions and live requirements. Import,
validation and intermediate card completion remain within the assigned outcome;
they do not independently require a new engineering context or grant publication
authority. Report unresolved prerequisites and acceptance.
