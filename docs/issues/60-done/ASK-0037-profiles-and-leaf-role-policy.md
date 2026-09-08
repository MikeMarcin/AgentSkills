---
schema: "implement-rfc.card.v1"
id: "ASK-0037"
title: "Add independent routing profiles, leaf defaults and explicit fallback policy"
status: "Done"
rfcs: ["RFC-ASK-0008"]
depends_on: ["ASK-0023", "ASK-0032"]
metadata: {"packet": "agent-skills-execution-usage", "provisional_id": false, "packet_key": "profiles-and-leaf-role-policy"}
acceptance: [{"criterion":"RFC-ASK-0008-AC01","outcome":"pass","revision":"3df7bd4ddc9e92181badcf25209259b2574f52f4","evidence":{"kind":"command","detail":"14 focused test_render_runtime_adapters.py tests pass against changes included in this finish; configuration behavior only, no live fallback/deployment claim."}},{"criterion":"RFC-ASK-0008-AC02","outcome":"pass","revision":"3df7bd4ddc9e92181badcf25209259b2574f52f4","evidence":{"kind":"command","detail":"14 focused test_render_runtime_adapters.py tests pass against changes included in this finish; configuration behavior only, no live fallback/deployment claim."}},{"criterion":"RFC-ASK-0008-AC03","outcome":"pass","revision":"3df7bd4ddc9e92181badcf25209259b2574f52f4","evidence":{"kind":"command","detail":"14 focused test_render_runtime_adapters.py tests pass against changes included in this finish; configuration behavior only, no live fallback/deployment claim."}}]
---

# ASK-0037: Add independent routing profiles, leaf defaults and explicit fallback policy

Governing RFCs: [RFC-ASK-0008](../../rfcs/RFC-ASK-0008-routing-profiles-and-portable-rollout.md).

## Objective and owned paths

Add baseline and opt-in Astra-low-first profiles, preserving explicit session choices. Keep routine worker versus deep worker, hold reviewers/test-runner/scout stable initially and decouple any shared route edits. Remove nested agent tooling from leaf roles where enforceable. Add requested/observed/fallback provenance and bounded approval policy without automatic quota purchases or resets. Do not reintroduce the removed verifier persona. Apply lifecycle safety equally to comparison arms.

Own only: `skills/implement-rfc/config/routing.json`; `skills/implement-rfc/config/routing-profiles.json`; `skills/implement-rfc/config/roles.json`; `skills/implement-rfc/scripts/render_runtime_adapters.py`; `skills/implement-rfc/tests/test_render_runtime_adapters.py`. Shared files require integrator scheduling; no unrelated consumer/config edits.

## Acceptance

- Changing the routine worker profile cannot silently lower review or overwrite native primary-session choices.
- Fallback records distinguish synthetic errors, unknown effort, unsupported effort, server availability and shared quota.

Criterion coverage: RFC-ASK-0008-AC01, RFC-ASK-0008-AC02, RFC-ASK-0008-AC03.

## Focused verification

Focused renderer/config tests assert role matrices, generated native fields, default leaf enforcement, profile digest and refusal on unsupported runtime capabilities. No live model bakeoff is needed to implement configuration.

## Run record

Implemented baseline/opt-in per-role profiles, capability-gated overrides, explicit-request precedence, requested/observed provenance, and bounded fallback receipt validation. All roles are leaves in generated Codex/Claude adapters. Primary native settings are untouched. Fallback receipts do not execute substitutions or infer available quota.

Verification: 14 renderer tests passed on native macOS, including public CLI candidate/refusal/local-selection/explicit-baseline behavior, unchanged review routes, native-settings preservation and bounded approval validation. No live model comparison or consumer deployment is claimed.
