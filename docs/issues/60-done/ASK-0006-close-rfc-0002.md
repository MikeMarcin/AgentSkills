---
id: ASK-0006
title: Verify and close RFC-ASK-0002
status: Done
rfc: RFC-ASK-0002
depends_on: ["ASK-0005"]
closeout: true
---

# ASK-0006: Verify and close RFC-ASK-0002

## Objective and owned paths

Own the second skill closeout and its integration handoff.

## Bounded work

Confirm first/second-skill order, command correctness, safe recovery instructions and private-data boundaries; record the integrated AgentSkills commit for MASK dogfood.

## Acceptance

Every RFC-ASK-0002 acceptance criterion is evidenced; no global skill installation or MASK engine copy was introduced.

## Focused verification

Structure gate plus the narrow skill/example check.

## Run record

All four acceptance criteria verified at the shared skill/JSON subprocess boundary. Skill-creator and code simplification review: concise self-contained procedure with no copied runtime, reusable deterministic fixture verification outside payload. Source checks, documentation structure and explicit-path diff review PASS. No new paid model runtime or host-discovery claim. Both skills ready for named MASK dogfood. Commit: this Done move.

## Durable closeout anchor

RFC_BASE_SHA: ed19f5e6e62954f89f99e49a6d0fda9da3b1aef9

Planned cards: ASK-0005.

Cross-repository handoff commits: MASK d8ffdec; AgentSkills management skill 11d43f5; this closeout supplies MASK-0015.

Next slice: MASK-0015 named two-repository dogfood.

## Closeout checklist

| Acceptance | Direct check / command | Result | Commit |
|---|---|---|---|
| RFC-ASK-0002-AC01 | First import b7aa506; second skill package/quick validation | PASS | 11d43f5 |
| RFC-ASK-0002-AC02 | Procedure distinguishes incremental/set, preview guards and update scopes | PASS | 11d43f5 |
| RFC-ASK-0002-AC03 | Refusal/recovery/auth instructions preserve content and authority | PASS | 11d43f5 |
| RFC-ASK-0002-AC04 | Executable JSON fixture transcript; absent-program and host-load guidance | PASS | 11d43f5 |
