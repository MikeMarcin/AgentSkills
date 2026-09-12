---
schema: "implement-rfc.card.v1"
id: "ASK-0072"
title: "An integrator collects its children instead of ending its turn to wait"
status: "Done"
rfcs: []
depends_on: []
priority: "P1"
acceptance: [{"criterion":"integrator-collects-inside-its-turn","outcome":"pass","revision":"b3cfe69","evidence":{"kind":"observation","detail":"Two fresh rfc-integrator dispatches on 2026-09-11 read the entrypoint and then dispatched both leaves with run_in_background: false, collecting both results in the same turn; harness metadata recorded requestShape foreground for each child and no completion reached the coordinator session. The second assignment said nothing about foreground dispatch or concurrency, so the behaviour came from the entrypoint alone. Both probes ran against the consumer's checked-in role file, which still carries the previous claude-fable-5-1 low route; the new integration route is unexercised natively."}},{"criterion":"leaf-prompts-and-adapter-grant","outcome":"pass","revision":"b3cfe69","evidence":{"kind":"command","detail":"tests/test_integrator_waits.py asserts the clause in every rendered leaf prompt for both providers, that COORDINATION_TOOLS omits TaskOutput and that the rendered Claude integrator lists SendMessage without TaskOutput. A scratch consumer render confirmed the same files on disk."}},{"criterion":"documented-host-behaviour","outcome":"pass","revision":"b3cfe69","evidence":{"kind":"observation","detail":"references/runtime-compatibility.md 'Nested child results' records the published subagent contract (a child's summary returns through its Agent call, TaskOutput stripped from every subagent even when the tools field lists it, background results delivered while the parent runs) separately from the 2026-09-11 observations. Named divergence: the documentation lists TaskStop as stripped by the first filter yet keeps it in the background filter, and TaskStop worked from a foreground subagent on 2.1.266; the guidance depends on neither."}},{"criterion":"integration-route-renders-for-both-providers","outcome":"pass","revision":"b3cfe69","evidence":{"kind":"artifact","detail":"Scratch consumer render: .claude/agents/rfc-integrator.md carries model \"claude-opus-5\" with effort xhigh, .codex/agents/rfc-integrator.toml carries model \"gpt-5.6-sol\" with model_reasoning_effort \"xhigh\"; leaf adapters keep their routes. Codex keys and the xhigh slug checked against the published model and subagent configuration references on 2026-09-11; no Codex session was run. A clean worktree of this commit passes 465 focused tests (9 skipped), portable source validation and the documentation gate (12 RFCs, 72 cards, 0 violations)."}}]
---

# ASK-0072: An integrator collects its children instead of ending its turn to wait

## Problem

Observed twice in a consumer's attended-review run on 2026-09-10/11. A foreground
`rfc-integrator` dispatched scouts in the background, then ended its turn to wait
for their notifications. A subagent's final message is its return, so each
integrator returned a short partial to the coordinator, and the scouts' completions
were delivered to the coordinator session instead. The coordinator forwarded
pointers by hand, and resumed integrators polled scout transcripts to recover the
reports. One scout left a filesystem-wide search running about 90 minutes past its
own report.

Nothing in the skill said how a subagent waits. The integrator role asked for
"native waiting", `runtime-compatibility.md` left foreground/background selection to
the integrator, and the rendered Claude role granted `TaskOutput`, which the host
strips from every subagent. The coordinator's workaround, "use blocking waits with
TaskOutput", was therefore impossible to follow.

## Objective and owned paths

A delegating agent collects every child inside its own turn, and a leaf leaves no
command running when it returns.

Owned paths: `skills/implement-rfc/references/milestone-integration.md`,
`references/runtime-compatibility.md`, `references/model-routing.md`,
`config/roles.json`, `config/routing.json`, `scripts/render_runtime_adapters.py`,
`generated/portable-manifest.json`, `tests/test_integrator_waits.py`,
`tests/test_render_runtime_adapters.py`, `tests/test_standard_worker_target.py` and
this card. No consumer re-staging, lock commit, or other skill is in scope.

## Bounded work

- The integrator entrypoint states the waiting contract where every integrator
  already reads: dispatch leaves in the foreground, several per message for
  concurrency, and never end the turn with a needed child running.
- Leaf roles finish their own background commands before returning.
- The Claude adapter stops granting `TaskOutput`.
- Record the host behavior against the published subagent documentation.
- Owner's 2026-09-11 allocation decision: move the integration route to
  `gpt-5.6-sol` xhigh and `claude-opus-5` xhigh.

## Acceptance

- AC1: The integrator entrypoint carries the rule, and a fresh `rfc-integrator` on
  its configured route dispatches leaves in the foreground and collects them in one
  turn without being told to in its assignment.
- AC2: Every leaf role prompt requires finishing its own background commands before
  returning, and the rendered Claude integrator no longer lists `TaskOutput`.
- AC3: The recorded routing behavior matches the published Claude and Codex
  documentation, with the observed divergences named.
- AC4: Both providers render the integration route as Sol xhigh and Opus 5 xhigh,
  with focused tests, the portable manifest and the documentation gate in agreement.

## Verification and execution record

Source revision `b3cfe69`. A clean worktree holding only this change passes the
full skill suite (465 tests, 9 skipped), `validate_portable_agents.py
--source-only` and the repository documentation gate, so the committed manifest
matches the committed tree. Unrelated in-flight work in the checkout stayed
uncommitted, and its pending manifest entries remain for its own owner.

Native limits: the two live integrator probes ran on the consumer's existing
role file, so they exercise the entrypoint rule at the previous route, not the
new one. No Codex session was run; its model id and effort slug were checked
against the published configuration reference only.

Continuation: consumers keep their checked-in role files until a separate
`mask ensure` re-stage records new locks, so the new route and the leaf clause
reach agents started after that re-stage. Six registered consumers select this
skill.
