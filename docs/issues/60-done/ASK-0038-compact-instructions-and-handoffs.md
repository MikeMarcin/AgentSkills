---
schema: "implement-rfc.card.v1"
id: "ASK-0038"
title: "Refactor task context and reporting without removing engineering requirements"
status: "Done"
rfcs: ["RFC-ASK-0008"]
depends_on: ["ASK-0037", "ASK-0029"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "compact-instructions-and-handoffs"}
acceptance: [{"criterion":"RFC-ASK-0008-AC03","outcome":"pass","revision":"b2a641f9fbb97aae8531468b8fdf8bba6168aa3a","evidence":{"kind":"command","detail":"11 unified workflow tests pass against included changes; selected rendered context preserves role authority and uncertainty. Existing banner compatibility retained; no measured instruction improvement asserted."}},{"criterion":"RFC-ASK-0008-AC04","outcome":"pass","revision":"b2a641f9fbb97aae8531468b8fdf8bba6168aa3a","evidence":{"kind":"command","detail":"11 unified workflow tests pass against included changes; selected rendered context preserves role authority and uncertainty. Existing banner compatibility retained; no measured instruction improvement asserted."}}]
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

Pre-refactor instruction baseline: 8326de11807875653805aadc13bf3c96e9c60907. Added triggered direct/runner and collection entry points; scoped assignment packets retain exact authority, ownership, evidence and uncertainty. Leaf instructions select only role-specific content and applicable addenda. Existing interactive duplicate-banner compatibility is intentionally retained until receipt-aware native parser/report qualification; no prompt-saving or instruction treatment result is asserted.

Verification: 11 test_unified_workflow.py tests pass, including actual rendered utility/test-runner/worker context and unchanged public claim/finish/human-pending authority. Public usage_report.py --help verified documented interface.

Owner pilot budget on 2026-09-08: up to two real backlog tasks, one bounded attempt each, no purchased credits or usage resets. Heterogeneous tasks are observational; profile remains opt-in.
