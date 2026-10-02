# Raw tabletop requests

These are user-task inputs, not expected outcomes. The coordinator provides fixture
discovery and simulated replies; questions must go to the coordinator, not the human.

## New authoring

Use author-rfc to draft a portable RFC pack for safe ledger export in this project.
I don't want a grilling session. Single-file export must refuse an existing destination
unchanged; new CSV files have a 10 MiB size limit and jobs have a 30-second timeout.
Later batch export must use at most 100 data rows per file, record a completed offset,
resume without duplicate rows, and refuse changed input identity. On interruption,
exclude partial files from the completed offset. All this behavior is decided. Fully
decompose the first outcome now and represent the defined batch/resume work for later
decomposition. Don't spend time choosing internal classes/modules. Save the draft in
drafts/new-export. Tell me the next implementation action.

## Supplied pack, interrupted answers and changed decision

Use grill-rfc on drafts/current, which came from the ChatGPT pack preserved in
supplied/original. Focus detailed review on retention and recovery; leave unrelated
decisions in place. Resume our interrupted round in the design record. For Q1: retain
completed files for 7 days. I haven't answered Q2 yet. Also change the earlier D1:
instead of refusing an existing destination, allow replacing it after an explicit
per-command confirmation. I sometimes call one export file an account. Review that
language too. Save revisions and the pending questions in the current draft.

## Adopted design amendment

Use author-rfc to propose an amendment to the adopted ledger export design. Change
the batch boundary from 100 to 250 data rows per file and the job timeout from 30 to
60 seconds. The existing live plan has active work and a pending native acceptance
decision; preserve those facts. Keep the single-file then batch/resume grouping if
possible. Save the proposal under drafts/amendment. Include the precise next action
for someone later authorized to implement it.

## Missing companion

Use grill-rfc to review the supplied portable pack. This fixture's host discovery
offers grill-rfc and grill-me but cannot resolve author-rfc or implement-rfc. Keep
any useful partial work and tell me what I can do next.

## Standalone nonsoftware grilling

Grill me about starting a neighborhood reading group. I have a $120 monthly budget,
want 6–10 people, and am deciding between weekly evenings and one long Saturday
session each month. I haven't chosen a venue. Keep this in conversation.
