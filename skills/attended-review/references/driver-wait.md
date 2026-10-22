# Driver waiting

The Python `wait` command polls local file metadata without model inference. Its
exit returns events to its caller; the host decides whether the driver resumes.
An idle shell session, async hook, or final answer does not itself guarantee a
new Codex turn. Keep durable decisions independent of that host capability.

## Share now, wait when idle

Before sharing, record the source checkout/revision, state/registry paths, session
ID, candidate revisions/fingerprints, durable consumed event cursor, server/Serve
identities, command ownership and owning driver in the private continuation. Keep
personal `--state` and cooperating `--registry` arguments identical on every command.

Publish the complete usable private HTTPS link promptly. While genuinely useful
independent work remains—agents, preparation, coordination or integration—keep
coordinating that work within prepared-candidate protection. The page saves intake
without an active waiter. Inspect `status --after CONSUMED_SEQUENCE` at natural
task boundaries and reconcile a recorded handback then, rather than asking for a
second click. Use those work boundaries, not a model polling loop or heartbeat.
A pending outer Codex wait parks the coordinator: child agents can continue, but
their results and integration may need the coordinator's attention.

When human input is the sole remaining dependency, automatic wait/resume is the
default in a qualified runtime:

1. Release engineering writers and persist exact command/session/cursor ownership.
   Before blocking, read `status --after CONSUMED_SEQUENCE` and verify the expected
   session. Reconcile returned candidate intake and any already-recorded handback.
   Persist the consumed cursor only after that reconciliation, before dispatching
   further work. A latest sequence alone must not skip an unconsumed event.
2. If handback was already recorded, process it immediately under the preserved
   engineering strategy. Otherwise arm `wait --after CHECKED_SEQUENCE --kind
   handed-back` from that reconciled status cursor. A handback racing between
   status and wait remains newer than the checked cursor and returns immediately.
3. Save the exact waiter command and command/cell identity. Follow the host path
   below, reusing applicable qualification. Partial decisions save immediately
   while the handback-only waiter stays blocked. In the idle Codex branch, retain
   one pending outer call without a final answer while actively waiting.

## Claude Code

For the idle branch, arm `wait --after CHECKED_SEQUENCE --kind handed-back` through
`Monitor` with `persistent: true` before ending the turn. This preserves the existing monitor
path; a plain background shell command's ten-minute lifetime is too short for an
overnight review. Qualify the actual host, not a rendered configuration.

## Codex with code-mode tools

In the idle branch, keep the coordinator's turn running on one pending call. The
review remains usable in its browser, and the chat may show as running while the model is idle.
No waiting subagent, daemon, model launcher or scheduled status check is needed.

Reuse the recorded qualification below for a matching awake runtime and toolchain;
a new review session does not require a new probe. Use the following orchestration
shape when the installed runtime exposes these tools. Substitute the reviewed
argument array and checked sequence; execute this as one `functions.exec` cell.
Argument quoting keeps paths literal.
The example uses a POSIX shell. Native Windows needs a qualified native argument
adapter; do not introduce Bash or WSL to make this example run.

```javascript
// @exec: {"yield_time_ms": 1000, "max_output_tokens": 1500}
const argv = [PYTHON, "-B", SCRIPT, "--repo-root", ROOT,
  // Include the same --state and --registry arguments when the session uses them.
  "wait", "--after", String(CHECKED_SEQUENCE), "--kind", "handed-back",
  "--timeout", "43200"];
const quote = value => "'" + value.replaceAll("'", "'\\''") + "'";
let result = await tools.exec_command({
  cmd: argv.map(quote).join(" "), tty: true,
  yield_time_ms: 1000, max_output_tokens: 1500
});
while (result.session_id) {
  result = await tools.write_stdin({
    session_id: result.session_id, chars: "",
    yield_time_ms: 300000, max_output_tokens: 1500
  });
}
text(result);
```

If the cell yields with a cell ID, call `functions.wait` for that exact cell with
`yield_time_ms: 43200000` and a compact output budget. Stay blocked on that call;
do not send a final answer while waiting. The inner `write_stdin` loop is
deterministic tool orchestration and prints no idle updates to the model. The
12-hour command timeout ends the review wait once; it does not start a retry loop.
After the process exits, check its exit code before parsing the event JSON.

For a changed or unsupported runtime, qualification must cover the entire stack,
including the outer wait; otherwise use explicit manual resume. Use a
disposable review: an intermediate decision must leave the call blocked and
handback must return once. Inspect recorded model usage and measure
handback-to-return latency on an awake host. Require zero idle model requests and
target a return within two seconds. Record the observed duration and actual
runtime/version in the consumer continuation; a short probe does not establish
overnight reliability. Extended idle tests are optional and run only when the
user requests them. An accepted timeout parameter alone proves no waiting behavior.
Treat a changed host or an early outer yield as unqualified; do not hide it with
model-driven re-polling. Native tools with other names require their own observed
blocking-wait qualification rather than an assumed equivalent.

### Recorded awake-runtime qualification

The observed stack was Codex Desktop with reported CLI `0.163.0-alpha.10.2`,
macOS 26.6.2 arm64, Python 3.14.7 and `functions.exec` / `functions.wait` /
`exec_command` / `write_stdin`, using the orchestration above. CLI version alone
does not identify the desktop build. Source was reviewed at
`38d0715610fa9255fdf990067c43b669c7d54191`; the attended-review runtime last changed
at `f52a273e4058ae58f420c19bc2d2370fe857610d`. Tailscale 1.102.3 carried the real
phone review.

| Observation | Result |
| --- | --- |
| Saved intermediate decision | Wait stayed blocked; handback followed 2.410406 seconds later |
| Handback and return | Exactly one new handback, expected session, waiter exit 0; return latency 0.1793 seconds |
| Blocked duration | Helper 43.392 seconds; outer call 32.604 seconds, with no early yield |
| Idle activity | No assistant activity or token-count usage events recorded during the blocked outer wait |
| Intake and cleanup | Session/fingerprints/cursor validated and consumed before dispatch; owned processes, Serve route and disposable fixture removed |

Handover and arming activity occurred before the blocked outer wait and is excluded
from the idle observation. This is a short awake-host qualification, reusable on
the matching stack; it establishes no overnight, sleep, app-restart or native
Windows guarantee. A prior extended test was interrupted without handback and
remains incomplete. Keep the host awake and its tool connection live.

## Intake, interruption and manual resume

On return, require exit 0, the expected session ID, and a `handed-back` event newer
than the checked cursor. Read `status --after CONSUMED_SEQUENCE` using the same
session location; reject a replaced session. Reconcile the exact candidate fingerprints,
verdicts, protections and task-owned commands. Persist the consumed event cursor
with that reconciliation before dispatching further work. Repeated delivery of
an already consumed event must not dispatch the same work twice. Follow the
preserved engineering strategy; handback grants no missing acceptance.

On timeout, cancellation, an early wrapper yield, or runtime failure, account for
and stop only the known waiter; verify it stopped using the host's process
controls. In a live PTY, Ctrl-C can stop that specific waiter. Leave the review
server and candidate protection intact. App closure/restart and computer sleep
can interrupt the tool connection, so inspect durable state and command ownership
on resume instead of promising continuation while the host is unavailable.

When an idle wait is needed but a qualified wait is unavailable or interrupted,
state plainly: decisions are saved, automatic
continuation is unavailable, and after **Finish and hand back** the user should
send `Resume the attended review` in this same chat. Read the saved session and
cursor on that user turn. Offline exports still require the existing import step.
Do not silently install a heartbeat or substitute a small agent that polls.
