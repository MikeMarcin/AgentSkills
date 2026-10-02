# Milestones

> Generated from `milestone-plan.json`; edit the JSON, not this view.

Plan: **ledger-export** · Coverage: **complete**

These are integration outcomes, not compulsory agent-launch boundaries.

## single-file

Operators can safely export a bounded CSV through the public CLI.

**Work:** `RFC-DRAFT-0001` [AC01]

**Prerequisites:** None

**Completion:**

- The public single-file path preserves destination ownership and exact output/job limits.

**Boundary:** A usable single-file export before the batch increment.

## batch-resume

Operators can resume bounded batches without duplicate output.

**Work:** `RFC-DRAFT-0001` [AC02, AC03]

**Prerequisites:** single-file

**Completion:**

- Public batch/resume paths satisfy partition, interruption and identity behavior.

**Boundary:** The complete defined batch/resume outcome with closeout evidence.
