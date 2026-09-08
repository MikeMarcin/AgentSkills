---
id: "RFC-ASK-0005"
title: "Bounded deterministic execution and durable delegation"
status: "Accepted"
owner: "MikeMarcin"
created: "2026-09-07"
---

# RFC-ASK-0005: Bounded deterministic execution and durable delegation

Pack IDs are provisional until the AgentSkills integrator reserves the live block.
This is a new RFC, not an amendment silently rewriting settled RFC-ASK-0001–0004.

## Decision and scope

Keep one intelligent integrator responsible for engineering judgment. Add a small,
local, deterministic **slice runner** bundled with `implement-rfc` that performs
already-selected control flow without repeatedly invoking a model. Use it for a
bounded stable slice; retain direct execution for small or tightly coupled work.
Do not add a mandatory LLM task-master persona, general workflow language, fleet
scheduler, long-running daemon, or hosted service.

The runner owns dependency readiness, dispatch, waiting, collection, deadlines and
bounded recovery. Workers own their bounded implementation/investigation. The
integrator owns scope, decomposition, interpretation, acceptance and integration.
A successful process is not an accepted engineering result. Planned semantic gates
return to the integrator even when all subprocesses succeeded.

### Existing building blocks, not a replacement workflow

Reuse `scripts/project_config.py` for consumer context, `issue_board.py` for the live
board, `record_evidence.py` for exact command/result recording, and the existing
station/lane helpers where a supported adapter genuinely needs them. The uploaded
source already has `rfc-test-runner`; do not resurrect the old `rfc-verifier` role.
The test-runner role remains an optional mechanical agent interface. Prescribed
commands should normally run as code, not a new model session.

`issue_board.py finish` remains the guarded bookkeeping mutation consuming the
integrator's explicit acceptance. The runner never creates an acceptance document
by interpreting “tests passed” or a worker's self-report. It may transport an
already-approved immutable document to the existing helper, but may not enlarge
that approval. Existing main-only reservation, claim and commit rules remain.

## Work-order contract

New public helper: `scripts/run_slice.py`. Proposed commands:

```text
run_slice.py validate --order FILE
run_slice.py start --order FILE --approve-order DIGEST
run_slice.py status --run ID --json
run_slice.py wait --run ID --until gate-or-terminal
run_slice.py cancel --run ID
run_slice.py recover --run ID --inspect
run_slice.py recover --run ID --report-only --task ID
```

These are to be implemented; the collector payload does not implement this runner.
Start is foreground/event-driven by default. Host-managed detachment is an explicit
adapter capability, not a promise that a killed shell leaves children supervised.
`wait` uses a blocking local/event primitive; it does not start an LLM poll loop.

One work order describes one stable slice, normally a few tasks. Begin with a
128 KiB order bound and 32 tasks maximum. These are configurable implementation
limits, not claims about optimal cognitive task size. Use JSON with four task
kinds: `command`, `agent`, `collect`, `integration_gate`. There are no expressions,
embedded templates that evaluate code, dynamic loops, or model-written callbacks.
Tasks reference an existing card/acceptance boundary rather than copying the RFC.

Required information: consumer root binding, invocation root, slice/card ID,
base revision plus approved dirty-path baseline, ordered dependencies, exact
owned/readable paths, expected report/artifact destinations, route/profile digest,
permission policy, timeout/dispatch budgets, retry classification and the final
integration gate. The order itself is data until explicitly admitted. Its digest
is a stale-plan guard, not cryptographic authority against a hostile same-user
process. Never regard a worker-authored order as approval of its own privileges.

Commands use argv arrays with each path one argument. Shell code is permitted only
through an explicitly named reviewed project script and interpreter in the admitted
order; no `eval`, shell fragments assembled from JSON, or transcript commands.
Command exit predicates and expected artifacts are deterministic. `exit 0` alone
cannot assert coverage or semantic acceptance. A requested test runner that ran
zero selected tests must report an incomplete check, not success.

