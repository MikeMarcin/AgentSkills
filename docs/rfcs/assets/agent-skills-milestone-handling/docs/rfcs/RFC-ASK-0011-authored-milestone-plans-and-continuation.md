---
id: "RFC-ASK-0011"
title: "Authored milestone plans and outcome-bound continuation"
status: "Proposed"
---

# RFC-ASK-0011: Authored milestone plans and outcome-bound continuation

## 1. Decision and scope

Make milestone planning a first-class input and runtime responsibility of
`implement-rfc`. A supplied plan is the default execution plan: discover it,
validate and reconcile it with live requirements, retain its grouping, and follow
it. Form a plan only where one is absent or incomplete. Amend existing planning
for an evidenced reason rather than recreating it at every handoff.

The same procedure handles an RFC pack, one RFC, an explicitly selected issue
collection, a large issue, a small fix and a resumed target. A milestone is a
bounded integrated outcome; an issue is a tracking/acceptance unit; an integrator
generation is a context/ownership lifetime. They are not interchangeable.

This is a new amendment to RFC-ASK-0010, not a rewrite of its settled history.
It retains the native interactive coordinator, independently selected engineering
routes, complete-slice delegation, independent risk-selected review, native waits,
exclusive writers, truthful acceptance, immutable RFC baselines and scoped commits.
It changes the unconditional milestone-complete => fresh-integrator action into
a checked result plus an explicit continuation decision.

Non-goals: a new scheduler, task database, planner role, external/API supervisor,
model-routing change, fixed generation/card budget, automatic package-script
execution, extra account purchase, broad consumer migration, or quota-savings
claim. No new human command sequence is required to implement an ordinary target.

## 2. Source basis and observed failure

The supplied September 8 AgentSkills snapshot is the implementation basis; live
reconciliation is required. See the retained pack's `reference/SOURCE_BASIS.md`
and file/dump-range hashes in `reference/source-basis.json` for exact grounding.

The snapshot's `SKILL.md` already permits the first integrator to select a
milestone, and `milestone-integration.md` already permits multi-card groupings.
`pack-lifecycle.md` reads order documents but carries sequencing into card
prerequisites, which does not retain integration grouping by itself. The
`coordinator_handoff.py` helper structurally validates returns and then maps
`milestone-complete` directly to `fresh-integrator`. Its tests supply that label;
they do not establish that the label describes the intended boundary. Worker
role instructions also refer to only the current issue-card slice.

The user reports a corrective pack being executed with card-sized integrator
turnover and high consumption. The exact live audit and latest source are not
included as a new snapshot here; the packet does not infer the cost fraction
caused by restarts. The defect this RFC addresses is independently clear: source
packaging, administrative completions and improvised labels can determine
engineering context lifetime without a durable outcome contract.

## 3. Authority and terminology

The user mandate and applicable repository/permission rules bound the work.
Live RFC/issue requirements and valid user amendments determine required behavior.
An adopted milestone plan determines its integration grouping and default order;
it cannot weaken acceptance or enlarge authorization. Board state and evidence
determine what is actually satisfied. Agent recommendations remain recommendations
until reconciled under those authorities.

| Term | Meaning |
|---|---|
| Target | The exact authorized RFCs/issues/criteria/area selection and stopping rule |
| Authored plan | Offline supplied intent, possibly complete, partial or legacy Markdown |
| Adopted plan | One live, remapped definition used for this target; amendments are recorded |
| Milestone | A bounded outcome, contributing work, exit criteria and integration boundary |
| Assignment | Exact milestone/obligations, candidate/ownership and producer authority |
| Generation | A native integrator context; may span related milestones or be replaced mid-milestone for recovery |
| Continuation | Current execution position and references, not another issue board |

An explicit user ordering constraint is binding. Array order in the authored
plan is the default preference among eligible milestones; `depends_on` expresses
hard milestone prerequisites. A blocked milestone may be bypassed only for
independent authorized work without violating required order, acceptance or
candidate protection. Milestone prerequisites supplement, never erase, actual
issue or architectural prerequisites.

