---
schema: "implement-rfc.card.v1"
id: "ASK-0024"
title: "Package the one-command collector and qualify a linked macOS consumer"
status: "Ready"
rfcs: ["RFC-ASK-0006"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "package-and-macos-capture"}
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
