# Bounded implementation change map

All production changes belong in AgentSkills unless explicit later scope says
otherwise. Repository paths below are from the attached September 8 dump.

| Current surface | Required change | Preserve |
|---|---|---|
| skills/implement-rfc/SKILL.md | Thin interactive coordinator entrypoint, explicit role branch, common intents and completion loop | Consumer selection, scope and human truthfulness |
| references/delegated-execution.md | Designated-integrator authority; serial context-isolation delegation; complete slice owners and useful concurrency | Standard/deep selection, independence, ownership and no routine review loop |
| references/milestone-integration.md (new) | Ordered engineering procedure and thin composed milestone selection | RFC/board acceptance and focused checks |
| references/coordination-handoff.md (new) | Compact current frontier, exact identities, dispositions, correction/replacement and cancellation | Existing closeout as authoritative project state |
| references/verification-and-closeout.md (new) | Co-located public-path evidence, integration check, review and terminal-state rules | Immutable RFC_BASE_SHA and all required evidence |
| references/attendance.md (new, or equivalent focused reference) | Attended prep, partial intake, protection/release and continuation pointer | Existing attended-review/wizard protocols |
| config/roles.json; schemas/roles.schema.json | Explicit new integrator, leaf restrictions, versioned typed delegation policy and reference loading | Existing role identities/addenda and leaf mutation boundaries |
| config/routing.json; schemas/routing.schema.json | Independent coordinator session route and integration class | Exact existing leaf routes and per-role explicit choice precedence |
| scripts/render_runtime_adapters.py | Role-aware tools, prompts, source digest, per-role route override and owned migration | Safe destinations, pins, two consumers, no shared-source rendering writes |
| config/codex-config.fragment.toml; agents/openai.yaml | Consistent optional local concurrency/entrypoint guidance; remove personal example path | No automatic global session, permission or speed changes |
| references/runtime-compatibility.md; model-routing.md | Correct current topology/entrypoints and remove conflicting active leaf/nesting/shim claims | Evidence versus configuration distinction; external runtime specifics dated separately |
| references/pack-lifecycle.md; bookkeeping.md | Authority means the designated integration owner, including authorized child integrator; local handoff is not an implied push | Main/lane distinctions, ID reservations, explicit path commits and helpers |
| references/role-adoption.md; routing-audit.md | New identity attribution, no hot switch, per-consumer activation and rollback | Historical role records, pins and modified-output refusals |
| scripts/usage_capture.py; usage_accounting.py | Owning response/thread records, transitive task-family identity and conservative reconciliation | Streaming/privacy/bounds; legacy data is fallback, not additional spend |
| scripts/usage_outcomes.py; usage_report.py | Missing outcome evidence differs from measured zero; all generations included | No semantic acceptance inferred from tokens or successful commands |
| tests/test_render_runtime_adapters.py; test_role_migration.py; test_standard_worker_target.py; test_unified_workflow.py; focused usage tests | New behavior plus preservation of historical seven-role projection | Retained original RFC assets remain immutable |
| README.md; AGENTS.md; CONTRIBUTING.md; local project.md; tracker rule READMEs | Reconcile active authority and entrypoint pointers only where contradictory | Consumer-specific facts, mandatory root reads and original history |
| generated/portable-manifest.json | Regenerate after final source changes | Loaded-host observation remains separate |

The supplied runtime-compatibility reference still describes utility nesting and
a generated Claude shim that conflict with newer active role/shared-link policy.
Resolve those relevant contradictions against current code and the new qualified
path; do not copy them into the new integrator. The old model-routing document's
main-only launcher rule must not send the new integrator through the companion
launcher: this pack uses native delegation, not the external runner.

No blanket rewrite of all references is required. Keep remote stations, Bedrock,
companion lanes and existing deterministic command helpers behind their existing
explicit-use branches. The packet does not reopen their implementation or
certify their old native evidence as new coordinator evidence.

The historical `test_standard_worker_target.py` compares the entire current role
set to a seven-role fixture. Update the live test to check the preserved legacy
projection plus a separate integrator assertion. Keep the historical checker and
fixture bytes intact under assets.
