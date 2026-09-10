# Author a milestone-aware RFC pack offline

This is the normal new-pack convention. The author can work from a chat and source
snapshot; running the consumer's scripting stack is not required. The runtime will
still validate and reconcile against the actual repository.

## Write intent, not a sequence of agent launches

Define the requested outcome and scope first. Draft RFC acceptance and issue slices,
then group complete integrated outcomes in `milestone-plan.json`. A milestone can
contain several cards or a well-bounded single issue. Include the relevant integration,
tests/docs and routine closeout in the outcome they support. Avoid an administrative
M0 whose only result is "the packet is imported" unless that is the user's actual
requested task. Do not put model routes, live hashes or permission grants in the plan.

Each group states what becomes demonstrably true, which issues/RFC obligations it
covers, prerequisites, exit criteria, and why the boundary is useful. A dependency
chain across cards can be one milestone. The final "tests" or "docs" card may be
necessary to that same outcome, not a compulsory new engineer. A large issue can
span milestones only through explicit disjoint source-criterion selections.

Use the minimal shape in [milestone-plan.template.json](milestone-plan.template.json),
which is an illustrative example with placeholder project IDs, not actual work.
The canonical schema is [../contracts/milestone-plan.schema.json](../contracts/milestone-plan.schema.json).
Copy it with the authoring kit when sharing outside this pack. Omitted criteria means
all acceptance of the selected source; an empty list is not a shortcut. Use actual
stable criterion labels, headings or unambiguous source quotes rather than inventing
acceptance IDs that the source does not contain.

A complete plan covers the selected target. For genuinely uncertain future work,
use `coverage: partial` and `unplanned_work` references, while making the first
milestone executable. Those obligations are still required. Do not use a partial
plan to omit awkward native/human acceptance. New unselected work is not authorized
merely because an author puts it in a plan.

## Make the file discoverable

Place the JSON at pack root. Add a `milestone_plan: "milestone-plan.json"` pointer
to a compatible pack index/manifest and a prominent ordinary link in README and
IMPLEMENTATION_PROMPT. Do not invent that field inside someone else's closed
manifest schema without updating it; the root convention and explicit link work
without a manifest. The entrypoint says to adopt/follow the supplied plan before
choosing the first engineering assignment.

Provide `MILESTONES.md` as a generated human view when useful. Do not separately
maintain a grouping in IMPLEMENTATION_ORDER.md or issue closeout prose. A rationale
file can link the plan instead of becoming a competing scheduler. Existing legacy
Markdown plans remain useful runtime inputs; a new pack should not require a model
to reverse-engineer them when structured intent is easy to provide.

## Check what is available without overstating it

When tools are available, check JSON syntax/schema, local references, unique IDs,
dependency cycles, exact duplicated/overlapping work, complete coverage and generated
view consistency. Verify pack cross-links and a real ID-map fixture. Otherwise label
those checks not run. Never invent a production revision, paid native test, semantic
acceptance or quota saving. Missing author-side checks do not forbid runtime adoption;
an invalid supplied plan must be repaired visibly rather than silently discarded.

The implementing skill preserves authored grouping by default, remaps provisional
IDs and resumes the adopted plan. It may amend it for a concrete discovery, keeping
unaffected milestones and unfinished obligations intact. It does not need to
rediscover the whole roadmap after each milestone or ask the user to approve ordinary
in-scope grouping. A milestone describes integration intent, not a compulsory one-to-one
integrator lifetime.
