---
schema: "implement-rfc.card.v1"
id: "ASK-0111"
title: "Allow complete category removal without losing allocation history"
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: []
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"274757065d42e833d5c041d5f23393de2cb70d54","evidence":{"kind":"observation","detail":"Focused fixtures preserve current card/reservation counter requirements, single-file requirements and counter rewind refusal while accepting a fully removed category."}},{"criterion":"AC02","outcome":"pass","revision":"274757065d42e833d5c041d5f23393de2cb70d54","evidence":{"kind":"observation","detail":"Public allocate resumes another branch high water after committed counter removal, refuses exhausted IDs and starts genuinely new categories at one."}},{"criterion":"AC03","outcome":"pass","revision":"274757065d42e833d5c041d5f23393de2cb70d54","evidence":{"kind":"observation","detail":"7 retirement, 17 board-audit and 32 issue-board tests pass. MASK preview/apply changes only AITO implement-rfc development links to this canonical source. No push or publication."}}]
---

AITO's owner requested removal of the fresh retired category receipts and counter
while renaming Pinax UI. The shared allocator currently requires a counter even
when that category has no remaining cards or reservations.

RFC_BASE_SHA: `d859ff1f87d83488b860ff0032131c0a1101af8a`

- **AC01:** An absent counter is allowed only when no current card or reservation
  needs it. Existing counter rewind checks remain enforced.
- **AC02:** Allocating a removed per-area category resumes at the highest next ID
  observed in Git history, including other refs; no IDs are reused.
- **AC03:** Focused public-command fixtures cover removal, resume and rejection.
  Deploy only the selected AITO helper locally through MASK; no push/publication.
