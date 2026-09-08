# Portable Delegated Execution

Use this reference only when bounded delegation will reduce primary-context
load, improve elapsed throughput, isolate writable test output, or add a
meaningfully independent check. Delegation is optional; agent count is not a
quality metric.

## Authority

The primary RFC integrator alone owns:

- interpretation of the live RFC, architecture decisions, and acceptance criteria;
- `RFC_BASE_SHA`, issue allocation, board transitions, and RFC ordering;
- staging, commits, pushes, and integration;
- verification sufficiency, documentation impact, and RFC status.

A delegated result is an input. It cannot expand acceptance, move cards, commit,
or close an RFC.

## Roles

### `rfc-utility`

Use for exact locating, inventories, prescribed read-only commands, schema or
adapter drift checks, and log condensation. Promote to `rfc-scout` when the
task requires semantic interpretation.

### `rfc-scout`

Use for bounded ownership, execution-path, package-selection,
verification-surface, documentation-impact, or first-cause analysis. A scout
should replace the corresponding broad primary scan; the primary confirms only
material conclusions.

### `rfc-worker`

Use for one current issue-card slice after ownership, non-goals, acceptance
criteria, and focused verification are clear. Give an exclusive file/path
scope. Only one agent writes a shared checkout at a time. The worker does not
commit or mutate tracker/RFC state.

### `rfc-worker-routine`

Use the worker contract above when the assignment supplies an established
approach, an existing repository pattern, exclusive ownership, and direct
verification. Exclude new or changed sensitive protocol, persistence, authority,
concurrency, lifetime, and destructive-migration behavior. If the assignment
exceeds these boundaries, return current progress and the reason for reassignment
to the primary; do not stretch the routine role or repeatedly retry it.

### `rfc-test-runner`

Use when an exact selected command set benefits from separate execution or a
writable build root. Isolation is optional unless the user explicitly requires
it or a concrete collision/source-integrity risk makes it useful.

The test runner:

- executes only supplied commands against the named candidate and output roots;
- may write disposable build/test outputs, but never source, agent documentation,
  trackers, RFCs, manifests, or generated repository files;
- reports each command's outcome, failures, skipped tests, incomplete runs,
  unexpected conditions, relevant diagnostics, artifacts, and uncertainties;
- never diagnoses root cause, chooses extra tests, classifies acceptance blockers,
  modifies commands to obtain a pass, or suppresses apparently unrelated failures;
- returns unsupplied decisions to the primary and does not spawn other agents or
  create seals, hash-bound evidence packages, or replay records.

The primary selects verification and judges acceptance. Scouts investigate
failures; reviewers examine whether recorded evidence can miss a broken claim.

The primary consumes the result and reruns only a check affected by a later
correction. It does not repeat unchanged passing commands.

### `rfc-reviewer` And `rfc-critical-reviewer`

Use an independent reviewer when explicitly requested or when it is likely to
add discriminating evidence for a changed wire/protocol contract,
persistence/migration behavior, authority/security boundary, concurrency
primitive, or destructive migration. Use the critical role when the risk and
expected value justify deeper counterexample search.

Give the reviewer the live acceptance criteria, final bounded diff, commands
already run, and concise result locations. Do not preload the implementation
transcript or ask it to ratify the implementation narrative.

Use one reviewer by default, preferring the opposite model family from the
implementation when available. The critical role replaces the ordinary role for
a named material risk. A second review requires an unresolved material concern
or an explicit request; see [model-routing.md](model-routing.md) and the lane
mechanics in [codex-lanes.md](codex-lanes.md).

A blocking finding must be an evidence-backed failure of an existing acceptance
criterion or a critical regression in the changed surface. Unsupported
suspicions, broader hardening, alternate designs, and requirement expansion are
non-blocking and become follow-up candidates. A correction receives only a
narrow changed-surface recheck; it never starts a whole-candidate review loop.

## Choosing Delegation

| Work shape | Default |
|---|---|
| Small, directly verifiable change | Primary agent |
| Substantial mechanical read-only inventory or commands | Optional `rfc-utility` |
| Bounded semantic repository investigation | Optional `rfc-scout` |
| Established approach and pattern with direct verification | Optional `rfc-worker-routine` |
| Other bounded implementation slice | Optional `rfc-worker` |
| Exact separate test/build command set | Optional `rfc-test-runner` |
| Named high-risk trigger or explicit request | Consider one reviewer |
| Missing safe runtime capability | Execute serially in the primary agent |

