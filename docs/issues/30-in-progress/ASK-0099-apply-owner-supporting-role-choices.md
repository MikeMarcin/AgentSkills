---
schema: implement-rfc.card.v1
id: ASK-0099
title: Apply owner amendments to supporting role model choices
status: "In Progress"
rfcs: []
depends_on: []
metadata: {"source_baseline":"d1ef57c8b6817b0f6340f01ecafd7cea1b380239","execution_strategy":"direct","requested_on":"2026-10-03"}
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
