---
name: implement-rfc
description: Implement or resume RFCs and RFC packs through verified milestones; inspect progress, prepare required human review, or close out selected scope.
---

# Implement RFC

Resolve the consumer and the selected execution strategy before loading an engineering
procedure or checking custom roles. Helper paths are relative to this installed skill;
consumer paths always use an explicit absolute source checkout root.

For explicit personal storage or a remembered external tracker, first read
[Personal storage](references/personal-storage.md). Otherwise resolve project context
with `scripts/project_config.py --repo-root ROOT` and read its `project.json`,
`project.md` and applicable repository instructions.

For **status only**, inspect the selected live queue/closeout with existing helpers
and report it without changing source, board or agents. For **usage only**, read
[Usage collection](references/usage-collection.md) and run its observational helper.
These branches end without implementation readiness or a model launch. For **review
only**, bind the exact candidate and required independence; use an explicitly
permitted independent reviewer, or leave required independent review pending.
Review does not grant repair authority or select an implementation strategy.

For implementation, resume, closeout or attended preparation, read
[Strategy selection](references/strategy-selection.md). Resolve natural-language intent
with `scripts/execution_strategy.py resolve`; preserve its resolved JSON beside the
existing continuation. Precedence is explicit invocation, preserved run selection,
explicit configured preference, then the backward-compatible coordinator-integrator
recipe. Topology, model routing and project/personal storage are separate choices.

Read the shared [Engineering contract](references/engineering-contract.md), then
**only the selected recipe entrypoint** returned by the resolver. That recipe owns
its execution procedure and custom-role readiness; the coordinator recipe is never
an outer wrapper around direct, native or planner-worker execution. A designated
coordinated `rfc-integrator` enters [Milestone integration](references/milestone-integration.md)
under its existing assignment; leaf roles follow their bounded assignment.

Preserve the user's mandate and amendments, current outcome, evidence, unresolved
obligations and stop conditions. Continue the authorized scope until its acceptance
or explicit stopping boundary; do not infer completion from a card, commit, short
return or context reset. Strategy changes require safe writer reconciliation and a
recorded new segment. Source edits/rendering do not prove installed or observed loading.
