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
