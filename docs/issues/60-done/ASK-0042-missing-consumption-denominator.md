---
schema: "implement-rfc.card.v1"
id: "ASK-0042"
title: "Keep accepted-task consumption unknown when usage evidence is absent"
status: "Done"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0029"]
metadata: {"packet": "agent-skills-execution-usage", "discovery": "integration-missing-consumption"}
acceptance: [{"criterion":"RFC-ASK-0007-AC04","outcome":"pass","revision":"1bce939602da524a015a4e43d6fce56b990e830f","evidence":{"kind":"command","detail":"Seven focused offline report tests pass. Accepted outcomes without ledger data yield null; an observed zero-token row yields zero. Included changes establish this regression guard."}},{"criterion":"RFC-ASK-0007-AC05","outcome":"pass","revision":"1bce939602da524a015a4e43d6fce56b990e830f","evidence":{"kind":"command","detail":"Seven focused offline report tests pass. Accepted outcomes without ledger data yield null; an observed zero-token row yields zero. Included changes establish this regression guard."}}]
---

# ASK-0042: Missing consumption denominator

## Objective and owned paths

Integration found that accepted outcomes with no corresponding ledger rows could
produce a false zero tokens-per-accepted-task value. Require observed consumption
coverage for every accepted task before reporting a precise ratio.

Own only `skills/implement-rfc/scripts/usage_outcomes.py` and
`skills/implement-rfc/tests/test_usage_report.py`.

## Acceptance

RFC-ASK-0007-AC04/AC05: accepted tasks lacking usage evidence retain a null ratio;
observed zero-token records remain distinct from absent records. Existing joins,
reopen handling and archive comparison remain unchanged.

## Verification

Focused offline outcome/report tests. No model calls or user data required.
