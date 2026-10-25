# Portable `implement-rfc`

This directory is shared RFC workflow source. Project mode keeps facts and
rules in the source repository; personal mode keeps them in its paired external
tracker. A single local agent can use
`SKILL.md`; native role adapters are optional. Remote stations are the separate
`remote-station` skill; [remote routing](references/remote-routing.md) keeps only
the rules for dispatching RFC work to one.

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

## MASK workflow readiness

`mask-workflow.json` is the passive descriptor MASK (RFC-MASK-0019) reads
beside `SKILL.md`. Its project contract declares the consumer inputs (`project.json`,
`project.md`, the optional execution selection) and every current role from
`config/roles.json` for Codex and Claude, all produced by the setup action
`prepare-roles`. The user contract declares the same roles without project
inputs. Both scopes render from the same canonical roles and routes; project
roles carry consumer addenda, while personal roles receive project facts through
the assignment. MASK runs `scripts/prepare_mask_roles.py` only under explicit
approval of a reviewed `mask install`, `register`, `repair` or `upgrade` task.
For an existing selection, preview `mask repair --project ROOT --dry-run --json`,
then apply with `mask repair --project ROOT --approve-plan HASH --json`, using
that result's `data.plan_hash`. A terminal invocation offers the same review;
`--user` selects personal skills. The approval covers the shown setup and exact
file replacements together;
the script writes the requested `STAGE/AGENT/NAME.ext` files through the same
`generate_roles` path as the standalone renderer and nothing else. MASK
validates the stage, writes the portable
`.mask/generated/implement-rfc/native-roles.lock.json` (it still reads a lock at the
retired `.mask/skill-config/implement-rfc/` location when that one is absent) and
deploys or retires the role files through its own journal; an unchanged rerun runs no
script. The canonical location is regenerable state that consumers conventionally
gitignore, so a fresh clone that should need no setup has to commit the lock and the
matching roles deliberately.

`scripts/workflow_preflight.py --repo-root ROOT --json` is the startup check:
it requires the program's `workflow_readiness_v1` capability and a complete
`status --check` result (older advertised interfaces use their compatibility path). Personal mode checks the selected source/tracker
binding and user-scope roles. An older MASK's link-only success is reported as
`unsupported`. Filesystem readiness is not host loading. The standalone
renderer (`render_runtime_adapters.py --repo-root ROOT`) remains available for
authoring and consumers that do not use MASK; its outputs are a distinct owner
from MASK-managed role files.

Consumer rendering discovers MASK's lock locations from `mask capabilities
--json` (`data.workflow.paths`), using `MASK_PROGRAM` or the `mask` on PATH.
This requires a MASK version advertising those paths, even for standalone
publication; an unavailable/older program is reported instead of guessing its
layout. Source-manifest generation and staged role generation do not need this
lookup. Setup requests also publish these consumer-relative paths, but the
staging entrypoint has no reason to open the lock: MASK owns publication.
Canonical lookup precedes retired fallback lookup. Retired-file cleanup belongs
to reviewed `mask repair` and `mask cleanup` tasks, with backups, never to the renderer.

MASK supports `compatible_locks` assertions for byte-identical package-input
changes. This renderer refactor does not qualify: each role's generated header
embeds a hash of the renderer source, so even a path-only edit changes output
bytes. No prior pair is vouched for by this package. One regeneration is needed
for this adoption; future MASK-only layout moves require no renderer edit.

## What is project-specific

Exactly two files under each project-mode consumer repository or personal-mode
tracker:

- `.mask/skill-config/implement-rfc/project.json` — machine-read facts: project tokens, tracker paths,
  lane names and their status words, single/per-area counters, sequencing, the structure-gate commands, the attended-review skill (or
  `null`), workstream branches, and per-role instruction addenda. The former
  `session_prefix` and `station_registry_doc` keys are optional legacy station
  keys; station identity lives in remote-station's `station.json`. `schemas/project.schema.json` documents the contract;
  `scripts/project_config.py` enforces it.
- `.mask/skill-config/implement-rfc/project.md` — the project's own rules in prose: what to read
  first, the side-effect boundary, what counts as a direct surface, the
  closeout-card contract, attended integration and platform eligibility.

The routine project worker inherits the `rfc-worker` project addenda, followed
by any `rfc-worker-routine` addenda. Personal assignments supply those addenda
for the selected source project. Its cheaper route does not relax project boundaries.

Everything else is the portable set. `generated/portable-manifest.json`
records its files and digests, and
`scripts/validate_portable_agents.py --compare <other-checkout-skill-dir>`
fails when two projects have drifted.

## Maintained Sources

New packs start with the [offline milestone authoring kit](examples/milestone-plans/README.md):
a minimal JSON plan, generated view, entrypoint pointer and portable schema. Validation
and rendering work outside a configured consumer. Live execution follows
[Plan-first execution](references/milestone-plans.md).
`coordinator_handoff.py assign` and `check` report the bound plan, current outcome,
producer/dispatch and continuation decision. Machine output retains recorded
replacement reasons; missing historical generation information stays unknown.
These observations do not measure subscription savings.

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
- `references/remote-routing.md`: dispatching RFC work to a remote station.
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
- `scripts/launch_remote_station.py`, `scripts/station_control.py`: temporary
  forwarders to the remote-station skill, kept for one release.

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

For personal mode, follow [Personal storage](references/personal-storage.md)
to bind the source Git common repository to an external tracker and select
the skill at user scope. `--repo-root` still names the source checkout;
`--mode personal` makes the selection explicit and observational commands
never initialize a missing binding.

`resolve_context()` returns `asset_root`, `source_root`, `workflow_root`,
`runtime_root`, `mode`, `project_config_path`, `project_rules_path`, and
validated `config`. Read the selected workflow rules
before editing. Keep this object or pass its root explicitly after changing
CWD. No helper selects a consumer when imported. Hidden config overrides are
validated inputs inside the selected consumer; they cannot redirect output.

## Role Adapters

Generate optional role adapters with `scripts/render_runtime_adapters.py --repo-root
/path/to/consumer`; pass `--check` for observational drift checking. A consumer
that carries MASK's `native-roles.lock.json` is judged against the fresh render and
that lock, its legacy publication manifest is ignored, and direct rendering into it
is refused in favour of `mask repair`. Without a lock the renderer writes
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
`examples/projects/sample-review/project.json` and `project.md` as an
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

## Remote stations

Station launch, status, takeover and hooks moved to the `remote-station` skill,
configured by its own `station.json`. For one release,
`scripts/launch_remote_station.py` and `scripts/station_control.py` here forward to
that skill when it is installed beside implement-rfc; otherwise they name
`mask install remote-station`.
