# Portable pack contract

Use this contract when a pack is requested, supplied, or required by the repository
at this drafting stage. Ordinary compact RFCs follow `SKILL.md` and its RFC template.

Keep an overview, RFCs, proposed implementation cards, one proposed closeout card per
RFC, decision record, implementation entrypoint, canonical milestone JSON, generated
Markdown view and portable schema together in the draft directory. Filenames can
follow the consumer's draft conventions. Make their pointers explicit in the overview
and entrypoint so raw intake can discover the plan. Preserve originals outside the
editable working draft and record their source/version.

Use the discovered `implement-rfc` package's `examples/milestone-plans/README.md`,
`milestone-plan.json`, `IMPLEMENTATION_PROMPT.md`, offline `validate.py` and
`schemas/milestone-plan.schema.json` as authoritative. Copy the plan example,
entrypoint and schema into the pack, then edit the plan and render `MILESTONES.md`
with that validator. Run it against the exact final JSON; save validation results
as draft checks, never invented implementation evidence. The renderer's stdout is
the generated view. The offline helper checks structure/identity/cycles/overlap;
consumer discovery/adoption/binding later resolves actual live selectors and context.
Distributing the optional helper requires its existing relative contract module;
normally use it from the discovered companion without copying a second engine.

## RFCs and cards

Use [the RFC template](../assets/rfc.template.md) and link each RFC to its proposed
implementation cards, closeout and canonical plan. RFC requirements/acceptance remain
authoritative; decisions link to them and cards/milestone work derive from them.
Keep the core skill's unique criterion-label convention for consumer binding. After an agreed
change, update affected artifacts and render the milestone view from JSON.

Use [the card template](../assets/card.template.md) and canonical
`implement-rfc.card.v1` fields/statuses from the companion's bookkeeping reference.
Relationships are arrays. Use the provisional IDs defined in `SKILL.md`; reconcile
actual IDs during authorized import. Proposed
cards normally use `Backlog`; execution establishes eligibility/Ready. Each RFC has
one proposed card with `closeout_for` including its ID, linked to all its required
acceptance. Do not put a made-up baseline, revisions or passing acceptance in it.

## Decisions and terminology

Use [the decision record template](../assets/decisions.template.md). For each material
choice, link the authoritative requirement/acceptance, status (open, proposed, settled
or explicitly deferred), actual answer, rationale and consequences, plus dependent
decisions/affected artifacts. Recommendations stay proposed until answered. Record
deferrals with the boundary they leave defined and any remaining readiness effect.
Record focused coverage and explicit confirmation separately from validation.

Keep a pack-local glossary when resolved domain language is needed. Read existing
context maps/glossaries first; preserve different meanings across bounded contexts.
Use concise definitions of domain concepts with preferred terms and avoided synonyms;
implementation detail belongs in the RFC, not the glossary. Challenge overloaded or
contradictory terms and concrete edge cases against code and domain usage.

Record a pack-local ADR only when a choice is hard to reverse, surprising without
context and the result of a real tradeoff. A short context/decision/rationale paragraph
usually suffices; add alternatives or consequences when useful. Ordinary decisions
still belong in the decision record. Propose later project glossary/ADR adoption
separately; authoring a draft does not authorize writes to live project records.

## Milestones and readiness

Retain authored grouping, outcome, dependency order and exits. Use plan-local stable
milestone IDs and typed source references; import remaps document IDs, not milestone
identity. Define integrated usable outcomes rather than one milestone per card.
Cards/dependencies are work and acceptance units; the plan is neither mutable board
state nor execution evidence.

Use `coverage: partial` with nonempty typed `unplanned_work` when some **defined**
requirements have not been decomposed. Include every remaining obligation without
overlapping planned work. Partial decomposition does not answer a material design
question. When future behavior itself is undecided, record that question and mark
affected future scope unready; a valid JSON plan must not be presented as full design
readiness. Identify independently ready current milestones without certifying future
scope. Keep optional internal detail explicitly deferred when observable
requirements are already defined. Do not add session routes, launch commands,
completion status or fabricated revisions to the plan.

Record four independent facts once in the decision record, linked from the overview:

- Structural validity: validator command/result and unchecked selectors/coverage.
- Design readiness: scope/milestones with material answers or remaining questions.
- Confirmation: actual user statement, scope/version covered, or pending.
- Execution eligibility: not evaluated by drafting; authorized implementation checks
  live mappings, dependencies, mandate and acceptance under its existing workflow.
