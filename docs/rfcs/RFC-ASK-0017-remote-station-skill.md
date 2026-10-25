---
id: "RFC-ASK-0017"
title: "Standalone remote-station skill and a version-agnostic launch command"
status: "Implementing"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
---

# Standalone remote-station skill and a version-agnostic launch command

## Problem and grounded current behavior

The owner asked, on 2026-10-24, to extract remote stations from implement-rfc into
their own skill, add it to the RFC bundle, fold the AITO and BetterPullReview
launchers into it, and add a system-wide `launch_remote_station` command that
forwards to the current repository's installed skill.

Station mechanics are an import-closed cluster inside implement-rfc:
`launch_remote_station`, `codex_station`, `station_control`, `station_lifecycle`,
`station_lease`, `station_hooks`, `remote_station_guard` and
`station_task_admission` under [scripts](../../skills/implement-rfc/scripts/).
No other implement-rfc script imports them. All of them read consumer identity through
`project_config`. Only station code reads `workstreams` (other than allocation's
`main` branch check), `session_prefix` and `station_registry_doc`. `project`,
`display_name` and `origin_repo_name` are shared with lanes, allocation and
adapter rendering. The guidance lives in
[remote-routing](../../skills/implement-rfc/references/remote-routing.md) and
`station-control.md` (since moved to
[remote-station](../../skills/remote-station/references/station-control.md)),
which mix general station rules with RFC dispatch rules.

Consumers diverge:

- BetterPullReview's `scripts/launch_remote_station.py` is already a 57-line
  forwarder to the installed implement-rfc launcher and `station_control.py`. It
  hard-codes the skill path and adds default takeover flags.
- AITO's `tools/launch_remote_station.py` (1,226 lines) and `tools/codex_station.py`
  are a stale private fork. Only `status` and `takeover` forward to the shared
  helper (AITO AGD-0063). The fork lags the skill: no `--repo-root`, `--no-claude`,
  `--no-codex` or pending-takeover recovery. It has one behavior the skill lacks:
  the "Claude return path UNVERIFIED" warning from AITO AGD-0056. Its hard-coded
  `moira` and `acta` workstreams name branches that no longer exist. Its
  station-file schema `aito.implement-rfc.remote-station.v2` is already accepted
  by `station_lifecycle.STATION_SCHEMAS`.
  - The fork's divergence let ASK-0123's timeout defect exist twice and get fixed
    twice.
  - AITO's tool hazard page (`tools/docs/agents/remote-stations.md`)
    holds the reproduced platform dead ends, and they apply to every consumer.

MASK installs skills per checkout as links under `.agents/skills/<id>`, pinned per
repository. Its only system-wide command is `mask` itself, written by
`mask self install --bin-dir` without editing PATH. Skills cannot declare commands.
Skills find one another by skill name.
[mask-source.json](../../mask-source.json) defines the `rfc` bundle as
author-rfc, grill-rfc, grill-me and implement-rfc.

## Proposed behavior and boundaries

### The remote-station skill

Add `skills/remote-station`, a portable skill that owns the station cluster above,
its tests, the platform-dead-end table and the general station contract (identity,
lease, provisioning, takeover, status, one driver per turn). implement-rfc keeps
only the rules it owns: RFC dispatch, envelope authority and lane interaction. It
refers to remote-station by skill name. Add remote-station to the `rfc` bundle.
Preserve every existing station behavior, including ASK-0123's history-sized turn
reads and the existing station identity rules (`station_id`, Codex `thread_id`,
Claude `session_id`, no recency selection).

Generalize the return-path warning into the skill for every Claude endpoint. Delete
the `moira` and `acta` workstreams instead of carrying them forward.

### Configuration

Owner answer, 2026-10-24: station configuration is a `station.json` that works
like implement-rfc's `project.json`.

remote-station owns `.mask/skill-config/remote-station/station.json`, declared as a
required input in the skill's `mask-workflow.json`. It follows the `project.json`
conventions: a versioned `schema` (`remote-station.config.v1`), validation that
refuses missing, malformed and unknown keys, and resolution from the invoking
checkout's root with no inference from the skill's physical path. It holds the
fields station code reads today: `project`, `display_name`, `origin_repo_name`,
`session_prefix`, `station_registry_doc` and `workstreams` (with per-workstream
`branch` and optional platforms). It uses `project_config`'s validation rules and
error codes for these keys. remote-station carries its own resolver and does not
import implement-rfc.

