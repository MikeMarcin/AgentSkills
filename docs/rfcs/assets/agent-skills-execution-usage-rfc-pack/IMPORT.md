# Live import into AgentSkills

This packet is not an overlay to unzip on top of the repository root. In particular,
its README, issue-plan.json and payload do not replace live tracker/config files.

## Intake

On the real AgentSkills main checkout, inspect current instructions, live RFC IDs,
`docs/issues/NEXT_ID`, reservations and source differences. Record the actual current
main SHA as the initial pre-implementation anchor. Do not copy a placeholder SHA
from this pack or use the first implementation commit as its own baseline.

Retain the unmodified extracted packet under
`docs/rfcs/assets/agent-skills-execution-usage-rfc-pack/` and its live mapping in
`docs/rfcs/assets/agent-skills-execution-usage-rfc-pack.LIVE_IMPORT.md`. Retained RFCs
and cards are provenance only; they are not indexed as another board or repeatedly
loaded into worker prompts.

Use the existing main-only allocator, for example the actual source command:

```sh
python scripts/allocate_issue_id.py --count 21 --reserve-for agent-skills-execution-usage
```

Inspect its returned allocation and commit the real counter/reservation paths before
using the IDs. If numbering moved, remap every card, dependency, closeout, criterion
reference, link and planned-card list when copying to **live** docs. Reconcile RFC
IDs 0005–0008 against current live documents as well; do not edit retained originals.
Do not ship a synthetic reservation from this external archive.

## Copy only governing live documents

Copy the four new governing RFCs to `docs/rfcs/` and new cards to their specified
live lanes. Add the new rows from INDEX_ADDITIONS.md to the existing RFC index.
Preserve existing tracker README/rules. Replace each new live closeout's UNRECORDED
baseline with the true intake anchor once it is established. Set
`metadata.provisional_id` false only in the mapped live cards. Keep Proposed until
accepted through the repo's normal workflow, and no unperformed checks are Done.

Run the existing `python scripts/verify_documentation.py --root .` and the canonical
board queries against the mapped live IDs. Confirm exactly one closeout per new RFC,
valid dependencies and no retained asset cards in the active queue. Make the intake
commit with explicit paths. No pipeline step in this pack authorizes a remote push.

## Runtime payload adoption

The helper files under `payload/skills/implement-rfc/` are implementation seeds for
ASK-0022–ASK-0028, not installation side effects of document intake. Review and copy
only through their owned cards into canonical `skills/implement-rfc/`, rename seed
tests to live test names, and reconcile imports/tests with existing helpers. Do not
use a runtime sys.path pointing into docs/rfcs/assets. Remove old duplicated entry
paths after compatibility tests, not before.

Keep all reusable changes in AgentSkills. A selected consumer sees them only after
its actual MASK binding/artifact has changed through the appropriate public flow.
Pinned, development-link and legacy-source selections are different. A collection
flag granting visibility across registrations does not grant deployment authority.

The live-import mapping records provisional-to-live IDs, actual reservation and
intake commits, source/archive hash, copied paths and payload-adoption disposition.
It does not claim native qualification or a successful experiment.
