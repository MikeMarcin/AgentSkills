---
schema: "implement-rfc.card.v1"
id: "ASK-0125"
title: "Migrate AITO to the remote-station skill"
status: "Ready"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124"]
priority: "P1"
platforms: ["win"]
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
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
