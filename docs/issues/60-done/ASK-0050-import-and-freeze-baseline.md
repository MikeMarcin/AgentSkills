---
schema: "implement-rfc.card.v1"
id: "ASK-0050"
title: "Import the coordinator pack and freeze the real baseline"
status: "Done"
rfcs: ["RFC-ASK-0010"]
depends_on: []
metadata: {"packet": "agent-skills-interactive-coordinator-2026-09-08", "provisional_id": false, "packet_key": "import-and-freeze-baseline", "milestone": "intake"}
acceptance: [{"criterion":"RFC-ASK-0010-AC14-intake","outcome":"pass","revision":"e2e8d21e8d59b3de7180538f3e889b5ee3802b8a","evidence":{"kind":"observation","detail":"Imported live RFC and nine reserved cards; baseline 9f991d9027a1aaa9bd9827eb4c51ef6d33432f7a, complete original packet and mapping retained. Documentation gate: 10 RFCs, 58 cards, zero structural violations. Scoped validation passed with one closeout and only dependency-satisfied intake Ready. Packet validator passed; 23 mutation tests passed, one filesystem-specific skip."}}]
---

# ASK-0050: Import the coordinator pack and freeze the real baseline

Governing RFC: [RFC-ASK-0010](../../rfcs/RFC-ASK-0010-interactive-coordinator-and-milestone-integrators.md).

## Objective and owned paths

Follow [IMPORT.md](../../rfcs/assets/agent-skills-interactive-coordinator-2026-09-08/IMPORT.md). Inspect live IDs/source changes and reserve nine real IDs on main through the public allocator; commit its returned counter/receipt before use. Import the new live RFC/cards with a complete mapping, preserve historical packs and record the actual RFC_BASE_SHA before source implementation. Record candidate adoption scope and the current engineering route independently of the coordinator target.

Owned paths:

- `docs/rfcs/new RFC and index row`
- `docs/issues/new cards, NEXT_ID and allocator reservation`
- `docs/rfcs/assets/new retained pack and LIVE_IMPORT`

## Acceptance

- The retained packet and live board have distinct identities; exactly one closeout covers the RFC.
- The actual baseline, live ID map and source deltas are recorded, with no fabricated commits or native evidence.
- Only dependency-satisfied work is Ready; the live scoped queue finds the next card.

Criterion coverage: RFC-ASK-0010-AC14.

## Focused verification

- Packet validator; existing documentation gate; scoped issue_board queue/validate and exact Git diff.

## Run record

Not started. No native run, source implementation, reservation, accepted work or
measured saving is claimed by this packet. Claim the live card before source work,
preserve unrelated changes and commit only explicit owned paths.

Intake verified at e2e8d21. Owner accepted implementation on 2026-09-08. Engineering route remains the current GPT-6 Astra session; no runtime model change is asserted. Real adoption scope is limited to AgentSkills owned development outputs after qualification; temporary fixtures cover other consumers.
