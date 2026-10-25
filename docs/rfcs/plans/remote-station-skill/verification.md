# Remote-station skill M1 verification

Milestone `agentskills-skill` (ASK-0124) of RFC-ASK-0017. Run
`remote-station-2026-10-24`, segment `m1-implementation-1`, mandate revision
`remote-station-v1`, selection `coordinator-implementer`. Host: native Windows 11,
Python 3.14, Git for Windows 2.55 (`cmd` and Git `sh` forwarders both exercised).

RFC_BASE_SHA `3ad85990719baec8f38544006a110c7a91bf6ab2`. Source candidate
`12d3c3285909542febf39ae090f4150a4e673fc0` (pure move `3173ee9` plus implementation
`12d3c32`). No AITO or BetterPullReview file was touched.

## Acceptance evidence

| Criterion | Actual check and result | Source revision |
|---|---|---|
| AC01 | `test_command_forwarder.StationConfigRefusalTests`: a disposable consumer holding only a `remote-station` link and `station.json` (no implement-rfc link or project context) answers `status --json` and runs a launch through the lease and supervisor to the Codex probe with Codex/Claude absent from PATH. Missing, malformed and unknown-key (`moira`) `station.json` each exit 2 naming the problem, with no lease start, no lifecycle lock and no station file. `test_station_config` covers every key rule, subdirectory resolution, explicit-root, origin and "project.json is not station configuration" refusals. The station suites run from `skills/remote-station/tests` (255 tests, 1 POSIX-only skip). `test_station_forwarders.test_forwarders_hold_no_station_logic` confirms implement-rfc keeps only the two forwarders. Pass. | `12d3c32` |
| AC02 | `python -B scripts/verify_rfc_bundle.py --mask-program C:/code/git/ManageAgentSkills` against the committed candidate with real MASK `9b73453`: tap, catalog, `bundle install agentskills/rfc` links all five skills (remote-station included) under `.agents/skills` and `.claude/skills` of a fresh fixture consumer; `status --check` healthy; remote-station `status --json` succeeds from both link roots and through implement-rfc's forwarder; uninstall, reinstall and upgrade pass. Receipt: [rfc-bundle-evidence.json](rfc-bundle-evidence.json). Pass. | `12d3c32` |
| AC03 | `test_command_forwarder.test_each_checkout_runs_its_own_pinned_version`: the installed command, through both `launch_remote_station.cmd` and the POSIX `launch_remote_station` under Git `sh`, runs version B from checkout B and its subdirectory, version C from B's linked worktree (its own link), and the real source version from checkout A's subdirectory. Pass. | `12d3c32` |
| AC04 | `test_refuses_outside_a_repository_and_without_the_skill_and_runs_nothing`: outside a repository the command exits 3 naming the directory; in a nested repository without the link (inside a consumer that has one) it exits 4 naming the root and `mask install remote-station`. Both print nothing on stdout and run no entry script. Pass. | `12d3c32` |
| AC05 | `test_arguments_stdio_and_exit_status_pass_through_unchanged` (argv with spaces and `=`, stdin, stdout, stderr, cwd and exit 7 through both forwarders) and `test_real_entry_matches_direct_invocation_for_status_refusal_and_launch` (forwarded `status --json`, refused `--machine Not_A_Token` and a launch reaching the Codex probe match direct invocation byte for byte in exit code, stdout and stderr). Negative control: removing `%*`/`"$@"` from the templates fails 9 subtests. Pass. | `12d3c32` |
| AC06 | M2 (ASK-0125): native AITO resume of `aito-main-win`. Not run in M1. | — |
| AC07 | M3 (ASK-0126): BetterPullReview documented commands. Not run in M1. | — |
| AC08 | `test_station_forwarders`: in a fixture consumer with both skills linked, implement-rfc's `launch_remote_station.py` (`status --json`, refused launch) and `station_control.py status --repo-root` match the remote-station scripts exactly, and the runpy `main(argv)` loading used by BetterPullReview's wrapper works. Without the sibling skill both exit 2 naming `mask install remote-station`. The real-MASK bundle run above also reaches the station through `.agents/skills/implement-rfc/scripts/launch_remote_station.py`. Pass. | `12d3c32` |

## Preserved behavior

All moved station tests pass from remote-station source, plus new tests for the
return-path warning (printed for every Claude endpoint, not for `--no-claude`),
management from a subdirectory, hooks from either guard location, and sequential
consumer identity. ASK-0123's history-sized turn read is unchanged.

## Regression comparison

The implement-rfc suite was run before (worktree at `011cc25`, 691 tests including
the then-resident station tests) and after (462 tests). Both runs share the same 20
failing test methods, all pre-existing Windows failures (cp1252 `read_text()` decoding, role-migration manifest
checks, issue-board CRLF/mode, usage capture). The only differences: the removed
personal-mode lease test, which failed before on a Windows backslash path, and one
new test whose fixture value was corrected and now passes. A first after-run hit
163 `0xC0000142` process-start failures (host resource exhaustion under concurrent
load); it was discarded and rerun cleanly.

`python scripts/verify_documentation.py --root .` (0 violations) and
`validate_portable_agents.py --source-only` pass; the implement-rfc portable
manifest was regenerated.

## Limits

- No real Claude or Codex runtime was started; fixture launches stop at the Codex
  probe. Live station resume is AC06's native M2 check.
- MASK refuses an input-only `mask-workflow.json`, so the skill ships none (see the
  RFC's implementation notes; owner decision pending).
- The guard's bounded recovery commands under explicit enforcement trust only the
  skill's entry script and project wrapper, not the bin command or the
  implement-rfc forwarder paths (documented in station control).
- `.cmd` forwarder caveats: `cmd.exe` expands `%VAR%` in arguments and asks
  "Terminate batch job" after Ctrl+C; Git `sh` converts POSIX-looking path
  arguments for native `py`.
