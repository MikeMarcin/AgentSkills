---
id: "RFC-ASK-0007"
title: "Reconciled usage accounting, account limits and task outcomes"
status: "Proposed"
owner: "MikeMarcin"
created: "2026-09-07"
---

# RFC-ASK-0007: Reconciled usage accounting, account limits and task outcomes

Pack IDs are provisional until the AgentSkills integrator reserves the live block.
This is a new RFC, not an amendment silently rewriting settled RFC-ASK-0001–0004.

## Decision

Build a small offline reporting layer over RFC-ASK-0006 captures and RFC-ASK-0005
execution receipts. Retain historical v1 audit archives. Report four distinct
views: **activity**, **observed runtime consumption**, **estimated price-equivalent
cost**, and **account allowance/credits**. Join outcomes to tasks to expose all-in
cost per accepted slice. Do not collapse these into a synthetic subscription meter.

The provided historical measurement is a baseline, not a controlled model trial.
Its high orchestration share identifies an opportunity; it neither guarantees a
saving nor proves that particular engineering work was wasted. The new runner must
record useful result delivery, not merely reduce visible text or tool-call counts.

## Accounting identities and attribution

Use a normalized local execution/request ledger with nullable `project`, `run`,
`slice`, `task`, `attempt`, `provider_account_alias`, `device_alias`, `native_session`,
`native_turn`, `response_id`, and `usage_epoch`. Every attribution has an evidence
basis and uncertainty. A top-level session can be companion work; “primary” is not
synonymous with integrator. Multiple assignments may share a session; never allocate
its entire lifetime to its last role banner. Retain unassigned work explicitly.

Requests belong once in the ledger. Presentation may group by logical project,
physical worktree, role, model/effort, task, or orchestrator versus child activity,
but totals cannot double-count an event across those dimensions. Git common-dir
groups do not merge independent clones. Across devices, request IDs when trustworthy
can deduplicate copied transcripts; otherwise show possible duplicates and bounds.
No equality inference from token totals alone.

### Claude reconciler

Deduplicate streamed assistant fragments by native response/message ID within the
appropriate session/provider identity. Request-level input/cache counters and final
run aggregates have different semantics. Do not add cache-creation categories twice,
count final output placeholders as final totals, or add a harness `totalTokens`
footprint to per-request usage. Use a genuine final aggregate only at the scope it
measures, with a non-overlap rule. If output cannot be recovered reliably, report
input/cache observations plus `output_incomplete`; do not compute a precise total
or bill by guessing. Retain synthetic errors separately from serving-model work.

### Codex reconciler

Keep input, cached-input subset, output and reasoning-output subset explicit. An
input total that already includes cached input is partitioned, not increased by
cached input. Reasoning already inside output is not added a second time.

Reconcile `last_token_usage` with a monotonic cumulative series in the same ownership
and epoch. Repeated snapshots do not create new requests. Establish a pre-window
baseline; an absent baseline yields a partial interval rather than charging the
entire first cumulative total. Counter reset/decrease, compaction and fork/inherited
history require explicit boundaries; compaction does not automatically imply a new
billable epoch. A cumulative delta spanning multiple unidentified requests may be
reported as an aggregate, not invented exact requests. Keep negative/conflicting
observations as anomalies rather than clamp-to-zero correctness.

Child histories with inherited usage require exact ownership evidence or an
`ownership_uncertain` subtotal excluded from exact totals. Native context model and
effort fields describe configuration unless the runtime attests the serving route.
A matched requested route is not proof of fallback causality or historical routing
correctness. An analysis update may revise a classification while preserving input
capture bytes and recording the parser version.

## Cost and allowance are different

An optional versioned local rate card contains provider, model identity, currency
or credit unit, uncached/cached input/output rates, service-tier multiplier,
effective interval and source reference. Explicitly distinguish **historical-rate
estimate** from **current-rate counterfactual**. Unknown model/rate/tier yields an
unknown or clearly bounded amount; no API-equivalent dollar number is labelled
subscription spend. Do not ship a rate fetcher that silently changes old reports.
Use decimal arithmetic and test cache partitions and category inclusion.

Native account snapshots contain the provider/account alias, observed time,
provider sample time/freshness where available, opaque pool ID, window duration,
reset instant, used percentage and actual credit balance where exposed. Preserve
opaque pool names; do not map an undocumented pool to a model based on its nickname.
A balance difference can reflect purchases/credits/refunds/concurrent activity and
is not automatically a project's debit. A zero balance is not the same as a zero
included quota. Missing windows are unknown, not zero.

Bundled `usage_quota.py codex` uses only the installed authenticated CLI app-server
read endpoint. It initializes and requests account limits; it must not create a
thread/turn, redeem resets, install hooks, refresh external credentials, or approve
any tool request. Fail closed on unrecognized interactive requests. Native CLI
implementation may contact its provider to read the account; this is explicit and
separate from offline `usage.py`.

