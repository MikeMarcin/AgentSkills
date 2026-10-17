---
schema: "implement-rfc.card.v1"
id: "ASK-0111"
title: "Allow complete category removal without losing allocation history"
status: "Ready"
rfcs: ["RFC-ASK-0003"]
depends_on: []
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
