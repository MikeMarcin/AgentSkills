---
schema: "implement-rfc.card.v1"
id: "ASK-0014"
title: "Unified workflow integration and closeout"
status: "Ready"
rfcs: ["RFC-ASK-0003"]
depends_on: ["ASK-0013"]
closeout_for: ["RFC-ASK-0003"]
metadata: {"closeout":true}
---

# Unified workflow integration and closeout

Owned paths: RFC, closeout, integration fixtures and provenance.

Acceptance: RFC-ASK-0003-AC06; implement the approved design and record direct checks.

RFC_BASE_SHA: dd5494d4a27e5e8a35046f7e15cb3cb873ea1bc3

Planned cards: ASK-0008, ASK-0009, ASK-0010, ASK-0011, ASK-0012, ASK-0013, ASK-0014.

| Criterion | Check / result | Commit |
|---|---|---|
| RFC-ASK-0003-AC01 | Not run | Pending |
| RFC-ASK-0003-AC02 | Not run | Pending |
| RFC-ASK-0003-AC03 | Not run | Pending |
| RFC-ASK-0003-AC04 | Not run | Pending |
| RFC-ASK-0003-AC05 | Not run | Pending |
| RFC-ASK-0003-AC06 | Not run | Pending |

Next: implement board/core, attended sessions and wizard in isolated source worktrees. User-approved design is recorded in ManageAgentSkills commit 9a78f09.

## Execution checkpoint (2026-09-05)

- Core ASK-0008 committed 872901f; acceptance workflow ASK-0009 committed 043e4b3; monorepo area/reservation refinement 55bc562.
- Wizard ASK-0011 committed af5c203. Native Windows Python3.14.6 (existing example-win-host SSH host) passed wizard8, attended12, unified-board9 tests; macOS focused board32/audit17/config15/unified9 and wizard8/attended12 passed. Legacy renderer fixture now explicitly tests missing external context refusal; targeted recheck remains.
- One critical integration review used the native inherited runtime (exact model/effort not exposed). Three attended concurrency findings reproduced: batch cancellation continued to next command; static version sharing admitted review during mutable preparation; release-before-session-invalidation crash allowed stale verdict. Worker is correcting them with regressions. No further reviewer planned; verify only changed paths.
- Live attended browser fixture proved immediate partial save then pause/reload persistence. Fixture server/tab/registry removed. Wizard browser smoke verified by worker. Pure local HTML generation/import tested; direct file browser navigation was unavailable in the tool, retained as limitation.
- Source remains isolated: main AgentSkills still 0cb7e6f; implementation checkout /Users/example/Documents/GitHub/AgentSkills-unified-workflow (codex/unified-rfc-workflow). Worker checkouts /Users/example/Documents/GitHub/AgentSkills-attended-session and /Users/example/Documents/GitHub/AgentSkills-portable-wizard retain copied uncommitted skill sources until integration consumed.
- Temporary one-off converters/plans: /tmp/unified-rfc-migration-20260905. All six candidate boards normalize structurally. Seven historical Done-dependency contradictions remain honestly unchanged (PLN1, sample_studio6); no source migration yet except this isolated AgentSkills worktree. SRV-0618 changed concurrently and freshness guard correctly refused; replan immediately before each cutover. sample_studio queue/validation measured ~0.55s, no cache needed.
- Windows temp root C:/Users/example/AppData/Local/Temp/unified-rfc-native-20260905 plus same-name .zip; local /tmp/unified-rfc-native-20260905.zip. Remove after corrected attended/native checks. All inputs are task-created tooling fixtures, not product builds.
- Next: consume attended fixes; finish ASK-0010; claim ASK-0012 and reconcile docs/templates/examples + activate source and MASK context in a bounded sequence. Then ASK-0013 consumer cutovers with fresh source checks, metadata-only staging of dirty cards, native adapter retirement/rendering, guarded MASK deployment. SRV product tools calling specialized old attended validators need repository-owned relocation; no historical compatibility fork inside shared skills. sample_studio support wrapper/docs patches being prepared outside its checkout.
