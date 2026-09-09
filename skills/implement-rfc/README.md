# Portable `implement-rfc`

This directory is shared RFC workflow source. Each consumer keeps its own
project facts and rules outside the skill. A single local agent can use
`SKILL.md`; native role adapters and remote station helpers are optional.

## Policy

Ordinary RFC work is acceptance-focused:

- the live RFC, issue board, owning instructions, and selected product path
  define the work;
- focused tests plus one direct public/selected-path lane are the default;
- verification tables are catalogs of available commands, not mandatory
  matrices;
- unchanged passing evidence is reused;
- delegation, isolation, and independent review are optional, risk-triggered
  tools; the `Closeout review runtime:` line is recorded, not audited;
- one integration-focused pass normally completes a pack/milestone; full relevant
  suites and critical review are selected when scope/risk warrant; exhaustive
  matrices, hermetic replay and repeated reviews are not defaults;
- temporary worktrees and build roots are removed when their result is
  consumed.

Retired and available only through Git history: the parallel-slices writer
mode and its lane-plan validator, the blocking delegation audit, and the
prescribed verification-matrix, documentation-ledger, and phase-checklist
formats.

## What is project-specific

Exactly two files under each consumer repository:

- `.mask/skill-config/implement-rfc/project.json` — machine-read facts: project tokens, tracker paths,
  lane names and their status words, single/per-area counters, sequencing, the structure-gate commands, the attended-review skill (or
  `null`), the station registry document, workstream branches, and per-role
  instruction addenda. `schemas/project.schema.json` documents the contract;
  `scripts/project_config.py` enforces it.
- `.mask/skill-config/implement-rfc/project.md` — the project's own rules in prose: what to read
  first, the side-effect boundary, what counts as a direct surface, the
  closeout-card contract, attended integration and platform eligibility.

The routine worker inherits the `rfc-worker` project addenda, followed by any
`rfc-worker-routine` addenda. Its cheaper route does not relax project boundaries.

Everything else is the portable set. `generated/portable-manifest.json`
records its files and digests, and
`scripts/validate_portable_agents.py --compare <other-checkout-skill-dir>`
fails when two projects have drifted.

## Maintained Sources

- `SKILL.md`: authoritative workflow and finish condition.
- `config/roles.json`: portable role semantics (one integrator and seven leaves).
- `config/routing.json`: capability-class routing for Codex and Claude.
- `references/pack-lifecycle.md`: pack import, lane authority, milestone
  integration, renumbering, handoff, and cleanup.
- `references/delegated-execution.md`: optional role/delegation guidance.
- `references/model-routing.md`: capability classes, role-to-model
  assignment rationale, and per-lane runtime selection.
- `references/codex-lanes.md`: launching delegated lanes on the Codex
  runtime from a Claude driver.
- `references/remote-routing.md`: remote-station identity and writer authority.
- `references/runtime-compatibility.md`: adapter and runtime-specific facts.
- `scripts/project_config.py`: invocation context resolver and project schema validator.
- `scripts/render_runtime_adapters.py`: deterministic native adapter renderer
  and separate portable-manifest authoring command.
- `scripts/validate_portable_agents.py`: skill tests, adapter drift check,
  cross-project comparison.
- `scripts/role_usage.py`: read-only Codex/Claude role census and recorded routing
  decisions; see [routing audit](references/routing-audit.md).
- `scripts/audit_board.py`: issue-board/RFC conformance audit; transcripts
  informational.
- `scripts/codex_lane.py`: routed Codex lane launcher over the openai-codex
  plugin's companion runtime.
- `scripts/station_lease.py`, `scripts/remote_station_guard.py`,
  `scripts/launch_remote_station.py`, `scripts/codex_station.py`: remote
  station identity, single-writer protection, and launch.

