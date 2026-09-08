---
schema: "implement-rfc.card.v1"
id: "ASK-0035"
title: "Qualify bounded execution and failure delivery across native hosts"
status: "Done"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0033", "ASK-0034"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "runner-native-qualification"}
acceptance: [{"criterion":"RFC-ASK-0005-AC01","outcome":"pass","revision":"42cd60e6ebcb1e922c93ad1a7109dbf073afb5e5","evidence":{"kind":"observation","detail":"Native macOS/Windows command and supported companion matrix recorded on this card; Windows Codex failure delivery exercised, local tool execution explicitly unqualified with direct fallback. Forty Windows runner cases reconciled after fixture-only fix; no automatic retries/acceptance/billing. Exact native reports inspected."}},{"criterion":"RFC-ASK-0005-AC03","outcome":"pass","revision":"42cd60e6ebcb1e922c93ad1a7109dbf073afb5e5","evidence":{"kind":"observation","detail":"Native macOS/Windows command and supported companion matrix recorded on this card; Windows Codex failure delivery exercised, local tool execution explicitly unqualified with direct fallback. Forty Windows runner cases reconciled after fixture-only fix; no automatic retries/acceptance/billing. Exact native reports inspected."}},{"criterion":"RFC-ASK-0005-AC04","outcome":"pass","revision":"42cd60e6ebcb1e922c93ad1a7109dbf073afb5e5","evidence":{"kind":"observation","detail":"Native macOS/Windows command and supported companion matrix recorded on this card; Windows Codex failure delivery exercised, local tool execution explicitly unqualified with direct fallback. Forty Windows runner cases reconciled after fixture-only fix; no automatic retries/acceptance/billing. Exact native reports inspected."}},{"criterion":"RFC-ASK-0005-AC05","outcome":"pass","revision":"42cd60e6ebcb1e922c93ad1a7109dbf073afb5e5","evidence":{"kind":"observation","detail":"Native macOS/Windows command and supported companion matrix recorded on this card; Windows Codex failure delivery exercised, local tool execution explicitly unqualified with direct fallback. Forty Windows runner cases reconciled after fixture-only fix; no automatic retries/acceptance/billing. Exact native reports inspected."}},{"criterion":"RFC-ASK-0005-AC06","outcome":"pass","revision":"42cd60e6ebcb1e922c93ad1a7109dbf073afb5e5","evidence":{"kind":"observation","detail":"Native macOS/Windows command and supported companion matrix recorded on this card; Windows Codex failure delivery exercised, local tool execution explicitly unqualified with direct fallback. Forty Windows runner cases reconciled after fixture-only fix; no automatic retries/acceptance/billing. Exact native reports inspected."}}]
---

# ASK-0035: Qualify bounded execution and failure delivery across native hosts

Governing RFCs: [RFC-ASK-0005](../../rfcs/RFC-ASK-0005-bounded-execution-and-durable-delegation.md).

## Objective and owned paths

Exercise command-only and one controlled agent slice on the native macOS/Windows combinations to be claimed. Demonstrate event-driven waiting, exact permission behavior, durable result collection and user cancellation. Review crash-after-launch and missing-report behavior at the native boundary. Keep unsupported combinations explicit and direct execution available; do not make an unavailable platform pass by relabelling a fake driver.

Own only: `skills/implement-rfc/tests/test_slice_integration.py`; `skills/implement-rfc/references/bounded-execution.md`; `selected native qualification records`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Claimed native combinations have actual runtime/permission/identity evidence and a result inspected at an integrator gate.
- No destructive reruns, lost ownership, automatic reset/credit use, or unbounded recovery under failure.

Criterion coverage: RFC-ASK-0005-AC01, RFC-ASK-0005-AC03, RFC-ASK-0005-AC04, RFC-ASK-0005-AC05, RFC-ASK-0005-AC06.

## Focused verification

Run selected end-to-end and negative native checks; reuse unchanged unit results. Capture only compact redacted facts and exact commands/artifact references.

## Run record

Implemented public read-only agent admission/delivery and four reproduced qualification corrections: frozen owned executable inputs, report replay after interrupted publication, cancellable event waits, and durable native identity checkpoints. Report publication is atomic/no-replace; native uncertainty never authorizes automatic relaunch. Source-writing/public recovery are explicitly unsupported; lower-level recovery remains bounded and cancellable.

Focused verification: 39 runner tests passed after lifecycle/public integration; 8 integration tests passed after runtime-capture privacy coverage; 3 public capture CLI tests passed after adding the new packaged journal reader. A scoped gpt-6-astra/high reviewer reproduced four blockers without model dispatch; all four received direct regression tests. Reviewer report is evidence, not semantic acceptance.

