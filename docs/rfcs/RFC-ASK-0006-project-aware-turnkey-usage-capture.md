---
id: "RFC-ASK-0006"
title: "Project-aware turnkey usage capture and MASK selection"
status: "Auto-Verified"
owner: "MikeMarcin"
created: "2026-09-07"
---

# RFC-ASK-0006: Project-aware turnkey usage capture and MASK selection

Live IDs were reserved and imported; the retained pack is immutable provenance.
This is a new RFC, not an amendment silently rewriting settled RFC-ASK-0001–0004.

## Decision

Ship `scripts/usage.py` and its supporting modules inside the **canonical
`skills/implement-rfc` package**. The normal user operation after deployment is:

```sh
python3 .agents/skills/implement-rfc/scripts/usage.py
python3 .agents/skills/implement-rfc/scripts/usage.py --mask-projects
```

The first selects the project from invocation cwd. The second selects **all local
MASK project registrations**, whether or not they select `implement-rfc`. It does
not mean all user history, personal-scope work, all devices, or all deployed skills.
The tool can be invoked by absolute installed path from a nested project directory;
its script location never selects the project. Python 3.11+, standard library and
Git are sufficient; no pip, agent session, cloud account or analyst preparation is
required for ordinary capture. The public protocol and a runnable implementation
seed are included in this pack; integration/native qualification remains work.

## Exact project selection

No scope flags: resolve cwd physically, find the nearest `.mask.json` without
crossing the nearest Git worktree root; otherwise select that Git worktree root.
Outside Git an enclosing `.mask.json` may identify a non-Git project. Without either,
refuse with an actionable error. This last fallback is an explicit **collector
extension**, not a claim that MASK's own implicit project selection works outside
Git. Do not require a valid implement-rfc board merely to measure a project.

`--project LABEL=PATH` is an explicit repeatable override. `--alias LABEL=OLD_PATH`
adds a selected project's historical path without scanning that path's contents.
Default scope is the selected physical project/worktree. `--include-worktrees`
explicitly expands cwd/explicit selection to other known worktrees of the same Git
repository, retaining distinct physical rows. It is incompatible with
`--mask-projects`, which selects exactly the registry's roots. Nested selected
projects use longest-containing-root attribution; no prefix-string matching such
as `repo` also selecting `repo-other`.

Use recorded runtime cwd and exact parent/session joins, not Claude's lossy encoded
directory names. A worktree group is presentation metadata, not permission to copy
usage into each project. Do not merge repositories because their names or remote
URLs match. Maintain physical registration, Git-common-dir grouping, caller-defined
logical project, device and account identity as separate dimensions. A local path
hash is not a globally portable project identifier; merge across devices requires
explicit project/account aliases and records the mapping basis.

## MASK adapter: use what already exists

Call the installed public **`mask project list --json`** once for selection. The
attached MASK `mask.py::project_dispatch` already emits the list; no upstream
feature, private registry access, source edit or new MASK RFC is required.

Validate the returned protocol envelope:

```json
{
  "schema_version": 1,
  "tool": "mask",
  "command": "project.list",
  "ok": true,
  "changed": false,
  "error": null,
  "data": {
    "projects": [
      {"root": "/example/project", "available": true,
       "root_identity": {"device": 0, "inode": 0}}
    ]
  }
}
```

The identity values above are illustrative, not a real root. Each project record
may include additional fields; ignore them. In particular do not export cached
manifests, lock contents, source URLs, link ownership or credentials simply because
the list returns them. `available` is only a directory-exists observation in the
supplied implementation. Compare the supplied `root_identity` when the root exists;
an identity mismatch is excluded and reported, never attributed to a replacement
checkout. Unavailable registrations remain in `scopes.json`, and retained logs may
be matched to their known old path with `historical_path_unverified` provenance.
No source/config inspection occurs at an identity-mismatched root.

Missing MASK, timeout, invalid JSON, unsupported protocol, nonzero exit or malformed
project rows must not cause a wider fallback. An empty registry yields a valid
empty capture and an explicit warning. A moving registry may receive one bounded
observational retry if MASK reports state drift; do not invoke `recover`, `ensure`,
`register`, `apply`, `update`, or `doctor` as a repair side effect.

Respect `MASK_HOME`; provide `--mask-home` forwarded as public `--home`. A path
`--mask-executable` and a direct `--mask-python-entrypoint` support explicit setups.
For the existing Windows `mask.cmd`, recognize only the exact v1 template emitted
by `mask_install.py::launcher_text`, recover its two quoted interpreter/program
paths as data (including doubled percent signs), and invoke argv directly. Do not
evaluate arbitrary batch content. Unknown launchers get the explicit-entrypoint
instruction, not permissive shell parsing. Test the installed launcher on Windows.

## Capture CLI and output contract

Defaults: seven-day window ending at invocation, both local provider homes, automatic
new ZIP in the platform's user-local implement-rfc usage directory. `--days 30`,
`--since`, `--until`, `--out`, `--machine`, `--claude-home`, `--codex-home`, and
`--quota-dir` cover common overrides. Date-only boundaries are UTC, while offset
RFC3339 timestamps retain their stated instant. Store UTC inclusive start/exclusive
end and display them unambiguously. Record provider sample time separately from
capture time. Display the exact archive path on completion.

