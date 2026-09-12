# Runtime Compatibility

Verified against public product documentation on 2026-08-02; remote-operation
sections verified 2026-08-31 (Claude Code CLI v2.1.251 and its docs; Codex CLI
0.151.0 plus the OpenAI Remote connections, App Server, and Hooks
documentation). This file describes current adapters, not permanent skill
semantics.

## Codex

Current local Codex releases support project custom agents in `.codex/agents/*.toml`. A custom agent can set `model`, `model_reasoning_effort`, `sandbox_mode`, and nested session configuration. Applicable skill instructions can request delegation.

Generated Codex agents:

- use `sandbox_mode = "read-only"` for utility, scout, and reviewer roles;
- use `sandbox_mode = "workspace-write"` for bounded workers and the source-immutable test runner because their configure/build/test/package roots must be writable;
- enable nested sessions only for the designated `rfc-integrator`; its configured leaf-role allowlist remains policy where the host cannot enforce types;
- keep `[agents] enabled = false` for every worker, scout, reviewer, utility and test-runner leaf;
- select models from `config/routing.json`.

Important limitation: live parent permission and sandbox overrides can be reapplied to children. Do not rely on a generated read-only sandbox while running the parent with an override that widens it. Inspect `git status --short` after read-only work and reject unexpected writes.

Merge `config/codex-config.fragment.toml` into `.codex/config.toml` to set a
runtime cap of 10 concurrent child threads. The skill schedules only bounded,
useful lanes; the runtime cap is not a target.

