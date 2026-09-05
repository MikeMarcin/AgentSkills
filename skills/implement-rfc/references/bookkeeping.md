# Board commands and contracts

Run `python <asset-root>/scripts/issue_board.py --repo-root ROOT COMMAND`.
All commands accept `--json` and return a versioned compact object. Errors return
nonzero; parse the object instead of re-reading the whole board.

| Command | Purpose |
|---|---|
| `queue --rfc RFC-ID [--rfc RFC-ID]` | Scoped active work and next eligible card |
| `queue --area AREA` | Explicit monorepo area scope |
| `queue --human-waiting` | Cards parked for human attendance |
| `queue --all --history` | Intentional complete inventory |
| `inspect ID [--body]` | Selected metadata, dependencies and optional Markdown |
| `validate [--rfc RFC-ID / --include ID ...]` | Global identity/counters and scoped workflow; no scope checks all |
| `allocate [--area AREA] --count N --reserve-for TOKEN` | Main-integrator reservation and counter advance |
| `move ID --to LANE [--parked-on TOKEN / --blocked-by TOKEN]` | Guarded move/link repair without commit |
| `claim ID [--platform PLATFORM]` | Commit eligible Ready card into In Progress |
| `finish ID --acceptance FILE --paths FILE ...` | Commit approved acceptance and supplied paths |

Mutations support `--dry-run`; claim/finish support `--expect-revision SHA` when
prepared against a specific HEAD. Queue prefers a sole eligible in-progress
claim, then priority (absent means P2) and stable ID. Ordered-index sequencing
uses the consumer RFC index before priority. It reports ambiguity and external
handoffs, never auto-promotes Backlog or guesses remote completion.

## Canonical frontmatter

Cards use one field per line between `---` fences. Values are JSON; plain text
strings are also accepted for convenient editing. Arrays and nested objects use
JSON syntax. No multiline YAML, implicit YAML dates or custom control fields.
Unchanged bytes and Markdown bodies survive ordinary moves; edited values use
JSON serialization. RFC frontmatter uses the same syntax with repository-defined
fields; its status remains authoritative.

```yaml
---
schema: implement-rfc.card.v1
id: APP-0001
title: Add selected behavior
status: Ready
rfcs: ["RFC-APP-0001", "RFC-LIB-0002"]
depends_on: []
priority: P1
platforms: ["mac", "win"]
metadata: {"estimate":3,"original_context":"retained descriptive data"}
---
```

Required fields are schema, id, title, status, rfcs and depends_on. Empty arrays
represent independent work. Optional `closeout_for` is a subset of rfcs.
`external_depends_on` entries use `Repository:AREA-0001`; verify their real
integrated handoff evidence. Optional area/priority/labels/owner/dates/milestone,
platforms, parked_on, blocked_by and acceptance are documented in
`schemas/issue-card.schema.json`. Additional descriptive data is unrestricted
JSON under metadata. Historical conversion is one-off consumer work, never a
shipped format adapter.

The lanes are Inbox, Backlog, Ready, In Progress, Parked, Blocked and Done.
Ready means local dependencies are Done. Parked requires its reason token;
`human-review` identifies attendance. Blocked requires a blocker token; keep
concrete detail in the body or metadata. Done is terminal; make follow-up cards
for new work. Never rewrite historical acceptance to satisfy a validator.

## Acceptance and explicit Git authority

A finish decision file has this shape:

```json
{"approved":true,"decision":"done","records":[
  {"criterion":"AC1","outcome":"pass","revision":"actual source revision",
   "evidence":{"kind":"observation","detail":"What was exercised and observed"}}
]}
```

Decision is `done` or `human-pending`. Outcomes are pass/fail/pending; Done
requires passing records. Evidence kinds are command, observation, artifact or
freeform; extra evidence detail is allowed. The agent owns completeness and
relevance of the criterion set. Human-pending stores partial evidence and parks
for human-review; it does not close the RFC.

`record_evidence.py --repo-root ROOT --criterion AC1 [--output NEW_FILE] -- COMMAND
ARG ...` captures revision, exit code, elapsed time and short output tails. It
uses argument arrays, no shell. A zero exit code proves only command success;
the agent still judges the acceptance claim. Reuse unchanged relevant evidence.

Claim/finish require an empty index, preserve unrelated working files, and never
push. Supply individual repository-relative files, not folders/globs. Card moves
and pristine repaired links are included automatically; an already-dirty
bookkeeping file requires explicit inclusion in finish or a prior separate
commit. Claim has no arbitrary source path option. The tool refuses symlinks,
protected link edits, collisions, stale reads and unsafe destinations. File
writes use atomic publication and roll back ordinary write failures without
overwriting concurrent edits. Git failures leave reviewable changes; inspect
status and the error before retrying. Never reset unrelated work to recover.

`bookkeeping` config names live link roots and protected/explicitly editable
patterns. Keep immutable imported packets outside editable roots. Repair actual
Markdown links, including relative links on the moved card; do not rewrite code
examples or historical prose.

## Counters and history

`next_id.mode` is single-file or per-area; values are always AREA-NNNN. Per-area
filenames are AREA. Validation and allocation share the same counter model:
live IDs, reservations, and historical high water on branches, remotes, tags and
HEAD. Transient tool checkpoint refs are excluded. The default 2,000 changed
commit history bound is visible in allocation JSON; exceeding it refuses rather
than silently ignoring history. Explicitly increase allocation.history_limit
when justified. Shallow/missing Git history cannot establish unseen remote
allocations; fetch the integrator's known refs before cross-machine allocation.

A deliberate historical override is configured under allocation.rewind_overrides
as `{area,floor,waived_through,date,reason}`. It never waives live/reserved IDs or
a later high-water value. Do not add overrides merely to silence a real collision.
Reserve on main, commit returned counter/receipt files, then hand IDs to lanes.
