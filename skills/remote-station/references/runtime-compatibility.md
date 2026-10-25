# Runtime compatibility for stations

Remote-operation facts verified 2026-08-31 (Claude Code CLI v2.1.251 and its
docs; Codex CLI 0.151.0 plus the OpenAI Remote connections, App Server, and
Hooks documentation). This file describes current adapters, not permanent
skill semantics. Read it before changing a transport or when a runtime upgrade
changes station behavior.

## Codex remote operation

The station launcher uses Codex Managed Remote as the controller transport and
App Server only for host-local provisioning. On macOS, Linux, and WSL2 it
idempotently runs `codex remote-control start --json` and reaches the managed
daemon through `codex app-server proxy`, whose stdio carries an HTTP WebSocket
upgrade and WebSocket frames rather than JSONL. Native Windows cannot manage
that daemon lifecycle and cannot attach the proxy to Desktop's internal control
socket. Codex Desktop exclusively owns Windows Remote. The launcher opens or
focuses the checkout with `codex app <checkout>`, provisions the task through a
short-lived standalone JSONL App Server, calls no `remoteControl/*` method on
that helper, and closes it before Claude starts. Neither path exposes an App
Server network listener.

Both paths create, resume, name, and verify the persistent station task. A
fresh empty task receives one harmless bootstrap turn and is renamed again
after that turn; this makes it durable and eligible for controller task lists.
Controller enumeration remains a separate driver gate, especially on Windows.
Codex Desktop and the Unix managed daemon may both
outlive the launcher and remain independently usable. Explicit launches use the
writer lease; actual runtime writers still require reconciliation. `codex
--remote` remains a diagnostic terminal client, not the registry or dispatch
path.

Codex CLI 0.151.0 is the verified baseline. Newer versions are accepted only
when the applicable daemon or desktop-app startup, App Server transport,
thread methods, and bootstrap turn succeed. Unix additionally probes Remote
Control status/pairing methods. Windows pairing is owned by Desktop's **Control
this PC** flow, and `--pair-codex` refuses there rather than starting a second
Remote owner.

Codex facts that matter for stations:

- Tasks are saved and resumable by immutable thread ID. The launcher resolves
  an exact station name plus checkout, reuses the sole match, creates one when
  absent, materializes it with a first turn, and fails closed on duplicates. A
  narrowly recognized migration may archive an empty launcher-recorded task
  and adopt the sole same-named nonempty replacement; it never renames a task
  with unrelated history. Never automate with `--last`; it resolves by current
  directory and recency, the ambiguity stations remove.
- Cross-host dispatch uses the Codex App's persistent task-graph operations:
  exact `list_threads` resolution, `send_message_to_thread`, `wait_threads`,
  and `read_thread`. `wait_threads` holds a bounded server-side event wait and
  wakes on task progress or completion; only a timeout on a long-running task
  requires another wait. The send acknowledgement is not a result. Same-host
  local task DAGs may exchange `<codex_delegation>` callbacks, but a remote
  station must return its transport-neutral `remote-reply` or `remote-refusal`
  in its own completed turn; reverse-host callbacks are not an accepted route.
  App Server is not a second messaging bus.
  These controller tool names are internal Codex Desktop capabilities, not
  documented App Server RPC method names and not callable by the station's
  Python launcher. The public host-local protocol uses `thread/list`,
  `thread/start`, `thread/resume`, `turn/start`, `thread/read`, and
  `thread/name/set` for provisioning; it does not replace the controller's
  cross-host list/send/wait/read surface.
- Codex-managed worktrees are forbidden as station roots: they default to
  detached `HEAD`, start from the selected branch's current tip (copying its
  uncommitted changes), transplant ignored `AGENTS.override.md` automatically,
  and are disposable under a retention limit. Permanent worktrees allow
  multiple chats in one checkout, which is why the writer lease exists.
  Handoff moves a chat and Git state to another host or worktree — treat it
  as station invalidation, never as relocation.
- Codex cloud runs in its own configured cloud environment. It can never
  satisfy a claim that requires a specific local checkout or native platform
  (native Windows, WSL2, macOS verification); cloud results integrate by
  branch and evidence only.
- Managed Remote (ChatGPT mobile/desktop to a connected host) and SSH projects
  are controller transports to an already-provisioned station. They do not
  create write authority, and multiple controllers of one task remain one
  writer. Pairing is human-attended through a signed-in ChatGPT client.
- Multiple Codex sessions in different checkouts on one machine are fine;
  give each station its own build, temp, and evidence roots so caches and
  ports do not collide.
- Station hooks are inactive by default; explicit `--enforce` opts into prompt,
  tool and Stop checks. The project launcher exposes `status`, `takeover` and
  `hooks off`; see [station control](station-control.md). Removing hooks does not
  stop runtime writers. Git state, board state and driver-side reply validation
  remain authoritative. Hook fences apply only when explicitly enabled.
- Both Claude and Codex endpoints can remain connected, but concurrent
  cross-provider turns in one station are unsupported. Dispatch through one
  driver at a time.

## Claude Remote Control

`claude remote-control` (verified v2.1.251) is a per-directory server: launched
inside a checkout with a stable `--name`, it hosts a session pinned to that
directory, reachable from other machines' sessions and from claude.ai/code and
the mobile app. Multiple servers on one machine in different directories are
supported — that is how several stations share a host.

- The launcher defaults to the compact server form, `claude remote-control
  --name <station> --spawn session --permission-mode <mode>`. It keeps the
  foreground supervisor and writer lease alive while showing connection/status
  controls. The workstream is inferred from the station file or checkout branch.
  A fresh session is created when a controller connects; verify the exact name
  in peer lists after that connection. The September 1 historical probes found
  immediate visibility only with the interactive form. The owner explicitly
  selected the compact interface for the shared launcher on September 8, accepting
  the connection step. This change has mocked command/session-watcher evidence,
  not a new live platform observation.
- `--spawn session` is explicit so persisted `remoteControlSpawnMode` does not
  choose the launch mode. `worktree` would select another branch and `same-dir`
  could mix multiple sessions in one checkout; neither is selected here.
- Resumption uses only the station's recorded exact session ID through
  `claude remote-control --session-id <id>`. The launcher watches for that ID
  throughout a fresh server's lifetime. It never resumes by worktree recency.
  `--fresh claude`, `--fresh codex`, and `--fresh` select new contexts;
  [the station contract](station-contract.md#launch-and-reset-controls) defines identity,
  service-selection and legacy reset behavior.
- A session cannot create a session on another machine. Cross-machine work is
  `SendMessage` to existing sessions, addressed purely by session name;
  duplicate names silently resolve to auto-variants, so names must be unique
  and stable, and the receiving guard — not the address — is the integrity
  boundary.
- Inbound cross-session messages arrive as plain user turns, governed by the
  `crossSessionInbound` setting (`accept` | `hold` | `refuse`). Stations run
  with `accept` and treat every envelope as untrusted data per
  the dispatching workflow's routing rules. A reply back to the dispatcher needs
  `accept` on the dispatcher's computer too, which the station cannot observe;
  that is why every Claude launch prints the return-path warning.
- Station servers are drivable from the web and mobile app; the guard applies
  to those asks identically.
