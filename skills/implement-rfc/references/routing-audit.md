# Local role usage and routing audit

Use `scripts/role_usage.py` when asked which roles ran, how often a driver uses
standard/deep workers, or whether recorded model selection matches an assignment.
Run it from either driver; `--driver` selects the history being read, not the
agent invoking the script. Python 3.11+ is sufficient; no host CLI is launched.

```sh
python /path/to/implement-rfc/scripts/role_usage.py --date 2026-09-05 --timezone America/Los_Angeles
python /path/to/implement-rfc/scripts/role_usage.py --driver codex --repo-root /path/to/project --json
python /path/to/implement-rfc/scripts/role_usage.py --driver claude --role rfc-worker-routine --json
```

Both drivers are selected by default. Omit `--date` for today in the selected
zone; the default zone is UTC. IANA zones require system timezone data (or the
Python `tzdata` package on hosts without it); UTC works without that package.
`--repo-root` matches the exact recorded checkout root, including distinct
worktrees. It is a filter and does not require project configuration or select
history from the skill's own directory. Omit it for all local projects.

The helper reads `$CODEX_HOME/sessions` and `archived_sessions` (default
`~/.codex`), and `$CLAUDE_CONFIG_DIR/projects` (default `~/.claude`). Override
with `--codex-home PATH` and `--claude-home PATH` for fixtures or retained local
copies. It does not fetch remote histories. Files are streamed on demand;
large histories may take time. No database, hook, daemon, telemetry upload,
second mutable ledger, or automatic scan at every closeout is installed.
Redirect stdout to a chosen local artifact if a snapshot is useful.

## Interpret the result

- **New agents**: distinct child identities created on the selected date.
- **Active agents**: distinct children with observed activity that date, including
  children created earlier.
- **Codex activity**: unique child-owned turn IDs, including follow-ups. Explicit
  thread IDs on runtime events establish ownership; inherited parent contexts
  do not. Multiple context records for one turn do not increase its turn count.
- **Claude activity**: unique assistant response IDs in subagent transcripts.
  Repeated streaming/content-block records do not increase the response count.
  Responses are not comparable to Codex turns or to billing/chart units.
- **Model observations**: Codex turn context model/effort; Claude assistant
  response model and recorded effort. Missing values remain null/unknown.
  Distinct model/effort observations within one activity remain visible, so
  observation totals can exceed the activity count. Configuration and a startup
  banner are not proof of the model that ran.
- **Role identity**: native metadata where available. Claude can fall back to
  an exact opening assistant `Role: ... | Model: ... | Effort: ...` banner; this is marked
  as self-reported. Prompts, model names and task titles never establish a role.
  Unattributed and non-RFC native subagents remain visible; filter by exact role
  when desired. A missing role is not evidence that no subagent ran.
- **Routing decisions**: the worker's exact assistant `Routing: standard|routine|deep |
  Reason: ...` line, with source location. Repeated startup/final copies are
  deduplicated. Reasons are limited to 500 characters; do not put sensitive
  information in these short assignment reasons. Missing historical reasons
  stay unknown; the helper does not reconstruct them from task text or models.

JSON schema identifier: `implement-rfc.role-usage.v1`. `summary` groups by driver
and role; `agents` retains identity, parent, project, activity, observations,
reason and file/line references. `sources` and `issues` describe inspected roots
and coverage problems. The output excludes full prompts, responses and tokens.
It includes local paths and task IDs, so keep snapshots local unless sharing
those details is intended.

Exit 0 means the selected scan completed without detected coverage errors;
it is not a verdict that routing was appropriate. Exit 1 returns a usable partial
report with issues (such as missing history roots, damaged files, duplicate
identities, or unproven Codex activity). Exit 2 indicates invalid CLI arguments.
Retained internal host formats can change, and deleted/unretained history cannot
be recovered. Empty readable roots mean no retained records, not proof of no
historical use. A snapshot of an active file may be partial; run again later if
its tail was incomplete. Missing optional audit coverage never blocks RFC work.

Compare observed model/effort with the routing policy that applied at the time.
Today's `config/routing.json` cannot prove yesterday's assignment was incorrect.
Likewise, a low standard/deep ratio is a reason to inspect assignments, not proof
of misrouting: the actual work may require sensitive contract changes.

## Claude-driven Codex companion lanes

`codex_lane.py` already records launches under the consumer's Git common
directory, in `<project>-codex-lanes.jsonl`. Include known logs explicitly:

```sh
python /path/to/implement-rfc/scripts/role_usage.py --driver claude --lane-log /path/to/git-common/project-codex-lanes.jsonl --json
```

Repeat `--lane-log` for multiple consumers. These rows appear in
`launch_attempts` with `driver: claude`, `executor: codex`, configured route and
source location. They are recorded before the companion executes and do not
establish execution or successful completion. They are never added to native
agent/activity totals or guessed to match a native session. A native Codex
record alone cannot prove a Claude driver launched it. Other remote/companion
histories and primary-agent work are outside the native census.

## Record new decisions

For substantial delegated implementation, select standard/deep as described in
[delegated execution](delegated-execution.md), and supply one concrete reason.
Workers repeat the assignment's decision after their identity line and in their
final Status. This keeps the reason in normal local runtime history for either
driver; no extra command is required for every delegation. Missing reasons in
older or cached role adapters are expected and remain unknown. Shared skill
links update policy immediately on disk; generated role adapters need an
explicit render in the selected consumer, and active hosts may cache both.

Historical `rfc-worker-routine`, `rfc-critical-reviewer` and routine decisions remain raw history. New selectors use `rfc-worker`, `rfc-worker-deep` and `rfc-reviewer-critical`. A generic historical worker without contemporaneous routing evidence remains unclassified; current models and dates cannot relabel it. Collect admitted assignments before regenerating; explicitly reissue when necessary, preserving original route evidence. No live session is hot-migrated.
