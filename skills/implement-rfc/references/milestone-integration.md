# Milestone integration

You are the designated engineering integrator for the supplied scope. Own RFC
interpretation, local design, slice coordination, evidence judgment, scoped commits
and permitted board updates. The coordinator owns user scope and continuation;
its low-cost route is not your engineering route. Leaf results remain inputs to
your judgment. Read [Coordination handoff](coordination-handoff.md) for return and
ownership transfer, not for the outer coordinator loop.

## 1. Orient from live state

Resolve the assigned root and read consumer rules, applicable instructions, selected
RFC/cards and current continuation. Inspect branch/status and the scoped queue;
use `scripts/issue_board.py` with explicit root and the selected RFC/area/card
filters. Read relevant material, not the entire board or previous transcript.

Recover immutable RFC_BASE_SHA and planned cards from each applicable closeout.
On resume, reconcile current code/commits, prior evidence, active owners and user
amendments. Preserve unrelated edits. For pack import, ID allocation/renumbering
or worktree integration, read installed `references/pack-lifecycle.md`. Reserve
on main and commit returned reservation paths before use. Main authority is not
granted to a lane by this role name.

**Ready:** selected scope, acceptance, baseline, current state and exclusive authority
are established. Missing context or an uncertain prior mutation remains unresolved.

## 2. Select a usable milestone

Within the authorized dependency order, choose the next bounded capability that
can be demonstrated through its relevant public path. Name its criteria, owned
paths, shared interfaces and required native/human evidence on the existing live
records. A milestone may group several cards; retain their separate acceptance.
Choose a meaningful working result rather than a fixed card count or timer.

For lifecycle/shared-state work, exercise a thin composed path before expanding
all dependent components. A small fix may complete in one milestone. A broad pack
is not one milestone merely because its cards share a theme. If the work cannot
reach its boundary, narrow the next attempt explicitly while preserving unfinished
criteria; splitting work never marks those criteria satisfied.

Read installed `references/bookkeeping.md` before claim/finish. Claim eligible
cards before source edits; explicitly promote dependency-ready Backlog work through
the supported board contract when needed. Helpers do not make that judgment.

**Selected:** a demonstrable result, relevant constraints, owned work and credible
verification strategy are recorded. This is not a new user-approval checkpoint.

## 3. Assign complete slices

Keep small, tightly coupled or immediately blocking work yourself. When useful
independent work exists, this skill requests bounded subagents through
[Delegated execution](delegated-execution.md). Assign implementation, local diagnosis,
required code/test/doc changes and focused checks to one complete-slice owner.
Default to standard engineering; select deep for a named unresolved reasoning
problem, not simply a sensitive domain.

Use the smallest useful team. Add a worker only for an independent result with
exclusive paths and compatible interfaces. Do distinct integration work yourself
or wait; consume the owner's result rather than repeat its investigation. A
scout replaces a bounded scan, and a separate test runner is optional, not a stage
all work must pass through. Use ordinary deterministic tools for trivial mechanics.

**Assigned:** every active slice has one owner, refreshed candidate/path scope,
criteria, neighboring interfaces and a concise result contract.

## 4. Implement and verify the changed behavior

Slice owners implement and diagnose within their scope, add relevant tests/docs,
and inspect touched code for straightforward simplification. Communicate an
actionable blocker, required interface/ownership change or completed result.
Use selected command batches when useful; retain full logs outside conversations
and inspect only the failing/relevant portions. Native waits and host-required
updates replace internal polling chatter. Escalate a material scope or architecture
change through the coordinator for the user's decision; routine in-scope repairs
remain automatic.

For **prescribed command batches**, read installed `references/bounded-execution.md`
before selecting the existing runner. For an actual **remote envelope or station**,
read `references/remote-routing.md`; an explicitly selected **Codex companion lane**
uses `references/codex-lanes.md`. These optional paths retain their current authority
and are not substitutes for the native interactive coordinator.

For acceptance checks, read [Verification and closeout](verification-and-closeout.md).
Run focused checks and the direct selected path when helper tests could pass while
the criterion remained false. Reuse evidence whose relevant inputs are unchanged;
rerun checks affected by a fix. Repeated failure without new information calls for
a reproducer and explicit unresolved question before another attempt.

**Candidate-ready:** changed paths, actual candidate/working state, checks, findings
and remaining obligations are explicit. Candidate-ready is not semantic acceptance
and a runtime/context limit is not completion.

## 5. Integrate and accept

Consume bounded diffs/results, reconcile interfaces and close missing/invalidated
checks. Run one justified integration-focused pass at the meaningful combined
boundary. Obtain independent review when requested or warranted, using the
verification reference. Adjudicate findings against existing acceptance, rather
than expanding the requirements or taking a vote.

Record actual criterion/outcome/revision/evidence and finish eligible cards through
the existing explicit-path bookkeeping contract. Required human decisions follow
[Attendance](attendance.md); required unavailable native checks remain open. Continue
independent unattended work. At an RFC's final boundary, apply the closeout rules
against its original baseline; do not redo full-pack closeout at every milestone.

**Accepted milestone:** the stated integrated behavior is demonstrated, no known
critical in-scope failure remains, and live statuses agree with evidence. Otherwise
return its actual partial, blocked or human-pending disposition.

## 6. Hand off the current frontier

Complete/stop task-owned writers and commands, account for their effects and consume
their results. Clean consumed temporary resources; preserve necessary handoffs and
artifacts. Write the current continuation on the selected live closeout: usable
behavior, current candidate, relevant invariants/rationale, unresolved obligations
and next bounded milestone. Other closeouts link to that record rather than copy it.

Return the compact fields in [Coordination handoff](coordination-handoff.md).
Within this milestone, corrections can resume your context. At the next milestone,
yield to a fresh integrator. Follow the user's stop instruction; local handoff
never implies push, publication or another checkout.

**Transferred:** the result identifies the current mandate/candidate, effects and
next step, and no unaccounted writer can collide with the successor.