### Remote operation

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
outlive the launcher and remain independently usable; the live writer lease and
hooks, not ownership of those processes, bound station mutation. `codex
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
- `.codex/hooks.json` re-asserts the guard on station prompts and before common
  mutating tools, and clears turn state on stop. Project-hook trust is
  human-attended through `/hooks`. OpenAI documents that specialized tool paths
  may bypass generic hooks, so the hook remains defense in depth; Git state,
  board state, restricted credentials, and driver-side reply validation stay
  authoritative.
- Both Claude and Codex endpoints can remain connected, but concurrent
  cross-provider turns in one station are unsupported. Dispatch through one
  driver at a time.

## Claude Code

Current Claude Code supports custom agents in `.claude/agents/*.md`, per-agent models and effort, tool allowlists, permission modes, maximum turns, foreground or background execution, and worktree isolation.

Generated Claude agents:

- use `permissionMode: plan` plus a read-focused tool allowlist for utility, scout, and reviewer roles;
- use `permissionMode: acceptEdits` for bounded workers and the test runner; the test runner has no Edit/Write tools and its instructions prohibit repository-source edits, including through Bash;
- list `Agent` with the configured leaf-role types only for `rfc-integrator`; type restrictions are not claimed as enforced within a delegated subagent;
- omit `Agent` from every worker, scout, reviewer, utility and test-runner leaf;
- only the designated integrator may delegate to the configured leaf roles; scouts, workers and reviewers remain leaves. A delegated child allowlist is policy where the host cannot enforce it;
- have the designated integrator dispatch leaf roles in the foreground, several per message for concurrency within the configured cap (see [nested child results](#nested-child-results-2026-09-11));
- select stable Anthropic model IDs from `config/routing.json`.

Parent permission modes can take precedence over a subagent's `permissionMode`. Before relying on read-only scouting or review, keep the parent in a permission mode that does not widen the child, and inspect `git status --short` after the run. The read-focused agents retain Bash for Git inspection and read-only verification commands, but `permissionMode: plan` denies mutating commands: configure, build, or test runs that write artifacts stay with the designated integrator, bounded worker, or test runner. Unexpected repository-source writes from a test runner invalidate the result.

The checked-in route declares Claude Code 2.1.255 or later for Fable 5.1. This floor is an owner-specified admission requirement; verify the installed runtime before claiming native serving. Configuration validation is not a live model-availability test. Worktree-isolated subagents received important main-checkout safety fixes by 2.1.210, but the default portable policy still does not enable static worktree isolation: a custom worktree subagent may branch from the repository's default branch rather than the primary session's current `HEAD`. Use worktree writers only after explicitly proving the desired base and integration behavior.

Claude Code keeps its default concurrency limit of 10. The portable skill uses
only bounded lanes that materially help the current task.

Claude Code officially discovers project skills from `.claude/skills/`; Codex uses the cross-client `.agents/skills/` location. Managed consumers link both discovery paths to their selected shared package. The renderer writes agent adapters referencing the provider-specific installed entrypoint; it does not replace the managed skill link or create another full skill copy.

### Long multi-commit sessions

Where a runtime exposes only a user-invoked goal command, the agent cannot start
it on the user's behalf. Use a writable persistent session task list when
available and permitted, mirroring the requested RFC order and closeout phases.
Where an agent-callable goal tool exists, follow the canonical skill's
authorization, reuse and completion rules. Either facility is a progress view;
the issue board and closeout cards stay authoritative.

Claude Code compacts long conversations, and compaction can silently drop the in-memory task queue mid-run. The skill's reorientation procedure exists for exactly this failure: re-derive the next card from the live board and the closeout card, and never conclude from memory that no work remains. For pack-scale runs, a larger context window can delay compaction but does not remove reorientation. Delegate bounded read-heavy work when doing so materially protects the integrator context; delegation is not required merely because a run is long.

Re-invoking the skill with the same arguments is the supported resume path after an interruption or a fresh session: reorientation recovers `RFC_BASE_SHA`, the ledgers, the phase checklist, and the next task from the closeout card, the board, and `git log`.

### Remote Control

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
  [remote routing](remote-routing.md#launch-and-reset-controls) defines identity,
  service-selection and legacy reset behavior.
- A session cannot create a session on another machine. Cross-machine work is
  `SendMessage` to existing sessions, addressed purely by session name;
  duplicate names silently resolve to auto-variants, so names must be unique
  and stable, and the receiving guard — not the address — is the integrity
  boundary.
- Inbound cross-session messages arrive as plain user turns, governed by the
  `crossSessionInbound` setting (`accept` | `hold` | `refuse`). Stations run
  with `accept` and treat every envelope as untrusted data per
  `references/remote-routing.md`.
- Station servers are drivable from the web and mobile app; the guard applies
  to those asks identically.

For Bedrock, keep the generated agent definitions unchanged and use `modelOverrides` in local or managed Claude Code settings to map the canonical model IDs to exact approved inference-profile ARNs. Family aliases are not considered reproducible routing. Unverified as of 2026-08-02: the `modelOverrides` setting could not be confirmed in official Claude Code documentation. Before relying on role-to-model routing through Bedrock, confirm on the Bedrock-configured machine that each generated agent's startup banner reports the expected model; if the setting is ignored, escalate to organization-managed model policy instead.

## Capability Fallback

The skill remains correct when an adapter is unavailable:

- keep ordinary engineering local to the designated integrator; required independent review uses only the qualified native review relay or remains pending;
- when a selected model does not support `max`, use the strongest supported effort, report the downgrade, and do not narrow the requested critical-review scope;
- keep writes with the designated integrator if a bounded worker cannot be controlled safely; never silently substitute the low-cost coordinator for engineering;
- preserve the same direct verification and closeout requirements;
- report the omitted delegation lane in the final summary.

## Source Documentation

- Codex subagents and custom agents: `https://developers.openai.com/codex/subagents`
- Codex skills: `https://developers.openai.com/codex/build-skills`
- Codex model recommendations: `https://developers.openai.com/codex/models`
- Codex Remote connections: `https://learn.chatgpt.com/docs/remote-connections`
- Codex App Server: `https://learn.chatgpt.com/docs/app-server`
- Codex hooks: `https://learn.chatgpt.com/docs/hooks`
- Claude Code subagents: `https://code.claude.com/docs/en/sub-agents`
- Claude Code skills: `https://code.claude.com/docs/en/skills`
- Claude Code model configuration: `https://code.claude.com/docs/en/model-config`
- Claude model IDs: `https://platform.claude.com/docs/en/about-claude/models/overview`
- Agent Skills progressive disclosure: `https://agentskills.io/skill-creation/best-practices`

## Native coordinator qualification (2026-09-08 source update)

The installed binaries reported Codex CLI 0.153.4 and Claude Code 2.1.260 during
this implementation. Version output is not native behavioral qualification.
Use [Coordination handoff](coordination-handoff.md) for native result/termination,
duplicate/stale mandates, cancellation, no-progress returns and recovery.

Current [Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
documents per-agent model/effort precedence and `agents.enabled`. The renderer
binds both route values and disables delegation for leaves. Child-type allowlists
remain policy; do not invent a depth key or claim native enforcement from a file.
Current [Claude subagent documentation](https://code.claude.com/docs/en/sub-agents)
documents per-agent effort overriding session effort. It limits the `Agent(type)`
allowlist to a main `--agent` session; a delegated integrator's child-type list is
policy even where native nested Agent calls work. Leaves omit Agent; integrators
inherit permissions by omitting permissionMode. Requested and observed routes
stay separate, and parent overrides require an actual serving check.

Qualify in fresh normal signed-in interactive sessions using disposable consumers.
Do not replace this with `codex exec`, `claude -p`, an SDK, external restart loop,
API key, permission bypass or global low-effort environment variable. Native
permission prompts remain user decisions. If unavailable, keep the required
criterion open while independent source work continues. Review relay is confined
to one integrator-selected independent review and returns judgment to that same
integrator. Ordinary implementation stays local to the integrator when nesting
is unavailable. Local handoff does not authorize a Git push.

### Desktop app Code tab observation (2026-09-10)

Two coordinator sessions in the Claude desktop app Code tab on Claude Code 2.1.260
could not resume a completed integrator. One listed `SendMessage` and then reported
`SendMessage is disabled for this session, in subagents as well as here`; a later
session did not list the tool at all. Neither had a permission deny rule, both had
`crossSessionInbound: accept`, and the version exceeds the documented minimum. The
rendered `rfc-integrator` role grants the tool, which does not make it available.
Treat the desktop Code tab as a host without `SendMessage` and run the fresh-dispatch
dispositions in [Coordination handoff](coordination-handoff.md#hosts-without-sendmessage);
the terminal CLI remains the qualified host for resume. This is a dated observation,
not a documented platform contract.

Follow-up, 2026-09-11: after the owner updated, a running desktop Code tab session
(desktop app 1.52386.0, Claude Code 2.1.260) gained `SendMessage` as a loadable tool
mid-session, and a send to a completed subagent resumed it and returned its reply.
Availability therefore varies by desktop build and session, not by CLI version or
settings. Record the observation at bind time in each run and select the resume or
fresh-dispatch disposition from what that session actually exposes.

### Nested child results (2026-09-11)

A nested child returns through its `Agent` call. The subagent documentation returns
a child's summary to its caller and strips `TaskOutput` from every subagent even
when the `tools` field lists it, so a foreground dispatch is the collection
mechanism and no nested wait primitive exists. A background child's result arrives
as a completion notification instead, and a resumed parent's history holds only what
its children delivered while it ran. The same definition resolves to a reduced
built-in tool set in the background.

Observed in Claude Code 2.1.266: an agent that has ended its turn is not re-invoked
when a child agent finishes; the completion goes to the main session, or is dropped
if it was queued just before the parent's last message. A parent still in its turn
receives it between tool calls, concurrently for dispatches issued in one message.
`TaskOutput` fails with `TaskOutput is not available inside subagents`, while
`TaskStop`, also documented as stripped, worked; depend on neither. A command a leaf
leaves running outlives its report and later re-invokes it: one stray search ran
about 90 minutes. Integrators that backgrounded their scouts and ended their turns
returned short partials, and the scouts' reports reached the coordinator.

[Milestone integration](milestone-integration.md#3-assign-complete-slices) collects
children inside the turn. Forward a stray leaf completion's result verbatim when
resuming the integrator that dispatched it; an agent task's `.output` file is that
child's full transcript, not a report.
