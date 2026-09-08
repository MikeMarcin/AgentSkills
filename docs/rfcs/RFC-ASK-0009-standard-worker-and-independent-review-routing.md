---
schema: "implement-rfc.rfc.v1"
id: "RFC-ASK-0009"
title: "Standard implementation worker and independent review routing"
status: "Auto-Verified"
---

# Standard implementation worker and independent review routing

## Decision and relationship to existing work

Make `rfc-worker` the broadly capable default implementation engineer. Rename the
existing difficult-work role to `rfc-worker-deep`, retire `rfc-worker-routine` from
new dispatch, and configure normal review independently of deep implementation.
Adopt the owner's requested provider/effort allocation below. These decisions are
author-directed; the Proposed lifecycle means not yet imported/implemented, not
that another routing interview or benchmark is required before starting.

This is a prospective follow-up to RFC-ASK-0008. Preserve its settled closeout,
observational evidence and inconclusive cost/quality result. Leave RFC-ASK-0005–0007
and their runner, capture, accounting and issue-board contracts intact.

## Current boundary

The supplied source assigns `rfc-worker-routine` to `standard` (Astra low / Opus high),
and both `rfc-worker` and `rfc-reviewer` to `deep` (Astra high / Fable high).
Critical review is Astra xhigh / Fable xhigh. The routine contract requires an
established approach and existing pattern, and categorically excludes sensitive
behavior changes. The generic role name consequently favors the costly exception.

The renderer has a closed class set, schema enums, routine-specific worker-addenda
inheritance, and no retirement of obsolete generated role files. The audit parser
recognizes `routine|deep|unknown` and two old worker names. These are part of the
change, not incidental cleanup. Exact locations are in the packet SOURCE_BASIS.

## Target routing

| Role | Class | Codex model | Effort | Claude model | Effort |
|---|---|---|---|---|---|
| `rfc-utility` | `mechanical` | `gpt-5.6-luna` | xhigh | `claude-haiku-4-5` | unsupported/null |
| `rfc-test-runner` | `mechanical` | `gpt-5.6-luna` | xhigh | `claude-haiku-4-5` | unsupported/null |
| `rfc-scout` | `balanced` | `gpt-5.6-sol` | low | `claude-opus-5` | low |
| `rfc-worker` | `standard` | `gpt-6-astra` | low | `claude-opus-5` | xhigh |
| `rfc-worker-deep` | `deep` | `gpt-6-astra` | high | `claude-fable-5-1` | high |
| `rfc-reviewer` | `review` | `gpt-6-astra` | medium | `claude-fable-5-1` | medium |
| `rfc-reviewer-critical` | `critical` | `gpt-6-astra` | xhigh | `claude-fable-5-1` | high |

`review` is a separate route class, not another agent persona. The deep-worker and
critical-review Claude requests currently coincide; keep their contracts and route
settings independent. Class names are semantic profiles, not a cross-model numeric
ranking: Opus xhigh does not make a standard assignment a deep assignment.

Preserve max_turns: utility 20, scout 28, workers 56, test runner 56, reviewer 40,
critical reviewer 56. Preserve each role's existing mutation authority and leaf
behavior. Neither reviewer receives source-write access. Preserve the normal
reviewer's adversarial acceptance checking, negative-path scrutiny and evidence
requirements. Changing effort never changes the acceptance bar.

## Standard-first selection

Use `rfc-worker` for normal delegated engineering: features, investigation and bug
repair, multi-file changes, refactoring, local design choices, tests and implementation
of approved architectural decisions. Require a clear goal, exclusive ownership,
constraints, acceptance criteria and a credible verification strategy. A worker can
develop that strategy and add its tests. An exact repository precedent or a prewritten
solution is not a prerequisite.

Unfamiliar code, multiple files, local design judgment, an ordinary failing test or a
sensitive-domain label alone does not justify deep routing. In particular, prescribed
permission checks, approved persistence/wire changes and known synchronization designs
can be implemented standard while receiving appropriate independent review.

Select `rfc-worker-deep` for a named unresolved reasoning problem: conflicting
invariants, difficult causal diagnosis, a materially ambiguous technical solution
within approved scope, or evidence from a bounded attempt that the standard route
cannot resolve the problem. A difficult problem known in advance can go directly deep;
do not spend a mandatory failed attempt first. Ordinary debugging can continue on
standard while it is making progress. Repeated blind retries are not a policy.

A deep assignment names the problem, established evidence and requested result.
Carry forward useful work. When the difficulty is resolved, return remaining ordinary
implementation to standard where a handoff is useful; do not restart or split trivial
remaining work merely to satisfy a routing ratio. A scope/authority/architecture
approval question goes to the integrator, not automatically to a more expensive model.
A capacity error follows the existing explicit capacity/fallback policy, not escalation.

