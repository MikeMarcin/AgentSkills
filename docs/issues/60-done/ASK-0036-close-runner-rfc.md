---
schema: "implement-rfc.card.v1"
id: "ASK-0036"
title: "Verify and close bounded execution and durable delegation"
status: "Done"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0035"]
closeout_for: ["RFC-ASK-0005"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "close-runner-rfc"}
acceptance: [{"criterion":"RFC-ASK-0005-AC01","outcome":"pass","revision":"2c404ee3b9bb864edd3244741585727fae3bebc3","evidence":{"kind":"observation","detail":"Closeout matrix ties passing admission/durability/authority fixtures to actual native macOS/Windows command and companion delivery. Unsupported Windows Codex local tools and public recovery/source-writing limits remain explicit. Exact live results on ASK-0035."}},{"criterion":"RFC-ASK-0005-AC02","outcome":"pass","revision":"2c404ee3b9bb864edd3244741585727fae3bebc3","evidence":{"kind":"observation","detail":"Closeout matrix ties passing admission/durability/authority fixtures to actual native macOS/Windows command and companion delivery. Unsupported Windows Codex local tools and public recovery/source-writing limits remain explicit. Exact live results on ASK-0035."}},{"criterion":"RFC-ASK-0005-AC03","outcome":"pass","revision":"2c404ee3b9bb864edd3244741585727fae3bebc3","evidence":{"kind":"observation","detail":"Closeout matrix ties passing admission/durability/authority fixtures to actual native macOS/Windows command and companion delivery. Unsupported Windows Codex local tools and public recovery/source-writing limits remain explicit. Exact live results on ASK-0035."}},{"criterion":"RFC-ASK-0005-AC04","outcome":"pass","revision":"2c404ee3b9bb864edd3244741585727fae3bebc3","evidence":{"kind":"observation","detail":"Closeout matrix ties passing admission/durability/authority fixtures to actual native macOS/Windows command and companion delivery. Unsupported Windows Codex local tools and public recovery/source-writing limits remain explicit. Exact live results on ASK-0035."}},{"criterion":"RFC-ASK-0005-AC05","outcome":"pass","revision":"2c404ee3b9bb864edd3244741585727fae3bebc3","evidence":{"kind":"observation","detail":"Closeout matrix ties passing admission/durability/authority fixtures to actual native macOS/Windows command and companion delivery. Unsupported Windows Codex local tools and public recovery/source-writing limits remain explicit. Exact live results on ASK-0035."}},{"criterion":"RFC-ASK-0005-AC06","outcome":"pass","revision":"2c404ee3b9bb864edd3244741585727fae3bebc3","evidence":{"kind":"observation","detail":"Closeout matrix ties passing admission/durability/authority fixtures to actual native macOS/Windows command and companion delivery. Unsupported Windows Codex local tools and public recovery/source-writing limits remain explicit. Exact live results on ASK-0035."}}]
---

# ASK-0036: Verify and close bounded execution and durable delegation

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Reconcile every governing criterion against direct evidence at its actual boundary. Reuse unchanged focused results; run missing/invalidated integration checks only. Record the actual pre-implementation RFC_BASE_SHA captured at intake and actual implementation revisions. Keep required native/semantic acceptance open until performed. Packet validation, fake-driver tests and successful symlink deployment are not evidence of live behavior or a subscription saving.

Own only: `docs/rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md`; `this live closeout card`; `affected public reference docs only`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Exactly one closeout owns this RFC; all required planned cards are Done and each criterion has an actual result/revision before Auto-Verified.
- Unmet required checks keep the RFC open. Inconclusive optimization results are reported truthfully and may retain the baseline.

Criterion coverage: RFC-ASK-0005-AC01, RFC-ASK-0005-AC02, RFC-ASK-0005-AC03, RFC-ASK-0005-AC04, RFC-ASK-0005-AC05, RFC-ASK-0005-AC06.

## Focused verification

Run the existing documentation/board gate plus only missing focused acceptance checks. Inspect the current live diff and dependency statuses; do not rerun an exhaustive historical matrix.

## Run record

Integration evidence reconciled on 2026-09-08. All planned runner cards are Done for their explicit supported matrix. The unqualified Windows Codex command-tool path remains a documented capability limitation, not an asserted success.

## Durable closeout anchor

RFC_BASE_SHA: 3fd05776115a7f3a224975e34edb30b0a65cf65a

Planned cards: ASK-0021, ASK-0031, ASK-0032, ASK-0033, ASK-0034, ASK-0035.

## Closeout checklist

| Acceptance | Direct check / evidence | Outcome | Implementation revision |
|---|---|---|---|
| RFC-ASK-0005-AC01 | Public command order tests: exact argv, test counts, timeout, failure, final integrator gate | Pass macOS subprocess path | 191f8eea35713cb56dfb37068139256402c85e56; f85f2ee |
| RFC-ASK-0005-AC02 | Frozen roots/routes/permissions/packets/owned script and dispatch-budget negative tests | Pass admitted supported stages | f85f2ee |
| RFC-ASK-0005-AC03 | Forty runner tests; four independently reproduced defects corrected; native public final report inspected | Pass supported delivery; native crash windows remain explicit | f85f2ee |
| RFC-ASK-0005-AC04 | Report-only fixture recovery and cancellation interleavings; native max-turn failure retained without retry | Pass bounded/explicit-unsupported contract; public recovery unsupported | 615cf91effa126672013da33a26b9ba115fe0086; f85f2ee |
| RFC-ASK-0005-AC05 | Native macOS Codex/Claude adapter reports and Claude public runner success/limit; exact records ASK-0033–0035 | Pass supported matrix; Windows Codex local tools explicitly unqualified | e48c29103025f2cd39aca84a9bd43ef357b8926f; 81cbb4b6123865c6a6ebb13e65c037d82abd1e6c; f85f2ee |
| RFC-ASK-0005-AC06 | Eleven unified workflow tests and public run result semantic_acceptance=not_decided_by_runner | Pass authority/direct-execution contract | 46eab5b9a1aaaaf3cce7dba320fa3e501a87b222; f85f2ee |

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
row was not evidence of host unavailability. The owner approved two additional native Windows attempts; Claude completed its
inventory and Codex delivered a command-tool timeout report. Both were inspected
and neither was redispatched. Native reports are retained outside the cleaned fixture. Deployment ASK-0039 and final
experiment decision ASK-0040 remain open. Resume from the live scoped queue. The approved two-task model pilot budget is exhausted; do not
infer authorization for more live experiments or credit/reset actions.

Disposable test roots and task-created temporary acceptance/edit files are
removed after consumption; the native fixture has been removed after report retention and qualification. Private user-local captures/reports and ignored native
run journals are intentionally retained; no temporary checkout is retained and
no publication/push or consumer migration was performed.

Final supported native matrix and exact additional attempts: ASK-0035 at `4fc6ee930752af4f8f6ddea3f8c2ce53ba907978`. Known native limitations are explicitly unsupported, preserving direct execution and requiring no retry, permission expansion or billing change.

## Subsequent pack reconciliation

ASK-0039 completed both consumer checks and baseline rollback at
226ec7ebc1ed32e6411cc8433e6e1b87f8e6a3aa. The separately approved two
Windows attempts were consumed: Claude inventory succeeded; Codex delivered a
failure report with local tool execution explicitly unsupported. Native fixture
cleanup is complete. Earlier pending statements above describe their recorded
checkpoint, not current host availability. Final evaluation disposition is owned
by ASK-0040 and the rollout closeout ASK-0041.
