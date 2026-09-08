---
schema: "implement-rfc.card.v1"
id: "ASK-0026"
title: "Verify and close the turnkey capture RFC"
status: "Ready"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0024", "ASK-0025"]
closeout_for: ["RFC-ASK-0006"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "close-capture-rfc"}
---

# ASK-0026: Verify and close the turnkey capture RFC

Governing RFCs: [RFC-ASK-0006](../../rfcs/RFC-ASK-0006-project-aware-turnkey-usage-capture.md).

## Objective and owned paths

Reconcile every governing criterion against direct evidence at its actual boundary. Reuse unchanged focused results; run missing/invalidated integration checks only. Record the actual pre-implementation RFC_BASE_SHA captured at intake and actual implementation revisions. Keep required native/semantic acceptance open until performed. Packet validation, fake-driver tests and successful symlink deployment are not evidence of live behavior or a subscription saving.

Own only: `docs/rfcs/RFC-ASK-0006-project-aware-turnkey-usage-capture.md`; `this live closeout card`; `affected public reference docs only`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Exactly one closeout owns this RFC; all required planned cards are Done and each criterion has an actual result/revision before Auto-Verified.
- Unmet required checks keep the RFC open. Inconclusive optimization results are reported truthfully and may retain the baseline.

Criterion coverage: RFC-ASK-0006-AC01, RFC-ASK-0006-AC02, RFC-ASK-0006-AC03, RFC-ASK-0006-AC04, RFC-ASK-0006-AC05, RFC-ASK-0006-AC06.

## Focused verification

Run the existing documentation/board gate plus only missing focused acceptance checks. Inspect the current live diff and dependency statuses; do not rerun an exhaustive historical matrix.

## Run record

Integration evidence reconciled on 2026-09-08. This closeout remains open behind its recorded prerequisites; these observations do not mark pending cards Done or the RFC Auto-Verified.

## Durable closeout anchor

RFC_BASE_SHA: 3fd05776115a7f3a224975e34edb30b0a65cf65a

Planned cards: ASK-0021, ASK-0022, ASK-0023, ASK-0024, ASK-0025.

## Closeout checklist

| Acceptance | Direct check / evidence | Outcome | Implementation revision |
|---|---|---|---|
| RFC-ASK-0006-AC01 | Cwd/linked CLI and strict-empty/archive integrity: test_usage_cli.py; native macOS ASK-0024 | Pass macOS and Windows | dbb343295a8094108d93accb7f80421c0ffbcfd1 |
| RFC-ASK-0006-AC02 | Public MASK scope/identity/worktree fixtures and native registry capture (ASK-0022/0024) | Pass local scope contract | 4e0297431de3fd3b96904da88d0e431ab73396fc |
| RFC-ASK-0006-AC03 | 51 scope/capture tests; versioned ownership/counter baselines; runtime projection fixture | Pass with explicit unknown ownership | 3e1348e1d5dcd15b4450900d5a971306b8dd097d; f85f2ee |
| RFC-ASK-0006-AC04 | 30,000-event stress and real 43.29 GB scan; exact metrics on ASK-0023/0024 | Pass bounded scan; live capture partial | 3e1348e1d5dcd15b4450900d5a971306b8dd097d |
| RFC-ASK-0006-AC05 | Read-only package/output/privacy CLI fixtures; default native archive | Pass selected macOS path | dbb343295a8094108d93accb7f80421c0ffbcfd1; f85f2ee |
| RFC-ASK-0006-AC06 | Native ExampleWinHost Windows-specific tests passed; 78 usage cases reconciled with one POSIX skip; real zero-argument ZIP | Pass native Windows after fixture corrections | ca81470d17bc14c851ec2f0d8349203611980515 |

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
row was not evidence of host unavailability. Native Windows agent qualification
awaits an explicit additional two-attempt budget. Deployment ASK-0039 and final
experiment decision ASK-0040 remain open. Resume from the live scoped queue. The approved two-task model pilot budget is exhausted; do not
infer authorization for more live experiments or credit/reset actions.

Disposable test roots and task-created temporary acceptance/edit files are
removed after consumption; the native fixture is temporarily retained while
Windows qualification remains active. Private user-local captures/reports and ignored native
run journals are intentionally retained; no temporary checkout is retained and
no publication/push or consumer migration was performed.