`usage_quota.py claude-stdin` accepts a supported native status-line payload and
writes an allowlisted snapshot. Composition with an existing status line is an
optional documented integration, never an overwrite. Manual snapshots support
providers/versions without a usable native field and clearly record manual
provenance. Capability-test installed versions and never invent an endpoint from
these examples. The seed's `data_freshness` is deliberately conservative.

Join snapshots to project experiments only when account, pool and reset epoch match
and concurrent activity is controlled or explicitly measured. Fractional quotas
have rounding, lag and sometimes overlapping windows. Do not apportion a multi-device
allowance decrement by role call share or raw token share. The normal report shows
project consumption and account constraints side by side, not falsely reconciled.

## Delivered outcomes and control overhead

Capture task dispatch, execution completion, report produced, report collected,
accepted/rejected/superseded/reopened and human repair as separate observations.
Keep engineering judgment in the existing acceptance record. A tiny derived event
or explicit link is sufficient; no duplicated acceptance form for every task.
The runner generates operational events automatically; direct work may have an
optional explicit assignment wrapper or remain honestly unassigned.

Include primary plus children, recovery, failed attempts, review and integration
repair in all-in comparisons. Denominator is accepted work at the stated boundary,
not session count or “agent finished.” Retain zero accepted-task cases without
division by zero. Reopened defects update the comparison; do not hide them because
the original run completed. Human repair minutes are user-entered/observed, not
inferred from silence between messages.

Classify waiting/listing separately from spawning/messaging. Associate a control
request's observed token footprint with its call where the join is exact, but
label mixed engineering+control requests. Waiting wall time is not continuous
reasoning time. Wrapper and nested call counts cannot both inflate saved-request
claims. Unknown nested `exec` operations stay unknown. Show model wake-ups, useful
handoffs, incomplete reports, recovery yields, duplicate examination candidates,
scan overhead and rate coverage; none alone is a quality score.

## Report surface

Add a single offline `scripts/usage_report.py` helper:

```text
usage_report.py CAPTURE.zip [CAPTURE.zip ...] --out DIRECTORY
usage_report.py BASELINE.zip CANDIDATE.zip --compare --out DIRECTORY
```

Produce a readable `REPORT.md`, `summary.json` and compact CSVs for selected
aggregation dimensions. No spreadsheet or database server is required. Reject
archive path traversal, duplicate entries, decompression bombs and hash mismatches;
read members without extracting to arbitrary paths. Offline reports include
coverage/error sections even when no usage was captured. Default tables separate
exact/reconciled, aggregate-only and unknown quantities. A support archive alone
does not prove quality, spend attribution or live provider availability.

Performance work should reuse stdlib parsing/indexes. Prefer an existing trusted
meter's authoritative exposed observations over inventing a private billing model,
but keep this workflow usable without installing a separate dashboard. Unknown
future fields remain available only through allowlisted schema updates.

## Evaluation contract

Operational safety repairs apply to all arms; do not intentionally abandon agents
in a control arm. Begin with runner versus current native coordination holding
model routes, task/revision, reviewer policy and context packet constant. Count
planning and integration overhead in both arms. Then compare routine Sol high with
Astra low while topology/review stay fixed. Finally measure instruction refactoring
without changing the selected route. Use explicit cohort/treatment IDs and source,
role/routing, capability and instruction digests.

A pilot of about 12 representative bounded tasks is a screening experiment, not a
statistically powered safety claim. Include independent acceptance, seeded failure
cases, counterbalanced order, cold/warm cache labels, controlled service tiers and
a user-approved quota/time ceiling before live work. Avoid duplicate mutations in
a real project by using isolated snapshots. Known difficult/high-risk work may
select the stronger profile immediately; routine failure is not artificially
forced for experimental symmetry.

Report inconclusive outcomes honestly. Shipping trustworthy collection and an
experiment does not require demonstrating a win. A regression or no saving is a
valid result and can justify leaving the candidate off. Promotion criteria and
rollback belong to RFC-ASK-0008, not a fitted threshold invented after results.

## Acceptance criteria

- **RFC-ASK-0007-AC01** — Claude fragments/aggregates and Codex snapshots/counter epochs/forks reconcile without double counting; unknown/missing/conflicting consumption is explicitly excluded or bounded.
- **RFC-ASK-0007-AC02** — Optional rate-card estimates preserve category inclusion, effective dates and service tiers and are never labelled actual subscription percentages or credit debits.
- **RFC-ASK-0007-AC03** — Native/manual quota helpers capture only allowed account observations with identity and freshness; they never start model work, buy credits, redeem resets or silently repair authentication.
- **RFC-ASK-0007-AC04** — Task/attempt joins distinguish delivered, collected, accepted and reopened work; all-in comparisons include primary, child, retry, recovery, review and repair while retaining unassigned work.
- **RFC-ASK-0007-AC05** — Offline v1/v2 archive reports validate privacy/integrity/bounds and expose partial coverage, opaque pools, overlapping-account activity and uncertainty instead of false exact totals.
- **RFC-ASK-0007-AC06** — Controlled runner, routing and instruction experiments have separate treatment IDs, fixed comparison conditions, explicit spend ceilings, independent acceptance and an honest inconclusive outcome.
