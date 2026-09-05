---
schema: "implement-rfc.card.v1"
id: "ASK-0013"
title: "One-off named consumer migrations"
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: ["ASK-0012"]
acceptance: [{"criterion":"RFC-ASK-0003-AC05","outcome":"pass","revision":"AgentSkills 05c15eb; MASK 18f09e3/421afe9; SampleLogs f9f8ab5; PLN 9c50c6a; SRV 683cb32c; sample_studio fa38f378c","evidence":{"kind":"observation","detail":"All six consumers deployed through guarded MASK previews and healthy doctor. Canonical live metadata: ASK14, MASK18, SampleLogs0, PLN192/16RFC, SRV611/27RFC, sample_studio4927/589RFC. Relevant documentation/scoped board and allocation preview checks passed. Historical PLN1/sample_studio6 Done-dependency contradictions preserved. Verified old skills retired outside discovery. Product changes excluded from commits; converters remain temporary pending final cleanup."}}]
---

# One-off named consumer migrations

Owned paths: SRV, SampleLogs, PLN, sample_studio workflow context/cards/skills/adapters; migration provenance.

Acceptance: RFC-ASK-0003-AC05; implement the approved design and record direct checks.
