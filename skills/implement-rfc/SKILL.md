---
name: implement-rfc
description: Implement or resume RFCs and RFC packs through verified milestones; inspect progress, prepare required human review, or close out selected scope.
---

# Implement RFC

Keep the authorized pack moving. In the native interactive session, act as its
**coordinator**: preserve the user mandate, dispatch one milestone integrator,
wait, then continue from its compact result. Engineering belongs to that integrator.

An assigned **rfc-integrator** enters [Milestone integration](references/milestone-integration.md)
directly. Workers and reviewers follow their bounded assignment and role, rather
than this coordinator loop.

## 1. Bind the run

Resolve the consumer with `scripts/project_config.py --repo-root ROOT` using an
absolute root. Resolve helper paths from the selected installed skill asset root.
Keep the consumer root explicit on helper calls; a shared skill link never
selects its consumer. Read its `.mask/skill-config/implement-rfc/project.json` and
`project.md`, applicable instructions, and the user's selected scope. Preserve
unrelated work and existing approval boundaries.

Read [Coordination handoff](references/coordination-handoff.md) before dispatch or
resume. Bind the integrator's engineering route independently of the coordinator;
use canonical configuration and actual host settings, not model names in prose.
For setup, unavailable roles or model/effort conflicts, read the installed
`references/model-routing.md` and `references/runtime-compatibility.md`.

Before the first native dispatch, check the required native role set with
`scripts/workflow_preflight.py --repo-root ROOT --json`. It accepts only a MASK
program that implements `workflow_readiness_v1` and reports complete declared
readiness; `unsupported`, `incomplete` or `error` is a setup problem to report
(`mask ensure --project ROOT` deploys or sets up the roles), never permission to
spawn a default agent as an integrator.

For **status only**, inspect the scoped live queue/closeout with existing helpers
and report it; source, board state and agents remain unchanged. That branch ends
here. For **review only**, dispatch one native read-only reviewer against the
selected candidate and requested criteria, wait, then return findings with source
and board unchanged. That branch also ends here; repairs need authorized
engineering scope. For **closeout only**, give one integrator the existing evidence and missing
criteria; reuse unchanged passing checks.

For implementation, resume, attended preparation or closeout,
retain the user's exact requirements,
subsequent amendments, permitted side effects and stop conditions in a small run
memo or existing durable mandate. Detailed engineering intake belongs to the child.

For **usage collection or diagnosis**, read installed `references/usage-collection.md`
or `references/routing-audit.md` for the selected task. Run its read-only helper
without starting an engineering family or inventing an acceptance gate.

**Ready:** scope, selected root/branch, engineering route and prior active ownership
are unambiguous. A missing required context or unexplained writer is unresolved,
not an invitation to select another repository or overwrite work.

## 2. Dispatch one integrator

Before implementation dispatch, resolve plan state through
[Plan-first execution](references/milestone-plans.md). Preserve the current authored
group and exits; invalid/stale input remains unresolved. Status, review and usage-only
requests bypass implementation planning. Raw intake and necessary plan formation
belong to the first integrator's preparation-and-execution assignment.

Send the current mandate revision, objective, live RFC/card references, baseline
and current handoff references, authorized integration scope and return contract.
Include adopted plan/current milestone binding, or exact raw-plan bootstrap scope
until intake permits binding. Use a fresh native non-history-copying `rfc-integrator`
for the initial assignment; keep the coordinator
conversation and previous engineering transcripts out of its assignment.

One small fix needs one integrator, not a mandatory team. Existing model/permission
choices remain explicit; capability failure follows the installed fallback policy.
An owner-selected direct mode uses the engineering procedure and engineering route
in the main session, never an implicit low-cost implementation fallback.

**Dispatched:** record the exact native child identity and assignment. Only that
integrator owns the current engineering scope.

## 3. Wait for an actionable event

Use native completion or the suitable blocking wait. An open attended session is
a second event source: keep its `wait` armed as [Attendance](references/attendance.md)
describes, so a hand-back or decision re-invokes this loop without a human message.
While the child works, wait;
its transcript, repetitive status checks and speculative engineering are not the
coordinator's work. A wait timeout continues the same wait. Provide host-required
user updates without creating additional internal status traffic.

Forward a user amendment with a new mandate revision. Treat a native permission
prompt as a user decision, not something an agent can approve. On cancellation,
stop task-owned work where supported and preserve its partial state.

**Return ready:** a result or meaningful interruption is available; result receipt
alone does not establish that all writers have stopped.

## 4. Consume and continue

Apply the disposition/identity rules in [Coordination handoff](references/coordination-handoff.md).
Consume the compact result and current evidence pointers; the integrator already
owns engineering verification. Return missing engineering judgment to it.

Resume the same integrator for its current milestone's correction or partial
invocation. Check completion separately from explicit continuation intent. Normally
dispatch fresh at a substantial boundary; related small continuation may reuse context
with a reason and renewed scope. Keep required human decisions open and continue
independent authorized work. Present the exact human ask when that is the actual
remaining boundary. Stop on the user's stop condition or an unresolved blocker.

**Closed:** report usable behavior, actual verification/commits, remaining decisions
and cleanup from the integrator's truthful closeout. A short return, context limit,
empty memory or lower usage column never establishes pack completion.

For canonical source authoring or guarded adapter rendering, follow [Model routing](references/model-routing.md). Rendering does not change the current session or prove runtime loading.
