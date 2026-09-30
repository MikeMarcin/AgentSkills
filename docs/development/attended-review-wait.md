# Attended-review wait correction, 2026-09-30

ASK-0092 replaces assumed Codex background wake behavior with a pending tool
call, or explicit manual resume when that runtime capability is unavailable.
Claude's existing persistent-monitor path is preserved. No review-state schema
or Python wait API changed. The canonical driver contract is
[Driver waiting](../../skills/attended-review/references/driver-wait.md).

## Observed Codex behavior

The native macOS desktop chat exposed `functions.exec`, `functions.wait`,
`exec_command` and `write_stdin`. The inspected CLI was 0.155.1 and Python was
3.14.7; CLI version is not an independent identification of the desktop build.
Fixtures used temporary checkout and registry roots, with no product verdicts.

The short probe started the existing Python waiter with an explicit cursor and
`--kind handed-back`. A deterministic fixture process saved A's decision after
15 seconds and handed back at 150 seconds, leaving B unanswered. One code-mode
cell awaited the command and its shell-session poll; one outer tool call awaited
that cell with a requested 12-hour window.

| Observation | Actual result |
| --- | --- |
| Outer wait interval | 17:52:06.415–17:54:31.947 UTC, 145.532 seconds |
| Partial decision | Saved without releasing the handback-only wait |
| Handback event | One returned event, correct session; A decided, B pending |
| Handback to outer tool return | 0.103197 seconds |
| Idle inference | No subsequent model-response items or usage records after the boundary request that invoked the wait |
| Native PTY cancellation | Ctrl-C ended only the fixture waiter; status remained identical |

The request that invoked the outer wait emitted its usage record 23 ms after
entry; this is boundary accounting, not a subsequent idle inference request.
The observed result comes from actual tool completion and recorded usage, not
acceptance of the requested timeout value.

The extended probe remained pending until the user interrupted the tool after
2,241 seconds and explicitly waived the six-hour prerequisite. It did not
complete and produced no fixture handback. Its waiter, delayed trigger and
temporary keep-awake process were identified and stopped, with no matching
processes left. The active exec cell no longer existed on reconciliation.
Overnight behavior, app restart and computer sleep are **unverified**; they are
documented interruption/recovery cases, not claimed continuous operation.

## Focused verification

- `python3 -B -m unittest discover -s skills/attended-review/tests -v`: 27 passed,
  including handback-only waiting across an old cursor and partial decision,
  cancellation preserving decisions/protection and resumed intake, and checkout
  isolation. Existing tests cover timeout, offline intake and the HTTP path.
- `python3 -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only`:
  passed after authoring the updated portable digest.
- `python3 -B scripts/verify_documentation.py --root .`: no structural violations.
- Passive frozen-Git payload validation: attended-review and implement-rfc both
  passed at implementation commit `81ed6a6d17c6e6b7831a2af353ba9c7b38af23f3` and
  the amended source commit `15992b600982ae999607f1bc597424e493ef36be`.
- `git diff --check`: passed.

These are local results. Native Windows waiting and other tool harnesses require
their own bounded qualification; a POSIX quoting example is not a Windows adapter.

## Scoped aito handoff

The user authorized pausing `rfc-fvi-0054-review-hand-back` and one setup message
to **Implement RFC-FVI-0054** (`01a0f12c-079d-7240-953a-69dcfeef3a23`). The
automation tool confirmed PAUSED while preserving the saved prompt/schedule.
On subsequent reconciliation its local automation file was absent; it was not
recreated. The live review retained its session, protected candidates and saved
partial verdict. No known old waiter remained in the process inventory.

The setup message supplied the installed waiter and saved cursor, the observed
bounded proof, the user's soak-test waiver, the new code-mode orchestration and
safe intake/recovery rules. It explicitly retained the pinned 901b strategy,
engineering delegation, budgets and acceptance; it did not upgrade managed
copies or grant new acceptance. No other consumers were deployed and nothing
was pushed or published.

The receiving chat reported that its old server and waiter had already ended,
then restored the same durable session. Process/state inspection confirmed a new
waiter with the installed script, cursor 18, handback-only filter and 12-hour
timeout. Its recorded tool calls show the awaited code-mode cell followed by
one `functions.wait` at 19:24:04.790 UTC with `yield_time_ms: 43200000`. The review
remained at sequence 19 with six ready/protected candidates and one saved verdict.
This verifies that the replacement was armed; the pending live review has not
yet established overnight reliability or a real-user handback result.
