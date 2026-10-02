---
schema: "implement-rfc.card.v1"
id: "ASK-0095"
title: "Publish the canonical RFC bundle in the source index"
status: "Done"
rfcs: ["RFC-ASK-0015"]
depends_on: ["ASK-0093"]
acceptance: [{"criterion":"package-discovery","outcome":"pass","revision":"fb67261a5fd8a69231e963226189fd98458e4d82","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-evidence.json","detail":"All 16 committed canonical packages remain discoverable and validate through the public CLI."}},{"criterion":"canonical-bundle-apply","outcome":"pass","revision":"fb67261a5fd8a69231e963226189fd98458e4d82","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-evidence.json","detail":"Exact committed source and MASK runtime install all four RFC skills for both adapters with reviewed implement-rfc setup, healthy status and repeat no-op in a disposable consumer."}},{"criterion":"companions-and-install-docs","outcome":"pass","revision":"fb67261a5fd8a69231e963226189fd98458e4d82","evidence":{"kind":"artifact","path":"docs/development/rfc-bundle-evidence.json","detail":"README names grill-rfc companions and implement-rfc plan kit; supported bundle fetch/show/preview/hash-apply/status and individual installation remain documented."}}]
---

# Publish the canonical RFC bundle in the source index

Owner mandate `named-bundles-v1`, 2026-10-02. Follow-up to the accepted authoring
skills, coordinated with MASK-0042 and MASK-0064. Own `mask-source.json`, README
and a focused index test. Preserve discovery of every existing canonical package.

Expose flat `agentskills/rfc` containing author-rfc, grill-rfc, grill-me and
implement-rfc through MASK's supported source-index schema. Explain grill-rfc's
companions and the supported reviewed bundle install command; individual install
remains available. Verify the actual canonical bundle in a disposable consumer,
including all four links and complete required workflow setup.

No source publication/push, real deployment, permission or credential change.
Record the actual upstream commit in the MASK handoff; do not copy tracker state.
