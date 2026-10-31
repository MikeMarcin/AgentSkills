---
id: "RFC-DRAFT-0002"
title: "Always-on review hub service on the owner's NAS"
status: "Proposed"
---

# Always-on review hub service on the owner's NAS

Part of the [review hub pack](../README.md). Session records come from
[RFC-DRAFT-0001](RFC-DRAFT-0001-review-hub-session-publication.md). Cards:
[DRAFT-0002](../issues/DRAFT-0002-hub-service.md),
[DRAFT-0003](../issues/DRAFT-0003-hub-push.md), closeout
[DRAFT-0005](../issues/DRAFT-0005-closeout-hub-service.md).
Decisions: [design record](../DECISIONS.md).

## Problem and grounded current behavior

Session records need a fixed, always-reachable place to collect them. Laptops sleep
and move, so no review machine can serve as that place. The owner chose an always-on
hub on their NAS, running in Docker and reachable over Tailscale Serve
([D1, D2](../DECISIONS.md)).

This repository's [AGENTS.md](../../../../../AGENTS.md) rules out daemons and fleet
sync in the skill library, and puts program runtime code in ManageAgentSkills. The
hub is therefore a separate deployable service. The skill library only defines the
record contract and the optional client. Where the service code lives is open
([D4](../DECISIONS.md)).

## Proposed behavior and boundaries

### Deployment

A Docker Compose stack with `restart: unless-stopped`:

- **hub:** a Python 3.11 standard-library HTTP service with SQLite on a mounted
  `/data` volume, plus a `/healthz` healthcheck.
- **tailscale:** the official Tailscale container, sharing its network with hub,
  exposing hub over Tailscale Serve HTTPS under its own node name. The hub has no
  LAN-facing or published host port. Funnel is never enabled.
- **ntfy:** a self-hosted ntfy server (see Push), on the same tailnet-only network.

The owner creates the tagged auth key, ACL rules and ntfy users. These secrets live
in an env file on the NAS and never in a repository. The stack does not publish
images to any registry.

### Access

The hub trusts only requests that arrive through its Tailscale Serve proxy and carry
a `Tailscale-User-Login` header matching a configured allowlist (the owner's login).
Requests without a matching identity get 403 on every route except `/healthz`.

### API and page

- `PUT /api/sessions/{session_id}` stores the latest version-1 record. A record
  with a lower `sequence` than the stored one is ignored. An invalid record gets a
  400 and is not stored.
- `GET /` lists sessions grouped by machine, then repository, oldest wait first.
  Each row shows harness, state, counts, last update and an open link to `url`.
- A session with no record for 15 minutes (3 missed heartbeats) shows as **stale**
  with its last known counts. It is not removed. A `stopped` session leaves the
  default list after 24 hours. Removing a record is a manual page action.
- While open, the page refreshes at least every 30 seconds and may show a browser
  notification when a session gains ready items.
- The hub stores, lists and links only. It never records answers, approvals or
  handbacks, and never contacts a session.

### Push

When a session's `ready` count rises from zero, or rises after the session has had
no notification for 10 minutes, the hub posts one message to a configured ntfy
topic with a hub token. The message is `<repo> on <machine>: <n> items ready` and
links to the hub page. It never includes the session URL or review content.

Android uses the ntfy app connected directly to the tailnet ntfy server. Desktop
computers use the pinned hub page. iOS delivery, which needs the public ntfy.sh
upstream relay, is deferred ([D6](../DECISIONS.md)).

## Acceptance

- **AC01:** The started stack serves the hub only through its Tailscale Serve HTTPS
  name. No port is reachable on the NAS LAN address, and Funnel is off.
- **AC02:** A request without an allowlisted `Tailscale-User-Login` gets 403 on the
  page and API, and stores nothing.
- **AC03:** After records from two machines and repositories arrive, the page lists
  both grouped by machine and repository, with counts and working open links. A
  lower-sequence record does not replace a newer one.
- **AC04:** A session silent for 15 minutes shows as stale with last known counts.
  A stopped session leaves the default list after 24 hours.
- **AC05:** A record that cannot be stored gets a 4xx response, and no route
  changes any review session's state.
- **AC06:** A ready count rising from zero produces exactly one ntfy message without
  session URL or content. Repeated updates within 10 minutes produce none.
- **AC07:** The ntfy server refuses anonymous subscription and publication, and
  with the upstream relay disabled, no notification request leaves the tailnet.
