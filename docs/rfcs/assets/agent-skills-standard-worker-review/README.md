# AgentSkills: standard worker and independent review routing

**One new RFC and four implementation cards.** This is a small, owner-directed
follow-up to the delivered execution/usage work, not a new orchestration system
or a benchmark project. Target: the canonical AgentSkills repository.

## Approved target

| Role | Route class | Codex | Claude |
|---|---|---|---|
| `rfc-worker` — default implementation | `standard` | Astra **low** | Opus 5 **xhigh** |
| `rfc-worker-deep` — explicit difficult problem | `deep` | Astra **high** | Fable 5.1 **high** |
| `rfc-reviewer` — normal independent review | `review` | Astra **medium** | Fable 5.1 **medium** |
| `rfc-critical-reviewer` — named material risk | `critical` | Astra **xhigh** | Fable 5.1 **high** |

Utility/test-runner and scout routes stay unchanged. Primary-session models,
permissions, processing speed, concurrency and turn limits are unchanged. The old
`rfc-worker-routine` is retired from new dispatch; historical records remain readable.

The standard worker handles normal features, diagnosis, refactoring, multi-file
implementation, local design decisions and approved architectural changes. A
copyable pattern is helpful, not mandatory. **Work is bounded; capability is not
restricted to trivial tasks.** Difficulty selects worker effort. Consequence selects
safeguards and review. Most ordinary implementation should start standard, without
an arbitrary percentage quota or a forced low-then-high sequence.

[Read the RFC](docs/rfcs/RFC-ASK-0009-standard-worker-and-independent-review-routing.md).
[Start implementation](IMPLEMENTATION_PROMPT.md).
[Import safely](IMPORT.md).
[Source basis and qualifications](SOURCE_BASIS.md).

## Plan

| Provisional card | Work | Dependency |
|---|---|---|
| ASK-0043 | Default-worker contract, role names, independent routes | None |
| ASK-0044 | Safe adapter/addenda migration and historical audit compatibility | ASK-0043 |
| ASK-0045 | Focused regression checks, generated source manifest, release guidance | ASK-0044 |
| ASK-0046 | One integration/closeout pass | ASK-0045 |

Only ASK-0043 is Ready. IDs reflect the supplied snapshot (NEXT_ID ASK-0043,
eight live RFCs), not a reservation in the live repository. Reserve and remap before
import. Do not overwrite a live NEXT_ID or amend settled RFCs to hide the change.

## Included acceptance fixtures

`fixtures/target-routing.json` gives exact target assignments, routes, mutations and
limits. It is an assertion fixture, **not** a drop-in replacement for routing.json.
`fixtures/selection-cases.json` specifies dispatch-policy examples and negative cases;
it is not measured model behavior or a requirement to build an automatic classifier.

`python3 tools/validate_pack.py` checks packet structure and integrity offline.
After implementation, `python3 tools/check_target_routes.py --repo-root /path/to/AgentSkills`
checks the effective canonical configuration and rendered in-memory prompts. It does
not deploy, launch models, inspect credentials, or edit a consumer. Its checks do not
replace migration regressions or semantic review.

## Deliberate boundaries

This pack adopts the requested policy without making a quality/cost win a release
gate. Existing capture/reporting stays in place, including cwd inference and
`--mask-projects`. Do not rebuild it, add a recurring audit, or run duplicate reviews
on every task. Preserve original instructions and evidence; compare routing revisions
when future data arrives. Fable allowance pressure and the model-capability comparison
are the owner's rationale, not measurements established by this pack.

There is no automatic deployment to every MASK-registered project, no pin bypass,
no model fallback, no automatic CLI upgrade, credit purchase, reset, or Git push.
Changes in a shared development-link source can affect consumers immediately; use
a separate authoring worktree and activate deliberately after verification.

The archive supplies specifications and offline checkers, not the implemented change.
See [VALIDATION.md](VALIDATION.md) for what was actually exercised.
