---
schema: "implement-rfc.card.v1"
id: "ASK-0031"
title: "Add bounded deterministic command stages and integrator gates"
status: "Done"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0021"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "prescribed-command-runner"}
acceptance: [{"criterion":"RFC-ASK-0005-AC01/AC02/AC06 command-only boundary","outcome":"pass","revision":"dbb343295a8094108d93accb7f80421c0ffbcfd1","evidence":{"kind":"observation","detail":"12 subprocess/admission tests passed; command batching has zero model transitions and always stops at semantic gate. Exact extended admission contract and limitations recorded in card; durable native agent work remains separate."}}]
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

## Implemented contract

Command-only admission requires physical `root_identity`, `invocation_root`, `input_hashes`, and `routing_ref` in addition to the proposal fields. Frozen permission JSON uses `implement-rfc.command-permissions.v1`, `execution: local_unsandboxed`, and exact `allowed_argv`. Predicates explicitly select `tests: none|unittest|pytest`; zero/missing selected-test evidence fails. The final gate depends on every prior task. This serial portable driver reports its lack of OS sandboxing, rejects inline evaluated fragments, and never dispatches agents or changes issue status. Input files, routing and permissions are rechecked at each stage; unrelated files do not invalidate a check.

Command evidence retains the existing record_evidence wire shape, with bounded stream files and timeout handling instead of its unbounded subprocess capture. At-most-one dispatch per run ID; uncertain runs are inspected, never silently rerun. General driver recovery belongs to ASK-0032.

Verification: `python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_slice_commands.py` — 12 tests passed. Public subprocess start reaches awaiting_integration; stale approval, changed roots/candidates, cycles, zero tests, failure, absent artifacts, cancellation, output limit, timeout, run reuse and exact spaced/non-ASCII argv exercised. Temporary consumers cleaned. No native agent support is claimed.
