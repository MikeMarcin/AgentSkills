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
Decisions: [design record](../DECISIONS.md). Grouping: [canonical plan](../milestone-plan.json).

## Problem and grounded current behavior

Session records need a fixed place to collect them while laptops sleep and move.
The owner chose an always-on
hub on their NAS, running in Docker and reachable over Tailscale Serve
([D1, D2](../DECISIONS.md)).

The owner selected a **new standalone repository** for the service during this
review (D4). AgentSkills retains the optional publisher and wire contract.
The [repository rules](../../../../../AGENTS.md) and
[consumer context](../../../../../.mask/skill-config/implement-rfc/project.md)
do not make this new daemon part of MASK. The hub's RFC/cards will be imported into
its own repository, with an external prerequisite on the verified publisher.
The [implementation entrypoint](../IMPLEMENTATION_PROMPT.md) describes that handoff.

## Proposed behavior and boundaries

### Deployment

A Docker Compose stack with `restart: unless-stopped`, built locally:

- **hub:** a Python 3.11 standard-library HTTP service with SQLite on a mounted
  `/data` volume, plus a minimal `/healthz` healthcheck. Records and hub metadata
  survive container restart.
- **tailscale:** the official Tailscale container, with persistent node state and
  explicit Serve configuration. Hub shares its network namespace and listens only
  on `127.0.0.1`; only Serve reaches that listener. Do not publish host ports or use
  host networking. The hub has a dedicated HTTPS origin; Funnel stays disabled.
- **ntfy:** an optional Compose profile, introduced by the hub-push milestone.
  It listens on loopback in the same namespace and is served at `/` on a separate
  configured HTTPS port. The Android server URL and allowed tailnet port are
  explicit deployment settings. The hub-service milestone runs without ntfy.

Pin tested image versions when implementing. The owner supplies the NAS location,
tailnet registration, access grants, HTTPS setup and ntfy accounts as needed for
deployment. Keep keys, tokens, databases and private env/config files off Git.
The source task prepares the stack and setup instructions; operating the NAS or
changing access requires that deployment scope. Nothing publishes an image.

### Access

Per D8, v1 authorizes any device that can reach the hub's Serve endpoint over the
tailnet, including tagged source machines. The hub performs no identity-header,
app-capability or application-credential check. The owner's Tailscale access rules
are the only access boundary; because every reachable device can list live review
capability URLs, those rules should limit the hub to the owner's devices.
The hub still listens only on loopback behind Serve, so LAN clients cannot reach it.
Per-user or publish-only authorization is deferred.
The service repository's README states this limitation plainly: any device that
can reach the hub over the tailnet can see and open every listed live review.
The owner is the only current user (D8).

### API and page

`PUT /api/sessions/{session_id}` accepts only the exact record contract in
RFC-DRAFT-0001: matching path/body ID, enums, nonnegative integer counts and their
sum, sequence/revision types, UTC timestamp, bounded labels and a nullable review
URL. Use a 16 KiB request limit. Review URLs must be HTTPS in the configured
tailnet DNS suffix, with the capability fragment and no userinfo or unexpected
path/query; a stopped record must have a null URL and other states a valid URL.
Reject invalid records with 400, oversized input with 413, and storage failure
with 5xx. A success response requires durable storage; it must not mislabel a
server failure as bad client input. Receipt bodies contain no saved capabilities.

Compare `publication_revision`, not `sequence` or sender time. A greater revision
atomically replaces the snapshot. An identical equal-revision record is a
heartbeat; a different equal-revision record gets 409. Lower revisions are
acknowledged as ignored without changing data or freshness. Successful new records
and identical heartbeats record hub-owned `received_at`. Keep ordering, receipt
times and notification bookkeeping across restarts. A stopped snapshot cannot be
revived by a delayed older update; a genuinely newer restart can revive it.

`GET /` and its same-origin listing API group by machine, then repository. Each
row shows harness, state, disjoint counts, receipt time and an open link when a
URL exists. Within a group, sort actionable rows by the hub's first receipt of the
current uninterrupted ready wait, oldest first; other rows follow. A heartbeat
does not reset that wait. Readiness for attention means `state == ready` and
`counts.ready > 0`; paused, handed-back, idle and stopped rows are distinguishable.

After 15 minutes without an accepted receipt, a non-stopped session is **stale**
with its last counts and a warning that its link may be unavailable. Staleness
overlays the reported state, does not remove it and does not itself announce new
ready work. A newer snapshot or identical heartbeat clears staleness. A stopped
row leaves the default list 24 hours after its first accepted transition to
stopped; duplicate stopped receipts do not reset that interval. Keep an inactive
view. Offline publishers' clocks cannot change these intervals.

