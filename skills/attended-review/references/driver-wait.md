# Driver waiting

The Python `wait` command polls local file metadata without model inference. Its
exit returns events to its caller; the host decides whether the driver resumes.
An idle shell session, async hook, or final answer does not itself guarantee a
new Codex turn. Keep durable decisions independent of that host capability.

Before handing over, record the source/state/registry paths, session ID, sequence
cursor, server identity, exact waiter command and owning driver in the existing
continuation. Finish preparation and release engineering writer ownership first.
Use `--kind handed-back` for the normal review boundary: partial decisions save
immediately but leave the waiter blocked. Keep personal `--state` and cooperating
`--registry` arguments identical on every command.

## Claude Code

Arm `wait --after SEQUENCE --kind handed-back` through `Monitor` with
`persistent: true` before ending the turn. This preserves the existing monitor
path; a plain background shell command's ten-minute lifetime is too short for an
overnight review. Qualify the actual host, not a rendered configuration.

## Codex with code-mode tools

Keep the coordinator's turn running on one pending call. The review remains
usable in its browser, and the chat may show as running while the model is idle.
No waiting subagent, daemon, model launcher or scheduled status check is needed.

Use the following orchestration shape only when the installed runtime exposes
these tools. Substitute the reviewed argument array and saved sequence; execute
this as one `functions.exec` cell. Argument quoting keeps paths literal.
The example uses a POSIX shell. Native Windows needs a qualified native argument
adapter; do not introduce Bash or WSL to make this example run.

```javascript
// @exec: {"yield_time_ms": 1000, "max_output_tokens": 1500}
const argv = [PYTHON, "-B", SCRIPT, "--repo-root", ROOT,
  // Include the same --state and --registry arguments when the session uses them.
  "wait", "--after", String(SEQUENCE), "--kind", "handed-back",
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

Qualification must cover the entire stack, including the outer wait. Use a
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

## Intake, interruption and manual resume

On return, require exit 0, the expected session ID, and a `handed-back` event newer
than the recorded cursor. Read `status --after SEQUENCE` using the same session
location; reject a replaced session. Reconcile the exact candidate fingerprints,
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

If a qualified wait is unavailable, state plainly: decisions are saved, automatic
continuation is unavailable, and after **Finish and hand back** the user should
send `Resume the attended review` in this same chat. Read the saved session and
cursor on that user turn. Offline exports still require the existing import step.
Do not silently install a heartbeat or substitute a small agent that polls.