## 4. Authored plan contract

Use `milestone-plan.json` as the canonical new-pack input. Its proposed schema is
`implement-rfc.milestone-plan.v1`, specified in the retained pack's
`contracts/milestone-plan.schema.json`. It contains a plan ID, scope and milestones.
Each milestone has a stable plan-local ID, outcome, typed work references,
prerequisite milestone IDs, exit criteria and a short boundary rationale.

A work reference selects either an issue or an RFC. Omitted `criteria` means all
of that document's applicable acceptance obligations; a supplied nonempty selector
list means only those obligations. Prefer existing stable criterion labels relative
to the referenced document. Exact headings or unambiguous source-text selectors
are permitted when that is how the source is organized; resolve them once during
adoption. Do not invent source criterion IDs or silently choose an ambiguous match.

`coverage` defaults to `complete`. A partial plan declares `coverage: partial`
and nonempty `unplanned_work`; these references remain required, not deferred out
of scope. The first executable milestone must be concrete. A plan can be complete
at issue granularity without duplicating every source acceptance paragraph. Runtime
coverage reconciliation must still account for every selected requirement.

The JSON has no status/Done fields, live native IDs, model routes, execution commands,
fake HEAD, absolute consumer paths or approval grants. Exit-criterion prose is data,
not an instruction to execute embedded code or treat the criterion as already passed.
A boundary explains a working result, interface/migration checkpoint, or bounded
maintenance batch; a card number, timer or heading alone is not an explanation.

`MILESTONES.md` is an optional generated rendering, not an independently maintained
plan. The manifest and implementation entrypoint explicitly link the JSON. A
legacy standalone `MILESTONES.md`, `IMPLEMENTATION_ORDER.md` or stage mapping
remains a supported authored plan. When JSON exists, a disagreeing alleged generated
view is drift to repair, not a competing runtime authority. Genuine conflicting
plans or explicit instructions require visible reconciliation.

There is no minimum card count. One issue can be a full milestone. An issue can
span milestones through disjoint criterion selectors while remaining open until
its complete acceptance is satisfied. The same obligation must not be assigned
as new work to multiple milestones. Reusing evidence is not duplicated ownership.
A complete RFC selected through multiple cards requires semantic coverage checking;
merely seeing its ID on any card does not establish full RFC coverage.

## 5. Discovery and adoption

For implementation/resume, the coordinator must resolve plan status before issuing
an engineering assignment. A small deterministic helper (proposed name
`scripts/milestone_plan.py`; reuse a live equivalent when present) performs bounded
read/parse/lookup/remap/render mechanics, never model dispatch or semantic acceptance.

Discovery order is intentional:

1. An explicit current user plan or replacement instruction is considered first.
2. Resume follows the target's adopted live-plan linkage and current continuation.
   A newly attached original packet cannot overwrite its amendments or active state.
3. A new pack follows an explicit manifest/entrypoint/README plan pointer, otherwise
   the root `milestone-plan.json` convention.
4. A planless structured lookup checks the selected target's known legacy order/
   milestone/stage documents. Markdown normalization is a bounded engineering step,
   not a universal regex planner or a new model stage.
5. Only actual absence or explicitly uncovered work invokes runtime formation.

Return compact, distinct states such as found, absent, needs-normalization,
invalid, unsupported-version, ambiguous and stale. An invalid supplied plan is
not absence. Do not silently retry a different file or issue queue to hide the
problem. The first integrator can make an obvious in-scope normalization/repair
while preserving intent; material ambiguity or changed requirements return to the
user under existing authority. Pure discovery/checks perform no mutation.

Resolve paths from the selected physical consumer and explicit source root, not
the shared skill's resolved symlink. New pack pointers must be ordinary relative
paths within the chosen pack; live pointers must remain within the selected
consumer. Reject escapes, conflicting logical identities, unsupported links and
special files. Do not crawl unrelated repositories or retained archives to guess
which plan is active. Parse data with bounded input/output and duplicate-key
rejection; network references and dynamic imports are not plan discovery.

