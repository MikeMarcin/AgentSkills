# Coordinator and milestone implementer

Use one coordinator and one engineering owner at a time. Select the generated
`rfc-implementer` role on the active host; its provider-specific route is independent
of the coordinator session route. A dispatched implementer enters **Implement the
milestone** below; it does not run the coordinator loop.

## Coordinate

Run `workflow_preflight.py --repo-root ROOT --selection FILE --json` for the resolved
selection. Add `--mode personal` only for personal tracker storage. This recipe needs
the native `rfc-implementer` role for the active host. Use its generated exact route
and the independently configured coordinator session route; an unavailable model or
explicit effort control is a capability blocker, not a reason to substitute another
route. Preserve an explicitly chosen coordinator session route.
[Host controls](../strategy-host-controls.md) covers scoped setup.

For each milestone:

1. Start a **fresh native `rfc-implementer` without copied conversation history**.
   Supply the exact repository and branch, user mandate and amendments, current
   milestone and live RFC/card/plan
   references, baseline, prior handoff, permitted effects and a durable return
   location. Give it the shared engineering contract and this recipe. Initial plan
   preparation belongs to this same implementer.
2. Wait for its completion notification without polling its transcript. Forward
   user amendments. The implementer owns engineering decisions, verification and
   upkeep; the coordinator tracks scope, child identity, progress and handoffs. A timeout continues the wait for the same child.
3. For unfinished work or corrections **within this milestone**, resume that same
   implementer, except across an attended-review wait. If native resume is unavailable,
   recover with a fresh implementer only after accounting for the previous owner's
   work and commands.
4. When required human acceptance is ready, require the implementer to prepare the
   configured attended-review session and start its loopback HTML server. Present the
   complete URL. After the implementer has returned a durable checkpoint and released
   its writer ownership, arm `wait --after SEQUENCE` through the host's durable
   background mechanism as `wait --after SEQUENCE --kind handed-back` **before yielding
   to the user**. The coordinator owns that watch and reads `status --after SEQUENCE`
   when it wakes; intermediate decisions stay durable without consuming the hand-back
   watch, so hand-back never depends on another user message.
5. Treat an attended-review wait as a context boundary. After hand-back, reconcile
   the recorded candidate, verdicts, protections and command state. If engineering,
   interpretation or upkeep remains, start a **fresh `rfc-implementer`** with the
   durable checkpoint and new events. If the verdict completes acceptance with no
   engineering work, the coordinator may close the milestone directly.
6. When the milestone is accepted and upkeep is finished, confirm the owner and its
   commands have stopped. Retire it and start a **new implementer for the next
   milestone**, even when the next milestone is small or closely related. Pass the
   durable handoff and live requirements, not the old conversation. Continue until
   the authorized pack is complete or a real blocker/user stop condition remains.

Do not dispatch additional workers, scouts, utilities, test runners or reviewers.
Deterministic tools and build/test subprocesses are ordinary implementer work. No
review relay, nested model call, shell model launcher or extra planning agent is
part of this default. Independently required acceptance stays pending until supplied
through a separately authorized review; self-review cannot satisfy it.

## Implement the milestone

Own the complete [engineering contract](../engineering-contract.md): understand the
requirements, prepare/adopt the plan where necessary, claim eligible work, design,
implement, test, diagnose, correct and self-review. Perform authorized integration
and explicit-path commits, update the issue board/RFCs and relevant documentation,
record evidence and decisions, and clean up task-owned temporary work. Complete all
constituent cards and exits in the bound milestone before handing back. Preserve
unrelated work and existing permission/publication boundaries.

Work directly as the non-delegating `rfc-implementer` leaf. Never claim native
enforcement or observed serving from a configuration file.

Use `milestone_checkpoint.py bind/check` for the selected milestone's obligations
and exits, with the supplied selection and run/segment identity. Its helpers check
consistency; you judge actual engineering evidence. Maintain one concise checkpoint
in the existing closeout so interrupted work can be recovered.

Return the milestone and child identity, actual result and candidate/commits,
verification and evidence links, completed upkeep, pending obligations, command
quiescence, and next eligible milestone or blocker. Stop at this milestone boundary;
the coordinator starts its successor. On the final milestone, reconcile the whole
authorized pack's acceptance and upkeep before reporting pack completion. Required
human, native or independent evidence remains explicit when unavailable.
