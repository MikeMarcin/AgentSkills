---
schema: "implement-rfc.card.v1"
id: "ASK-0126"
title: "Migrate BetterPullReview to the remote-station skill"
status: "Done"
rfcs: ["RFC-ASK-0017"]
depends_on: ["ASK-0124"]
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
acceptance: [{"criterion":"RFC-ASK-0017-AC07","outcome":"pass","revision":"BetterPullReview@e1c8661ac491c9d9d25cabe8edd1139f12d1cab9","evidence":{"kind":"observation","detail":"BetterPullReview scripts/launch_remote_station.py now forwards to its pinned .agents/skills/remote-station entry (MASK pin AgentSkills e0b729c, BetterPullReview db885a37a) with station.json written from project.json and no private takeover defaults. Live read-only `py -3 scripts/launch_remote_station.py status --json` on bpr-main-win (stn-a3502cc1) is byte-identical before and after the change and again at closeout (exit 0). Takeover with no options, --json and --confirm-runtime-stopped matched old versus new in disposable fixtures (M3 implementer; not run on the live station; fixture logs not retained). Closeout code check: the skill's main() adds --mode local and --stop-previous for takeover exactly as the deleted forwarder did. Remote-station suite 255 OK (1 skip); BetterPullReview documentation gate OK, 67 doc tests OK."}}]
---

# Migrate BetterPullReview to the remote-station skill

Milestone M3 `bpr-migration` of RFC-ASK-0017, in the BetterPullReview consumer
under its own instructions and tracker. Write its `station.json` from its
implement-rfc `project.json`, point `scripts/launch_remote_station.py` at
remote-station (or the shared forwarder shape) and drop its private takeover
defaults, which the skill now applies.

Acceptance: RFC-ASK-0017 AC07.
