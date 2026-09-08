# Focused acceptance matrix

A pack check verifies internal documents/examples/code fixtures, not live product
acceptance. Reuse unchanged results; run tests at the boundary a claim actually names.

| Boundary | Essential cases | Governing criteria |
|---|---|---|
| Root inference | Nested cwd, installed symlink elsewhere, nearest declaration, nested repo, missing root, explicit override | 0006 AC01–02 |
| MASK public selection | Actual envelope, root_identity, unavailable row, duplicate/root replacement, empty list, custom home, failure/no wider fallback, Windows launcher | 0006 AC02, AC06 |
| History streaming | Large files, oversized line, active append, torn tail, copied file, malformed record, outside scope, uncertain child ownership | 0006 AC03–05 |
| Privacy/package | Secret/source sentinels, unknown fields, no auth files, read-only package, no bytecode mutation, existing ZIP and symlink preservation | 0006 AC05–06 |
| Accounting | Claude fragments/inclusive aggregate, Codex last/cumulative/subsets/forks/resets, absent baseline, missing rate/tier, opaque pools | 0007 AC01–03 |
| Outcomes/report | Collected-not-accepted, partial recovery, reused session/multiple assignments, rework/reopen, zero accepted, mixed accounts, archive bombs | 0007 AC04–06 |
| Prescribed execution | argv exactness, relevant candidate preconditions, failed/empty test, unrelated dirty files, no automatic semantic acceptance | 0005 AC01–02, AC06 |
| Durable ownership | Crash-before/after-dispatch, duplicate completion, wrong session/turn, child result before/after parent stop, cancellation races | 0005 AC03–04 |
| Native adapter | Actual permission/auth/route, no model polling, bounded events, unsupported resume ID, quota exhaustion, exact installed capabilities | 0005 AC05 |
| Policy/context | Explicit user selection, independent routine/review routes, leaf enforcement truth, compact packets retaining uncertainty, fallback floor | 0008 AC01–04 |
| Distribution/evaluation | Real pin/dev-link, two contexts, reversible pilot, no implicit update-all, separate cohorts, negative/inconclusive decision | 0008 AC05–06 |

## Experiment stop conditions

Stop the affected branch on unauthorized effects, silent repeated mutation, lost
result ownership, acceptance-oracle weakening, unexpected paid billing or serious
semantic regression. Preserve findings and classify the failure. An unresolved
native platform is blocked, not a reason to falsify evidence. A lack of measured
savings is not failure of an honestly implemented comparison tool.

## Resource qualification

Measure the collector on a synthetic many-session/large-line fixture and a real
retained-history sample. Record bytes visited, output bytes, elapsed scan time,
working-set observation and exclusions. Fix bounded-indexing regressions rather
than silently restoring the former entire-file size skip. Runner fixtures include
1,000 idle/repeated events and assert zero model wake-ups and no duplicate dispatch.
Use an explicit live usage ceiling and task count; not a hidden recurring workload.

## Run the included offline tests

```sh
python3 tools/run_payload_tests.py
python3 tools/validate_pack.py
```

Those tools require only Python stdlib. The payload tests use disposable directories,
a fake MASK program and real temporary Git/worktrees. They never invoke your provider
CLI. Native test claims are maintained separately in the owning live closeout.