Native macOS public CLI pilot, existing claude.ai subscription, requested sonnet/high, Read/Grep/Glob, safe-mode/dontAsk:
- ASK-0025 preparation: run `backlog-windows-plan-20260908`, one 120-second/five-turn attempt. Native `error_max_turns`; no final report, no recovery/retry. Durable session identity retained. Top-level result was completion_unknown before the known-failure label correction; lifecycle retained max_turns exactly.
- ASK-0035 documentation check: run `backlog-runner-docs-20260908`, one 120-second/eight-turn attempt. Final report produced, collected and inspected at awaiting_integration. Applied useful terminology/qualification clarifications. No source edit by companion; no RFC acceptance delegated.

Public invocations were `python3 -B skills/implement-rfc/scripts/run_slice.py start --order .mask/generated/implement-rfc/pilot/order.json --approve-order 14129df10a22b4fcdaa922b86cad3c5175789352adfa147379de65e9f2136c7c` and the same command with `order-docs.json` / `f47a3d9f239e11257b586d9228a164d23e417bbdca8a6f6c5e5703f90d5a1cd3`. Exact frozen inputs and private reports remain under ignored `.mask/generated/implement-rfc/`. All companion processes closed.

Owner budget: two real backlog tasks, one bounded attempt each, no purchased credits/resets. Used two; exhausted. This is observational orchestration qualification, not a controlled routing/instruction comparison, quota-saving claim or completion of ASK-0025. Candidate remains opt-in.

Required Windows/native combinations remain unqualified: project station registry is empty and project instructions specify local implementation only. Do not mark this card Done or its RFC Auto-Verified. Previous macOS adapter observations remain on ASK-0033/0034; no Windows evidence is inferred.

## Integrator-owned qualification corrections

Qualification identified source defects and a missing selected public agent path.
The integrator extends this card's exclusive source scope to `slice_model.py`,
`run_slice.py`, `slice_runtime.py`, `slice_events.py`, `slice_codex.py`,
`slice_claude.py`, and their focused tests to correct input freezing, crash-safe
report publication, cancellable event waits, and admitted read-only agent stages.
No consumer settings, remote station, or billing changes are included.

The same integration slice also owns `usage.py` and `slice_events.py` to include privacy-safe selected-consumer lifecycle observations in captures. These observations never infer acceptance or add inclusive usage aggregates to token consumption.

The integration scope includes `tests/test_usage_cli.py` to exercise the updated read-only package file set.


## Native Windows qualification and supported boundary

Owner approved two additional Windows qualification attempts on 2026-09-08,
separate from the exhausted two-task pilot. Exactly one per provider ran through
public `run_slice.py start` with frozen orders, no automatic redispatch/recovery,
no purchased credits/resets, and existing native subscription authentication:

- Codex CLI 0.153.4, gpt-5.6-sol/low, read-only/never, 120-second wall limit.
  Run `native-windows-codex-20260908`, order digest
  `4b3cb21b9cc839859e7554071b575bdc803937e63b2a0e0bd3b053f2a64d7b33`.
  Native report delivery/collection succeeded. The inspected report says both
  internal file-read tool calls hit local command-runner startup timeout; the
  requested inventory was not completed. This is failure-delivery evidence,
  not successful Windows Codex file-reading qualification or semantic acceptance.
- Claude Code 2.1.263, sonnet/high, Read-only tool set, safe-mode/dontAsk,
  eight native turns/120-second wall limit. Run `native-windows-claude-20260908`,
  order digest `50d96d547e5c435e8236536202c058bec34b23d5caf4b8485fe62e947d95a473`.
  The report correctly inventories Windows output paths and capture exit/strict
  behavior. Integrator inspected the report; production, collection and semantic
  decision remain distinct.

Native Windows command suite: 40 cases, one fixture UTF-8 error corrected on
ASK-0025; its focused rerun passed. Public command cancellation, deadlines,
quoted Unicode argv and final gate execute natively. Driver lifecycle fixtures
run on Windows but do not masquerade as additional live model attempts.

Both native reports, exact orders and journals are retained under
`C:\Users\example\AppData\Local\implement-rfc\qualification\execution-usage-20260908`.
Both companion processes closed. Source candidate is `1a165ef`; the two later
fixture-only corrections are committed at `ca81470d`. No station checkout changed.

Supported qualification matrix: commands on macOS/Windows; macOS Codex/Claude
companion execution/report delivery; Windows Claude read-only execution/report
 delivery; Windows Codex authentication/protocol/failure delivery only. Windows
Codex local tool execution remains explicitly unqualified and should use direct
commands or an explicitly selected qualified runtime. The RFC permits explicit
unsupported capabilities and direct execution; no broader native success is claimed.
The card is accepted for this documented supported boundary, replacing the earlier
incorrect host-unavailability blocker. Further native model attempts are not
preapproved by either exhausted budget.
