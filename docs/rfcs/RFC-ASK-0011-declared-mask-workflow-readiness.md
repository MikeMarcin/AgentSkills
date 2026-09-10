---
schema: "implement-rfc.rfc.v1"
id: "RFC-ASK-0011"
title: "Declared MASK workflow readiness for implement-rfc"
status: "Auto-Verified"
---

# Declared MASK workflow readiness for implement-rfc

## Decision

Publish implement-rfc's required native role set as a passive MASK workflow
descriptor (`mask-workflow.json` beside `SKILL.md`), provide the staged
preparation entrypoint that MASK's approved-setup path invokes, and add a startup
preflight that accepts only a MASK program advertising `workflow_readiness_v1`.

This is the AgentSkills side of ManageAgentSkills RFC-MASK-0019 ("Declared
workflow readiness and optional setup"). MASK's engine consumes the descriptor,
runs the entrypoint only under explicit `package.setup` consent, validates the
staged outputs, computes the portable `native-roles.lock.json` and deploys or
retires role files through its own typed journal. AgentSkills owns role bytes,
consumer-context/routing semantics and the authoring refactor; MASK owns
deployment, ownership and recovery. No MASK runtime code lives here.

## Design

- **Descriptor.** `skills/implement-rfc/mask-workflow.json` declares the
  required consumer inputs (`project.json` required JSON, `project.md` required
  text, the optional execution-selection JSON) and every current role for both
  supported agents: `rfc-integrator` plus the seven leaf roles. Roles are
  produced by the setup action `prepare-roles` because the rendered definitions
  interpolate consumer addenda and honour explicit routing profiles, which
  universal static files cannot represent. Names and routes are derived from
  `config/roles.json` and `config/routing.json` at staging time; no model ID is
  hard-coded in the descriptor.
- **Staging entrypoint.** `scripts/prepare_mask_roles.py` implements MASK's fixed
  interface (`--repo-root`, `--output-root`, `--request-file`; request schema
  `mask.setup-request.v1`). It reuses the renderer's pure generation functions,
  writes exactly `STAGE/AGENT/NAME.ext` for the requested roles and nothing else,
  never touches consumer destinations or MASK state, and refuses requests whose
  declared input digests differ from the consumer files it reads.
- **Renderer refactor.** `render_runtime_adapters.py` exposes `generate_roles`
  so the standalone renderer and the staging entrypoint share one generation
  path; standalone rendering behavior is unchanged.
- **Preflight.** `scripts/workflow_preflight.py` runs the selected MASK program
  read-only (`capabilities --json`, `ensure --check --json`) against an explicit
  consumer root and returns `ready`, `incomplete`, `unsupported` or `error`. An
  older program without `workflow_readiness_v1` is reported as unsupported; a
  link-only success is never accepted as workflow readiness.

## Acceptance criteria

**RFC-ASK-0011-AC01 — Valid descriptor.** MASK parses the shipped descriptor
without `workflow.invalid`/`workflow.role_invalid`, reports `workflow=declared`
for implement-rfc, and lists every current role for both agents.

**RFC-ASK-0011-AC02 — Staged preparation.** Under explicit setup consent, MASK's
real CLI runs the entrypoint, validates the stage, writes the portable lock and
deploys the role files into a disposable consumer; `ensure` then reports complete
workflow readiness and an unchanged rerun runs no script.

**RFC-ASK-0011-AC03 — Refusal paths.** `--check`/`--dry-run` never execute the
entrypoint; declined consent leaves setup incomplete with exit 4; a stage request
whose inputs disagree with the consumer is refused by the entrypoint.

**RFC-ASK-0011-AC04 — Consumer fidelity.** Staged roles equal the standalone
renderer's output for the same consumer, so addenda and explicit routes are
neither erased nor leaked between two distinct consumers.

**RFC-ASK-0011-AC05 — Retirement.** Removing the requirement retires the
MASK-owned role files through MASK's own plan.

**RFC-ASK-0011-AC06 — Preflight skew.** The preflight accepts only a program
advertising `workflow_readiness_v1` and an `ensure --check` result with complete
workflow readiness; other results are reported as unsupported/incomplete.

**RFC-ASK-0011-AC07 — Repository gate.** The configured structure gate and the
focused skill tests pass; the portable manifest is regenerated.

## Implementation authorization

The owner authorized this separate AgentSkills mandate on 2026-09-09 to unblock
ManageAgentSkills MASK-0090/MASK-0092. Scope is this repository only; the MASK
repository is read-only from here. No push, publication or consumer migration.

## Verified implementation

The sole [closeout](../issues/60-done/ASK-0059-declare-mask-workflow-readiness.md)
records actual MASK CLI evidence for all seven criteria against baseline
0dd8a29a3d93776a22da325db4d9a4f3299daf2a on macOS; Windows/Linux lanes and fresh
host loading remain unverified. Descriptor, entrypoint, preflight and refactored
renderer landed in 4bd053c and 0f8b3cd.
