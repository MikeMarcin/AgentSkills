# Remote-station skill verification (M1, M4)

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
| AC09 | Measured on the same 80 recorded `aito-main-win` (`stn-39ef5ffb`) remote-task turns from the Codex rollout, plus the one recorded Claude endpoint turn, with tiktoken `o200k_base` ([method and results](#ac09-per-turn-token-measurement)). The before measurement was committed first (`83dc8c3`). Station protocol per turn fell from 1,716.6 to 441.1 tokens (−74.3%). All measured per-turn tokens fell from 215,204 to 113,163 (−47.4%). Pass. | `ee12b1e` |
| AC10 | `test_guard_refusals_fire_for_v1_and_v2_requests` (delegated request route, both versions): replayed `task_id` is denied as "already used" with reason `authority-exceeded`, the existing code, unchanged. Project mismatch in the envelope (v1 field; v2 JSON naming `project`) and in the station file gives `project-mismatch`. A lane-commit request to a read-only station gives `authority-exceeded`. A past `expires_at` gives `expired`. A wrong `station` gives `station-mismatch`. No turn state is written. `test_guard_refusals_fire_for_v1_and_v2_prompts` gets the same reasons from the fenced-prompt route's refusal envelope. That route keeps no task receipts, in v1 as in v2, so replay is a request-route refusal only. `test_v2_cannot_carry_caller_identity_or_unknown_flags` and `test_v2_flags_refuse_order_repeats_identity_and_shell_text` cover caller identity, order, repeats and shell text. All cases also run under the `aito.`-prefixed station schema. Pass. | `ee12b1e` |
| AC11 | `test_v1_dispatcher_envelopes_are_still_admitted`: the recorded dispatcher's v1 base64 request (with `checkout`, `notes`, cards and RFCs) is admitted. So are v1 fenced YAML and JSON prompts. The v1 helper output is byte-compatible. `.remote-station.json` and the lifecycle record are byte-identical afterwards. Every pre-existing v1 guard test passes unchanged, apart from the one assertion that read the old full-receipt hook text. The receipt it checked is now asserted on disk. Station identity code (`station_lifecycle`, `station_config`, the launcher and the station file schema) is untouched. Pass. | `ee12b1e` |

## AC09 per-turn token measurement

Milestone `compact-station-messaging` (ASK-0128). Run `remote-station-2026-10-24`,
segment `m4-implementation-1`. Script, inputs and outputs:
[measure_station_tokens.py](token-measurement/measure_station_tokens.py),
[before-v1.json](token-measurement/before-v1.json) and
[after-v2.json](token-measurement/after-v2.json). The outputs hold counts and
digests only, never transcript text.

**Inputs (read-only).** The station identity in AITO's `.remote-station.json`
names Codex thread `01a10525-e3fa-7250-85cf-c27f2f84897d` and Claude session
`session_01Mb2Coeg8PF5g19jUAMQGm1`. The Codex rollout
`~/.codex/sessions/2026/10/03/rollout-2026-10-03T21-22-11-01a10525-…jsonl.zst`
(sha256 prefix `d4846d5bdae85061`) holds 154 delegated prompts. 80 of them carry a
remote-task envelope. The local Claude transcript of that endpoint
(`f5700793-….jsonl`) holds one 192-token read-only capability prompt, with no
envelope and no hook context. Station messaging therefore costs that endpoint
nothing, before and after.

**Tokenizer.** tiktoken 0.14.0 `o200k_base`, installed in a scratch virtual
environment. The rollout's model (`gpt-6.1-sol`) has no public tokenizer, so
`o200k_base` is the closest public OpenAI encoding. Anthropic `count_tokens` needs
the network API and was not used. A `chars/4` proxy was run as a cross-check. It
undercounts base64 by more than half: 791.1 versus 1,716.6 protocol tokens per
turn before. That is why it is not the primary method.

**Sections** (per turn, from the actual items the station model received):
the `<codex_delegation>` wrapper; a fenced envelope; the admission request line;
prompt sentences repeated verbatim from earlier prompts; other prose; the
station model's own tool call re-typing the request (generated output tokens);
the helper's printed output; and hook `additionalContext`. "Station protocol" is
the fenced envelope, request line, echo, helper output and hook context.

**After.** `--format v2` re-expresses the same 80 turns in the shipped protocol.
The v2 envelope omits station-file fields and empty lists. The v2 plain-flag
request line replaces `--envelope-base64`, and a prompt that carried both keeps
only the line. The helper output and the one-line hook acknowledgement take
their v2 forms. Prose is never rewritten. All 89 re-expressed requests parse with
the skill's own `station_task_admission.command_request` (89/89).

| Section, mean tokens per turn | Before (v1) | After (v2) |
|---|---:|---:|
| Delegation wrapper | 51.0 | 51.0 |
| Fenced envelope | 29.2 | 7.8 |
| Admission request line | 799.3 | 171.8 |
| Model re-types the request (output) | 638.6 | 145.2 |
| Helper output | 96.1 | 84.7 |
| Hook additionalContext | 153.4 | 31.5 |
| Prose repeated from earlier prompts | 128.3 | 128.3 |
| Other prose | 794.2 | 794.2 |
| **Station protocol** | **1,716.6** | **441.1** |

Totals over the 80 turns: station protocol fell from 137,326 to 35,285 tokens.
All measured tokens fell from 215,204 to 113,163. Each protocol item is also
re-read by every later model request in its turn. That re-read cost fell from
2,909,841 to 699,002 tokens (−76%).

**What the before measurement showed (`83dc8c3`), and the design it chose.** Of
the RFC's three hypotheses:

- Station-invariant envelope fields were real but small: about 20% of the
  payload (132 of 663 tokens).
- The full-receipt hook context was confirmed at 153 tokens per turn.
- Repeated dispatch text was 128 tokens per turn.

The dominant cost was not among the hypotheses. The admission payload was
base64: the same envelopes cost 663.4 tokens encoded against 224.3 readable.
The station model then re-typed all of it as output. Plain flags carry the same
fields in 80.9 tokens; base64 of a compact envelope would still cost 502.7. v2 is
therefore a plain-flag request, a compact envelope and a one-line acknowledgement.
The remote-routing rule that forbids restating guard-enforced rules targets the
repeated prose. The re-expression does not rewrite prose, so that rule's effect
is unmeasured.

**Reproduce:**

```sh
python -m venv <scratch>/venv && <scratch>/venv/Scripts/python -m pip install tiktoken
<scratch>/venv/Scripts/python -I docs/rfcs/plans/remote-station-skill/token-measurement/measure_station_tokens.py   --codex-rollout <rollout .jsonl.zst> --claude-transcript <claude .jsonl>   --station-file <aito>/.remote-station.json --format v1|v2 --output <file>
```

Rerunning `--format v1` with the final script reproduces `before-v1.json` byte
for byte. Python 3.14 or later is needed to read `.zst`.

## M4 suites and gates

On candidate `ee12b1e`, native Windows, Python 3.14:

- The remote-station suite (`python -B -m unittest discover -s skills/remote-station/tests`)
  ran 279 tests: OK, 1 POSIX-only skip. Before M4 it ran 255.
- The implement-rfc suite ran 462 tests and failed in the same 20 test methods as
  the M1 baseline. All are pre-existing Windows failures: cp1252 `read_text()`
  (`test_portable_sources_name_no_project` fails on the untouched
  `coordination-handoff.md`), the generated-view `·` decoding, issue-board
  CRLF/mode and native-failure journal tests. None reads the changed files.
  `scripts/run_tests.py` stops at the first failing skill, which is why each suite
  was run directly with the runner's own command.
- `python -B scripts/verify_rfc_bundle.py --mask-program C:/code/git/ManageAgentSkills --source-revision ee12b1e`
  (real MASK `9b73453`): "Canonical agentskills/rfc ready: 5 skills,
  remote-station beside implement-rfc", with uninstall, reinstall and upgrade
  passing.
- `scripts/verify_documentation.py` reported 0 violations.
- `validate_portable_agents.py --source-only` reported the portable source valid.
- `render_runtime_adapters.py --write-source-manifest --check` reported the
  manifest fresh.
- `git diff --check` was clean.

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
