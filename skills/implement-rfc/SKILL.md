---
name: implement-rfc
description: Implement or resume RFCs and RFC packs through bounded cards, focused acceptance checks, explicit commits, attended handoffs and truthful closeout in the selected repository.
---

# Implement RFC

Carry the requested scope from its live board to a truthful closeout. Agents
judge acceptance and evidence relevance; helpers handle deterministic mechanics.

## Select and resume

Resolve the consumer once with `python <asset-root>/scripts/project_config.py
--repo-root /absolute/consumer`. Assets may be shared links. Consumer facts are
exactly `.mask/skill-config/implement-rfc/project.json` and `project.md` beneath
that root. Explicit root wins over `IMPLEMENT_RFC_PROJECT_ROOT`, then invocation
Git root. Missing or mismatched context refuses; examples are never defaults.
Keep `--repo-root` explicit on subsequent helper calls.

1. Report selected repository/branch, inspect Git status, and read project.md,
   root/nearest instructions and the requested live RFC/card. Preserve unrelated
   work. Load deeper ownership/hazard references only for the selected surface.
2. Run `scripts/issue_board.py --repo-root ROOT queue --rfc RFC-ID --json`.
   Repeat `--rfc` for a pack, or use `--area AREA` for an explicitly requested
   monorepo area. `--include ID ...` adds named cards. Whole-board work requires
   `--all`; never schedule unrelated projects or areas. The compact queue omits
   Done history; `inspect ID --body` retrieves a selected card when needed.
3. Recover the closeout's immutable `RFC_BASE_SHA`, planned cards and evidence.
   Cross-check scoped live state with commits since that baseline after an
   interruption. Do not re-read unrelated history or repeat unchanged checks.
   Resolve ambiguous in-progress claims explicitly. Scripts do not promote
   Backlog cards or treat external handoff references as integration evidence.
4. Before source work, establish bounded acceptance, owned paths and a closeout
   anchor. Reserve needed IDs on the main integrator with `allocate --area AREA
   --count N --reserve-for TOKEN`; omit area only for an unambiguous counter.
   Commit its returned counter/receipt paths before use. Record planning and
   claim commits. Read [pack lifecycle](references/pack-lifecycle.md) only for
   import, worktree lanes, integration, renumbering or handoff.

The live RFC and board are authoritative. A runtime goal may supplement them
only if goal tracking is authorized; never infer authorization or invent a
budget from an ordinary implementation request.

## Implement a slice

- Select dependency-ready work and its narrowest direct check. Claim with
  `issue_board.py --repo-root ROOT claim ID --json`; this moves and commits the
  card and pristine repaired links. The index must be empty. Platform eligibility
  is card metadata (`--platform win|mac|linux`), not separate Ready directories.
- For substantial delegated implementation, choose **routine** or **deep** and
  give one concrete reason in the assignment. Prefer `rfc-worker-routine` when
  the approach and repository pattern are established, ownership is exclusive,
  and verification is direct. Use `rfc-worker` for unresolved design or changed
  sensitive behavior; name that reason. Small direct changes can stay with the
  primary. See [delegated execution](references/delegated-execution.md).
- Implement within owned paths. Put rote repetition into a durable helper when
  useful; avoid adding process scaffolding merely to document thinking. Update
  code, tests and retained instructions only where changed behavior requires it.
- Run focused changed-surface checks; exercise the public selected path if unit
  checks can pass while the acceptance claim is false. Reuse evidence whose
  relevant inputs are unchanged. Unrelated HEAD advancement does not invalidate
  it. Review the changed code for straightforward simplifications.
- Record criterion, outcome, revision and evidence. `record_evidence.py` captures
  one command and exit result; the agent must still decide what it proves.
  Observations, artifacts and freeform evidence are equally supported where
  appropriate. No fake commands, compulsory bundles/hashes or proof-of-proof.
- Finish using `issue_board.py --repo-root ROOT finish ID --acceptance FILE
  --paths FILE ... --json`. The decision file explicitly approves Done or
  automated-complete/human-pending; the command records evidence, repairs links
  and commits only the card/bookkeeping and supplied individual paths. It never
  infers acceptance, sweeps unrelated edits or pushes. Inspect its result.
  See [bookkeeping](references/bookkeeping.md) for the small wire contract,
  dry runs, stale-input refusals and recovery.

One canonical card model supports multiple RFCs and areas. Scope validation
examines requested work and its dependency closure; identity and counter
invariants remain global. Historical workflow contradictions outside that scope
are follow-ups, not reasons to fabricate completion or block independent work.
Descriptive data belongs in `metadata`, not custom scheduling fields.

## Choose verification at the right boundary

Ordinary slices use focused checks and reuse unchanged passing evidence. At
pack or milestone completion, normally run one integration-focused verification
pass. Full relevant suites and a critical review are appropriate when changed
scope/risk justify them; a substantial single RFC may warrant the same treatment.
State the claims the broader checks will resolve, then consume the result once.

