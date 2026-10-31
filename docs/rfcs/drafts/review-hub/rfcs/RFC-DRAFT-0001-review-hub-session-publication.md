---
id: "RFC-DRAFT-0001"
title: "Attended-review session publication to an optional review hub"
status: "Proposed"
---

# Attended-review session publication to an optional review hub

Part of the [review hub pack](../README.md). The hub service itself is
[RFC-DRAFT-0002](RFC-DRAFT-0002-review-hub-service.md). Cards:
[DRAFT-0001](../issues/DRAFT-0001-session-publisher.md), closeout
[DRAFT-0004](../issues/DRAFT-0004-closeout-session-publication.md).
Decisions: [design record](../DECISIONS.md). Grouping: [canonical plan](../milestone-plan.json).

## Problem and grounded current behavior

The owner runs attended reviews across several projects, harnesses (Claude, Codex)
and machines. Each checkout already retains its session and URL after the chat;
there is no shared index of which checkouts need attention.

[attended_review.py](../../../../../skills/attended-review/scripts/attended_review.py)
provides the relevant facts in `Session.initialize`, `Session.status`,
`Session.hand_back` and `serve`: one durable session ID per checkout/session directory,
candidate phases and decisions, separate paused/handed-back flags, and a host URL.
Multiple harnesses sharing that directory share the session, rather than creating
one hub row per chat. The state may also live in an explicit external directory.

`serve --tailscale` records both the HTTPS origin and the complete capability URL
including `#token=...`. Host start, replacement and shutdown do **not** advance the
review event `sequence`; it cannot order hub records by itself. See the
[session contract](../../../../../skills/attended-review/references/session-contract.md)
and [transport contract](../../../../../skills/attended-review/references/tailscale-serve.md).

## Proposed behavior and boundaries

### Hub configuration

Publication is opt-in per session. `serve --hub URL` selects a destination;
otherwise `ATTENDED_REVIEW_HUB`, then the previously saved destination, applies.
`serve --no-hub` overrides both, clears the saved destination and cancels pending
publication. The two flags are mutually exclusive. These settings also apply when
attaching to an existing host. The running host and later mutating CLI commands
reuse the saved setting even when their shell lacks the environment variable.
Disabling cannot retract a request already sent; the old hub entry becomes stale.

The setting, publication revision and delivery diagnostics belong in separate local
publisher metadata beside the session, outside the review event stream. A session
that has never enabled publication gains no files, fields, output or network activity.

The hub URL is a Tailscale Serve HTTPS origin, with an optional port and no userinfo,
path other than `/`, query or fragment. Validate it before changing configuration;
invalid explicit configuration is a configuration error, not a delivery failure.
Verify TLS certificates and refuse redirects, so a redirect cannot disclose a
session capability to another destination. The client supplies no application
credential; the hub authorizes the proxy's tailnet identity/capability headers as
defined in RFC-DRAFT-0002.

### Session record

The client sends a version-1 JSON record with exactly these fields:

| Field | Meaning |
|---|---|
| `schema` | `attended-review.hub-record.v1` |
| `session_id` | The existing session `id`, also used in the request path |
| `repo` | Display label: checkout directory name, plus the `origin` repository basename when available |
| `machine` | Host name |
| `harness` | `claude`, `codex` or `unknown`, identifying the serving harness; later CLI callers do not relabel it |
| `url` | Complete private HTTPS review URL with its capability fragment; `null` when stopped |
| `state` | `preparing`, `ready`, `idle`, `paused`, `handed-back` or `stopped`, derived below |
| `counts` | Nonnegative integers `{waiting, ready, answered, total}`, derived below |
| `sequence` | Current review event sequence, for diagnostics |
| `publication_revision` | Positive, durable integer ordering snapshots for this session |
| `updated_at` | UTC ISO-8601 time this snapshot changed, not a freshness authority |

Each current candidate belongs to exactly one count: `answered` has a current
decision; `ready` has no decision and is both ready and protected; `waiting` is
every other unanswered candidate, including preparation/cancellation. These three
counts sum to `total`. Saved feedback alone is not an answer. Counts describe the
queue even when it is paused or handed back.

