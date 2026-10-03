---
schema: implement-rfc.card.v1
id: ASK-0100
title: Raise mechanical Luna effort for reliable failure reporting
status: "Done"
rfcs: []
depends_on: []
metadata: {"source_baseline":"eafcc1fe59ce48d2ad6e05d3c52dbb3b7f7c5352","execution_strategy":"direct","requested_on":"2026-10-03"}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"01e94a2cf225ee2793d3e4b1d27b5219b10350ec","evidence":{"kind":"command","detail":"35 native adapter/fake-companion tests pass. Both mechanical roles request and report GPT-6 Luna xhigh without downgrade while preserving authority and sandbox boundaries."}},{"criterion":"AC2","outcome":"pass","revision":"01e94a2cf225ee2793d3e4b1d27b5219b10350ec","evidence":{"kind":"artifact","detail":"Selection evidence records the owner-selected Luna xhigh cost tradeoff, dated effort-specific Luna/Sonnet aggregate and terminal results and unmeasured local error-reporting quality."}},{"criterion":"AC3","outcome":"pass","revision":"01e94a2cf225ee2793d3e4b1d27b5219b10350ec","evidence":{"kind":"command","detail":"Portable manifest, skill frontmatter, diff and documentation checks pass. Baseline comparison confirms only mechanical effort changes in routing; other routes and role/strategy sources are unchanged."}}]
---

The owner questioned Luna low's ability to handle test or tool errors, asked for
a Luna configuration comparable to Sonnet 5.5 low, and selected GPT-6 Luna xhigh
for the Codex utility/test-runner default after reviewing the effort-specific
benchmark tradeoff. Apply that exact choice; retain Sonnet 5.5 low on Claude.

Own the mechanical Codex route in `skills/implement-rfc/config/routing.json`,
its active route table and selection evidence, existing native/companion route
tests and the source manifest. Record aggregate intelligence, terminal performance
and benchmark cost separately. Similar overall scores do not establish equivalent
error handling. Preserve all other routes, authority, permissions and strategies.
No subagents, live consumers, model trials, publication or Git push.

Acceptance:

- AC1: Canonical configuration and native/companion requests select Luna xhigh
  for both mechanical roles, preserving exact banners and existing boundaries.
- AC2: Dated evidence records the owner-selected cost tradeoff, effort-specific
  comparison with Sonnet low and the unmeasured failure-reporting limitation.
- AC3: Focused adapter/companion tests, source-manifest validation, skill validation
  and documentation checks pass; other routes and role contracts match baseline.

Use existing tests in temporary consumers with the fake companion. Preserve
historical accepted cards and route evidence. No local model-quality trial is
claimed by deterministic route verification.

## Verified result, 2026-10-03

Source revision: `01e94a2cf225ee2793d3e4b1d27b5219b10350ec`.
The [active routes](../../../skills/implement-rfc/references/model-routing.md)
now request GPT-6 Luna xhigh for both Codex mechanical roles. The
[selection evidence](../../../skills/implement-rfc/references/model-selection-evidence.md)
records the effort-specific benchmark comparison and the owner's explicit cost
preference. Claude retains Sonnet 5.5 low.

| Criterion | Evidence and result | Revision |
|---|---|---|
| AC1 | Independent native expectations verify exact requested model/effort, banners, mutation/delegation limits and addenda. Fake-companion execution verifies xhigh arguments, effective banner and requested/effective launch records without a downgrade for either mechanical role. PASS. | `01e94a2` |
| AC2 | Reviewed official OpenAI model/subagent guidance and Artificial Analysis's full Luna/Sonnet effort comparison. Evidence separates aggregate intelligence, terminal performance, benchmark task cost and local quality limits; the owner selected Luna xhigh after receiving the tradeoff. PASS. | `01e94a2` |
| AC3 | `PYTHONPATH=skills/implement-rfc/tests:skills/implement-rfc/scripts python3 -B -m unittest test_render_runtime_adapters test_codex_lane`: 35 tests PASS. Source-manifest validation, skill frontmatter validation, `git diff --check` and documentation gate PASS (15 RFCs/101 cards, no structural violations). | `01e94a2` |

Baseline comparison against `eafcc1f` confirms the only routing change is Codex
mechanical effort from low to xhigh. All other routes, role instructions,
permissions, entrypoint and strategy sources are unchanged. Six scoped skill
files changed, including the regenerated manifest. Existing mechanical contracts
already require exact commands, exit status, failed/skipped/incomplete outcomes,
diagnostic evidence and escalation of unsupplied decisions; their authority was
not expanded.

No live consumer, installed model session or admitted assignment changed. Model
failure-reporting quality and realized savings remain unmeasured. The two broader
strategy-test defects recorded in ASK-0097 remain outside scope; this focused
verification does not claim the entire repository suite passes.

Closeout review runtime: primary-session self-review; direct execution, no subagents.
