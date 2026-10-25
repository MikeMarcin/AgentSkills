---
schema: "implement-rfc.card.v1"
id: "ASK-0124"
title: "Extract the remote-station skill, station.json and launch command"
status: "In Progress"
rfcs: ["RFC-ASK-0017"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
---

# Extract the remote-station skill, station.json and launch command

Milestone M1 `agentskills-skill` of RFC-ASK-0017. Own `skills/remote-station/**`,
the station cluster's removal from `skills/implement-rfc/**` (leaving the two
temporary forwarders), `mask-source.json`, `scripts/run_tests.py`,
`scripts/verify_rfc_bundle.py` and scoped RFC/plan/evidence records. Preserve
unrelated work. No consumer repository edits.

Acceptance: RFC-ASK-0017 AC01, AC02, AC03, AC04, AC05 and AC08.
