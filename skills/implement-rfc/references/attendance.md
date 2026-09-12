# Attendance

Use the existing attended-review skill for explicit human acceptance and attended
preparation; use wizard for genuinely required guided manual steps. These are
conditional workflows, not mandatory stages for every implementation or UI change.

## Prepare a required decision

The integrator or its explicitly assigned owner prepares objective evidence and
the exact candidate/ask through the selected consumer's attended-review contract.
Expose ready items promptly, prepare quick items first, and let slow preparation
be interrupted. The coordinator presents the resulting page/ask without repeating
engineering preparation.

Before marking each candidate ready, run the shortest public path needed to make
its review scenario judgeable on that exact candidate. Record the entry point,
terminal result and evidence pointer beside the candidate. A digest identifies the
candidate but does not prove it can perform the scenario. Classify a failed
prerequisite against each candidate: keep affected candidates unready with the
concrete failure, while independent judgeable candidates can proceed. Do not build
successive review bundles while their relevant prerequisite remains red; repair it
and rerun the affected path first. Required human judgment remains pending.

Use local HTML and practical captured evidence. If a server is unavailable, use
the existing offline export/import path; server absence does not force a different
acceptance standard. Before ending the turn, arm the attended-review `wait` command
as a background watch whose exit re-invokes the driver: on Claude Code, `Monitor` with
`persistent: true`, since a plain background command is capped at ten minutes. A
hand-back or decision then reaches the coordinator without a human message. Save each
independent decision durably and preserve unanswered
items. A partial review or “finish and hand back” signal is not approval of the
remaining candidates.

**Prepared:** the user can inspect the actual candidate and provide the required
decision, with exact pending items and preparation limitations visible.

## Protect and consume

Respect the existing session's protected candidate inputs and shared-resource
conflicts. Unrelated work can continue. Stepping away preserves protections;
explicit resume-development releases conflicting resources and marks only affected
unanswered items for new preparation. Reconcile relevant input changes; unrelated
HEAD movement alone does not invalidate the candidate. These cooperative guards
cannot freeze arbitrary external editors.

Validate returned verdicts against the candidate they describe. The engineering
integrator incorporates partial decisions, verifies any correction and performs
the normal acceptance/board update. The coordinator preserves the human's actual
instructions; it does not synthesize missing verdicts or decide acceptance from
an empty queue remembered in conversation. Nor does it interpret them: it forwards
the session id, the event cursor and the candidate ids, and leaves what a rejection
means, which other candidates it touches and whether a remark is a defect or a
requirement change to the integrator. Interpreting a rejection to a root cause is a
named unresolved reasoning problem the integrator may delegate to `rfc-worker-deep`.

**Consumed:** received decisions remain attached to their actual candidates,
unanswered requirements stay pending, and conflicting protection is resolved
before further writes.

## Continue or hand back

Finish automated-complete work as human-pending through the existing bookkeeping
contract, keeping required card/RFC status open. Continue independent authorized
work. Return human-pending as the pack's stopping boundary only when no eligible
independent unattended work remains or the user explicitly stops the run.
