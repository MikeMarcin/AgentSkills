# Strict planner-worker recipe

The primary planner owns scope, design decisions, work orders, acceptance, evidence
judgment and permitted tracker/commit bookkeeping under the shared engineering
contract. One worker owns every product edit, including tests, documentation and
corrections. The planner may inspect source, run deterministic checks and review the
diff. It sends concrete findings back to the worker; it does not patch the product.

Resolve `planner-cheaper-worker-strict` with `--routing FILE` supplying the exact
worker provider/model/effort. The preset requests Astra Max for the planner but leaves
the worker unset. “Cheaper” is a caller choice, not a cost guarantee or a model alias.
No worker default, upgrade or fallback is inferred. Generic `planner-worker` requires
both routes. The initial host adapter supports Codex; other hosts remain unsupported.

Use the selected MASK profile with no custom RFC roles. Spawn the built-in worker
with the exact requested route on a surface that supports explicit model and effort;
check that an inherited custom agent does not override that role. If the requested
route or control is unavailable, stop at an explicit capability blocker. Do not
substitute the coordinated RFC roles. [Host controls](../strategy-host-controls.md)
provides scoped settings; configured settings do not prove actual serving.

Give the worker the bound milestone, relevant common contract, exact owned paths,
requirements and checks, plus this policy: implement and correct only the assigned
product; preserve other edits; do not delegate, change routes, accept cards or commit;
return changed paths, checks, evidence and unresolved concerns. Keep at most one
worker active. Reuse that worker for iterative feedback after each reviewed result.
Confirm quiescence before replacing it and record why context was replaced. Do not
add scout, tester or reviewer children. Independent external acceptance remains a
pending obligation when required by the consumer; a worker return cannot waive it.

Use primary `milestone_checkpoint.py bind/check` for plan and acceptance continuity.
Retain actual host lifecycle, work-order, result and review evidence beside that
checkpoint. `planner_worker.py check` checks an optional bounded observation record
for concurrency, routing and edit ownership; it does not launch a worker, certify
host enforcement or decide product acceptance. Unknown observations stay unknown.

A planner takeover, additional child, recursive delegation or route change is a
visible deviation under the original selection. Quiesce writers, preserve evidence
and obtain authority for a changed strategy when it changes the mandate. Never label
a planner fix as worker output or silently relabel an expensive/noncompliant attempt.
