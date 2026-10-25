# Milestones

> Generated from `milestone-plan.json`; edit the JSON, not this view.

Plan: **remote-station-skill** · Coverage: **complete**

These are integration outcomes, not compulsory agent-launch boundaries.

## agentskills-skill

A portable remote-station skill configured only by station.json owns every station behavior, ships a version-free launch_remote_station command, joins the rfc bundle, and leaves implement-rfc only temporary forwarders.

**Work:** `ASK-0124`

**Prerequisites:** None

**Completion:**

- AC01-AC05 and AC08 are demonstrated through public script and forwarder paths in disposable fixture consumers, including a consumer without implement-rfc and a real MASK bundle install.
- Existing station identity, lease, lifecycle, takeover and ASK-0123 turn-read behavior is preserved with its tests running from remote-station source; implement-rfc holds no station implementation besides the two forwarders.
- Skill and implement-rfc documentation, the bundle, closeout checklist and continuation agree; task commands and writers are quiescent.

**Boundary:** AgentSkills source only; no AITO or BetterPullReview edits, push, publication or credential change.

## aito-migration

AITO launches its stations through a forwarder to remote-station with station.json, and its private launcher, Codex helper and their tests are gone.

**Work:** `ASK-0125`

**Prerequisites:** agentskills-skill

**Completion:**

- AC06 is observed natively on Windows: aito-main-win resumes with the same station_id, Codex thread and Claude session and prints the return-path warning.
- The owner's uncommitted AITO station edits are reconciled before the fork files are deleted.

**Boundary:** AITO repository under its own instructions and tracker; native resume may require the owner.

## bpr-migration

BetterPullReview's documented station commands behave as before through remote-station without private takeover defaults.

**Work:** `ASK-0126`, `ASK-0127`

**Prerequisites:** agentskills-skill

**Completion:**

- AC07 is demonstrated through BetterPullReview's documented commands, including takeover with no options.
- RFC-ASK-0017 closeout reconciles AC01-AC08 against RFC_BASE_SHA with truthful pending native evidence.
- RFC-ASK-0017 closeout also reconciles the 2026-10-24 owner-amendment criteria AC09-AC11 from compact-station-messaging (ASK-0128).

**Boundary:** BetterPullReview repository under its own instructions and tracker, plus AgentSkills closeout records.

## compact-station-messaging

Compact station message passing: remote-station dispatch, admission and acknowledgement stop re-sending station-invariant boilerplate on every turn, with a measured per-turn token reduction and no weakening of guard refusals or v1 compatibility.

**Work:** `ASK-0128`

**Prerequisites:** agentskills-skill

**Completion:**

- AC09: per-turn token cost is measured on the same recorded aito-main-win turns (Codex thread history and Claude session transcript) before and after the change, with the method recorded; the before measurement precedes design and is kept as evidence.
- AC10: every guard refusal still fires for both v1 and v2 envelopes: replayed or reused task_id, project mismatch, authority exceeded and expired.
- AC11: v1 envelopes from existing dispatchers are still admitted during the compatibility release, and station identity rules are unchanged.

**Boundary:** skills/remote-station plus the implement-rfc dispatch rules that build station prompts; no push, publication or credential change.
