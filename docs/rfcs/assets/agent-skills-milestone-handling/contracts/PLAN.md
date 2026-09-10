# Plan data and runtime boundary

This document supplements the proposed JSON Schema. The RFC is normative when a
prose example is incomplete. Paths/names are proposed implementation seams;
reconcile any newer live equivalent. This is not a production helper shipped here.

## Minimum authoring shape

Required top-level keys: `schema`, `id`, `scope`, `milestones`. `coverage` defaults
to `complete`; `unplanned_work` defaults to `[]`. A partial plan requires a nonempty
`unplanned_work`. Scope contains at least one nonempty `rfcs` or `issues` array.
A milestone needs `id`, `outcome`, `work`, `depends_on`, `exit_criteria`, `boundary`.
The schema is closed; unknown executable/agent/status fields are errors.

A work reference is exactly one of `{issue, criteria?}` or `{rfc, criteria?}`.
Omitted criteria means all applicable obligations. An empty criteria list is
invalid; it must not mean no work. The same whole-document obligation cannot be
assigned twice. Disjoint selectors permit one issue/RFC to span milestones.
Whole-plus-partial overlaps and overlapping selectors are diagnosed. Natural-language
selector equivalence and duplicate RFC-to-card coverage require engineering judgment;
structural equality checks do not prove semantic disjointness.

Relative criterion labels such as `AC01` are preferred when they already exist in
the source. If a criterion includes its full RFC ID, remapping changes that typed
reference explicitly. An ambiguous heading/quote or missing criterion keeps the
assignment unresolved. The plan does not manufacture source acceptance IDs.

A card listed in scope but not covered by milestone work or explicit unplanned
work is a coverage error. An RFC represented by contributing cards must have actual
acceptance coverage reconciled, not simply matching `rfcs` tags. A complete plan
with unresolved semantic coverage may be structurally valid but is not fully
validated. Discovering incomplete coverage repairs the plan under the existing
scope authority; it does not drop requirements or pretend absence of a plan.

## Order and eligibility

Array order is the authored preference among eligible milestones. Dependencies
name hard prerequisites and form an acyclic graph. Do not sort milestone IDs and
thereby replace supplied order. Missing dependencies/cycles/self-edges are errors.
A logically valid non-topological array is allowed: precedence edges govern actual
eligibility; keep the authored preference visible rather than rewriting the array.

Issue dependencies remain operative. Dependencies wholly within a milestone permit
serial implementation within it, not a forced milestone split. A dependency on an
unsatisfied issue in a later milestone requires a consistent milestone relation or
an explained plan correction; do not silently move/omit the dependency. A prerequisite
outside the authorized target is reported rather than implemented without authority.
File-disjointness alone does not prove independence.

Source scopes and runtime mandates differ: an offline pack can cover more than a
later user request. A subset invocation binds a projection of authorized work and
retains necessary ordering. A partial projection cannot accept a whole source
milestone/card. Keep excluded work outside authority and keep blocked dependencies
visible. Do not mutate the broader shared plan merely to describe a one-off subset.

## Three homes for three facts

1. Retained source plan: immutable authored provenance.
2. Adopted live plan: authoritative grouping/intent with remapped references.
3. Existing continuation/assignment: active position, exact producer, evidence and
   current authority; no copied backlog or mutable duplicate card status.

Default adopted location is `<rfc_root>/plans/<plan-id>/milestone-plan.json`.
Cards can point through `metadata.milestone_plan`, e.g. `{id, path}`. Use an existing
consumer convention when available and document it; new consumers should work
without user-written configuration. Plans have no global ID allocator. A conflicting
ID/content requires explicit resolution, not last-writer-wins or silently inventing
another "same" active plan. Live linkage must survive board lane moves and exports.

Amendments use ordinary scoped file edits and Git history plus a compact reason
on the existing continuation. No mandatory event database. Preserve prior IDs where
meaning survives; explicit splits/merges record predecessor mapping and transfer
all unsatisfied obligations. New scope needs the user's authority. Future-only
changes do not force replacement of an unaffected active producer.

## Helper operations and effect limits

Expose existing-style, task-oriented operations over a shared implementation:
discover/check, inspect-current, adopt/remap, render-view, and amendment validation.
The exact CLI can be reconciled with current tools; do not create aliases that each
force a second model turn. Coordinator startup should compose deterministic lookup
and return one compact actionable result.

Checks/inspect/discover/render-to-stdout are observational. An explicit adopt or
render-to-file writes only named, owned local records after stale/collision checks.
Use existing root, atomic file/compare-before-write and board mechanisms. Interrupted
multi-file adoption is detectable and idempotently reconcilable; do not claim atomic
visibility across all records or host readers. No implicit commit, push, fetching,
model dispatch, package script execution or global consumer scan.

Results distinguish structural, reference and semantic coverage; unknown is not pass.
Human mode is useful concise text; `--json` explicitly returns the versioned machine
shape. Bound large reports with continuation indicators. Never hide a truncated
check behind a success result. Plan selection should normally return the current
milestone and small remainder summary, not every card body or full future plan.

## Parsing and identity

Reject duplicate JSON keys, nonfinite values, excessive input, recursive path escapes,
special/linked plan files and unsupported schema versions. Use a reasonable published
runtime input limit (initial proposal: 1 MiB and 256 milestones) and refuse with an
actionable message, not silent truncation. This is accidental/malformed-input
protection, not a sandbox for hostile same-user programs.

Normalize omitted defaults before hashing. Canonical parsed JSON with sorted object
keys, preserved array order and UTF-8 strings is enough for a definition fingerprint;
no claim of an external canonical-JSON standard is required. JSON whitespace is not
a grouping change. The source provenance can separately hash original file bytes.
Generated MILESTONES.md must be deterministic and checkable against the JSON.

An assignment binds the selected plan/milestone definition and resolved requirement
projection. Source requirement edits can invalidate obligations even if the plan
JSON is unchanged. Compare relevant inputs rather than every unrelated HEAD change.
Runtime computes/binds these identities without user-facing hash-copying ceremony.

## Legacy and incomplete inputs

Legacy Markdown or structured stage mappings are supported without a universal
Markdown grammar. Discovery returns the exact source reference; the first integrator
normalizes once, preserves intended membership/order/outcomes and records ambiguity
or omissions. Material supplied contradictions are surfaced; harmless omissions can
be resolved within scope. Never fall back to card-at-a-time because a file name or
format differs from the new convention.

A partial plan retains authored milestones and uses explicit unplanned obligations
for the remainder. Before executing newly formed work, persist its current definition
and coverage. A small planless target needs one small plan, not a planning RFC.
Status/review/usage-only queries do not create plans. No author-side script execution
is required for a plan to be eligible for runtime adoption.