For substantial implementation selected for delegation, make the routine/deep
choice before dispatch. Prefer `rfc-worker-routine` when its prerequisites hold;
otherwise use `rfc-worker` and name the unresolved design or sensitive behavior.
Do not treat the generic worker as the default merely because it appears first.
Put one short line in the assignment: `Routing: routine | Reason: <concrete reason>`
or `Routing: deep | Reason: <concrete reason>`. Ask the worker to repeat this
line after its startup identity and in its final Status so either driver retains
the decision in normal session history. If reassignment is needed, record
the new choice and reason rather than rewriting the earlier decision. This is
an assignment decision, not a quota, mandatory agent pipeline or acceptance gate.

Delegated roles are leaves by default. Commission independent siblings from the
primary when needed; do not add unrestricted Agent tooling to a leaf. Inspect
the driver capability before claiming enforcement rather than policy alone.

Run trivial deterministic commands directly. Workers normally run their own
focused checks; there is no mandatory scout/worker/test-runner/reviewer pipeline.

Parallel read-only agents must own different questions. Do not request duplicate
same-prompt scans merely to obtain a vote. Stop delegation after it has answered
the bounded question.

## Assignment Contract

Name the role and purpose, then provide only what the role needs. The following
packet is the actual context boundary: link relevant source and original evidence,
include applicable constraints verbatim, and leave unsearched facts explicit.
Do not attach the parent transcript, every RFC, retained import assets, or a full
board dump. Read a linked procedure only when the selected action needs it.
Mechanical inventory cannot resolve architecture or authorization questions.

For example, a utility packet names exact paths/search terms and asks for matches;
a test-runner packet names exact argv, candidate and disposable output roots;
a semantic investigation uses a scout with a bounded question and acceptance
references. Do not silently promote a utility because its output is convenient.

Name each root once; internal evidence may use repo-relative paths plus revision,
symbol and line. Use absolute paths when crossing roots or when requested.

Assignment fields:

```text
Role and purpose:
Routing: routine or deep | Reason: concrete reason (implementation workers only)
Current card or review target:
Repository root and branch/candidate:
Question or acceptance claims:
Allowed paths or roots:
Explicit non-goals:
Applicable instructions:
Exact commands or evidence:
Requested result:
```

Use a role-prefixed runtime name such as `rfc_scout_backend_selection` or
`rfc_utility_cache_inventory`. For adapters without an authoritative compatible dispatch receipt, retain the startup banner
`Role: <role> | Model: <model> | Effort: <effort>` before analysis so routing
mistakes are visible. Role-to-model assignment and its rationale live in
[model-routing.md](model-routing.md) and `config/routing.json`.

For workers, state that they must not commit, move cards, allocate IDs, or
change RFC status. For test runners, name the candidate, exact commands, writable
output root if any, and expected concise result.

## Result Contract

Use the role-specific compact format in `config/roles.json`. Every result
should:

- lead with status or blocking failures;
- cite exact paths, symbols, commands, and result locations;
- distinguish fact, uncertainty, and unsearched surfaces;
- avoid raw logs, copied RFC prose, and broad repository summaries.

Unexpected source writes invalidate a read-only or test-runner result. Preserve
unrelated user changes and inspect Git state after delegated work.

## Runtime Fallback

When an adapter, nested agent, read-only sandbox, or per-role model is
unavailable, perform the bounded work serially while preserving the same
acceptance boundary. A fallback may reduce speed or independence; it does not
create new verification requirements. Report the omitted optional lane without
blocking closeout.

Use the optional [local routing audit](routing-audit.md) to count observed role
usage in either driver and inspect recorded decisions. Missing historical reasons
remain unknown; a startup banner alone is not runtime model evidence.

## Receipt and profile compatibility

Baseline `config/routing.json` remains the shared default. Explicit task/session
selection wins over an admitted order route, selected profile and baseline.
The former `astra-low-first` candidate is now the shared baseline; its separate
profile has been removed. Future explicit profile overrides require verified
capabilities. The capability file maps provider to exact model to supported effort
values; it is an operator-supplied observation, not provider discovery. A missing
capability refuses the override. No profile changes the primary session.

The runtime-adapters manifest records requested settings, profile digest and
experiment label. Driver dispatch receipts establish owned attempts; observed
serving data is stronger than requests. Legacy role banners remain self-report
metadata. Keep startup/final banners for the current interactive adapters until
their receipt-aware parser and report path are qualified; do not silently replace
that compatibility contract merely to reduce prose.

`fallback_receipt` validates an explicit alternative and bounded approval scope;
it never executes a fallback. Unknown effort, unsupported effort, actual `none`,
synthetic errors, availability and model/shared quota are distinct. Capacity
errors do not justify stronger reasoning. No automatic credit purchase or reset.
