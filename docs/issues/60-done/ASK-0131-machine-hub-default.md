---
schema: "implement-rfc.card.v1"
id: "ASK-0131"
title: "Machine-wide default hub for attended-review publication"
status: "Done"
rfcs: ["RFC-ASK-0018"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"review-hub-publisher","path":"docs/rfcs/plans/review-hub-publisher/milestone-plan.json"},"amendment":"owner-2026-11-04-machine-hub-default"}
acceptance: [{"criterion":"RFC-ASK-0018-AC08","outcome":"pass","revision":"5f770a6a18650b9414621098663e8e6436dc1f53","evidence":{"kind":"artifact","path":"docs/rfcs/plans/review-hub-publisher/verification.md","detail":"Disposable ATTENDED_REVIEW_HUB_CONFIG paths and fixture hubs: hub-config set validates first, writes 0600 atomically, show/clear report; a never-enabled session adopts the machine default when served via Tailscale (harness codex, later plain-shell CLI reused); --no-hub saved disable, --hub saved destination and ATTENDED_REVIEW_HUB each outrank the file; a machine-sourced destination follows file changes; invalid schema/origin, non-JSON and unreadable files publish nothing, keep exit 0 and warn in status without file content; missing file: no files, fields or requests (AC01 differential identical vs RFC_BASE_SHA). Suite 53 OK."}}]
---

# Machine-wide default hub for attended-review publication

Implement owner-amended [RFC-ASK-0018](../../rfcs/RFC-ASK-0018-review-hub-session-publication.md)
AC08 in `skills/attended-review`: a per-user machine file supplies the
lowest-precedence hub destination, so every session served through Tailscale on
a configured machine publishes without per-session flags, from Claude, Codex or a
plain shell. Add the `hub-config set|show|clear` helper and document it in the
session contract, SKILL.md and README.

Preserve AC01-AC07 and their evidence. A missing machine file keeps exact current
behavior. Tests use disposable `ATTENDED_REVIEW_HUB_CONFIG` paths and fixture
hubs only; never write the real user configuration, upgrade consumers or push.
