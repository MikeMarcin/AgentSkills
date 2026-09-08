# AgentSkills: bounded execution and actionable usage

**Deliverable:** an implementation-ready RFC pack for the **AgentSkills** repository,
plus a runnable project-aware collector seed to integrate into `implement-rfc`.
It does not change your repositories, install a runner, switch model routes, update
MASK consumers, or claim measured savings.

Start with [IMPLEMENTATION_PROMPT.md](IMPLEMENTATION_PROMPT.md) and
[IMPORT.md](IMPORT.md). The [implementation order](IMPLEMENTATION_ORDER.md) provides
staged checkpoints. [USAGE_TOOL.md](USAGE_TOOL.md) explains the working payload.

## Four new RFCs

| Provisional ID | Responsibility |
|---|---|
| RFC-ASK-0005 | Deterministic command/agent execution, durable report collection, bounded recovery, semantic integrator gates |
| RFC-ASK-0006 | Turnkey cwd-scoped capture, public MASK project selection, privacy, native packaging |
| RFC-ASK-0007 | Counter reconciliation, separate quota/credits, all-in task outcomes, offline reports |
| RFC-ASK-0008 | Low-first routing experiment, leaf roles, compact instructions, scoped rollout and rollback |

There are **21 provisional cards, ASK-0021–ASK-0041**, including exactly one closeout
per RFC. Their statuses are unstarted; only the dependency-free intake card is Ready.
The source snapshot's NEXT_ID is ASK-0021, but no live IDs have been reserved here.

## Intended installed collection experience

From a project's root after adoption:

```sh
python3 .agents/skills/implement-rfc/scripts/usage.py
python3 .agents/skills/implement-rfc/scripts/usage.py --mask-projects --days 30
```

A single automatically named ZIP is produced outside the shared skill directory.
The first command infers the project from the invocation working directory. The
second selects every **local** MASK project registration, preserving separate
worktrees and unavailable rows. It never means deploy/update all projects or collect
from remote machines. No model, account, upload or network operation runs during
ordinary capture. The optional native quota reader is a separate explicit command.

## Included now versus implementation work

Included now: four source-grounded RFCs, 21 bounded cards, acceptance mapping,
contracts/examples, import instructions, offline validation, and a runnable Python
collector with cwd/MASK selection and a quota-read companion. Tests and their actual
results are recorded in [VALIDATION.md](VALIDATION.md).

Still implementation work: the deterministic runner and native driver adapters,
production memory/index hardening, the reconciled reporting/outcome layer, generated
routing profiles, live MASK/native OS qualification, and the controlled experiment.
The payload is an integration seed, not a declaration that those RFCs are complete.

The design builds on the current `rfc-test-runner`, `issue_board.py`,
`record_evidence.py` and generated adapter policy; it does not resurrect the old
verifier role or add a second issue tracker. [SOURCE_GROUNDING.md](SOURCE_GROUNDING.md)
distinguishes uploaded source, retained measurements, new design and external
runtime references. No private raw measurement archive is included in this pack.
