---
schema: "implement-rfc.card.v1"
id: "ASK-0029"
title: "Join task outcomes and produce offline comparison reports"
status: "Done"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0027", "ASK-0028"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "outcomes-and-offline-report"}
acceptance: [{"criterion":"RFC-ASK-0007-AC04/AC05/AC06 offline report contract","outcome":"pass","revision":"a1dd05446b8b038dd6987c6dc0baf728f09260e0","evidence":{"kind":"observation","detail":"Six archive/outcome tests and public native reporting on the retained private capture passed. Integrator inspected explicit unknowns, zero accepted tasks, and separated activity. Experiment configuration validation only; live comparison remains open."}}]
---

# ASK-0029: Join task outcomes and produce offline comparison reports

Governing RFCs: [RFC-ASK-0007](../../rfcs/RFC-ASK-0007-usage-accounting-outcomes-and-experiments.md).

## Objective and owned paths

Join captured operational events to existing acceptance references without a second task board. Produce REPORT.md, summary.json and compact CSVs by project/worktree/task/role/route and primary/child. Keep unassigned sessions, account readings, unknown ownership and possible copied-history duplication visible. Separate wait/list from messaging/spawning and mixed control/engineering requests. Include all attempts/reviews/repair and reopened outcomes in comparisons. Supply treatment IDs and a small experiment configuration independent of provider model calls.

Own only: `skills/implement-rfc/scripts/usage_report.py`; `skills/implement-rfc/scripts/usage_outcomes.py`; `skills/implement-rfc/tests/test_usage_report.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Report-produced, collected and accepted are distinguishable; zero accepted tasks is not a misleading zero-cost success.
- A corrupt/traversing/oversized/duplicate-entry archive is rejected; different-schema evidence remains immutable and explained.

Criterion coverage: RFC-ASK-0007-AC04, RFC-ASK-0007-AC05, RFC-ASK-0007-AC06.

## Focused verification

Run deterministic valid/invalid archive fixtures, hand-checked all-in task totals, mixed-account and reopened-outcome comparisons. Review a redacted sample report for understandable unknowns.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.

## Evidence and implemented boundary

Six report/outcome fixtures pass (`python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_usage_report.py`): public v1/v2 CLI, immutable inputs, traversal/duplicate/hash/expansion rejection, reopened outcomes, all-attempt joins, ambiguous assignment and cross-capture non-addition. Optional dated rate cards are explicit `--rates` inputs; no rates are fetched. Observational real-backlog experiments cannot promote a candidate automatically. CSV output includes project, provider, role, session kind, route and classification dimensions; unsafe spreadsheet prefixes are escaped.

Public native report command consumed the private seven-project capture and wrote `~/Library/Application Support/implement-rfc/usage/reports/execution-pack-20260908/REPORT.md` plus summary/CSVs. Integrator inspected the report: 17,954 aggregate-only, 12,579 ownership-uncertain, 56 unknown, 29 synthetic-error and 21,423 reconciled-request rows. Zero accepted tasks is explicit because no acceptance/assignment input was supplied; no denominator or subscription debit is invented. Claude companion's actual ASK-0029 note was consumed during implementation. Private capture/report remain outside Git.

Live controlled experiments and owner decisions are not claimed by these offline fixtures; their cards remain open.
