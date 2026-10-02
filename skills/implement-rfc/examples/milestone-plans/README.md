# Offline milestone authoring

For the surrounding RFC/card/decision artifact contract, resolve `author-rfc` by
skill name through the host's discovery. `grill-rfc` is an optional design interview;
neither it nor authoring confirmation adds an execution gate. This kit remains the
authoritative plan schema/validator/renderer; drafting needs no execution preflight.

Copy `milestone-plan.json` and `IMPLEMENTATION_PROMPT.md` to the pack root. Replace
the example issue ID and outcome with the actual proposed work. Keep plan-local
milestone IDs stable when live issue/RFC IDs are remapped. A one-fix request needs
only this one-milestone shape; several connected issues may contribute to one outcome.

The portable [JSON Schema](../../schemas/milestone-plan.schema.json) can be copied
into an offline editor or any Draft 2020-12 validator. No consumer checkout,
project configuration, native agent, or repository scripting stack is needed to
write a plan. The schema checks shape; the small optional Python helper below also
checks duplicate identities, dependency cycles and overlapping work. Neither proves
that exits cover requirements or that a referenced issue actually exists.

From any working directory, with Python 3 and this skill available:

```sh
python3 /path/to/implement-rfc/examples/milestone-plans/validate.py /path/to/pack/milestone-plan.json
python3 /path/to/implement-rfc/examples/milestone-plans/validate.py /path/to/pack/milestone-plan.json --render
```

Save the second command's stdout as `MILESTONES.md` after edits; never maintain
that view independently. The helper imports only the standard-library contract
module in `scripts/milestone_plan_contract.py`; it does not resolve consumer context.
Distribute that module with its relative skill path if distributing the helper.
The entrypoint link makes discovery explicit; a manifest may additionally contain
`"milestone_plan": "milestone-plan.json"`.

Use `{"issue":"DEMO-0001"}` for all applicable issue obligations, or
`{"rfc":"RFC-DEMO-0001","criteria":["AC01"]}` for selected existing criteria.
List selected RFCs/issues in `scope`. Criterion selectors must resolve unambiguously
after import. Disjoint criteria on a large issue may belong to different milestones;
the card stays open until its full acceptance is satisfied. Ordered milestone arrays
express preference, and `depends_on` contains hard milestone prerequisites.

For partial planning, use `"coverage":"partial"` and a nonempty `unplanned_work`
list of typed work references. Keep the current milestone concrete and every remaining
obligation represented without overlapping its current work. Do not use completion
status, model names, launch commands or invented revisions as plan fields.

For a legacy Markdown/stage plan, the first implementing engineer writes the JSON
normalization while preserving authored grouping and source evidence. For absent
plans, that same engineer forms the bounded current outcome and implements it.
Follow [adaptive preparation](../../references/milestone-plans.md#adaptive-preparation)
for receipts, adoption and reasoned amendments; invalid supplied plans are not absence.
Source exports include this kit, schema and live plan links. Keep session logs in
the consumer's excluded local runtime directories, outside the portable skill.
