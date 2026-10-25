# Remote-station skill continuation

Status: M1 `agentskills-skill` complete and accepted; ASK-0124 Done. RFC-ASK-0017
stays Implementing: M2 (AITO, AC06) and M3 (BetterPullReview, AC07) remain.

Assignment: one non-delegating `rfc-implementer` (effective route
`claude-opus-5-5`, effort high) under the coordinator-implementer recipe, on
AgentSkills `main`. Run `remote-station-2026-10-24`; segment `m1-implementation-1`;
mandate revision `remote-station-v1` (owner, 2026-10-24: "Implement the RFC ...
Consumer migration scope names AITO and BetterPullReview"). Selection:
`execution-selection.json` (`coordinator-implementer`, host load not verified). No
push, publication, credential or permission change was authorized or made.

RFC_BASE_SHA: `3ad85990719baec8f38544006a110c7a91bf6ab2`.
Source candidate: `12d3c3285909542febf39ae090f4150a4e673fc0`.

Commits on main, in order: `3ad8599` reserve ASK-0124..0127; `67c77e4` and `e5295e0`
implement-rfc Windows fixes found while adopting the plan (POSIX provenance path in
`milestone_plan.py adopt`; UTF-8 read of `MILESTONES.md`); `e89ca41` import and plan;
`625600a` claim; `011cc25` checkpoint binding; `3173ee9` pure moves; `12d3c32`
implementation; then the ASK-0124 finish and this record.

Changed paths: `skills/remote-station/**` (new skill), `skills/implement-rfc/`
(`SKILL.md`, `README.md`, `references/remote-routing.md`,
`references/runtime-compatibility.md`, `schemas/project.schema.json`,
`scripts/project_config.py`, forwarders `scripts/launch_remote_station.py` and
`scripts/station_control.py`, tests, regenerated `generated/portable-manifest.json`),
`mask-source.json`, `README.md`, `scripts/run_tests.py`,
`scripts/verify_rfc_bundle.py`, RFC-ASK-0017, its cards and this plan directory.

Verification: see `verification.md` and `rfc-bundle-evidence.json`. Remote-station
suite 255 tests OK (1 POSIX-only skip); implement-rfc suite shows only the same 20
pre-existing Windows failures as the pre-change baseline; real-MASK bundle check,
documentation gate and portable-source validation pass.

Decisions recorded in the RFC's implementation notes: no `mask-workflow.json`
because MASK refuses an input-only descriptor (owner decision pending; options are
to accept the resolver-only check or add input-only descriptors to
ManageAgentSkills); frozen `implement-rfc.*` durable identifiers; no personal-mode
reading in station code; AITO's uncommitted fork edits carried nothing new.

Command and ownership state: quiescent. All test, bundle and baseline runs finished;
the temporary baseline worktree was removed (`git worktree list` shows only the main
checkout). No review server, waiter or writer is handed off. No real Claude or Codex
runtime was started.

## Next

M2 `aito-migration` (ASK-0125, now Ready) needs a fresh implementer in
`C:\code\git\aito` under AITO's own instructions and tracker, on native Windows:

1. Reconcile with the owner the uncommitted edits to `tools/codex_station.py`,
   `tools/tests/test_codex_station.py` and `tools/tests/test_launch_remote_station.py`
   (they port ASK-0123's turn-read timeout, already in the skill) before deleting
   those files.
2. Install remote-station (MASK upgrade to a revision containing `12d3c32` or later),
   write `.mask/skill-config/remote-station/station.json` from AITO's `project.json`
   without the `moira` and `acta` workstreams, replace
   `tools/launch_remote_station.py` with a forwarder of at most 30 lines, delete the
   fork and its tests, and reduce `tools/docs/agents/remote-stations.md` and
   `docs/remote-stations.md` to AITO-specific setup (the hazard table is now
   `skills/remote-station/references/platform-dead-ends.md`).
3. AC06: resume `aito-main-win` (`stn-39ef5ffb`) natively and observe the same
   `station_id`, Codex thread and Claude session plus the return-path warning. This
   may need the owner; never fabricate it.

M3 `bpr-migration` (ASK-0126, Ready) is independent of M2 and can run first if M2
waits on the owner.

## Consistency check

`checkpoint-final.json` renews the M1 binding at `00b0023` (records-only movement
after the source candidate; `git diff 12d3c32 00b0023` over `skills`, `scripts`,
`mask-source.json` and `README.md` is empty). `completion-observation.json` accounts
for `ASK-0124:*` and all three exits; `milestone_checkpoint.py check --execution
quiescent` returned `fresh-context` (`completion-check.json`). That consistency
result does not replace engineering acceptance, which is in `ASK-0124.acceptance.json`
and `verification.md`.
