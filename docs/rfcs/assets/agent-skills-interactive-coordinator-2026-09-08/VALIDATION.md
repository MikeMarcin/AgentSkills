# Validation and evidence boundaries

## 1. Packet checks (performed while authoring)

`python -B tools/validate_pack.py` checks file integrity, safe layout, provisional
RFC/card identities, dependency/closeout coverage, routing targets, relative links
and fixture shapes. `python -B tools/test_pack.py` exercises refusal cases by
mutating disposable packet copies. Actual results live in
[PACK_CHECKS.md](PACK_CHECKS.md). These are **packet checks**, not source implementation,
native model tests, semantic acceptance or measured savings.

## 2. Source implementation checks (future)

Reconcile the actual current source first. Add focused tests for the role schema,
renderer authority/entrypoints, compact handoff identity and transitive accounting.
Use the source's existing public helpers and tests for their unaffected contracts.
Likely affected modules, from the supplied snapshot:

| Surface | Existing focused tests / gate |
|---|---|
| Roles/rendering/migration | test_render_runtime_adapters.py, test_role_migration.py, test_standard_worker_target.py |
| Consumer isolation | test_project_config.py; two distinct disposable consumers through shared links |
| Board/baseline/finish | test_unified_workflow.py, test_issue_board.py, test_audit_board.py, scoped structure gate |
| Usage parsing/family | test_usage_capture.py, test_usage_accounting.py, test_usage_report.py, test_usage_scope.py, test_role_usage.py |
| Package/source | validate_portable_agents.py --source-only, selected public MASK package validation, git diff --check |

Select relevant tests once; extend live role-target tests to preserve the old-role
projection while allowing the new integrator/session route. Retained historical
packet fixtures remain unchanged. Do not run an unchanged optional remote suite
merely because it exists, and do not label known failures as passes. New helper
names and CLI operations are implementation choices until documented and tested;
this packet does not supply a fake production command.

For handoff normalization, test valid labelled/JSON results, missing/current
mandate identity, duplicate terminal events, result-before-quiescence, unknown
exit, user cancellation and same-milestone continuation. Test structural JSON
implications separately from native ownership and semantic acceptance.

For usage, use the synthetic owning-response fixture with hand-calculated totals:
coordinator plus two integrator generations plus a leaf; duplicate deliveries,
parent summaries and old cumulative counters must not double count. Cached input
and reasoning output remain subsets. Missing outcome input is unknown, while an
explicit measured empty outcome set can be zero. Report gaps/conflicts rather than
select a favorable denominator.

## 3. Native behavior (future)

[NATIVE_QUALIFICATION.md](NATIVE_QUALIFICATION.md) owns the bounded actual interactive
course for each driver. Required missing driver evidence keeps its card/RFC
criterion open; continue independent implementation work. Native nested capability,
effective routes, safe continuation and waiting require observations of the chosen
runtime, not just successful renderer output or a model-written banner.

An OS-specific behavior is claimed only on the OS actually exercised. Reuse portable
logic and source-isolation evidence; no automatic Windows × macOS × every-host ×
every-model product matrix. A required native boundary remains explicit rather
than substituted with Linux mocks.

## 4. Efficiency and adoption (future)

The denominator is **demonstrated accepted capability with equivalent verification**.
Report total family usage and coverage; coordinator share, coordinator responses
per completed milestone, integrator onboarding/compactions, rework and independent
review are diagnostics. Do not sum inclusive thread totals with response records.
Do not treat fewer cards, slower concurrency or fewer elapsed active hours as a
quality-preserving saving.

Use the earlier SRV audit as motivation only, not a matched baseline for this tiny
course. A combined model/topology/instruction change is a rollout observation,
not the existing helper's one-factor controlled experiment. Keep that helper's
strict validation intact. An explicitly budgeted later matched comparison may
hold other factors stable; no repeated broad bakeoff is required now.

Record one of: lower all-in cost observed; higher cost observed; incomparable;
or insufficient coverage. An inconclusive result can support an owner-directed
trial with a transparent rollback choice, but cannot be promoted as a measured
optimization. The 40-hour goal remains an objective, not an invented acceptance
threshold. Required quality/correctness boundaries are not negotiable to meet it.

## 5. Closeout (future)

One linked closeout records the actual immutable RFC_BASE_SHA, planned cards,
criterion/check/outcome/revision rows, chosen source/adapter versions, limitations,
cleanup and selected activation/rollback. Reuse unchanged evidence. Packet IDs and
blank rows never count as a real reservation or completed work. No source commit,
push, deployment, subscription change or live native pass occurred in authoring.
