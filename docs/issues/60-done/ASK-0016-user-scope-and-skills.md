---
schema: "implement-rfc.card.v1"
id: "ASK-0016"
title: "Migrate approved personal and project installations"
status: "Done"
rfcs: ["RFC-ASK-0004"]
depends_on: ["ASK-0015"]
acceptance: [{"criterion":"Guarded live migration and consumer handoffs","outcome":"pass","revision":"3232119a0fe7f5e3effdac28b7f17eafc5f29049","evidence":{"kind":"observation","detail":"Five personal skills on both targets, two sample_studio skills on both targets and one AST Codex skill deployed with public CLI guards; all selected doctor checks and convergence passed. 16 originals retained with fingerprints and restoration instructions. Consumer commits 970834ef0 (sample_studio) and 40b77fd (AST); SAMPLE_STUDIO focused validation and AST 15-strip/Swift/CMake wrapper passed. Existing sample_studio humanizer edit preserved."}}]
---

# ASK-0016: Migrate approved personal and project installations

Owned scope: selected skill packages, management guidance, migration records and explicit consumer handoffs.

Acceptance: direct passing checks for the bounded slice and explicit source changes; record actual evidence before finish.
