# Source grounding and proposal boundaries

## Governing uploaded source

**AgentSkills(2).zip** is the implementation baseline used for this pack, not the
older AgentSkills(1) archive or SAMPLE_STUDIO's historical copied skill. Byte hashes and
selected canonical file hashes are in [reference/source-manifest.json](reference/source-manifest.json).
The `.git` directory, resource forks, symlink payloads and caches are not included
in the deliverable. No live branch/commit state is inferred from archive timestamps.

The source defines AgentSkills as the canonical skills-content library and MASK as
the deployment manager. The current issue counter is ASK-0021; current RFCs 0001–0004
are settled. `docs/rfcs/README.md`, `docs/issues/README.md`, consumer project context
and `references/pack-lifecycle.md` govern intake, reservation, one closeout per RFC,
status truth and immutable retained packs. Those existing rules are preserved.

Important current implementation seams:

| Source | Supported fact | New work |
|---|---|---|
| skills/implement-rfc/SKILL.md | Bounded/direct work, scoped board queries, evidence and guarded acceptance already exist | Use runner only for stable prescribed stages, not a compulsory agent tree |
| config/roles.json | Current mechanical role is rfc-test-runner; scout/workers/reviewers may spawn utilities | Leaf defaults and reliable external result ownership |
| config/routing.json | Routine worker Sol high; deep Astra high shared with reviewer; mechanical Luna xhigh | Independent candidate profile, retain reviewer settings and explicit user selection |
| scripts/issue_board.py | Existing queue/claim/finish bookkeeping boundary | Reuse; runner cannot manufacture acceptance |
| scripts/record_evidence.py | Existing exact-command evidence helper | Reuse; do not create a parallel proof system |
| scripts/role_usage.py | Activity observability, not a subscription meter | Common project-aware capture/accounting without breaking legacy activity callers |
| scripts/project_config.py | Consumer context separate from installed skill source | Use that separation for writes; collector supports measuring projects without a board |
| scripts/render_runtime_adapters.py | Native adapter generation from shared policy | Profiles, truthful capability/enforcement and scoped output |

## MASK source consulted

The attached `manage_agent_skills_project_source.md`, generated September 7 at
18:48:22 Pacific, contains the current implementation and tests. Read paths:

- `mask.py::project_dispatch`: `project.list` returns `data.projects` as a list of
  records with `available=Path(root).is_dir()`; it does not return a root-keyed map.
- `mask.py::result`: protocol envelope `schema_version=1`, `tool=mask`, canonical
  command `project.list`, `ok`, `changed`, `error` and `data`.
- `mask_core.py::registry_record`, `registered_root`, `state`: root identity is
  **`root_identity`**, containing `device` and `inode`; availability alone is not
  identity validation.
- `mask_core.py::project_root`: implicit MASK discovery stays in the nearest Git
  worktree; outside Git MASK requires explicit selection. The collector's declared
  non-Git fallback is an intentional new collector behavior, not an existing MASK fact.
- `mask_install.py::launcher_text`: exact owned Windows v1 .cmd template and quoted
  interpreter/program paths, with percent escaping.
- CLI/state docs and tests: project.list retains missing registrations and is
  project-only; worktrees have independent physical registrations. General `--all`
  semantics may include user scope and are not used for this collector.
- Pinned/source/development records: deployment modes differ; updating canonical
  content is not proof that a pinned consumer changed.

The adapter uses this existing public CLI. This is **not** a new MASK implementation
RFC, and it must not import/edit `MASK_HOME/state.json` to avoid a CLI issue.

## Retained measurements: what they establish

The earlier `rfc-measurement-analysis/FINDINGS.md` and its archive are retained
analysis inputs from this conversation, not fresh source truth. The pack uses their
limited observations to choose experiment hypotheses: more coordination in the
captured SamplePlanner workload; large mostly cached parent contexts; two stopped
scouts without observed resumption; no Astra-low comparison or accepted-work oracle.

The chronology correction is preserved: the utilities were launched well before
the scout limit, and some completed before the scout stopped. “No late fan-out”
alone would not fix that result-delivery failure. Per-task attribution and exact
consumption still need the new records. Rate-equivalent control shares are not
predicted quota savings. No raw private measurement/transcript archive is bundled.

## New design and included implementation seed

RFC-ASK-0005's runner/lifecycle, RFC-ASK-0007's reconciler/readout, and the new routing
profiles are proposals to implement. The payload implements cwd/MASK selection and
updated collection/quota helpers based on the earlier audit kit. It is runnable,
not a stub, but native production qualification and bounded-index hardening remain
explicit cards. This packet does not claim an operational runner exists already.

The supplied writing-for-agents skill informs progressive disclosure and compact
handoffs. Its wording heuristics are not treated as measured guarantees; explicit
requirements, security boundaries and uncertainty are retained.

## External runtime references, checked for the adapter design

- OpenAI, **Codex App Server**: https://developers.openai.com/codex/app-server/
  documents managed thread/turn events and account-rate-limit read operations.
  Installed capability discovery and permission preservation are still required.
- Anthropic, **Run Claude Code programmatically**:
  https://code.claude.com/docs/en/headless — print-mode structured output and resumable
  native sessions. The stream-json example includes `--verbose`.
- Anthropic, **CLI reference**: https://code.claude.com/docs/en/cli-reference — mode,
  resumption, turn-limit and output options; supported behavior is runtime-specific.

These references justify adapter entrypoints, not an assertion of subscription
savings, permission equivalence, subagent-ID interchangeability or universal version
support. Current model benchmarks/rate cards are not required to implement this pack;
the experiment must measure the actual selected routes rather than assume a winner.
