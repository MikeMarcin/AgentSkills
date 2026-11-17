---
schema: "implement-rfc.card.v1"
id: "ASK-0136"
title: "Check paragraph rhythm in the technical book humanizer"
status: "Done"
rfcs: []
depends_on: []
metadata: {"baseline":"6e3d868070a0a17e149e287d78f75b25529c1db6","requested_on":"2026-11-17"}
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"6695e5f849e7b6cdf2b95a247c73c69cb74bce6a","evidence":{"kind":"observation","detail":"Cloud author and independent reviewer verified formulaic paragraph openings/closers are revised while only-after/until conditions, parallel definitions/procedures, teaching recaps and repeated technical terms are preserved. Canonical diff adds only the focused final-pass check and guardrail paragraph. No installed-skill behavior was tested."}},{"criterion":"AC2","outcome":"pass","revision":"6695e5f849e7b6cdf2b95a247c73c69cb74bce6a","evidence":{"kind":"command","detail":"Canonical SHA-256 4300ec3cf847b17be231a733b7a311169b89b294336f31ceacf52439a38c3d86, 39550 bytes. Removing the sole insertion reproduces original bytes exactly. Cloud skill-creator quick_validate.py passed. Canonical verify_documentation.py: 19 RFCs, 136 cards, 0 structural violations; issue_board validate --include ASK-0136 valid; git diff --check passed. Provenance names reviewed upstream metadata 4.0.0 and source-only scope."}}]
---

# Check paragraph rhythm in the technical book humanizer

Add a focused check to the existing final review pass for recurring paragraph
shapes and formulaic openings. Preserve technical meaning, useful repetition,
parallel definitions and procedures. Use original wording informed by the
reviewed blader/humanizer skill; import no other upstream rules or files.

Own the canonical `skills/technical-book-humanizer/SKILL.md` addition and its
entry in `docs/development/skill-provenance.md`. No installation, MASK state,
catalog, RFC or remote changes are included.

Acceptance:

- AC1: The final review pass checks neighboring paragraphs for mechanical rhythm
  and formulaic openings without imposing variety or changing technical meaning.
- AC2: All prior skill bytes remain unchanged; the provenance accurately records
  the narrow inspiration and source-only scope. Focused validation and repository
  documentation/board checks pass.