Adopt the plan beside live project documents, conventionally
`<rfc_root>/plans/<plan-id>/milestone-plan.json`, or an explicitly configured existing
consumer location. A target with no RFC still uses a task-local plan anchor under
the consumer's supported workflow records; it does not require a synthetic RFC.
The default location must work without making users edit project configuration.

Link the live plan from the applicable RFC/issue/closeout records using the current
metadata convention; a compact `metadata.milestone_plan` reference is a suitable
card extension when no established equivalent exists. Keep one definition, not
copied groupings on every card. Validate link repair across card moves and source
exports. No global allocator or registry is introduced for plan-local IDs.

At import, use the real RFC/issue mapping for typed scope/work references and
criterion references that genuinely contain remapped IDs. Preserve milestone IDs,
ordered arrays, outcomes and integration intent. Do not mass-replace ID-like text
in historical prose or fixture examples. The original packet is immutable. Record
its provenance, live plan path and mapping in the existing LIVE_IMPORT record.
An already adopted identical plan is a no-op; a conflicting plan ID is not overwrite
permission. Partial import/adoption is reconciled on resume and cannot report ready
while required linkage or references are unresolved.

## 6. Initial preparation and planless formation

A valid authored plan is adopted rather than re-planned. Reconcile scope, resolved
references, completed evidence and relevant current dependencies; do not require
a second architect to defend every authored choice. The burden is on an amendment
to name a concrete problem. Continue normal authorized work after recording adoption;
there is no extra owner signoff just for choosing a group.

Where a plan is absent/incomplete, the first integrator surveys the requested
outcomes, sketches only the useful remainder, defines the current milestone and
implements it in that same context. The coordinator retains mandate and pointers;
it does not preload RFCs, code and all card histories to duplicate engineering
planning. A scout is optional for a named unknown, not a disposable pack planner.

Form the current milestone around a demonstrable result and gather implementation,
relevant integration, tests and documentation needed for it. Inspect relevant
not-yet-ready dependent cards: a queue's next eligible row is not the milestone.
Claim/edit work only when actual dependency/ownership rules permit it. Keep small,
connected work together and choose an explicit seam before unrelated or very large
investigation. A bounded maintenance batch is legitimate; do not invent a product
feature linking unrelated fixes merely to justify keeping a context.

Keep import, baseline capture and ordinary bookkeeping/closeout with the engineering
work they support. Import-only, review-only and closeout-only user requests retain
their actual task boundaries. Status, review and usage diagnosis do not instantiate
an implementation plan or engineering family. A one-fix request uses the minimal
one-milestone shape and focused verification, without a planner/team ceremony.

Explicit subset requests use a scoped projection of a broader adopted plan. Preserve
source linkage and relevant ordering, expose excluded prerequisites, and bind only
authorized obligations. Completing the projection does not mark its parent milestone
or the whole source RFC Done. New unrelated issues do not extend a finite mandate.
An intentionally open-ended area mandate must retain its user's stopping rule.

## 7. Execution binding and completion

The assignment binds the actual consumer/mandate, adopted plan identity, selected
milestone definition and resolved obligation set in addition to existing route,
ownership/candidate and side-effect limits. Use the existing run/dispatch/producer
identities. Compute definition fingerprints automatically; do not require users
or the coordinator to copy hash strings between mechanical commands.

The plan has no acceptance state. Live cards and evidence remain authoritative;
the current continuation records only execution position and references to those
facts. For sources without criterion IDs, store a resolved obligation projection
with source references so later changes are detectable. This is a compact assignment
record, not a second repository-wide requirement database.

The integrator works through its eligible constituent cards without a terminal
return per card. A card commit or progress message is progress within that
assignment. Resume renews dispatch identity and ownership while retaining the same
native context when suitable. In-flight commands/writers are accounted for before
a new assignment or replacement can overlap them.

