---
id: "RFC-ASK-0019"
title: "Checked question format and authoring rules for attended-review"
status: "Auto-Verified"
metadata: {"milestone_plan":{"id":"attended-review-question-quality","path":"docs/rfcs/plans/attended-review-question-quality/milestone-plan.json"}}
---

# Checked question format and authoring rules for attended-review

Imported from [RFC-DRAFT-0003](drafts/RFC-DRAFT-0003-attended-review-question-quality.md)
([live import record](plans/attended-review-question-quality/attended-review-question-quality.LIVE_IMPORT.md)).
Cards: [ASK-0134](../issues/60-done/ASK-0134-checked-question-format.md), closeout
[ASK-0135](../issues/60-done/ASK-0135-close-question-quality-rfc.md). Grouping:
[adopted plan](plans/attended-review-question-quality/milestone-plan.json).

Mandate (owner, 2026-11-15): "Implement the RFC at
docs/rfcs/drafts/RFC-DRAFT-0003-attended-review-question-quality.md." This directive
records acceptance of this RFC as written, including its two owner decisions.

## Problem and grounded current behavior

The owner reported that attended-review questions are too long and inconsistent:
mockups with and without a way to open them, features with no screenshot, paths
buried in paragraphs instead of behind a copy button, and frozen builds that open
somewhere other than the thing under review. This is a source proposal for the
portable skill. It does not migrate a consumer or deploy an updated skill.

The skill specifies the session protocol in detail and the question almost not at
all:

- [SKILL.md](../../skills/attended-review/SKILL.md) step 2 carries the only
  authoring guidance: "Include concise review material or inline media; prefer a
  prepared stable build." The [session contract](../../skills/attended-review/references/session-contract.md)
  covers state, intake, protection and publication.
- The [helper](../../skills/attended-review/scripts/attended_review.py) validates
  field types only. `content` is any text of any length, and a candidate with a
  `launch` command and no preparation command becomes ready as "Static review
  material prepared" without the command ever having run.
- The [page](../../skills/attended-review/assets/review.html) prints the
  candidate ID and full `revision` above the title, the criteria, then `content` as
  one plain-text block. It has no steps, links or image roles. `copy` renders a copy
  button, but nothing requires its use.

Stored sessions for two consumers were read on 2026-11-15: 915 questions in about
240 BetterPullReview sessions and 421 questions in 26 aito sessions, with all 362
reviewer notes. They are an authoring reference, not committed evidence.

| Observation | BetterPullReview | aito |
|---|---|---|
| Median words to read per question | 188 | 171 |
| Launch command with no image | 375 (40%) | 14 (3%) |
| Absolute path in prose with no copy button | 110 | 4 |
| Tracker IDs in the question text | 583 (63%) | 201 (47%) |
| Hex digests in the "What to check" bullets | rare | 83 |
| Most options on one question | 6 | 16 |

Further observations:

- **Drift.** BetterPullReview questions with a launch and no image fell from 70% in
  early September to 9% in late October, then rose to 49% in November. Quality
  followed whichever driver and repository note was current.
