---
schema: "implement-rfc.card.v1"
id: "ASK-0025"
title: "Qualify collector invocation and MASK launcher handling on Windows"
status: "Ready"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "windows-capture-qualification"}
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

Prepared `test_usage_windows.py` with two native-only qualification tests: real disposable MASK registry/worktrees/unavailable registration, public self-install plan/apply of an owned mask.cmd, percent/non-ASCII paths, Windows case aliases, unsupported wrapper refusal, linked invocation, immutable read-only file attributes and archive platform/hash checks. No MASK internal state edits or source copies as deployment fallback.

Command: `python3 -m unittest discover -s skills/implement-rfc/tests -p test_usage_windows.py -v` on macOS. Result: two skipped because native Windows is required. This is test preparation, not a Windows pass. Native command: set MASK_TEST_PROGRAM to the Windows checkout's absolute mask.py and run that same unittest command; link privilege must already be available. No permission grants are authorized or performed.

The repository has no configured remote station and specifies local implementation only. Required Windows evidence remains blocked, including native read-only/pinned attributes; no POSIX mock substitutes. One budgeted Claude preparation attempt hit the structured native turn limit with no final report; no retry/recovery was made. The integrator prepared these fixtures directly.
