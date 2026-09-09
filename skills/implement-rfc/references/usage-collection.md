# Local usage capture

From a project root, run:

```sh
python3 .agents/skills/implement-rfc/scripts/usage.py
python3 .agents/skills/implement-rfc/scripts/usage.py --mask-projects
```

The first selects the invocation cwd's nearest declaration inside its Git
worktree, or the worktree itself. Outside Git, an enclosing `.mask.json` also
selects a project. The script's installed location does not select scope. No
implement-rfc board is required. `--mask-projects` reads the public local MASK
registry once and keeps registrations and worktrees distinct. It does not update
or deploy skills. Missing MASK refuses without broadening selection.

Use `--dry-run` to inspect roots without reading history or writing an archive.
Use `--mask-python-entrypoint /absolute/path/to/ManageAgentSkills/mask.py` if the
launcher is absent; `--mask-home` forwards public `--home`. Windows launcher
recognition accepts only MASK's exact owned v1 template, never arbitrary batch
code. `--project LABEL=PATH` and `--alias LABEL=OLD_PATH` select explicit current
and historical paths. `--include-worktrees` is an explicit expansion and cannot
be combined with registry selection.

A normal capture reads seven days of retained local Claude and Codex history and
prints a new ZIP path under the platform's user-local `implement-rfc/usage`
directory. `--days`, `--since`, `--until`, `--claude-home`, `--codex-home`, and
`--out` override those choices. Date-only boundaries are UTC; timestamp offsets
retain their instant. The end is exclusive. Existing output is preserved.

Inspect `SUMMARY.md`, `coverage.json`, and `manifest.json` before sharing the ZIP.
Default output excludes raw prompts, commands, source, reasoning and credentials.
Labels, timestamps and stable hashes can still identify work. Sensitive previews
require explicit `--include-task-text`; ordinary capture never uploads, runs a
model, reads native quota, or changes provider settings. Do not commit private
capture archives. Quota snapshots are a separate explicit companion interface.

Exit 0 means a usable archive, including partial or empty captures. `--strict`
returns 3 for those captures, retaining the ZIP. Fatal selection/I/O errors return
2; interruption returns 130 and removes only the unfinished output created by
that invocation. Missing history is unknown, not zero usage.

Histories stream their initial size with visible malformed, oversized and torn
records. SQLite indexes and streamed session summaries bound Python memory;
indexes live in task-owned temporary directories and are not exported. File
inventory rows cap at 10,000 with an omitted-row count. Coverage records bytes
scanned, elapsed scan seconds, and peak process RSS in the OS's native units when
available (bytes on macOS, KiB on Linux). RSS includes interpreter history and is
not an isolated collector allocation measurement. Token observations remain
unsummed until accounting reconciles response fragments, forks and counters.

## Native qualification

The owning live cards record exact commands and actual tested platforms. A
linked script invocation proves filesystem execution, not first-prompt host
loading. Portable fixtures do not qualify Windows. Keep unavailable native
combinations explicit and retain direct execution.

## Explicit quota snapshots

`python3 .agents/skills/implement-rfc/scripts/usage_quota.py codex
--account-label codex-main --machine mac-main --out-dir /local/quota` initializes
the installed native app server and reads account rate limits. This command can
contact the provider; it never starts a thread/turn or services authentication,
permission, purchase or reset requests. Failed/unsupported reads stay unknown.
Import saved snapshots with `usage.py --quota-dir /local/quota`.

An existing Claude status-line integration may pipe its native JSON to
`usage_quota.py claude-stdin --account-label claude-main --out-dir /local/quota`.
This is offline input parsing; no hook is installed or overwritten. `manual` mode
requires an explicit provider and observed used percentage or credit balance.
Provider sample time remains unknown unless established; capture time is not a
freshness guarantee. Opaque pools, account windows, actual credits and project
consumption remain separate. No model-to-pool mapping or project debit is inferred.

## Offline accounting and outcomes

Run `python3 <asset-root>/scripts/usage_report.py CAPTURE.zip --out NEW_DIRECTORY`
for immutable archive validation, reconciled ledger, grouped CSV and Markdown
report. Use `--help` for explicit outcome and optional rate-card inputs; quota snapshots are imported
through capture.
Duplicate captures are compared separately rather than summed. Missing baselines,
ownership or serving settings remain unknown; synthetic errors are separate.

Codex `token_usage_record` observations require the payload's owning thread and
response ID. Repeated copies of one response under the same owner count once;
conflicting copies and missing identities stay unknown. Input/cache and
output/reasoning remain parent/subset counts. Native response totals take
precedence over legacy request/turn/thread counters in the same session; those
alternate observations are never added. Each supplied surface must corroborate
independently against a comparable baseline interval or exact response; a matching
last-response counter cannot validate a conflicting cumulative counter.
Disagreement and unresolved overlap remain in the
ledger, so partially covered legacy intervals cannot claim complete consumption.
Sessions without owning response records retain the v1/v2 cumulative fallback.
Unknown native shapes remain visible in the capture's shape inventory; they do
not establish zero usage or known ownership.

The report's `session_lineage`, `families` and ledger ancestry columns follow
explicit native parent links transitively, including successive integrators,
leaves, deeper descendants and resumed sessions. Legacy parent fields remain
readable. Missing/conflicting parents and cycles stay unknown; the observed
family is not a certificate that every descendant history was retained. Roles
never assign a task, outcome or parent. Project scope is unchanged: missing or
unselected parent histories are not fetched or silently added.

Absent `--outcomes` produces `outcome_input: missing`, a null accepted task count
and no per-accepted-task ratio. An explicitly supplied outcomes document with no
accepted events reports an observed zero instead. Neither case establishes zero
productivity. Alternate counters that corroborate counted responses do not
create extra attempts; unresolved discrepancies still prevent an exact ratio.

Acceptance comes from explicit outcome records, not completion text or a moved
card inferred from time. Reopened tasks leave the accepted denominator; review,
failed attempts and recovery still count toward attributable all-in consumption.
Unassigned/unknown usage prevents a precise per-accepted-task claim. Price
equivalents from dated rates are estimates, not subscription charges. Compare
routing, orchestration and instruction changes separately; heterogeneous real
backlog work is observational and cannot automatically promote a profile.

The coordinator/integrator rollout changes topology, instructions and coordinator
route together. It is a combined observational rollout, not a one-factor
experiment. Existing experiment validation and unmatched-promotion restrictions
remain unchanged; token observations alone establish neither savings nor quality.
