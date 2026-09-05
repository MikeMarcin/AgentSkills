---
id: ASK-0003
title: Keep shared source immutable during adapter rendering
status: Backlog
rfc: RFC-ASK-0001
depends_on: ["ASK-0002"]
---

# ASK-0003: Keep shared source immutable during adapter rendering

## Objective and owned paths

Own renderer/validator, changed guard/root call sites, source-manifest authoring command and adapter tests.

## Bounded work

Disable the Claude shim in shared mode. Write per-consumer metadata outside skill links, preflight output ownership/parents, and distinguish portable-source validation from consumer validation. Search all helpers for hard-coded roots and project-config paths. Replace the inherited blanket project-name substring linter with scoped checks: WebSocket mask variables and the agentskills.io reference must pass; genuine SRV/consumer coupling must still fail.

## Acceptance

Both consumer adapter families reflect the right project; shared SKILL.md and all shared assets are unchanged. Linked parents and unknown existing output files refuse. Legacy bootstrap mode remains explicit.

## Focused verification

Run focused `test_render_runtime_adapters.py` in MASK and AgentSkills contexts and shared-symlink tests; include positive/negative coupling-lint fixtures and compare source-tree hashes before/after consumers A/B. Run only affected optional-helper tests.

## Run record

Not started. Record actual commands, outcomes and commits here. Read the live board before claiming. Never stage unrelated paths.