The designated milestone integrator owns authorized tracker, commit, integration
and RFC-status decisions within its assigned main/lane scope. The native
coordinator preserves the user mandate and continuation; leaves return bounded
inputs to the integrator's judgment. Session routes are separate from delegated
roles, and rendering does not select or hot-switch the current session.

## Select A Consumer

Invoke the physical shared script or either skill link from the consumer:

```sh
python3 /path/to/implement-rfc/scripts/project_config.py --repo-root /path/to/consumer
python3 /path/to/implement-rfc/scripts/audit_board.py --repo-root /path/to/consumer
```

Explicit `--repo-root PATH` (API `repo_root=PATH`) takes precedence over
`IMPLEMENT_RFC_PROJECT_ROOT`, then Git's root for invocation CWD. Nested CWD
and Git worktrees are supported. Explicit roots must name the worktree root;
invalid roots never fall through. Origin repository-name mismatches refuse.
Fixtures may use explicit identities without an origin remote.

`resolve_context()` returns `asset_root`, `repo_root`, `project_config_path`,
`project_rules_path`, and validated `config`. Read the selected project rules
before editing. Keep this object or pass its root explicitly after changing
CWD. No helper selects a consumer when imported. Hidden config overrides are
validated inputs inside the selected consumer; they cannot redirect output.

## Role Adapters

Generate optional role adapters with `scripts/render_runtime_adapters.py --repo-root
/path/to/consumer`; pass `--check` for observational drift checking. It writes
`.codex/agents/rfc-*.toml`, `.claude/agents/rfc-*.md`, and
`.mask/generated/implement-rfc/runtime-adapters.json`. It never emits a Claude
skill shim or writes through either skill link. Linked destination parents and
unrecognized existing files refuse. Replacement requires a generated marker
and membership in the prior consumer manifest; reconcile legacy bootstrap
adapters deliberately before first rendering.

Author the source digest separately in the canonical checkout with
`python3 scripts/render_runtime_adapters.py --write-source-manifest` (paths here
are relative to the skill). `validate_portable_agents.py --source-only` checks
the digest without writing. `--repo-root /path/to/consumer` checks only that
consumer's adapters; `--compare /path/to/other/skill` compares actual source
bytes. MASK never executes these commands during skill deployment.

## Routing Changes

Change role assignments or provider routes only in `config/routing.json`,
update `verified_as_of`, then render and validate. For candidate evaluation,
use `--repo-root` and `--routing-override` with a temporary directory.

## Use From Another Project

1. Create the consumer's `.mask/skill-config/implement-rfc/project.json` and
   `project.md`; the JSON file is complete facts under
   `schemas/project.schema.json`, without a merge layer.
2. Read the shared skill explicitly by path or through its managed directory
   links. The linked skill's physical parent never chooses a consumer.
3. Run `project_config.py --repo-root /path/to/consumer`, report the selected
   checkout, and read its external rules before implementation.

The inherited context is retained in
`examples/projects/samplereview/project.json` and `project.md` as an
example only. It is never a default for an arbitrary consumer.

All consumers require external v2 context and canonical cards. Historical
conversion is one-off migration work outside this skill. See
[bookkeeping](references/bookkeeping.md) for the CLI and card/evidence contracts.

## Bedrock

Keep generated Claude agent files unchanged. If Claude Code's
`modelOverrides` setting is supported and approved in the target environment,
map the stable model IDs to inference-profile ARNs outside the portable skill
using `config/claude-bedrock-model-overrides.example.json`. Confirm each
agent's startup banner before relying on the mapping.

## Optional remote station controls

The station launcher starts or resumes both runtimes. Use `--fresh codex`,
`--fresh claude`, or `--fresh` for both contexts while retaining station identity.
`--no-claude` and `--no-codex` select one service. Claude uses the compact Remote
Control server; a fresh session becomes visible after a controller connects.
See [launch and reset controls](references/remote-routing.md#launch-and-reset-controls)
for exact-ID resumption, writer ownership and legacy flags.
