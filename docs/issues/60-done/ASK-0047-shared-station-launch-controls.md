---
schema: implement-rfc.card.v1
id: ASK-0047
title: Shared station fresh-context controls and compact Claude server
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"bfd2224fcd7bf31fef40b4d5bf869e193b847223","evidence":{"kind":"observation","detail":"Fresh/service flags and preserved station/disabled identities covered by launcher tests."}},{"criterion":"AC2","outcome":"pass","revision":"bfd2224fcd7bf31fef40b4d5bf869e193b847223","evidence":{"kind":"observation","detail":"Compact command, delayed bridge watcher, exact-ID resume and interrupted fresh binding covered by launcher tests; docs reconciled."}},{"criterion":"AC3","outcome":"pass","revision":"bfd2224fcd7bf31fef40b4d5bf869e193b847223","evidence":{"kind":"observation","detail":"RPC tests cover archive catalog, active/unrelated refusal, foreign writer, bootstrap errors and replacement."}},{"criterion":"AC4","outcome":"pass","revision":"bfd2224fcd7bf31fef40b4d5bf869e193b847223","evidence":{"kind":"observation","detail":"116 tests passed with 2 optional schema skips; two linked consumer main invocations, SRV wrapper help, source/structure gates and diff hygiene passed."}}]
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

## Scope clarification

Independent owner-requested enhancement after the completed RFC-ASK-0003 adoption.
It does not reopen that terminal RFC or amend its historical acceptance.

## Verification and closeout

Implementation revision: bfd2224fcd7bf31fef40b4d5bf869e193b847223. Primary semantic/simplification review retained
consumer context on both provisioning paths and recursive replacement. Added
an interruption regression: fresh Claude clears its old registry binding before
connection. No known critical in-scope defect; no live runtime trial was performed.

Commands: `python3 -B -m unittest discover -s skills/implement-rfc/tests -p NAME.py -q`:
test_launch_remote_station (63 pass), test_codex_station (39 pass),
test_remote_station_guard (10 pass, 2 optional jsonschema tests skipped),
test_station_lease (4 pass). Total 116 passing tests, 2 optional skips.
Launcher tests execute the public main entry point through source links in two
independent temporary Git consumers, replacing only the live launch boundary.
SampleReview's real wrapper `python3 scripts/launch_remote_station.py --help`
exposes the new controls through its existing shared link.

The guard suite initially failed before any guard execution because its copied
fixture still declared the retired project.v1 schema. Expanded test ownership to
that fixture, adopted canonical CONFIG, and exposed startup stderr for failures;
all executable guard cases then passed. Production guard/lease code is unchanged.
The initial structure gate rejected linking a new open follow-up to terminal
RFC-ASK-0003; this independent enhancement uses rfcs: [] without reopening history.

`python3 -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only`,
`python3 -B scripts/verify_documentation.py --root .` (9 RFCs, 47 cards, no violations),
and `git diff --check` passed. Source manifest regenerated with the authoring helper.
Test temporary directories were removed. No live resets, daemon launches, pushes,
registry updates or platform-native claims. Existing source links observe this edit.
