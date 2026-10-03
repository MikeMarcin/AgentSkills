---
name: author-rfc
description: Draft or revise grounded RFCs and portable RFC packs, propose amendments to adopted designs, or resume proposal authoring for later implement-rfc execution.
---

# Author RFC

Own the proposal and its artifacts. Default to one compact RFC. Build a portable
pack when requested, maintain it when supplied, or follow repository requirements
for pack artifacts at this drafting stage. Later implementation bookkeeping alone
does not require an authoring pack. Draft without automatically running an interview;
use `grill-rfc` for a requested challenge or offer it when systematic review would help.

## Ground the proposal

Read applicable instructions and available consumer workflow context for document
conventions and constraints. Inspect the affected implementation, existing requirements
and relevant terminology until the proposal's material claims are supported; cite
decisive sources. Investigate discoverable facts directly. Separate observed behavior
from proposals and surface conflicts between supplied designs, code and requirements.
Consumer configuration and execution preflight are unnecessary just to draft.

On resume, recover current scope, artifacts, settled decisions and unanswered questions.
Preserve supplied originals and provenance. Edit unadopted drafts directly, retaining
authored grouping unless an agreed change warrants regrouping. For adopted material,
read [Amendments](references/amendments.md). Honor the requested destination or draft
convention; otherwise save the RFC separately from live trackers.

Open a question when a concrete scenario in the request, inspected code or applicable
rules leaves competing outcomes unresolved. Hypothetical risks alone do not create a
design or permission question. Follow established execution conventions within current
authorization and retain actual approval boundaries. A material choice changes the
intended outcome, scope, safety, authority, compatibility or a contract callers depend
on. Keep such unanswered choices explicit and affected scope unready; a recommendation
is not a user answer. Routine engineering choices belong to implementation.

## Write and revise

Use [the RFC template](assets/rfc.template.md) for the grounded problem, proposed
behavior/boundaries and observable acceptance. Include only detail needed to decide
the proposal and distinguish success from failure. For small changes, use short
paragraphs and a few independent acceptance criteria; expand to resolve concrete
ambiguity. State each requirement once. Acceptance names distinguishing observations
and refers to defined behavior instead of repeating it. Leave mechanisms and test-case
inventories to implementation unless they settle a material design choice.
Reference established conventions and specify
the changes. Add significant alternatives or technical detail where their omission
would leave material behavior ambiguous, or when requested. Internal design may be
deferred without becoming an execution prerequisite. Keep exact constraints and
numeric defaults. Define each stable acceptance ID once in its RFC; the handoff
binder counts repeated labels even in cross-references. Within that RFC, refer to
behavior by heading or description; cards and plans may reference its criterion IDs.

Keep material decisions, actual answers and open questions inline. Use a separate
[decision record](assets/decisions.template.md) when substantial history benefits
continuation. Link to requirements rather than restating them. After an answered
round or agreed change, update affected behavior, acceptance and existing supporting
artifacts; reopen only affected questions and confirmation, retaining other answers.
On interruption, record the pending frontier and next action at the existing location.

## Portable packs

When building or maintaining a pack, read [Artifact contract](references/artifact-contract.md).
Resolve `implement-rfc` by skill name through the host's discovery and use its offline
milestone kit; this branch needs its canonical schema, validator and renderer. Paths
are relative to the discovered package. If unavailable, preserve useful drafts and
name the artifacts/checks still pending; do not invent a replacement schema.

Use `grill-me` only for interview mechanics, or `grill-rfc` for RFC challenge. Pass
scope, settled decisions, questions, artifact paths and requested coverage without
restarting intake. Missing optional companions do not block ordinary RFC authoring.

## Hand off truthfully

Deliver the draft without requiring blanket confirmation. Seek an explicit answer
when resolving a material choice or conducting requested shared-understanding review.
Record only actual answers and their scope/version; earlier confirmation does not
cover changed behavior. Hand over artifact paths, material open questions, relevant
deferrals and checks actually performed in the reply. Keep authoring/check/runtime
reports in that reply unless requested as saved artifacts. Pack readiness reporting
follows its contract.
`implement-rfc` determines live execution eligibility; authoring confirmation and
optional grilling add no implementation gate.

Use provisional `RFC-DRAFT-NNNN` IDs for RFCs and `DRAFT-NNNN` for proposed cards,
with zero-padded numeric suffixes. Live ID allocation, counter
advancement, RFC_BASE_SHA capture, card claims, acceptance evidence and implementation
belong to authorized `implement-rfc` execution. Keep draft validation output distinct
from implementation acceptance evidence.
