---
schema: "implement-rfc.card.v1"
id: "ASK-0131"
title: "Machine-wide default hub for attended-review publication"
status: "In Progress"
rfcs: ["RFC-ASK-0018"]
depends_on: []
priority: "P1"
metadata: {"milestone_plan":{"id":"review-hub-publisher","path":"docs/rfcs/plans/review-hub-publisher/milestone-plan.json"},"amendment":"owner-2026-11-04-machine-hub-default"}
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
