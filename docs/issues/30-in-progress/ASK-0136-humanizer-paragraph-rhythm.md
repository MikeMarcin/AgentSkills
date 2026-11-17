---
schema: "implement-rfc.card.v1"
id: "ASK-0136"
title: "Check paragraph rhythm in the technical book humanizer"
status: "In Progress"
rfcs: []
depends_on: []
metadata: {"baseline":"6e3d868070a0a17e149e287d78f75b25529c1db6","requested_on":"2026-11-17"}
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
