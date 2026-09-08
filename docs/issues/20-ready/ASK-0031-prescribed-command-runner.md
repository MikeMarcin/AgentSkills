---
schema: "implement-rfc.card.v1"
id: "ASK-0031"
title: "Add bounded deterministic command stages and integrator gates"
status: "Ready"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0021"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "prescribed-command-runner"}
---

# ASK-0031: Add bounded deterministic command stages and integrator gates

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Implement order validation and the command-only runner first. Reuse consumer project resolution and exact evidence helpers. Enforce argv, ownership, root binding, capabilities, budgets, relevant preconditions and integration_gate. Keep running scripts a separately authorized effect; never infer authorization from an uploaded work-order file or successful schema validation. Batch prescribed tests without an LLM deciding each next call.

Own only: `skills/implement-rfc/scripts/run_slice.py`; `skills/implement-rfc/scripts/slice_model.py`; `skills/implement-rfc/tests/test_slice_commands.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Invalid dependency cycles/order/root/commands produce no effects; already-selected stages need no model invocation.
- The result stops at awaiting integration; the runner cannot manufacture semantic acceptance or select the next RFC issue.

Criterion coverage: RFC-ASK-0005-AC01, RFC-ASK-0005-AC02, RFC-ASK-0005-AC06.

## Focused verification

Disposable subprocess fixtures cover success, nonzero exit, zero selected tests, missing output, cancellation and changed candidate. Assert no model/runtime API is touched in command-only mode.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
