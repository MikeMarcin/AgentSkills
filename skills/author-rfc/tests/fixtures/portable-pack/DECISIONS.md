# Design record: ledger export

## Scope and provenance

Unadopted fixture ChatGPT draft revision 1, with proposed requirements linked in the RFC.
Two authored groups: single-file, then batch/resume. This record is supplied fixture
history, not acceptance of the skill implementation or confirmation of future changes.

## Decisions

| Decision | Requirement/acceptance | Status and actual answer | Rationale/consequences |
|---|---|---|---|
| D1 Destination ownership | RFC AC01 | Settled: refuse existing destinations | Preserve local operator data; applies to cards and first milestone |
| D2 Bounded files | RFC AC02 | Settled: at most 100 data rows and 10 MiB | Makes recovery inspectable; applies to batch milestone |
| D3 Job timeout | RFC AC01/AC02 | Settled: 30 seconds | Bound operator wait |
| D4 Resume identity | RFC AC03 | Settled: refuse mismatched input | Avoid duplicate/wrong output |

## Readiness and coverage

Defined behavior; internal module/class design explicitly deferred. Structural/live
selector checks have not run. No execution eligibility assessment or implementation
evidence. Review coverage is supplied drafting only.

## Shared understanding and confirmation

No recorded user confirmation. Recommendations or new revisions need explicit answers.

## Continuation

Validate the exported plan/schema; review the requested focus; retain authored grouping.
