# Runtime Compatibility

Verified against public product documentation on 2026-08-02. This file
describes current adapters, not permanent skill semantics.

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

Remote-station transport facts (Codex Managed Remote, App Server provisioning,
Claude Remote Control) live in the remote-station skill's
`references/runtime-compatibility.md`.

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

The checked-in route declares Claude Code 2.1.284 or later. Current
[model configuration documentation](https://code.claude.com/docs/en/model-config)
requires 2.1.284 for Sonnet 5.5 and 2.1.280 for Opus 5.5 (checked 2026-10-03).
Verify the installed runtime before claiming native serving; configuration
validation is not a live model-availability test. Worktree-isolated subagents
received important main-checkout safety fixes by 2.1.210, but the default portable
policy still does not enable static worktree isolation: a custom worktree subagent
may branch from the repository's default branch rather than the primary session's
current `HEAD`. Use worktree writers only after explicitly proving the desired
base and integration behavior.

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

For Bedrock, keep the generated agent definitions unchanged and use `modelOverrides`
in local or managed Claude Code settings to map canonical model IDs to exact approved
inference-profile ARNs. [Model configuration](https://code.claude.com/docs/en/model-config)
documents the setting (checked 2026-10-03). Family aliases are not reproducible
routing. Confirm approved inference profiles and each role's effective model on
the Bedrock-configured machine before relying on those routes.

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

### Foreground dispatch and Monitor events (2026-09-11)

Observed in the desktop app Code tab on Claude Code 2.1.266. A `Monitor` armed on a
command emitting one line every twenty seconds, followed in the same message by a
foreground `Agent` dispatch that held the turn for ninety-five seconds: all five
events emitted during the dispatch reached the main session as one batch only after
the `Agent` call returned, and the main loop took no turn between them. Monitor
events therefore queue behind a foreground dispatch; an armed trail gives no
in-session visibility while the coordinator is blocked, and no relay turn is spent.

In the same session an `rfc-integrator` dispatched with `run_in_background: true`
reported its tools as `Read, Bash, Edit, Write, Skill, Agent, SendMessage, TaskStop`,
with `Grep` and `Glob` absent, dispatched a foreground `rfc-utility` leaf, received
its reply and returned it; the completion reached the main session as a notification.
A background integrator can therefore assign slices on this host. Both are dated
observations of one desktop build, not documented platform contracts;
[Progress relay](progress-relay.md) selects the dispatch mode from them.
