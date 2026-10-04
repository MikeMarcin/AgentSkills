---
schema: implement-rfc.card.v1
id: ASK-0102
title: Scope station bootstrap restrictions to the materialization turn
status: "Ready"
rfcs: []
depends_on: []
---

# Scope station bootstrap restrictions to the materialization turn

Correct the shared Codex station bootstrap prompt so its temporary prohibition
on inspecting or modifying files cannot be mistaken for a permanent read-only
station policy. The station's registry, validated work envelope, writer lease,
repository instructions and current owner mandate govern later work.

## Observed failure

On 2026-10-03/04, AITO's fresh native-Windows station `aito-main-win` on JaegAW
was provisioned with `authority: lane-commit` but refused later authorized file
work because its bootstrap user message said:

> Do not inspect or modify files. Reply exactly STATION READY.

The current task was resolved from `C:\code\git\aito\.remote-station.json`
as `01a10525-e3fa-7250-85cf-c27f2f84897d`, reached through the Desktop Remote
host `remote-control:env_e_6a925c2980dc832da3493cea2cb4d944`. Its response
treated the unqualified bootstrap sentence as a continuing owner restriction
and requested a direct owner instruction despite the coordinator's authorized
work request. The owner clarified: “I did not create a read-only station I dont
know why it says that. Make changes as needed”. Forwarding that clarification
allowed file inspection; separate live writer/readiness guards still applied.

Canonical source at `b75119cd7a39310407827c5275799ab25f84f39f`:
`skills/implement-rfc/scripts/codex_station.py:station_bootstrap_text` emits
the same unqualified sentence. AITO also retains an older consumer helper
with that wording. Correct the canonical source first; any consumer migration
requires its own authorized scope and readiness checks.

## Owned scope

Shared Codex station bootstrap generation, exact bootstrap-only history
recognition and their focused tests. Update directly relevant station guidance
and the portable manifest through its named generator if required. No live
station reset, permission widening, history rewrite or consumer rollout.

## Acceptance

- AC1: The bootstrap message explicitly limits the no-tools/no-file-work
  restriction to that single materialization turn and still requests exactly
  `STATION READY`. It states that later authorized work follows the validated
  station authority and repository instructions.
- AC2: A correctly bound later task with a valid envelope and live writer lease
  is not refused solely because of the bootstrap instruction. Read-only
  authority, unrelated scope and unreconciled writers remain protected.
- AC3: Safe replacement recognizes both the new exact completed bootstrap turn
  and the legacy exact completed bootstrap turn as bootstrap-only histories.
  Active turns, tool activity, additional work turns and unrelated lookalike
  prompts remain ineligible; do not broaden matching by substring.
- AC4: Focused prompt/materialization/replacement tests cover those cases and
  pass. Required portable-source and documentation gates pass. A recorded
  station runtime observation distinguishes prompt interpretation from writer
  or host readiness failures; test fixtures alone do not certify live delivery.

## Verification plan

Run the focused `test_codex_station.py` suite and only relevant launcher/guard
cases needed by changed behavior, then the repository's portable-source and
documentation gates plus `git diff --check`. Retain the generated prompt,
source revision, commands and results. If a live interpretation check cannot
be performed safely, record that obligation precisely instead of reporting it
as passed.
