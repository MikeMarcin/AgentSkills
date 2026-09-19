# Selectable execution strategies

Status: proposed implementation brief, revision 2. Grounded in the supplied September 18 AgentSkills dump and the user's corrected experiment scope. No live issue IDs or source changes are created here.

## 1. Separate the stable contract from execution strategy

The common contract states what authorized work must preserve and deliver: consumer/source/tracker identity; scope and amendments; applicable project instructions; immutable RFC_BASE_SHA; dependency eligibility; authored milestones and their exits; claim-before-edit; source/path ownership; relevant tests and evidence; permitted explicit-path commits; truthful issue/RFC status; required human/native/independent review; and recoverable continuation.

It is not a universal planning or orchestration algorithm. Except for genuine dependency/authority rules, it does not prescribe how many agents work, which model plans, how implementation is partitioned, or when native contexts reset. Preserve authored milestone grouping and acceptance, while allowing each strategy to choose internal decomposition. A supplied detailed solution is an experimental input, not free planning that can be omitted from the record.

Use one existing board/plan/evidence/closeout model. Remove agent-role assumptions only where needed to make its obligations available to every execution owner. A direct or native primary may hold engineering and bookkeeping authority within its authorized lane; no topology turns a lane into main or grants publication, allocation, credentials or cross-repository rights.

## 2. Three distinct concepts

**Topology** names responsibility and context structure: direct, native, coordinator-integrator, planner-worker, or a future registered recipe.

**Routing** binds exact provider/model/effort choices where the strategy controls them. Native child selection is explicitly system-owned, not fabricated custom roles. UI labels, requested fields, effective local configuration and observed serving are separate evidence.

**Strategy/preset** selects a versioned topology recipe plus routing, context/recovery policy and allowed fallback behavior. `direct-astra-max` is a useful preset; Astra Max is not built into the definition of direct execution.

An **experiment arm** freezes a strategy plus common task/baseline/environment and its budget for one attempt. Experiments select any explicit subset of registered strategies. More entries in the catalog must not increase the work done by an ordinary run.

## 3. A small registration seam, not another orchestration engine

Keep one public `implement-rfc` skill. Resolve the selected strategy before loading a topology procedure or checking its custom roles. A small catalog points to one selected recipe; other recipes stay out of runtime context.

A recipe identifies its ID/revision, common-contract compatibility, package-relative instruction entrypoint, supported/qualified host facts, required custom roles and capabilities, engineering/bookkeeping owner, delegation authority, and recovery/checkpoint policy. Routing remains independently supplied. The companion example is illustrative; reconcile actual schema versioning before implementation.

Adding a recipe should mean registering a descriptor, writing the recipe, supplying any scoped roles/routes, and passing common conformance cases. Do not hard-code a closed four-value topology enum in board/usage schemas. Unknown IDs refuse selection until registered; extensible does not mean accepting arbitrary unvalidated scripts. Load passive trusted package data, not downloaded executables or automatic plugin entrypoints.

Reuse ordinary native-session controls. Deterministic helpers may resolve selection, validate inputs, prepare a scoped configuration and collect evidence. They do not launch an external supervisory model, reinterpret user authorization or schedule engineering turns independently.

Natural-language selection is sufficient. Proposed preset names are UI conveniences, not shipped command syntax. Selection precedence is explicit invocation, then the current run's preserved selection, then any explicitly configured preference, then the backward-compatible coordinator-integrator default. Do not add a new preference database solely for this pilot. A run records its resolved recipe/routing snapshot beside existing continuation evidence.

Keep project/personal storage separate. The current `workflow_preflight.py --mode` selects storage; older execution-selection.v1 direct/runner language is a different axis. Do not repurpose either field. Scope future machine-readable selection explicitly, for example `strategy`/`topology_id`, after reconciling current schemas.

## 4. Required recipes

### Direct

The primary owns design, implementation, tests, self-review and permitted bookkeeping. Native model delegation tools are disabled through supported scoped host controls where available. Delegating through a shell, companion or other tool is still delegation. Ordinary deterministic tools and build/test subprocesses remain available.

