---
schema: "implement-rfc.card.v1"
id: "ASK-0071"
title: "Adapt writing-for-agents as a portable AgentSkills skill"
status: "Done"
rfcs: []
depends_on: []
priority: "P2"
metadata: {"origin": "user request 2026-09-11: port matt-skills writing-for-agents to AgentSkills the way wizard was ported (ASK-0011)", "skills": ["writing-for-agents"], "upstream": {"repository": "https://github.com/mattpocock/skills.git", "path": "skills/productivity/writing-for-agents", "commit": "3cca18b368ae95cdbdebbff572ccafa662551015", "tree": "ad2925850efb8973a72d2e666f7a975f9a2d4a9b", "license": "MIT, Copyright (c) 2026 Matt Pocock"}}
acceptance: [{"criterion":"portable-package-validates","outcome":"pass","revision":"096f3c80dfa1f8c6c47119b44fb6bcaa562ed0cb","evidence":{"kind":"command","detail":"mask skill validate writing-for-agents --json: valid, no issues, scope mask-package-v1. No host activation or invocation fields and no dynamic shell syntax in the package."}},{"criterion":"links-anchors-and-documentation-gate","outcome":"pass","revision":"096f3c80dfa1f8c6c47119b44fb6bcaa562ed0cb","evidence":{"kind":"command","detail":"Focused checker: every relative link and anchor in the package, README.md and skill-provenance.md resolves. verify_documentation.py: 12 RFCs, 71 cards, 0 structural violations."}},{"criterion":"tabletop-finds-planted-defects","outcome":"pass","revision":"096f3c80dfa1f8c6c47119b44fb6bcaa562ed0cb","evidence":{"kind":"observation","detail":"Sonnet tabletop on a sample skill with 17 planted defects (6 MASK-specific, 3 from the folded-in applications, 8 generic). First run on the pre-revision package found 14 plus 2 unplanted ones; after sharpening the mechanics wording and adding the obligations pruning rule, the second run found all 17 and cited the added sentences. Both runs reached references/skill-mechanics.md through the entrypoint pointer and read nothing else."}},{"criterion":"provenance-and-rewrite","outcome":"pass","revision":"096f3c80dfa1f8c6c47119b44fb6bcaa562ed0cb","evidence":{"kind":"artifact","detail":"Package README names the upstream repository, commit 3cca18b368ae95cdbdebbff572ccafa662551015, skill tree ad2925850efb8973a72d2e666f7a975f9a2d4a9b and the MIT notice, retained byte-identical to the upstream LICENSE. Shared 8-word sequences with the upstream text: 0 of 2,345; longest shared run is 7 words (a heading plus the opening of one definition)."}}]
---

# ASK-0071: Adapt writing-for-agents as a portable AgentSkills skill

## Problem

RFC-ASK-0008 and RFC-ASK-0010 apply Matt Pocock's writing-for-agents skill as an
editorial source, but only through copies retained in RFC packets. No selectable
AgentSkills package carries it, and its skill mechanics rely on host-specific
frontmatter that plain MASK packages refuse.

## Objective and owned paths

Owned paths: `skills/writing-for-agents/**`, the catalog row and authoring
pointer in `README.md`, and `docs/development/skill-provenance.md`.

## Bounded work

- Adapt the guidance the way ASK-0011 adapted wizard: keep the useful concepts,
  rewrite rather than copy, change what conflicts with plain MASK packages and
  the recorded RFC-ASK-0008/0010 applications, and credit the source.
- Skill mechanics cover portable frontmatter, selection scope as the context-load
  lever, reaching other skills by name, splitting, and the catalog as the human
  index.
- Record provenance and keep the upstream MIT notice in the package.
- Change no project or personal selection.

## Acceptance

- `mask skill validate writing-for-agents --json` passes, and the package holds
  no host-specific fields or dynamic shell syntax.
- Package links resolve and the documentation gate passes.
- A tabletop agent given only the package and a flawed sample skill finds the
  planted defects, including the MASK-specific ones.
- Provenance names the upstream commit and license, and the text is shown not to
  be a verbatim copy.

## Verification and execution record

Source revision 096f3c8. `mask skill validate writing-for-agents --json` is
valid with no issues; `--all` is unchanged apart from the pre-existing untracked
`skills/.DS_Store` entry. A focused checker confirmed that every relative link
and anchor in the package and in the two edited documents resolves, that no file
carries dynamic shell syntax, and that the retained notice is byte-identical to
the upstream `LICENSE`. The documentation gate reports 12 RFCs, 71 cards and 0
violations.

Rewrite evidence: the package shares 0 eight-word sequences with the upstream
text (2,345 in the port), and its longest shared run is the seven-word heading
and definition opening of "Leading words". SKILL.md is 1,842 words against the
source's 1,777; the mechanics reference is 521 against 414.

Tabletop, 2026-09-11: a fresh Sonnet agent was given only this package and a
sample skill carrying 17 planted defects (6 MASK-specific, 3 from the folded-in
applications, 8 generic). The first run found 14, missing the block-scalar
description, the unguarded publish step and the vague quality word standing in
for an obligation; that run also found two defects that were not planted. The
mechanics wording was sharpened and a pruning rule was added so obligations,
authority boundaries and uncertainty survive compression. The second run on the
revised package found all 17 and cited the new sentences. Both runs reached
`references/skill-mechanics.md` through the entrypoint pointer and read nothing
else. The scoring key was visible in a directory listing during the first run;
the agent reported leaving it unopened, and it was moved before the second run.

No consumer or personal selection changed; `.mask.json` is untouched.
