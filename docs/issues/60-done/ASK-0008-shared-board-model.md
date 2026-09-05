---
schema: "implement-rfc.card.v1"
id: "ASK-0008"
title: "Canonical board, context and allocation"
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: []
---

# Canonical board, context and allocation

Owned paths: skills/implement-rfc/scripts/{board_model,project_config,issue_board}.py; config/schema and tests.

Acceptance: RFC-ASK-0003-AC01; implement the approved design, preserve unrelated changes, verify focused public behavior and record actual results.

## Progress

Claimed for implementation.

Core complete: canonical card/project schema, scope-aware queue, shared single/per-area counter history and Git bookkeeping APIs. Tests: issue_board 32, audit_board 17, project_config 15, unified public workflow 9 passed on macOS. Canonical self-board migration is isolated in this worktree; live source remains unchanged.
