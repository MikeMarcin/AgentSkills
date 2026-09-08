# AgentSkills: interactive coordinator and milestone integrators

**Implementation RFC pack · September 8, 2026 · AgentSkills only**

Keep the driver in the native interactive Claude Code or Codex session. That
session coordinates the authorized pack at **Opus 5 low** or **GPT-5.6 Sol low**,
respectively. It dispatches a fresh engineering integrator for each coherent
milestone, waits through native completion facilities, and consumes a compact
return. The integrator owns engineering judgment, implementation, verification,
board updates and commits. Workers retain complete-slice ownership; review
retains its independent, risk-selected role.

The objective is less repeated context and coordination per accepted capability,
not longer wall-clock sessions obtained by slowing useful work. The quality and
side-effect boundaries stay intact.

## Start here

Read [IMPLEMENTATION_PROMPT.md](IMPLEMENTATION_PROMPT.md) to implement the pack,
[IMPORT.md](IMPORT.md) to reconcile live IDs and capture the real baseline, and
the [RFC](docs/rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md)
for the decisions and acceptance criteria. [IMPLEMENTATION_ORDER.md](IMPLEMENTATION_ORDER.md)
groups the cards into usable milestones; the imported live board becomes the
execution source of truth.

The packet contains **one new RFC and nine provisional cards, ASK-0050–0058**.
Those IDs follow the supplied snapshot, not a live reservation. Existing settled
RFCs and historical results are not rewritten. No source implementation, native
qualification, rollout or measured saving is asserted by this packet.

## The important decisions

| Surface | Decision |
|---|---|
| Outer driver | Native interactive session; no external supervisor, headless launch loop, SDK, API credential use or new daemon |
| Coordinator routes | Codex `gpt-5.6-sol / low`; Claude `claude-opus-5 / low`; independent from all engineering routes |
| Integrator route | Preserve the owner's explicitly selected engineering route before lowering the coordinator. The proposal supplies a separately configurable integration default for a previously unconfigured run; see ROUTING.md |
| Context boundary | Fresh integrator at the next milestone; same integrator for the current milestone's corrections or partial invocation |
| Milestone | A bounded, demonstrable integrated capability; not one agent per card and not the whole pack in one child |
| Waiting | Native completion/wait, with only actionable interruptions; no speculative coordinator engineering |
| Acceptance | Direct evidence and sufficient integration checks; independent review where requested or warranted; required human/native acceptance remains open |
| Common paths | Implementation, resume, one-card work, status-only, attended preparation/intake, closeout and runtime-limited execution remain explicit |
| Rollout | Qualify native behavior, report all-in family cost, adopt only selected owned outputs; no fleet migration |

## Included implementation material

[draft/skills/implement-rfc/](draft/skills/implement-rfc/README.md) contains editorial
candidates for the short entrypoint and role-specific references. They are not a
complete replacement package: reconcile them with current helper contracts,
consumer instructions and generated roles before adoption. Branch-specific
instructions remain behind explicit pointers; leaf agents do not preload the
coordinator procedure or the entire pack.

[contracts/](contracts/README.md) specifies the compact dispatch/return boundary.
It is not a workflow engine or second board. [WORKFLOW_CASES.md](WORKFLOW_CASES.md)
and its fixture data cover normal and exceptional continuations.
[VALIDATION.md](VALIDATION.md) separates packet checks, implementation tests,
native behavioral qualification and efficiency observations.

[ROUTING.md](ROUTING.md), [CHANGE_MAP.md](CHANGE_MAP.md) and
[WRITING_REVIEW.md](WRITING_REVIEW.md) identify the exact existing contracts that
need reconciliation. [SOURCE_BASIS.md](SOURCE_BASIS.md) distinguishes supplied
source, user decisions, new design choices and dated external runtime facts.

## Validate this packet

From its root, run `python -B tools/validate_pack.py` and
`python -B tools/test_pack.py`. Both use the Python standard library, remain
inside disposable/local file operations, and never invoke a model or import
repository code. See [PACK_CHECKS.md](PACK_CHECKS.md) for the actual generation-time
results. Passing these checks validates the packet, not the future workflow.
