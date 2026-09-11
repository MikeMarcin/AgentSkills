---
schema: "implement-rfc.card.v1"
id: "ASK-0067"
title: "Let an attended hand-back wake the driver and clear stale hand-back state"
status: "Backlog"
rfcs: []
depends_on: []
priority: "P1"
metadata: {"origin": "SampleReview attended session v002/v003, 2026-09-10", "skills": ["attended-review", "implement-rfc"]}
---

# ASK-0067: Let an attended hand-back wake the driver and clear stale hand-back state

## Problem

`attended_review.py hand_back()` writes `handed_back` and appends a `handed-back` event, then returns. Nothing tells a driver: there is no blocking command, no signal, no process exit. The SKILL.md step 6 tells the driver to read `status --after SEQUENCE`, but a native driver that has ended its turn never runs it. On 2026-09-10 the user clicked **Finish and hand back** at 16:45:58 on the SampleReview session and had to tell the coordinator by hand. The whole reason for the local host over the offline HTML was that the driver should not need to be told.

Second defect: re-preparing candidates for a new revision (v003) left `handed_back` holding the v002 timestamp. A driver asking "has the owner handed back?" reads stale truth on a fresh queue.

## Objective and owned paths

Owned surfaces: `skills/attended-review/scripts/attended_review.py`, `skills/attended-review/SKILL.md`, `skills/attended-review/references/session-contract.md`, `skills/attended-review/tests/test_attended_review.py`, and the implement-rfc coordinator text that names the attended wait (`skills/implement-rfc/SKILL.md` step 3, `skills/implement-rfc/references/attendance.md`).

## Bounded work

- Add a `wait` subcommand: `wait [--after SEQUENCE] [--kind KIND ...] [--timeout SECONDS]`. It blocks until an event with sequence greater than `--after` and a matching kind exists (default kinds `handed-back` and `decision`), prints the new events as JSON and exits 0; a timeout exits nonzero with the current sequence. Poll the session file; take no lock while idle. Keep it host-independent so it works with `serve` running or not, and with the offline `import` path.
- Document the driver contract: after opening `serve`, the driver arms `wait` as a background command whose exit re-invokes it (Claude `run_in_background`, the Codex equivalent), before ending its turn. The coordinator's step 3 in implement-rfc lists the attended wait as an actionable event alongside the child wait.
- Clear `handed_back` whenever `init` adds or changes a candidate revision, `prepare` publishes a new candidate, `start` resumes review, or `resume-development` releases candidates. `status` then reports hand-back only for the current queue.
- Tests: `wait` returns on a hand-back and on a decision, times out cleanly, ignores older sequences; re-preparation clears `handed_back`; the existing hand-back test still passes.

## Acceptance

- A driver that armed `wait` before ending its turn is re-invoked by its host when the human clicks **Finish and hand back**, without the human writing a message. Evidence: one actual Claude course on a disposable consumer, the recorded event sequence and the driver's wake turn.
- `status` on a freshly prepared revision reports `handed_back: null` until the human hands that revision back.
- Session contract and SKILL.md name the `wait` command and the arm-before-ending rule; no daemon is introduced.
- Focused tests pass; no other command's behaviour changes.

## Verification and execution record

Run `python3 -m unittest skills/attended-review/tests/test_attended_review.py` and the documentation gate. Not started.
