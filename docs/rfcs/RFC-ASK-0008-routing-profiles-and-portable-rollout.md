---
id: "RFC-ASK-0008"
title: "Routing profiles, compact instructions and portable rollout"
status: "Implementing"
owner: "MikeMarcin"
created: "2026-09-07"
---

# RFC-ASK-0008: Routing profiles, compact instructions and portable rollout

Live IDs were reserved and imported; the retained pack is immutable provenance.
This is a new RFC, not an amendment silently rewriting settled RFC-ASK-0001–0004.

## Decision

Separate semantic role, execution topology, model/effort profile and available
account capacity. Do not treat a capability class or effort word as a permanent
model-independent quality ranking. Introduce explicit experimental profiles without
silently changing every user's main session or every project selecting this skill.

The first deployment makes report delivery reliable and collection usable. Keep
routing fixed during the runner comparison. Ship an explicit `astra-low-first`
candidate profile and retain the current baseline. Promotion follows a recorded
bounded experiment and owner decision, not a leaderboard score or the number of
times a role ran.

## Preserve current roles and decouple policy changes

The supplied source uses utility, scout, routine worker, deep worker, **test-runner**,
reviewer and critical reviewer. Keep those names; a new `worker-skilled` persona is
unnecessary. `rfc-worker-routine` is the established-pattern path; `rfc-worker` is
the deeper implementation path. Utility is mechanical inventory, not interpreting
access-control correctness or selecting an architectural example.

A plan can remain entirely in the integrator when delegation does not replace work,
isolate substantial context, or yield independent evidence. An Astra-low child of
an Astra-low integrator is not a cheaper model route merely because it is a child.
A deterministic runner has no model/effort and must not be counted as an extra
reasoning role. A small-model execution bridge is optional only where the native
host requires one; account for it and label that it is not inference-free control.

Proposed Codex profiles, subject to installed model capability:

| Responsibility | Existing baseline in uploaded source | Low-first candidate |
|---|---|---|
| Main integrator | Existing explicit user/session selection | Astra low when explicitly selected for ordinary work |
| Utility | Luna xhigh | Unchanged initially |
| Scout | Sol low | Unchanged initially; evaluate separately |
| Routine worker | Sol high | Astra low |
| Deep worker | Astra high | Astra high |
| Test-runner agent | Luna xhigh | Unchanged; prefer direct command batching |
| Reviewer | Astra high | Astra high |
| Critical reviewer | Astra xhigh | Astra xhigh |

The existing `deep` route is shared by worker and reviewer. Do not lower this class
to implement a routine-worker experiment. Extend assignments/profiles so roles can
vary independently while preserving backwards compatibility with the current
routing document. Profiles include a digest and experiment label; renderer output
records requested settings. A runtime observation remains the stronger statement
about what actually served a request. Freeze model IDs from the live configuration;
never invent a provider model identifier when a capability lookup fails.

Recommended precedence: explicit user task/session selection, explicit admitted
work-order route, selected profile, then existing shared baseline. Project context
remains project facts; do not turn `.mask/skill-config/.../project.json` into an
unbounded arbitrary command/model override channel. A profile selection may live in
an explicitly documented generated runtime selection file or invocation option;
make its consumer-scoped effect and lifetime clear. Renderer must not overwrite
unrelated native settings or operate through a shared symlink destination.

### Concrete configuration placement

Keep current `config/routing.json` as the baseline authority and add shared
`config/routing-profiles.json` (`implement-rfc.routing-profiles.v1`) with bounded
per-provider/per-role overrides. The sample candidate overrides only
`rfc-worker-routine`; its integrator setting is a recommendation until an explicit
session selection. Add an explicit renderer `--profile` selector; absent means
`baseline`.

Persist an operator-selected mode/profile/experiment only in consumer-generated
`.mask/generated/implement-rfc/execution-selection.json` using
`implement-rfc.execution-selection.v1`; absence means direct mode and baseline.
An explicit invocation overrides this local selection. Keep this outside
project.json's project-facts contract and outside shared installed content.
Configuring the selection is an explicit runner/config helper action, never a
side effect of capture, reading the skill or discovering a registry.

## Escalation and fallback

Select deep work for known unresolved architecture, consequential invariants,
subtle concurrency/security/persistence reasoning, contradictory evidence, or a
substantive unsuccessful bounded attempt. The integrator can select deep immediately
where warranted. A single ordinary failing test is not automatic escalation; fixing
straightforward implementation errors remains part of routine work.

Differentiate runtime unavailability, model-specific quota exhaustion, shared quota
exhaustion, authentication/permissions, request-size errors and task difficulty.
Task difficulty can justify stronger reasoning. Quota errors cannot.

A fallback policy names exact approved provider/model/effort alternatives, task
risk floor, permission/billing boundary, maximum attempts and approval scope. Record
requested route, actual refusal/limit event, alternative approval and subsequent
observed serving route. Synthetic/error messages are not unidentified model work.
Missing effort, unsupported effort and actual `none` are separate values.

For Claude Fable exhaustion, an Opus alternative may be offered only when it meets
the preapproved capability floor and the relevant allowance is available. Ask once
per selected run when the substitution lowers the agreed review/effort condition,
changes provider/data handling or paid usage. Never assume model-name substitution
escapes a shared account limit. Vendor-native fallback settings must be checked for
the actual error classes they handle; a server-unavailability fallback is not a
subscription-exhaustion policy. Preserve partial results when no approved capacity
exists. Never redeem reset tokens or buy credits automatically.

