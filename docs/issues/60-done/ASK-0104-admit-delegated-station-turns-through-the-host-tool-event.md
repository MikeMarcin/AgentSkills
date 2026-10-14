---
schema: implement-rfc.card.v1
id: ASK-0104
title: Admit delegated station turns through the trusted host tool event
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"command","detail":"56 focused guard/parser cases include exact quoted native py grammar, size/malformed/duplicate/unknown payload refusal, copied helper/shell/caller-identity rejection, and direct CLI non-admission."}},{"criterion":"AC2","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"observation","detail":"Actual EXAMPLE-HOST PreToolUse admitted distinct host turns REDACTED-SESSION-007 and REDACTED-SESSION-008 at unchanged stn-39ef5ffb/generation0/endpoint and held PID55408 lease. 168 installed source blobs and helper digest matched the committed candidate. Source FF and native probe tools executed; no restart or manual state seed. Receipts: native-admission-sync-receipt.json and native-initial-probe/receipt.json. Negative tests preserve lifecycle/checkout/origin/branch/base/expiry/authority/lease checks and refuse authority replacement."}},{"criterion":"AC3","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"command","detail":"Wrong-turn tools, replay after Stop, expired requests and receipt capacity/storage failure refused in focused tests; fresh consecutive host turns each had their own actual admission. First authorization was cleared by Stop. Source/doc/diff gates passed."}},{"criterion":"AC4","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"observation","detail":"Actual EXAMPLE-HOST PreToolUse admitted distinct host turns REDACTED-SESSION-007 and REDACTED-SESSION-008 at unchanged stn-39ef5ffb/generation0/endpoint and held PID55408 lease. 168 installed source blobs and helper digest matched the committed candidate. Source FF and native probe tools executed; no restart or manual state seed. Receipts: native-admission-sync-receipt.json and native-initial-probe/receipt.json."}}]
---

# Admit delegated station turns through the trusted host tool event

Continue the same authorized AITO Windows endpoint under its expected held
supervisor lease when Codex delegation supplies a tool-output item rather than
a user prompt. This is a bounded prerequisite of ENT-0058 under mandate-4.

## Observed failure and design

Codex 0.160.0's actual runtime log records `TurnInput` containing a
`FunctionCallOutput` from `codex_app.send_message_to_thread`, wrapped in
`codex_delegation`. The current app builds `toolOutput` with an empty text-input
array. The configured UserPromptSubmit hook does not run for this delivery;
PreToolUse correctly refuses the first command because no turn was admitted.
The current station, task, main branch and held integrator lease remain valid.
The exposed send tool has no text-input override; the existing owner proxy is
unavailable before RPC. No alternate server or ownership transfer is implied.

Add one public installed request helper accepting only a bounded base64 JSON
remote-task envelope. The exact helper command is recognized by PreToolUse,
which validates the actual host session and turn plus every existing lifecycle,
checkout, envelope, authority, ancestry, expiry and expected-lease check before
writing admission. The request CLI validates syntax and acknowledges that the
hook controls admission; it has no state writer or caller identity arguments.
Reject alternate helper copies, interpreter commands, shell prefixes/suffixes,
unknown or duplicate envelope fields, and reused admission tasks. Preserve the
normal UserPromptSubmit route and ordinary tool enforcement.

## Acceptance

- AC1: Only the exact installed helper command can request admission. Bounded
  strict payload/command parsing rejects malformed base64, size excess, copied
  paths, shell composition and caller-supplied identity. Direct CLI execution
  never writes admission or claims host acceptance.
- AC2: Admission uses the trusted host event session and turn and preserves
  every station/lifecycle/checkout/branch/base/expiry/authority/held-lease check.
  Failed requests create no authorization. Existing accepted authority cannot
  be widened by a later request in that turn.
- AC3: Ordinary tools still require their exact accepted turn. Expired requests,
  wrong-turn state, repeated tasks and replay after Stop fail. Stop clears the
  current authorization; each new turn needs fresh admission. Focused tests,
  portable-source/documentation gates and diff hygiene pass.
- AC4: The actual bound Windows host accepts the exact request under PreToolUse
  and executes two successive real delegated turns with fresh task identities.
  Record hook source event, actual session/turn, source revision and unchanged
  station/endpoint/lease. Fixtures alone cannot pass this criterion.

No manual turn-state seeding, transcript authority scanning, guard disablement,
registry normalization, MASK internals, app-binary edits, new user-facing chat,
supervisor restart or fabricated native Natvis acceptance.

## Implementation checkpoint — 2026-10-04

The exact installed `station_task_admission.py` command, or its same resolved
installed link target, now requests admission through actual PreToolUse. The
hook supplies identity and performs all existing live validation before writing
the turn record. Optional checkout paths must match the live root. The CLI has
only one payload argument and no state-writing dependency. Strict JSON rejects
duplicate/unknown fields; independent tasks may have empty RFC/card arrays,
matching the existing runtime envelope contract and updated schema.

Request receipts retain used task IDs after Stop, with a 4,096-receipt cap per
endpoint session. Each request and retry needs a fresh task ID. Receipt/storage
failure refuses admission; a retained partial receipt prevents replay. Repeated
requests cannot replace admitted authority. Request expiry is checked on later
tools. The ordinary prompt path remains available. Configuration failures now
emit the documented PreToolUse deny shape rather than a generic block object.

Focused verification passed 56 guard/parser tests, including canonical and exact
former station markers, linked consumers, quoted Windows `py -3 -B` grammar,
malformed/oversized/duplicate payloads, copied paths/shell composition, direct CLI
non-admission, caller/wrong host identity, checkout/origin/branch/base/expiry,
authority/lease/lifecycle refusal, replay/Stop/capacity and storage failure.
Four focused station-control cases passed for held/stale lease reporting, former
registry identity, interrupted transfer/retirement and fresh-generation fencing.
The source and documentation gates passed (15 RFCs, 104 cards, zero violations),
and diff hygiene passed. Commands/logs are retained in the AITO milestone's
ignored `ent0058/ask0104-guard-tests.log` and `ask0104-control-tests.log` receipts.

The initial focused run exposed a test fixture's unresolved temporary-root
comparison and unclosed replacement-holder pipes; both fixture issues were
corrected before the final pass. A configuration-refusal case also identified
the generic block output, which is now a PreToolUse denial. Local source review
confirmed that the request CLI cannot import the guard/state writer, live
validation precedes all authorization writes, and receipts confer no authority.

AC4 remains pending until the coordinator returns the actual Windows host
source-event receipt and two consecutive fresh delegated turns at unchanged
station/endpoint/lease. No native acceptance is inferred from fixture tests.
Unrelated `.mask.lock.json` is preserved; no AgentSkills push is authorized.

## Actual native closeout — 2026-10-04

The same registered Windows task accepted the exact resolved installed-helper
command through actual PreToolUse on source
`4c0f70c490445780dd8bb5805481d0da326a4bf3`. The host supplied session
`REDACTED-SESSION-006` and distinct turns
`REDACTED-SESSION-007` / task
`task-20261004-native-admission-sync-0628`, then
`REDACTED-SESSION-008` / task
`task-20261004-native-ent0058-probe-0633`. Both state records name
`admission_source: PreToolUse`; two persistent task-use receipts remain, while
Stop removed the first turn's authorization before the second request.

The first turn fast-forwarded AITO normally from `90567fdc` to `b85337da` and
verified 168 exact package blobs and helper SHA-256
`8b141ab07f1e9072c32a6e12307ea8ab569a213ec0034aaaef182f38edff0922`.
The second turn configured and ran the native build/test probe. Registry,
endpoint, authority, generation 0 and held lease PID 55408 / supervisor PID 7836
were unchanged before and after. No caller identity, simulated event, manual
state seed, restart or physical intervention supplied admission.

Actual receipts are retained in AITO's existing run directory as
`ent0058/native-admission-sync-receipt.json`,
`ent0058/native-initial-probe/receipt.json` and its station-before/after logs.
AC1–AC4 pass with those live observations and the focused source checks above.
The product probe failed independently on optimized compiler flags; this is
not native Natvis acceptance. Unrelated builders/Visual Studio work remain
untouched, and global writer quiescence is not asserted.