Milestone completion requires all assigned obligations and exit criteria to have
relevant accepted evidence, no known critical in-scope failure, and truthful live
records. Required human/native decisions cannot be hidden in a "complete" summary.
Whole-card Done is neither necessary for a partial-card milestone nor sufficient
to prove a composed public-path exit criterion. The helper checks completeness and
identity of the supplied evidence/obligation projection; the integrator judges
whether the evidence actually proves the claims.

A text label never independently authorizes a new generation. A v2 return (exact
version reconciled with live history) separates result disposition from continuation
intent. Details and transition cases are in the retained pack's
`contracts/CONTINUATION.md`. Preserve native completion observations: a delivered
result is not proof of writer quiescence. Stale/duplicate/unknown observations must
not advance the board, accept work or launch a second writer.

## 8. Context renewal and replanning

Continue the same integrator within its current milestone and correction cycle.
Fresh context normally separates substantial completed integrated outcomes. A small,
closely related next outcome can reuse useful context with explicit renewed scope;
this is an intentional exception, not a permanent pack-sized agent pool. Before
replacement record a concrete boundary/context/availability/ownership/user-request
reason. No card-count, commit, heading or pack-count heuristic triggers replacement.

Context pressure can justify handoff before exhaustion, using actual signals where
available; never invent token telemetry. Recovery may replace a context mid-milestone
but carries the same unsatisfied obligations. First establish prior writers and
descendants inactive or safely transferred, reconcile actual edits/commands, and
retain failed approaches and invariants needed by the successor. Unsupported native
resume is a real recovery reason, not permission to fake reuse or bypass host policy.

After completion the outgoing integrator normally says the remaining authored plan
is unchanged and identifies its next eligible milestone. Replanning occurs only
for material new information, changed scope, an actual dependency/capability issue,
or unsuitable size/context. Amend only affected definitions with reason, source
basis and preserved remaining obligations. User requirements and permissions are
not ordinary replanning fields. Splitting work cannot declare the original exit
criteria passed; merging must retain their coverage.

Bind returns to the definition accepted for their dispatch, not merely today's
filename or HEAD. An unrelated future-plan edit need not invalidate an unchanged
active milestone: compare affected milestone, mandate, prerequisite and requirement
fingerprints. An affected amendment requires reconciliation and a renewed assignment
before further work; do not reinterpret an old producer's result against new scope.
No hot-upgrade or global rewrite of active runs is implied.

Human-pending/blocked results preserve the exact candidate/decision. Independent
authorized work may proceed after safe release, using a suitable current or fresh
context with a reason. A dependent milestone cannot pretend a pending predecessor
is accepted. Keep independent review fresh and genuinely independent: an implementer
cannot become its own reviewer to save context.

## 9. Role instructions, reading and reporting

Co-locate the common selection rules and conditional plan branches; retain a short
mandatory discovery/binding step in SKILL.md. The integrator sees its full milestone
and relevant source; a worker sees only its complete assigned slice and neighboring
interfaces; a reviewer sees requirements, candidate and evidence, not implementation
transcripts or the full future plan. Do not weaken applicable consumer rules to meet
an arbitrary word count. Measure actual per-role common reading paths before/after.

Reconcile canonical role definitions as well as prose references. A complete worker
slice can include explicitly assigned work from several cards; the integrator still
claims/finishes cards and owns commits. Workers cannot independently choose another
card. Leaf reuse, independent review and native wait rules remain in force. At a
real ownership transfer, account for descendants instead of keeping a permanent
unscoped worker pool.

Normal human output should identify the adopted plan and current outcome without
raw JSON. Machine mode is explicit. A typical report is:

    Plan: human-cli-correction (authored, reconciled)
    Current: complete-install — 3 contributing issues
    Progress: parser accepted; operation and public-CLI evidence remain
    Integrator: generation 1, continuing the assigned outcome

