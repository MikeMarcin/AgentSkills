# Portable RFC authoring and grilling evidence

Assignment: RFC-ASK-0015, one `portable-authoring` milestone in
`rfc-authoring-skills`, mandate `user-approved-plan-v1`. Canonical source candidate:
`39f02b7c654699e76233b8cfe6f966d915ca74b9`. Source-only delivery; no selection,
deployment, publication or push. Upstream reference revision was observed as
`d81f3a183412e71a5b1e84ca21bc1a35eea03a60`; its unrelated `.gitignore` change is preserved.

## Deterministic verification

Captured command records are in [the evidence JSON](rfc-authoring-skills-evidence.json).

| Surface | Actual outcome |
|---|---|
| New skill frontmatter | skill-creator quick_validate passed for all three packages |
| Passive MASK packages | disposable source commit/local bare remote/tap/home; author-rfc, grill-rfc, grill-me and implement-rfc validate; no real registry/selections used |
| Portable pack handoff | two consumers, ALP and BET, with different configured document roots, symlinked canonical implement-rfc; offline export/schema/view, discovery, actual document/ID/link remapping, adoption and binding of both authored milestones pass |
| Selector and adoption failures | missing AC02, ambiguous duplicate AC02 and changed-source re-adoption each refuse; grouping and source identities preserved |
| Documentation gate | 15 RFCs, 94 cards, zero structural violations |
| Portable source | regenerated implement-rfc manifest valid |
| Existing offline kit | two tests pass; optional published-schema test skipped because jsonschema is unavailable in the selected Python runtime |

The initial fixture run exposed an unremapped draft-relative plan pointer and an
unfetched approved MASK tap. The fixture now remaps document pointers with IDs and
explicitly fetches its local tap. These were fixture corrections; no MASK or
implement-rfc runtime changes were necessary. The final recorded run passed against
the committed source candidate. Self-review checked companion reachability, single
ownership of interview/artifact guidance, exact numeric constraints, amendment and
readiness boundaries, MIT notices, and the actual public helper path.

## Behavioral acceptance frontier

AC01, AC02 and AC05 remain pending independent tabletop evidence. Raw task inputs
are separate from evaluation judgments in
`skills/author-rfc/tests/fixtures/tabletop-requests.md`. The coordinator receives
isolated projects for new authoring/partial decomposition, supplied-pack resume and
changed decisions/focused review, adopted amendments with active/pending obligations,
and missing companions; standalone nonsoftware interviewing uses conversation.
Evaluator questions go to the coordinator for simulated fixture replies, not the
human. Existing task authorization is not test-design confirmation.

This evidence establishes offline helper/package behavior, not running-host skill
loading, real installations or broad native qualification. No independent outcome
is inferred from instruction wording. The final candidate and actual evaluator
coverage/outcomes must be recorded before closing this milestone.

## Run contract and command state

Run `agent-skills-rfc-authoring-20261001`, segment `initial`; preserved selection
uses installed coordinator recipe fingerprint
`sha256:f798ea0d5a9d86b935f1ffffe53670a9ac2a310037ceac6f960795b91a20b0e3`.
Canonical source has ASK-0092's newer attendance text and fingerprint
`sha256:b236a31fbebd1a5d2cca1db05ac16f48fcd011dbc312f2d64c00f72dffbe2b14`.
Bind/check use the matching installed
`/Users/jaeger/.agents/skills/implement-rfc/scripts/milestone_checkpoint.py`;
candidate tests use canonical source. No installed selection/role was changed.

All deterministic processes ended. Temporary test repositories/homes/remotes were
removed by their temporary-directory contexts. No worktree or server was created.
Only the explicit run/checkpoint/tabletop scratch directory is retained for the
coordinator's required acceptance. Canonical source writer ownership is released
at this checkpoint; evaluators may read source and write isolated fixture artifacts.
Resume engineering for repairs and final closeout after their actual evidence arrives.
