---
schema: "implement-rfc.card.v1"
id: "ASK-0019"
title: "A verdict loses its note and cannot be changed"
status: "Done"
rfcs: []
depends_on: []
priority: "P1"
acceptance: [{"criterion":"Each of the four is fixed and covered by a test that fails before the fix","outcome":"pass","revision":"7ad3231","evidence":{"kind":"observation","detail":"The 18-test suite passes and covers all four: a verdict replaced with the previous one kept in superseded, a verdict with a note and an image withdrawn and given again, refusals for a non-image attachment and for five of them, and the offline file's generation stamp. Refusing a changed verdict, dropping attachments from the record, dropping the stamp and dropping the launch field each fail a named test. verify_documentation.py reports no structural violations."}},{"criterion":"A session driven end to end in a browser records a verdict with its note and an image, changes it, clears it, and exports what it recorded","outcome":"pass","revision":"7ad3231","evidence":{"kind":"observation","detail":"A throwaway session was served and driven in a browser: a note and a PNG were attached to a rejection, the verdict line read back 'Recorded: reject - \"...\" - 1 image(s)' with the note still in the box and the thumbnail shown, Accept became 'Accept instead' and changed the verdict, Clear removed it and said so, and the export carried the outcome, the note and the image. The generated offline file contained the live decision and its generated_at, and importing its export was accepted idempotently."}}]
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

## Notes (2026-09-07)

- **Changing a verdict.** `intake` refused any verdict that differed from
  the one already recorded, and the page disabled both buttons the moment
  one existed. A verdict is now replaceable: the one the reviewer lands on
  is the record, the one it replaced is appended to the candidate's
  `superseded` list, and an identical repeat is still idempotent. A verdict
  can also be withdrawn (`outcome: "withdrawn"`), which clears the decision
  and keeps what was said. The page offers "Accept instead", "Reject
  instead" and "Clear decision".
- **The note.** It was always saved and never shown. The verdict line now
  reads it back in quotation marks, the box is refilled from the recorded
  verdict when a candidate is selected, and the page stays on the candidate
  that was just answered instead of jumping to the next one, so the
  reviewer sees what was kept.
- **Images.** A verdict carries up to four inline images, each bounded, and
  the page attaches them from an ordinary file input, shows them as
  thumbnails, and includes them in the export. The intake validates the
  count, the shape and the data URL, and the request bound was raised to
  hold one verdict with its pictures.
- **The offline file.** It is a snapshot; it now records `generated_at` and
  says so on the page, so a file written before a decision cannot be
  mistaken for a record of it. Its export carries attachments as well as
  notes.
- **Opening what is under review.** A candidate may carry
  `launch: {label, command}`, shown in a copyable field and never run. The
  packet that started this asked its reviewer to navigate a file tree by
  hand.
- **Evidence.** The suite is 18 tests, including a verdict replaced with
  its previous kept, a verdict with a note and an image withdrawn and given
  again, refusals for a non-image attachment and for five of them, and the
  offline file's stamp and launch command. `verify_documentation.py`
  reports 4 RFCs, 19 cards and no structural violations. The page itself
  was driven in a browser against a throwaway session: a note and an image
  were recorded on a rejection, the verdict line read them back, the
  decision was changed to accept and then cleared, and the export carried
  the outcome, the note and the image.
- **Negative mutations.** Refusing a changed verdict, dropping attachments
  from the record, dropping the generation stamp and dropping the launch
  field each fail a named test.