For the initial preset request Astra Max, verified on the actual client. Native compaction is allowed and recorded; milestones do not force a new session. Recover a genuinely interrupted run using current records; distinguish recovery from an uninterrupted single-session result. Independent review, where required, is separate from this implementation session and remains pending until supplied.

### Native

The primary receives the common engineering/bookkeeping obligations and authorized task, with Astra Ultra selected for the initial preset. The native system chooses whether to delegate, task partitioning, child contexts and supported child routes. Do not prescribe a team, a mandatory scout/test/reviewer pipeline, integrator turnover, custom role allowlists, RFC dispatch receipts or custom worker economics.

The primary remains accountable for the final candidate, evidence and truthful bookkeeping. Preserve workspace/permission boundaries and safe writer lifecycle. Do not force native children to pretend to be `rfc-worker` or require bespoke per-child receipts; use actual available native lifecycle observations. Lack of child route visibility is a telemetry limitation, not zero cost or invented identity.

A native run may legitimately choose no children. Keep it in the native-enabled arm and record that outcome; do not force a spawn to make the treatment look different. Conversely, a client without the requested Ultra/native capability is not silently replaced by Max plus a hand-written orchestration prompt.

No custom RFC coordination instructions may be injected into this path. Inspect project, user and plugin-provided instructions, custom agent definitions and global subagent defaults for leakage. Use supported scoped configuration or a task-owned isolated environment rather than deleting or editing the user's global settings. Do not strip project correctness requirements when excluding topology policy. If exclusion cannot be established, disclose the contamination and do not claim a clean native baseline.

### Coordinator-integrator

Preserve the existing coordinator, milestone integrator, bounded-leaf procedures, routes, context renewal, read-only/worker permissions and handoff/ownership guards. No forced worker quota or model upgrade is part of the initial comparison. Source defaults are not proof of installed or served routes: snapshot the effective treatment before the trial.

This recipe owns the existing custom role machinery, not the common contract. An explicit strategy choice routes directly to it; it is not an outer wrapper around the other recipes.

### Planner-worker (experimental)

Use a strong primary planner and a named cheaper worker route. For a first variant, the planner can be Astra Max; choose the exact worker model AND effort before selection becomes runnable. Cheap is a measurement hypothesis relative to that user's account and task, not a model family alias or an inference from low reasoning effort.

The planner investigates, makes design/interface decisions, turns them into bounded work orders, diagnoses material failures, updates the plan, judges evidence and performs permitted bookkeeping/integration. Workers perform product-code/test/doc edits and focused checks; they may make ordinary local coding decisions within the work order and return material ambiguity. They do not change shared architecture, grant their own broader scope, own tracker/commit decisions or recursively delegate.

Keep the feedback loop active: plan -> implement/check -> inspect -> correct/replan. Do not define the only initial recipe as a giant one-shot plan handed to an abandoned weak worker. A plan-once variant can be a separately registered experiment later.

Start the first recipe with one worker active at a time, reusing its useful context for corrections. That makes the planned delegation policy clear without making parallelism a second uncontrolled variable; an explicitly parallel variant can be another preset.

The planner makes no product-code edits in this strict variant. It can write work orders, contract sketches and bookkeeping, inspect code and use deterministic integration commands that do not author source changes. If the planner starts supplying essentially complete product patches in its plan, record this as architect/editor behavior rather than concealing where the engineering happened.

Planner takeovers, worker upgrades and extra reviewers are not silent escape hatches. Either exclude them in the strict recipe and preserve a blocked result, or preregister a separate practical variant with explicit fallback policy. A predeclared fallback counts as strategy cost; an unplanned switch is a treatment deviation. Do not discard either because its cost is inconvenient. Planner self-review is not independent review.

## 5. Bookkeeping and readiness for every recipe

Resolve source/tracker roots and branch authority with existing helpers. Preserve personal-lane pairing, claim/finish guards, actual evidence revisions and existing acceptance semantics. Preflight required capabilities for the selected recipe; direct/native do not require bespoke RFC role files merely because coordinator-integrator does.

Do not bypass an existing MASK readiness failure indiscriminately. Classify core consumer/input/binding failures separately from unused-role requirements. If the current MASK workflow descriptor cannot express selected requirements, implement the smallest explicit cross-repository capability handoff needed, or use an honest supported isolated setup. Retain all applicable shared-source and ownership checks. No wholesale global role removal or silent default-agent substitution.

