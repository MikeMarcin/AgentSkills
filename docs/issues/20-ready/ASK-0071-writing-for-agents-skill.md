---
schema: "implement-rfc.card.v1"
id: "ASK-0071"
title: "Adapt writing-for-agents as a portable AgentSkills skill"
status: "Ready"
rfcs: []
depends_on: []
priority: "P2"
metadata: {"origin": "user request 2026-09-11: port matt-skills writing-for-agents to AgentSkills the way wizard was ported (ASK-0011)", "skills": ["writing-for-agents"], "upstream": {"repository": "https://github.com/mattpocock/skills.git", "path": "skills/productivity/writing-for-agents", "commit": "3cca18b368ae95cdbdebbff572ccafa662551015", "tree": "ad2925850efb8973a72d2e666f7a975f9a2d4a9b", "license": "MIT, Copyright (c) 2026 Matt Pocock"}}
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
