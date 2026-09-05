---
id: "RFC-ASK-0004"
title: "Selected skill consolidation and consumer migration"
status: "Auto-Verified"
owner: "MikeMarcin"
created: "2026-09-05"
---

# RFC-ASK-0004: Selected skill consolidation and consumer migration

## Accepted scope

Implement the user-approved plan from 2026-09-05. MASK owns user commands, scope-aware planning, v1/v2 state and journal compatibility, source updates, schemas, tests and CLI documentation. AgentSkills owns four personal imports (coauthoring, code-simplifier, technical-book-humanizer, instamat-image-to-pbr), TRELLIS and concept-art imports from sample_studio, the generic sprite workflow from AST, management guidance, and the selected migrations. Keep personal selection separate from the three project-derived skills. Preserve project-specific tooling, unrelated edits, and existing contracts; no push or publication.

## Verification boundary

Public CLI subprocess tests with temporary roots and local bare remotes, offline imported-package tests, AST existing validation/build wrapper, and guarded live migration with backups. Native macOS evidence only; do not infer native Windows or host UI loading acceptance.

## Acceptance criteria

- **RFC-ASK-0004-AC01** — Seven selected skill packages are validated and preserve existing contracts.
- **RFC-ASK-0004-AC02** — Personal, sample_studio and AST deployments use verified managed links with restorable backups.
- **RFC-ASK-0004-AC03** — Offline checks and consumer checks pass; unrelated edits and deferred packages are preserved.
