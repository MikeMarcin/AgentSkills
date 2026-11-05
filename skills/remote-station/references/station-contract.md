# Station contract

The general station contract: identity, naming, launch and reset, the writer
lease, transports and the one-driver rule. Read it before launching a station on
a workstream checkout or changing station code. Status, takeover and hooks are in
[station control](station-control.md). What work a dispatcher sends to a station,
and with what authority, belongs to the dispatching workflow; for RFC work that is
implement-rfc's `references/remote-routing.md`.

## Terminology

- **Station** — a durable execution endpoint: one project, one workstream, one
  branch, one dedicated checkout, in one OS environment on one machine, with
  one recorded authority. A station outlives any session. No two writing
  stations share a checkout.
- **Station branch** — the only branch a station commits to and pushes.
- **Station endpoint** — the Claude Remote Control session or persistent Codex
  task currently bound to a station. Endpoints can reconnect; the station
  identity stays.
- **Controller** — a device steering an existing station session (another
  session via message, the claude.ai/code web page, the mobile app, a
  terminal). Controllers never gain separate write authority.
- **Driver** — the one controller that dispatches work to a station at a time.

## Configuration

`.mask/skill-config/remote-station/station.json` in the consumer checkout holds
the facts station code reads. `scripts/station_config.py` validates it (schema
`remote-station.config.v1`, documented by `schemas/station-config.schema.json`)
and refuses missing, malformed and unknown keys before any runtime starts. It is
resolved from the invoking checkout's Git root, an explicit `--repo-root`, or
`REMOTE_STATION_PROJECT_ROOT`, never from the skill's physical path.

| Key | Meaning |
|---|---|
| `project` | Project token recorded in station files and lease names |
| `display_name` | Human name used in messages |
| `origin_repo_name` | Repository token the checkout's `origin` must name |
| `session_prefix` | First token of every station name |
| `station_registry_doc` | Repository document listing the stations in use |
| `workstreams` | Map of workstream token to `branch` and optional `platform` (`win`, `linux`, `mac`); must contain `main` |

A consumer migrating from implement-rfc's `project.json` copies these keys and
sets the new schema. Drop workstreams whose branches no longer exist.

## Session naming

`<project>-<workstream|role>-<platform>[-<machine>]`, lowercase, hyphenated.

- project token: `session_prefix` from `station.json`
- workstream token: a key of `workstreams`, or `main` for the project integrator;
  the platform token is omitted when the workstream is itself platform-bound (a
  per-platform verification lane)
- platform token: `mac` | `linux` | `win`
- machine suffix: mandatory whenever the same platform exists on more than one
  machine (`<prefix>-<workstream>-linux-example-win-host` vs `<prefix>-<workstream>-linux-nuc`)

Examples: `<prefix>-main-mac` for the integrator on a Mac, `<prefix>-win-example-win-host`
for a platform-bound Windows lane on machine `example-win-host`.

Names are transport labels, not authority. Cross-machine messaging resolves
duplicates to silent auto-variants, so a colliding name misroutes without an
error; keep the authoritative list of names in use in the station registry
(`station_registry_doc`) and never rely on a variant name. Authority always comes
from the station file plus the dispatcher's identity guard.

## Station registry

The document named by `station_registry_doc` is the single station registry:
workstream, station branch, machine, environment, and provisioning status per
station. Add a row there before launching a new station; never reuse a name for a
different checkout.

## Station identity file

The launcher writes `.remote-station.json`, untracked, at the checkout root:

```json
{
  "schema": "implement-rfc.remote-station.v2",
  "station_id": "stn-8f2c41d0",
  "station": "<prefix>-<workstream>-linux",
  "project": "<project>",
  "workstream": "<workstream>",
  "environment": "wsl2",
  "branch": "<workstream branch>",
  "authority": "lane-commit",
  "codex": {
    "thread_id": "019c9e77-1f64-7000-a651-2ad109d03fc3",
    "thread_name": "<prefix>-<workstream>-linux",
    "cli_version": "0.151.0"
  },
  "claude": {
    "session_id": "session_0123456789abcdefghijklmn"
  }
}
```

- `station_id` is generated once and reused on relaunch; the name may be
  cosmetically adjusted, the id may not.
- `station` is the name the launcher reads back on relaunch, machine suffix
  included. The suffix is inferred from this field exactly as the workstream
  is, because a recomputed shorter name does not make the checkout a different
  station — it keeps `codex.thread_id` and then refuses to rename that task.
  An explicit `--machine` that contradicts the record is a refusal.
- `codex.thread_id` is the immutable persistent-task identity and is also
  reused on relaunch. `thread_name` equals `station`; a mismatch is a hard
  stop. `codex` may be `null` before Codex provisioning, including `--no-codex`
  and the deprecated `--no-server` path.
