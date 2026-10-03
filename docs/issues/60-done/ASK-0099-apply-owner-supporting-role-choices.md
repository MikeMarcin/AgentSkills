---
schema: implement-rfc.card.v1
id: ASK-0099
title: Apply owner amendments to supporting role model choices
status: "Done"
rfcs: []
depends_on: []
metadata: {"source_baseline":"d1ef57c8b6817b0f6340f01ecafd7cea1b380239","execution_strategy":"direct","requested_on":"2026-10-03"}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"d3b01ddcd7a154c56dfdec0f9d22926746ecf32b","evidence":{"kind":"command","detail":"49 focused native/companion/historical/migration tests pass. Independent route matrix matches the owner choices; baseline comparison preserves protected routes and all other skill sources."}},{"criterion":"AC2","outcome":"pass","revision":"d3b01ddcd7a154c56dfdec0f9d22926746ecf32b","evidence":{"kind":"artifact","detail":"Active model-routing, model-selection-evidence and codex-lanes references distinguish owner choices from public facts and requested native max from effective companion xhigh."}},{"criterion":"AC3","outcome":"pass","revision":"d3b01ddcd7a154c56dfdec0f9d22926746ecf32b","evidence":{"kind":"command","detail":"Portable source manifest, skill frontmatter, diff and documentation checks pass. No live deployment or model-quality trial is claimed; prior broader strategy test failures are recorded."}}]
---

The owner amended the supporting-role selection after ASK-0097. Apply Sol 6.1
high for the older Codex integrator; Sol 6.1 xhigh / Opus 5.5 xhigh for ordinary
review; retain Astra xhigh and restore Fable 5.1 xhigh for critical review;
Sol 6.1 max / Opus 5.5 max for infrequent deep work; and Sonnet 5.5 low for
Claude utility and test-runner work. Other selected routes remain unchanged.

Own `skills/implement-rfc/config/routing.json`, active model/routing/companion
references, existing native and companion route tests, and the source manifest.
Keep public benchmark and cost facts distinct from these owner preferences.
Native deep adapters request max; the existing companion fallback reports
requested max and effective xhigh. Preserve coordinator session routes,
implementation routes, roles, permissions, strategy recipes and unrelated edits.
No subagents, live deployment, model trials, publication or Git push.

Acceptance:

- AC1: Canonical routes and generated native requests match the owner's exact
  model/effort choices; unchanged routes and authority boundaries are preserved.
- AC2: Active references explain the amended choices without recasting public
  evidence, and distinguish native max from the companion's reported fallback.
- AC3: Focused routing tests, source-manifest validation, skill validation and
  documentation checks pass; verification and deployment limits are recorded.

Use existing tests with temporary consumers and the fake companion. Historical
cards, retained packets and accepted route evidence retain their original meaning.

## Verified result, 2026-10-03

Source revision: `d3b01ddcd7a154c56dfdec0f9d22926746ecf32b`.
The [active route table](../../../skills/implement-rfc/references/model-routing.md)
and [selection rationale](../../../skills/implement-rfc/references/model-selection-evidence.md)
record the owner's amendments. The native deep adapters request max; the
companion's existing max-to-xhigh fallback is retained and explicitly documented.

| Criterion | Evidence and result | Revision |
|---|---|---|
| AC1 | The independent expected route matrix verifies all nine native roles, exact model/effort arguments, banners, mutation/delegation limits and addenda. Baseline comparison confirms the coordinator/implementation routes, unchanged supporting choices, entrypoint, authority, strategy declarations and recipes are preserved. PASS. | `d3b01dd` |
| AC2 | Active references distinguish owner preferences from dated benchmark/pricing facts, keep Fable for critical-review diversity, reserve max for rare deep work and state Sonnet's higher token price than Haiku. Companion tests verify requested max/effective xhigh, the effective banner, diagnostic and launch record. PASS. | `d3b01dd` |
| AC3 | `PYTHONPATH=skills/implement-rfc/tests:skills/implement-rfc/scripts python3 -B -m unittest test_render_runtime_adapters test_codex_lane test_standard_worker_target test_role_migration`: 49 tests PASS. Source-manifest validation, skill frontmatter validation, `git diff --check` and the repository documentation gate PASS (15 RFCs/99 cards, no structural violations). | `d3b01dd` |

Only seven scoped skill files differ from baseline `d1ef57c`. The source manifest
was regenerated after the final reference edit. No live consumer, installed
client, admitted assignment or model session changed. Native serving and local
model quality remain unmeasured. The previous real-MASK fixture check was not
repeated for this mapping-only amendment. The two previously reproduced strategy
test defects recorded in ASK-0097 remain outside scope; this is a focused routing
verification, not a claim that every repository test passes.

Closeout review runtime: primary-session self-review; direct execution, no subagents.