Each consumer migration writes `station.json` from its implement-rfc `project.json`.
implement-rfc keeps the identity fields and the `main` branch check its own scripts
use. It stops requiring `session_prefix` and `station_registry_doc` once no
implement-rfc script reads them. The shared identity fields are deliberately
duplicated.

### Entry contract

Each version of the skill provides `scripts/launch_remote_station.py`. It is
invoked as a script with the user's arguments, from any directory inside the
checkout, by the interpreter the caller chose. It resolves the checkout itself. It
covers launch, `status`, `takeover` and `hooks`, applying BetterPullReview's
takeover defaults (`--mode local --stop-previous`) unless options are given.
This path and invocation shape is the frozen interface the command depends on. A
future skill version may change anything behind it, but must not move or remove it.

### System-wide command

Ship a small, version-free forwarder with the skill. Installing it writes
`launch_remote_station` (POSIX) and `launch_remote_station.cmd` (Windows) into a
chosen bin directory. This mirrors `mask self install --bin-dir`: nothing is
elevated and PATH is not edited. The forwarder:

1. finds the checkout root of the current directory with Git (`--show-toplevel`,
   so linked worktrees resolve to themselves);
2. outside a repository, exits nonzero with a message that names the directory;
3. runs `<root>/.agents/skills/remote-station/scripts/launch_remote_station.py`.
   If that link is missing, it exits nonzero and names `mask install remote-station`.
   It never falls back to another checkout, a user-scope skill or a cached copy;
4. passes arguments, working directory, stdio and exit code through unchanged,
   using `py -3` on native Windows and `python3` elsewhere;
5. contains no station logic and imports nothing from the skill. Installing it again
   from a newer skill version is idempotent.

Because the target is the checkout's own pinned link, two repositories pinned to
different versions each run their own version. Upgrading the forwarder never
changes station behavior.

Owner answer, 2026-10-24: the skill installs the forwarder for now. Its script
`scripts/install_command.py --bin-dir DIR` writes both forwarder files and needs no
MASK change. MASK-managed commands that skills declare remain possible future
ManageAgentSkills work and are not part of this RFC.

### Compatibility and consumer migration

For one release, keep `implement-rfc/scripts/launch_remote_station.py` and
`station_control.py` as forwarders to the sibling remote-station skill, so existing
wrappers and documentation keep working. Remove them in a later release.

- **AITO:** replace `tools/launch_remote_station.py` with a forwarder of at most
  30 lines (same target and rules as the system-wide command) and delete
  `tools/codex_station.py` and their tests. Move the hazard table into the skill,
  and reduce AITO's tool page and `docs/remote-stations.md` to AITO-specific setup.
  The existing `aito-main-win` station (`stn-39ef5ffb`, its recorded Codex task and
  Claude session) must resume unchanged.
- **BetterPullReview:** point its existing forwarder at remote-station (or the same
  shared forwarder shape) and drop its private takeover defaults, which the skill
  now applies.

Out of scope: the cross-provider turn mutex, station routing semantics, MASK
internals, publication and live-runtime qualification beyond the AITO resume check.

## Acceptance

- **AC01:** remote-station installs and runs in a consumer that has no implement-rfc
  skill, configured only by `station.json`. A missing, malformed or unknown-key
  `station.json` refuses the launch before any runtime starts. The station test suites run from its source, and implement-rfc keeps no
  station implementation other than the temporary forwarders.
- **AC02:** The `rfc` bundle lists remote-station. Installing the bundle into a
  fresh fixture consumer links it next to implement-rfc.
- **AC03:** From two fixture checkouts pinned to different remote-station versions,
  the system-wide command runs each checkout's own version, including from a
  subdirectory and from a linked worktree.
- **AC04:** The command exits nonzero with distinct messages outside a Git
  repository and inside a repository without the skill. It runs nothing in either
  case.
