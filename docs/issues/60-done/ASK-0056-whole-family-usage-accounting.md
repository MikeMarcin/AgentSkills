---
schema: "implement-rfc.card.v1"
id: "ASK-0056"
title: "Measure all integrator generations without losing or double-counting usage"
status: "Done"
rfcs: ["RFC-ASK-0010"]
depends_on: ["ASK-0051"]
metadata: {"packet": "agent-skills-interactive-coordinator-2026-09-08", "provisional_id": false, "packet_key": "whole-family-usage-accounting", "milestone": "M2"}
acceptance: [{"criterion":"RFC-ASK-0010-AC12-source","outcome":"pass","revision":"90bc01c","evidence":{"kind":"observation","detail":"Owning response reconciliation and transitive lineage implemented in 5772548; corrections in 90bc01c. Usage suite 93 tests OK (3 platform/optional skips), final affected 51 tests OK; correction 29 tests OK plus 4 bounded/public checks. Synthetic public capture/report: four owning responses across root/two integrators/grandchild, input750 cached580 uncached170 output75 reasoning20 total825. Missing outcome null versus explicit empty zero. Independent native rfc-reviewer GPT6Astra high found conflicting cumulative and parent ancestry errors; both reproduced, fixed, and four focused review checks pass with no remaining blockers. No private audit was supplied; no native course or savings acceptance claimed."}}]
---

# ASK-0056: Measure all integrator generations without losing or double-counting usage

Governing RFC: [RFC-ASK-0010](../../rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md).

## Objective and owned paths

Add owning native response/thread usage surfaces identified by the supplied audit, retaining streaming/privacy/bounds. Reconcile alternate request, turn, thread and legacy counters conservatively; response identity plus owner determine duplicates. Follow transitive descendants across multiple integrator generations without assuming every role name is a task or every session is direct-root. Missing parent/coverage evidence remains unknown. Distinguish absent outcome input from an explicitly observed zero accepted outcomes. Keep the current controlled-experiment validator intact: this combined owner-directed rollout is not a one-factor experiment.

Owned paths:

- `skills/implement-rfc/scripts/usage_capture.py`
- `skills/implement-rfc/scripts/usage_accounting.py`
- `skills/implement-rfc/scripts/usage_outcomes.py`
- `skills/implement-rfc/scripts/usage_report.py`
- `skills/implement-rfc/tests/test_usage_capture.py`
- `skills/implement-rfc/tests/test_usage_accounting.py`
- `skills/implement-rfc/tests/test_usage_report.py`
- `skills/implement-rfc/references/usage-collection.md and routing-audit.md limited clarification`

## Acceptance

- Hand-calculated fixtures cover root, two integrator generations, grandchildren, resumes, duplicate/inclusive totals, conflicting counters and missing identities.
- Input/cache and output/reasoning subsets are not added twice; alternate totals are not independently billed.
- A missing accepted-work denominator is reported missing/unknown rather than zero productivity.
- Existing v1/v2 capture compatibility, read-only behavior, bounded scanning and private-output exclusions remain operative.

Criterion coverage: RFC-ASK-0010-AC12.

## Focused verification

- Focused existing parser/accounting/outcome/report suites, with sanitized new native-record fixtures.
- Reconcile supplied audit owning-record totals when available without copying private raw logs into the source repository.
- This card can proceed independently of the native course but does not certify either runtime or a saving.

## Run record

Not started. No native run, source implementation, reservation, accepted work or
measured saving is claimed by this packet. Claim the live card before source work,
preserve unrelated changes and commit only explicit owned paths.
