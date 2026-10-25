---
schema: "implement-rfc.card.v1"
id: "ASK-0127"
title: "Close the remote-station skill RFC"
status: "Backlog"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124", "ASK-0125", "ASK-0126", "ASK-0128"]
closeout_for: ["RFC-ASK-0017"]
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
---

# Close the remote-station skill RFC

RFC_BASE_SHA: 3ad85990719baec8f38544006a110c7a91bf6ab2

Planned local cards: ASK-0124 (M1), ASK-0125 (M2), ASK-0126 (M3), ASK-0128 (M4,
owner amendment 2026-10-24), ASK-0127 (closeout).

Closeout review runtime: M1 local implementer self-review (claude-opus-5-5); no independent review required or run.

## Milestone plan

The [adopted plan](../../rfcs/plans/remote-station-skill/milestone-plan.json) has
four milestones:

1. **M1 `agentskills-skill`** (ASK-0124, AgentSkills): remote-station skill,
   `station.json` resolver, entry contract, `install_command.py` forwarder, `rfc`
   bundle membership, temporary implement-rfc forwarders and tests. AC01–AC05, AC08.
2. **M2 `aito-migration`** (ASK-0125, AITO, native Windows): AC06.
3. **M3 `bpr-migration`** (ASK-0126, BetterPullReview): AC07.
4. **M4 `compact-station-messaging`** (ASK-0128, AgentSkills; added by the owner
   amendment of 2026-10-24, after M1): AC09–AC11.

## Acceptance checklist

| Criterion | Check/command | Outcome | Implementation commit |
|---|---|---|---|
| AC01 | `test_command_forwarder.StationConfigRefusalTests`, `test_station_config`, remote-station suite (255 tests) and `test_station_forwarders`; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | 12d3c32 |
| AC02 | `python -B scripts/verify_rfc_bundle.py --mask-program C:/code/git/ManageAgentSkills` (real MASK 9b73453); [bundle receipt](../../rfcs/plans/remote-station-skill/rfc-bundle-evidence.json) | Pass | 12d3c32 |
| AC03 | `test_command_forwarder.test_each_checkout_runs_its_own_pinned_version` (cmd and Git sh); [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | 12d3c32 |
| AC04 | `test_command_forwarder.test_refuses_outside_a_repository_and_without_the_skill_and_runs_nothing`; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | 12d3c32 |
| AC05 | `test_command_forwarder` pass-through and direct-equivalence tests, with negative control; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | 12d3c32 |
| AC06 | M2 native AITO resume of `aito-main-win` | Not run | |
| AC07 | M3 BetterPullReview documented commands | Not run | |
| AC08 | `test_station_forwarders` and the forwarder run inside the real-MASK bundle check; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | 12d3c32 |
| AC09 | M4 before/after per-turn token measurement on recorded `aito-main-win` turns | Not run | |
| AC10 | M4 guard refusals for v1 and v2 envelopes | Not run | |
| AC11 | M4 v1 admission during the compatibility release | Not run | |

## Checkpoint

M1 `agentskills-skill` accepted at source candidate
`12d3c3285909542febf39ae090f4150a4e673fc0` (pure move `3173ee9`, implementation
`12d3c32`); ASK-0124 Done. Earlier commits: reservation `3ad8599`, implement-rfc
Windows fixes `67c77e4` and `e5295e0` found while adopting the plan, import
`e89ca41`, claim `625600a`, binding `011cc25`. Continuation, commands and pending
obligations: [continuation](../../rfcs/plans/remote-station-skill/continuation.md).

Pending: AC06 (M2, ASK-0125, native Windows; may need the owner), AC07 (M3,
ASK-0126) and AC09–AC11 (M4, ASK-0128, owner amendment 2026-10-24). Owner decision pending on shipping no `mask-workflow.json` (MASK refuses
an input-only descriptor; see the RFC's implementation notes). M2 must reconcile the
owner's uncommitted AITO edits to `tools/codex_station.py`,
`tools/tests/test_codex_station.py` and `tools/tests/test_launch_remote_station.py`
before deleting those files.
