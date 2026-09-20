# Simple milestone default

Owner-directed change, 2026-09-19, implemented at `5a40143` under ASK-0088.

Historical note: ASK-0089 subsequently renamed the public strategy to the
provider-neutral `coordinator-implementer` and moved the implementer route into the
generated cross-host `rfc-implementer` role. The evidence below describes ASK-0088's
original candidate.

New unspecified Codex runs select `coordinator-implementer-astra-max`: a Sol Low
coordinator dispatches one fresh Astra Max implementer per milestone. The implementer
owns planning, implementation, tests, self-review, authorized integration and commits,
board/RFC/documentation upkeep, evidence and cleanup. Corrections within a milestone
stay with its owner; every next milestone gets a fresh context after safe handoff.
No additional agents, nested model calls or automatic reviewers are part of this
default. Independently required acceptance cannot be self-certified.

The [recipe](../../skills/implement-rfc/references/strategies/coordinator-implementer.md)
uses a generic native agent with explicit model and effort, avoiding the earlier
Sol-bound custom integrator. The resolver still honors explicit and preserved
selections before the new default. The earlier recipes and historical study kit
remain available unchanged. This is an owner preference, not an M4 study verdict.

## Verification

All 26 focused AgentSkills tests passed:

- `test_execution_strategy.py`: 3; complete default routes, precedence, preserved
  baseline selection, selected instruction loading and invalid catalog refusal.
- `test_strategy_host.py`: 3; one-child coordinator settings, Max implementer
  settings with delegation disabled, and route mismatch detection.
- `test_mask_workflow.py`: 11; existing roles, staging and baseline readiness.
- `test_strategy_mask_public.py`: 1 public CLI scenario in two separate disposable
  consumers, through real installed links and approved development links. Plain
  preflight selects the new default without custom roles; missing inputs still fail
  and checks preserve MASK state.
- `test_planner_worker.py`: 3; existing selected recipe behavior.
- `test_primary_checkpoint.py`: 2; existing milestone acceptance and recovery.
- `test_strategy_study.py`: 3; historical kit and open-ended recipe registration.

Portable source validation, skill validation, documentation structure and
`git diff --check` passed. MASK's supporting read-only development-link fix at
`5c5c176` passed 32 profile, readiness, scope and pinned-update regression tests;
MASK-0119 records its closeout. Initial development preflight failed because MASK
treated inspection as mutating reconciliation. The fix separates those operations;
mutating ensure/apply still refuse development overrides.

No live implementation or judge agent was launched for qualification. Scoped host
configuration is verified as data, not as observed model serving or enforcement.
The current global Codex session setting was observed as Astra Max and was left
unchanged. The recipe's coordinator route is requested for a new task; an explicit
session model choice is preserved. Installation does not switch an active model.

## Local activation

Used the public MASK `source dev-link` command, reviewing each scope's preview and
applying its exact plan hash. Only the `implement-rfc` links and MASK ownership
records changed, for personal scope and the AgentSkills, ManageAgentSkills and
aito source checkouts. These are explicit local, unpinned development links to the
canonical authoring checkout; no tap was pushed or published. Ordinary upgrades
require an explicit return to pinned deployment first.

- Personal scope: selected readiness `ready_dev_link`, no state changes on check.
- AgentSkills: default preflight ready, no required custom roles.
- aito: default preflight ready, no required custom roles.
- ManageAgentSkills: default resolves and links are installed; preflight retains
  the existing `integration.approval_required` condition. No permission was granted.

Other project pins were not migrated and may continue to select their old package.
New tasks must discover the updated skill; loading in an already-running host was
not claimed. No generic `default` agent override was found in the inspected personal
and three selected project Codex agent directories.

The three FWB-0231 worktrees retain their original HEADs and clean tracked state:
Direct `d987a8b6cecd4a763f22d4c0ddc2b353df6e6b0f`, Coordinator
`16662de5e54e2e9f863e3bc57edd86001a59a8de`, and failed Native
`fa2b4b04678273c8cf67ccc7642248d00276a721`. Study artifacts were not edited and
no candidate was integrated.
