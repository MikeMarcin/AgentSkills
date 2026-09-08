# Coordination handoff

A handoff preserves the current engineering frontier, not the story of the run.
Use the live board/RFCs and a chosen closeout as project truth. A small task-local
memo may hold the original user mandate/amendments and native IDs; it is not a
second backlog. Resolve all paths from the selected consumer, not the skill link.

## Assignment

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

Put enduring invariants, architectural decisions and relevant failed approaches
in the durable continuation. Return pointers rather than logs, full diffs, copied
RFCs or older summaries. Preserve necessary rationale even when it needs more than
a few paragraphs; context savings never justify deleting a live constraint.

## Dispositions

| Result | Next action |
|---|---|
| milestone-complete | When quiescent, fresh integrator for the next milestone |
| continue-milestone | Same integrator, same current problem with renewed scope |
| human-pending | Keep the exact ask/candidate open; fresh integrator for eligible independent work, otherwise present the ask |
| blocked | Account for effects; continue independent eligible work only after safe release, otherwise report blocker |
| cancelled | Stop and preserve; no automatic restart |
| pack-complete | Report verified closeout; no required criterion may remain pending |
| review-request | No-grandchildren fallback only: forward the selected native review assignment, wait, then resume this integrator to adjudicate |

## Completion and ownership

Match the result to its exact dispatch and current mandate before continuation.
Consume duplicate terminal events once. Native terminal/quiescent observations
must agree with the producer's account wherever exposed. A timeout means wait
again for the same child, not spawn its replacement. A partial turn can resume
without pretending it ended the milestone. Repeated unchanged partial returns
need an actionable diagnosis, not an indefinite resume loop.

Before replacing a writer, establish that it and its descendants stopped and
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

Use native nested review where supported. With no grandchildren, the integrator
can request one explicit sibling reviewer through the coordinator after writers
are quiescent. It supplies role, exact candidate, current criteria/risk and evidence.
The coordinator forwards that request and its eventual result reference without
engineering judgment. Resume the same integrator to adjudicate. This branch is
not a general worker broker; unavailable required review stays unresolved.

If the interactive host exits, retain the memo/closeout and resume from live state
at the next user-authorized invocation. No automatic external restart is promised.
