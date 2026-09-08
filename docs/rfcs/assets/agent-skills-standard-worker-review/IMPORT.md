# Import and adoption

Read the live AgentSkills instructions and canonical implement-rfc project context.
Use an isolated authoring worktree for source edits so consumers following development
links do not see an intermediate role migration. The integrator owns main/IDs/indexes.

## Register one RFC and four cards

The supplied source has eight live RFCs and NEXT_ID ASK-0043. Treat RFC-ASK-0009 and
ASK-0043–0046 as provisional. Reconcile all IDs and current changes first. On the real
integrator main, reserve four issue IDs using the existing wrapper:

```sh
python3 scripts/allocate_issue_id.py --count 4 --reserve-for standard-worker-review --dry-run
python3 scripts/allocate_issue_id.py --count 4 --reserve-for standard-worker-review
```

Use the actual allocator result. Commit only its returned counter/receipt paths before
source work. Remap the packet's new filenames, frontmatter, links and criterion IDs
consistently if necessary; never overwrite existing IDs or rewind NEXT_ID. RFC IDs
require a separate live index collision check; the issue allocator does not reserve RFCs.
Retain the original packet unchanged under `docs/rfcs/assets/` as provenance, not a second
live board. Record actual mappings, imported destinations, deliberate exclusions and the
real baseline in a LIVE_IMPORT record. No fake reservation or snapshot SHA is supplied.

Merge this row into the live RFC tracker (adjust the ID if remapped):

```text
| RFC-ASK-0009 | Proposed | Standard implementation worker and independent review routing |
```

Copy the new RFC and four cards, not a replacement README or NEXT_ID. The work is
owner-directed; advance the live lifecycle through the existing workflow without a new
model-selection interview. Set ASK-0046's RFC_BASE_SHA before source edits. Use existing
`issue_board.py` claim/finish commands, not direct card moves or per-platform folders.

Run `python3 scripts/verify_documentation.py --root .` after import. Sequence is
ASK-0043 → ASK-0044 → ASK-0045 → ASK-0046, with exactly one closeout. No dependency
requires a new MASK RFC or deployment to every project.

## Existing consumers

Use the current `manage-agent-skills` skill and MASK public CLI contracts. Inspect
`mask capabilities --json`, `mask source status --json`, and the selected consumer's
`mask project show --project ROOT --json`. Inspect selected artifact/pin state before
preparing changes. `mask project list --json` or an inventory can locate consumers;
it does not authorize updating them. Public plan/apply with the matching guard remains
a separate explicit action. Do not edit MASK internal files or rewrite context en masse.

For selected consumers already following the updated canonical development source,
regenerate only after active old assignments are collected or explicitly reissued:

```sh
python3 /path/to/AgentSkills/skills/implement-rfc/scripts/render_runtime_adapters.py --repo-root ROOT --check
python3 /path/to/AgentSkills/skills/implement-rfc/scripts/render_runtime_adapters.py --repo-root ROOT
python3 /path/to/AgentSkills/skills/implement-rfc/scripts/render_runtime_adapters.py --repo-root ROOT --check
```

The first check may correctly report old/stale roles; the implementation must preflight
ownership and hashes before the write. For pinned consumers, first use the supported,
explicit MASK selection/update flow, then invoke the renderer from that consumer's
selected artifact rather than mixing canonical HEAD with its old pin. A successful
render is not evidence that a running agent reloaded. Do not restart live work silently.

Capture the previous source/artifact and owned manifest before adoption. Roll back only
explicitly selected clean owned artifacts/settings; refuse user modifications and keep
usage/evidence history intact. No automatic source push, credit use or CLI upgrade.