At dispatch, recheck physical root, approved input/ownership boundary, capabilities
and route. An unrelated file change need not invalidate an isolated read-only
check; a relevant source/permission/route change must. Mutating siblings either
have disjoint enforceable ownership/worktrees or run serially. A path declaration
is not an OS sandbox: report the enforcement actually provided by the native host.
Default concurrency is one mutation task; bounded independent read-only siblings
are opt-in. The integrator does not reread every worker file merely for ceremony.

## Small durable state, not another issue tracker

Use consumer-local ignored state under `.mask/generated/implement-rfc/runs/<run-id>`
when the existing resolver validates it, or the designated user-state fallback
for a read-only checkout. Never derive the output root from the installed skill
path: it may point into AgentSkills or a read-only MASK content-addressed artifact.
Use a single writer, one small work-order document, one append-only event stream,
and bounded report/evidence files. The issue board remains the only live tracker.

Identity tuple: `run_id`, `task_id`, `attempt_id`, `driver_session_id`,
`driver_turn_id` where available. Record native IDs locally; the usage export
pseudonymizes them consistently. Repeated tasks using one session are separate
assignments. Session role labels are not assignment identities.

Logical task states:

```text
planned -> ready -> dispatched -> running -> report_ready -> collected
                                                |             |
                                       execution_failed   awaiting_integration
                                                              |
                                            accepted | rejected | superseded
```

`cancelled`, `blocked` and `completion_unknown` are explicit alternatives. Execution
termination, report production, report collection and integration acceptance are
separate events. Terminal attempts remain immutable; retry creates a new attempt.
A later correction to acceptance is an event, not an edited historical success.
No child owns the only copy of its children's result locations.

Write dispatch intent before side effects. If a crash happens between intent and
receipt, inspect the native runtime using the retained identity. Do not relaunch
an uncertain mutation merely because a result file is absent. Exactly-once side
effects are not promised. Guarantee at-most-one automatic launch per admitted
attempt, deduplicated completion handling, and explicit uncertainty at the crash
boundary. Commands with approved safe retry semantics may retry once; unknown or
non-idempotent operations require integrator disposition.

Use OS advisory writer locking and atomic replacements where supported. A torn
final event may be ignored with an explicit recovery warning; an interior corrupt
event is not silently skipped. Do not unlink busy locks or declare stale ownership
from a PID alone. Unrelated processes cannot submit approvals merely by placing
JSON in the report directory; local IPC/results must be bound to launched attempts.

## Reports, budgets and recovery

Delegated agents are leaves by default. They can propose another independent
question, but only the integrator/runner admits a new sibling assignment. This
avoids a turn-limited scout becoming the fragile owner of several children.

A compact report contains established findings/changes, evidence references,
uncertainty, and remaining work. Publish a partial result on a meaningful phase
boundary and on a soft budget signal when the driver supports it. Reserve synthesis
headroom; do not rely on agents counting their own turns exactly. Runtime turns,
API requests, tool calls and wall time are separate measures. An unsupported turn
limit is reported as unsupported, not simulated with a response-count guess.

On a structured eligible turn-limit termination with no usable report:

1. Collect any already-produced report and child evidence first.
2. If the driver supports same-context resumption with the required read-only
   restriction, permit **one bounded report-only continuation** within an explicitly
   preapproved recovery budget. It synthesizes existing findings; no new discovery,
   source mutation, delegation, model change or verification campaign.
3. Mark recovery attempted, report produced, collected and accepted separately.
   If resume is unsupported or still fails, preserve partial evidence and return
   `blocked`/`completion_unknown` to the integrator. No infinite resurrection.

Intentional user cancellation never triggers recovery. Cancel stops new dispatch,
signals only owned processes/turns, records the native acknowledgement if any, and
preserves unacknowledged cancellation as uncertain. It does not reset Git, delete
worktrees, discard edits or erase completed reports. Quota exhaustion is a capacity
block, not permission to buy credits, redeem resets or switch billing modes.