Derive state in this priority order: `stopped` when the published transport has
closed; `handed-back` when the current queue has been handed back; `paused` when
paused; `ready` when ready count is positive; `preparing` when waiting count is
positive; otherwise `idle`. A handback with unanswered ready candidates is therefore
visible without claiming approval or demanding another answer. Starting review or
changing the queue follows the existing helper's rules for clearing handback.

Only publish after this session has successfully served through Tailscale. For
later shutdown records, retain its identity and counts but clear the URL. Never
publish `local_url`, a loopback/offline link, or merely the HTTPS origin without
its token. A currently loopback-only host leaves a previously published session
stopped. Prepared-but-never-served sessions remain outside this version.

The record excludes candidate titles, criteria, content, full filesystem paths,
remote URLs, credentials, comments and verdicts. Parse only the origin repository
basename; do not copy the Git remote string. Labels and counts are private metadata;
the URL additionally grants review access. Keep payloads and tokens out of delivery
logs and warnings. The exact record keys and count keys are the wire contract;
unknown fields are rejected by the hub.

### Ordering

Every changed snapshot, including URL rotation, shutdown and restart, gets a larger
`publication_revision` persisted before transmission. Concurrent CLI and host
publishers must never assign a newer revision to an older snapshot. Restarting the
host preserves the counter; review `sequence` stays governed by existing events.
Heartbeats resend the identical snapshot and revision. Hub comparison and receipt
time are defined in RFC-DRAFT-0002; sender clocks never decide record precedence.

### When to publish

Queue publication after successful Tailscale host start/attachment, and after
committed changes from `init`, `prepare` (including failures/cancellation), `ready`,
`import`, `start`, `pause`, `hand-back` and `resume-development`. Browser answers,
withdrawals and state changes use the same path. Changes to feedback/observations
that advance the reported sequence are also reflected. Publish only committed
snapshots; a failed intake must not announce an answer.

While serving, send a heartbeat every 5 minutes. Graceful shutdown, handled
termination and transport failure attempt a final stopped snapshot. A forced kill,
machine sleep or power loss can only be detected by hub staleness. Restart announces
the new URL even when no review event has occurred.

### Failure isolation

Publication is best effort. Each network attempt has a 3-second total deadline and
no immediate retry. A bounded worker owned by the foreground review host performs
delivery after local state commits, outside review/resource locks. It may coalesce
pending updates to the latest snapshot; an outage must not grow an unbounded queue
or thread set. A later change or heartbeat can send the latest snapshot again.
There is no separate publisher daemon. When no host is running, an already-enabled
mutating CLI command may make one bounded attempt after committing locally;
graceful host exit may spend at most one such deadline on final delivery.

Delivery and publisher-metadata failures never roll back review data, hold intake
locks, delay the browser response or change the command's existing success/failure
exit status. Invalid review input still fails normally. Record a concise local
delivery diagnostic and expose the current failure as a `hub` warning in `status`;
clear it after confirmed delivery. The hub's response is only a receipt/error,
never an instruction. Decisions remain local to the session page or `import`.

## Acceptance

- **AC01:** A never-enabled fixture retains existing command output, review-state
  bytes, files and network behavior, accounting for existing random/time fields.
- **AC02:** A fixture hub observes the exact wire contract at the defined publication
  points, including CLI and browser changes; unserved/loopback material and private
  review content are absent.
- **AC03:** Slow/unreachable hubs and publisher-metadata failures preserve saved
  answers, browser responsiveness, existing exit semantics and bounded resources;
  delivery warnings appear and clear on recovery.
- **AC04:** Invalid origins, certificate failures and redirects send no capability
  to an unvalidated destination, and delivery diagnostics contain no payload/token.
- **AC05:** An available fixture hub receives a heartbeat within 5 minutes plus
  the 3-second deadline, without advancing either sequence or publication revision.
- **AC06:** Mixed candidate phases, withdrawal, pause, partial handback and resume
  produce the defined disjoint counts and states; shutdown/restart and concurrent
  callers preserve snapshot ordering even with an unchanged review sequence.
- **AC07:** Configuration precedence, reuse across shells/host attachment and
  explicit disabling work as specified, with no foreground browser network wait.
