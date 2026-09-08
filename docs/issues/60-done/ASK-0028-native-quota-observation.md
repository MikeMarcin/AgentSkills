---
schema: "implement-rfc.card.v1"
id: "ASK-0028"
title: "Integrate bounded native and manual account-quota observation"
status: "Done"
rfcs: ["RFC-ASK-0007"]
depends_on: ["ASK-0023"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "native-quota-observation"}
acceptance: [{"criterion":"RFC-ASK-0007-AC03 quota boundary","outcome":"pass","revision":"7f18fc4e7777fda5c4001d7a48ccd01919307e12","evidence":{"kind":"observation","detail":"Seven quota tests and one native macOS Codex read pass; exact protocol and private artifact recorded on card. Offline status-line/manual inputs preserve unknown freshness and opaque pools; no native Claude endpoint asserted."}}]
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

## Evidence

Seven quota fixtures pass (`python3 -B -m unittest discover -s skills/implement-rfc/tests -p test_usage_quota.py`), including exact three-method whitelist, interactive-auth refusal without a response, malformed protocol, sanitizer rebuilding, missing-versus-zero values and credit privacy.

Native macOS command: `python3 -B skills/implement-rfc/scripts/usage_quota.py codex --account-label codex-main --machine mac-main --out-dir ~/Library/Application\ Support/implement-rfc/usage/quota` exited 0 and saved `codex-20260908T032715-d5f0028a05.json`. Private account values remain only in the user-local artifact. No model turn or auth/reset mutation. Claude stdin/manual are offline input modes; no native Claude quota endpoint is claimed or hook installed.
