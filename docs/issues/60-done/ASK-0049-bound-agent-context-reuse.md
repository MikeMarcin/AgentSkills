---
schema: "implement-rfc.card.v1"
id: "ASK-0049"
title: "Bound agent context reuse"
status: "Done"
rfcs: ["RFC-ASK-0009"]
depends_on: []
acceptance: [{"criterion":"Context reuse boundaries","outcome":"pass","revision":"0b6f786","evidence":{"kind":"observation","detail":"Independent ten-case tabletop distinguished related reuse, fresh independent assignments, safe ownership handoff and compact fresh packets. Two wording ambiguities resolved. 25 focused tests, skill validation, portable source validation and diff check passed; actual efficiency unmeasured."}}]
---

# Bound agent context reuse

Follow-up to RFC-ASK-0009 and ASK-0048. Preserve historical acceptance.
RFC_BASE_SHA: d3ebb84acd4af3a35f3b3a0f8a3f0c73609ecde8

Own skills/implement-rfc/SKILL.md, references/delegated-execution.md and
 generated/portable-manifest.json, plus this card. Clarify reuse for related
follow-ups versus fresh context for new bounded assignments and independent
review. Preserve routing, ownership, focused verification and no review loops.
No fixed token/turn quotas, runtime changes or consumer migration.

Acceptance: guidance covers same-slice repair, related next slice, unrelated
subsystem, role changes, correction recheck versus new review, and accumulated
irrelevant context. Independent tabletop decisions follow those boundaries;
portable and skill validation pass. Actual runtime efficiency remains unmeasured.

## Results

Implementation: 0b6f786. Independent context_reuse_cases subagent evaluated ten
scenarios using only revised skill instructions and case inputs. It selected reuse
for same-slice repair, related parser continuation, narrow reviewer correction and
relevant compacted context; fresh context for unrelated work, role changes, new
review boundaries and stale assumptions. It withheld successor write ownership
until predecessor completion/stop and inspection, and omitted parent history on
fresh spawn. Its two wording concerns were addressed by restricting successor
retirement/handoff language explicitly to fresh replacements.

11 unified-workflow tests and 14 runtime-adapter tests passed. Skill validator,
portable source validator and diff check passed. This is tabletop policy evidence;
no live runtime efficiency improvement or consumer reload is claimed.
