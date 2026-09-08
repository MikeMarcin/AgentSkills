---
schema: "implement-rfc.card.v1"
id: "ASK-0022"
title: "Implement invocation-scoped project discovery and MASK selection"
status: "Ready"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0021"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "project-scope-and-mask-adapter"}
---

# ASK-0022: Implement invocation-scoped project discovery and MASK selection

Governing RFCs: [RFC-ASK-0006](../../rfcs/RFC-ASK-0006-project-aware-turnkey-usage-capture.md).

## Objective and owned paths

Adopt and review the scope seed. Infer from cwd, not script/symlink location; distinguish the collector non-Git fallback from MASK semantics. Use exact project.list JSON and root_identity. Keep separate registered worktrees, unavailable rows, explicit aliases, longest matching nested roots and optional worktree expansion. Support MASK_HOME, the generated Windows launcher and explicit paths. Never read MASK internal files as a shortcut.

Own only: `skills/implement-rfc/scripts/usage_scope.py`; `skills/implement-rfc/tests/test_usage_scope.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Default root and explicit root selection stay inside their intended boundaries; missing MASK cannot select all machine history.
- The actual public MASK response shape is fixture-tested, including extra fields, pinned/dev-link records and root-identity replacement.

Criterion coverage: RFC-ASK-0006-AC01, RFC-ASK-0006-AC02.

## Focused verification

Run scope tests with fake MASK and real temporary Git/worktree fixtures; inspect no registration/config/source changes. Exercise failures and an empty registry.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
