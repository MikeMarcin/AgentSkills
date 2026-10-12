---
schema: implement-rfc.card.v1
id: ASK-0105
title: Remove default station tool blocking and expose station management
status: "In Progress"
rfcs: []
depends_on: []
---

# Remove default station tool blocking and expose station management

Owner mandate (2026-10-11): work directly; implement-rfc station hooks obstructed
MASK recovery in WSL BetterPullReview, and the buried status/takeover advice was
unhelpful. Make station management ergonomic or remove the hooks.

Chosen outcome: ordinary hook invocations are inactive. Blocking enforcement
requires explicit `--enforce`; it is retained for deliberately guarded stations.
The project launcher exposes status, takeover and removal of station hooks.
Explicit launches retain supervisor leases; removing hooks does not stop a writer
or prove runtime quiescence. This owner amendment supersedes claims that every
station turn must be admitted through automatic project hooks.

Scope: canonical shared helpers, focused fixtures, station instructions and
portable manifest. Owner scope expansion: remove hooks from every registered
Windows/WSL MASK project selecting implement-rfc. Inventory: Windows BetterPullReview,
ManageAgentSkills, aito and bpr-windows; WSL BetterPullReview, ManageAgentSkills and
bpr-linux. Both MASK checkouts have no station hooks. Preserve unrelated commands,
dirty files, locked skill versions, local ownership and active runtimes. Existing
consumer management scripts expose status/takeover, with separate consumer records.
No push, live stop/takeover, global settings, other consumer migration or MASK
internal-state edits. Baseline: 4c0f70c490445780dd8bb5805481d0da326a4bf3.

Acceptance:
- AC1: Default hook execution cannot block tools or prompts and writes no
  admission/lifecycle state; explicit enforcement retains existing checks.
- AC2: Launcher status/takeover uses the current checkout without hidden helper
  paths or manual root/mode flags, and starts no runtime for inspection.
- AC3: Hook inspection/removal previews changes, removes only station guard
  commands, preserves unrelated hooks/settings and fails safely on malformed or
  linked configuration. Disabling hooks never stops or transfers a writer.
- AC4: Guidance accurately names public recovery commands, optional enforcement
  and remaining writer obligations; focused POSIX/Windows checks and portable
  source/documentation gates pass. Live deployment evidence is separate.

Execution: direct in the primary session; no agents or background writers.
Readiness reports project.not_registered on this Windows checkout. Canonical
source authoring and fixture verification remain available; no installed host
loading or native remote-stop qualification is claimed.
