# Dependency order and useful checkpoints

This is the immutable intake plan, not a second live issue board. The imported
cards become authoritative. There are no calendar deadlines or invented durations.

| Checkpoint | Cards | Usable outcome |
|---|---|---|
| Intake | ASK-0021 | Live mapped IDs, true baseline, current source reconciliation |
| Capture first | ASK-0022–0025; close ASK-0026 | Cwd and MASK-wide one-command captures with native-qualified packaging |
| Command runner | ASK-0031 | Already-planned checks execute without model-by-model stepping |
| Durable delivery | ASK-0032–0035; close ASK-0036 | Owned native attempts, durable reports, bounded recovery and semantic handoff |
| Accounting | ASK-0027–0029; close ASK-0030 | Conservative request/resource ledger, quota snapshots and task-outcome readout |
| Policy and context | ASK-0037–0038 | Leaf roles, independent profiles and compact task context; candidate still explicit |
| Scoped deployment | ASK-0039 | Actual selected consumer artifacts, opt-in controls and rollback |
| Evaluate, then decide | ASK-0040; close ASK-0041 | Separate comparisons and owner promotion/retention/rollback decision |

After intake, command batching can proceed independently of capture work. Counter
reconciliation and native quota work start after the capture schema is established.
Codex and Claude adapters can proceed independently once the durable lifecycle
contract is stable. Concurrent ownership of common helpers/renderer/config must be
coordinated; naming two cards independent does not make their files independent.

Lifecycle safety improvements apply to all arms. The first live comparison changes
only orchestration, with route/review/acceptance held constant. The next changes only
the ordinary worker route. Instruction comparisons use identified pre/post content
without changing either topology or selected model. Candidate support can ship before
promotion; an inconclusive result retains the baseline.

Do not wait for a complete dashboard before repairing lost reports, and do not run
a costly full benchmark just to finish the reporting tool. Native/environment waits
remain explicit on their owning cards while independent work proceeds. All planned
closed-state evidence must be real, not inferred from fixtures.
