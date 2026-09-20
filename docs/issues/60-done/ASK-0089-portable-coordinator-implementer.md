---
schema: "implement-rfc.card.v1"
id: "ASK-0089"
title: "Make coordinator-implementer portable across review rounds"
status: "Done"
rfcs: ["RFC-ASK-0014"]
depends_on: ["ASK-0088"]
acceptance: [{"criterion":"AC1: provider-neutral strategy identity and explicit Codex/Claude coordinator and implementer routes","outcome":"pass","revision":"afd62da274a33ea49acda8af3b02ee93cfd91ab0","evidence":{"kind":"command","detail":"Focused execution-strategy, host-control, renderer and MASK workflow tests pass. The default resolves as coordinator-implementer with no provider-bearing strategy name; routing.json defines independent rfc-coordinator and rfc-implementer routes for Codex and Claude."}},{"criterion":"AC2: generated non-delegating rfc-implementer owns the complete milestone cycle","outcome":"pass","revision":"afd62da274a33ea49acda8af3b02ee93cfd91ab0","evidence":{"kind":"command","detail":"57 focused tests pass, including deterministic native adapter rendering, role schema migration, MASK staged role setup and leaf waiting contracts. Portable validation and skill quick validation pass."}},{"criterion":"AC3: loopback attended review, durable hand-back watch and fresh post-review implementer","outcome":"pass","revision":"afd62da274a33ea49acda8af3b02ee93cfd91ab0","evidence":{"kind":"artifact","detail":"The coordinator-implementer recipe orders loopback server startup, URL presentation, coordinator-owned wait arming before yield, status intake on wake and a fresh rfc-implementer whenever hand-back leaves engineering, interpretation or upkeep work. A focused instruction-path test locks the ordering."}}]
---

# ASK-0089: Portable coordinator-implementer review cycles

Owner-directed correction to the default introduced by
[ASK-0088](ASK-0088-simple-milestone-default.md).

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
