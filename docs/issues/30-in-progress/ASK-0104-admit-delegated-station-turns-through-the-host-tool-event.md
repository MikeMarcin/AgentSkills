---
schema: implement-rfc.card.v1
id: ASK-0104
title: Admit delegated station turns through the trusted host tool event
status: "In Progress"
rfcs: []
depends_on: []
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
