---
id: "RFC-ASK-0015"
title: "Portable RFC authoring and optional grilling"
status: "Implementing"
metadata: {"milestone_plan":{"id":"rfc-authoring-skills","path":"docs/rfcs/plans/rfc-authoring-skills/milestone-plan.json"}}
---

# Portable RFC authoring and optional grilling

The owner approved this integrated source-only milestone on 2026-10-01.
[ASK-0093](../issues/60-done/ASK-0093-author-rfc-and-grilling-skills.md) implements it;
[ASK-0094](../issues/60-done/ASK-0094-close-rfc-authoring-skills.md) owns closeout.
The [authored plan](plans/rfc-authoring-skills/milestone-plan.json) preserves one
integrated outcome. Mandate revision: `user-approved-plan-v1`.

## Problem and current behavior

AgentSkills has an execution workflow with an offline milestone schema, validator,
renderer, typed adoption and consumer binding. It lacks portable proposal authoring
and interview skills. Matt Pocock's upstream grilling and domain-modeling material
provides useful interview and terminology disciplines, but its explicit-only metadata,
mandatory Skill-tool calls, mandatory exploration subagents and project-level document
writes do not match this library's portable package and authoring boundaries.

## Goals and boundaries

Add `author-rfc -> optional grill-rfc -> implement-rfc` for new proposals and supplied
ChatGPT-authored packs. Material design decisions are always covered; detailed internal
implementation design is available for the entire proposal or selected areas on request.
Grilling is optional per task and adds no execution review gate. Canonical source only:
no personal/project selections, deployment, publication, pushes, credentials or permission
changes. MASK program code remains outside this repository's scope.

## Proposed behavior and interfaces

`author-rfc` owns grounding and the artifact contract: new authoring, unadopted revision,
proposed amendments to adopted material and resume. Read applicable instructions,
relevant implementation, RFCs, terminology and available consumer context; distinguish
observed behavior from proposals. Preserve originals, provenance, exact constraints and
numeric defaults, authored grouping and settled decisions unless an agreed change
warrants revision. An adopted-plan change identifies the live source, affected
requirements, rationale and before/after changes; authorized implementation handles
publication and active-work reconciliation. Replaying adoption over a live plan is
invalid; source/intent conflicts refuse. `check-amendment` preserves scope, obligations
and exits; it does not authorize changed requirements.

Ordinary authoring produces one compact RFC, with material decisions, actual answers
and open questions inline. A portable pack is created when requested, maintained when
supplied, or produced when the repository requires those artifacts at the drafting
stage. Such packs contain an overview, RFCs, proposed implementation cards, one
proposed closeout card per RFC, decision record, implementation entrypoint, canonical
milestone JSON, generated Markdown view and portable schema. Only that branch needs
implement-rfc's offline kit. Reuse its schema and helpers; resolve companions by skill
name through host discovery. Unavailable capabilities leave their operation pending,
while useful drafts are preserved. Drafting needs no execution preflight. Authoring
uses provisional IDs and never allocates live IDs, advances counters, captures
RFC_BASE_SHA, claims cards, creates acceptance evidence or starts implementation.

RFCs state the grounded problem, proposed behavior/boundaries and stable observable
acceptance. Add alternatives, specialized detail or separate decision history only
when they carry a material tradeoff or aid continuation. Inspect the affected path
until material claims are supported and cite decisive sources. Reuse established
conventions by reference; routine engineering choices remain with implementation.
Unresolved choices affecting intended outcomes, scope, safety, authority, compatibility
or caller-dependent contracts remain explicit. Ordinary drafts need no blanket design
confirmation; record actual answers and their scope. Pack-local decisions link to
authoritative requirements/acceptance rather than restating them.
Create pack-local contextual glossaries when needed; propose later project glossary/ADR
adoption separately. Record a significant ADR when a real tradeoff is hard to reverse
and surprising without context.

`grill-me` owns shared interview mechanics, with a decision tree and at most three
independent frontier questions with recommendations per round. Investigate discoverable
facts directly; wait for explicit answers without autoResolutionMs. Standalone defaults
to conversation only. `grill-rfc` combines author-rfc artifacts and grill-me mechanics,
challenging scope, behavior, interfaces, failure cases, compatibility, migrations,
acceptance, dependencies and milestone outcomes where relevant. After answered rounds,
propagate decisions/consequences through RFCs, acceptance, cards and milestones and
regenerate the view. Changed answers reopen affected branches and confirmation while
preserving unaffected decisions. Finish with a concise shared-understanding summary and
explicit confirmation. Recommendations remain proposals until answered; focused reviews
report actual coverage.

Structural validity, design readiness, confirmation and execution eligibility are
separate. Unanswered material decisions leave affected scope unready. An independently
ready current milestone may be identified without certifying the whole pack. Canonical
`coverage`/`unplanned_work` permit partial decomposition of defined requirements; they
neither settle material questions nor require optional internal design detail.

## Alternatives and decisions

