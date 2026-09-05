---
schema: "implement-rfc.card.v1"
id: "ASK-0002"
title: "Resolve workflow context from the consumer project"
status: "Done"
rfcs: ["RFC-ASK-0001"]
depends_on: ["ASK-0001"]
---

# ASK-0002: Resolve workflow context from the consumer project

## Objective and owned paths

Own shared config resolution, SKILL.md/README project selection instructions, helper call sites and focused project-context tests.

## Bounded work

Implement explicit root/environment/Git-CWD context, external project facts/rules, missing-context refusal and deliberate legacy local-copy support. Remove import-time project selection from affected scripts; move inherited SRV context to examples.

## Acceptance

Consumers A/B and nested CWD select different facts through one source; wrong/missing contexts refuse. No physical-source-path inference chooses the board. Sequential calls do not reuse another consumer.

## Focused verification

Implement/run the skill's focused `test_project_config.py` plus new shared-context/worktree fixtures and affected helper tests. No optional remote session launch.

## Run record

Implemented invocation-scoped context and all helper consumers. Primary reviewed complete diff and reproduced: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=skills/implement-rfc/tests python3 -m unittest test_project_config test_audit_board test_codex_lane test_codex_station test_launch_remote_station test_station_lease test_remote_station_guard — 143 tests, OK, 2 optional-jsonschema skips. Tests use local fixtures/mocked runtime calls; no remote station launched. Code-simplifier review and git diff --check passed. Commit: this Done move.
