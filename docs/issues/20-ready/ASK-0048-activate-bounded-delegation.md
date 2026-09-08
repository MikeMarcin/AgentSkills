---
schema: "implement-rfc.card.v1"
id: "ASK-0048"
title: "Activate bounded delegation in implement-rfc"
status: "Ready"
rfcs: ["RFC-ASK-0009"]
depends_on: []
---

# Activate bounded delegation in implement-rfc

Follow-up to RFC-ASK-0009; historical acceptance remains unchanged.
RFC_BASE_SHA: 9db4f05fe6e47b047823c718a0af3503a3223f04

The reported UX redesign session selected no subagents because optional routing
never explicitly activated delegation under a host policy requiring a skill request.

Own SKILL.md, references/delegated-execution.md and generated/portable-manifest.json
under skills/implement-rfc, plus this card. Make the skill explicitly request bounded
delegation when useful independent primary work can continue. Preserve small/coupled
local execution, runtime restrictions, leaf authority, standard/deep routing and
risk-based review. No consumer adapter or live task mutation.

Acceptance: entrypoint activates applicable delegation; realistic independent policy
cases distinguish useful parallel work, coupled work and runtime prohibitions;
portable manifest and documentation validation pass. Record observed limits here.
