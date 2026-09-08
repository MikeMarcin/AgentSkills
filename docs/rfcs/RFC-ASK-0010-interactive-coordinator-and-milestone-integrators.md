---
schema: "implement-rfc.rfc.v1"
id: "RFC-ASK-0010"
title: "Interactive coordinator and milestone integrators"
status: "Implementing"
---

# Interactive coordinator and milestone integrators

## Decision

Run authorized RFC work from a thin native interactive coordinator. It retains
the user's mandate and execution continuity; a fresh `rfc-integrator` subagent
owns each milestone's engineering context. The coordinator waits for results,
then dispatches the next milestone without requiring another user prompt.

Pair this topology with milestone-focused implementation: select demonstrable
integrated behavior, give complete slices to owners, exercise a thin composed
path early, verify at the appropriate boundary, and return only the current
frontier and necessary rationale. Keep the implementation quality bar unchanged.

The owner selected Codex **GPT-5.6 Sol low** and Claude **Opus 5 low** for the
coordinator because Codex allowance is the limiting resource. These are operational
choices, not claims of benchmark equivalence. The integrator and every leaf role
have separately bound engineering routes. [Routing](assets/agent-skills-interactive-coordinator-2026-09-08/ROUTING.md) defines
preservation and the proposed fallback defaults for previously unconfigured runs.

This is a new prospective RFC. Preserve the settled contracts and historical
acceptance of RFC-ASK-0003/0005/0007/0008/0009; update active instructions where
this RFC deliberately changes current behavior. The supplied reuse patch already
exists in the current dump and remains the starting point.

## Evidence and problem

The supplied September 8 audit reports 4,573 responses and about 575 million
input tokens for the selected task family, with a mean input around 126,000 tokens.
Its primary produced 1,721 responses and 215 million input tokens. Fresh initial
children later accumulated substantial contexts; the later reuse patch has
focused/tabletop evidence, not measured savings. These historical observations
motivate the design, not a measured attribution of waste.

The current skill ties integration authority to the primary, encourages delegation
alongside useful primary work, and renders all existing roles as leaves. That
combination cannot simply be relabeled into a coordinator/integrator hierarchy.
The supplied writing-for-agents references motivate explicit ordered steps,
checkable completion, co-located rules and branch-triggered reference loading.
See [SOURCE_BASIS.md](assets/agent-skills-interactive-coordinator-2026-09-08/SOURCE_BASIS.md) for exact source boundaries.

## Goals and non-goals

The pack must continue unattended within a running native interactive session,
through all eligible authorized work or an actual stop/required human boundary.
A new milestone gets fresh engineering context without losing pack decisions,
source ownership, acceptance obligations or the immutable baseline. Ordinary
work remains straightforward; no new approval is required merely to rotate.

This RFC does not introduce an external supervisor, programmatic subscription
credential reuse, headless CLI loop, SDK control plane, daemon, queue service,
fleet scheduler, cross-provider coordinator, task-language runtime or new board.
It does not promise survival after the interactive host exits, exact quota
savings, unlimited runtime, or freedom from genuine permission prompts. It does
not authorize credential, permission, billing, source-publication or push changes.

## Terminology

| Term | Meaning |
|---|---|
| Coordinator | The native interactive main conversation, responsible for mandate and continuation, not engineering integration |
| Milestone | One bounded integrated capability demonstrated through its relevant public/selected boundary; may include several cards |
| Integrator | The sole designated engineering owner for the current milestone and assigned integration scope |
| Slice owner | Worker or integrator carrying one bounded implementation through diagnosis and focused verification |
| Handoff | Current frontier, relevant rationale and evidence pointers needed by a successor; not the conversation transcript |
| Invocation | A runtime run/turn of an agent; reaching its limit is not completing the milestone |
| Quiescent | Assigned writers and task commands have completed/stopped and their effects are accounted for; not simply “no message arrived” |

## 1. Authority and native topology

Ordinary topology is coordinator → one integrator → bounded leaf roles. There is
one active engineering integrator for a writable integration scope. The integrator
may implement coupled work itself and delegate independent complete slices. Leaves
remain leaves; integrators never spawn peer integrators or coordinators.

The coordinator owns user communication, the exact authorized scope and subsequent
user amendments, selected session route, active child identity, and continuation.
It may inspect compact status and maintain a small run memo. It does not become a
parallel implementer, duplicate the integrator's diff/test review, allocate cards
on the integrator's behalf, or accept engineering claims independently.

