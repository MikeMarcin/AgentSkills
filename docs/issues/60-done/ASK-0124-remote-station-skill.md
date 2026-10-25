---
schema: "implement-rfc.card.v1"
id: "ASK-0124"
title: "Extract the remote-station skill, station.json and launch command"
status: "Done"
rfcs: ["RFC-ASK-0017"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"remote-station-skill","path":"docs/rfcs/plans/remote-station-skill/milestone-plan.json"}}
acceptance: [{"criterion":"RFC-ASK-0017-AC01","outcome":"pass","revision":"12d3c3285909542febf39ae090f4150a4e673fc0","evidence":{"kind":"artifact","detail":"Consumer with only remote-station and station.json: status and a launch reaching the Codex probe; missing/malformed/unknown-key station.json exit 2 before any lease or runtime; 255 station tests run from remote-station source; implement-rfc holds only the two forwarders.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}},{"criterion":"RFC-ASK-0017-AC02","outcome":"pass","revision":"12d3c3285909542febf39ae090f4150a4e673fc0","evidence":{"kind":"artifact","detail":"Real MASK 9b73453 bundle install of agentskills/rfc into a fresh fixture links remote-station beside implement-rfc in both link roots; status healthy; station status runs from both roots and through the implement-rfc forwarder.","path":"docs/rfcs/plans/remote-station-skill/rfc-bundle-evidence.json"}},{"criterion":"RFC-ASK-0017-AC03","outcome":"pass","revision":"12d3c3285909542febf39ae090f4150a4e673fc0","evidence":{"kind":"artifact","detail":"Installed cmd and sh forwarders run each checkout's own pinned version, including from a subdirectory and from a linked worktree with its own link.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}},{"criterion":"RFC-ASK-0017-AC04","outcome":"pass","revision":"12d3c3285909542febf39ae090f4150a4e673fc0","evidence":{"kind":"artifact","detail":"Outside a repository exit 3 naming the directory; nested repository without the link exit 4 naming mask install remote-station; nothing runs and stdout stays empty.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}},{"criterion":"RFC-ASK-0017-AC05","outcome":"pass","revision":"12d3c3285909542febf39ae090f4150a4e673fc0","evidence":{"kind":"artifact","detail":"argv, stdin, stdout, stderr, cwd and exit status pass through both forwarders; status --json, a refused launch and a launch match direct invocation byte for byte; negative control without argument forwarding fails.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}},{"criterion":"RFC-ASK-0017-AC08","outcome":"pass","revision":"12d3c3285909542febf39ae090f4150a4e673fc0","evidence":{"kind":"artifact","detail":"implement-rfc launch_remote_station.py and station_control.py forwarders match the remote-station scripts and support runpy main(argv); missing sibling names mask install remote-station.","path":"docs/rfcs/plans/remote-station-skill/verification.md"}}]
---

# Extract the remote-station skill, station.json and launch command

Milestone M1 `agentskills-skill` of RFC-ASK-0017. Own `skills/remote-station/**`,
the station cluster's removal from `skills/implement-rfc/**` (leaving the two
temporary forwarders), `mask-source.json`, `scripts/run_tests.py`,
`scripts/verify_rfc_bundle.py` and scoped RFC/plan/evidence records. Preserve
unrelated work. No consumer repository edits.

Acceptance: RFC-ASK-0017 AC01, AC02, AC03, AC04, AC05 and AC08.
