# Design record

## Scope and provenance

Review hub pack, draft revision 1, authored 2026-10-30 from a design conversation
with the owner. No earlier originals.

## Decisions

| Decision | Requirement/acceptance | Status and actual answer | Rationale/consequences | Depends on / affected artifacts |
|---|---|---|---|---|
| D1 Hub hosting | RFC-DRAFT-0002 Deployment | Settled: "hosting the hub always-on over tailserve on my NAS" | One fixed address; laptops only send updates. An always-on service, so it stays outside the skill library. | D4; RFC-DRAFT-0002 |
| D2 Packaging | RFC-DRAFT-0002 Deployment, AC01 | Settled: "Docker" | Compose stack with Tailscale sidecar and ntfy. | RFC-DRAFT-0002 |
| D3 Push service | RFC-DRAFT-0002 Push, AC06–AC07 | Settled: push is fine, "anything safe and free"; self-hosted ntfy proposed and accepted without objection | Free, no accounts, stays on the tailnet. Firebase not reused. | D6; DRAFT-0003 |
| D4 Service code location | RFC-DRAFT-0002 Problem | **Open.** Proposed: a new small repository, or a home under ManageAgentSkills | AGENTS.md rules out daemons in this library and puts runtime code in ManageAgentSkills. | Blocks DRAFT-0002, DRAFT-0003 |
| D5 Hub is read-only for reviews | RFC-DRAFT-0001 Failure isolation; RFC-DRAFT-0002 AC05 | Proposed; owner said "got it" to the summary | Keeps attended-review's intake and handback contract unchanged. | Both RFCs |
| D6 iOS delivery | RFC-DRAFT-0002 Push | Deferred: "i dont care about iOS at this moment" | Enabling it later needs the ntfy.sh upstream relay (message IDs only). | RFC-DRAFT-0002 AC07 |
| D7 Desktop notifications | RFC-DRAFT-0002 page | Proposed: pinned hub page, no ntfy on computers | Owner said "got it" to the recommendation. | DRAFT-0002 |

## Open frontier and explicit deferrals

- D4 is the only material open question. It blocks the hub-service and hub-push
  milestones, not session-publication.
- Deferred: iOS push, Codex/cloud sessions outside the tailnet, showing
  prepared-but-unserved waits.
- Numeric defaults (5-minute heartbeat, 3-second timeout, 15-minute stale,
  24-hour stopped retention, 10-minute push quiet period) are proposals.

## Checks and confirmation

- **Structural validity:** `validate.py milestone-plan.json` from the installed
  implement-rfc kit reported "Structurally valid; references and semantic coverage
  unchecked." `MILESTONES.md` is its `--render` output.
- **Design readiness:** session-publication is design-ready. hub-service and
  hub-push wait on D4.
- **Confirmation:** the owner agreed to the summarized design in chat ("got it");
  no review of this written draft yet.
- **Execution eligibility:** not evaluated by drafting.

## Continuation

Answer D4, then optionally run `grill-rfc`, then import with `implement-rfc`.
