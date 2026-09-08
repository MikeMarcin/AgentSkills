---
schema: "implement-rfc.card.v1"
id: "ASK-0025"
title: "Qualify collector invocation and MASK launcher handling on Windows"
status: "Done"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "windows-capture-qualification"}
acceptance: [{"criterion":"RFC-ASK-0006-AC02","outcome":"pass","revision":"3aa9ee77457c577365eb29612fe33853bae52aac","evidence":{"kind":"observation","detail":"Native Windows ExampleWinHost collector/MASK launcher/worktree/link/read-only-file fixtures passed; 78 usage cases reconciled after two test-only fixes (one POSIX skip). Actual zero-argument capture exit0, partial/empty metadata ZIP retained. Details and actual source snapshot in card."}},{"criterion":"RFC-ASK-0006-AC05","outcome":"pass","revision":"3aa9ee77457c577365eb29612fe33853bae52aac","evidence":{"kind":"observation","detail":"Native Windows ExampleWinHost collector/MASK launcher/worktree/link/read-only-file fixtures passed; 78 usage cases reconciled after two test-only fixes (one POSIX skip). Actual zero-argument capture exit0, partial/empty metadata ZIP retained. Details and actual source snapshot in card."}},{"criterion":"RFC-ASK-0006-AC06","outcome":"pass","revision":"3aa9ee77457c577365eb29612fe33853bae52aac","evidence":{"kind":"observation","detail":"Native Windows ExampleWinHost collector/MASK launcher/worktree/link/read-only-file fixtures passed; 78 usage cases reconciled after two test-only fixes (one POSIX skip). Actual zero-argument capture exit0, partial/empty metadata ZIP retained. Details and actual source snapshot in card."}}]
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


## Owner-confirmed native host and qualification correction

Owner clarified the existing ExampleWinHost SSH/station on 2026-09-08. Trusted alias
`example-win-host` reaches native Windows build 26200 with Python 3.14.6 and public
MASK 0.2.0. The active MASK station is read-only-proof and was not modified.
Testing uses the exact source snapshot `1a165ef` in a disposable archive checkout.

Integrator expands this card's owned fixture paths to `test_usage_capture.py`
and `test_slice_commands.py`: native tests exposed a POSIX-only historical alias
and a generated Python source file written with Windows locale encoding. Both
are fixture corrections, preserving the production absolute-path and exact-argv
contracts. Native stderr confirmed SyntaxError from the fixture's non-UTF-8 byte;
no command interpolation or runtime path coercion was involved.


## Native acceptance

ExampleWinHost Windows 10.0.26200, Python 3.14.6, public MASK 0.2.0, 2026-09-08:
`python -B -m unittest discover -s skills/implement-rfc/tests -p test_usage*.py -q`
ran 78 cases: 75 passed, two fixture alias errors, one expected POSIX-only skip.
Both fixture alias cases and the separate runner Unicode-source case passed their
focused native rerun after the recorded fixture corrections. The same three
corrected cases passed on macOS. Production capture code was unchanged.

The two native Windows-specific tests passed: real public MASK registry and
owned launcher, two worktrees plus unavailable root, percent/non-ASCII/case paths,
custom-wrapper refusal, actual symbolic-link invocation, file-attribute read-only
package, unchanged package hashes and a valid Windows ZIP. The read-only fixture
asserts Windows file attributes, not an untested directory ACL guarantee.

A genuine zero-argument invocation from `C:\code\git\AgentSkills-mask-station`
using the candidate's absolute `usage.py` completed with exit 0 and created
`C:\Users\example\AppData\Local\implement-rfc\usage\captures\rfc-usage-local-20260908T040857Z-43d1485d.zip`.
It reports one project, zero matching sessions, partial_or_empty coverage; absence
is not reported as zero consumption or cross-host completeness. No model/network
provider call, deployment, source/station edit or settings change was made.

Evidence source: `1a165ef` archive plus the two exact test-only changes included in
this finish. Native fixture root is task-owned and scheduled for cleanup after
remaining command qualification; the private user-local capture is retained.
The earlier unavailable-host conclusion was superseded by the owner's SSH
clarification; no host-key verification or permissions were bypassed.
