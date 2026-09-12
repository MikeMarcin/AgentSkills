---
schema: "implement-rfc.card.v1"
id: "ASK-0014"
title: "Unified workflow integration and closeout"
status: "Done"
rfcs: ["RFC-ASK-0003"]
depends_on: ["ASK-0013"]
closeout_for: ["RFC-ASK-0003"]
metadata: {"closeout":true}
acceptance: [{"criterion":"RFC-ASK-0003-AC06","outcome":"pass","revision":"ba45ad0a7e010a1c0204730058a2c258ef84afdf plus reviewed closeout/documentation changes","evidence":{"kind":"observation","detail":"Integrated all six consumer cutovers; source/package and all six adapter checks pass. Focused macOS/native Windows suites and one critical review consumed with corrected regression evidence. Historical follow-ups and host-loading/offline UI limitations recorded in closeout. Task worktrees, fixture hosts, one-off converters and native test archives removed. Final MASK source-revision state is reconciled after this commit through guarded apply."}}]
---

# Unified workflow integration and closeout

RFC_BASE_SHA: dd5494d4a27e5e8a35046f7e15cb3cb873ea1bc3

Planned cards: ASK-0008, ASK-0009, ASK-0010, ASK-0011, ASK-0012, ASK-0013, ASK-0014.
Accepted design and outcome: AgentSkills RFC-ASK-0003 and this closeout record.

| Criterion | Check / result | Implementation commits |
|---|---|---|
| RFC-ASK-0003-AC01 | Canonical multi-RFC model, scoped queue, single/per-area reservation and visible bounded Git history. macOS board32/audit17/config15 and final unified10 tests passed; native Windows unified9 passed before the platform-independent completed-dependency pruning refinement. sample_studio full model loads in about 0.55s; no cache/daemon needed. | 872901f, 55bc562, 8ffffff, 05c15eb |
| RFC-ASK-0003-AC02 | Claim/acceptance-driven finish exercised through real task cards and disposable Git fixtures, with narrow path authority, stale/collision refusal and no push. Minimal evidence recorder plus observation/artifact escape hatch preserve agent judgment. Focused slice checks and warranted integration policy documented. | 043e4b3, 815757a |
| RFC-ASK-0003-AC03 | Attended16 public CLI/HTTP tests passed on macOS and native Windows Python3.14.6. Covers partial durable intake, simultaneous hosts/resource conflicts, interruption and selective protection. Live browser fixture saved one decision then paused/reloaded with remaining work intact. Offline HTML generation/import shares the intake. | 0a3d102 |
| RFC-ASK-0003-AC04 | Wizard8 tests passed on macOS and native Windows Python3.14.6. Live browser saved a manual response, consumed agent observation and retained pause/reload progress. Portable standard-library Python/HTML; no Bash/WSL. Original implementation informed by wizard UX, no substantive template code copied. | af5c203 |
| RFC-ASK-0003-AC05 | All six consumers adopted three shared skills through guarded MASK previews/applies and healthy cutover doctors. Four packages validate; all six generated-adapter checks pass. Per-consumer provenance records card/RFC counts and focused checks. No per-project workflow fork or durable converter. | MASK 18f09e3/421afe9; SampleLogs f9f8ab5; PLN 9c50c6a; SRV 683cb32c; sample_studio fa38f378c; AgentSkills 6e023f4/815757a |
| RFC-ASK-0003-AC06 | One integration-focused pass consumed the focused suites, source/package/adapters, live browser and native Windows results. AgentSkills3RFC/14cards and MASK4RFC/18cards documentation gates pass. One critical review found three attended concurrency defects, all corrected with four regressions. Cleanup completed as recorded below. | 0a3d102, 8ffffff, 05c15eb and this closeout |

## Integration findings and boundaries

One independent critical review examined concrete shared-board/attended authority and concurrency risks. It found whole-batch cancellation continuing into queued preparation, static version sharing accepting mutable preparation, and resource release preceding durable invalidation. All three were fixed; attended16 passed on both platforms after the fixes. No repeated reviewer loop. The runtime inherited the native model; exact model/effort telemetry was unavailable and is not asserted.

SRV retained specialized immutable RFC0016/17 evidence contracts as owned product tools outside skill discovery. Its actual documentation gate, documentation62, relocated contract4 and public allocator2 tests pass; prepared fixtures also passed RFC0017 44, capture38 plus recorded fixture coverage, and verdict checks. The real historical registration replay at c82e51c2c933887632fb0bb35db876375a151de9 passed read-only. PLN's scoped audit and allocation preview pass. sample_studio's scoped audit, five public wrapper tests, focused agent-document gate and ExampleModule live plan check (10 issues/3 dependencies) pass. SampleLogs's empty board remains empty. No application build or fabricated historical product revalidation was added for migration.

The one-off migrations preserve all live Markdown card/RFC bodies and truthful statuses: PLN192cards/16RFC, SRV611/27, sample_studio4927/589. Final converted files matched the reviewed plans. Five PLN platform cards and 41 sample_studio cards with unmet dependencies moved to Backlog; seven sample_studio attended cards moved to Parked. Platform and original descriptive metadata remain explicit. SRV's human queue returns SRV-0153 separately from its three service waits; sample_studio returns seven human waits. AgentSkills/MASK also use the one human-review token.

Full-board validation deliberately retains seven historical contradictions: PLN-0017 Done to PLN-0016 Blocked; sample_studio CHR-0123/FWB-0083 to CHR-0114 Ready, ENT-0061 to ENT-0060 Blocked, FVI-0398/FVI-0405 to FVL-0097 Blocked, and FVI-0463 to FVI-0389 Blocked. MOD-0043–0050 still require blocker triage. These are recorded product follow-ups, not hidden validation successes or newly invented completion. Scoped work prunes completed prerequisite history while global identity/counter checks remain intact.

Filesystem deployment and public tools are verified. An already-running Claude/Codex host loading updated skill content was not directly asserted. Both use the same driver-neutral CLI/intake. Pure local HTML generation and import were tested; direct file-URL browser navigation was unavailable in the UI tool. The fallback remains supported and no server is required to export/import partial decisions. Cooperative protections cannot prevent arbitrary external tools from altering resources.

## Cleanup and reconciliation

Removed the three task-created AgentSkills worktrees after matching all worker files to committed canonical source and confirming integrated branch ancestry. Removed `/tmp/unified-rfc-migration-20260905` including all converters/plans/candidates, `/tmp/unified-attended-ui-20260905`, acceptance scratch files, and `/tmp/unified-rfc-native-20260905.zip`. Removed native Windows `C:/Users/example/AppData/Local/Temp/unified-rfc-native-20260905` and its archive through the existing SSH connection. No fixture host remained running. Verified retired original skill backups remain intentionally ignored outside discovery roots; these are consumer provenance, not durable migration code.

All work is locally committed. Source-revision bookkeeping in MASK is reconciled using a fresh guarded plan/apply after the final source commit. No push, publication, credentials change or arbitrary product acceptance occurred. Concurrent SRV product edits, SampleLogs's unrelated .DS_Store and sample_studio's technical-book-humanizer change remain outside this task's commits.