`--dry-run` resolves scope and prints the selected roots without scanning history
or writing output; MASK/Git observational calls are allowed. `--json` emits a bounded
summary; progress uses stderr. Existing output is never overwritten. Exit 0 means a
usable capture was produced, not complete coverage or implementation quality.
`--strict` returns 3 for a usable partial/empty capture. Fatal selection or I/O
errors return 2; interruption returns 130 and removes only this invocation's
unfinished artifact. A collector bug must not unlink a pre-existing file.

The archive contains `manifest.json`, `SUMMARY.md`, `scopes.json`, `sessions.json`,
`events.jsonl`, `counter_baselines.json`, `configuration.json`, `coverage.json`, and
optional sanitized quota/outcome records. Include hashes and byte counts for every
member, collector/schema versions, selected scope, interval, device pseudonym and
privacy mode. Schema `rfc-usage-evidence.v2` is an explicit advance from the v1 audit
kit; analysts accept both, never silently reinterpret old observations. A readable
summary is enough to identify coverage and next action; there is no dashboard
server or mandatory spreadsheet.

## Provider parsing and bounded resources

Visit each physical retained history file once even when multiple selected roots
share a provider history directory. Include both primaries and children. Keep exact
join candidates: response IDs, native turn/session IDs, parent call IDs, agent IDs,
structured termination, final usage, runtime model observations and requested
configuration. Missing role/model/effort stays unknown or unsupported as appropriate.
`<synthetic>`/API errors are not a fallback model. Role banners are self-reports.

Stream the file size observed at open instead of skipping entire large histories
by default or chasing an active writer forever. A configured positive file limit
is permitted only with per-file exclusion evidence. Bound individual lines and
report overlong/truncated/malformed records, changed files and identity conflicts.
Use a preceding cumulative-counter observation as `baseline_only_not_activity`;
never bill the start-of-window baseline as new usage. Older context/parent records
may be read solely to establish ownership and must not expand the activity interval.

Recognize current and legacy tool names, including `wait_agent`, `list_agents`,
`send_message`, `exec`, `wait`, `SendMessage`, and tool target aliases. Preserve
unknown tool-name hashes and coverage. For `exec`/parallel wrappers, retain only
structural nested tool names when already machine-readable. Never execute source
or infer arbitrary JavaScript behavior just to classify it. Parent wrapper and
child calls are separate display dimensions, not automatically two units of work.

File readers and archive writers are streaming. Normalized-event dedup and session
indexes also need bounded memory: adopt a temporary stdlib SQLite index when the
in-memory threshold is crossed. The included seed streams files but still retains
some event/call indexes in memory; ASK-0023 owns that production hardening. Measure
large-history behavior so a small-file happy path cannot conceal missing spend.
Record scan bytes/time, skipped counts, peak working-set observations when available,
and output bytes. Do not invent a universal memory number from this pack.

## Privacy and effects

Default allowlist excludes raw prompts, commands, tool results, source/patches,
reasoning, credentials, account tokens, reset IDs, URLs with credentials and auth
files. Current instruction/config inspection exports lengths, hashes and narrowly
allowed route fields, not arbitrary settings. Generated script bytecode must not
modify a read-only linked skill. The archive is **pseudonymized metadata, not
anonymous data**: stable hashes, timestamps and labels can identify work.

`--include-task-text` is a separately explicit sensitive mode with best-effort
redaction and a prominent manifest warning; it is unnecessary for routine experiment
accounting. Never enable it by ambient project configuration or `--mask-projects`.
No automatic upload, background schedule, native quota request, model call, agent
restart, symlink migration or state mutation occurs during ordinary capture.
Native quota capture is an explicit companion command under RFC-ASK-0007.

The packet supplies runnable collector code and focused fixtures under `payload/`.
Adopt it into the canonical package through an owned card, review and run tests,
then deploy through existing MASK flows. Never run from an immutable retained pack
as a hidden production dependency. Make old `role_usage.py` remain an activity view
with explicit scope or adapt it to this common parser without breaking its callers.

## Acceptance criteria

- **RFC-ASK-0006-AC01** — A zero-argument invocation selects cwd rather than the shared skill/source checkout, creates a new readable metadata ZIP, and works without mandatory board configuration or pip installation.
- **RFC-ASK-0006-AC02** — --mask-projects uses only public MASK project.list JSON, preserves unavailable registrations, validates root_identity, keeps worktrees distinct and never widens or mutates scope on errors.
- **RFC-ASK-0006-AC03** — Both primaries and subagents are captured with versioned tool/control identities, preceding counter baselines, structured final results and explicit unknown/unsupported evidence.
- **RFC-ASK-0006-AC04** — Large histories are streamed with bounded memory/indexing and visible truncation/coverage; a sample remains usable while concurrent writers append.
- **RFC-ASK-0006-AC05** — Default exports exclude raw task/source/credential/command/reasoning content, linked skill files stay unchanged, existing output is preserved, and no model/network/upload occurs.
- **RFC-ASK-0006-AC06** — Installed canonical and MASK-linked execution is verified on native macOS and Windows, including nested cwd, a Windows launcher and two registered worktrees; no cross-host completeness is implied.

## Implementation authorization

Accepted for implementation by the owner’s import-and-implement request on 2026-09-07. Native and owner-decision criteria remain open until exercised.

## Native closeout

Capture acceptance is verified on macOS and native ExampleWinHost Windows. See ASK-0026
for the exact source revisions, partial-coverage observations and focused native
checks. This status does not qualify other RFCs, infer complete account usage,
or deploy a consumer profile.
