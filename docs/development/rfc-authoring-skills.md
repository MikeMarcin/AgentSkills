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

## Independent behavioral acceptance

AC01, AC02 and AC05 pass on the unchanged source candidate. The coordinator supplied
[actual independent observations, replies and receipts](rfc-authoring-skills-independent.json)
from five fresh Codex agents. All 36 protected canonical hashes and 41 protected
original/live fixture files matched; no material source defect was found. Raw tasks
remain separate from judgments in `skills/author-rfc/tests/fixtures/tabletop-requests.md`.

| Case | Actual coverage |
|---|---|
| New authoring | Two RFCs/five proposed cards; declined optional grilling, complete artifact contract, four planned/six defined future criteria and partial coverage; optional internals/confirmation add no implementation gate |
| Supplied-pack resume | Partial replies and changed D1 reopen only affected branches; decisions and consequences propagate through RFC/cards/plan/view after each round; exact defaults/grouping/originals preserved |
| Focused retention/recovery | Revision 5 keeps material age/collision/race/recovery-data deferrals unready; terminology and observed/proposed contradictions remain explicit; separate exact synthetic confirmation covers only retention-recovery-r5 |
| Adopted amendment | Separate proposal records numeric before/after and live identities; active writer and pending native candidate unchanged; later reconciliation required before publication/binding renewal |
| Missing companions | Unavailable author-rfc/implement-rfc named; bounded grounding and unanswered frontier retained; pack unchanged and complete workflow pending |
| Standalone nonsoftware | Initial conversation-only frontier of three independent questions with recommendations; no RFC artifacts/companions or inferred answers |

The engineering leaf also exercised the **actual independently generated pack** in
two additional disposable linked consumers. [The 18 command receipts](rfc-authoring-skills-fresh-handoff.json)
record discovery, two-RFC/five-card ID and document-pointer remapping, adoption,
binding every current milestone, inspection and rendering. The authored
`safe-single-file-export` group binds AC01–AC04; partial coverage and typed future
AC05–AC10 survive unchanged after remapping. An initial driver path-normalization
failure from macOS `/var` versus `/private/var` is retained in
[its separate receipt](rfc-authoring-skills-driver-failure.json); only the disposable
driver was corrected. No source repair was required.

Actual host coverage is fixture inventory resolution/direct skill reads in Codex,
with synthetic coordinator replies. Automatic skill triggering/loading, native
Claude and native question-tool execution were not exercised. Nonsoftware coverage
ends at its initial frontier, not a completed event plan. No real installation,
selection, deployment or product implementation was performed. The optional
jsonschema check remains skipped. These limits do not waive a selected source
criterion or imply broader qualification. Synthetic design confirmation belongs
only to that test design, not to the human's real design decisions.

## Run contract and command state

Run `agent-skills-rfc-authoring-20261001`, segment `initial`; preserved selection
uses installed coordinator recipe fingerprint
`sha256:f798ea0d5a9d86b935f1ffffe53670a9ac2a310037ceac6f960795b91a20b0e3`.
Canonical source has ASK-0092's newer attendance text and fingerprint
`sha256:b236a31fbebd1a5d2cca1db05ac16f48fcd011dbc312f2d64c00f72dffbe2b14`.
Bind/check use the matching installed
`/Users/jaeger/.agents/skills/implement-rfc/scripts/milestone_checkpoint.py`;
candidate tests use canonical source. No installed selection/role was changed.

All deterministic and evaluator commands ended. Temporary test repositories/homes/
remotes were removed by their temporary-directory contexts. No worktree or server
was created. The coordinator returned canonical writer ownership for final acceptance
and upkeep after all five evaluator assignments quiesced. Actual receipts are now
durable here; the task-owned tabletop/source-plan scratch was removed after receipt
identity checks, including both consumed fixture Git repositories and their links.
The compact run selection/checkpoint remains available to the coordinator for final
handoff. Source packages have no changes after the accepted source candidate.
ASK-0093 is Done at `7235132b25e478f2c37afdfe6693598dbf3ded83`; closeout records
all five actual criterion outcomes. The selected milestone has no remaining
in-scope obligation. Unrelated unfinished RFCs are preserved.