Reuse the existing kit rather than a parallel planning engine. Three skills provide
independent invocation while keeping interview guidance in grill-me, artifact guidance
in author-rfc and specialized challenges in grill-rfc. Preserve MIT notices inside
adapted packages and record upstream revision. Portable frontmatter and host discovery
replace upstream host-specific invocation controls and mandatory dispatch.

## Acceptance

- **AC01:** author-rfc produces grounded, portable drafts/revisions/amendments with
  the artifact, readiness, provenance and authority contracts above; no automatic grill.
- **AC02:** grill-me and grill-rfc preserve explicit-answer interviews, resumed/changed
  decisions, consequence propagation, focused coverage and explicit confirmation,
  including standalone nonsoftware use and missing companions.
- **AC03:** packages validate through disposable MASK fixtures; catalog/provenance and
  relevant implement-rfc authoring pointers are current, MIT notice/source revision
  retained, documentation and regenerated portable manifest checks pass.
- **AC04:** a generated pack completes discovery, actual document/ID remapping,
  adoption and binding of every milestone in two distinct disposable linked consumer
  contexts; grouping survives and missing and ambiguous criterion selectors refuse.
- **AC05:** independent fresh-agent tabletop scenarios exercise new authoring, supplied
  revision, adopted amendments, interrupted/changed answers, partial decomposition,
  focused deep review, contradictions, missing companions and nonsoftware grilling.
  Inspect actual next actions/artifacts; unresolved material decisions keep affected
  scope unready and declining optional grilling adds no implementation gate. Record
  actual host coverage and unavailable checks honestly.
- **AC06:** a small authoring request produces a compact grounded RFC without an
  unsolicited implementation pack or blanket confirmation step. A changed answer
  updates affected behavior/acceptance and preserves other answers and material
  uncertainty, without inventing confirmation or execution authority.
- **AC07:** requested or supplied portable packs retain canonical artifact and handoff
  compatibility. Companion guidance selects the compact or pack branch consistently;
  focused package, documentation and public handoff checks pass on the source candidate.

## Verification and closeout

The engineering leaf performs deterministic checks and prepares a durable exact-candidate
handoff. The coordinator supplies independent tabletop evidence and resumes the leaf
for repairs and closeout. Structural checks and configuration readiness alone do not
establish behavior or running-host skill loading. Required acceptance stays pending
until supplied; no new real-host installation/native qualification is imposed.

## Accepted source outcome

AC01–AC05 pass for `39f02b7c654699e76233b8cfe6f966d915ca74b9`; see
[actual evidence and coverage limits](../development/rfc-authoring-skills.md).
Five independent Codex fixture cases and the actual newly authored pack's two-consumer
public handoff supplied the remaining acceptance. No source repair was needed.
Native Claude, automatic skill loading and native question tools were unexercised;
nonsoftware coverage is its initial frontier. Synthetic scoped confirmation is
test input, not a real human design decision. Source-only delivery and optional
jsonschema skip remain explicit. Consumed fixture projects are cleaned up; no
publication/deployment or unrelated closeout was performed.

## Canonical bundle command amendment — 2026-10-02

Owner authorization "Make the admendment to the rfc and update it" selects MASK's
bundle install/uninstall vocabulary under `named-bundles-v2`. Follow-up ASK-0096
updates canonical README and disposable verification, preserving accepted skill
payloads, four-skill bundle and discovery of all 16 packages. Historical ASK-0095
acceptance remains valid for its candidate; current command acceptance is verified
against the revised exact source/runtime. MASK-0128 owns runtime and the live
RFC-MASK-0010 amendment. No publication or real consumer deployment is implied.

Owner then selected install/uninstall/upgrade and answered "yes go with
recommendation": upgrade reviews definition changes and newer unheld package
versions together, preserving manual/overlapping selections, pins and local edits.
The owner also requested installed bundles be included in `mask upgrade --all`.
ASK-0096 verifies the exact canonical source with MASK's combined named preview
and guarded aggregate application, using a separate derived local fixture update.
All four RFC skills are ready with reviewed setup; all 16 packages remain
discoverable. [Current receipt](../development/rfc-bundle-upgrade-evidence.json)
also covers offline safe uninstall, manual companion preservation, reinstall and
repeat no-op. The source-only follow-up is accepted; original authoring acceptance
and host-loading limits remain unchanged.

## Compact authoring amendment — 2026-10-03

The owner authorized the reviewed alignment and implementation: “Ask the sub agent
to do that alignment, and then implement the plan.” [ASK-0098](../issues/30-in-progress/ASK-0098-compact-rfc-authoring.md)
owns the bounded follow-up above and AC06–AC07, with the original RFC baseline and
historical AC01–AC05 evidence retained. The source baseline for this amendment is
`5a6c64d167b65b7ff52b9b2e347ba2412baa6c03`. One added milestone preserves the original
completed grouping. Existing pack schema/runtime behavior and the MASK auto-commit
draft are outside this change; no publication or consumer deployment is authorized.
