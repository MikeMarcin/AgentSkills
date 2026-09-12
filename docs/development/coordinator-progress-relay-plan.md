# Coordinator progress relay — plan, revised and implemented 2026-09-11

Filed as [ASK-0073](../issues/30-in-progress/ASK-0073-coordinator-progress-relay.md).
This revision replaces the 2026-09-11 draft: the host question is settled, the wake
budget is the design, and the helper serves Claude Code, Codex and a terminal from one
command. Implemented in the working tree; AC5 waits on a real visible run.

## Problem

The coordinator dispatches one integrator and waits (`SKILL.md` step 3). Slices run
inside that integrator, so nothing reaches the owner between milestone returns. Observed
on SampleReview, 2026-09-11: a milestone ran past two hours and produced roughly two
sentences of coordinator text, while the integrator committed per slice every five to
twenty minutes and the in-flight slice showed as the owned dirty working set. The durable
trail already exists at the right granularity; no path surfaced it.

## Outcome

An owner who asks for a visible run sees one coalesced burst of trail lines per wake gap
in the coordinator chat. The coordinator spends no wake the trail did not earn: nothing
while quiet, at most one per gap while busy, plus the integrator's own completion. The
default run spends no relay wakes at all. The same helper serves an owner's terminal and a
Codex driver without a second mechanism, a new writer, or any state file.

## Settled host observations

Both recorded under `### Foreground dispatch and Monitor events (2026-09-11)` in
`references/runtime-compatibility.md`:

| Question | Observation | Consequence |
|---|---|---|
| Do `Monitor` events reach the session during a foreground `Agent` dispatch? | No. Five ticks emitted during a 95-second dispatch arrived as one batch after it returned; no turn ran between them. | An armed trail beside a foreground dispatch costs nothing and shows nothing. Variant A of the draft is not observability. |
| Does a background `rfc-integrator` keep `Agent`? | Yes. Tools `Read, Bash, Edit, Write, Skill, Agent, SendMessage, TaskStop`; `Grep` and `Glob` absent. It dispatched an `rfc-utility` leaf and returned its reply. | Background dispatch is viable on this host, so a visible run uses it. |

The draft's variant table keyed on rendering alone. The revised design separates "the
owner sees a line" from "the coordinator takes a turn" and treats the second as the cost.

## Design

### Wake budget

A wake is one coordinator turn on a large cached prefix. Each mode states its budget:

- **Default run.** Foreground dispatch, zero relay wakes, no in-session trail. An owner
  who wants to watch runs the helper with `--follow --min-gap 0` in a terminal.
- **Visible run (owner asks).** Background integrator dispatch; `--follow` armed under
  `Monitor` with `persistent: true`. Follow mode holds events and emits them as one
  multi-line burst no more than once per `--min-gap` (default 900 seconds). Lines within
  200 milliseconds batch into one notification, so one burst is one wake. Wakes per hour
  are at most 3600 divided by the gap, plus one completion, and zero while quiet.
  `--quiet-after` (default off) adds one heartbeat only when the in-flight set changed
  and nothing else was emitted for that long. The watch is stopped with `TaskStop` at
  consume time.
- **Codex driver.** No `Monitor`, and no new wake source. `wait_threads` already wakes on
  a timeout; on each such wake the driver runs one-shot `--since CURSOR`, forwards the
  digest, keeps the printed `cursor` line in its memo and waits again. The same one-shot at
  consume time turns any milestone return into a trail summary on either host.

### Relay turn

The relay turn forwards the burst's lines as the user-visible update, uses no tool,
makes no board query and no second dispatch, and ends. The integrator owns every fact
behind those lines. A quiet trail with an unchanged in-flight set is a fact to report, not
a reason to query, message or replace the child. Relay drift is the named risk; the
reference text and AC5 are the control.

### Helper: `scripts/progress_trail.py`

```
progress_trail.py --repo-root ROOT [--since SHA] [--follow] [--interval S] [--min-gap S] [--quiet-after S] [--json]
```

- Resolves the consumer through `project_config.resolve_context` with the root explicit;
  a shared skill link never selects its consumer. Refuses a missing, unmanaged or
  non-root path and a `--since` that is not an ancestor of `HEAD` with exit 2.
- One line per committed lane transition (`claim`, `finish`, `park`, `block`, `move`),
  scoped commit, uncommitted `pending` lane move, and changed `in-flight` set. Lane
  transitions pair the card ID across the commit's deleted and added board paths, because
  a finish rewrites the card enough that Git reports delete plus add rather than a rename.
  A commit that moves a card is one transition line, never a transition plus a commit.
- Runs Git with `GIT_OPTIONAL_LOCKS=0`, so it never refreshes the index or blocks a claim
  or finish in progress. The test digests every byte under the consumer, `.git` included,
  before and after each run.
- Named to avoid `slice_events.py`, which is the lifecycle event store, a different record.

## Acceptance

See the card. AC1 (one sentence, at most 250 bytes, mechanics behind the pointer), AC2
(helper behavior over two linked consumers), AC3 (coalescing, quiet behavior, one-shot
cursor), AC4 (dated observations and the dispatch mode that follows them) are accepted in
the working tree. AC5 (a real visible run with clean relay turns) is open.

## Non-goals

Smaller milestones to force more returns; coordinator polling of the child or the board;
a second board or any new durable state; changes to slice assignment, routes, permissions
or milestone selection; Codex lane progress, which has its own lane log.

## Risks and current state

- **Relay drift.** A coordinator woken repeatedly is a coordinator tempted into
  engineering. Controlled by the reference's relay-turn text and AC5.
- **Rate limiting.** A flooding monitor is stopped by the host. The coalescing gap is the
  control; re-arming mid-milestone is a second wake source, not a repair.
- **Background tool set.** `Grep` and `Glob` were absent from the background integrator;
  `Bash` covers both. Recorded, not worked around.
- **Two in-progress cards.** ASK-0070 and ASK-0073 are both In Progress in the working
  tree, which the queue reports as an ambiguous claim. ASK-0073 was written directly in
  owner-selected direct mode; the owner settles ordering and commits.
- **Mid-run reference edits.** Consumers link this skill and integrators read
  `references/*.md` lazily. Land these changes when no run is active in a linked consumer.
- **Manifest drift.** The portable digest changed; linked consumers re-stage their roles
  lock the usual way.

## Terminal watch, unchanged

The helper replaces the hand-rolled loop from the draft with one supported command:

```sh
python3 .claude/skills/implement-rfc/scripts/progress_trail.py --repo-root "$PWD" --follow --min-gap 0 --interval 30
```
