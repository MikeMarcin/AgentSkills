---
schema: "implement-rfc.card.v1"
id: "ASK-0072"
title: "An integrator collects its children instead of ending its turn to wait"
status: "Ready"
rfcs: []
depends_on: []
priority: "P1"
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

## Verification and continuation

Focused instruction and rendered-adapter tests, the full skill suite, portable
source validation and the repository documentation gate. Native Codex execution is
not exercised; its model and effort are checked against the published
configuration reference only. Consumers keep their existing checked-in role files
until a separate `mask ensure` re-stage records new locks.