An owner page action can remove a row through `DELETE /api/sessions/{session_id}`.
It removes that hub record only, and explains that a still-running publisher can
recreate it on its next accepted publication. Preserve the revision floor and
notification quiet period in a tombstone: older or conflicting equal-revision
requests cannot resurrect it. An identical heartbeat may restore visibility but
is not a new readiness increase. This action never stops a session or releases
its protections.

The page refreshes at least every 30 seconds while active, showing fetch failures
instead of silently presenting old data as current. Optional foreground browser
notifications require the user's browser permission and follow the ready-increase
rule; no background Web Push is implied. The hub stores, lists and links only.
It never records review decisions, prepares candidates or contacts session URLs.

### Capability protection

Treat every label and URL as untrusted input: render labels as text and allow only
validated links. Use `Cache-Control: no-store`, `Referrer-Policy: no-referrer`,
`noopener noreferrer` links, and a restrictive same-origin CSP with no third-party
scripts, analytics, embeds or previews. Do not log request bodies or session URLs.
The mounted data is private because it holds live review capabilities.

Browser mutations require the exact configured Origin; publish clients may omit
Origin, but a supplied foreign Origin is refused. Require JSON for publication,
reject cross-origin API access and permit deletion only through the owner action,
never a GET. Authentication and input validation apply to the listing API as well
as the page; receipt responses never echo stored records.

### Push

Push is optional. Define the effective ready count as `counts.ready` in the ready
state, otherwise zero. A newly accepted snapshot that increases it, including a
session's first positive record, qualifies for one notification attempt, provided
at least 10 minutes have elapsed since the previous attempt for that session.
The quiet period applies even to another zero-to-positive transition and survives
restart. Identical heartbeats, out-of-order records, unchanged counts and stale
recovery alone do not trigger push. Changes suppressed during the quiet period
do not schedule a delayed reminder; the page remains the current queue.

Reserve an attempt durably before sending and process it outside record intake.
Before sending, discard it if the session has become stale, inactive or removed;
use its current ready count. Delivery failure leaves the accepted record usable
and creates a redacted operational warning. Do not retry an uncertain delivery
or replay reserved attempts after a crash: exactly-once delivery cannot be
promised across the hub/ntfy boundary. A later qualifying increase can try again
after the quiet period. This policy favors avoiding duplicate interruptions over
guaranteed delivery.

Send `<repo> on <machine>: <n> items ready`, linking only to the hub page. This is
private summary metadata, without session capabilities or review content. Configure
ntfy default access as `deny-all`, with a dedicated topic, a publish-only hub account
and a read-only phone account; their tokens inherit those account permissions.
Disable public upstream, Firebase and Web Push forwarding, along with unrelated
outbound notification integrations. See [ntfy access and forwarding configuration](https://docs.ntfy.sh/config/).

Android connects to the configured tailnet ntfy HTTPS origin using its
[instant-delivery service](https://docs.ntfy.sh/subscribe/phone/#instant-delivery).
Delivery needs Tailscale connectivity and the app's background/notification
permissions; verify it with the phone screen off. Desktop use is the pinned hub
page. iOS push remains deferred (D6). Notification content stays with the self-hosted
service and authorized tailnet clients; this does not promise an absence of normal
Tailscale coordination or encrypted relay traffic.

## Acceptance

- **AC01:** The hub-only stack exposes only its intended Serve HTTPS endpoint,
  with persistent state, no reachable backend/LAN ports and
  Funnel disabled. Record an actual NAS deployment observation for this boundary.
- **AC02:** A tailnet device, including a tagged one, can publish and view through
  Serve without credentials, and the backend is unreachable except through Serve.
- **AC03:** Two machines/repositories appear with correct grouping, wait order,
  counts and full working capability links. Reordered, equal-conflicting and
  restart/stop records obey revision precedence, including after hub restart.
- **AC04:** Hub receipt time governs stale and stopped visibility despite skewed
  client clocks, duplicates and hub restart; removal/republication follows its
  documented semantics without affecting the review session.
- **AC05:** Invalid, oversized and unstorable records return the defined errors
  without partial storage; successful receipts are durable and no route operates
  a review session.
- **AC06:** A qualifying ready increase causes one best-effort attempt. Duplicates,
  repeated zero crossings, unchanged heartbeats, restart and failure respect the
  quiet period, privacy and intake-isolation contract.
- **AC07:** The push profile preserves the deployment boundary, ntfy denies
  anonymous or excessive account access, external forwarding is disabled, and a
  subscribed Android phone receives the summary and hub link
  while its screen is off. Fixture-only results leave phone acceptance open.
- **AC08:** Hostile labels/URLs, cross-origin mutations cannot expose capabilities; the page, headers, logs and notifications satisfy
  Capability protection.
