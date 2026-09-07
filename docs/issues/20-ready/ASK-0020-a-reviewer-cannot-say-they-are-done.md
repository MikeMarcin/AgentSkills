---
schema: "implement-rfc.card.v1"
id: "ASK-0020"
title: "A reviewer cannot say they are done, and the buttons do not say what they do"
status: "Ready"
rfcs: []
depends_on: []
priority: "P1"
---

# A reviewer cannot say they are done, and the buttons do not say what they do

A product owner finished answering one candidate and asked, in these
words: "there is no button to just say process the results of my
rejection and stop the review? Because that's what I want to do". There
is not. Their answer was already saved, but nothing on the page said so
in those terms, and nothing told the driver the reviewer had stopped.

They also could not tell which of the three controls at the top of the
page records an answer: "I don't know which of these buttons to press
for: I just want to deliver the answer I've decided and stop here."
Those three are Start with what's ready, Pause session and Skip for now,
none of which record anything, and they sit above the card whose Accept
and Reject do.

The same note asked for two smaller things: a candidate that wants a URL
pasted somewhere should offer it in a copy box, the way a launch command
already is, and a screenshot should be pasteable into the note box rather
than saved to a file and hunted for.

## Scope

- A control that ends the review: it records nothing new, marks the
  session handed back so the driver sees it, and tells the reviewer their
  answers are saved and the tab can be closed. Undecided candidates stay
  undecided.
- The controls say what they do and are grouped by what they act on: the
  answer to this candidate, and the session as a whole. The ones that
  record an answer are next to the note they belong with.
- A candidate may carry values to copy, each labelled, beside its launch
  command.
- An image pasted into the note box becomes an attachment, under the
  bounds an attached file already has.
- Owned paths: `skills/attended-review`.

## Acceptance

- A reviewer can answer one candidate, end the review, and be told what
  was recorded, without asking which button to press.
- The driver can see that a session was handed back and what was decided.
- A pasted image and a copied value are covered by tests.
