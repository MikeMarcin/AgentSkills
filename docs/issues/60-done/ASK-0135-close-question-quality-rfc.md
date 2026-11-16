---
schema: "implement-rfc.card.v1"
id: "ASK-0135"
title: "Close checked question format RFC"
status: "Done"
rfcs: ["RFC-ASK-0019"]
depends_on: ["ASK-0134"]
closeout_for: ["RFC-ASK-0019"]
priority: "P1"
metadata: {"milestone_plan":{"id":"attended-review-question-quality","path":"docs/rfcs/plans/attended-review-question-quality/milestone-plan.json"}}
acceptance: [{"criterion": "RFC-ASK-0019-AC01", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Each kind admitted; real page renders parts in the defined order identically live and offline; identity only in provenance; headless Chrome offline and live screenshots.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC02", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "One Copy action each for launch command and step value; Reference and Now figures side by side, captioned by role.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC03", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Static prepare leaves a build waiting and unprotected with the launch-check reason; passing prepare command or ready --evidence makes it ready; failing command stays waiting.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC04", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "16 violations named at once with rule ID, part and fix; nothing saved, existing session bytes unchanged; check reports the identical list without a session.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC05", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Waived question admitted and counted; reason shown on that question and bound to its fingerprint; empty, unknown and unwaivable waivers refused.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC06", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Setup note shown on entering its group only; every question keeps a working launch copy; note binds only the group's fingerprints.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC07", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Differential against the RFC_BASE_SHA helper: v1/v2 fingerprints, outputs (except added checks) and normalized state identical; legacy violations reported as unchecked legacy format; golden fingerprints pass.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC08", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Guide example rewriting BetterPullReview BPR-2032-import-preview-b passes check at 75 driver-written words (was 416).", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}, {"criterion": "RFC-ASK-0019-AC09", "outcome": "pass", "revision": "670238c425c0e2fcaa4475df9a1368c0eaac0f14", "evidence": {"kind": "artifact", "detail": "Guide rule table equals helper rule set; contract names every rule, limit, kind and field; SKILL.md and example README agree; no migration claim.", "path": "docs/rfcs/plans/attended-review-question-quality/verification.md"}}]
---

# Close checked question format RFC

Close out [RFC-ASK-0019](../../rfcs/RFC-ASK-0019-attended-review-question-quality.md)
by verifying AC01–AC09 together against the integrated source revision.

RFC_BASE_SHA: 5fd9ad3951934469593be781e6078927c9e20c23

Planned local cards: ASK-0134 (implementation), ASK-0135 (closeout).

No human attended review is required by the RFC; none is invented here.

Closeout review runtime: local implementer self-review; no independent or human gate required.

## Verification and execution record

The [criterion checklist](../../rfcs/plans/attended-review-question-quality/verification.md)
records AC01–AC09 with commands, observations and source commit `670238c425c0e2fcaa4475df9a1368c0eaac0f14`.
ASK-0134 is Done. Run `question-quality-2026-11-15`, segment `implementation-1`,
coordinator-implementer. Changed paths: `skills/attended-review/**` (SKILL.md,
README, contract, new `references/question-authoring.md`, helper, page, tests, new
`examples/question_kinds.py`) and this RFC's records. All fixture hosts were stopped
and fixture roots were disposable; no consumer was migrated or deployed.

Pending: none for this RFC. Not performed or claimed: native Windows, other browsers,
embedding the real BetterPullReview mockup and capture in the guide example.
