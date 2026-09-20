---
schema: "implement-rfc.card.v1"
id: "ASK-0089"
title: "Make coordinator-implementer portable across review rounds"
status: "In Progress"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0088"]
---

# ASK-0089: Portable coordinator-implementer review cycles

Owner-directed correction to the default introduced by
[ASK-0088](../60-done/ASK-0088-simple-milestone-default.md).

## Acceptance

- **AC1:** The public/default strategy is named `coordinator-implementer`, without
  a provider or model in its identity, and both Codex and Claude have explicit
  coordinator and implementer routes.
- **AC2:** A generated `rfc-implementer` role owns the complete milestone engineering
  cycle without nested delegation, so a coordinator can select the same role contract
  on either supported host.
- **AC3:** Required attended review starts the loopback HTML session, arms the durable
  hand-back watch before yielding, and gives any post-review engineering round with
  work to do to a fresh implementer after safe ownership reconciliation.

## Authority

Edit canonical `implement-rfc` skill source, generated manifests, focused tests and
the linked RFC/card directly on main without subagents. Preserve existing acceptance,
publication and consumer-migration boundaries. No push, live model qualification,
global host configuration change or unrelated consumer deployment.
