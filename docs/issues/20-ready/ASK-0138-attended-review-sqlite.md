---
schema: "implement-rfc.card.v1"
id: "ASK-0138"
title: "Isolate active attended-review state and deploy the SQLite publisher"
status: "Ready"
rfcs: []
depends_on: ["ASK-0129"]
metadata: {"baseline":"9e11ff876c623711a0c5929564466ad159c8e352","requested_on":"2026-11-19"}
---

# Isolate active attended-review state and deploy the SQLite publisher

Use indexed active state for new sessions. Preserve existing JSON sessions and
the existing resource registry. Keep ordinary decisions and notes scoped to the
affected cards. Keep browser polling and hub publication independent of bulk
media and unrelated card bodies.

- AC1: Qualify the CLI, browser, leases, local host lifecycle and unchanged hub
  protocol on isolated sessions. Exercise a large review and decision retries.
- AC2: Hand Back atomically publishes the immutable revision to the existing
  readable UTF-8 session.json. Verify legacy read, note search, attachments,
  subsequent publication and recovery from interrupted and overlapping exports.
- AC3: Verify the pushed source revision and installed fleet revisions, retain
  rollback, and exercise a disposable review through the live hub. Record
  unavailable or disallowed actions explicitly.
