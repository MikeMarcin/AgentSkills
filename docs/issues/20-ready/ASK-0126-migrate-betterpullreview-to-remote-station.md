---
schema: "implement-rfc.card.v1"
id: "ASK-0126"
title: "Migrate BetterPullReview to the remote-station skill"
status: "Ready"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124"]
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
---

# Migrate BetterPullReview to the remote-station skill

Milestone M3 `bpr-migration` of RFC-ASK-0017, in the BetterPullReview consumer
under its own instructions and tracker. Write its `station.json` from its
implement-rfc `project.json`, point `scripts/launch_remote_station.py` at
remote-station (or the shared forwarder shape) and drop its private takeover
defaults, which the skill now applies.

Acceptance: RFC-ASK-0017 AC07.
