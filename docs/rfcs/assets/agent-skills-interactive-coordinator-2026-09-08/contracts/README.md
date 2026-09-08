# Compact native assignment and return

This is a logical data contract, not a launcher, persisted workflow engine or
second issue board. Existing native tool calls carry assignments and results.
The implementation may use labelled Markdown or a small JSON object; normalize
without an extra model call where useful. A schema-valid reply does not establish
native termination, engineering acceptance, or completion of the pack.

## Assignment

Bind **run ID, dispatch ID, native producer ID when assigned, current mandate
revision, selected consumer root/branch, engineering route, authorized scope,
milestone objective, immutable baseline/closeout pointers, and allowed effects**.
The coordinator retains exact user requirements and amendments separately from
engineering recommendations. A new milestone receives the current continuation;
it does not receive previous engineering transcripts or a recursively expanded
summary of every earlier milestone.

Use an existing run memo or task-local ignored location for native identities and
private user text. The live RFC/cards remain the acceptance and scheduling record.
Do not put credentials, full raw transcripts or private account usage into Git.
A session ID is an observation, not a write lease. Only the currently designated
integrator has the engineering assignment, and ordinary ownership rules still apply.

## Return

The illustrative JSON shape is documented by
[milestone-return.schema.json](milestone-return.schema.json). It provides one
boundary to test and adapt, not an obligation to create a new JSON-generating tool.
All values in [the example](../fixtures/return.example.json) are synthetic.

| Field | Meaning |
|---|---|
| run_id, dispatch_id, producer_id | Exact assignment identity; match against the native dispatch |
| mandate_revision | The revision of the user's instructions this result consumed |
| milestone | Current bounded integrated objective, not all future work |
| disposition | One of the dispositions defined below |
| summary | Usable result or exact partial state, not a transcript |
| candidate_revision | Actual observed Git revision, or null; never an invented hash |
| handoff_ref | Consumer-relative pointer to the current durable continuation, or null if none exists |
| ownership | quiescent, active or unknown; account for owned edits, children and commands |
| next_objective | A bounded recommendation inside the mandate, or null |
| required_pending | Specific human/native/engineering obligations still open |
| evidence_refs | Pointers to the existing criterion/check/candidate records |

The native result may also carry route observations and a review-request payload.
Keep those existing native observations rather than demand repeated self-reports.
Where the host supplies no field, report unknown instead of interpreting the
requested configuration as an observation.

## Disposition semantics

- **milestone-complete:** accepted automated boundary is recorded, all affected
  writers are accounted for; after quiescence, a fresh integrator takes the next
  eligible milestone. Pack-level pending obligations may remain.
- **continue-milestone:** retain the same integrator for its correction or partial
  invocation. Preserve existing side effects; this is not permission to replay work.
- **human-pending / blocked:** retain the exact unresolved work. After safe release,
  continue independent eligible work when available; otherwise return the actual ask.
- **cancelled:** preserve partial work and stop; no automatic resume or successor.
- **pack-complete:** all required selected acceptance is satisfied and linked,
  writers quiescent, no required pending item or next objective. Native completion
  and a plausible message are not substitutes for the integrator's actual evidence.
- **review-request:** qualified no-grandchildren path only; one explicit read-only
  sibling review, then resume the same integrator for judgment. See the handoff
  reference. This does not turn the coordinator into a general worker scheduler.

Duplicate delivery is consumed once for the exact dispatch. A late result for an
old mandate cannot authorize the next dispatch. An unknown or malformed result
returns to the same producer for clarification where safe; a producer that exited
uncertainly requires effects reconciliation before further writing. Bind candidate
and repository observations again after an interruption or external change.

The schema checks only structural implications such as a pack-complete result
having no pending work. Tests must separately exercise live ownership, stale
mandates, result/termination ordering and acceptance relevance.
