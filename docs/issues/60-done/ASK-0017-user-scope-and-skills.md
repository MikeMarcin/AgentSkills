---
schema: "implement-rfc.card.v1"
id: "ASK-0017"
title: "Close out selected skill consolidation"
status: "Done"
rfcs: ["RFC-ASK-0004"]
depends_on: ["ASK-0016"]
closeout_for: ["RFC-ASK-0004"]
acceptance: [{"criterion":"RFC-ASK-0004-AC01","outcome":"pass","revision":"b22549b91024a396b773ee6d61e2db9f79b39402","evidence":{"kind":"observation","detail":"Seven MASK package validations and skill-shape checks; 17 installed-path offline tests via scripts/verify_selected_skill_imports.py"}},{"criterion":"RFC-ASK-0004-AC02","outcome":"pass","revision":"3232119a0fe7f5e3effdac28b7f17eafc5f29049","evidence":{"kind":"observation","detail":"Guarded public CLI deployments and doctor checks; 16 fingerprinted originals retained with RESTORE.md; consumer commits sample_studio 970834ef0 and AST 40b77fd"}},{"criterion":"RFC-ASK-0004-AC03","outcome":"pass","revision":"b22549b91024a396b773ee6d61e2db9f79b39402","evidence":{"kind":"observation","detail":"17 imported-package tests; AST 15 SampleCharacter strips, Swift tests and CMake build exit 0; sample_studio six agent-doc checks; unchanged humanizer fingerprint"}}]
---

# ASK-0017: Close out selected skill consolidation

Owned scope: selected skill packages, management guidance, migration records and explicit consumer handoffs.

RFC_BASE_SHA: 9e4d136c6280a8a47dfc330b4ff199fffec7bf61

Planned cards: ASK-0015, ASK-0016, ASK-0017

| Criterion | Check / evidence | Outcome | Revision |
|---|---|---|---|
| RFC-ASK-0004-AC01 | Seven MASK package validations and skill-shape checks; 17 installed-path offline tests via scripts/verify_selected_skill_imports.py | Pass | `b22549b91024a396b773ee6d61e2db9f79b39402` |
| RFC-ASK-0004-AC02 | Guarded public CLI deployments and doctor checks; 16 fingerprinted originals retained with RESTORE.md; consumer commits sample_studio 970834ef0 and AST 40b77fd | Pass | `3232119a0fe7f5e3effdac28b7f17eafc5f29049` |
| RFC-ASK-0004-AC03 | 17 imported-package tests; AST 15 SampleCharacter strips, Swift tests and CMake build exit 0; sample_studio six agent-doc checks; unchanged humanizer fingerprint | Pass | `b22549b91024a396b773ee6d61e2db9f79b39402` |

Closeout review runtime: primary agent, local diff and contract review; no delegated review. Native macOS filesystem/command evidence only. Native Windows user scope and loading by running agent UIs were not exercised. Temporary fixture roots were automatically removed; the named migration backups are intentionally retained. No push or publication.
