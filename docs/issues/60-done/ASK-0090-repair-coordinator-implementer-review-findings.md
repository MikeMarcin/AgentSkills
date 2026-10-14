---
schema: "implement-rfc.card.v1"
id: "ASK-0090"
title: "Repair coordinator-implementer review findings"
status: "Done"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0089"]
acceptance: [{"criterion":"AC1: MASK accepts and deploys the coordinator-implementer profile","outcome":"pass","revision":"57d9fe62e8e4372f53da7974523a03fb0a7dee70","evidence":{"kind":"command","detail":"MASK_TEST_PROGRAM=/Users/EXAMPLE/Documents/GitHub/ManageAgentSkills/mask.py python3 -B -m unittest skills/implement-rfc/tests/test_strategy_mask_public.py passes in 61.360s across two disposable installed consumers, including guarded staged setup and both generated provider roles."}},{"criterion":"AC2: explicit route precedence is preserved","outcome":"pass","revision":"57d9fe62e8e4372f53da7974523a03fb0a7dee70","evidence":{"kind":"command","detail":"test_strategy_host verifies explicit Astra/high coordinator and Terra/medium implementer routes render unchanged and inspect as configuration_consistent; defaults fill only absent slots."}},{"criterion":"AC3: published routing schema matches canonical roles and classes","outcome":"pass","revision":"57d9fe62e8e4372f53da7974523a03fb0a7dee70","evidence":{"kind":"command","detail":"Focused renderer tests compare routing.schema.json role and class sets against canonical routing.json; 42 strategy/renderer/workflow tests pass."}},{"criterion":"AC4: attended-review watch remains armed until hand-back","outcome":"pass","revision":"57d9fe62e8e4372f53da7974523a03fb0a7dee70","evidence":{"kind":"command","detail":"Coordinator recipe uses wait --after SEQUENCE --kind handed-back before yielding. All 24 attended-review tests pass, including the behavioral case where a decision does not satisfy a hand-back-only wait."}}]
---

# ASK-0090: Repair coordinator-implementer review findings

Follow-up for the independent critical review of ASK-0089.

## Acceptance

- **AC1:** MASK accepts the coordinator-implementer profile and the public installed
  workflow test passes through the actual MASK program.
- **AC2:** Explicit selected coordinator and implementer routes retain precedence in
  rendering and inspection; defaults fill only absent route slots.
- **AC3:** The published routing schema accepts the canonical `rfc-implementer` and
  `implementation` class and rejects drift consistently with the Python validator.
- **AC4:** The coordinator keeps a durable attended-review watch armed until hand-back,
  re-arming after decision-only wakeups, with behavioral test coverage.

## Authority

Edit the canonical implement-rfc source, focused tests, generated manifest and linked
bookkeeping directly. No push, consumer deployment, global host setting change or
live model qualification.
