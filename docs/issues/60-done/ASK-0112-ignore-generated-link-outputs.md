---
schema: "implement-rfc.card.v1"
id: "ASK-0112"
title: "Keep board link repair out of ignored generated output"
status: "Done"
rfcs: []
depends_on: ["ASK-0111"]
acceptance: [{"criterion":"AC01","outcome":"pass","revision":"91a1174835b4e4da7ad18772f5d576c7de84949a","evidence":{"kind":"observation","detail":"Public fixture leaves ignored generated Markdown byte-identical and repairs both tracked (even if ignored by a later rule) and ordinary untracked references within configured roots."}},{"criterion":"AC02","outcome":"pass","revision":"91a1174835b4e4da7ad18772f5d576c7de84949a","evidence":{"kind":"observation","detail":"33 issue-board and 11 unified-workflow tests pass, including path safety, protected links, rollback, stale reads and claim/finish. Portable source manifest regenerated and validation passes. No concurrency checks relaxed."}}]
---

RFC_BASE_SHA: `eac8951b2e892b3ad0fb03c7239829b676151ea9`

AITO Pinax closeout scanned large ignored source exports, expanding its stale-read
window until an unrelated card changed. Link repair should use Git's tracked and
non-ignored untracked Markdown within the configured roots.

- **AC01:** Ignored untracked Markdown is neither scanned nor rewritten; tracked
  and ordinary untracked references still follow card moves within configured roots.
- **AC02:** Existing path safety, protected-file, rollback and stale-read checks
  pass alongside the new public-command fixture. No concurrency guard is waived.
