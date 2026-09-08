---
schema: "implement-rfc.card.v1"
id: "ASK-0035"
title: "Qualify bounded execution and failure delivery across native hosts"
status: "Backlog"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0033", "ASK-0034"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "runner-native-qualification"}
---

# ASK-0035: Qualify bounded execution and failure delivery across native hosts

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Exercise command-only and one controlled agent slice on the native macOS/Windows combinations to be claimed. Demonstrate event-driven waiting, exact permission behavior, durable result collection and user cancellation. Review crash-after-launch and missing-report behavior at the native boundary. Keep unsupported combinations explicit and direct execution available; do not make an unavailable platform pass by relabelling a fake driver.

Own only: `skills/implement-rfc/tests/test_slice_integration.py`; `skills/implement-rfc/references/bounded-execution.md`; `selected native qualification records`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Claimed native combinations have actual runtime/permission/identity evidence and a result inspected at an integrator gate.
- No destructive reruns, lost ownership, automatic reset/credit use, or unbounded recovery under failure.

Criterion coverage: RFC-ASK-0005-AC01, RFC-ASK-0005-AC03, RFC-ASK-0005-AC04, RFC-ASK-0005-AC05, RFC-ASK-0005-AC06.

## Focused verification

Run selected end-to-end and negative native checks; reuse unchanged unit results. Capture only compact redacted facts and exact commands/artifact references.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