## Native adapters and the no-polling boundary

Implement driver-neutral operations `capabilities`, `launch`, `events`, `cancel`,
`recover_report` and `inspect_attempt`. Keep protocol adapters beside the runner;
no vendor SDK dependency in the portable command-only path.

**Codex:** use the installed CLI app-server protocol where supported. Initialize,
start/resume only a runner-owned thread, start a bounded turn, consume completion
and error notifications, and correlate thread/turn IDs. A native `turn/completed`
event is a lifecycle signal, not acceptance. Approval requests pause for the
existing authorized host/user; the runner does not auto-approve. Do not reinterpret
an in-editor native subagent ID as a resumable app-server thread without a tested
mapping. Inspect installed protocol capability instead of trusting a version
string or assuming future fields exist. Keep existing subscription authentication;
never provision an API key or quietly use an SDK route with different billing.

**Claude:** use the installed CLI's supported print/stream-json mode for
runner-owned companion sessions and exact native session IDs. Preserve permission
and settings behavior explicitly; do not assume subprocess companions inherit the
interactive agent's tool restrictions. Retain final result and usage records.
Native interactive subagents may have a different resume mechanism: use a supported
bridge or return an actionable limitation. Do not scrape the interactive screen,
tail the full hidden transcript into the integrator, or claim automatic recovery
for sessions the adapter cannot control.

Adapters must report which paths use true event-driven orchestration and which
still require native host intervention. A scripted status watcher is acceptable
when the underlying service lacks notifications **if it does not cause LLM calls**
and has a bounded polling cadence; idle status does not inflate model usage.

## Verification and rollout

First ship exact command batching, then durable agent dispatch/collection. Test
with fake drivers and disposable subprocesses: reordered/duplicate completion,
crash after launch-before-receipt, missing report, both scout interleavings from
the baseline, quota block, cancellation, changed root, stale order, conflicting
writers, output overflow and untrusted result content. Prove that 1,000 simulated
idle notifications produce zero model requests and no repeated dispatch.

Live qualification is narrow: one prescribed command batch and one bounded agent
slice through each claimed driver/platform, with exact runtime capability and
billing mode recorded. Native macOS and Windows claims need native evidence;
Linux tests here are not substitutes. Unsupported combinations retain direct
execution and explicit limitations. Enabling a runner never enables a cross-provider
switch. Measurement hooks record control wake-ups and durable outcome joins without
making every ordinary issue carry a new administrative checklist.

## Acceptance criteria

- **RFC-ASK-0005-AC01** — Prescribed command batches execute without model-mediated stage transitions, stop on failed/incomplete predicates, and always retain an integrator semantic gate.
- **RFC-ASK-0005-AC02** — Work orders, root/permission/route binding, dependency ownership, concurrency and budget limits are validated before execution; malformed or stale orders cause no dispatch.
- **RFC-ASK-0005-AC03** — Dispatch, report production, collection and acceptance are durably distinct; duplicate/reordered events and crash boundaries do not silently relaunch mutations or lose ownership.
- **RFC-ASK-0005-AC04** — Eligible truncation supports one bounded report-only recovery or an explicit unsupported/blocked result; intentional cancellation is never automatically resumed.
- **RFC-ASK-0005-AC05** — Codex and Claude adapters preserve native permissions and authentication, expose capability limits, and avoid LLM polling; each claimed native combination has direct evidence.
- **RFC-ASK-0005-AC06** — Existing board, evidence and test-runner contracts remain authoritative; direct execution is available, and no mandatory daemon, second tracker, automatic billing switch or fleet dependency appears.

## Implementation authorization

Accepted for implementation by the owner’s import-and-implement request on 2026-09-07. Native and owner-decision criteria remain open until exercised.
