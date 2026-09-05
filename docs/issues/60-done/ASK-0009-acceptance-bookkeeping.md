---
schema: "implement-rfc.card.v1"
id: "ASK-0009"
title: "Explicit claims, finish and efficient workflow"
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: ["ASK-0008"]
acceptance: [{"criterion":"RFC-ASK-0003-AC02","outcome":"pass","revision":"8acf9c54d3f0cb78a138d9b35a20d813806efec5","evidence":{"kind":"command","detail":"[\"python3\", \"-m\", \"unittest\", \"discover\", \"-s\", \"skills/implement-rfc/tests\", \"-p\", \"test_unified_workflow.py\"]","exit_code":0,"elapsed_seconds":4.397,"stdout_tail":"","stderr_tail":".........\n----------------------------------------------------------------------\nRan 9 tests in 4.319s\n\nOK\n"}}]
---

# Explicit claims, finish and efficient workflow

Owned paths: skills/implement-rfc/** and tests.

Acceptance: RFC-ASK-0003-AC02; implement the approved design and record direct checks.
