---
schema: "implement-rfc.card.v1"
id: "ASK-0123"
title: "Give Codex station turn reads a history-sized timeout"
status: "Done"
rfcs: []
depends_on: []
metadata: {"execution_strategy":"direct","requested_on":"2026-10-24"}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"daabae5b56586fa7ca908e85fd68ef8c250ac814","evidence":{"kind":"command","detail":"Reproduced on native Windows: thread/read for the 87-turn AITO station task returned in 0.0 s without turns and 58.1 s with includeTurns under Codex CLI 0.164.0, so the 30 s default refused --fresh. Turn-including reads now use THREAD_TURNS_READ_TIMEOUT_SECONDS (300 s); other requests keep 30 s. New regression test asserts every provisioning thread/read uses the longer timeout."}},{"criterion":"AC2","outcome":"pass","revision":"daabae5b56586fa7ca908e85fd68ef8c250ac814","evidence":{"kind":"command","detail":"PYTHONUTF8=1 py -3 -B -m unittest test_codex_station test_launch_remote_station test_station_control test_station_lease: 163 tests OK, 1 skip. station_activity shares the read and its fixtures were updated for the keyword."}},{"criterion":"AC3","outcome":"pass","revision":"daabae5b56586fa7ca908e85fd68ef8c250ac814","evidence":{"kind":"command","detail":"Manifest rehashed from index blobs in existing order (baseline 8a7b605df8ee23cb reproduced first), giving f98d0b97f1a8fd6c; validate_portable_agents --source-only reports portable source valid in a clean LF worktree; verify_documentation 0 violations; diff check clean."}}]
---

# Give Codex station turn reads a history-sized timeout

`launch_remote_station.py --fresh` on the AITO native Windows station refused
with `Codex App Server timed out during thread/read`. Every App Server request
used one 30 second timeout, and reading a long-lived station task with its turns
takes longer than that.

Own `skills/implement-rfc/scripts/codex_station.py`, its station fixtures and the
portable manifest. Preserve the default timeout for all other requests.

Acceptance:

- AC1: Turn-including `thread/read` waits long enough for a long station history;
  other requests keep the default.
- AC2: Focused station suites pass.
- AC3: Portable-source and documentation validation and diff checks pass.

## Verified result, 2026-10-24

Source revision: `daabae5b56586fa7ca908e85fd68ef8c250ac814`.

The read scales with history, so 300 seconds is headroom, not a bound. AITO's own
consumer copy in `tools/codex_station.py` received the same change; consumer
deployment through MASK is outside this card.

The working tree here is CRLF, so the manifest was hashed from index blobs and
validated from a clean LF worktree, following ASK-0122.

Closeout review runtime: primary-session self-review; direct execution, no subagents.
