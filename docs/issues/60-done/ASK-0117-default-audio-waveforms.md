---
schema: "implement-rfc.card.v1"
id: "ASK-0117"
title: "Prepare audio waveform previews by default"
status: "Done"
rfcs: []
depends_on: []
priority: "P2"
metadata: {"milestone_plan":{"id":"attended-review-waveforms","path":"docs/rfcs/plans/attended-review-waveforms/milestone-plan.json"},"related_rfc":"RFC-ASK-0016","related_issues":["ASK-0116"]}
acceptance: [{"criterion":"ASK-0117-WAVE01","outcome":"pass","revision":"a1d3d6cf7af83e51a4111b144673940f01cb4cd2","evidence":{"kind":"artifact","detail":"Decisive audio branch reaches one authoritative default and useful-spectrogram/fallback rule before preparation; self-tabletop and pruning review recorded.","path":"docs/rfcs/plans/attended-review-waveforms/verification.md"}},{"criterion":"ASK-0117-WAVE02","outcome":"pass","revision":"a1d3d6cf7af83e51a4111b144673940f01cb4cd2","evidence":{"kind":"artifact","detail":"Six exact-PCM SVGs numerically verified and rendered; two isolated symlinked consumers retain previews through public preparation/offline HTML, with no inferred answers.","path":"docs/rfcs/plans/attended-review-waveforms/verification.md"}},{"criterion":"ASK-0117-WAVE03","outcome":"pass","revision":"a1d3d6cf7af83e51a4111b144673940f01cb4cd2","evidence":{"kind":"artifact","detail":"Focused structure/portable-source checks and self-review pass; historical acceptance/limits preserved, fixtures released and removed, commands quiescent.","path":"docs/rfcs/plans/attended-review-waveforms/verification.md"}}]
---

# Prepare audio waveform previews by default

Owner mandate, 2026-10-19: "Can we improve that", following the request that agents
normally include waveform previews and useful spectrograms without a separate ask.
Mandate revision: `waveform-guidance-source-v1`. Assignment `/root/waveform_guidance`:
one non-delegating implementer on AgentSkills main. Baseline:
`d72887ef3d79d71e4029d3146b85bdf55fbbf55d`.

Source-only scope: attended-review entrypoint, session contract, portable mixed-audio
example and these scoped records. Related completed design:
[RFC-ASK-0016](../../rfcs/RFC-ASK-0016-attended-review-audio-questions.md); completed
navigation follow-up: [ASK-0116](ASK-0116-answer-adjacent-review-navigation.md).
Their historical acceptance and native qualification limits remain unchanged.
No deployment, consumer migration, Faraday/profile/session changes, dependency
installation, general media pipeline, runtime feature or push.

Acceptance:

- **WAVE01:** Before audio-session preparation, the main skill reaches one
  authoritative rule: include an exact-clip waveform by default without a user ask;
  add a spectrogram when frequency/noise/pitch/timbre judgment benefits. Reuse
  trustworthy exact-clip images or prepare them with existing available tools.
  Unavailable tooling/previews have a concise visible limitation while playable
  review proceeds. Preserve original audio, inline portability, identity binding
  and dependency/approval boundaries.
- **WAVE02:** The portable example demonstrates default waveforms from each exact
  valid synthetic clip with standard-library preparation. The intentionally broken
  clip explains its missing preview. Focused public preparation/offline composition
  and direct image/sample checks verify the example without claiming new native
  qualification or human approval.
- **WAVE03:** Focused documentation/pruning checks and self-review pass; exact
  candidate, local commits, pending limits and quiescent task ownership are durable.