The designated integrator owns RFC interpretation within the user's mandate,
architecture/local design, milestones and slice selection, verification sufficiency,
review adjudication, staging, explicit-path commits and authorized board/RFC updates.
Integration authority follows the role and assigned repository/worktree, not
whether the runtime calls the conversation “primary.” Main-only allocator and
tracker-rule authority remains main-only. A lane integrator keeps the existing
lane limitations and requests main integration rather than modifying main.

A return from this expressly authorized integrator can carry its acceptance
judgment, supported by live evidence. Ordinary worker/reviewer results remain
inputs, not acceptance authority. No role can broaden user scope, approve native
permission prompts, or infer permission to publish/push.

Use native non-history-copying subagents. Inspect supported spawning, wait/resume,
background tools, role routing and depth on the installed host. The interface
must not fake freshness by invoking the skill inline or by forking the whole
coordinator history. Count integrators and their descendants against actual host
capacity; preserve headroom and release completed task-owned threads when safe.

Where a host lacks grandchildren, keep ordinary work inside the same correctly
routed integrator. A required independent review can use the bounded native
review-relay branch in section 4; otherwise leave the actual missing capability
open. This is not permission to launch headless agents or let Sol-low perform
an unannounced serial engineering fallback.

## 2. Coordinator loop

**Bind.** Resolve the selected consumer, scope, stop conditions and routes. Retain
original user requirements and explicit amendments distinctly from implementation
summaries. Bind an integrator route before the coordinator downshift. Inspect
existing run/claim ownership on resume. Completion: one unambiguous authorized
scope and no unexplained previous writer.

**Dispatch.** Send one integrator the selected root/branch, mandate revision,
current milestone objective or initial “select next milestone” instruction,
relevant live references, immutable baseline references, authority/ownership and
compact return contract. On the first run the integrator does detailed pack intake;
the coordinator does not scan the entire implementation before delegating.
Completion: exact child identity and requested route associated with this dispatch.

**Wait.** Use the native blocking/completion primitive or its supported idle
continuation. Do not poll through unnecessary model turns, inspect the transcript
repeatedly or invent engineering work while waiting. A wait timeout retains the
same child. Act on user interruption, actionable blocker, permission event or
completion; comply with host-required user updates without internal status chatter.
Completion: a meaningful event, not the passage of an arbitrary interval.

**Consume and continue.** Validate the returned identity, current mandate,
disposition and ownership at the level needed to continue. Consume evidence
references; engineering verification already belongs to the integrator. A missing
or contradictory return is a clarification to that integrator, not permission
to mark the milestone complete. Continue through eligible authorized scope without
an extra “continue?” prompt.

Readiness requires both a result and terminal/quiescent execution observations
where the native host exposes them. Do not release write ownership from prose
alone when the runtime says the producer or a descendant is still working.
When native visibility is limited, preserve the explicit uncertainty and reconcile
it before giving another writer the same scope.

## 3. Milestone-focused implementation

The integrator reorients from live RFC/cards, consumer rules, current code and
compact continuation. It verifies baseline/candidate/claims rather than treating
a handoff as unquestionable state. Original acceptance and project instructions
remain mandatory; it reads applicable instructions even if hidden host injection
cannot be measured.

Choose the next coherent **usable result**, not a fixed card count, subsystem-wide
assignment or timer. A one-card fix may be one milestone; a long pack requires
multiple milestones. Specify demonstrable behavior, relevant criteria, paths,
interfaces and required human/native checks. For lifecycle/shared-state work,
exercise a thin public composition before expanding all dependent features. A
milestone is an execution grouping of live cards, not another mutable task list.

Give a worker the implementation, local diagnosis and focused checks required to
reach candidate-ready. Bounded local design and diagnosis remain standard-worker
work; a named unresolved reasoning problem selects deep. Consequence selects
safeguards/review, not automatically higher effort. The integrator does different
useful work or waits; it does not reconstruct every worker command.

Use the smallest useful team, adding concurrent work only for independent results
with explicit ownership and compatible interfaces. File disjointness alone does
not establish semantic independence. Run short deterministic commands directly;
batch prescribed commands when doing so removes avoidable interaction. Keep full
logs in task-owned files and return compact outcomes/failure locations. Existing
bounded runner support remains optional and does not become the outer driver.

