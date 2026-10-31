# Design record

## Scope and provenance

Review hub pack, draft revision 2, reviewed 2026-10-30 at the owner's request:
"Review this pack and make changes if it needs them."

The supplied, untracked revision 1 attributed its design to an earlier conversation.
Its 13 files are preserved byte-for-byte outside this working draft at
[review-hub-draft-v1](../../assets/review-hub-draft-v1/README.md). Earlier quotations
below are reported by that supplied record; this review did not independently read
the earlier conversation. New answers are identified separately.

Grounding used AgentSkills source at `64938f927093de1d3071e94d3372d2f96feedeb3`,
particularly the session/transport implementation linked from the publisher RFC,
the repository/consumer rules, and `milestone_plan.py`'s single-consumer binding.
Current official Tailscale and ntfy sources are linked beside the requirements
they inform in the service RFC. The original's claims that session records vanish
with a chat and that review sequence orders host changes were corrected.

## Decisions

| Decision | Requirement/acceptance | Status and actual answer | Rationale/consequences | Depends on / affected artifacts |
|---|---|---|---|---|
| D1 Hub hosting | [Service Deployment](rfcs/RFC-DRAFT-0002-review-hub-service.md#deployment) | Settled in supplied record: "hosting the hub always-on over tailserve on my NAS" | One stable index; source machines still host their own reviews. | D4; service RFC |
| D2 Packaging | [Service Deployment](rfcs/RFC-DRAFT-0002-review-hub-service.md#deployment), AC01 | Settled in supplied record: "Docker" | Compose with persistent hub/Tailscale state; ntfy is an optional profile. | Service/push cards |
| D3 Push service | [Push](rfcs/RFC-DRAFT-0002-review-hub-service.md#push), AC06–AC07 | Push permitted in supplied record: "anything safe and free". Self-hosted ntfy remains the proposed implementation; silence is not specific confirmation. | Requires local accounts; no external notification-provider account or relay is proposed. | D6; DRAFT-0003 |
| D4 Service code location | [Service ownership](rfcs/RFC-DRAFT-0002-review-hub-service.md#problem-and-grounded-current-behavior) | **Settled in this review:** owner selected "A new standalone repository (recommended)". | Publisher stays in AgentSkills. Separate consumer plans preserve the external prerequisite; no daemon is added to MASK. Repository name/path belongs to later authorized setup. | Both consumer plans, cards, entrypoint |
| D5 Hub is read-only for reviews | [Failure isolation](rfcs/RFC-DRAFT-0001-review-hub-session-publication.md#failure-isolation); service AC05 | Retained proposal; supplied record reports "got it" to a summary. | Listing/removal affects hub records only; review decisions and protections stay with the session. | Both RFCs |
| D6 iOS delivery | [Push](rfcs/RFC-DRAFT-0002-review-hub-service.md#push) | Explicitly deferred in supplied record: "i dont care about iOS at this moment". | No public upstream/FCM/Web Push forwarding in this version. | DRAFT-0003 |
| D7 Desktop notifications | [API and page](rfcs/RFC-DRAFT-0002-review-hub-service.md#api-and-page) | Retained proposal: pinned page, optional foreground browser notifications. Supplied record reports "got it" to the recommendation. | Browser permission remains a browser action; a closed tab has no background delivery guarantee. | DRAFT-0002 |
| D8 Hub access | [Access](rfcs/RFC-DRAFT-0002-review-hub-service.md#access), AC02 | **Settled 2026-10-30:** owner first chose "Include tagged (Recommended)", then revised: "i dont need auth right now other than being on the VPN". v1 authorizes any device that can reach the hub over the tailnet; no identity-header or app-capability checks. | Tailnet ACLs are the only access boundary, so any reachable device can read live review capability URLs. Tagged machines are included without extra grants. Per-user or capability checks are deferred. Owner added: "record that limitation honestly in the rep readme, but im the only one using it right now". | Service Access, AC02, AC08 |

## Review changes

- Defined disjoint candidate counts and states for partial handback, pause and idle;
  corrected publication coverage for readiness, withdrawal, restart and shutdown.
- Added durable publication ordering separate from review sequence, identical
  heartbeats and hub receipt-time freshness, so transport changes and skewed clocks
  cannot regress the index.
- Defined persistent opt-in/disable behavior, bounded asynchronous delivery and
  redacted diagnostics. The no-hub path preserves existing review behavior.
- Specified capability handling, proxy isolation, input/Origin validation and
  private page/log behavior; identified the tagged-device access choice above.
- Corrected storage failures to 5xx, made record removal/republication explicit,
  and separated the hub-only stack from optional push.
- Reconciled the push rule with its quiet period, persisted attempt throttling,
  and replaced an unachievable exactly-once claim with explicit best-effort
  behavior. Added real Android/NAS acceptance boundaries.
- Preserved milestone identities/grouping while making cross-repository import
  executable through consumer plans and an external publisher closeout dependency.

## Open frontier and explicit deferrals

- No material open questions remain. Deferred: per-user/app-capability
  authorization on the hub (D8).
- Deferred: iOS push, Codex/cloud sessions outside the tailnet, showing
  prepared-but-unserved waits.
- Numeric defaults (5-minute heartbeat, 3-second timeout, 15-minute stale,
  24-hour stopped visibility, 10-minute push quiet period) are retained proposals.
  Record validation uses a proposed 16 KiB bound. Internal code layout and the
  standalone repository's name are routine setup/implementation choices.

## Checks and confirmation

- **Structural validity:** the installed implement-rfc kit's
  `examples/milestone-plans/validate.py` passed for the final umbrella plan and both
  consumer plans; each reports "Structurally valid; references and semantic coverage
  unchecked." Their `MILESTONES.md` files are generated with `--render`. Separate
  draft checks passed for all 15 unique criterion labels and their plan coverage,
  five Backlog cards with one fully covered closeout per RFC, 56 local links/anchors,
  consumer-plan equivalence, canonical schema bytes, unchanged original snapshot
  and whitespace. `python3 -B scripts/verify_documentation.py --root
  /Users/jaeger/Documents/GitHub/AgentSkills` reported 17 RFCs, 128 cards and zero
  structural violations; that live-board check does not validate draft behavior.
  Live selector binding, semantic implementation coverage and runtime/NAS/phone
  acceptance remain unchecked. These are authoring checks, not implementation evidence.
- **Design readiness:** session-publication is defined independently. Hub-service
  and hub-push are design-ready since D8 was settled. Complete plan coverage means decomposition of the written
  criteria, not that an unresolved access choice has been answered.
- **Confirmation:** this session authorizes review/revision and explicitly settles
  D4. The supplied draft's earlier "got it" is not confirmation of revision 2;
  no blanket written-design confirmation or implementation authorization is claimed.
- **Execution eligibility:** not evaluated by drafting.

## Continuation

A later authorized implementation can start with
session-publication using the [entrypoint](IMPLEMENTATION_PROMPT.md). Preserve the
standalone service handoff and any outstanding NAS/phone acceptance; optional
`grill-rfc` is not an execution prerequisite.
