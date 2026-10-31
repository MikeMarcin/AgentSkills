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
Decisions: [design record](../DECISIONS.md).

## Problem and grounded current behavior

The owner runs attended reviews across several projects, harnesses (Claude, Codex)
and machines. The only place a review URL appears is the chat that started it.
This makes it hard to see which reviews are waiting.

Each session already has what a hub needs:

- A random session `id` and a durable event `sequence` in
  `.mask/attended-review/session.json`
  ([attended_review.py](../../../../../skills/attended-review/scripts/attended_review.py),
  state creation near line 347).
- `serve --tailscale` records a private HTTPS `origin` for the host
  (`host["tailscale"]`, near line 1050). The page URL is a capability URL.
- `status` reports per-candidate readiness and answers
  ([session contract](../../../../../skills/attended-review/references/session-contract.md)).

There is no record of active sessions that outlives the chat, and no way to
announce one anywhere else.

## Proposed behavior and boundaries

### Hub configuration

Publication is opt-in. A session publishes only when a hub URL is configured,
through `ATTENDED_REVIEW_HUB` or a `--hub URL` option on commands that change
session state. Without a hub URL, behavior and on-disk bytes are unchanged.
The hub URL must be `https://`. The client sends no credentials of its own; it
relies on the tailnet identity that the hub's Tailscale Serve proxy adds (see
RFC-DRAFT-0002).

### Session record

The client sends a version-1 JSON record with exactly these fields:

| Field | Meaning |
|---|---|
| `schema` | `attended-review.hub-record.v1` |
| `session_id` | The existing session `id` |
| `repo` | Checkout directory name, plus the `origin` remote's repository name when available |
| `machine` | Host name |
| `harness` | `claude`, `codex` or `unknown`, from the environment that ran the command |
| `url` | The served page URL, or `null` when not served |
| `state` | `preparing`, `ready`, `paused`, `stopped` |
| `counts` | `{waiting, ready, answered, total}` candidates |
| `sequence` | The session's current sequence |
| `updated_at` | UTC ISO-8601 timestamp |

The record carries no candidate titles, criteria, content, paths, comments or
verdicts. `url` is the only sensitive field, and the hub protects it.

### When to publish

The client sends the record on `serve` start, after `prepare` changes readiness,
after each recorded answer or import, on `pause`, `hand-back` and `stop`, and as a
heartbeat every 5 minutes while a host is serving. `stop` sends `state: stopped`.

### Failure isolation

Publication is best effort. Each attempt has a 3-second timeout and is never
retried in the foreground. Failures go to the session log and to a `hub` warning
in `status`. They never change review state, block intake, delay a response to the
browser, or make a command exit non-zero. The hub never sends anything back to the
session. Decisions are still recorded only through the session's own page or
`import`.

## Acceptance

- **AC01:** With no hub configured, every command's output and session-state bytes
  match current behavior for the same fixture.
- **AC02:** With a hub configured, a fixture hub receives a record matching the
  version-1 field set after `serve`, an answer, `pause` and `stop`, and the record
  contains no candidate content, criteria, paths, comments or verdicts.
- **AC03:** With the configured hub unreachable or slow (over 3 seconds), answers
  are still saved, the browser receives its response without waiting on the hub,
  commands exit 0 and `status` reports a hub warning.
- **AC04:** A non-`https://` hub URL is refused before any request is sent.
- **AC05:** While serving, a fixture hub receives a heartbeat within 5 minutes
  plus the 3-second timeout, with no change to the session sequence.