Small or tightly coupled work may remain in the primary. Prescribed build/test stages
use the existing runner or test-runner when useful. No agent is mandatory solely to
show a standard-first ratio. The objective is that most ordinary delegated implementation
starts standard, not that a fixed percentage of all tasks or tokens must use it.

## Review selection and approval

Normal independent review uses `rfc-reviewer` at medium on both providers. Select the
existing critical reviewer up front when a named material risk warrants deeper
counterexample analysis. Do not wait for medium to announce that it missed a defect.
Risk selection is not a requirement to audit every sensitive domain in every change.

Keep the same compact findings contract and integrator adjudication. Do not run
medium then critical by default. A specific unresolved review question can receive
an explicit verified route override or the critical reviewer; record the reason and
review only the relevant question. Do not create a third permanent reviewer persona.
The critical Fable route is high, as requested, not an automatic restoration to xhigh.

The integrator keeps acceptance, commits and card transitions. Workers do not gain
those privileges through renaming or increased reasoning. Source-writing companion
support remains whatever the current runtime actually qualifies; this RFC adds none.

## Configuration and adapter changes

Edit canonical `skills/implement-rfc` source only. Change SKILL.md, roles.json,
routing.json and their active routing/delegation/audit references together. Extend
`MODEL_CLASSES` and routing.schema.json for `review`; active reviewer assignment must
resolve to it. Preserve historical config readability, strict typo rejection and
explicit-user > admitted-order > selected-profile > baseline precedence. Test reviewer
and worker overrides separately. Keep provider names out of shared semantic role prose.

Update native Codex/Claude rendering and the Codex companion path. Current owned
files named `rfc-worker` change meaning; new files named `rfc-worker-deep` must be
created, and owned obsolete `rfc-worker-routine` files retired. A blind JSON edit or
search/replace is insufficient.

Preflight all touched existing destinations and retired paths before changing any:
require the expected project/manifest ownership, generator marker, matching prior
content hash and safe regular-file paths without linked parents. A modified,
unrecognized or linked path blocks that migration and remains untouched. No recursive
delete, force overwrite or blanket removal of `.claude/agents`/`.codex/agents`.
`--check` detects stale and retired outputs without mutation. Record the new manifest
only after success; keep interrupted publication detectable and safely retryable, and
do not launch from a mixed adapter set. Reuse the renderer's existing safe-write
mechanisms; do not introduce a new deployment platform.

Preserve project-specific worker safeguards in both new roles. Existing
`role_addenda["rfc-worker"]` are common worker constraints and apply once to standard
and deep. Existing `role_addenda["rfc-worker-routine"]` remain additional standard-worker
constraints during compatibility; new `role_addenda["rfc-worker-deep"]` apply only deep.
Deduplicate identical strings stably without dropping distinct constraints. Explicit
legacy local restrictions may be stricter than the new shared default: retain and flag
for owner review, never erase or reinterpret them. No consumer-wide context rewrite is
needed merely to preserve common boundaries.

New selectors use the new names. An old `rfc-worker-routine` launch/override receives a
clear migration diagnostic; do not silently discard or map an override to a different
route. Existing admitted work or resumed sessions retain their original assignment and
route evidence until consumed or explicitly reissued by the integrator. In particular,
an old `rfc-worker` assignment must not silently become standard merely because a
new resolver now uses that name. Inventory active orders before regeneration. No new
global alias registry or hot migration of active model conversations.

## Historical usage and observability

Emit `Routing: standard | Reason: default implementation` for the ordinary default
(or the actual supplied reason), and `Routing: deep | Reason: <specific problem>` for
explicit deep work. Keep the existing startup/final compatibility format rather than
introducing another command per assignment. Missing assignment information stays unknown.

Extend the role_usage parser and worker classification to both new workers while
retaining old names and `routine` decisions. Read the new `standard` decision. Preserve
raw role names, observations, reasons and historical schema/source digests. A historic
`rfc-worker` without a contemporaneous route/class/decision remains unclassified; never
use today's default, a timestamp, or model-name heuristics to rewrite history.

Use existing assignment/manifest/receipt evidence when available for derived categories;
label its basis and separate requested settings from observed serving settings. Unknown
model/effort and synthetic error records remain unknown/errors. Keep dispatch share,
escalation, outcomes and consumption separate; a few deep tasks can dominate consumption
without most work being misrouted. Do not add an inference-based billing model or a
second usage collector. Existing cwd and `--mask-projects` capture behavior stays intact.

## Runtime qualification and cost claims