## Leaf roles, reporting and compact instruction loading

Remove nested agent tools from delegated roles by default, rather than merely
replacing `Agent(rfc-utility)` text while leaving an unrestricted Agent capability.
A driver that cannot enforce this reports policy-only enforcement and uses the
supported direct/runner path; it cannot claim a security guarantee. Keep explicit
reader/writer and build-artifact restrictions. The main integrator can commission
bounded independent siblings with runner-owned delivery.

Apply writing-for-agents as an authoring review, not another runtime prompt to
load. Keep the mandatory skill core short and branch-specific procedures behind
clear triggers. Do not convert an explicit correctness requirement into a catchy
adjective or remove uncertainty to shorten a report. Required runtime data:
assignment boundary, relevant sources/revision, ownership, constraints, verification
and expected handoff. Avoid dumping the parent conversation or every RFC asset
into each utility/test-runner context.

Use one authoritative dispatch receipt instead of repeated startup/final role
banners **only after** parser/report compatibility and provenance are in place.
Retain legacy banner parsing as self-report metadata. Report path roots once;
repo-relative paths plus revision/symbol/line evidence normally suffice internally.
Absolute paths remain appropriate when explicitly requested or crossing roots.
Avoid redundant “I will/Completed/No proposals” prose, but do not use the savings
from a few sentences to obscure repeated context or abandoned assignments.

Existing project instructions, user constraints, approved design and evidence
requirements remain authoritative. Test load-path changes by checking the actual
instructions presented to the worker, not by summing every Markdown file on disk.
Record stable-prefix/cache conditions for comparisons. Integration may condense its
own checkpoint context, but acceptance must retain original evidence references
and unresolved facts rather than trusting a lossy confident summary.

## Portable distribution and rollback

All reusable logic belongs in AgentSkills `skills/implement-rfc`. MASK manages its
source, selected artifacts, bindings and per-agent targets. Do not add a new global
manager, per-project fork, hidden pack runtime dependency, or edits to MASK internals.
The currently supplied MASK supports both shared/development links and pinned
artifacts; changing canonical files alone does not prove a pinned consumer changed.

First qualify canonical helper invocation, then one MASK-linked consumer for each
provider, then the two experimental projects. Existing registry membership is
not approval to deploy: **`usage.py --mask-projects` remains read-only collection**.
Consumer enablement and updates use explicit existing MASK public plan/apply/source
flows with exact selected roots and guard hashes, independently of capture scope.
Do not auto-update all registered projects, start new agents, replace user configs,
publish repositories, or imply host first-prompt loading from successful symlinks.

Keep a reversible baseline profile and record previous source/artifact selection.
Disable runner/profile selection prospectively; preserve evidence, partially
completed work and durable reports. Never roll back by resetting user source edits
or deleting history. Native CLI adaptation cannot be rolled back merely by restoring
a Markdown role file; compare generated settings and retained runtime capabilities.

## Qualification and decision rule

Automated safety fixtures must pass before a live budget is consumed. A narrow live
comparison captures all-in context/requests/latency, result delivery, semantic
acceptance, human repair and later reopening. Runner acceptance requires fewer
model-mediated predetermined transitions and no lost/doubled work; it does not
require a predetermined percentage quota win. Candidate routing remains opt-in
unless the owner accepts its measured quality/cost tradeoff. “Inconclusive, retain
baseline” is a successful evaluation outcome, not permission to invent evidence.

Evaluate instruction changes separately from topology and route. A serious missed
acceptance invariant stops promotion and creates a bounded defect card; do not
change the oracle to make the candidate pass. Report task difficulty and cache/
service-tier conditions so route selection bias does not masquerade as a result.

The final readout is one compact comparison and deployment decision, linked to
existing cards/evidence. Do not add an exhaustive recurring audit, mandatory
cross-model review for every tiny slice, or a proof-of-proof archive. Required
native claims stay open until exercised; a packet or Linux fixture pass cannot
close native macOS/Windows/host-runtime acceptance.

## Acceptance criteria

- **RFC-ASK-0008-AC01** — Baseline and low-first profiles preserve explicit user authority, select routine/deep work deliberately and decouple worker changes from reviewer settings without inventing new personas.
- **RFC-ASK-0008-AC02** — Fallback/escalation receipts distinguish task difficulty, quota, unavailability and actual serving routes; capability or billing changes require scoped approval and no reset/credit action is automated.
- **RFC-ASK-0008-AC03** — Delegated roles default to leaves with truthful enforcement claims; legacy roles/banners remain analysable and test-runner authority stays mechanical.
- **RFC-ASK-0008-AC04** — Compact progressive-disclosure instructions preserve original constraints, acceptance and uncertainty while avoiding mandatory duplicated provenance or broad context injection.
- **RFC-ASK-0008-AC05** — Canonical and MASK-managed adoption is scoped and reversible, respects pinned artifacts and unrelated settings, and never treats --mask-projects collection as deployment authority.
- **RFC-ASK-0008-AC06** — A bounded, separately attributed runner/routing/instruction evaluation records quality, all-in cost and actual limitations; promotion or retention/rollback is an explicit evidence-based owner decision.

## Implementation authorization

Accepted for implementation by the owner’s import-and-implement request on 2026-09-07. Native and owner-decision criteria remain open until exercised.
