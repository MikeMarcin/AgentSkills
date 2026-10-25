---
schema: "implement-rfc.card.v1"
id: "ASK-0125"
title: "Migrate AITO to the remote-station skill"
status: "Parked"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124"]
priority: "P1"
platforms: ["win"]
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
parked_on: "human-review"
acceptance: [{"criterion":"RFC-ASK-0017-AC06","outcome":"pending","revision":"aito@7c915c183ef97747f4257d6dec027f05751fcda4","evidence":{"kind":"observation","detail":"Engineering landed in AITO 7c915c183e (MASK pin AgentSkills e0b729c in c626d7a8cb): tools/launch_remote_station.py is a 24-line forwarder, tools/codex_station.py and both fork test files are deleted (owner approved discarding the uncommitted ASK-0123 port), station.json keeps only the main workstream. `py -3 tools/launch_remote_station.py status --json` exits 0 at closeout with station_id stn-39ef5ffb, Codex thread 01a10525-e3fa-7250-85cf-c27f2f84897d and Claude session session_01Mb2Coeg8PF5g19jUAMQGm1. An identity probe through the skill's own code resolves aito-main-win, accepts the aito.implement-rfc.remote-station.v2 schema, keeps the same station, thread and session, and renders the return-path warning. Tools suite: the same 7 pre-existing failures as the clean baseline (84 tests after, 171 before; the 87 removed are the fork's). PENDING: the live native resume, which only the owner can run: `py -3 tools/launch_remote_station.py --require-claude-resume` in PowerShell at C:/code/git/aito, observing the same station_id, Codex thread and Claude session plus the printed return-path warning."}}]
---

# Migrate AITO to the remote-station skill

Milestone M2 `aito-migration` of RFC-ASK-0017, in the AITO consumer
(`C:\code\git\aito`) under its own instructions and tracker. Write AITO's
`station.json` from its implement-rfc `project.json` (dropping the `moira` and
`acta` workstreams), replace `tools/launch_remote_station.py` with a forwarder of
at most 30 lines, delete `tools/codex_station.py` and both fork test files, and
reduce `tools/docs/agents/remote-stations.md` and `docs/remote-stations.md` to
AITO-specific setup.

Hazard: AITO's worktree held uncommitted user changes to `tools/codex_station.py`,
`tools/tests/test_codex_station.py` and `tools/tests/test_launch_remote_station.py`
on 2026-10-24. They port ASK-0123's history-sized turn read, which the skill already
has; reconcile them with the owner before deleting those files.

Acceptance: RFC-ASK-0017 AC06, which needs a native Windows resume of
`aito-main-win` (`stn-39ef5ffb`) with the same station, Codex thread and Claude
session, plus the return-path warning. Never fabricate that observation.