- `claude.session_id` is the exact Remote Control identity recorded after a
  fresh named session starts. Relaunch uses `--session-id`; it never selects a
  conversation by recency across linked Git worktrees. The field may be absent
  or `null` in an older registry, causing one fresh named session and migration.
- `environment` is one of `macos`, `windows-native`, `wsl2`, `linux-native`.
  WSL2 counts as a Linux station, never a Windows one; native Windows work
  runs only in a `windows-native` station.
- `authority` is `lane-commit` (commit and push the station branch) or
  `read-only-proof` (build, test, verify, report; no commits, pushes, or
  tracker edits). A station without provisioned push credentials operates as
  `read-only-proof` regardless of what this field says.

`schemas/remote-station.schema.json` validates the file. The file is
machine-local configuration, not dispatch input: a message cannot rewrite it,
and a hand-edited file that disagrees with the live checkout (wrong branch, wrong
repo) is a hard stop, not truth.

The exact former marker `aito.implement-rfc.remote-station.v2` describes the
same v2 fields and remains read-compatible under the full guard/lifecycle
checks. New launchers emit the canonical marker above. Reading compatibility
never rewrites the registry or changes the bound endpoint, generation or lease.
Successive authorized turns through the current endpoint need no supervisor
restart; ownership transfer follows [station control](station-control.md).

The `implement-rfc.*` names of the station file, lifecycle state, lease and
envelope schemas, and the Git-directory file names, predate this skill. They are
frozen so existing stations resume unchanged; do not rename them.

## Launch and reset controls

Run `scripts/launch_remote_station.py` from anywhere in the consumer checkout,
through its skill link, the `launch_remote_station` command, or with an explicit
`--repo-root`. Normal launch starts or resumes both runtimes under the writer
lease. Use `python3` on macOS, Linux and WSL2; use `py -3` in native Windows
PowerShell or cmd.

| Option | Behavior |
|---|---|
| `--fresh` or `--fresh both` | New context for both enabled runtimes |
| `--fresh codex` | Archive the validated idle Codex task and create a replacement |
| `--fresh claude` | Clear the saved Claude binding and start a new named session |
| `--no-claude` | Run Codex only; keep the terminal open to hold the lease |
| `--no-codex` | Run Claude only, retaining any saved Codex binding |
| `--help-all` | Show setup and troubleshooting flags |

Fresh context keeps station identity, name and machine suffix. With one service
skipped, `--fresh` affects only the enabled runtime. Skipping does not stop an
already-running endpoint. Active or unrelated Codex tasks are refused; history
is archived, never deleted. If Desktop holds an idle task's writer, archive that
exact task in Desktop and retry. An archived catalog entry is recognized even
when `thread/read` omits the archived flag. Bootstrap failures include the
server's error message. Reading a task's turns uses a history-sized timeout,
because a long-lived station task can take far longer than one ordinary request.

Claude uses the compact `claude remote-control --name NAME --spawn session`
server interface, showing status and connection controls rather than a terminal
conversation. A fresh session may not appear in peer lists until a controller
connects. The launcher watches for the exact bridge session ID throughout the
server lifetime. Restarts use that ID, never a directory-wide recency guess.
`--require-claude-resume` (legacy `--continue`/`-c`) refuses without that ID;
normal launch attempts resumption and can start fresh after a startup refusal.
An explicit fresh Claude launch clears the old binding before starting, so an
interruption before connection cannot silently resume the discarded context.

Every launch with Claude enabled prints a note that Claude replies are
unconfirmed. The launcher cannot observe receipt by the receiving dispatcher: replies
held or refused there usually mean that dispatcher's computer lacks
`"crossSessionInbound": "accept"` in `~/.claude/settings.json`, which the station's
own setting cannot verify. A running station or an accepted send confirms neither
delivery nor that the station is offline. Confirm receipt in the dispatcher before
unattended dispatch.

The legacy `--fresh-station` additionally discards station identity and the
inferred machine suffix. It archives validated station tasks before provisioning
under the canonical name. It refuses with strict Claude resume, `--no-server`,
or either skipped service; use `--fresh` for ordinary context resets instead.
Legacy `--new-codex-session` and `--new-claude-session` remain accepted.

## Writer lease

`scripts/station_lease.py` makes single-writer mechanical rather than
conversational. It holds an OS-level exclusive lock for the lifetime of the
wrapped process and releases it automatically on exit or crash:

```sh
python3 scripts/station_lease.py run --role station-writer --station <station> -- <command...>
python3 scripts/station_lease.py status --role station-writer
```

- `station-writer` locks inside the checkout's own git dir: one writer per
  checkout, independent per worktree.
- `project-integrator` locks inside the common git dir: one integrator per
  repository across all worktrees.