Use existing startup identity reporting; do not create a rival role banner. Extend
existing run/usage linkage minimally with plan/milestone and replacement reason.
Diagnostics can flag an explicit card-only replacement or missing justification;
`integrator_count > 1` is not itself a failure. Missing historical fields are unknown.
Cached/uncached input and output remain distinct; fewer generations do not establish
subscription savings or more accepted work. No mandatory capture or quota gate.

## 10. Compatibility, rollout and implementation of this packet

Reconcile live source before choosing schema numbers or file names. Historical v1
returns remain readable; a missing plan binding in a still-active legacy run needs
one scoped reconciliation preserving its producer, not a new generation by default.
Never reinterpret old records as evidence of checks they did not perform. New-format
unknown fields/versions produce clear compatibility diagnostics. A retained
backward reader may reproduce historical interpretation, but new plan-aware control
must not bypass binding through the v1 automatic-fresh path.

Canonical role/source updates must reach the selected runtime definitions through
the current approved adoption mechanism. Verify checked-in/generated role content
and observed host selection separately. Preserve existing routes/addenda and do not
silently use `default` in place of a missing required role. MASK readiness integration
is a separate workstream; this RFC neither depends on unfinished MASK features nor
reimplements its package installer. Explicit local qualification/selected adoption
is sufficient here; unselected consumers are not migrated.

This packet deliberately supplies its own plan now. Read its root
`IMPLEMENTATION_PROMPT.md` before delegation. Until the new reader exists, bind the
same two groups in the existing live continuation as a temporary input adaptation;
the first integrator then builds the new mechanism. Do not wait for the feature
under implementation to discover the plan required to implement it. Do not turn
seven cards into seven milestones or introduce an import-only generation. Keep
active bootstrap assignments on their bound instruction version until safe renewal.

## 11. Verification and acceptance

All criteria below are mandatory for this RFC's terminal acceptance. Offline pack
validation proves artifact consistency, not production behavior, native model
judgment or measured quota savings. `VERIFICATION.md` and `NATIVE_QUALIFICATION.md`
in the retained packet define direct evidence and a bounded test course. Tests must
start from raw inputs with absent discovery/registration/remapping, not fixtures
that already selected the desired milestone or supplied a convenient disposition.

**RFC-ASK-0011-AC01** — **Authored-plan-first discovery.** Ordinary implementation startup discovers an explicitly selected plan, an adopted live plan, a linked pack plan, or the conventional root milestone-plan.json before selecting card-sized work. Valid authored grouping is preserved. A supplied malformed, conflicting or unsupported plan is diagnosed rather than silently treated as absent.

**RFC-ASK-0011-AC02** — **Portable plan contract and authoring.** The versioned plan contract supports whole issues, explicit portions of issues, RFC criteria without cards, complete and partial decomposition, stable milestone identities, outcomes, dependencies and exit criteria. It contains no native-agent identity, model launch instructions, live completion state or fabricated Git revisions. New authoring guidance and examples use the canonical plan and a generated human view.

**RFC-ASK-0011-AC03** — **Live adoption and resume linkage.** Import remaps typed RFC/issue/criterion references using the actual ID map, retains authored milestone identities and immutable source provenance, and establishes discoverable live linkage. An interrupted or later RFC/issue-only invocation resumes the adopted plan rather than restoring the original or rebuilding grouping. Unrelated consumers, retained packets, and unrelated Git work are preserved.

**RFC-ASK-0011-AC04** — **Plan-driven assignment and continuation.** Assignments bind the selected target, plan definition, milestone and obligation set. Finishing an intermediate card, landing a commit, importing the pack or emitting a progress heading does not complete the milestone or cause integrator replacement. One invocation normally continues through eligible constituent work without a coordinator round trip per card.

**RFC-ASK-0011-AC05** — **Completion separate from context renewal.** The continuation contract separates engineering disposition from continue/fresh/wait/stop decisions. Fresh context normally separates substantial integrated outcomes; related small continuation can reuse context with renewed authority. Recovery can replace an unavailable or pressured context before completion without losing unfinished obligations. Replacement needs a recorded concrete reason, never a fixed card/pack count.

