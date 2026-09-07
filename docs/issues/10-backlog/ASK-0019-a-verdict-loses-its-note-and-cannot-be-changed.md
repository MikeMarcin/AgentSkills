---
schema: "implement-rfc.card.v1"
id: "ASK-0019"
title: "A verdict loses its note and cannot be changed"
status: "Backlog"
rfcs: []
depends_on: []
priority: "P1"
---

# A verdict loses its note and cannot be changed

A product owner reviewing a SampleReview session on 2026-09-07 could
not complete it, and said so: "I have no way to reset/clear an answer if I
accidentally did one", "It looks like it lost my response note when I
clicked reject on the first one", "There's no place to add images so I
have to use the fallback flow", and "The fallback flow didn't have the
decision I made in the json export. Literally unusable."

Four defects, and the last is the serious one: the record of a decision
they had made was not in the export they were told to hand back.

- A recorded verdict disabled Accept and Reject for good, and intake
  refused any different verdict for the same candidate. An accidental
  press was final.
- The note was saved with the verdict and then never shown again: the page
  cleared the box, moved to the next candidate, and the verdict line
  reported only the outcome. Nothing told the reviewer their words had
  been kept.
- There was no way to attach a picture, which is what a rejection of a
  user interface usually is. The reviewer went to the offline file looking
  for one.
- The offline file is a snapshot taken when it was written. Theirs was
  written before they decided anything, so its export was empty and said
  nothing about why.

## Scope

- A verdict is replaceable and can be withdrawn; every superseded verdict
  is kept beside the current one, so changing a mind hides nothing.
- The note is part of the verdict: it is saved, shown back in the verdict
  line, and returned to the box when the candidate is selected again.
- A verdict carries inline images, bounded in count and size, through the
  page, the export and the intake.
- The offline file states when it was written, so its silence about later
  decisions cannot be mistaken for a record.
- A candidate may name a command that opens what it asks the reviewer to
  look at, shown for copying and never run.
- Owned paths: `skills/attended-review`.

## Acceptance

- Each of the four is fixed and covered by a test that fails before the
  fix.
- A session driven end to end in a browser records a verdict with its note
  and an image, changes it, clears it, and exports what it recorded.
