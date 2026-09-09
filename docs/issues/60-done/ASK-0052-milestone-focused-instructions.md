---
schema: "implement-rfc.card.v1"
id: "ASK-0052"
title: "Rewrite the common implement-rfc path around complete integrated milestones"
status: "Done"
rfcs: ["RFC-ASK-0010"]
depends_on: ["ASK-0051"]
metadata: {"packet": "agent-skills-interactive-coordinator-2026-09-08", "provisional_id": false, "packet_key": "milestone-focused-instructions", "milestone": "M1"}
acceptance: [{"criterion":"AC04-source","outcome":"pass","revision":"7c3fc2901ce2305d5a9ee43224653d899904c7df","evidence":{"kind":"observation","detail":"12 unified workflow/historical target tests and 2 pointer/provider-entrypoint tests pass. Static candidate reader evaluated eight next-action scenarios: multi-card milestone, one-card, status, review, correction, closeout, partial attendance, no grandchildren. Clarified last branch to integrator-local work plus qualified independent-review relay only. Source manifest validates. Static sizes include mandatory consumer/root/RFC/selected-card text and generated integrator prompt; exclude hidden host input and are not runtime usage or a savings measurement.","instruction_load":{"baseline_entrypoint":{"words":1695,"utf8_bytes":12926},"candidate_entrypoint":{"words":720,"utf8_bytes":5501},"shared_required_documents":["AGENTS.md","README.md","CONTRIBUTING.md","docs/rfcs/README.md","docs/issues/README.md",".mask/skill-config/implement-rfc/project.md",".mask/skill-config/implement-rfc/project.json","docs/rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md","docs/issues/30-in-progress/ASK-0052-milestone-focused-instructions.md"],"common_payload":{"words":6422,"utf8_bytes":52044},"coordinator":{"paths":["SKILL.md","references/native-coordination.md"],"words":7459,"utf8_bytes":59969},"integrator":{"paths":["references/milestone-integration.md","references/native-coordination.md","references/delegated-execution.md","references/verification-and-closeout.md","references/bookkeeping.md"],"words":10221,"utf8_bytes":80833}}}},{"criterion":"AC07-source","outcome":"pass","revision":"7c3fc2901ce2305d5a9ee43224653d899904c7df","evidence":{"kind":"observation","detail":"12 unified workflow/historical target tests and 2 pointer/provider-entrypoint tests pass. Static candidate reader evaluated eight next-action scenarios: multi-card milestone, one-card, status, review, correction, closeout, partial attendance, no grandchildren. Clarified last branch to integrator-local work plus qualified independent-review relay only. Source manifest validates. Static sizes include mandatory consumer/root/RFC/selected-card text and generated integrator prompt; exclude hidden host input and are not runtime usage or a savings measurement.","instruction_load":{"baseline_entrypoint":{"words":1695,"utf8_bytes":12926},"candidate_entrypoint":{"words":720,"utf8_bytes":5501},"shared_required_documents":["AGENTS.md","README.md","CONTRIBUTING.md","docs/rfcs/README.md","docs/issues/README.md",".mask/skill-config/implement-rfc/project.md",".mask/skill-config/implement-rfc/project.json","docs/rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md","docs/issues/30-in-progress/ASK-0052-milestone-focused-instructions.md"],"common_payload":{"words":6422,"utf8_bytes":52044},"coordinator":{"paths":["SKILL.md","references/native-coordination.md"],"words":7459,"utf8_bytes":59969},"integrator":{"paths":["references/milestone-integration.md","references/native-coordination.md","references/delegated-execution.md","references/verification-and-closeout.md","references/bookkeeping.md"],"words":10221,"utf8_bytes":80833}}}},{"criterion":"AC08-instructions","outcome":"pass","revision":"7c3fc2901ce2305d5a9ee43224653d899904c7df","evidence":{"kind":"observation","detail":"12 unified workflow/historical target tests and 2 pointer/provider-entrypoint tests pass. Static candidate reader evaluated eight next-action scenarios: multi-card milestone, one-card, status, review, correction, closeout, partial attendance, no grandchildren. Clarified last branch to integrator-local work plus qualified independent-review relay only. Source manifest validates. Static sizes include mandatory consumer/root/RFC/selected-card text and generated integrator prompt; exclude hidden host input and are not runtime usage or a savings measurement.","instruction_load":{"baseline_entrypoint":{"words":1695,"utf8_bytes":12926},"candidate_entrypoint":{"words":720,"utf8_bytes":5501},"shared_required_documents":["AGENTS.md","README.md","CONTRIBUTING.md","docs/rfcs/README.md","docs/issues/README.md",".mask/skill-config/implement-rfc/project.md",".mask/skill-config/implement-rfc/project.json","docs/rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md","docs/issues/30-in-progress/ASK-0052-milestone-focused-instructions.md"],"common_payload":{"words":6422,"utf8_bytes":52044},"coordinator":{"paths":["SKILL.md","references/native-coordination.md"],"words":7459,"utf8_bytes":59969},"integrator":{"paths":["references/milestone-integration.md","references/native-coordination.md","references/delegated-execution.md","references/verification-and-closeout.md","references/bookkeeping.md"],"words":10221,"utf8_bytes":80833}}}},{"criterion":"AC09-instructions","outcome":"pass","revision":"7c3fc2901ce2305d5a9ee43224653d899904c7df","evidence":{"kind":"observation","detail":"12 unified workflow/historical target tests and 2 pointer/provider-entrypoint tests pass. Static candidate reader evaluated eight next-action scenarios: multi-card milestone, one-card, status, review, correction, closeout, partial attendance, no grandchildren. Clarified last branch to integrator-local work plus qualified independent-review relay only. Source manifest validates. Static sizes include mandatory consumer/root/RFC/selected-card text and generated integrator prompt; exclude hidden host input and are not runtime usage or a savings measurement.","instruction_load":{"baseline_entrypoint":{"words":1695,"utf8_bytes":12926},"candidate_entrypoint":{"words":720,"utf8_bytes":5501},"shared_required_documents":["AGENTS.md","README.md","CONTRIBUTING.md","docs/rfcs/README.md","docs/issues/README.md",".mask/skill-config/implement-rfc/project.md",".mask/skill-config/implement-rfc/project.json","docs/rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md","docs/issues/30-in-progress/ASK-0052-milestone-focused-instructions.md"],"common_payload":{"words":6422,"utf8_bytes":52044},"coordinator":{"paths":["SKILL.md","references/native-coordination.md"],"words":7459,"utf8_bytes":59969},"integrator":{"paths":["references/milestone-integration.md","references/native-coordination.md","references/delegated-execution.md","references/verification-and-closeout.md","references/bookkeeping.md"],"words":10221,"utf8_bytes":80833}}}}]
---

