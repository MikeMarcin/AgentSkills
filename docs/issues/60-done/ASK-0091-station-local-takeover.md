---
schema: "implement-rfc.card.v1"
id: "ASK-0091"
title: "Managed station local takeover"
status: "Done"
rfcs: []
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"station-local-takeover","path":"docs/rfcs/plans/station-local-takeover/milestone-plan.json"}}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"bf257dabf48dde0527dc8e92e012095d71e7126c","evidence":{"kind":"observation","detail":"Replacement prompts and exact bounded helper/inspection argv work; unbound second linked consumer permits ordinary mutations while managed/retired endpoints defer writes."}},{"criterion":"AC2","outcome":"pass","revision":"bf257dabf48dde0527dc8e92e012095d71e7126c","evidence":{"kind":"observation","detail":"Real disposable POSIX supervisor stop and dirty/checkpoint preservation, durable retired fencing, OS transfer serialization, interrupted receipt recovery and repeat idempotence pass."}},{"criterion":"AC3","outcome":"pass","revision":"bf257dabf48dde0527dc8e92e012095d71e7126c","evidence":{"kind":"observation","detail":"Project/branch/base/envelope/lease regression checks and fresh linked-consumer launcher composition pass; existing owner RPC adapter has exact task/cwd and complete terminal checks; unsupported hosts are manual and native unqualified status is recorded."}},{"criterion":"AC4","outcome":"pass","revision":"bf257dabf48dde0527dc8e92e012095d71e7126c","evidence":{"kind":"observation","detail":"28 control, 63 launcher, 39 Codex, 12 guard (2 optional schema skips), 4 lease cases passed; two consumer links, source manifest, raw exact-Git package validation and docs gates pass."}},{"criterion":"AC5","outcome":"pass","revision":"bf257dabf48dde0527dc8e92e012095d71e7126c","evidence":{"kind":"observation","detail":"MASK 2fcd627c6ef89b0bd0d722a8802adc0ec30485fa accepted in 189b218e8f1eaea74467203e4a8ddb2b3ad5f3f4; focused public normal import, approval-consent and integrity checks pass, actual consumer readiness restored with installed source/cache hashes unchanged."}}]
---

# Managed station local takeover

Owner-authorized on 2026-09-29; assignment `/root/station_takeover`, mandate
`station-local-takeover-20260929-v2`, selected coordinator-implementer strategy.
RFC_BASE_SHA: acc7ac56a588e5b818ee99a117b6e917b07f1930 (pre-source baseline).
No existing RFC is amended or closed by this bounded follow-up.

Keep hooks for explicitly managed stations. Accept replacement prompts and bounded
inspection/recovery while restricting mutations until the prior writer is quiescent.
Provide JSON status and `takeover --mode local --stop-previous`, with scoped runtime
stop evidence and supervisor proof. A human instruction to resume here authorizes
that operation without another confirmation; the hook itself never parses prose as
mutation authority. Retain history, dirty edits, checkpoints, obligations and strategy.
Fence retired endpoints, serialize competing transfers, recover interruptions and
preserve launcher fresh contexts. Metadata age is never inactivity evidence. No
automatic old-chat archive, arbitrary sidecar PID kill, live runtime launch, station
stop, deployment, push or MASK changes.

## Acceptance

AC1: Ordinary unbound local chats remain unrestricted; managed replacement prompts and exact bounded inspection/recovery commands work while writes require quiescence.

AC2: JSON status and authorized local takeover preserve history, dirty edits, checkpoints, obligations and strategy, fence retired endpoints durably, serialize transfers and recover interrupted operations.

AC3: Project, branch, endpoint, envelope and supervisor lease guards remain enforced; fresh launcher contexts work and unsupported stop adapters provide precise manual recovery without guessing inactivity.

AC4: Focused fixture-process and mocked-runtime tests cover paused, crashed, active, stale, repeated, concurrent, interrupted, dirty and retired writes; two linked consumer compositions, package and documentation gates pass.

[Plan](../../rfcs/plans/station-local-takeover/milestone-plan.json).
[Durable checkpoint](../../development/station-takeover.md).


AC5: The owner amendment is integrated at the exact MASK candidate: normal imports preserve bounded interpreter caches, strict source verification and original preview consent; actual consumer readiness is restored without deleting caches.

Owner amendment v2 (2026-09-29) adds bounded MASK bytecode verification without
changing the station obligations or execution strategy. MASK-0127 is Done at
189b218e8f1eaea74467203e4a8ddb2b3ad5f3f4; engineering candidate
2fcd627c6ef89b0bd0d722a8802adc0ec30485fa. Its public import,
preview-consent, artifact/recovery and actual readiness observations supply AC5.