Reuse agents for the same problem's correction or relevant continuation with an
appropriate role. Retire a replaced writer before another edits its scope. Start
a fresh context for a new unrelated acceptance problem or independent review.
Within a milestone the integrator remains continuous across fixes and partial
invocations. At the next milestone it is replaced; this is the deliberate context
boundary even when adjacent milestones concern the same subsystem.

## 4. Return and continuation contract

[contracts/README.md](assets/agent-skills-interactive-coordinator-2026-09-08/contracts/README.md) defines the compact logical
fields. Use the actual native result plus a small durable return when needed;
this does not require a durable event service, schema registry or output reparsing
model. Preserve only one authoritative current continuation on a chosen live
closeout (other closeouts can link it). A small ignored run memo may retain exact
user amendments and native IDs; it contains neither another backlog nor raw logs.

| Disposition | Coordinator action |
|---|---|
| milestone-complete | After result/ownership checks, start a fresh integrator for its bounded next milestone |
| continue-milestone | Resume the same integrator for the unresolved current milestone; renew the assignment scope |
| human-pending | Preserve exact required decisions/candidate protection. Continue independent work via a fresh integrator when eligible; otherwise hand the pending work to the user |
| blocked | Preserve the actual blocker. Continue separately eligible work only after safe release; otherwise stop with an actionable report |
| cancelled | Stop; do not resurrect the agent or launch the next milestone |
| pack-complete | Report the integrator's verified closeout, after compact scope/identity consistency checks; required pending acceptance forbids this disposition |
| review-request | Only the explicit no-grandchildren fallback: quiesce writers, spawn the integrator-selected native leaf reviewer, then resume the same integrator to adjudicate its result |

The review relay is not a general sibling-worker broker. The integrator supplies
the exact reviewer role, candidate, acceptance/risk question and evidence pointers.
The coordinator forwards that bounded assignment, waits and passes its result
reference back without adjudication. Reviewer and integrator must not edit the
candidate concurrently. An unsupported review remains an actual limitation, never
an invitation for an external supervisor.

Bind returns to the run/dispatch, producer identity and mandate revision. A duplicate
terminal event is consumed once. A late obsolete return cannot override a newer
user amendment, reaccept cancelled work or launch a duplicate milestone. After
terminal collection, do not send a courtesy message to a retired agent: messaging
can be a resume operation. Resume always means an explicit live assignment.

User scope changes are forwarded to the current integrator with a new mandate
revision. On cancellation, stop task-owned work where supported, account for
outstanding effects and preserve partial work. If a producer disappears mid-write,
first establish it is inactive, inspect the task state and use a recovery assignment;
never blindly replay mutation. Host exit is an interruption, not a promised
automatic restart. Resume uses exact known identities or a fresh reconciled
recovery context, never “most recent session” guessing.

Repeated identical partial returns without new progress or an actionable next
step trigger a blocker investigation, not an unbounded resume loop. The return
may be longer when essential rationale requires it; context-size pressure never
converts unfinished acceptance into success.

## 5. Quality, attendance and closeout

Keep focused changed-surface verification, direct public-path checks when helper
tests can pass with false acceptance, and one justified integration-focused pass
per meaningful milestone. Reuse unchanged passing evidence by relevant inputs,
not by coincidental HEAD equality. Fixes receive affected rechecks. Wider relevant
suites/native checks are selected for the claims and combined risk they resolve;
there is no automatic exhaustive matrix or blanket ban on broad checks.

Review remains independent when requested or risk warrants it. Give a reviewer
requirements, candidate and evidence, not the implementation narrative. Critical
review replaces ordinary review for the named material risk. Reproduce/adjudicate
findings; narrow correction rechecks do not create a whole-candidate review loop.
An implementer is not its own independent reviewer, including after a role rename.

Claim before source changes; reserve on main and commit reservations before use.
Keep explicit acceptance files/paths and existing index/ownership guards. The
integrator finishes cards; helpers never infer semantic acceptance. Record real
criterion, outcome, revision and evidence on live records.

Required human decisions remain pending while independent work continues. Attended
preparation uses the existing attended-review/wizard mechanisms, surfaces ready
items promptly, saves partial decisions and respects candidate protections and
explicit release. Do not add human review solely because a surface has UI.
A later verdict is checked against its actual candidate; unrelated HEAD changes
do not automatically invalidate it. The coordinator can present the resulting
page/ask while the integrator owns preparation and incorporation.