# ASK-0052: Rewrite the common implement-rfc path around complete integrated milestones

Governing RFC: [RFC-ASK-0010](../../rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md).

## Objective and owned paths

Use the supplied writing-for-agents references and draft as editorial inputs. Keep the coordinator short; route an assigned integrator directly to the engineering procedure. Specify usable milestone selection, early thin composition, complete-slice ownership, useful concurrency and native waiting. Disclose branch-only procedures through specific pointers. Preserve direct checks, risk-selected independent review, simplification, immutable baseline, explicit path commits, required human/native acceptance and attended protection/partial intake. Remove conflicting active primary-only wording without changing unrelated consumer instructions or settled history. Count the actual combined per-role paths and test next actions, not just keywords.

Owned paths:

- `skills/implement-rfc/SKILL.md`
- `skills/implement-rfc/references/milestone-integration.md`
- `skills/implement-rfc/references/delegated-execution.md`
- `skills/implement-rfc/references/verification-and-closeout.md`
- `skills/implement-rfc/references/attendance.md`
- `skills/implement-rfc/config/roles.json instruction changes coordinated with ASK-0051`
- `README.md, AGENTS.md, CONTRIBUTING.md and AgentSkills workflow/tracker rules only where active conflicts exist`
- `skills/implement-rfc/tests/test_unified_workflow.py and focused instruction cases`

## Acceptance

- Normal implementation reaches a demonstrable integrated capability without a mandatory role pipeline or whole-pack child.
- Status-only makes no edits or child; one-card work uses a single integrator; resume, closeout and attendance have explicit completion boundaries.
- Ordinary worker eligibility, useful same-problem reuse and independent review remain intact.
- All mandatory branches remain reachable and direct acceptance is no weaker; root/consumer rules are not silently waived to reduce prompt size.

Criterion coverage: RFC-ASK-0010-AC04, RFC-ASK-0010-AC07, RFC-ASK-0010-AC08, RFC-ASK-0010-AC09.

## Focused verification

- Workflow cases using the actual candidate text; pointer/reachability and word/byte comparison against the source snapshot.
- Focused existing bookkeeping/unified workflow tests for affected boundaries; package/source checks.
- Review changed instructions for duplicated meanings, stale runtime claims and missing branch triggers.

## Run record

Not started. No native run, source implementation, reservation, accepted work or
measured saving is claimed by this packet. Claim the live card before source work,
preserve unrelated changes and commit only explicit owned paths.