Application-wide builds, exhaustive matrices, hermetic replay, repeated reviews
and manual approval checkpoints are not defaults. Broader work outside the
warranted integration pass requires an explicit request or a concrete unresolved
defect. A fix receives only the checks affected by that fix. Unavailable optional
coverage is a limitation, not a new requirement. Required acceptance that cannot
be exercised remains open and is reported honestly.

Correct contained in-scope failures. Track separable noncritical improvements
as follow-ups. Ask about a material scope/architecture change; routine fixes
within the accepted boundary do not require a new approval ceremony.

## Human attendance

An explicitly required human decision leaves its card/RFC open. Complete the
unattended work, finish as `human-pending`, and continue independent work. Never
invent a human gate merely because a surface has UI. Query waiting cards with
`queue --human-waiting` (optionally scoped by RFC or area).

When asked to **prepare for an attended session**, use the shared
`attended-review` skill. Surface ready items immediately, prepare quick items
first, and allow interruption of slow preparation. The user can review a partial
queue and stop at any point; save each independent decision immediately. Prefer
local HTML and practical agent-captured objective evidence. Use `wizard` when
manual steps need guided presentation. Keep pure local HTML intake usable if a
server is unavailable; both Claude and Codex can drive the same session.

Protect selected candidates and relevant dependencies/resources. Unrelated work
continues. Stepping away retains protection; **resume development** explicitly
releases conflicting resources and marks only affected unanswered items needing
preparation. Observe attended conflicts before changing protected inputs. These
cooperative protections do not freeze arbitrary external tools or other agents.
Completed verdicts stay attached to the actual candidate; relevant later changes
may require another review. Do not invalidate evidence for unrelated HEAD changes.

## Integration and closeout

The finish condition is direct passing evidence for all in-scope criteria, the
selected public path exercised where applicable, no known critical in-scope
failure, and agreement between implementation, docs, cards and RFC status.
`Implemented` is distinct from `Auto-Verified`. An unresolved required human
criterion keeps terminal status open even when automated work is complete.

At integration, inspect the final scoped diff against `RFC_BASE_SHA`, check all
required cards including relevant unlinked discoveries, reconcile RFC/index
status and run the configured structure gate once. Substitute a configured
`{rfc}` token with the selected RFC ID; helpers accepting repeated `--rfc` can
coalesce a pack into one scoped invocation. Keep actual check/result/
revision records on the closeout; do not create a second mutable status ledger.
The main integrator confirms terminal status after integrating worktree slices.

Isolation and independent review are optional tools for concrete persistence,
migration, protocol, authority, concurrency or destructive-operation risks.
[Delegated execution](references/delegated-execution.md) defines bounded worker
and reviewer contracts. Keep exclusive write ownership, staging/commits and
acceptance with the integrator; use one risk-focused reviewer where warranted,
not a review loop. Models and roles follow the shared routing policy; only
repository ownership facts/addenda are configurable.

Record exact task-created temporary roots and their consumers. Once consumed,
confirm no user files/processes depend on them and remove them; never retain a
checkout as evidence. Report completed scope, commits, actual verification,
remaining decisions/limitations and cleanup. Context pressure does not complete
a task: preserve the next actionable slice in the closeout and continue.

## Select execution and collect usage

Keep small or coupled work in the integrator. For already selected command
stages, read [bounded execution](references/bounded-execution.md); review the
order before starting it. Native companion capabilities and limitations are
listed there. A delivered report or successful command never approves acceptance.

For local usage, run `python3 <asset-root>/scripts/usage.py` from the desired
project, or add `--mask-projects` for public registry scope. Read
[usage collection](references/usage-collection.md) only for options, quota or
offline analysis. Capture does not deploy skills or launch models. Historical
role activity remains available through `role_usage.py`; it is not accepted-work
or subscription billing evidence.

## Optional runtime support

Read [remote routing](references/remote-routing.md) only for a remote envelope,
station marker or actual dispatch; read [Codex lanes](references/codex-lanes.md)
only when launching one. Missing optional runtimes do not add acceptance gates.

Shared role source is `config/roles.json` and `config/routing.json`. Explicitly
render consumer adapters with `scripts/render_runtime_adapters.py --repo-root
ROOT`; `--check` is read-only. Baseline routing is the default. An explicit
`--profile` requires verified capabilities for each overridden model/effort and
changes delegated adapters only; it never selects the primary session. Writes stay in consumer agent directories and
`.mask/generated/implement-rfc/`, never through linked skill roots. Existing
outputs require matching ownership markers and prior manifest. Source authors
use `--write-source-manifest` and `validate_portable_agents.py --source-only`.

For local role usage or routing diagnosis, read [routing audit](references/routing-audit.md)
and run `scripts/role_usage.py`. It reads Codex and Claude history on demand;
it does not install hooks, send telemetry, or add a closeout gate.