- **AC05:** Arguments, stdio and exit status pass through unchanged for launch,
  `status --json` and a refused launch.
- **AC06:** On native Windows, AITO's forwarder resumes `aito-main-win` with the
  same `station_id`, Codex thread and Claude session, and prints the return-path
  warning. AITO's private launcher and Codex helper are removed.
- **AC07:** BetterPullReview's documented commands, including takeover with no
  options, behave as before through remote-station.
- **AC08:** Existing implement-rfc launcher paths still work through the temporary
  forwarders.

AC09–AC11 were added by the owner amendment of 2026-10-24 below.

## Execution authority

Accepted for implementation by the owner on 2026-10-24 ("Implement the RFC ...
Consumer migration scope names AITO and BetterPullReview"). Mandate revision
`remote-station-v1`. No push, publication or credential change is authorized.
Original draft retained unchanged under `drafts/`. Live work: ASK-0124
(AgentSkills skill, AC01–AC05, AC08), ASK-0125 (AITO migration, AC06), ASK-0126
(BetterPullReview migration, AC07); closeout: ASK-0127. Milestones and exits are in
the [adopted plan](plans/remote-station-skill/milestone-plan.json).

## Owner amendment 2026-10-24: compact station message passing

This section records an owner amendment. It is a requirement, not an observation.

The owner added milestone M4 `compact-station-messaging` ("Compact station message
passing"), giving this reason: "the remote-station message format is token
inefficient, with boilerplate re-sent on every turn." Live work: ASK-0128. It depends
on M1 `agentskills-skill`. Its boundary is `skills/remote-station` plus the
implement-rfc dispatch rules that build station prompts. No push is authorized. The
closeout card ASK-0127 now also waits on ASK-0128.

- **AC09:** Per-turn token cost is measured on the same recorded `aito-main-win`
  turns (Codex thread history and Claude session transcript), before and after the
  change, and the method is recorded. The before measurement precedes design and is
  kept as evidence.
- **AC10:** Every guard refusal still fires for both v1 and v2 envelopes: replayed or
  reused `task_id`, project mismatch, authority exceeded and expired.
- **AC11:** v1 envelopes from existing dispatchers are still admitted during the
  compatibility release. Station identity rules are unchanged.

Candidate causes are unmeasured hypotheses, and AC09's measurement decides:

- The `implement-rfc.remote-task.v1` envelope (schema
  `remote-task-envelope.v1.json`) re-sends station-invariant fields on every turn.
- `remote_station_guard.py` `_admit_request` injects the full admission receipt
  JSON as hook `additionalContext`.
- Bootstrap and dispatch text is repeated on every turn.

A likely shape, which does not bind the design: a compact v2 envelope whose
invariants come from the station identity file; the guard validates the expanded
envelope; v1 is still accepted for one release; and the hook returns a one-line
acknowledgement with a receipt ID.

## Implementation notes

- **No `mask-workflow.json` (pending owner decision).** MASK at ManageAgentSkills
  `9b73453` refuses a workflow descriptor whose `native_roles` list is empty
  (`workflow.invalid`: "Descriptor native roles must be a nonempty bounded list"),
  and remote-station declares no native roles. The skill therefore ships no
  descriptor; `station_config.py` enforces the required `station.json` itself and
  refuses before any runtime starts. Declaring the input for `mask status` needs an
  input-only descriptor in ManageAgentSkills, which this RFC leaves out of scope.
- Durable identifiers keep their `implement-rfc.*` names (station-file, lifecycle,
  lease and envelope schemas; Git-directory file names) so existing stations
  resume unchanged.
- Station code no longer reads implement-rfc's personal-mode binding: it resolves
  only the invoking checkout's `station.json`. implement-rfc's remote routing still
  forbids dispatching personal-mode RFC work to a station.
- AITO's uncommitted 2026-10-24 edits to its fork port ASK-0123's history-sized
  turn read, which the skill already had; there was nothing further to carry over.

## Verification and execution record

See the [closeout](../issues/10-backlog/ASK-0127-close-remote-station-skill-rfc.md)
and [verification record](plans/remote-station-skill/verification.md).