- **Unverified launches.** Reviewer notes record three `FIXTURES_MISSING` failures,
  one `STARTUP_FAILED`, a build that "closes instantly", and fixtures that could not
  show the behaviour ("I'm not able to leave a comment on this review fixture so I
  cannot tell if this is working").
- **Tracker language.** Fourteen notes say some form of "I have no idea what I'm
  looking at here"; two say "Show me in screenshots."
- **Built versus approved.** Several rejections are "that looks almost nothing like
  the mockups": the approved design was not shown beside the build.
- **Boilerplate.** In BetterPullReview, 281 questions explain how Accept and Reject
  work, 190 open with a commit subject line required by that repository's
  instructions, 166 repeat a "nothing reaches GitHub" disclaimer and 25 say "same
  build as the other question".
- **Identity in the reading path.** 91 aito questions carry a `revision` over 200
  characters, which the page prints first; its art-set questions run a median of
  427 words, mostly digests and file facts.
- **Cost.** BetterPullReview questions with a launch and an image were left
  unanswered 7% of the time and rejected 22%; with a launch alone, 18% and 32%.
  Forty topics took three or more rounds. This is correlation, consistent with the
  notes.

Source basis: AgentSkills `bfdcf5b1ae99f87991e6b4899f9165fe2e3e03d8`.

## Proposed behavior and boundaries

### A question has named parts

A new manifest version gives a question explicit parts, which the page renders in
this fixed order. Exact field names are implementation choices.

1. **Title**: the decision, in the reviewer's words.
2. **Why**: one sentence saying why the reviewer is being asked.
3. **What to check**: short observable statements.
4. **Reference**: images of what was approved or intended, when the question
   judges something against an earlier design.
5. **Now**: images of what the reviewer should see, shown beside the reference.
6. **Open it**: the launch command with its copy button.
7. **Try**: numbered steps. A step that needs a value pasted carries that value
   with its own copy button.
8. **Links**: labelled `http` or `https` links, opened in a new tab. A local file
   is opened by a launch command, never linked.
9. **Not in this round**: known gaps the reviewer should not judge.
10. **Note**: optional free text for what fits nowhere else.
11. **Provenance**, collapsed: candidate ID, revision, fingerprint, metadata, paths
    and resources. The revision no longer appears above the title.

All text stays plain text; the page still evaluates no Markdown or HTML. Every part
that affects the judgment binds the candidate fingerprint, as review material does
today.

Material under review is distinct from text about the task. A document the reviewer
is asked to read, an audio clip or an image is material and has no word budget.
Everything the driver writes to explain the task is budgeted.

### Question kinds and their required parts

Every question in the new version declares a kind. Each kind requires the parts
that make it answerable.

| Kind | The reviewer | Required |
|---|---|---|
| Build | tries a running candidate | Launch, a recorded launch check, at least one Now image |
| Design | judges mockups, renders or art | At least one image; a way to open any openable artifact; one labelled image per option |
| Decision | chooses between stated alternatives or reads a document | The alternatives as options, or the document as material |
| Audio | listens to one clip | Unchanged from the existing audio question |

A build question becomes ready only after a launch check is recorded: a preparation
command that exits 0, or the driver's `ready --evidence`. Static publication no
longer makes it ready. The check establishes that the command starts, stays open
until the reviewer closes it, lands on the surface under review, and that its
fixture holds the state the steps need. The Now image is captured from that
candidate. The helper still never runs a launch command and gains no capture
ability; consumers supply the check, as they supply preparation today.

A build question also states its reference: the approved design's images, or that
no earlier design exists.

### Budgets and other checks

These defaults apply to driver-written text:

| Part | Limit |
|---|---|
| Title | 12 words |
| Why | 25 words |
| What to check | 3 statements, 20 words each |
| Try | 5 steps, 20 words each |
| Not in this round | 3 items, 15 words each |
| Note | 60 words |
| Options | 6, 15 words each |
| Image label | 12 words |
| Waiver reason | 25 words |

The helper also refuses:

- an absolute path or URL in any text part, which belongs in a step's copy value,
  a launch command or a link;
- a hex string of 12 or more characters in the title, Why, What to check, steps or
  options, which belongs in provenance;
- a tracker ID in the title, Why or What to check;
- a question whose kind is missing a required part.

Several independent choices are separate questions. The existing rule already says
so; the option limit enforces it, and the page needs no grouped-choice control.

### Refusal, waivers and reporting

`init` refuses a manifest that breaks a rule, saving nothing from it. The error
names every violation at once, each with a stable rule ID and how to satisfy it. A
read-only check command reports the same result without touching a session.

A rule is waived per question with a written reason. The page shows the reason to
the reviewer on that question, for example "No screenshot: the change is a
keyboard shortcut." Waivers bind the fingerprint and are counted in `init` output.
An empty reason is refused.

### Shared setup

A manifest can state setup once for the questions that share it: the launch
command and one note of at most 40 words. The page shows the note once on entering
that group and keeps the launch command on each question. Questions no longer
restate the build, disclaimers or "same as the other question".

How Accept, Reject and notes work is the page's job. Question text does not explain
it.

### Authoring guide

Add one short reference, loaded when writing a manifest, and point SKILL.md step 2
at it. It holds:

- a template per kind;
- the rule that the reviewer is never told what they are about to see;
- the rule that steps exercise the surface and never navigate to it, unless
  navigation is what is under review;
- a driver self-check to run before sharing: open the page, read each question as
  the reviewer, and confirm the launch check and images match the candidate;
- one before-and-after example.

The portable example gains one passing question of each kind and one manifest that
fails the checks.

### Compatibility and scope

Version 1 and 2 manifests, sessions, fingerprints, verdicts and imports keep their
current behavior. Decision intake, feedback, protection, waiting, transport and hub
publication are unchanged. The live and offline pages render the new parts the
same way. The runtime stays standard-library only.

Implementation owns `skills/attended-review/`: instructions, the new reference,
contract, helper, page, focused tests and the example. This amends the
attended-session behavior accepted by [RFC-ASK-0003](RFC-ASK-0003-unified-rfc-workflow.md)
and extended by [RFC-ASK-0016](RFC-ASK-0016-attended-review-audio-questions.md).
Their recorded acceptance is unchanged.

Consumer changes are outside this proposal and are listed only so they are not
lost:

- BetterPullReview: move the frozen commit line from question content to metadata;
  give its freeze tool a way to open on a named surface.
- aito: have its art-review producer emit digests and file facts as provenance.

### Owner decisions

**Owner decision — refuse or report (2026-11-15):** the owner selected "Refuse
with waivers" over reporting violations and proceeding. `init` refuses a
new-version manifest that breaks a rule, as written under Refusal, waivers and
reporting. This answer settles enforcement. The numeric limits were offered for
comment with it and drew no change; they stand as defaults and are not recorded
as separately confirmed.

**Owner decision — earlier manifest versions (2026-11-15):** the owner selected
"Accept, report only" over refusing them for new questions. `init` keeps
accepting version 1 and 2 manifests, runs the checks without refusing, and labels
the result as unchecked legacy format in its output. Existing producers, including
aito's generated manifests, keep working until they are updated.

No material design questions remain open in this draft. These two answers settle
enforcement and legacy handling; they do not record blanket confirmation of the
whole proposal.

## Acceptance

- **AC01:** A new-version manifest with one question of each kind renders its
  parts in the defined order on the live and offline pages, with the revision and
  other identity only under provenance.
- **AC02:** A step's value and the launch command each copy with one action, and a
  reference image appears beside the current image with each labelled by role.
- **AC03:** A build question with no recorded launch check stays waiting after
  static preparation and becomes ready after a passing check or driver evidence.
- **AC04:** A manifest breaking several rules is refused with every violation
  named, and saves nothing; the read-only check reports the same violations.
- **AC05:** A waived rule admits the question, and its reason is visible to the
  reviewer on that question and bound to its fingerprint.
- **AC06:** Shared setup stated once appears once per group while each question
  keeps a working launch copy.
- **AC07:** Version 1 and 2 manifests, existing sessions and their fingerprints,
  verdicts and imports behave as before; `init` admits a version 1 or 2
  manifest that breaks the rules and reports its violations as unchecked legacy
  format.
- **AC08:** The latest reviewed BetterPullReview question, rewritten in the new
  format as the guide's example, passes the checks at no more than 80
  driver-written words.
- **AC09:** SKILL.md, the authoring reference, the contract and the example
  describe the same parts, kinds, limits and rule IDs, and focused source checks
  cover the changed behavior without claiming a consumer migration.

## Implementation record

Implemented in `skills/attended-review` at `670238c425c0e2fcaa4475df9a1368c0eaac0f14`; the
[verification checklist](plans/attended-review-question-quality/verification.md)
records each criterion. The helper's contract is the
[Question format](../../skills/attended-review/references/session-contract.md#question-format-manifest-version-3)
section; drivers read [Writing review questions](../../skills/attended-review/references/question-authoring.md).

Implementation choices within this RFC: manifest `schema_version: 3`; fields `kind`,
`why`, `criteria` (What to check), `reference` (images or `"none"`), `now`, `launch`,
`steps` (`{text, value?}`), `links`, `not_in_round`, `note`, `document` (material),
`options`, `waivers` (`{RULE_ID: reason}`) and `setup` naming a top-level `setups`
entry. `content`, `copy` and `question_type` are refused in version 3. A version-3
session's state becomes `schema_version: 3` so an older helper cannot publish a build
question without its launch check; decision intake stays version 2. Rule IDs and
limits are those in the contract. Waivers apply to every rule except
`kind-required`, `setup-note-words` and `waiver-reason-words`. Opening an openable
design artifact and capturing the Now image from the candidate are driver
self-checks; the helper cannot detect them.

