---
schema: "implement-rfc.card.v1"
id: "ASK-0138"
title: "Isolate active attended-review state and deploy the SQLite publisher"
status: "In Progress"
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

## Verified release and partial fleet rollout

Source revision `f912696506263070606cbcbff22b077a4bd05046` was pushed to
`origin/main` and verified through GitHub. GitHub Actions remained disabled.

- AC1 passed on macOS. The attended-review suite ran 64 tests, and the Node
  browser fixture passed. The stress case used a database over 40 MiB and
  verified that compact status, delta reads, Accept, note saves, and retries
  worked with unrelated card and material data unavailable. The hub suite ran
  87 tests with two skips, including the publisher integration against a
  disposable hub.
- AC2 passed. A killed exporter recovered its exact marker across processes.
  Later preparation progressed during the interrupted export.
  A replay of an older marker kept the newer archive intact. The real hub smoke
  used the published MASK helper over Tailscale HTTPS for Accept, Reject,
  a critical UTF-8 note with an attachment, retries, and Hand Back. The prior
  helper and literal grep read sequence 11. A later publication at sequence 15
  kept that archive byte-for-byte intact. The live hub answered health checks
  before and after, and the disposable row was cleared.
- AC3 is pending for `jaegaw-windows` and `jaegaw-wsl`. Signed MASK operation
  `281d4dcb073d09c6e5ce6ce5314d1118` verified the exact release in the
  `this-mac` and `intel-mac` personal scopes for Codex and Claude. The other
  two installations are queued with unknown SSH delivery outcomes. The signed
  authorization expires November 26, 2026 at 8:04 a.m. Pacific time. Prior and
  release packages, checksums and a verified source restore patch were retained for
  rollback. The live activation
  used the publisher against the existing hub service.
