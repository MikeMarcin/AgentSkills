# Milestone result and context continuation

The existing run/dispatch/producer/mandate/ownership fields and independent-review
relay remain. Introduce a versioned extension, proposed v2, after inspecting live
history. Do not append incompatible fields to a closed v1 object and call it v1.
The packet specifies the required semantics; the implementing agent reuses the live
serialization and runtime adapters rather than starting a parallel orchestrator.

## Assignment binding

Retain exact native child identity, consumer/root/branch, route and permission
scope. Add a plan binding with adopted plan path/ID, definition identity, milestone
ID and resolved obligation-set identity. A worker receives only its authorized
subset. The assignment's definition is immutable for that dispatch.

The local continuation links the binding and stores actual producer/generation
records already needed for recovery. The authored plan stores none of them. A native
same-context resume receives a new dispatch ID and refreshed candidate/path authority;
it does not silently carry write ownership from any previous task.

For prep-and-execute with no usable plan, the initial assignment explicitly grants
bounded planning within the known mandate. The first integrator writes the adopted
current milestone/binding before source implementation and continues in its same
context. The coordinator can consume the binding on the normal result; no extra
planning-only producer or mandatory approval turn. A material scope question still
returns to the user. File-helper validation does not grant new authority.

## Two separate decisions

A logical result reports work disposition: completed milestone, partial, pending
human decision, blocked, cancelled, complete target or the existing review relay.
Its explicit continuation request is `continue`, `fresh`, `wait` or `stop`, with
the intended next milestone (or the same unfinished milestone), reason and evidence
pointers. Exact spelling may follow the live versioned contract; do not infer the
context action solely from disposition or a prose heading.

| Observation | Required control behavior |
|---|---|
| Intermediate card/commit/heading; obligations remain | Continue current integrator; no terminal milestone claim |
| Partial native invocation; useful context available | Resume same native identity with renewed dispatch, if host supports it |
| Selected substantial milestone accepted; next eligible outcome exists | Normally fresh integrator, naming that actual boundary |
| Accepted milestone plus small tightly related next outcome | May continue same integrator with explicit reason and renewed authority |
| Context pressure/unavailable producer before acceptance | Account for old effects, then fresh recovery assignment for unchanged unsatisfied scope |
| Plan replan changes current obligations | Reconcile/renew assignment; preserve pending work, never relabel it complete |
| Human/native criterion pending | Keep it pending; use independently eligible work only, after safe release |
| Active/unknown old writer or commands | Wait/reconcile; do not launch overlapping replacement |
| Duplicate or stale result | Consume once/ignore stale; no next spawn or duplicated acceptance |
| Cancellation | Stop task-owned work safely and preserve; do not resume automatically |
| Entire selected target actually accepted | Close out; no administrative successor |
| Required review relay | Existing qualified native relay, then same integrator adjudicates |

Reason categories can be compact: integrated-boundary, related-continuation,
context-pressure, producer-unavailable, ownership-recovery, explicit-user-request.
Each records the concrete current fact; choosing a category string is not sufficient
justification. `card-done`, `commit-created`, `M2-heading`, `pack-opened` and an
unexplained generation limit are not valid replacement reasons. No minimum/maximum
generation count is imposed on arbitrary real work.

## Completion checks

The control helper compares the return to the assignment's actual binding, not
only a textual milestone ID. It checks all assigned obligations and exit criteria
are accounted for by relevant acceptance records, plus evidence references and
current ownership observations. Engineering relevance/truth is still the integrator's
judgment; the helper must keep that limitation visible.

A "complete" claim with a missing obligation is rejected for clarification or
reconciliation, not converted into a spawn. Required pending evidence prevents
acceptance of that scope. For a partial-card projection, the whole card may stay
open; for a finished set of cards, a composed integration criterion may still be
missing. These are separate cases and tests must cover both.

Safe replacement requires known inactive/quiescent or explicitly transferred producer,
children and commands, and reconciled actual working state. Native completion alone
may not establish descendants stopped; the data contract must not pretend it does.
No blind command replay after a lost acknowledgement. Preserve stale-result,
cancellation, repeated-no-progress and duplicate consumption guards already present.

## Revisions and compatibility

Compute identities automatically. An unchanged active milestone can finish against
its bound definition even when an unrelated future milestone was amended, provided
mandate, requirements, prerequisites and effects still match. An affected edit requires
new explicit assignment identity and acknowledgement; never accept an old response
as proof of newly added criteria. Successful helper execution is not that acknowledgement.

V1 logs remain historical input. New plan-aware continuation cannot silently
reinterpret an old `milestone-complete` as current binding/acceptance. Recover one
small binding from the live mandate/plan/evidence with the existing producer where
possible; otherwise report a genuine capability/recovery limitation. Do not bulk
rewrite old return files or replace active sessions merely to upgrade the schema.

## Economics and diagnostic trace

Record plan/milestone, dispatch/native producer and a concrete replacement reason
in the existing run record. Repeated same-producer dispatches are not generations;
failed launches are separate attempts; unknown historical causes stay unknown.
Report unexplained/card-driven replacements, not a blanket warning for two generations.

Do not convert response count or cached input into an account debit. Include failed
attempts, workers, reviews and repairs in any later cost study; join accepted outcomes
before claiming efficiency. This RFC needs lifecycle correctness and compact
observability, not a new benchmark system or a quota target hidden in acceptance.
