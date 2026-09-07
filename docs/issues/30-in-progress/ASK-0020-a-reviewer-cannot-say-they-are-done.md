---
schema: "implement-rfc.card.v1"
id: "ASK-0020"
title: "A reviewer cannot say they are done, and the buttons do not say what they do"
status: "In Progress"
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

## Notes (2026-09-07)

- **Finishing.** "Finish and hand back" records nothing and decides
  nothing. It stamps `handed_back` on the session, writes a `handed-back`
  event naming what was decided and what was left, and tells the reviewer
  what was recorded in the same sentence: "1 answered: <title> — reject. 1
  left unanswered. Your answers are saved; you can close this tab." Once
  handed back the verdict controls are disabled and the header says so.
  Offline it opens the export instead, with the same summary, because
  there is no driver to tell. `hand-back` is also a CLI command, so a
  driver can see it in `status`.
- **Which button.** The controls are in two labelled groups now. "This
  session:" holds Finish and hand back, Pause and come back later, and
  Start with what's ready. "This candidate:" sits inside the card under a
  "Your answer" heading with the note box, and holds Accept, Reject, Clear
  my answer and Answer later. Skip for now moved into that group and says
  what it does. The owner could not tell which of the three top controls
  recorded an answer; none of them did.
- **Pasting a screenshot.** An image on the clipboard, pasted into the note
  box, becomes an attachment under the same bounds a chosen file has. The
  label says so. Choosing files still works and both paths share one
  routine.
- **Copying what the candidate asks for.** A candidate may carry `copy`,
  labelled values shown beside the launch command with their own Copy
  buttons, for the pull request link a packet asks to be pasted somewhere
  else. Like the command, it binds the fingerprint and is never executed.
- **A bug of my own.** The `copy` validator's loop variable shadowed the
  manifest parameter it was validating, so `manifest()` returned the last
  copied value and every init failed with `KeyError: candidates`. Caught by
  the new test on its first run; renamed.
- **Evidence.** Twenty tests pass. Handing back is pinned to decide nothing
  and to report both lists; a candidate's copied values reach the offline
  file and a value without a label is refused. Three mutations, a hand-back
  that decides, a manifest that drops `copy`, and a status that omits
  `handed_back`, each fail a named test. The page was driven in a browser:
  an image pasted into the note attached itself, Reject recorded it with
  the note read back, and Finish and hand back reported "1 answered … 1
  left unanswered" and disabled the answer controls, with the driver's
  `status` showing `handed_back` and the untouched candidate still open.
