---
id: ASK-0002
title: Resolve workflow context from the consumer project
status: Backlog
rfc: RFC-ASK-0001
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

Not started. Record actual commands, outcomes and commits here. Read the live board before claiming. Never stage unrelated paths.