Extract or reuse topology-neutral plan binding and obligation/exit validation where currently embedded in coordinator_handoff.py. Real dispatch ownership validation stays with the coordinator recipe. A direct checkpoint is not a fake child return. Keep active command/writer reconciliation common as a safety obligation, but let native mode use native evidence rather than imposing the custom protocol.

Read-only status and usage remain observational. Review-only binds the requested candidate and real independence; it does not inherit an implementation route accidentally. A topology change during resume requires quiescing/accounting for current writers and effects, retaining unmet obligations, then explicitly recording the new segment. An experiment cannot hide that switch in its original label.

## 6. Experiment integration

The record needs a variable list of arms, not fixed D/O columns. Record declared strategy/routing separately from actual agents/routes, adherence/deviations and telemetry coverage. Recognize system-managed and unknown roles without losing attributable usage. Native partial introspection must not prevent objective code evaluation; it can prevent precise economic or per-role claims.

Keep experiment provenance outside implementation context and outside the production acceptance state. Acceptance/outcome events point to existing live evidence; the experiment index is not another issue board. A topology's extra planning, dispatch and recovery belong in its arm's cost. Comparative external judging and one-time study setup are separate disclosed costs.

## 7. Source change map

Inspect before editing; not every listed file must change.

- `skills/implement-rfc/SKILL.md`: early strategy resolution and one selected entrypoint.
- Engineering/bookkeeping/verification references: one topology-neutral obligation source; preserve every existing requirement.
- `references/milestone-integration.md`, delegated-execution.md and coordination-handoff.md: retain coordinated mechanics behind the coordinator-integrator recipe.
- `references/milestone-plans.md`, `scripts/milestone_plan.py`, milestone_continuation.py and coordinator_handoff.py: shared obligation/binding checks without fabricated native children.
- New small strategy catalog/recipes and a selection helper only where deterministic work earns it.
- `scripts/workflow_preflight.py`, mask-workflow.json and guarded setup: selected capabilities with truthful compatibility, including any narrow MASK handoff.
- roles/routing schemas, render_runtime_adapters.py and source manifest: isolated recipe-specific role sets; preserve baseline defaults and historical records.
- usage capture/report/outcome helpers: additive arm/strategy provenance and explicit native/unknown observations; no second collector.
- Active root/consumer instructions: remove unavoidable topology conflicts only under explicitly scoped edits. Retained packets remain historical.

## 8. Acceptance and regression cases

Deliver and test complete paths, not just flags or keywords:

1. Direct consumer claim -> code -> direct checks -> evidence -> permitted commit, with bespoke roles absent and native delegation disabled.
2. Native selected entry reaches common engineering without loading coordinator policy or configuring custom RFC children; no mandatory spawn. Actual Ultra capability/loading still needs native evidence.
3. Coordinator-integrator preserves baseline routes, readiness and checked handoff behavior.
4. Two-card authored milestone and interruption/resume retain grouping, scope, required evidence and selected strategy in all applicable paths; a card or context boundary is not completion.
5. Required human/native/independent review cannot be self-certified or erased by any recipe.
6. Project/personal storage, distinct worktree pairs, dirty unrelated changes, stale evidence and uncertain writers retain current guards.
7. Native telemetry with unavailable descendants or aggregate-only usage remains explicitly partial; totals do not double-count overlapping counters.
8. Planner-worker preserves product-edit ownership and accounts for feedback/recovery; an unplanned takeover is visible.
9. A fifth synthetic recipe can be registered and used in common fixture/tabletop cases without editing the board, acceptance or usage schema; duplicate/unknown/incompatible descriptors refuse safely.
10. Status/usage-only remain read-only; selecting one recipe does not load all recipe text or mutate shared/global configuration.

Measure loaded instruction paths only as a diagnostic. Run native qualification only for the routes/capabilities actually claimed and within an explicit owner-selected budget. Never infer effective host loading from a rendered file or test fixture.

Preserve existing default behavior until the owner changes it. Do not turn trial infrastructure into another general scheduler, an automatic experiment service or a model benchmark project that blocks ordinary RFC work.
