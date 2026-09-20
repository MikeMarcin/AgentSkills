# Strategy selection

Use `execution_strategy.py resolve --strategy NAME --json` for explicit natural-language
intent; names are helper selectors, not model-launch commands. `--preserved FILE`
resumes the exact resolved snapshot. `--preference NAME` supplies an explicitly
configured preference; no separate preference database is created. `--routing FILE`
supplies exact named route pairs. Explicit selection wins preserved selection, then
preference, then `coordinator-implementer-astra-max`. This owner-selected default uses
a Sol Low coordinator and one fresh Astra Max implementer for each milestone, with
no further model delegation. The earlier coordinator-integrator recipe remains an
explicit choice, and preserved runs keep their original selection. Keep routing selections
separate from topology and from `workflow_preflight.py --mode project|personal`.
The older execution-selection.v1 direct/runner mode still means command execution.

The catalog is trusted passive package data. A descriptor names ID/revision, compatible
common contract, package-relative entrypoint, requirement profile, owners, delegation
policy, required route slots and host support/qualification facts. Recipe IDs are not
a closed enum. Register future recipes and pass common conformance tests; no executable
plugin loading, downloaded code or external model scheduler is involved. Unknown IDs,
invalid paths, duplicate names and incompatible versions refuse selection.

The resolved snapshot names exactly the common contract and selected recipe instruction
paths plus their fingerprints. Save it beside existing continuation evidence; do not
load all recipes. `configuration_complete` describes routing inputs, never host loading.
Capability, configured route and observed serving remain distinct. Preflight applies
only the selected custom-role requirements while retaining MASK's core checks.

A topology switch during resume requires an explicit new segment after writer/effect
reconciliation, with prior pending obligations and deviation history retained. The
resolver only resolves inputs; it never authorizes or performs that transition.

The [study kit](strategy-study/README.md) is loaded only for explicit experiment
preparation or execution. Its v2 manifest validates selected arms without enumerating
topologies in board, acceptance or usage schemas. Historical experiment.v1 retains
its original one-dimension semantics. Neither format grants run authority.
