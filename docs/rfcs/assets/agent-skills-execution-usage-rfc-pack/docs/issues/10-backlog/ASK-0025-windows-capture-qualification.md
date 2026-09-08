---
schema: "implement-rfc.card.v1"
id: "ASK-0025"
title: "Qualify collector invocation and MASK launcher handling on Windows"
status: "Backlog"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": true, "packet_key": "windows-capture-qualification"}
---

# ASK-0025: Qualify collector invocation and MASK launcher handling on Windows

Governing RFCs: [RFC-ASK-0006](../../rfcs/RFC-ASK-0006-project-aware-turnkey-usage-capture.md).

## Objective and owned paths

Run the same contract through installed Windows Python and MASK, including paths with spaces/non-ASCII/percent characters, case aliases, linked worktrees and read-only pinned skill output. Verify safe recognition of the actual generated mask.cmd template or documented explicit-entrypoint limitation for a custom wrapper. Do not claim POSIX mocks qualify Windows process invocation or filesystem identity.

Own only: `skills/implement-rfc/tests/test_usage_windows.py`; `skills/implement-rfc/scripts/usage_scope.py if native correction required`; `selected Windows acceptance evidence references`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Native Windows cwd and --mask-projects capture work without shell interpolation of registry paths.
- No source/link/global config changes or silent filesystem fallback; native limitations are explicit.

Criterion coverage: RFC-ASK-0006-AC02, RFC-ASK-0006-AC05, RFC-ASK-0006-AC06.

## Focused verification

Run the Windows-specific subprocess and actual two-registration capture checks. Reuse portable parser results unless changed by a native fix.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
