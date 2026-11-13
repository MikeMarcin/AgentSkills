---
schema: implement-rfc.card.v1
id: ASK-0133
title: Preserve Opus fallback for Fable deep roles
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"899c849","evidence":{"kind":"command","detail":"25 adapter tests pass, including two isolated consumers through a symlinked skill: only Claude deep-worker/critical-review routes change to Opus max/xhigh; baseline restoration reproduces original role bytes. Explicit narrower host capabilities and task override admission remain enforced."}},{"criterion":"AC2","outcome":"pass","revision":"899c849","evidence":{"kind":"artifact","path":"skills/implement-rfc/references/model-routing.md","detail":"Entrypoint routes quota refusals to the bounded owner-approved policy, distinguishing model quota from shared limits and other errors, preserving task floors and partial work, recording one fallback attempt and requiring actual host loading before dispatch."}},{"criterion":"AC3","outcome":"pass","revision":"899c849","evidence":{"kind":"command","detail":"13 MASK workflow tests pass, including real staged setup entrypoint loading the saved fallback profile. Portable-source validation, diff check and documentation gate pass (18 RFCs, 133 cards, zero violations)."}}]
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

Implemented in `899c849`. Source/configuration and disposable rendering/staging
are verified; no live quota refusal, serving observation, publication or consumer
upgrade was performed. Personal managed setup has no profile input and retains
that capability limit. The optional generic skill-creator quick validator could
not run with system Python because PyYAML is absent; the repository's portable
source validator passed. Closeout review runtime: local implementer self-review;
no independent review required or run.
