# Remote-station skill continuation

Status: M1 `agentskills-skill` (ASK-0124), M3 `bpr-migration` (ASK-0126) and
M4 `compact-station-messaging` (ASK-0128) are complete and accepted. M2
`aito-migration` (ASK-0125) landed its engineering, but the card is Parked on
`human-review`: AC06's live native resume has not been observed. RFC-ASK-0017
stays Implementing, and closeout ASK-0127 stays in Backlog until ASK-0125 is Done
(see "Closeout segment" below).

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

## Owner amendment 2026-10-24 (segment `owner-amendment-m4`)

The owner added milestone M4 `compact-station-messaging` ("Compact station message
passing"), giving this reason: "the remote-station message format is token
inefficient, with boilerplate re-sent on every turn." Records-only segment
`owner-amendment-m4` of run `remote-station-2026-10-24` (coordinator-implementer)
recorded it:

- RFC section "Owner amendment 2026-10-24" holds AC09–AC11, the unmeasured
  candidate causes (hypotheses only) and the non-binding likely shape.
- `milestone-plan.json` gains `ASK-0128` in scope and milestone
  `compact-station-messaging` (prerequisite `agentskills-skill`). `bpr-migration`
  gains an added exit for closeout of AC09–AC11; its existing exits are unchanged.
  `MILESTONES.md` was regenerated with the helper's `render()`. The `render` CLI
  refuses to run while the view is stale.
- `milestone_plan.py check-amendment` refused, as designed for a scope change
  (`amendment cannot change plan identity or authorized scope`). The owner amendment
  is the explicit requirement change, and `check` on the published plan reports
  `structural: valid`.
- ASK-0128 was reserved (`a0f66c8`) and created in Ready (its only dependency,
  ASK-0124, is Done). ASK-0127 now depends on ASK-0128, and its checklist and
  `verification.md` carry AC09–AC11 as Not run. Following the existing pattern for
  ASK-0125, this is a card-level dependency; `bpr-migration` gains no milestone
  prerequisite.
- The M1 binding is unaffected. `bind` reproduces `checkpoint-final.json`'s
  definition, obligation and prerequisite fingerprints. `milestone_checkpoint.py
  check` now reports `reconcile` only because HEAD moved past `00b0023` through
  records-only commits. M1 needs no rebind.

MASK was upgraded to AgentSkills `e0b729c` in all consumers and pushed with owner
approval. AgentSkills' own upgrade outputs (`.mask.json`, `.mask.lock.json`) are
committed as `chore(mask): upgrade skills`. Like the other managed links, the new
`remote-station` links under `.agents/skills` and `.claude/skills` are machine-local
and are now gitignored.

## M4 implementation (segment `m4-implementation-1`)

One non-delegating `rfc-implementer` (effective route `claude-opus-5-5`, effort
medium), coordinator-implementer, on AgentSkills `main`. Other agents edited AITO
(M2) and BetterPullReview (M3) at the same time. This segment read AITO's
`.remote-station.json`, the Codex rollout and the Claude transcript, read-only, and
wrote nothing outside AgentSkills.

Commits: `3307b9d` claim; `83dc8c3` the before measurement (script plus
`token-measurement/before-v1.json`, committed before any design); `ee12b1e`
implementation; then the ASK-0128 finish with this record.

What changed: `skills/remote-station/scripts/station_task_admission.py` (v2
envelope validation and the plain-flag v2 request; v1 unchanged),
`remote_station_guard.py` (expands v2 from the station file and then applies the
v1 checks; one-line admission acknowledgement), the new
`schemas/remote-task-envelope.v2.schema.json`, `references/station-control.md`,
the guard tests, and implement-rfc's `references/remote-routing.md` dispatch
rules, with the regenerated `generated/portable-manifest.json`.

Result: station protocol fell from 1,716.6 to 441.1 tokens per turn on the same
80 recorded turns (o200k_base). AC09–AC11 pass; the evidence is in
`verification.md`. Pending for closeout (ASK-0127, not edited here): reconcile
AC09–AC11 into the closeout table. The repeated-prose rule's effect is
unmeasured. v1 removal after the compatibility release is unscheduled. A live
v2 admission on a real Codex station has not been observed; fixtures and the
recorded-turn re-expression stand in for it.

Command state: quiescent. All suites and the bundle check finished. The scratch
tokenizer virtual environment lives outside the repository. No runtime, server
or writer is handed off.

## Closeout segment (`closeout-1`)

One non-delegating `rfc-implementer` (effective route `claude-opus-5-5`, effort
medium), coordinator-implementer, run `remote-station-2026-10-24`, on AgentSkills
`main`. It wrote only AgentSkills tracker and plan records. It reran read-only
checks in AITO and BetterPullReview and edited neither repository.

Consumer commits, verified with `git show`:

- AITO: `c626d7a8cb` MASK upgrade (pin AgentSkills `e0b729c`) and `7c915c183e`
  forwarder, `station.json`, fork deletion and reduced docs.
- BetterPullReview: `db885a37a` MASK upgrade (pin `e0b729c`) and `e1c8661ac`
  forwarder, `station.json` and docs.

AgentSkills commits in this segment: `e3d78ba` claim ASK-0126; `de51c17` claim
ASK-0125; `3fc3d6e` finish ASK-0126 (AC07 pass, M2/M3 verification section);
`2949e1c` park ASK-0125 (`human-pending`, AC06 pending); then the closeout record
that fills ASK-0127's table and this section.

Rerun at closeout: AITO `status --json` (exit 0, `stn-39ef5ffb` with the
recorded Codex thread and Claude session). AITO tools suite: the same 7 failures
as the clean baseline. BetterPullReview `status --json` (exit 0, byte-identical
to the M3 before capture). The takeover-default code was compared between the
skill and the deleted BetterPullReview forwarder.

Gates:

- `issue_board.py validate` (global and `--rfc RFC-ASK-0017`): valid.
- `audit_board.py --rfc RFC-ASK-0017`: no violations.
- `verify_documentation.py`: 0 violations.
- `milestone_plan.py check`: structural valid.
- `git diff --check`: clean.
- `milestone_checkpoint.py check` on `checkpoint-final.json` returns
  `reconcile` ("candidate revision is not the current source revision"). This
  is expected. M4's `ee12b1e` changed `skills/remote-station` and implement-rfc's
  `remote-routing.md` after the M1 binding at `00b0023`. M4 has its own
  acceptance in `ASK-0128.acceptance.json`. M2 and M3 ran in their own
  repositories, so no AgentSkills binding was made for them. M1 acceptance is
  unaffected.

Distribution: AgentSkills `main` is 7 commits ahead of `origin/main` (`e0b729c`)
before this segment, and every consumer still pins `e0b729c`. M4 reaches
consumers only through a push and `mask upgrade`, which are not authorized.

## Next

1. **Owner, AC06:** in PowerShell at `C:/code/git/aito`, run
   `py -3 tools/launch_remote_station.py --require-claude-resume` and confirm the
   same `station_id` (`stn-39ef5ffb`), Codex thread
   `01a10525-e3fa-7250-85cf-c27f2f84897d`, Claude session
   `session_01Mb2Coeg8PF5g19jUAMQGm1`, plus the printed "Claude return path
   UNVERIFIED" warning. Never fabricate this observation.
2. Then a fresh implementer finishes ASK-0125 with that observation as AC06
   evidence (decision `done`), records AC06 in ASK-0127, makes ASK-0127 Ready,
   claims and finishes it, and moves RFC-ASK-0017 to its terminal status.
3. Owner decisions that remain open (none blocks AC06):
   - `mask-workflow.json`: accept the resolver-only check, or add input-only
     descriptors to ManageAgentSkills.
   - The removal date for v1 envelopes and the implement-rfc forwarders.
   - BetterPullReview's `mac` workstream: its `mac-lane` branch is absent on
     origin.
   - AITO `station_registry_doc`: `station.json` names `docs/remote-stations.md`,
     while `project.json` still names `tools/docs/agents/remote-stations.md`.
   - Push and `mask upgrade`, which would deliver M4 to consumers.
4. Not yet observed: a live v2 admission on a real Codex station.

## Consistency check

`checkpoint-final.json` renews the M1 binding at `00b0023` (records-only movement
after the source candidate; `git diff 12d3c32 00b0023` over `skills`, `scripts`,
`mask-source.json` and `README.md` is empty). `completion-observation.json` accounts
for `ASK-0124:*` and all three exits; `milestone_checkpoint.py check --execution
quiescent` returned `fresh-context` (`completion-check.json`). That consistency
result does not replace engineering acceptance, which is in `ASK-0124.acceptance.json`
and `verification.md`.
