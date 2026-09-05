---
id: ASK-0003
title: Keep shared source immutable during adapter rendering
status: Done
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

Safe renderer/validator implemented. PYTHONDONTWRITEBYTECODE=1 IMPLEMENT_RFC_PROJECT_ROOT=<consumer> python3 -m unittest discover -s skills/implement-rfc/tests -p test_render_runtime_adapters.py: 11/11 pass for each real MASK and AgentSkills context. Final simplification rerun: 11/11. Includes both symlink families, two consumers, source-byte immutability, legacy copy, collisions/linked parents, observational check and positive/negative coupling lint. Source-only validator, quick_validate.py and git diff --check pass. No consumer adapters generated in real checkouts. Bootstrap suites previously reproduced 6/6 and 8/9 with known inherited lint failure in each context; repaired here. Commit: this Done move.
