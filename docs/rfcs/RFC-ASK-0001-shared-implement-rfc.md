---
id: RFC-ASK-0001
title: Import and adapt the portable implement-rfc workflow
status: Implementing
owner: MikeMarcin
created: 2026-09-05
---

# RFC-ASK-0001: Import and adapt the portable implement-rfc workflow


## Summary

Make the supplied SRV `implement-rfc` the first skill in `MikeMarcin/AgentSkills`, then adapt it to operate as one shared directory from multiple consumer projects. Preserve its acceptance-focused execution, board lifecycle and optional native adapters. Do not transplant SRV's architecture or model/runtime obligations into MASK.

## Motivation and observed source

The archive is already portable in workflow content but not in installation topology. Its two project-specific files live inside the skill, `project_config.repo_root()` derives a project from the resolved script path, and the renderer writes a Claude shim into the skill entrypoint. With MASK's two symlinks, running that renderer could overwrite the canonical shared `SKILL.md`. The source paths and findings are enumerated in the pack's SOURCE-REVIEW.md.

## Scope and ownership

Own `skills/implement-rfc/**`, its example contexts, provenance notice, focused tests, this repository's `.mask/skill-config/implement-rfc/**`, and its bootstrap/tracker instructions. Existing SRV is read-only and does not receive changes. Do not add MASK implementation code, a runtime plugin framework, cross-device synchronization or new remote-station behavior.

## Import boundary

Import the 39 clean payload files from the packet unchanged in a distinct first skill-import commit. Preserve filenames and supporting resources; exclude macOS resource forks and Python caches. Record the input archive hash and source attribution. This first commit may still contain inherited SRV context, so it is **not shared-deployment-ready**. Keep AgentSkills private. Do not add another skill until the first import and adaptation have landed.

## Three separate roots

1. **Asset root:** resolved physical directory containing this skill's SKILL.md, scripts, schemas, shared references and role/routing sources.
2. **Consumer root:** the repository whose RFCs, cards and source the agent is implementing.
3. **Generated-output root:** consumer-local `.mask/generated/implement-rfc/` plus explicit native adapter destinations beneath that consumer.

The asset root never determines the consumer root. Changing CWD to a skill script directory must not change an already selected consumer. Supporting references remain relative to the asset root except for the two explicitly external project-context files.

## Consumer resolution contract

Introduce one shared resolver in `scripts/project_config.py`, returning a context object with `asset_root`, `repo_root`, `project_config_path`, `project_rules_path`, and validated config. Precedence:

- an explicit script `--repo-root PATH` / API `repo_root=PATH`;
- `IMPLEMENT_RFC_PROJECT_ROOT` when no explicit argument was supplied;
- `git -C <invocation-cwd> rev-parse --show-toplevel`.

An explicit invalid value is an error, not permission to fall through. Resolve Git worktrees via Git's actual worktree root; do not jump to the main worktree or follow another repository outside that root. The resolver is not dependent on MASK being installed or the project being in MASK's registry.

For shared mode, read exactly:

```text
<consumer>/.mask/skill-config/implement-rfc/project.json
<consumer>/.mask/skill-config/implement-rfc/project.md
```

Use the supplied `implement-rfc.project.v1` schema initially. No deep-merge configuration system: the file is complete project facts. The skill's Start instructions explicitly load the external project rules before editing and report the selected repository. Missing context is an actionable error; never fall back to SRV's embedded facts for an arbitrary consumer.

Retain legacy local-copy support only when the skill is physically contained at `<consumer>/.agents/skills/implement-rfc`, is not shared through a symlink, and its embedded identity agrees with the selected repository. Explicit hidden test/config overrides remain supported where needed, but they cannot silently redirect output to another repository. Move inherited SRV context to `examples/projects/samplereview/` in the shared source. The shared source must not present SRV config as its default active project.

A local checkout without a remote may still be used in fixtures; real implementation verifies the configured origin name from live Git before starting. Tests use explicit fixture identities rather than a remote network call.

## Helper changes

Audit **all** helper consumers, not just `project_config.py`:

- `audit_board.py`: explicit consumer selects both config and board roots; remove the frozen PROJECT_PATH default that defeats selection.
- `render_runtime_adapters.py`: explicit consumer selects facts and output paths together.
- `validate_portable_agents.py`: separate source validation from selected consumer-adapter validation.
- `codex_lane.py`, `codex_station.py`, `launch_remote_station.py`, `station_lease.py`: remove module-import-time project selection. Resolve after arguments are parsed and pass context explicitly through the selected operation.
- `remote_station_guard.py`: resolve from the event's actual consumer CWD using the same library; do not load context through a linked skill path.
- Tests must not assume `SKILL_DIR.parents[2]` is the consumer or that one process can only ever load one project.

