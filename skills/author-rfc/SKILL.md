---
name: author-rfc
description: Draft or revise grounded RFCs and portable RFC packs, propose amendments to adopted designs, or resume proposal authoring for later implement-rfc execution.
---

# Author RFC

Own the proposal and its artifacts. Use this skill for new designs, supplied packs
(including ChatGPT drafts), unadopted revisions and proposed amendments. Draft without
automatically running a full interview. Material design choices still need answers;
offer `grill-rfc` when a systematic challenge would help or use it when requested.
Declining that optional interview creates no implement-rfc review gate.

## Ground the proposal

Read applicable instructions, existing RFCs, relevant implementation and terminology
(including context maps/glossaries). Read available consumer workflow context for
document conventions and constraints. Consumer configuration and execution preflight
are unnecessary just to draft. Investigate discoverable facts directly; describe
observed behavior with its source separately from proposed behavior. Surface conflicts
between the supplied design, code and existing requirements; do not silently choose
which source should change.

Recover current scope, artifact locations, settled decisions and unanswered questions
before new intake. Preserve original supplied material and provenance. Edit unadopted
working drafts directly, keeping authored grouping unless an agreed design change
warrants regrouping. For adopted material, read [Amendments](references/amendments.md).
Honor the requested destination or repository draft convention; otherwise use a
portable draft directory separate from live trackers.

Cover material decisions about behavior, boundaries, interfaces, failure handling,
compatibility, migrations and acceptance. A material unanswered choice makes the
affected scope unready; record it instead of filling it with your recommendation.
Detailed internal implementation design is optional: provide it on request for the
whole proposal or named areas. Explicitly defer detail that does not affect required
behavior; avoid converting such detail into an execution prerequisite.

## Build and maintain the pack

Read [Artifact contract](references/artifact-contract.md) when producing or revising
artifacts. Use its templates for RFCs, cards and the decision record. Resolve the
companion `implement-rfc` **by skill name through the host's available discovery**;
read its offline milestone authoring kit and use its existing schema, validator and
renderer. Paths in that kit are relative to the discovered package. No particular
host Skill tool or installation root is assumed. If unavailable, name the missing
capability, preserve drafts and explain which artifacts/checks await it; do not
invent a replacement schema or silently claim a complete handoff.

Keep the RFC requirements/acceptance authoritative. Decisions link to those sections;
cards and milestone work derive from them. After each answered round or agreed change,
update the decision record and consequences across RFCs, acceptance, cards and plan;
regenerate the milestone Markdown view from JSON. Preserve exact constraints and
numeric defaults. Reopen affected dependent decisions and confirmation after a change,
while retaining unaffected answers. If interrupted, record the exact pending frontier
and next action at the existing draft location.

Use `grill-me` only when interview mechanics are needed, or `grill-rfc` for an RFC
challenge. Pass scope, settled decisions, open questions, artifact paths and requested
coverage to the companion without restarting intake. Companion requirements depend
on the operation: `implement-rfc` for a complete portable plan kit; `grill-rfc` and its
companions for requested RFC grilling. Missing optional grilling does not block
ordinary authoring; missing required capabilities leave their operation pending.

## Hand off truthfully

Report structural validation, design readiness by affected scope/milestone, user
confirmation and execution eligibility separately. Structural success does not answer
design questions or resolve live dependencies. An independently ready current
milestone may be identified while future material decisions remain open; do not
certify the whole pack. Partial decomposition of **defined** requirements uses the
canonical `coverage` and `unplanned_work`, not a readiness waiver.

Summarize the design and ask for explicit confirmation when seeking shared
understanding. Record only an actual answer; recommendations and earlier confirmation
of a different design remain unaccepted for changed scope. Focused review confirms
only its recorded coverage. `implement-rfc` determines live execution eligibility
under its own authorized workflow; authoring confirmation is a design record, not a
new implementation gate. Hand over artifact paths, unresolved decisions/deferrals,
validation results and the implementation entrypoint.

Authoring uses provisional IDs and proposed cards. Live ID allocation, counter
advancement, RFC_BASE_SHA capture, card claims, acceptance evidence and implementation
belong to authorized `implement-rfc` execution. Keep draft validation output distinct
from implementation acceptance evidence.
