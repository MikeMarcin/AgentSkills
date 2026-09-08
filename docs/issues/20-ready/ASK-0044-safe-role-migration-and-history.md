---
schema: "implement-rfc.card.v1"
id: "ASK-0044"
title: "Migrate role adapters safely and preserve historical audit meaning"
status: "Ready"
rfcs: ["RFC-ASK-0009"]
depends_on: ["ASK-0043"]
metadata: {"packet":"agent-skills-standard-worker-review", "provisional_id":true}
---

# ASK-0044: Migrate role adapters safely and preserve historical audit meaning

Governing RFC: [RFC-ASK-0009](../../rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md).

Criterion coverage: RFC-ASK-0009-AC03, RFC-ASK-0009-AC04.

## Objective and owned paths

Own bounded migration changes in `scripts/render_runtime_adapters.py`,
`scripts/{codex_lane,role_usage}.py`, their focused tests, and active
`references/{routing-audit,codex-lanes}.md`. Touch usage capture/reporting only where
new role names actually require a compatibility fix; do not rebuild accounting.

## Work

Apply common worker addenda to both roles once; retain legacy routine addenda for
standard and new deep-specific addenda for deep. Preflight renamed/replaced/retired
adapter paths using prior hashes and ownership; retire only clean generated routine
files. Detect stale retired files in check mode. Refuse modified or unowned files
before writing; keep interruption/retry/rollback detectable without a new framework.

Inventory active assignments before scoped regeneration. Do not remap an old admitted
`rfc-worker` deep request to standard. Diagnose obsolete new selectors explicitly.
Read new standard/deep and old routine/deep/unknown decisions, retain raw role identities,
and never reinterpret legacy generic worker records using today's config or model name.
Preserve declared versus observed route evidence and existing authority precedence.

## Acceptance and verification

RFC-ASK-0009-AC03/AC04. Add fixture cases for clean rename, modified old worker/routine,
unmanaged collision, symlink escape, interrupted migration/retry, no-op/check purity,
common and role-specific addenda, stale override keys, frozen old assignments,
old/new/ambiguous history, duplicate banners and unknown efforts. No live user histories
or credentials are needed. Keep runtime limitations explicit.

## Run record

Not started.
