---
schema: "implement-rfc.card.v1"
id: "ASK-0024"
title: "Package the one-command collector and qualify a linked macOS consumer"
status: "Done"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "package-and-macos-capture"}
acceptance: [{"criterion":"ASK-0024 native macOS CLI","outcome":"pass","revision":"3e1348e1d5dcd15b4450900d5a971306b8dd097d","evidence":{"kind":"observation","detail":"Three CLI tests and two installed native captures passed; exact artifacts, source revision, partial coverage and resource observations recorded in this card. Windows remains open."}}]
---

# ASK-0024: Package the one-command collector and qualify a linked macOS consumer

Governing RFCs: [RFC-ASK-0006](../../rfcs/RFC-ASK-0006-project-aware-turnkey-usage-capture.md).

## Objective and owned paths

Make help/default output practical and integrate the helper into the canonical package. Invoke from nested cwd through a real MASK-managed installed path. Capture one project by default and all local registrations via --mask-projects, including a worktree and unavailable row. Verify output outside the shared source, read-only installed artifact behavior, home overrides, strict exit, dry-run and metadata privacy. Use private live data only in a user-local archive, not committed fixtures.

Own only: `skills/implement-rfc/references/usage-collection.md`; `skills/implement-rfc/scripts/usage.py`; `skills/implement-rfc/tests/test_usage_cli.py`; `selected acceptance evidence references`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- One command yields an attachment-ready ZIP with readable coverage and no manual list of project paths.
- Native macOS behavior and exact installed source/artifact version are recorded; deployment success is not called proof of UI first-prompt loading.

Criterion coverage: RFC-ASK-0006-AC01, RFC-ASK-0006-AC05, RFC-ASK-0006-AC06.

## Focused verification

Run focused CLI integration tests plus named native macOS commands from the usage runbook. Record exact artifact path/hash locally; commit only redacted acceptance facts.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.

## Native macOS evidence

Canonical payload revision: 3e1348e1d5dcd15b4450900d5a971306b8dd097d. Existing MASK-managed `.agents/skills/implement-rfc` resolves to canonical AgentSkills. Invoked its absolute `scripts/usage.py --json` from `AgentSkills/docs`, then `--mask-projects --mask-python-entrypoint /Users/example/Documents/GitHub/ManageAgentSkills/mask.py --json`. Both exited 0. Cwd selection produced an explicitly empty archive; all seven registrations produced 400 active sessions. No registration or source binding changed.

Private user-local artifacts (not committed): `~/Library/Application Support/implement-rfc/usage/captures/rfc-usage-local-20260908T025829Z-3200c47f.zip` and `rfc-usage-local-20260908T025848Z-e0b66bad.zip`. Registry archive SHA256: 35ae8e14421dc61312b85f26f4f6c0901603c278e4a83f5e503ae5a4946cb559; 30,339,196 bytes. Scan: 43,290,960,802 bytes, 333.446 seconds, native peak RSS 393,494,528 bytes. Coverage is partial: 23,940 warnings; the retained warning sample consists of project-change exclusions, not invented zero usage. These archives are user deliverables, not disposable checkout evidence.

`python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_usage_cli.py`: 3 tests pass on macOS. Real disposable MASK registry exercised two worktrees and an unavailable root; nested linked invocation, strict empty archive, exact member hashes and read-only package without bytecode writes passed. Fixture roots were automatically removed; no Windows or UI host-loading claim.
