# implement-rfc: selectable execution strategies and real-code experiments

Revision 2 — September 18, 2026. Proposed design and experiment materials, not an applied implementation or a trial result.

This packet supersedes the two-choice design in `implement-rfc-direct-trial.zip`. The earlier packet remains historical. The correction is substantive: Ultra is an intended native-orchestration treatment, not an unsuitable direct control to postpone.

## Decision

Preserve one RFC engineering, bookkeeping and acceptance contract. Select an execution strategy independently of that contract. Compare these three initial treatments:

| Treatment | Execution topology | Routing |
|---|---|---|
| Direct Astra Max | Primary engineers directly; no model delegation | Explicit Astra Max primary |
| Native Astra Ultra | Native system decides whether/how to delegate; no custom RFC orchestration | Explicit Astra Ultra primary; native child selection/defaults |
| Coordinator/integrator baseline | Existing interactive coordinator, milestone integrators and permitted leaves | Frozen existing route configuration |

Register strong-planner/cheaper-worker as another experimental strategy. It is not mandatory in every trial; add it to an experiment before any implementation starts, after selecting its exact routes and budget. Future topologies use the same integration seam and acceptance/measurement contract.

The native primary still satisfies project requirements, permissions and bookkeeping. It does not receive a custom coordinator wrapped around its work. Direct engineering does not manufacture handoffs to itself. All strategies remain in normal authorized native sessions; this design adds no external agent supervisor.

## Contents

- [Implementation brief](IMPLEMENTATION_BRIEF.md): common contract, strategy seam, source change map and regression requirements.
- [Multi-arm trial](MULTI_ARM_TRIAL.md): matched task blocks, isolation, blind evaluation and usage accounting.
- [Run and judge prompts](PROMPTS.md): one shared implementation prompt and topology-specific addenda.
- [Milestones](MILESTONES.md): offline-authored delivery order and exits.
- [Readout template](READOUT_TEMPLATE.md): quality, adherence, usage and uncertainty, reported separately.
- [Example study](examples/study.template.json): three initial treatment selections plus an available fourth; intentionally unlaunchable draft.
- [Example strategy registration](examples/strategy-registration.template.json): a proposed passive descriptor, not a shipped schema or executable plugin.
- [Source notes](SOURCE_NOTES.md): source observations, public references and limits.

Natural-language usage should be enough: “Use implement-rfc with native execution and Astra Ultra,” or “Use the planner-worker strategy with these exact routes.” Names such as `direct-astra-max` are proposed preset labels, not existing CLI flags.

Complete and qualify the implementation seam before running the measured product task. Neither this packet nor its example JSON launches agents, changes source, allocates issue IDs, spends a trial budget or certifies a winner.
