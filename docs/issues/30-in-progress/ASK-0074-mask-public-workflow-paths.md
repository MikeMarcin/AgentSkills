---
schema: "implement-rfc.card.v1"
id: "ASK-0074"
title: "Consume MASK-owned workflow paths without hardcoded lock locations"
status: "In Progress"
rfcs: ["RFC-ASK-0011"]
depends_on: []
---

# ASK-0074

September 12, 2026 owner-authorized direct deployment follow-up paired with
ManageAgentSkills MASK-0097. Baseline `266c364c140fd0412556265ee43df31a7811cf70`;
preserve existing renderer, README and test edits relocating the lock.

AC1: standalone renderer reads lock paths from MASK capabilities, retaining
canonical-first fallback and refusing unsupported MASK instead of guessing paths.
AC2: output-equivalent path-discovery changes declare tested prior lock hash pairs;
generated native roles remain byte-identical in two consumer contexts.
AC3: focused renderer/staging tests and portable source validation pass.

Scope: canonical renderer/helper, descriptor, focused tests, README and portable
manifest. No native role/routing changes, live consumer migration or push.
