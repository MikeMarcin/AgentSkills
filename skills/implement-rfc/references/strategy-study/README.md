# Reusable multi-arm study kit

Status: preparation only; M4 has not run. This kit selects no product task, baseline,
budget, exact judge route or worktree location. Copy the [draft template](study.template.json)
only when the owner authorizes a future study. Default arms are Direct Astra Max,
Native Astra Ultra and the existing coordinated baseline. Planner-worker is optional;
its missing worker route never blocks an independently selected three-arm study.

## Freeze the study before implementation

1. Choose an authorized dependency-ready product task outside implement-rfc. Freeze
   its requirements, authored milestone plan, acceptance commands and held-out
   fixtures. Establish pre-existing failures at the exact source/tracker baselines.
   Give every arm the same task/plan; record how much solution detail is prescribed.
2. Fill every `common_inputs` reference with a durable versioned artifact. Record the
   exact skill commit and recipe revisions. References to environment and isolation
   must cover host/surface/build, toolchain/hardware, permissions, immutable caches,
   mutable outputs, instructions and known leakage limitations. No credential copy,
   global configuration edits or global-memory clearing is part of this protocol.
3. Specify a common practical resource ceiling, units, stop policy and one bounded
   external-feedback repair episode (or another symmetric policy). Record whether
   the ceiling is enforced or advisory, including overshoot. Declare approval,
   intervention and failure handling. No credit purchase/reset is implied.
4. Resolve selected recipes and freeze exact requested routes. For the coordinator
   baseline, snapshot its actual current coordinator, integrator and leaf routes;
   do not upgrade it for the study. For optional planner-worker, supply both exact
   routes before adding the arm. Freeze treatment selection before seeing candidates.
5. Only after run authorization, allocate distinct source worktrees from the same
   base and isolated outputs. Personal storage needs a paired tracker worktree from
   the same tracker base per arm; project storage records a null tracker worktree.
   Preallocate shared IDs through authorized tracker mechanisms before branching.
   Worktrees provide Git separation, not a security boundary. Exclude other arms'
   refs, code, transcripts and solution memory; disclose cooperative-only isolation.
6. Choose exact Astra and Fable judge routes and independent fresh judge sessions.
   Randomize implementation order before execution; prefer sequential runs on one
   host for the first block. Privately assign neutral candidate IDs and randomize
   each judge's presentation order, using the same candidate set. Retain the private
   map separately from quality packets. Balance orders across later blocks.

Populate `effective_configuration_reference` with inspected effective inputs and
their coverage/limitations. Actual serving observations remain null until observed.
No separate live qualification sessions are required: assess capability during the
authorized arm and preserve a capability blocker if it cannot proceed. Native
behavior remains unverified until then. Mark the manifest `frozen` only after its
references, authority and policy have been reviewed; validation alone grants none.

## Scoped configuration and validation

Use [host controls](../strategy-host-controls.md) for task-owned settings. The common
prompt plus exactly one [strategy addendum](prompts.md) defines each arm. Inspect all
known low-to-high configuration layers, inherited instructions and agent discovery
roots. Preserve global settings/authentication. Native must exclude custom RFC roles,
coordination instructions and child route overrides through supported isolation;
record ordinary native defaults, without forcing child routes or a child count.

Run these commands against the installed skill package, substituting task-owned paths:

```sh
python3 scripts/strategy_study.py --study references/strategy-study/study.template.json
python3 scripts/execution_strategy.py resolve --strategy direct-astra-max --json
python3 scripts/execution_strategy.py resolve --strategy native-astra-ultra --json
python3 scripts/strategy_host.py render --selection SELECTION.json
python3 scripts/strategy_host.py inspect --selection SELECTION.json --config SCOPED.toml
python3 scripts/strategy_study.py --study FROZEN-STUDY.json --require-frozen
python3 scripts/workflow_preflight.py --repo-root SOURCE --selection SELECTION.json
```

`render` prints TOML; it never writes settings or launches a model. Add every supplied
layer/instruction/root to `inspect`; use `--complete-inputs` only when that assertion
is justified. MASK readiness, requested settings, effective settings and observed
execution are distinct evidence. Frozen-manifest validation checks shape/catalog
consistency; verify the contents and identity of referenced artifacts separately.
The draft template deliberately fails `--require-frozen`.

## Freeze and judge candidates

Run each arm to its first-submission gate or declared stop boundary. Retain failed
attempts, compactions, replacement sessions, dispatch failures, human nudges and
deviations. Do not cherry-pick or relabel a takeover. Zero children is compliant for
native. Before freezing, account for writers and commands with supported lifecycle
evidence; a final response alone is insufficient. Bind a commit or complete base-bound
patch, dirty effects, pending obligations and evidence. Keep initial candidates immutable.

Run identical objective checks in disposable output roots. New reproducers must test
existing requirements and be applied consistently. Give each judge all candidates,
requirements, relevant surrounding source and objective results under neutral IDs.
Remove strategy/model names, branches, execution traces, usage and promotional text;
retain unredacted originals and audit evidence/bookkeeping separately. Do not hide
product defects while anonymizing. Each judge records per-candidate findings before
a comparison, with file/symbol evidence and reproducers where possible. Permit ties,
partial order and insufficient evidence. Freeze both verdicts before revealing usage
or the other verdict; resolve disagreement from evidence, not agreement alone.

## Repairs, accounting and readout

After all initial candidates and verdicts are frozen, give each arm only its own valid
finding/reproducer packet. Preserve original routing, topology and symmetric repair
budget. Never expose another solution. Freeze repaired candidates separately and
recheck affected criteria. A new requirement is an explicit common amendment, not a
hidden acceptance failure. Preserve first/final findings, usage and elapsed time.

Use existing `usage_capture.py` and `usage_report.py`; see [usage collection](../usage-collection.md).
Join outcomes to exact study/arm/attempt/session intervals with strategy, topology,
recipe revision, initial/repair phase, coverage, route ownership and deviations. A
trustworthy inclusive observation covers primary and children once; unknown aggregate
semantics remain separate, and missing child breakdown does not invent costs. Keep
arm work, shared review/validation and one-time setup in separate buckets. Record
start-to-gate elapsed time (not summed parallel durations), human time/count, resource
usage, resets/outages and unrelated account activity. Subscription windows are separate
measurements; tokens are not credits or charges.

```sh
python3 scripts/usage_report.py ARM-A.zip ARM-B.zip ARM-C.zip --compare --experiment FROZEN-STUDY.json --outcomes OUTCOMES.json --out REPORT
```

The manifest records provenance, not production acceptance. Accepted alternatives are
not multiple delivered production tasks. Use the [readout template](readout.md) to
separate acceptance, quality, adherence, observability and economics. A local matched
block cannot establish a universal topology effect: these treatments vary routing and
procedure too. Preserve alternatives until authorized integration/disposition; do not
force a release helper or mark the product delivered from experiment results alone.

Stop after kit validation for this delivery. No product task, experimental worktrees,
arm/judge runs or comparative verdict are created by these files.
