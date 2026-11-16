# Writing review questions (manifest version 3)

Load this when writing a manifest. The [session contract](session-contract.md#question-format-manifest-version-3)
defines the same fields, kinds, limits and rule IDs for the helper. Run
`check --manifest FILE` while writing; `init` refuses what `check` reports.

A question asks a person to make one decision. They read it on a page beside the
thing under review, often on another screen. Every word you write is a word they
read before they can look. Material under review (a document to read, a clip, an
image) has no word budget; the text you write about the task does.

## Parts, in the order the page shows them

| Part | Field | Limit |
|---|---|---|
| Title: the decision, in the reviewer's words | `title` | 12 words |
| Why: one sentence saying why they are asked | `why` | 25 words |
| What to check: short observable statements | `criteria` | 3 statements, 20 words each |
| Reference: what was approved or intended | `reference` | images; each label 12 words |
| Now: what the reviewer should see | `now` | images; each label 12 words |
| Open it: the launch command, copied in one action | `launch` | (copy value) |
| Try: numbered steps; a pasted value has its own copy button | `steps` | 5 steps, 20 words each |
| Links: labelled `http`/`https` pages, opened in a new tab | `links` | |
| Not in this round: known gaps not to judge | `not_in_round` | 3 items, 15 words each |
| Note: what fits nowhere else | `note` | 60 words |
| Options, when choosing between alternatives | `options` | 6, 15 words each |
| Provenance, collapsed: ID, revision, fingerprint, metadata, paths, resources | `revision`, `metadata`, `paths`, `resources` | |

`document` holds text the reviewer is asked to read, and `media` holds other
material such as video or a waveform; neither is budgeted. Waiver reasons are at
most 25 words and a shared setup note at most 40. All text is plain text.

## Kinds

Every question declares `kind`. Each kind requires what makes it answerable.

| Kind | The reviewer | Required (rule ID) |
|---|---|---|
| `build` | tries a running candidate | `launch` (`build-launch`); a Now image (`build-now-image`); a reference, images or `"none"` (`build-reference`); a recorded launch check before it is ready |
| `design` | judges mockups, renders or art | an image (`design-image`); one labelled image per option, by its `option` (`design-option-image`); a way to open any openable artifact |
| `decision` | chooses between alternatives or reads a document | two or more `options`, or a `document` (`decision-material`) |
| `audio` | listens to one clip | the existing [audio question](session-contract.md#audio-questions-manifest-version-2) |

A build question is ready only after a launch check: a `prepare` command that exits
0, or your `ready ID --evidence TEXT` after checking yourself. The check shows the
command starts, stays open until the reviewer closes it, lands on the surface under
review, and that its fixture holds the state the steps need. Capture the Now image
from that candidate. The helper never runs the launch command and cannot capture.

## Rules

| Rule ID | Refuses | Satisfy it by |
|---|---|---|
| `title-words` | a title over 12 words | stating the decision in the reviewer's words |
| `why-words` | Why over 25 words | one sentence |
| `check-count` | more than 3 What to check statements | asking a separate question for others |
| `check-words` | a statement over 20 words | one short observable statement |
| `step-count` | more than 5 steps | exercising the surface, not the way to it |
| `step-words` | a step over 20 words | moving a pasted value into the step's `value` |
| `not-in-round-count` | more than 3 gaps | naming only gaps the reviewer would judge |
| `not-in-round-words` | a gap over 15 words | naming the gap, not its history |
| `note-words` | a note over 60 words | moving material, setup and page instructions out |
| `option-count` | more than 6 options | separate questions for independent choices |
| `option-words` | an option over 15 words | naming it and showing it in an image |
| `image-label-words` | an image label over 12 words | saying what the image shows |
| `setup-note-words` | a shared setup note over 40 words (not waivable) | saying only what the group shares |
| `waiver-reason-words` | a waiver reason over 25 words (not waivable) | one sentence for the reviewer |
| `no-path-or-url` | an absolute path or URL in any text you write | a step value, the launch command or a link |
| `no-long-hex` | a hex string of 12+ characters in the title, Why, What to check, steps or options | metadata; provenance shows it |
| `no-tracker-id` | a tracker ID such as `ABC-123` in the title, Why or What to check | describing the behavior; IDs go in metadata |
| `kind-required` | a question without a kind (not waivable) | `build`, `design`, `decision` or `audio` |
| `build-launch` | a build question without a launch | `launch`, or a shared setup with one |
| `build-now-image` | a build question without a Now image | a capture from the candidate |
| `build-reference` | a build question without a stated reference | the approved images, or `"reference": "none"` |
| `design-image` | a design question without an image | the mockup, render or art |
| `design-option-image` | a design option without its image | a Now image whose `option` names it |
| `decision-material` | a decision without alternatives or a document | two or more options, or the `document` |

Standards spelled like tracker IDs (SHA-256, ISO-8601, UTF-8) are not tracker IDs.
Versions 1 and 2 are admitted and the same checks are reported as
`unchecked legacy format`.

### Waivers

Waive a rule for one question in `waivers`, with a reason the reviewer reads on that question:

```json
"waivers": {"build-now-image": "No screenshot: the change is a keyboard shortcut."}
```

The reason binds the question's fingerprint and `init` counts waivers. An empty
reason or an unknown rule is refused.

### Shared setup

State setup shared by several questions once, in the manifest's top-level
`setups`, and name it in each question's `setup`. The page shows the note once on entering the group;
each question keeps the launch command.

```json
"setups": {"frozen-build": {"launch": {"command": "python3 /path/to/launch.py"}, "note": "One frozen build; nothing reaches GitHub."}}
```

## How to write them

- Never tell the reviewer what they are about to see. Show it (Now), and say what
  to judge (What to check).
- Steps exercise the surface under review. They never navigate to it unless
  navigation is what is under review: make the launch land there.
- The page explains Accept, Reject and notes. Do not.
- Put revisions, digests, tracker IDs, commit subjects and file facts in
  `metadata`, which provenance shows collapsed.
- Several independent choices are several questions.

## Templates

```json
{"id": "ID", "kind": "build", "title": "…?", "revision": "REV", "why": "…", "criteria": ["…"],
 "reference": [{"url": "data:image/png;base64,…", "label": "…"}], "now": [{"url": "data:image/png;base64,…", "label": "…"}],
 "launch": {"command": "…"}, "steps": [{"text": "…", "value": "…"}], "not_in_round": ["…"]}
{"id": "ID", "kind": "design", "title": "…?", "revision": "REV", "criteria": ["…"], "options": ["A", "B"],
 "now": [{"url": "data:image/png;base64,…", "label": "…", "option": "A"}, {"url": "data:image/png;base64,…", "label": "…", "option": "B"}]}
{"id": "ID", "kind": "decision", "title": "…?", "revision": "REV", "criteria": ["…"], "document": "TEXT TO READ"}
{"id": "ID", "kind": "audio", "title": "…?", "revision": "REV", "criteria": ["…"],
 "audio": {"url": "data:audio/wav;base64,…", "purpose": "…", "scope": "…"}, "media": [{"kind": "image", "url": "data:image/svg+xml;base64,…", "label": "Waveform"}]}
```

## Before you share the session

1. Run `check`, then `init` and `prepare`. Record each build's launch check.
2. Open the page. Read each question as the reviewer, top to bottom, without
   opening anything else.
3. Confirm each launch opens this candidate on the surface under review, the Now
   images come from it, and each step's value pastes where the step says.

## Before and after

The latest reviewed BetterPullReview question before this format (paths made
representative): 416 driver-written words, a launch with no image, rejected. Its content, abbreviated:

> Frozen from 18a70bb96087 "BPR-2200: on Windows every Qt test of tests/adapters_qt
> runs offscreen with the Windows fonts (…)" (2026-11-15T18:24:55-08:00), HEAD of
> claude/v0-5-0-prerelease-targets-52265d at freeze. It contains the import preview
> as built at 8af4a4501 (BPR-2032). You chose B, List and detail, in
> workflow-import-v001. This is that design built with the app's own widgets. Launch
> the build with the command below. It opens a local draft with an earlier revision
> of the Synthetic Org workflow already imported into the build's own profile.
> Nothing reaches GitHub, agents are the Fixture agent, and nothing runs. What to
> try: open Settings › Agents, choose Import configuration…, and pick this file:
> /Users/reviewer/workflow-import-v002/look/synthetic-org.bpr-config.json. The
> preview opens with everything chosen and Import enabled. On the left is a ticked
> list in sections, each item tagged New, Updated or Unchanged (…). Each choice is
> one click (…). Cancel when you are done. The Profiles page and the Import/Export
> Profile Settings move (BPR-2198) are not in this build. (…) Accept keeps the
> preview. Reject, with a note saying what to change.

After, 75 words, passing `check`. The two images are placeholders here; a real
manifest embeds the approved option B and a capture from the frozen build. Its
build cannot yet open on the import dialog, so one step still navigates there.

```json
{"schema_version": 3, "candidates": [{
  "id": "import-preview-b", "kind": "build", "revision": "workflow-import-v002",
  "title": "Is the import preview option B as approved?",
  "why": "You chose B; this is it built with the app's widgets.",
  "criteria": ["Opens with everything chosen and Import enabled.",
               "Updates show yours beside the file's, changes marked.",
               "The unknown action is named and refused."],
  "reference": [{"url": "data:image/png;base64,…", "label": "Option B as approved"}],
  "now": [{"url": "data:image/png;base64,…", "label": "Built preview with the sample file"}],
  "launch": {"command": "python3 /Users/reviewer/workflow-import-v002/launch.py"},
  "steps": [{"text": "In Settings, Agents, choose Import configuration… and paste this file.",
             "value": "/Users/reviewer/workflow-import-v002/look/synthetic-org.bpr-config.json"},
            {"text": "Try one choice per item, then Cancel."}],
  "not_in_round": ["The Profiles page and the settings move."],
  "metadata": {"rfc": "RFC-BPR-0112", "card": "BPR-2032", "frozen": "18a70bb96087", "built": "8af4a4501"}}]}
```