At RFC closeout inspect the final scoped diff against immutable RFC_BASE_SHA,
account for every required criterion and relevant in-scope discovery, reconcile
cards/RFC/index and run the configured structure gate. Full-pack closure is not
repeated at every milestone. Required human/native gaps keep terminal status open.
Clean consumed task-owned resources while preserving current handoffs and useful
artifacts. No local milestone handoff implies a Git push.

## 6. Context-efficient skill structure and common workflows

The short public SKILL.md serves the interactive coordinator. A role branch sends
an already assigned integrator directly to its implementation reference and sends
workers/reviewers to their own assignments. This prevents recursive application
of the coordinator loop. Keep one public skill; plain references supply the
sequence/branch cut described in writing-for-agents.

Use [draft instructions](assets/agent-skills-interactive-coordinator-2026-09-08/draft/skills/implement-rfc/README.md) as editorial
candidates. Model IDs and consumer facts stay in config; command flags remain in
existing public helper contracts. Route references by explicit operations rather
than preload all files. Generated role prompts carry only the relevant role and
necessary reference pointer. The actual combined text of each path, including
mandatory consumer reads, is what matters—not merely SKILL.md line count.

Status-only requests inspect compact scoped state without a child or source writes.
A tiny authorized implementation uses one integrator, not a mandatory scout→worker→
test-runner→reviewer pipeline. Resume restores ownership/mandate/frontier before
work. Review-only work may dispatch one read-only reviewer directly and return its
findings; source and board stay unchanged unless repairs are separately authorized.
Closeout-only work reuses valid evidence and runs only missing/warranted checks.
Attendance and runtime-limited branches preserve the same authority and quality.
An explicit owner opt-out can use the direct integrator procedure in the main
session with its engineering route; never silently implement in a low coordinator.

## 7. Native qualification, deployment and measurement

Qualify one bounded two-milestone run in each selected native interactive driver.
Each must show automatic second-milestone dispatch, a fresh integrator context,
useful prior invariants retained without first-milestone transcript, actual role
routing, scoped commits, no duplicate writer and a thin coordinator. Exercise a
same-problem correction/partial continuation plus truthful human-pending behavior
in those cases or focused additional fixtures, not a large paid benchmark matrix.
Use disposable consumers and actual subscription-backed host sessions; no API
substitute. Missing required native evidence remains open. Respect actual owner
spend authorization; this document does not fabricate a trial ceiling.

Keep native capability and quality acceptance separate from savings evidence.
The efficiency readout includes coordinator, all integrator generations and leaf
descendants, setup, failed attempts, correction, review and integration. Count
owning native responses once; response/turn/thread/rolling counters are alternate
surfaces, not additive spend. Cached input and reasoning output remain subsets.
Unknown ownership or missing outcomes stay unknown. The narrow existing collector
correction is in scope; a new dashboard/evaluation service is not.

The requested 40+ productive project-hour goal corresponds approximately to a
60% reduction from the earlier extrapolated 16.1-hour allowance pace, conditional
on comparable useful work and quota weighting. It is not a pass threshold for
this implementation. Record native behavior, quality, accepted capabilities and
all-in observations; compare matched work only when a separately bounded comparison
is available. Unmatched backlog work can support an owner trial/adoption decision,
not a causal claim of 60% savings. Do not prolong sessions by adding idle time.

Existing experiment helpers permit one factor and restrict unmatched promotion.
Leave that controlled-experiment meaning intact: this owner-directed combined
workflow trial changes topology, instructions and coordinator route together.
Describe it as a combined observational rollout; do not label it a one-factor
experiment or weaken old experimental validity checks to get a “promote” result.

Render from canonical authoring source only for explicitly selected development
consumers; pinned consumers use their selected artifact and normal guarded MASK
updates. Preserve active assignments and source versions; no hot-switch claims.
Update root/current instructions and exact legacy-preservation tests without
rewriting retained historical packs. Prove two distinct fixture consumers remain
isolated. Record candidate/source/artifact identity, native host/version and
configured versus observed routes. Rollback is a guarded change of selected owned
workflow artifacts, never reset of accepted product work or private audit history.

## Acceptance criteria

**RFC-ASK-0010-AC01 — Native interactive continuity.** One coordinator remains in
the native interactive session and automatically dispatches the second milestone
integrator after the first is safely consumed; no external/headless/API supervisor.

