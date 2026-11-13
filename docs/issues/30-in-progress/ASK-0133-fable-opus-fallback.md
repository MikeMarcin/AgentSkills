---
schema: implement-rfc.card.v1
id: ASK-0133
title: Preserve Opus fallback for Fable deep roles
status: In Progress
rfcs: []
depends_on: []
---

The owner requested retaining Opus settings as a fallback when Fable's allowance
runs out before Opus. Keep Fable defaults and unrelated roles unchanged. Own the
routing profile, active routing guidance, focused adapter tests and portable manifest.
The critical review Opus alternative is a newly approved fallback, not a claim that
its immediate predecessor was Opus (that route was Fable 5.1 xhigh).

- AC1: A named fallback profile selects Claude Opus 5.5 max for `rfc-worker-deep`
  and Opus 5.5 xhigh for `rfc-reviewer-critical`, retaining other role routes.
- AC2: Guidance scopes fallback to model-specific Fable exhaustion with Opus
  allowance/capability available, preserves task floors and records the switch.
- AC3: Focused public rendering checks, portable validation and documentation
  checks pass. No live quota or installed-host behavior is claimed.

Baseline: `eecf7aba4bd3f5de414a408762305dc08a74a0d3`. Direct implementation;
unrelated staged art-skill work is preserved. Ordinary explicit-path commits are
used because claim/finish helpers require an empty shared index.
