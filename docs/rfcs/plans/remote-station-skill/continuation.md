# Remote-station skill continuation

Status: M1 `agentskills-skill` complete and accepted; ASK-0124 Done. M4
`compact-station-messaging` complete and accepted; ASK-0128 Done (see "M4
implementation" below). RFC-ASK-0017 stays Implementing: M2 (AITO, AC06) and M3
(BetterPullReview, AC07), then closeout ASK-0127, remain.

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