- `run` acquires nonblocking and execs the command with the lock inherited; a
  held lock exits with status 75 and prints the recorded holder. The OS lock
  and readable holder sidecar are separate so native Windows can report the
  owner while the lock is held. `status` reports free or held plus the holder
  record.

The unified launcher wraps its station supervisor in `run` — the `main`
workstream under the `project-integrator` role, every other workstream under
`station-writer` (so on an integrator checkout the station-writer lock being
free while the integrator lease is held is the expected state, not a gap).
The supervisor holds the lease while both provider endpoints are reachable;
when it stops, the Codex task may persist; reconcile its active writers before reuse. The
lease guarantees there are never two *wrapped* writers in one checkout; it
does not authenticate which one — the guard, ownership rules, hooks, and
branch-restricted push credentials do that. The deprecated direct-Codex path
prints its own lease-wrapped command.

The guarantee is only as complete as launch discipline: the lock cannot see a
session that was never wrapped, and the guard only inspects envelopes, not
another process's file writes. So a checkout bound to a station accepts edits
from that station's session only — an ordinary unwrapped session must not
edit it, and a controller steering the station is still the station's one
writer, not a second one.

## Transports

- **Claude Code**: stations are `claude remote-control --spawn session`
  servers launched by `scripts/launch_remote_station.py`; dispatch is
  `SendMessage` with the work message. Server, spawn-mode, and messaging facts
  live in [runtime compatibility](runtime-compatibility.md).
- **Codex**: stations are persistent tasks provisioned through the
  host-local App Server and exposed through Managed Remote. Unix hosts start
  the installer-managed daemon and use its WebSocket-over-stdio proxy; native
  Windows leaves Remote exclusively with Codex Desktop, opens or focuses it
  through `codex app <checkout>`, and uses a short-lived standalone JSONL App
  Server only for local task provisioning—never for `remoteControl/*`. A newly
  created task receives one non-mutating bootstrap turn
  so it is durable and eligible for controller task lists, then the helper
  unsubscribes before exit. A relaunch may clear and retry one exact stale
  active-writer result only when all recorded turns are terminal; an
  in-progress turn always refuses. App Server is provisioning only: the driver
  uses Codex App persistent-task operations to
  locate exactly one connected task by exact host, station name, checkout, and
  recorded thread ID, send the work as a follow-up, wait, and read the completed
  turn. Zero or duplicate matches refuse.
  `codex --remote` is a diagnostic terminal client, not the station registry or
  driver transport.
- **Mobile / web**: Claude endpoints are reachable from claude.ai/code and the
  Claude mobile app; Codex endpoints are reachable through Remote on paired
  ChatGPT clients. Driving either endpoint directly is normal operation, and
  the dispatcher's guard still refuses out-of-scope asks.

Both endpoints may be connected, but **exactly one driver dispatches work to a
station at a time**. The lease prevents another station writer; there is no
cross-provider turn mutex, so concurrent Claude and Codex turns in one station are
unsupported. An immediate Codex send acknowledgement is never the reply.

## Desktop capability checks

A provisioned task and a completed bootstrap prove task materialization, not
desktop automation capability. Keep the launcher's exact bootstrap turn and
temporary provisioning helper free of tool probes: bootstrap-only history is
also used to recognize safe task migration. Check capabilities in a normal turn
of the exact station task reached through its controller route.

Before declaring computer use unavailable or asking the user to perform UI work,
read the installed computer-use skill for the station's OS and follow its
initialization and recovery instructions. Discover its required deferred tools
when the runtime provides tool discovery. A browser automation surface reporting
no native apps proves only that surface's limitation; it does not establish that
the separate platform computer-use runtime is unavailable.

If the installed Windows computer-use skill specifies `node_repl` with
`import("@oai/sky")`, use that runtime and its documented window inventory and
capture APIs. Browser-only `cua_repl` inventory and guessed native methods are
not substitutes. Follow the installed skill if its runtime changes; do not
spawn helper executables or create a custom protocol client to bypass it.

Use the smallest probe needed for the requested work: enumerate windows on the
station host, select a returned target, then inspect its state. Follow the
platform skill's activation/refresh recovery for a minimized or stale target,
within the user's authorized task. Report the exact task/host, runtime and
observed outcome. Distinguish a missing required tool after discovery, package
initialization failure, helper connection/pipe failure, empty window inventory,
and target-specific capture failure. A failed capture of one minimized window
does not negate successful enumeration or establish a host-wide outage. Stop
at the installed skill's recovery boundary and report the actual remaining
limitation; do not infer it from an unrelated runtime or a different task.

## Deferred hardening

Recorded so later work starts from the same intent: a cross-provider turn
mutex, a station catalog tool, a merge queue, stronger specialized-tool hook
coverage, a Claude hook equivalent, and a cloud executor class. None of these
change the contract above; they mechanize it.