**RFC-ASK-0010-AC02 — Independent routing.** Coordinator defaults match the owner's
Sol-low/Opus-low decision. Integrator route resolution preserves explicit prior
engineering choices; all seven existing leaf roles retain their routes. Actual
request precedence and requested/observed distinctions are tested.

**RFC-ASK-0010-AC03 — Role authority and ownership.** The designated integrator may
perform authorized integration/board/commit operations. Existing leaves cannot.
Main/lane scope, exclusive writers, permissions and side-effect guards survive.

**RFC-ASK-0010-AC04 — Bounded milestone delivery.** A real composed result is exercised
early; complete slice owners implement, diagnose and check; small/coupled work
stays local to the integrator. No mandatory role pipeline or whole-pack child.

**RFC-ASK-0010-AC05 — Freshness and correction continuity.** Each new milestone has
a fresh non-history-copying integrator; current-problem corrections/partial runs
resume the current one. Required invariants survive without transcript preload.

**RFC-ASK-0010-AC06 — Safe continuation contract.** Exact identities and mandate
revision govern duplicate, stale, incomplete, cancelled, active-writer and recovery
cases. Native result and execution completion are distinguished. Waiting does not
become a coordinator investigation or busy loop.

**RFC-ASK-0010-AC07 — Preserved quality and acceptance.** Direct criteria/public-path
checks, risk-selected independent review, affected reruns, explicit acceptance
records and immutable-baseline closeout remain operative; no review or testing
quality reduction is accepted as an efficiency optimization.

**RFC-ASK-0010-AC08 — Common workflow coverage.** Scoped implementation, one-card
work, resume, status-only, review/closeout-only, attended preparation/partial intake
and runtime-limited paths follow the intended role and authority boundaries.
Required human/native gaps remain open while independent work continues.

**RFC-ASK-0010-AC09 — Efficient and reachable instructions.** Ordered role-specific
steps have checkable exits; branch references are reachable before use; no conflicting
active primary/leaf rules remain. Measured common-path loads include generated
prompts and consumer rules. Plain package validation and source immutability pass.

**RFC-ASK-0010-AC10 — Codex native qualification.** The named installed Codex interactive
host demonstrates the two-milestone path with actual requested/effective routes,
freshness, native waiting/resume and quality evidence. Mocks do not satisfy it.

**RFC-ASK-0010-AC11 — Claude native qualification.** The named installed Claude Code
interactive host demonstrates that path, including actual background/nesting tools,
effort isolation and continuation. A CLI version check alone does not satisfy it.

**RFC-ASK-0010-AC12 — Honest whole-family measurement.** The existing collector/reconciler
covers owning response records and transitive descendants without duplicates;
missing outcomes are not zero. The readout includes all attempts, preserves quality
observations, and clearly distinguishes quota, tokens and rate equivalents.

**RFC-ASK-0010-AC13 — Scoped activation and rollback.** Two distinct fixture consumers
and selected real adoption preserve ownership, pins, source identity and existing
explicit choices. Runtime-loaded behavior is distinguished from rendering; rollback
preserves product commits/history and refuses unexpected output changes.

**RFC-ASK-0010-AC14 — Truthful integration and closeout.** Actual baseline, final
scoped diff, each required criterion and nine-card linkage are reconciled on the
live board. The RFC reaches Auto-Verified only after required native and semantic
acceptance; savings may be negative/inconclusive and are never invented.

## Implementation scope

See [CHANGE_MAP.md](assets/agent-skills-interactive-coordinator-2026-09-08/CHANGE_MAP.md), [IMPLEMENTATION_ORDER.md](assets/agent-skills-interactive-coordinator-2026-09-08/IMPLEMENTATION_ORDER.md)
and the linked cards. The live RFC should retain links to the imported packet
assets or appropriate active docs after intake; import rewrites packet-relative
links, preserving this retained original. Program runtime changes in ManageAgentSkills
and migrations of unselected consumers are outside this RFC.

## Implementation authorization

The owner directed implementation of this pack on 2026-09-08, accepting this RFC. Scope is AgentSkills; original RFC_BASE_SHA remains 9f991d9027a1aaa9bd9827eb4c51ef6d33432f7a. M1 covers ASK-0051–0053; M2 covers ASK-0054–0056; M3 covers ASK-0057–0058. Native acceptance and selected adoption require actual evidence. No consumer fleet migration or push is authorized.
