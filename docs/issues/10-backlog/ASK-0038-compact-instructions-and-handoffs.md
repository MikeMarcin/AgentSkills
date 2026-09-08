---
schema: "implement-rfc.card.v1"
id: "ASK-0038"
title: "Refactor task context and reporting without removing engineering requirements"
status: "Backlog"
rfcs: ["RFC-ASK-0008"]
depends_on: ["ASK-0037", "ASK-0029"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "compact-instructions-and-handoffs"}
---

# ASK-0038: Refactor task context and reporting without removing engineering requirements

Governing RFCs: [RFC-ASK-0008](../../rfcs/RFC-ASK-0008-routing-profiles-and-portable-rollout.md).

## Objective and owned paths

Apply the supplied writing-for-agents review as an editing aid. Load only branch-relevant procedures and minimal work-order context; preserve exact constraints/evidence/uncertainty. Replace duplicate role banners only after authoritative receipts and backwards-compatible historical parsing exist. Document direct/runner choice, semantic gates and the two collection commands. Keep an identified pre-refactor version for the instruction-only treatment.

Own only: `skills/implement-rfc/SKILL.md`; `skills/implement-rfc/references/delegated-execution.md`; `skills/implement-rfc/references/usage-collection.md`; `skills/implement-rfc/references/bounded-execution.md`; `skills/implement-rfc/tests/test_unified_workflow.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Mechanical inventory does not silently answer semantic authorization/architecture questions; unresolved facts are explicit.
- The core skill does not expand into the whole pack, and retained assets are not runtime context or live state.

Criterion coverage: RFC-ASK-0008-AC03, RFC-ASK-0008-AC04.

## Focused verification

Test branch-specific context assembly and compare fixture packets; check actual selected content, not just Markdown byte counts. Verify the existing bookkeeping/accepted-finish contract stays unchanged.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
