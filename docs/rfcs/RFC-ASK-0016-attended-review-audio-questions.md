---
id: "RFC-ASK-0016"
title: "Audio questions and durable feedback in attended-review"
status: "Implementing"
---

# Audio questions and durable feedback in attended-review

## Problem and grounded current behavior

The owner requested folding the Faraday Headshot audio audition into AgentSkills'
attended-review, improving it and making it a question type with the normal feedback
and session behavior. This is a source proposal, not authorization to migrate Faraday's
active review or deploy an updated skill.

The two implementations already supply complementary behavior:

- [attended-review](../../skills/attended-review/SKILL.md) provides a mixed queue,
  preparation and candidate protection, immediate durable verdicts, partial handback,
  event-based driver waiting and offline HTML/import. Its [manifest and intake
  implementation](../../skills/attended-review/scripts/attended_review.py) already
  accepts inline audio and verdict notes/image attachments. Its [page](../../skills/attended-review/assets/review.html)
  renders generic media players. Feedback is captured when a verdict is submitted;
  typing a note and selecting another question discards the unsubmitted text. The
  renderer also rebuilds media elements on redraw, interrupting playback.
- The [Faraday audition](http://127.0.0.1:63179/) presents six exact clips, grouped as
  three launcher and three death alternatives. It explains purpose, when the sound
  plays, listening criteria and rejection cues; supplies waveform/spectrogram images;
  and separates creative fit in isolation from rights and in-game approval. Its
  browser-local choices and notes require a complete batch before copying a verdict
  into the chat. It is a separate static review surface, with no attended-review
  intake or handback. The owner rejected Death C for death while suggesting it for
  non-death pain: feedback needs to preserve that distinction.

Source basis: AgentSkills `3d138cdad3fae7bc50d9f857c4feb0dbb3d86aa8`;
Faraday/Kiln `code/kiln_asset_pipeline/tools/audio_source/audio_review.py` at
`ee824787b66e79bb7624746d12fa142a78a82ab3`, inspected in
`/Users/jaeger/.codex/worktrees/b4e7/aito`. The live batch is
`faraday-headshot:/audio-review/9b6d640539f51c0d5f75b17b`. These are authoring
references, not implementation baselines or new acceptance evidence. The transient
localhost page is an example, not a dependency of the portable skill.

## Proposed behavior and boundaries

### An audio question in the existing queue

Add an explicit audio question type within the existing candidate model. A question
is the item the reviewer answers; its prepared candidate supplies the material and
identity. Audio questions and existing ordinary review/selection questions coexist
in one session, use the same preparation/protection and intake, and share navigation,
feedback, pause, answer revision/withdrawal, partial export and handback. A second
audio controller, verdict store or driver workflow is unnecessary.

An audio question identifies the exact clip and intended purpose under review. Its
presentation brings together:

- A useful title and variant label, such as "Launcher B — Plasma blast".
- The question, review scope and listening criteria, using the existing criteria
  and content where possible. Purpose, playback context, "listen for" and "reject
  if" material are supported without requiring game-specific fields.
- The playable clip beside the answer and feedback controls.
- Optional producer-supplied waveform/spectrogram images, contextual references and
  concise technical observations. Detailed provenance belongs in a disclosure;
  a technical pass or agent recommendation never selects a human answer.

The type and all material affecting the judgment participate in candidate identity,
including clip bytes, purpose, scope and listening context. Unchanged legacy
candidates keep their fingerprints; unrelated HEAD movement and queue reordering
remain irrelevant. A changed clip or intended use follows the existing release,
new revision and re-preparation process, retaining prior feedback and verdict history.

**Owner decision — answer unit for alternatives (2026-10-19):** the owner selected
"Per-clip answers, with easy A/B comparison (recommended)". Each exact clip gets its
own accept/reject answer and feedback, allowing several acceptable clips or none.
Comparison groups affect navigation only; unanswered siblings remain pending.
There is no implicit "reject the rest" action. This answer settles the alternative
answer format; it does not record blanket confirmation of the whole proposal.

### Listening and comparison

Provide play/pause, seek, replay from the beginning and an explicit loop toggle.
Playback starts only from reviewer action, and at most one review clip plays at a
time. Navigating away or handing back stops playback. Background status refreshes,
feedback saves and changes to another question's preparation must preserve the
active player's position, playback state and the reviewer's current edit/focus.

Related alternatives can be auditioned without scrolling through repeated diagnostic
material. Switching clips starts the selected clip from its beginning and clearly
identifies it. Returning to a clip restores its own feedback and verdict. This is sequential
comparison; synchronized playback, gain matching, normalization, mixing and blind
auditions are outside this proposal. The reviewed audio is not transformed.

Loading or decode failures are shown next to the affected player and remain visible
to the driver. A failure must not look like successful playback. It leaves the
question unanswered unless the reviewer explicitly supplies a verdict; playback
telemetry and diagnostic images cannot establish that the human listened or approved.

### Shared feedback that survives before an answer

Use one feedback system for every question type. Text and the existing bounded image
attachments can be saved while the question is unanswered; no forced accept/reject
is needed to retain a comment. Switching questions, answering later, pausing, reloading
or restarting the live host preserves saved feedback for that candidate fingerprint.

Live feedback saves to session state and reports saving, saved or failed status.
Navigation and handback flush outstanding edits; failed saves retain a recoverable
local draft and expose retry/export rather than claiming durability. Offline feedback
uses the same browser-storage warning and partial export/import model as decisions.
The reviewer can export feedback for an unanswered question. An unsaved edit is
never silently replaced by a status refresh or an older server copy.

Feedback alone is not a verdict and does not increase the answered count. Submitting
an answer includes the current feedback. Editing feedback on an answered question
preserves its explicit outcome and retains prior submitted content in history;
clearing the answer returns it to pending without discarding its feedback. Clearing
feedback is an explicit action. A reviewer may insert the current playback time into
the ordinary text feedback to locate a problem; untimed comments work equally well.

The Death C case must remain expressible as "reject for death; consider for pain".
The comment does not approve another use, reclassify the asset, generate a new task
or authorize integration. The driver interprets follow-up work under the user's
actual mandate.

### One durable intake and partial handback

Expose saved feedback alongside verdicts through the existing status/events and
offline transfer paths. Import validates session, candidate identity and prepared
state for the whole supplied partial set before saving any of it. Retries are
idempotent; stale material cannot acquire a current verdict or comment. A normal
handback-only driver wait continues to wait for handback, not every keystroke or
playback action. The handback reports answered and unanswered questions, including
unanswered questions that have feedback.

Keep the current session and protection semantics in the [session contract](../../skills/attended-review/references/session-contract.md)
and the qualified-host/manual-resume behavior in [Driver waiting](../../skills/attended-review/references/driver-wait.md).
Existing manifests, sessions and version-1 decision imports remain supported without
turning old audio media into newly interpreted questions. Reading old state does not
rewrite candidate identity or historical verdicts. New definitions and feedback-aware
exports use explicit format versioning so older importers refuse unsupported content
instead of silently dropping feedback. Upgraded runtime state must be identified;
implementation documents how to resume it with a compatible helper.

The loopback host and offline page support the same audio/feedback semantics. Retain
inline self-contained media, the standard-library runtime, current attachment/intake
bounds, token/origin protection and the prohibition on browser-triggered commands or
Git operations. No remote fetch, arbitrary file-serving endpoint, installed media
toolchain or new runtime dependency is needed. Optional diagnostic images are prepared
by the producer. Exact field names, persistence layout and rendering decomposition
are implementation choices within these contracts.

### Scope of the amendment and handoff

This proposed additive amendment concerns the portable-session behavior accepted by
[RFC-ASK-0003](RFC-ASK-0003-unified-rfc-workflow.md), specifically its attended-session
criterion ending in AC03, implemented by [ASK-0010](../issues/60-done/ASK-0010-attended-sessions.md).
Their exact source revision is the AgentSkills authoring reference above. Historical
acceptance remains unchanged. The wait correction in
[ASK-0092](../issues/60-done/ASK-0092-attended-review-without-model-polling.md) and its
recorded runtime limits remain in force. No adopted milestone exit is being rewritten.

Implementation owns `skills/attended-review/` instructions, contract, helper, page,
focused tests and a small portable mixed-question example. Correct relevant contract
drift while documenting the extension: the current intake permits verdict revision
and withdrawal, and its request bound is 20 MiB, despite older contradictory prose.
Keep existing limits rather than expanding them to accommodate audio feedback.

Faraday's Kiln producer remains responsible for asset preparation, diagnostics,
rights evidence and game-specific admission. Its isolation approval must not become
rights or in-game approval. Adoption of this generic skill does not rewrite existing
Faraday verdicts, replace its active hosts, alter its frozen packages or move its cards.
A later consumer task can emit the new manifest and reconcile domain evidence through
that consumer's authorized workflow. MASK runtime, deployment and consumer migration
are outside this source change.

No material design questions remain open in this draft. Authorized implement-rfc
execution should allocate/import the live RFC and bounded work/closeout records,
reconcile any concurrent attended-review
changes and implement this as one integrated source outcome. No portable pack or new
live tracker entries are created during this authoring task.

## Acceptance

- **AC01:** A portable mixed-session example presents ordinary and audio questions
  through one queue and intake, with the audio judgment's purpose and scope visible.
- **AC02:** The example's launcher/death alternatives demonstrate independent
  per-clip answers with comparison navigation, including partial review without
  inferred decisions for the remaining alternatives.
- **AC03:** Live and offline listening exercise the defined controls and failure
  behavior; a status/feedback update during playback preserves the active audition.
- **AC04:** Feedback entered before a verdict survives the defined navigation and
  resume boundaries, transfers while still unanswered, and never counts as acceptance.
  The Death C rejection and reuse suggestion remain separately interpretable.
- **AC05:** An answered question can have its feedback revised or its answer cleared
  with the specified history and retention; refresh or failed saves cannot silently
  discard a newer edit or claim an unsaved edit is durable.
- **AC06:** Public CLI/HTTP and offline paths agree on partial intake, retry and stale
  identity behavior for the extension. A clip or purpose change cannot inherit old
  feedback/approval, while unchanged legacy candidates and version-1 imports retain
  their established behavior.
- **AC07:** A handback with unanswered feedback returns through the existing driver
  boundary and protection model; idle review introduces no recurring model requests
  or domain-specific approval claims.
- **AC08:** Canonical instructions, contract and portable example describe the same
  supported formats and actual bounds. Focused source checks cover changed behavior
  and retain the package's offline and dependency-free runtime boundary, without
  claiming a Faraday migration or unperformed native-host qualification.

## Execution authority

Accepted for implementation by the owner on 2026-10-19. Source-only mandate revision `audio-source-v1`; owner decision above remains authoritative. Original draft retained unchanged under `drafts/`. Live work: ASK-0114; closeout: ASK-0115.
