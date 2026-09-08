---
schema: "implement-rfc.card.v1"
id: "ASK-0043"
title: "Make the standard worker the default and separate review routing"
status: "Done"
rfcs: ["RFC-ASK-0009"]
depends_on: []
metadata: {"packet":"agent-skills-standard-worker-review", "provisional_id":true}
acceptance: [{"criterion":"RFC-ASK-0009-AC01/AC02 policy and configuration slice","outcome":"pass","revision":"78696978a9acb9c054c18402eac0fcc8835d823d plus supplied working paths","evidence":{"kind":"command","detail":"14 test_render_runtime_adapters tests passed; semantic policy inspected against RFC. Migration and full source qualification remain ASK-0044/0045."}}]
---

# ASK-0043: Make the standard worker the default and separate review routing

Governing RFC: [RFC-ASK-0009](../../rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md).

Criterion coverage: RFC-ASK-0009-AC01, RFC-ASK-0009-AC02.

## Objective and owned paths

Import/reconcile this RFC and four cards through the integrator, capture the real
RFC_BASE_SHA on ASK-0046, and implement the approved default-first policy.
Own `skills/implement-rfc/SKILL.md`, `config/{roles,routing}.json`,
`schemas/routing.schema.json`, route-class handling in `scripts/render_runtime_adapters.py`,
and active `references/{model-routing,delegated-execution}.md` plus focused tests.

## Work

Rename old `rfc-worker` to `rfc-worker-deep`; replace old routine with the broad
`rfc-worker`. Remove the existing-pattern and sensitive-domain blanket exclusions,
not ownership or approval boundaries. Adopt every matrix row; add independent `review`
class in both JSON Schema and Python validation. Keep deep Claude Fable high and
critical Codex Astra xhigh. Preserve other routes, limits, mutation and leaf settings.
Align Fable CLI floor as specified; do not upgrade a user's runtime automatically.
Do not regenerate live consumer adapters before ASK-0044 makes migration safe.

## Acceptance and verification

RFC-ASK-0009-AC01/AC02. Assert exact configuration and unchanged unrelated fields;
read the selected generated instructions against the packet selection cases.
No mandatory live task trial. No source-manifest claim until the full source agrees.

## Run record

Not started. No live IDs reserved or implementation result supplied by this pack.
