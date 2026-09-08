---
schema: "implement-rfc.card.v1"
id: "ASK-0048"
title: "Activate bounded delegation in implement-rfc"
status: "Done"
rfcs: ["RFC-ASK-0009"]
depends_on: []
acceptance: [{"criterion":"Delegation activation","outcome":"pass","revision":"44e3eb0","evidence":{"kind":"observation","detail":"Explicit entrypoint request; independent seven-scenario tabletop selected useful delegation and respected local/prohibited/unavailable cases. 25 focused tests, skill validator, portable source validator and diff check passed. Live UX task behavior and runtime serving untested."}}]
---

# Activate bounded delegation in implement-rfc

Follow-up to RFC-ASK-0009; historical acceptance remains unchanged.
RFC_BASE_SHA: 9db4f05fe6e47b047823c718a0af3503a3223f04

The reported UX redesign session selected no subagents because optional routing
never explicitly activated delegation under a host policy requiring a skill request.

Own SKILL.md, references/delegated-execution.md and generated/portable-manifest.json
under skills/implement-rfc, plus this card. Make the skill explicitly request bounded
delegation when useful independent primary work can continue. Preserve small/coupled
local execution, runtime restrictions, leaf authority, standard/deep routing and
risk-based review. No consumer adapter or live task mutation.

Acceptance: entrypoint activates applicable delegation; realistic independent policy
cases distinguish useful parallel work, coupled work and runtime prohibitions;
portable manifest and documentation validation pass. Record observed limits here.

## Results

Source revision: 44e3eb0. Independent subagent delegation_policy_cases read only the
revised skill and seven supplied scenarios. It selected scout, standard worker,
test runner and one reviewer for independent work; local execution for an immediately
blocking correction, user prohibition and missing API. This is tabletop behavioral
evidence, not execution or serving evidence from the reported UX task.

11 test_unified_workflow and 14 test_render_runtime_adapters tests passed.
quick_validate.py and validate_portable_agents.py --source-only passed; diff check
passed. Pre-closeout documentation validation correctly reported this unfinished
follow-up under the terminal RFC; rerun after finishing the card.

The evaluator also observed older role names in the current runtime and an existing
sandbox-fallback ambiguity. No role adapters or consumer sessions were changed;
those observations do not establish a routing failure in the UX task. Shared links
observe integrated source bytes, but running tasks must reread cached instructions.
