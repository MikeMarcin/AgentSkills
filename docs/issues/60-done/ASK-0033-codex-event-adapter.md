---
schema: "implement-rfc.card.v1"
id: "ASK-0033"
title: "Implement the capability-checked Codex event-driven adapter"
status: "Done"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0032"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "codex-event-adapter"}
acceptance: [{"criterion":"RFC-ASK-0005-AC05 Codex companion","outcome":"pass","revision":"d9a130c79be0cb1ae085dee8758e5a1d3ee1c166","evidence":{"kind":"observation","detail":"Five protocol tests and an installed native macOS useful backlog analysis passed. Integrator inspected collected report and native lifecycle; unsupported capabilities and exact runtime recorded in card."}}]
---

# ASK-0033: Implement the capability-checked Codex event-driven adapter

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Bind the runner to installed app-server operations and exact owned thread/turn identities. Preserve authentication, user-selected routes, permission requests and supported structured completion. Keep startup/version/protocol capability independent. Do not treat an arbitrary native subagent ID as a top-level resumable thread. Where native embedded sessions cannot be controlled, expose a supported companion or explicit handoff instead of pretending zero-poll orchestration.

Own only: `skills/implement-rfc/scripts/slice_codex.py`; `skills/implement-rfc/tests/test_slice_codex.py`; `skills/implement-rfc/references/bounded-execution.md`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- The adapter wakes the integrator for decisions/gates, not every status interval.
- Runtime errors, quota blocks and unsupported operations preserve partial evidence and cannot fall through to API billing or approvals.

Criterion coverage: RFC-ASK-0005-AC05.

## Focused verification

Fake protocol transcripts assert exact launch/cancel/notification joins and unsupported behavior. Record a bounded live installed-CLI smoke only with approved capacity and permissions.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.

## Native macOS qualification

Installed runtime: codex-cli 0.153.2. Generated protocol schemas established supported fields and enums; an initialize/account-read probe confirmed existing ChatGPT authentication with zero model turns. One bounded read-only baseline `gpt-5.6-sol` / `high` companion analyzed real backlog ASK-0027, per the owner's request to use useful work. Packet capped wall time at 120 seconds, used read-only sandbox and approvalPolicy never, and prohibited edits/delegation/network research. No source or board changes came from the companion.

The event stream delivered three partial messages, native execution completion, durable report production, collection and awaiting_integration. The integrator read the report: missing counter baselines, reset/compaction ambiguity and inherited child usage are useful inputs for ASK-0027. Report: `.mask/generated/implement-rfc/runs/native-codex-accounting-scout-20260908/accounting-scout-1.report.txt`. Native thread/turn identities remain in local lifecycle records. No API key, reset or credit purchase occurred. The owned app-server subprocess was closed.

Five fake-protocol tests passed via `python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_slice_codex.py`. Native embedded-subagent adoption, turn-count limits and report-only resume remain explicitly unsupported. macOS companion support is qualified; Windows remains open.
