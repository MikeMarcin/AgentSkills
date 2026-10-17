---
schema: "implement-rfc.card.v1"
id: "ASK-0112"
title: "Keep board link repair out of ignored generated output"
status: "In Progress"
rfcs: []
depends_on: ["ASK-0111"]
---

RFC_BASE_SHA: `eac8951b2e892b3ad0fb03c7239829b676151ea9`

AITO Pinax closeout scanned large ignored source exports, expanding its stale-read
window until an unrelated card changed. Link repair should use Git's tracked and
non-ignored untracked Markdown within the configured roots.

- **AC01:** Ignored untracked Markdown is neither scanned nor rewritten; tracked
  and ordinary untracked references still follow card moves within configured roots.
- **AC02:** Existing path safety, protected-file, rollback and stale-read checks
  pass alongside the new public-command fixture. No concurrency guard is waived.
