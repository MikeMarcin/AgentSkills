---
schema: "implement-rfc.card.v1"
id: "ASK-0090"
title: "Repair coordinator-implementer review findings"
status: "In Progress"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0089"]
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