Use exact model IDs. Requested settings are not proof of actual serving settings.
Current official documentation supports the requested effort values and states Fable
5.1 requires Claude Code 2.1.255, above this source's declared 2.1.219 floor. Align the
declaration/documented check to at least 2.1.255 (never lower a higher live floor); use
the existing runtime admission path to report unsupported/capped settings. Do not add
an auto-updater or silently clamp a requested route and report it as successful.

Use plain `xhigh`, not Claude `ultracode`; the latter adds workflow behavior. Preserve
current processing speed and primary configuration. Do not translate a selected effort
into permission to purchase credits, redeem resets or fall back to another model.
Provider effort labels are model-specific. The owner's allowance observations and
Astra/Opus comparison motivate the choice but are not verified project-task benchmarks.
Lower Fable effort and more Opus work are intended allocation changes, not promised
subscription savings or a proof of equivalent review quality.

## Qualification, rollout and rollback

Test exact routes, schema validation, rendered selected instructions, inherited addenda,
retired-file collision handling, legacy/new audit records and explicit override
independence with local fixtures. Exercise public renderer and companion forwarding
with fake drivers; inspect the exact model/effort arguments. Include a no-mutation check
and a second render/check for idempotence. Reuse unchanged focused evidence.

Refresh the portable manifest once code/tests/docs agree. Keep the checked-in baseline
profile only; no experimental persona or mandatory cross-model evaluation is required.
One integration-focused pass and an evidence-backed review of changed routing/migration
behavior suffice; do not rerun the historical full matrix by habit. Native requests or
live quality trials need separately authorized budget and are not a gate for this
configuration change. State precisely when validation stops at rendered/fake-driver
requests rather than runtime serving or quality.

Use an isolated authoring worktree so shared development links do not expose partial
changes. Inspect MASK public capabilities/status/selection and pinned versus development
content; prepare a scoped adoption/rollback handoff using existing commands. Registry
membership is not write authority. `--mask-projects` remains read-only measurement.
A pin is not updated by merely changing canonical bytes. Regenerate adapters only for
explicitly selected consumer roots and after active work is accounted for. Preserve
unrelated user settings, skills, pins and evidence. No mandatory fleet migration.

Record the source revision and previous artifact/adapter selection for rollback. Restore
only clean owned generated artifacts and the expressly selected prior source; refuse
conflicting user edits. Never reset user source, delete reports, rewrite old RFC/card
history, or assume a running agent reloaded. A future usage readout can refine policy
without blocking this owner-directed change now.

## Acceptance criteria

- **RFC-ASK-0009-AC01** — New work uses the broad standard `rfc-worker` by default;
  deep work has an explicit name/reason; risk safeguards and worker difficulty remain
  independent, with ownership, approval and leaf boundaries unchanged.
- **RFC-ASK-0009-AC02** — All seven roles match the target matrix; normal review is
  independently configurable, correct schema/runtime-request values are emitted, and
  unrelated routes, limits, permissions and primary settings are preserved.
- **RFC-ASK-0009-AC03** — Safe migration retires only owned clean obsolete adapters,
  preserves worker addenda and active assignments, refuses conflicts before mutation,
  and leaves repeat/check/rollback behavior truthful.
- **RFC-ASK-0009-AC04** — New and historical role/decision records remain readable and
  distinguishable; the generic worker name is not retroactively relabeled or billed
  from current settings, and existing usage capture behavior is unchanged.
- **RFC-ASK-0009-AC05** — Focused automated and integration checks substantiate the
  configuration/migration contract, portable source is consistent, and observed versus
  untested runtime/quality/cost boundaries are accurately recorded.
- **RFC-ASK-0009-AC06** — Active docs and scoped MASK adoption/rollback guidance agree
  with the target; owner-directed promotion requires no new bakeoff, hidden spend,
  blanket consumer rewrite, extra persistent persona or new orchestration framework.

## Work and closeout

ASK-0043 → ASK-0044 → ASK-0045 → ASK-0046 (provisional until live reservation).
ASK-0046 is the sole closeout; capture the actual immutable RFC_BASE_SHA before source
work. Retain direct criterion/evidence/outcome/revision rows there. No terminal status
until required configuration/migration evidence exists. Optional native serving and
quality/cost measurements must remain clearly unclaimed, not fabricated pass results.

## Owner adjustment and verified closeout

The owner explicitly renamed `rfc-critical-reviewer` to `rfc-reviewer-critical`.
The live target uses that spelling. Migration preserves legacy critical-reviewer
addenda and raw historical identity, retires only clean owned old adapters and
rejects retired new selectors. The retained original pack is unchanged.

Auto-Verified at the configuration/migration acceptance boundary; all six criteria
are recorded on ASK-0046. Native serving/reload, quality equivalence and subscription
savings were not tested or claimed. Consumer adapter rollout remains separately scoped.
