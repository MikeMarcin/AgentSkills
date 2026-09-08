# AgentSkills integrator prompt

Use `$implement-rfc` in the **AgentSkills repository**, not in SAMPLE_STUDIO, SampleReview,
SamplePlanner or ManageAgentSkills. Implement this pack in its bounded dependency
order. Read the repo AGENTS.md, current project context, RFC/issue contracts and
IMPORT.md before changes. Keep the retained pack immutable and use live imported
cards as the tracker.

Reconcile the current source with SOURCE_GROUNDING.md. The latest upload already
has `rfc-test-runner`, guarded `claim`/`finish` and `record_evidence.py`. Extend these
rather than recreating their ownership or semantic-acceptance logic. Preserve
settled RFCs and unrelated source/config edits. Reserve/remap live IDs through the
canonical main-branch allocator; capture the actual RFC_BASE_SHA before any feature
implementation. Never claim the pack's provisional IDs were reserved.

Deliver the bundled usage collector early. The installed interface must be:
`python3 .agents/skills/implement-rfc/scripts/usage.py`, defaulting to invocation cwd,
and the same command with `--mask-projects` selecting all local registered MASK
projects. Use public `mask project list --json`, with actual `root_identity` and
read-only behavior; no MASK internal-state access or new upstream feature is needed.
Keep content/scripts in the canonical skills/implement-rfc package and deployment
through explicit existing MASK operations.

Implement prescribed command batching before the general agent lifecycle adapter.
Keep a capable integrator at planned semantic gates and on genuine deviations.
Runner code handles exact control flow, not another persistent weak planner. Default
to direct work when delegation/runner overhead does not earn its cost. Preserve
all completed/partial reports, and never automatically resume a cancelled task or
repeat an uncertain mutation. Capability-test native drivers and preserve permission,
authentication and billing boundaries.

Implement the outcome/accounting readout without inventing precise subscription
spend. Keep requested/observed routes, role activity, tokens/cache, price-equivalent
estimates, account quotas and accepted task outcomes distinct. Apply lifecycle safety
to all experiment arms. Hold model routes fixed for the runner comparison; introduce
Astra-low-first as a separate explicit candidate and instruction changes separately.
Do not silently lower the reviewer because it shares a deep route class.

Use the payload as reviewed implementation input, not as a hidden import from the
retained archive. Run the focused supplied tests, then add the production tests
named by the owning cards. Small successful slices do not need a mandatory multi-agent
review matrix. Native claims, real account reads and live experiments require their
actual stated evidence. No additional quota is consumed merely to manufacture a
closeout; preserve blocked/inconclusive cases and continue independent work.

Do not update every registered project, publish/push repositories, replace global
agent settings, buy credits, redeem resets, add a daemon or switch to API billing.
Record each implemented slice, direct evidence, actual commits, remaining uncertainty
and the next dependency-ready card. Finish only after the existing integrator
acceptance contract is met; a process or test exit alone is not acceptance.
