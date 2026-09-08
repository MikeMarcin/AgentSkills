---
schema: "implement-rfc.card.v1"
id: "ASK-0028"
title: "Integrate bounded native and manual account-quota observation"
status: "Backlog"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": true, "packet_key": "native-quota-observation"}
---

# ASK-0028: Integrate bounded native and manual account-quota observation

Governing RFCs: [RFC-ASK-0007](../../rfcs/RFC-ASK-0007-usage-accounting-outcomes-and-experiments.md).

## Objective and owned paths

Review the bundled quota seed. Preserve a separate opt-in native read command and safe manual/status-line inputs. Validate complete allowed protocol exchange, account aliases, pool IDs, reset intervals, provider/capture freshness and actual returned units. Document composition rather than overwriting an existing Claude status line. A future account/usage endpoint requires capability verification, not assumption. Offline collection does not initiate account reads.

Own only: `skills/implement-rfc/scripts/usage_quota.py`; `skills/implement-rfc/tests/test_usage_quota.py`; `skills/implement-rfc/references/usage-collection.md`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- No thread/turn creation, permission grants, reset consumption, purchases, external token servicing or silent authentication repair.
- Unavailable quota is explicitly unknown; no undocumented pool-to-model mapping.

Criterion coverage: RFC-ASK-0007-AC03.

## Focused verification

Fake app-server protocol tests must assert the exact whitelist of sent methods and refusal of interactive requests. Add one authorized native read per supported provider mode without running model tasks.

## Run record

Not started. No native result, implementation revision, quota saving or semantic acceptance is asserted. Claim this live card before editing; preserve unrelated changes and commit explicit paths.