Existing remote routing and delegation remain optional. Preserve their current behavior with focused tests if touched, but do not enable or extend them for MASK.

## Safe adapter rendering

For a shared skill, the renderer may write only:

```text
<consumer>/.codex/agents/rfc-*.toml
<consumer>/.claude/agents/rfc-*.md
<consumer>/.mask/generated/implement-rfc/runtime-adapters.json
```

Do **not** emit `.claude/skills/implement-rfc/SKILL.md` in shared mode. Claude follows the directory symlink directly. Do not put per-project generated files under either symlinked skill root. Resolve and preflight all generated destinations; refuse a linked parent or an existing unrecognized file rather than writing through it. Existing adapters are replaceable only when they carry this renderer's recognized generated marker and are listed in its prior consumer manifest; bootstrap-generated adapters need an explicit one-time reconciliation, not broad overwrite.

Keep portable-source digest generation as an explicit authoring operation in AgentSkills, separate from rendering a consumer. A consumer render/validation must leave the entire shared skill tree byte-identical, including `generated/`. A test hashes the source before/after rendering consumers A and B and validates different project addenda appear only in their own adapter files. `--check` is observational and never repairs source or adapters.

The optional adapter-render command must state that it is generating **role adapters**, not installing or upgrading skills. MASK never invokes it implicitly. A single local agent can use SKILL.md without any native role definitions. Routing/model names are inherited configurable defaults; missing runtime capability is not a required new dependency.

## Bootstrap and cutover

Before the shared resolver exists, use an isolated temporary project-local copy of the original skill with only the two documented project files replaced by the packet's context. The original renderer may run **only while those locations are real project-local directories**, not symlinks. That gives the implementer its existing workflow before MASK exists.

Once this RFC passes, use the shared skill explicitly by path or via a temporary untracked link in a fixture. The actual MASK-managed cutover happens under RFC-MASK-0004. Do not let a bootstrap source copy become a permanent second authority.

## Migration, tests and rejection cases

Test one source with two differently named consumer projects, nested CWD, explicit override, environment selection, an actual Git worktree, no project config, invalid project config, misleading symlink ancestry and repeated calls with different contexts in one process. Verify both native output families without requiring an external model to run.

Shared-mode renderer tests place both agent skill entries as symlinks and assert the canonical SKILL.md is unchanged. Legacy tests exercise the real-directory bootstrap mode separately. Focused existing routing/guard tests run only for helpers changed by this adaptation.

The inherited `test_portable_sources_name_no_project` is not valid for arbitrary project names: it rejects WebSocket masking variables for MASK and the `agentskills.io` standards URL for AgentSkills. Replace blanket substring banning with scoped checks for project-coupled configuration, instructions and concrete repository identities. Include negative fixtures that still detect genuine SRV facts or the wrong consumer, and positive fixtures for harmless protocol identifiers/documentation. Do not rename the product, globally whitelist all matching strings, or delete the portability check. Both adapted test contexts must be green before closeout; the bootstrap false-positive is not a terminal waiver.

## Rollback and limitations

Until MASK cutover, the temporary local executor remains a recoverable bootstrap artifact. Ordinary Git revert can undo source adaptations; the tool does not need to merge project configuration into skills. Do not revert by overwriting live consumer directories. This RFC does not certify the skill's optional remote orchestration or inherited provider model availability.


## Acceptance criteria

- **RFC-ASK-0001-AC01** — The first AgentSkills skill-import commit contains the clean supplied implement-rfc files with recorded provenance and no cache/resource-fork files; no second skill precedes it.
- **RFC-ASK-0001-AC02** — Two consumers use the same physical skill with different project facts/rules, nested invocation and explicit root selection; missing/mismatched context refuses rather than selecting SRV or the source repo.
- **RFC-ASK-0001-AC03** — Every affected helper defers project selection until invocation; focused tests cover sequential different consumers and any changed optional helper path.
- **RFC-ASK-0001-AC04** — Consumer rendering/validation produces distinct correct native adapters without modifying shared SKILL.md, source references or source generated metadata; unsafe destination parents/collisions refuse.
- **RFC-ASK-0001-AC05** — An unlinked legacy local copy remains usable for bootstrapping; shared/local entrypoints are unambiguous. The adapted portability checks pass for MASK and AgentSkills while still detecting genuine project coupling, without requiring MASK itself.
- **RFC-ASK-0001-AC06** — Project context templates, skill instructions, adapter docs and live board agree; the closeout records actual checks and the integration commit.
