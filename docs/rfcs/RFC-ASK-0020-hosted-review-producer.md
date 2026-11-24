---
id: "RFC-ASK-0020"
title: "Publish and receive hosted attended reviews"
status: "Implementing"
metadata: {"milestone_plan":{"id":"hosted-review-producer","path":"docs/rfcs/plans/hosted-review-producer/milestone-plan.json"}}
---

# Publish and receive hosted attended reviews

On 2026-11-24 the owner authorized the native AgentSkills producer integration
with local commits and loopback verification. The hub owns the hosted v1 wire
contract in `docs/hosted-reviews.md` at AttendedReviewHub `c9e38c56ae9902baa57850a5e5b64d90a16fb5b0`.
The source requirements are RFC-ARH-0003 and RFC-ARH-0004. This work covers the
producer counterpart and native integration prerequisite ARH-0012.

Add an explicit hosted mode for a newly prepared review. Capture the selected
content, candidate bindings and allowed media in an immutable package. Persist
enrollment binding and publication receipts without credentials. Prevent local
decision and publish-through paths from becoming competing writers for a hosted
review. Keep legacy pass-through and archived JSON readers compatible.

The enrolled producer resumes publication and retrieves its exact frozen
handback without an origin listener. Verify version, digest, bindings and current
local candidate identity before writing. Use the existing durable storage and
archive mechanisms so a retry after interruption yields one logical local
Hand Back, with ACK sent only after durable output. Conflicts require attention
and must preserve existing work. Keep credentials and material out of ordinary
output. Live rollout and consumer installation are outside this scope.

- **AC01** Native commands publish explicitly selected prepared content, recover
  idempotently across interruption, and enforce a single hosted decision writer.
- **AC02** Against the hub, an offline origin recovers a frozen delivery, writes
  existing searchable JSON through the exact Hand Back marker, and ACKs once
  durable. Replay, failed writes, wrong bindings and existing conflicts preserve
  truthful status and unrelated results.
- **AC03** An unchanged legacy reader reads the result. Pass-through behavior
  remains compatible and hosted transport authenticates its configured TLS
  endpoint without redirecting credentials.

[Work card](../issues/60-done/ASK-0141-hosted-review-producer.md) and
[closeout](../issues/20-ready/ASK-0142-close-hosted-review-producer.md).
