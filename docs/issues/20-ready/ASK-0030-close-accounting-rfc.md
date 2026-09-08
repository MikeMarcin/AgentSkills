---
schema: "implement-rfc.card.v1"
id: "ASK-0030"
title: "Verify and close accounting and experiment readout"
status: "Ready"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0026", "ASK-0029"]
closeout_for: ["RFC-ASK-0007"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "close-accounting-rfc"}
---

# ASK-0030: Verify and close accounting and experiment readout

Governing RFCs: [RFC-ASK-0007](../../rfcs/RFC-ASK-0007-usage-accounting-outcomes-and-experiments.md).

## Objective and owned paths

Reconcile every governing criterion against direct evidence at its actual boundary. Reuse unchanged focused results; run missing/invalidated integration checks only. Record the actual pre-implementation RFC_BASE_SHA captured at intake and actual implementation revisions. Keep required native/semantic acceptance open until performed. Packet validation, fake-driver tests and successful symlink deployment are not evidence of live behavior or a subscription saving.

Own only: `docs/rfcs/RFC-ASK-0007-usage-accounting-outcomes-and-experiments.md`; `this live closeout card`; `affected public reference docs only`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Exactly one closeout owns this RFC; all required planned cards are Done and each criterion has an actual result/revision before Auto-Verified.
- Unmet required checks keep the RFC open. Inconclusive optimization results are reported truthfully and may retain the baseline.

Criterion coverage: RFC-ASK-0007-AC01, RFC-ASK-0007-AC02, RFC-ASK-0007-AC03, RFC-ASK-0007-AC04, RFC-ASK-0007-AC05, RFC-ASK-0007-AC06.

## Focused verification

Run the existing documentation/board gate plus only missing focused acceptance checks. Inspect the current live diff and dependency statuses; do not rerun an exhaustive historical matrix.

## Run record

Integration evidence reconciled on 2026-09-08. All planned accounting/tooling cards and the missing-consumption follow-up are Done. This closeout approves the accounting and experiment-contract implementation; actual optimization treatment/deployment decisions remain on ASK-0040.

## Durable closeout anchor

RFC_BASE_SHA: 3fd05776115a7f3a224975e34edb30b0a65cf65a

Planned cards: ASK-0021, ASK-0027, ASK-0028, ASK-0029; integration discovery ASK-0042.

## Closeout checklist

| Acceptance | Direct check / evidence | Outcome | Implementation revision |
|---|---|---|---|
| RFC-ASK-0007-AC01 | Eight hand-counted reconciliation fixtures: fragments/forks/resets/missing baselines | Pass | b64c39567413d721717c62809ea495e3d5e86ed6 |
| RFC-ASK-0007-AC02 | Dated optional Decimal rate-card/category/service-tier fixtures | Pass estimate contract; no subscription debit inferred | b64c39567413d721717c62809ea495e3d5e86ed6 |
| RFC-ASK-0007-AC03 | Seven quota tests and native Codex account/rateLimits/read; private observation on ASK-0028 | Pass observed native/manual boundary; Claude native endpoint not claimed | 70e4f6a5205b991e1978a9306bcc69f7e5f28b8a |
| RFC-ASK-0007-AC04 | Outcome/reopen/join fixtures plus missing-consumption regression ASK-0042 | Pass offline contract; pilot not an all-in comparison | 10be3e55d34a2278e181b3000dc546d6ed197bd6; 4456ad7f |
| RFC-ASK-0007-AC05 | Seven report tests; live immutable archive report; partial/unknown totals retained | Pass selected archive boundary | 10be3e55d34a2278e181b3000dc546d6ed197bd6; 4456ad7f |
| RFC-ASK-0007-AC06 | Experiment schema/observational-promotion refusal; two budgeted backlog observations on ASK-0035/0040 | Pass experiment contract; actual optimization readout remains ASK-0040 | 10be3e55d34a2278e181b3000dc546d6ed197bd6; f85f2ee |

## Integration verification and remaining boundary

At source candidate `810e012`, `python3 -m unittest discover -s skills/implement-rfc/tests -q`
ran 337 tests: 323 passed, 10 failed, four skipped. All ten failures are the unchanged
`test_remote_station_guard.py` setup: its fixture supplies retired `closeout_card`
and `rfc_link_field` keys rejected by the unchanged project resolver. Reproduced
one setup failure and read its stderr; no remote runtime was launched. This is a
pre-existing optional-station fixture defect outside the changed pack surface,
not a passing full suite. Windows skips do not qualify Windows. After the bounded
ASK-0042 correction, seven focused offline report tests passed. No full-suite rerun
was warranted by that isolated change.

Closeout review runtime: optional scoped `rfc-reviewer`, gpt-6-astra/high, read-only
runner protocol/durability review. Four reproduced defects were corrected under
ASK-0035 with direct regressions; no additional model review loop was run.

The canonical portable source validator passed. Final structure-gate result is
recorded below. Owner clarified the existing ExampleWinHost SSH/station. Native Windows collector and
command checks are now recorded on ASK-0025/0035; absence of an AgentSkills station
row was not evidence of host unavailability. Two additional owner-approved Windows native attempts completed report delivery;
Claude completed its inventory and Codex reported a local-tool timeout. No
redispatch or recovery occurred; the native fixture is cleaned. Deployment ASK-0039 and final
experiment decision ASK-0040 remain open. Resume from the live scoped queue. The approved two-task model pilot budget is exhausted; do not
infer authorization for more live experiments or credit/reset actions.

Disposable test roots and task-created temporary acceptance/edit files are
removed after consumption; the native fixture was removed after its private reports were retained. Private user-local captures/reports and ignored native
run journals are intentionally retained; no temporary checkout is retained and
no publication/push or consumer migration was performed.


## Accounting versus live optimization boundary

The imported ordering puts this tooling closeout before ASK-0040. AC06 here is
verified as the executable experiment/readout contract: one dimension, distinct
treatment ID, explicit owner ceiling and fixed-condition references, with
observational promotion refused. It does not assert that a matched live routing
or instruction treatment occurred. The later live readout and final owner
retention/promotion decision remain explicitly open on ASK-0040/RFC-ASK-0008.
No native quota saving, all-in ratio or winner is claimed from the backlog pilot.
