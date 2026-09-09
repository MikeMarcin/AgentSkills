# Delegated execution

The milestone integrator owns engineering decisions and authorized integration.
It may delegate complete bounded slices; existing workers, scouts, utilities,
test runners and reviewers remain leaves. The outer coordinator's serial dispatch
is justified by context isolation even when it has no useful parallel work.

## Select work and role

| Work | Owner |
|---|---|
| Small or tightly coupled engineering | Milestone integrator |
| Exact read-only lookup or mechanical inventory | rfc-utility, only when a separate agent materially helps |
| Bounded semantic investigation | rfc-scout |
| Normal engineering, diagnosis, refactoring or local design | rfc-worker |
| Named unresolved difficult reasoning problem | rfc-worker-deep |
| Prescribed commands benefiting from separate output ownership | rfc-test-runner |
| Requested or risk-selected independent review | rfc-reviewer or rfc-reviewer-critical |

Canonical configuration supplies routes. Standard engineering needs bounded scope,
constraints, ownership and credible verification; the worker may develop the local
approach. Existing patterns help but are not required. Difficulty selects effort;
consequence selects safeguards and review. Known-hard work may start deep without
first wasting a standard attempt. Follow existing explicit fallback authority for
unavailable routes rather than silently changing models or accounts.

## Complete assignment

Provide the exact selected consumer/candidate, role/routing reason, live criterion
references, exclusive allowed paths, constraints and shared interfaces, required
focused verification and compact result. Refresh that scope for each assignment;
previous write ownership does not silently carry forward. Implementation includes
local diagnosis, relevant tests/docs and focused checks until candidate-ready.

For workers, preserve the routing receipt `Routing: standard | Reason: ...` or
`Routing: deep | Reason: <named unresolved problem>`. Missing historical routing
is unknown. Retain the native role banner as requested configuration; observed
model/effort is a separate fact when telemetry exposes it.

The integrator consumes the result rather than repeats the worker's scan. It can
inspect material conclusions and integration seams without reproducing every
command. Parallel read-only agents own different questions, not duplicate prompts
for voting. Add concurrency for independently useful results, not idle capacity.

**Assigned:** one responsible owner, acceptance/candidate/path scope and result
boundary are explicit; unexplained overlapping edits stop the assignment.

## Leaf boundaries and results

Workers modify only owned source/test/doc paths. The integrator claims/finishes
cards, allocates IDs, stages/commits and adjudicates acceptance. Workers may
prepare an authorized human-review artifact within their scope; they report its
pending verdict and continue unattended work. They do not invent a human gate.

Test runners execute exactly selected commands and write only assigned disposable
build/test output. They report failures, skips and incomplete runs; diagnosis,
extra tests and acceptance decisions return to the integrator. Scouts investigate
bounded questions. Utility performs supplied mechanical work, not architecture.

A worker returns Status, Changed files, Verification, Remaining risks and
Uncertainties, with actual candidate/working state and evidence pointers. A reviewer
returns Status, Blocking findings, Non-blocking findings and Material limitations.
Use compact relevant content; logs and detailed output stay at the named evidence
locations. An actionable blocker, interface change or completion warrants a message;
status polling that cannot change a decision does not.

## Context lifetime

Reuse a leaf for a correction, narrow recheck or closely related continuation when
its context, role and route still fit. Refresh ownership/candidate on continuation.
Start fresh for unrelated acceptance work, a different role or a new independent
review. An implementer cannot become its own independent reviewer. Check the
specific correction to a finding without restarting a full-candidate review loop.

At an integrator's completed milestone, collect or stop its children before ownership
transfer. Do not retain a permanent worker/reviewer pool across the whole pack.
For a replacement, account for the outgoing writer's effects first. A new card alone
is not a leaf reset; a new milestone deliberately is an integrator reset.

## Review and optional runtimes

Before commissioning review, read [Verification and closeout](verification-and-closeout.md).
Native same-driver delegation is the ordinary path. Read installed
`references/codex-lanes.md` or `references/remote-routing.md` only for an explicitly
selected existing companion/station surface. This coordinator design does not
require or authorize external agent invocation. Use existing bounded command
helpers only for already-selected supported mechanics; they do not decide acceptance.

## Native assignment details

Use role-prefixed task names and fresh non-history-copying contexts where supported.
Every assignment names Role and purpose; Repository root and branch/candidate;
Question or acceptance claims; Allowed paths or roots; Explicit non-goals;
Applicable instructions; Exact commands or evidence; Requested result. Add the
routing reason for an implementation owner. Read required consumer instructions;
never infer permission from an inherited summary. Keep the selected root explicit.

Runtime model and effort selections follow [Model routing](model-routing.md).
Use the existing startup identity banner and repeat the routing reason in the final
Status where configured; an unavailable serving observation remains unknown.
Only the designated integrator adjudicates acceptance and owns board/commit work.
Return permission requests to the coordinator/user; do not approve them in a child.
If a child cannot surface an approval, preserve its prepared work and return a
reviewable patch or command to the integrator. Never wait indefinitely on an
invisible approval or bypass the sandbox.
