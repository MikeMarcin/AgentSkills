---
schema: "implement-rfc.card.v1"
id: "ASK-0045"
title: "Qualify routing and prepare scoped consumer adoption"
status: "Done"
rfcs: ["RFC-ASK-0009"]
depends_on: ["ASK-0044"]
metadata: {"packet":"agent-skills-standard-worker-review", "provisional_id":true}
acceptance: [{"criterion":"RFC-ASK-0009-AC01–AC06 qualification","outcome":"pass","revision":"fbe7c80f8059e61f4e2cf619c75e85e600ed564a plus supplied working paths","evidence":{"kind":"command","detail":"69 integration-focused renderer/target/usage capture/scope/CLI tests passed; 9 migration and 9 slice integration tests passed; portable source valid; immutable packet validator: 0 violations. Primary reviewed all 13 selection cases and full changed migration/routing diff. MASK capabilities/config/source status/project show were observational and establish development links, no selected pin, ahead/dirty canonical source. role-adoption.md documents scoped guarded adoption and clean rollback with native serving/quality/cost unclaimed."}}]
---

# ASK-0045: Qualify routing and prepare scoped consumer adoption

Governing RFC: [RFC-ASK-0009](../../rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md).

Criterion coverage: RFC-ASK-0009-AC01, RFC-ASK-0009-AC02, RFC-ASK-0009-AC03, RFC-ASK-0009-AC04, RFC-ASK-0009-AC05, RFC-ASK-0009-AC06.

## Objective and owned paths

Own affected `skills/implement-rfc/tests/`, compact active routing/deployment guidance,
`generated/portable-manifest.json`, and source-backed corrections in the already owned
routing surface. No changes to MASK program internals or arbitrary consumer contexts.

## Work

Run the target checker; test native adapter rendering and companion argument forwarding
through fixtures for all roles. Separate normal-review and deep-worker overrides on both
providers. Fix the stale active lane-test Sol-high routine expectation rather than
editing historical examples. Verify retired dispatch failure before any model launch.

Inspect instructions against the policy cases, including sensitive-but-straightforward
implementation. Preserve review's existing adversarial acceptance contract and no-default
repeat-review rule. Refresh the portable source manifest from a canonical authoring
worktree after source/tests/docs agree. Run source validation and a second renderer check.

Prepare existing MASK public plan/selection/apply guidance for explicitly selected
consumers, including development links versus pins, active-session limitations, clean
owned adapter migration, and rollback. Use temporary linked consumer fixtures; no broad
registry deployment. Actual account/model requests remain separately budget-authorized.

## Acceptance and verification

RFC-ASK-0009-AC01–AC06. Focused suites: test_render_runtime_adapters, test_codex_lane,
test_role_usage, test_unified_workflow and any directly affected usage tests. Reuse
unchanged evidence; do not run the entire old optional-runtime matrix by habit.
Record unavailable native/serving checks as not exercised, not passes. No quality/cost
benchmark is required to adopt this owner-directed policy.

## Run record

Not started.
