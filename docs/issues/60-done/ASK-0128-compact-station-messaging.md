---
schema: "implement-rfc.card.v1"
id: "ASK-0128"
title: "Compact station message passing"
status: "Done"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124"]
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
acceptance: [{"criterion":"RFC-ASK-0017-AC09","outcome":"pass","revision":"ee12b1e95a60d9997297df81e35451095f2c9f1e","evidence":{"kind":"artifact","detail":"Same 80 recorded aito-main-win remote-task turns (Codex rollout) plus the one Claude endpoint turn, tiktoken o200k_base; before committed first (83dc8c3). Station protocol 1716.6 -> 441.1 tokens per turn (-74.3%); all measured tokens 215204 -> 113163 (-47.4%); 89/89 re-expressed v2 requests parse with the skill's parser.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}},{"criterion":"RFC-ASK-0017-AC10","outcome":"pass","revision":"ee12b1e95a60d9997297df81e35451095f2c9f1e","evidence":{"kind":"artifact","detail":"Replayed task_id (authority-exceeded, unchanged code), project mismatch, authority exceeded, expired and station mismatch refuse for v1 and v2 on the delegated request route, and with the same reasons on the fenced-prompt route; no turn state written; also under the aito-prefixed station schema.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}},{"criterion":"RFC-ASK-0017-AC11","outcome":"pass","revision":"ee12b1e95a60d9997297df81e35451095f2c9f1e","evidence":{"kind":"artifact","detail":"Recorded-dispatcher v1 base64 request and v1 fenced YAML/JSON prompts admitted; v1 helper output byte-compatible; station file and lifecycle record byte-identical; station identity code untouched.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}}]
---

# Compact station message passing

Milestone M4 `compact-station-messaging` of RFC-ASK-0017, added by the owner
amendment of 2026-10-24: "the remote-station message format is token inefficient,
with boilerplate re-sent on every turn."

Boundary: `skills/remote-station` plus the implement-rfc dispatch rules that build
station prompts. No push, publication or credential change.

Acceptance: RFC-ASK-0017 AC09, AC10 and AC11.

1. **Measure first (AC09).** Measure per-turn tokens on recorded `aito-main-win`
   turns: the Codex thread history and the Claude session transcript. Record the
   method and keep the measurement as evidence before any design. After the change,
   measure the same turns again with the same method.
2. **Design from the measurement.** Change only what the measurement attributes
   cost to.
3. **Keep every refusal (AC10).** Replayed or reused `task_id`, project mismatch,
   authority exceeded and expired must still refuse for v1 and v2 envelopes.
4. **Keep compatibility (AC11).** v1 envelopes from existing dispatchers are still
   admitted during the compatibility release. Station identity rules do not change.

Hypotheses, unmeasured: the RFC's "Owner amendment 2026-10-24" section lists the
suspected causes and a likely shape. Neither is binding; the measurement decides.
