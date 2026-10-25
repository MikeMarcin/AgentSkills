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

Implementation commits are repository-qualified. Unqualified hashes are
AgentSkills.

| Criterion | Check/command | Outcome | Implementation commit |
|---|---|---|---|
| AC01 | `test_command_forwarder.StationConfigRefusalTests`, `test_station_config`, remote-station suite (255 tests) and `test_station_forwarders`; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills 12d3c32 |
| AC02 | `python -B scripts/verify_rfc_bundle.py --mask-program C:/code/git/ManageAgentSkills` (real MASK 9b73453); [bundle receipt](../../rfcs/plans/remote-station-skill/rfc-bundle-evidence.json) | Pass | AgentSkills 12d3c32 |
| AC03 | `test_command_forwarder.test_each_checkout_runs_its_own_pinned_version` (cmd and Git sh); [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills 12d3c32 |
| AC04 | `test_command_forwarder.test_refuses_outside_a_repository_and_without_the_skill_and_runs_nothing`; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills 12d3c32 |
| AC05 | `test_command_forwarder` pass-through and direct-equivalence tests, with negative control; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills 12d3c32 |
| AC06 | AITO `py -3 tools/launch_remote_station.py status --json` (exit 0: `stn-39ef5ffb`, the recorded Codex thread and Claude session), skill-code identity probe with the return-path warning, tools suite unchanged against baseline. Live native resume `py -3 tools/launch_remote_station.py --require-claude-resume` not observed; [verification](../../rfcs/plans/remote-station-skill/verification.md#m2-and-m3-consumer-migrations) | Pending (owner native resume); fork removal done | AITO 7c915c183e (MASK pin c626d7a8cb) |
| AC07 | BetterPullReview `py -3 scripts/launch_remote_station.py status --json` (byte-identical before, after and at closeout); takeover with no options, `--json` and `--confirm-runtime-stopped` identical old against new in disposable fixtures; [verification](../../rfcs/plans/remote-station-skill/verification.md#m2-and-m3-consumer-migrations) | Pass | BetterPullReview e1c8661ac (MASK pin db885a37a) |
| AC08 | `test_station_forwarders` and the forwarder run inside the real-MASK bundle check; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills 12d3c32 |
| AC09 | `measure_station_tokens.py --format v1` before (committed 83dc8c3) and `--format v2` after, on 80 recorded `aito-main-win` turns, tiktoken `o200k_base`: station protocol 1,716.6 to 441.1 tokens per turn (−74.3%); [measurement](../../rfcs/plans/remote-station-skill/verification.md#ac09-per-turn-token-measurement) | Pass | AgentSkills ee12b1e |
| AC10 | `test_guard_refusals_fire_for_v1_and_v2_requests` and `..._prompts`: replay, project mismatch, authority exceeded, expired (and station mismatch) for v1 and v2; remote-station suite 279 OK; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills ee12b1e |
| AC11 | `test_v1_dispatcher_envelopes_are_still_admitted`; station file and lifecycle record byte-identical; station identity code untouched; [verification](../../rfcs/plans/remote-station-skill/verification.md) | Pass | AgentSkills ee12b1e |

## Checkpoint

M1 `agentskills-skill` accepted at source candidate
`12d3c3285909542febf39ae090f4150a4e673fc0` (pure move `3173ee9`, implementation
`12d3c32`); ASK-0124 Done. Earlier commits: reservation `3ad8599`, implement-rfc
Windows fixes `67c77e4` and `e5295e0` found while adopting the plan, import
`e89ca41`, claim `625600a`, binding `011cc25`. M4 `compact-station-messaging`
accepted at `ee12b1e`; ASK-0128 Done. M3 `bpr-migration` accepted at
BetterPullReview `e1c8661ac`; ASK-0126 Done. M2 `aito-migration` engineering
landed at AITO `7c915c183e`; ASK-0125 Parked on `human-review` for AC06's live
native resume. Continuation, commands and pending obligations:
[continuation](../../rfcs/plans/remote-station-skill/continuation.md).

This card stays in Backlog: it depends on ASK-0125, which is not Done.
RFC-ASK-0017 stays Implementing.

Pending:

- AC06: the owner runs `py -3 tools/launch_remote_station.py --require-claude-resume`
  in PowerShell at `C:/code/git/aito` and confirms the same `station_id`
  (`stn-39ef5ffb`), Codex thread, Claude session and the printed return-path
  warning. Then finish ASK-0125 with the observation and close this card.
- Owner decisions: no `mask-workflow.json` (MASK refuses an input-only
  descriptor); the removal date for v1 envelopes and the implement-rfc
  forwarders after the compatibility release; BetterPullReview's `mac`
  workstream, whose `mac-lane` branch is absent on origin; AITO's
  `station_registry_doc`, which `station.json` sets to `docs/remote-stations.md`
  while its unchanged implement-rfc `project.json` still names
  `tools/docs/agents/remote-stations.md`.
- Unobserved: a live v2 admission on a real Codex station.
- Distribution: consumers pin AgentSkills `e0b729c`, which lacks M4. Consumers
  get M4 only after a push of AgentSkills `main` and a `mask upgrade`, neither
  of which is authorized.