**RFC-ASK-0011-AC06** — **Legacy and planless targets.** Legacy Markdown/stage plans normalize once with preserved intent. A planless RFC, loose issue set, large issue or small fix obtains a bounded current milestone from the first integrator, which then implements it. No compulsory planner agent, synthetic RFC, full upfront decomposition, or new approval ceremony is introduced. Status/review/usage-only paths bypass implementation planning.

**RFC-ASK-0011-AC07** — **Dependency and partial-work correctness.** Planning looks through relevant dependency chains, while execution claims only eligible work. Partial issue/criterion assignments do not close whole cards prematurely. Selected subsets cannot authorize the rest of a pack. Already satisfied work reuses relevant evidence; blocked/human-pending prerequisites and out-of-scope dependencies remain explicit.

**RFC-ASK-0011-AC08** — **Reasoned amendment without lost work.** A completed checkpoint normally retains the remaining authored plan unchanged. Material discoveries permit scoped amendments with a reason and preserved outstanding obligations; requirement or permission changes retain user authority. Active assignments use exact definition identity, stale/duplicate returns cannot advance changed scope, and interruption/recovery never replays uncertain mutation.

**RFC-ASK-0011-AC09** — **Role and verification efficiency.** Coordinator, integrator, workers and reviewers receive only their needed plan projection and relevant requirements. Complete worker assignments may include multiple explicitly assigned cards; unrelated work and board authority remain excluded. Shared rules are co-located and rendered roles agree. Focused checks and existing risk-selected independent review are preserved without repeated unchanged full-milestone review per card.

**RFC-ASK-0011-AC10** — **Structural and public-path regression.** Tests start from raw structured/legacy/planless inputs, not pre-normalized fixtures. Public helper paths through two linked consumers cover discovery, remap, resume, amendment, refusal and false-completion handling. Contract tests distinguish structural validation from semantic acceptance and include malformed, conflicting, stale, partial, reordered and duplicate cases.

**RFC-ASK-0011-AC11** — **Bounded native qualification.** Actual selected Claude and Codex interactive drivers demonstrate authored grouping across intermediate card completions and a meaningful integration transition, plus a small planless follow-up. Exact native roles/routes, producer identities, observed context/turn boundaries and limitations are recorded. Mock tests, generated files and self-reported banners do not substitute for observed host behavior.

**RFC-ASK-0011-AC12** — **Safe selected adoption and truthful closeout.** Current source/adapters/contracts are reconciled at a safe boundary for the explicitly selected AgentSkills consumer and disposable fixtures. Existing routes, addenda, ownership protections and unrelated active assignments survive. Lightweight diagnostic linkage distinguishes justified generations from unexplained churn without inventing quota savings. All mandatory criteria have direct evidence or remain explicitly open; settled RFC history is unchanged.

## 12. Risks and rejected alternatives

An overly rigid authored plan can become wrong as implementation changes. Scoped,
reasoned amendments preserve intent without pretending the snapshot is omniscient.
A completely advisory plan can be discarded casually; adoption therefore makes its
grouping the default, not merely a hint. A structured parser cannot judge milestone
size or requirements truth; native behavior and engineering evidence remain separate.

One generation per card discards useful context. One generation per ZIP treats
packaging as a context budget. An exhaustive upfront planner duplicates intake;
next-ready-card-only planning ignores integration dependencies. A mandatory planner
agent adds startup without necessarily improving judgment. Multiple mutable JSON/
Markdown/board copies lose authority. This RFC instead uses authored-plan-first
adoption, minimal fallback formation and one live definition with explicit continuation.

Large schemas, blanket matrices and repeated expensive qualification would undermine
this correction. Keep the schema to required intent, use the existing native host
and helpers, and exercise the actual failure with small representative tasks.
