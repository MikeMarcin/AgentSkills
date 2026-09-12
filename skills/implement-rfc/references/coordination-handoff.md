# Coordination handoff

A handoff preserves the current engineering frontier, not the story of the run.
Use the live board/RFCs and a chosen closeout as project truth. A small task-local
memo may hold the original user mandate/amendments and native IDs; it is not a
second backlog. Resolve all paths from the selected consumer, not the skill link.

## Assignment

Use [Plan-first execution](milestone-plans.md) for discovery and computed binding.
Bind current outcome, obligations and exits; grouping survives card progress.
V2 separates acceptance from explicit continuation intent and reason.

Give the integrator: run/dispatch and current mandate identity; exact root/branch;
authorized RFC/card/area scope and milestone objective; applicable closeout and
immutable baseline references; ownership and allowed side effects; engineering
route; current continuation; and this return contract. Preserve actual user
requirements separately from the previous integrator's recommendations.

The initial objective may be “select the next usable milestone in this authorized
scope.” Later objectives come from the outgoing integrator and live state. The
coordinator checks scope; the incoming integrator verifies technical relevance.

## Compact return

Return the normal role identity plus these fields, as one small structured result
or its labelled equivalent supported by the native host:

- Run/dispatch, producer identity and mandate revision; milestone and disposition.
- Usable behavior or partial result; current candidate/working state and exact
  handoff/evidence locations. Unobserved revisions/routes remain unknown.
- Whether task writers/commands are quiescent, active or unknown, and what remains
  to account for. A generated success sentence is not runtime completion.
- Required human/native/blocker obligations and the next bounded objective, or
  the explicit reason no eligible independent work remains.

Keep a concise current-frontier paragraph at the top of the existing closeout:
current outcome/binding and candidate, accepted evidence pointers, pending obligations,
active ownership/commands and next step. Link historical detail below instead of
requiring successors to rediscover the current state from chronological reports.
Put enduring invariants, architectural decisions and relevant failed approaches
in the durable continuation. Return pointers rather than logs, full diffs, copied
RFCs or older summaries. Preserve necessary rationale even when it needs more than
a few paragraphs; context savings never justify deleting a live constraint.

## Dispositions

| Result | Next action |
|---|---|
| milestone-complete | Check bound obligations/exits and explicit continuation; normally fresh at a substantial boundary, related reuse needs reason and renewed scope |
| continue-milestone | Same integrator, same current problem with renewed scope and a new dispatch identity; without `SendMessage`, a fresh integrator carrying the return's continuation pointers |
| human-pending | Keep exact ask/candidate open; eligible independent work needs checked continuation and safe release, otherwise present the ask |
| blocked | Account for effects; continue independent eligible work only after safe release, otherwise report blocker |
| cancelled | Stop and preserve; no automatic restart |
| pack-complete | Report verified closeout; no required criterion may remain pending |
| review-request | No-grandchildren fallback only: forward the selected native review assignment, wait, then resume this integrator to adjudicate; without `SendMessage`, a fresh integrator receives the review result reference |

## Completion and ownership

Match the result to its exact dispatch and current mandate before continuation.
Consume duplicate terminal events once. Native terminal/quiescent observations
must agree with the producer's account wherever exposed. A timeout means wait
again for the same child, not spawn its replacement. A partial turn can resume
without pretending it ended the milestone. Repeated unchanged partial returns
need an actionable diagnosis, not an indefinite resume loop.

Before replacing a writer, collect its available result and checkpoint/artifact
pointers through its current owner; inspect useful partial work before repeating it.
Then establish that it and its descendants stopped and
account for their edits/commands. Dirty unrelated files can remain; dirty owned
partial work must be explicitly transferred and inspected. Missing or contradictory
state goes back to the current integrator, or to a recovery assignment after prior
writers are inactive. Mutation is not blindly replayed after an uncertain exit.

A later user amendment supersedes an old recommendation. Forward it explicitly;
late results cannot undo it. Cancellation prevents the next dispatch. Preserve
partial work and required approvals. After a result is consumed and the agent
retired, avoid courtesy messages: a message can resume it. Any resume is an explicit
assignment with renewed authority, never an accidental acknowledgement.

## Runtime-limited review

When ordinary leaf spawning is unavailable, keep implementation and verification
local to the designated integrator. The coordinator never substitutes its cheaper
engineering route. Use native nested review where supported. With no grandchildren, the integrator
can request one explicit sibling reviewer through the coordinator after writers
are quiescent. It supplies role, exact candidate, current criteria/risk and evidence.
The coordinator forwards that request and its eventual result reference without
engineering judgment. Resume the same integrator to adjudicate. This branch is
not a general worker broker; unavailable required review stays unresolved.

If the interactive host exits, retain the memo/closeout and resume from live state
at the next user-authorized invocation. No automatic external restart is promised.

## Hosts without SendMessage

`SendMessage` denotes native resume capability here, not a required tool spelling.
Record the actual tool and behavior at bind time: some hosts separate messaging an
active child from resuming an idle child (for example `send_message` and
`followup_task`). An exposed message tool alone does not prove idle resume works.
Where no native resume is available, treat every continue-milestone and review-request as a fresh
`rfc-integrator` dispatch carrying the previous return's continuation pointers,
current candidate, evidence locations and a renewed dispatch identity. Every compact
return must therefore already be fresh-dispatch-ready: a successor reading only the
durable continuation and the return can take over without the retired context.
Before retiring an integrator on such a host, confirm its children and task commands
are quiescent; nothing can reach them afterwards, and orphaned children keep
spending. The coordinator still forwards pointers, never its own engineering summary.

## Optional data checks

`scripts/coordinator_handoff.py` validates the logical return and suggests a
control action from supplied native observations. It launches no models, stores
no queue or leases, and approves no engineering claim. The versioned shape lives
in `schemas/milestone-return-v2.schema.json`; the old v1 schema remains historical.

Call `continuation` with the current assignment and execution state covering the
producer, descendants and task commands. Supply already consumed identity tuples
from the existing private memo; JSON lists are accepted after reload. A result
with no consumption key is not consumed. Renew dispatch identity when explicitly
resuming the same integrator. New milestones use the explicit checked continuation
decision: normally a new native producer at a substantial boundary, or related reuse
with renewed scope. Historical v1 interpretation cannot bypass a plan-aware binding.
Supply `prior_partial` when comparing repeated partial returns. Identical candidate,
handoff, evidence, pending work and next-step observations require investigation;
the agent still judges whether superficially changed prose represents progress.

The qualified review-relay flag is an observation of available native behavior,
not a permission grant. A return with missing fields or unknown producer effects
requires clarification/reconciliation before further writers. Validate returned
candidate/evidence against the assigned consumer after recovery, preserving all
owned partial changes. No courtesy message follows retirement.
