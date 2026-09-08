---
schema: "implement-rfc.card.v1"
id: "ASK-0041"
title: "Verify and close routing, instructions and portable rollout"
status: "Backlog"
rfcs: ["RFC-ASK-0008"]
depends_on: ["ASK-0040"]
closeout_for: ["RFC-ASK-0008"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "close-rollout-rfc"}
---

# ASK-0041: Verify and close routing, instructions and portable rollout

Governing RFCs: [RFC-ASK-0008](../../rfcs/RFC-ASK-0008-routing-profiles-and-portable-rollout.md).

## Objective and owned paths

Reconcile every governing criterion against direct evidence at its actual boundary. Reuse unchanged focused results; run missing/invalidated integration checks only. Record the actual pre-implementation RFC_BASE_SHA captured at intake and actual implementation revisions. Keep required native/semantic acceptance open until performed. Packet validation, fake-driver tests and successful symlink deployment are not evidence of live behavior or a subscription saving.

Own only: `docs/rfcs/RFC-ASK-0008-routing-profiles-and-portable-rollout.md`; `this live closeout card`; `affected public reference docs only`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Exactly one closeout owns this RFC; all required planned cards are Done and each criterion has an actual result/revision before Auto-Verified.
- Unmet required checks keep the RFC open. Inconclusive optimization results are reported truthfully and may retain the baseline.

Criterion coverage: RFC-ASK-0008-AC01, RFC-ASK-0008-AC02, RFC-ASK-0008-AC03, RFC-ASK-0008-AC04, RFC-ASK-0008-AC05, RFC-ASK-0008-AC06.

## Focused verification

Run the existing documentation/board gate plus only missing focused acceptance checks. Inspect the current live diff and dependency statuses; do not rerun an exhaustive historical matrix.

## Run record

Integration evidence reconciled on 2026-09-08. This closeout remains open behind its recorded prerequisites; these observations do not mark pending cards Done or the RFC Auto-Verified.

## Durable closeout anchor

RFC_BASE_SHA: 3fd05776115a7f3a224975e34edb30b0a65cf65a

Planned cards: ASK-0021, ASK-0037, ASK-0038, ASK-0039, ASK-0040.

## Closeout checklist

| Acceptance | Direct check / evidence | Outcome | Implementation revision |
|---|---|---|---|
| RFC-ASK-0008-AC01 | Fourteen renderer tests: opt-in candidate, independent review routes, unchanged native session config | Pass configuration; no profile promotion | 8326de11807875653805aadc13bf3c96e9c60907 |
| RFC-ASK-0008-AC02 | Explicit bounded fallback receipt validator and provenance tests | Pass configuration; no live substitution claimed | 8326de11807875653805aadc13bf3c96e9c60907 |
| RFC-ASK-0008-AC03 | Leaf Codex/Claude adapters and rendered role-authority tests; companion enforcement limitation documented | Pass generated adapters; Codex companion policy-only | 8326de11807875653805aadc13bf3c96e9c60907; f85f2ee |
| RFC-ASK-0008-AC04 | Eleven unified workflow tests inspect selected packets; legacy banner compatibility retained | Pass selected instructions; instruction treatment not measured | 46eab5b9a1aaaaf3cce7dba320fa3e501a87b222 |
| RFC-ASK-0008-AC05 | Actual SampleReview/SamplePlanner candidate checks and baseline rollback; public MASK pinned artifact invocation | Pass scoped adoption; host first-prompt loading not verified | 226ec7ebc1ed32e6411cc8433e6e1b87f8e6a3aa |
| RFC-ASK-0008-AC06 | Two backlog and two Windows attempts: two useful reports, one failure report, one turn limit | Observational only; final owner disposition pending | d7a9599461eb246cfa9ed11c6fea2408950076e2 |

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

The refreshed canonical portable source validator passed. Final structure-gate
result will be recorded at closeout. Native Windows capture and command checks
passed, including three corrected test-fixture reruns on Windows and macOS.
Windows Codex delivered a failure report but local tool startup timed out; that
execution path is explicitly unsupported. Windows Claude delivered a useful
read-only inventory. Detailed native evidence is on ASK-0025/0035/0036.

ASK-0039 is Done: both named consumers passed profile check and rollback; baseline
is restored and protected settings/SamplePlanner overrides are unchanged. Final
owner disposition is pending on ASK-0040. Both specifically authorized model
budgets are exhausted; no more attempts, purchases or resets are authorized.

Native temporary fixture checkout was removed after retaining reports outside it;
the existing Windows station remained clean. Local temporary fixture roots were
removed. Private user-local captures/reports and ignored native run journals are
intentionally retained. No publication/push or actual consumer pin migration was
performed.
