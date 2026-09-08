---
schema: "implement-rfc.card.v1"
id: "ASK-0035"
title: "Qualify bounded execution and failure delivery across native hosts"
status: "Ready"
rfcs: ["RFC-ASK-0005"]
depends_on: ["ASK-0033", "ASK-0034"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "runner-native-qualification"}
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
