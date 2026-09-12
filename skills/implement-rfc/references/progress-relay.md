# Progress relay

The slice trail is the consumer's existing durable record: board lane transitions,
the integrator's scoped commits and the owned dirty working set. Relay forwards
that record. It writes nothing, holds no state file and never queries the child.

`scripts/progress_trail.py --repo-root ROOT` reads the trail through the project
config contract with the root explicit. Every emitted line is one of: a lane
transition committed by the board (`claim`, `finish`, `park`, `block`, `move`), a
scoped commit, an uncommitted `pending` lane move, or an `in-flight` count of
changed non-board paths. A commit that moves a card is one transition line, never
a transition plus a commit line. Git runs with optional locks disabled, so the
helper never blocks a claim or finish in progress.

## Wake budget

A wake is one coordinator turn on a large cached prefix. The budget is the design:

- **Default run (no relay).** Foreground integrator dispatch; zero relay wakes.
  Monitor events queue behind a foreground `Agent` call and arrive as one batch
  after it returns, so an armed trail adds nothing to the transcript mid-run
  ([observation](runtime-compatibility.md#foreground-dispatch-and-monitor-events-2026-09-11)).
  An owner who wants to watch runs `--follow --min-gap 0 --interval 30` in a
  terminal; it costs the run nothing.
- **Visible run (owner asks).** Dispatch the same `rfc-integrator` in the
  background and arm `--follow` under `Monitor` with `persistent: true`. Follow
  mode coalesces: it holds events and emits them as one burst no more than once
  per `--min-gap` (default 900 seconds), and the burst lands as one notification.
  Wakes per hour are therefore at most 3600 divided by the gap, plus one for the
  integrator's completion, and zero while the trail is quiet. `--quiet-after`
  (default off) adds one heartbeat only when the in-flight set changed and nothing
  else was emitted for that long. Stop the watch with `TaskStop` when the
  integrator's result is consumed; a persistent monitor outlives the milestone.
- **Hosts without Monitor (Codex).** No new wake source. Each time the bounded
  wait returns without a result, run one-shot `--since CURSOR`, forward the digest,
  keep the printed `cursor` line in the run memo, and wait again. The same one-shot
  at consume time turns any milestone return into a trail summary on either host.

Keep the helper's filter to lane transitions, commits and changed in-flight sets. A
flooding monitor is stopped by the host; re-arming mid-milestone is a second wake
source, not a repair.

## Relay turn

The relay turn forwards the burst's lines as the user-visible update, uses no tool,
makes no board query and no second dispatch, and ends. The integrator owns every
fact behind those lines. A progress event is a trail observation, not a milestone
return: acceptance, dispatch, board reading and engineering conclusions stay in
step 4, on the integrator's compact result.

## Quiet trail

From the trail alone a long slice looks exactly like a stalled run. The in-flight
set separates them: a growing set is a slice in progress, an unchanged set past the
heartbeat is a fact to report, not a reason to query, message or replace the child.

## Background integrator

A background `rfc-integrator` keeps `Agent` and dispatched a leaf in the dated
observation, with `Grep` and `Glob` absent from its tool list; `Bash` covers both.
Its completion reaches the coordinator as a notification. Its children still return
inside its own turn, as [Nested child results](runtime-compatibility.md#nested-child-results-2026-09-11)
requires, so it must not background its leaves.
