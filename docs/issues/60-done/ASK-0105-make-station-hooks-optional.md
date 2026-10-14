---
schema: implement-rfc.card.v1
id: ASK-0105
title: Remove default station tool blocking and expose station management
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"cc5853c","evidence":{"kind":"command","detail":"Native Windows guard suite exercised 60 cases: 58 passed initially with 2 new fixture-import errors; after adding the fixture module path, all four affected/new default/public recovery cases pass in the narrow rerun. Existing enforcement checks remain passing. POSIX default hook checks also pass. Default invocations emit no hook output or state, even replacement MASK calls/malformed events."}},{"criterion":"AC2","outcome":"pass","revision":"cc5853c","evidence":{"kind":"command","detail":"Native station-control suite: 48 tests, 47 pass and one POSIX process-group test skipped. Both new public status/takeover cases pass on WSL too; status does not mutate identity and takeover still needs actual stop proof. Existing launcher help test passes. Project status succeeds in all five actual station consumers, retaining their managed/local/transferring modes."}},{"criterion":"AC3","outcome":"pass","revision":"cc5853c","evidence":{"kind":"command","detail":"Eight removal fixtures pass on Windows; POSIX seven original fixtures plus mixed-platform case pass. Coverage: exact-byte preview, unrelated settings/commands, mixed-platform preservation, malformed/duplicate JSON, file/parent symlink refusal, missing configuration, idempotency and two linked consumers without readiness/registry prerequisites."}},{"criterion":"AC4","outcome":"pass","revision":"cc5853c","evidence":{"kind":"observation","detail":"Portable source valid; canonical documentation gate 15 RFCs/105 cards, zero violations; diff check clean. Windows registry four projects and WSL registry three projects audited, complete: five hook-bearing consumers now have no guard commands, two MASK checkouts had none. Local consumer commits: WSL BPR 739411f14 + closeout 3834878, Windows BPR 86303b24b, bpr-windows a1dea9354, WSL bpr-linux b31fcd4e9, AITO a69c47bd5. Actual status calls pass. BPR main documentation gate passes; old lane gates expose pre-existing NEXT_ID 0907/high-water mismatch, untouched. AITO changed-source checks pass with unchanged inherited tools instruction budget failure recorded. No other consumer, source publication, installed skill upgrade or runtime stop/loading observation is claimed."}}]
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
