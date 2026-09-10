---
schema: "implement-rfc.card.v1"
id: "ASK-0059"
title: "Declare MASK workflow readiness for implement-rfc"
status: "In Progress"
rfcs: ["RFC-ASK-0011"]
depends_on: []
closeout_for: ["RFC-ASK-0011"]
metadata: {"mandate": "mask-corrective-ux-readiness D10 rev3", "upstream": "ManageAgentSkills MASK-0090 / RFC-MASK-0019"}
---

# ASK-0059: Declare MASK workflow readiness for implement-rfc

Governing RFC: [RFC-ASK-0011](../../rfcs/RFC-ASK-0011-declared-mask-workflow-readiness.md).

## Objective and owned paths

Ship `mask-workflow.json`, the staged preparation entrypoint and the startup
preflight for implement-rfc; prove them with MASK's real CLI against disposable
consumers; record the handoff facts MASK-0090 needs.

Owned paths:

- `skills/implement-rfc/mask-workflow.json`
- `skills/implement-rfc/scripts/prepare_mask_roles.py`
- `skills/implement-rfc/scripts/workflow_preflight.py`
- `skills/implement-rfc/scripts/render_runtime_adapters.py` (shared generation function only)
- `skills/implement-rfc/tests/test_mask_workflow.py`
- `skills/implement-rfc/generated/portable-manifest.json`
- `skills/implement-rfc/README.md`, `skills/implement-rfc/SKILL.md` (readiness paragraph)
- this card and the RFC

## Acceptance

Criterion coverage: RFC-ASK-0011-AC01 through RFC-ASK-0011-AC07.

## Continuation

RFC_BASE_SHA: 0dd8a29a3d93776a22da325db4d9a4f3299daf2a

Exit criteria for this milestone: all seven criteria have actual evidence from
MASK's CLI run as a subprocess (macOS), the structure gate passes, and the
completion commit is recorded here.
