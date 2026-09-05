---
schema: "implement-rfc.card.v1"
id: "ASK-0007"
title: "Refresh implement-rfc from SampleReview"
status: "Done"
rfcs: ["RFC-ASK-0001"]
depends_on: ["ASK-0004"]
---

# ASK-0007: Refresh implement-rfc from SampleReview

## Objective and owned paths

Import the latest local SampleReview skill changes into the canonical shared
skill while retaining the completed shared-consumer adaptation. Own
`skills/implement-rfc/**`, `docs/development/skill-provenance.md`, and this card.
SampleReview is read-only; consumer configuration and MASK state are outside
this refresh.

## Bounded work and acceptance

- Import SRV commit `c609655bc615e79e8e17eefc198c89861de0d90f`'s validated
  issue-board commands, schema, reference and tests.
- Preserve explicit external consumer resolution, fixture isolation, and safe
  adapter rendering. Keep inherited SRV facts only in the historical example.
- Verify changed board/config helpers, source validation and the public CLI
  through shared links with two different disposable consumers.
- Record provenance and regenerate only the portable source manifest.

## Verification and run record

RFC_BASE_SHA: d7d316700bcded466f02f8f20e5c473f47cf3ed1

This follow-up preserves the original RFC closeout and its historical evidence.
Implementation commit: `285ad90`.

Imported the upstream delta and retained shared selection and rendering. The new
schema preserves existing external dependency references and platform labels;
queue output surfaces external handoffs for the agent to verify. Consumer move
policy remains opt-in, so this card uses the existing repository lifecycle.

All 76 focused tests passed without skips:

| Command (from AgentSkills; `PYTHONDONTWRITEBYTECODE=1`) | Result |
|---|---|
| `python3 -m unittest discover -s skills/implement-rfc/tests -p test_issue_board.py` | 32 passed, including two distinct consumers through shared links, nested invocation, move isolation, missing/mismatched context refusal, and unchanged source bytes |
| `python3 -m unittest discover -s skills/implement-rfc/tests -p test_audit_board.py` | 18 passed |
| `python3 -m unittest discover -s skills/implement-rfc/tests -p test_project_config.py` | 15 passed |
| `python3 -m unittest discover -s skills/implement-rfc/tests -p test_render_runtime_adapters.py` | 11 passed |

Additional verification:

- `python3 -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only`: passed after source manifest regeneration.
- Skill-creator `quick_validate.py skills/implement-rfc`: passed.
- MASK `skill validate implement-rfc --json`: valid, no issues.
- Public `issue_board.py --repo-root <consumer> validate --json`: AgentSkills
  (7 cards) and ManageAgentSkills (18 cards) passed. MASK's audit also reported
  no violations or warnings.
- `python3 -B scripts/verify_documentation.py --root .` and `git diff --check`:
  passed at closeout.

Reviewed the changed code using code-simplifier guidance; no broad rewrite was
needed. Temporary fixtures were removed by their context managers. No optional
remote orchestration, live adapter regeneration or host UI-loading check ran.
No remaining work in this refresh; original RFC closeout evidence is unchanged.
