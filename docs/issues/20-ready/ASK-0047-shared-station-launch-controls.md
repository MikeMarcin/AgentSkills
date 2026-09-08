---
schema: implement-rfc.card.v1
id: ASK-0047
title: Shared station fresh-context controls and compact Claude server
status: Ready
rfcs: ["RFC-ASK-0003"]
depends_on: []
---

# Shared station fresh-context controls and compact Claude server

Owner-requested follow-up to shared workflow adoption. Port SampleReview
39063364 into canonical source, preserving consumer configuration and newer behavior.
Baseline: 171a17d. Routing: primary | Reason: coupled bounded upstream port.
This card anchors follow-up acceptance; historical RFC closeout remains unchanged.

Owned paths: skills/implement-rfc/scripts/{launch_remote_station,codex_station}.py,
their tests, active station references/README, source manifest if required.

## Acceptance

- AC1: --fresh selects codex, claude or both without resetting station identity;
  disabled services retain bindings. Legacy identity reset remains supported.
- AC2: Claude defaults to compact remote-control server, records the exact session
  after delayed connection, and resumes only that identity. Docs explain visibility.
- AC3: Codex resets archive only validated idle station tasks, recognize archived
  catalog entries and report bootstrap/foreign-writer failures. Active/unrelated
  tasks are refused without bypassing ownership.
- AC4: Focused mocked launcher/RPC tests and public helper invocation through linked
  sources in two consumer contexts pass; structure and portable-source gates pass.

No push, live session reset, credentials, deployment registry or consumer migration.
Existing links observe the authorized canonical edit. No live launch is required.
