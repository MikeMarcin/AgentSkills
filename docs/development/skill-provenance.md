# Skill provenance and licensing

On 2026-10-14 the owner adopted the root [MIT License](../../LICENSE) for original
contributions to AgentSkills and ManageAgentSkills. That grant covers this
library's original instructions, helpers and documentation; it does not replace
third-party copyright or license notices or change the origin of retained imports.

Author-rfc, grill-rfc and grill-me retain Matt Pocock's complete MIT notice in
their package `LICENSE` files. Writing-for-agents retains the complete upstream
notice in its package [README](../../skills/writing-for-agents/README.md).
Those files and retained reference notices remain byte-identical at adoption.
Preserve the applicable notices when copying or distributing adapted content.
Each skill package also carries the complete original-contribution MIT notice,
so an individual MASK installation retains it. For author-rfc, grill-rfc and
grill-me it is named `LICENSE.original`, alongside the unchanged upstream
`LICENSE`; other packages use `LICENSE`. Writing-for-agents retains its upstream
notice separately in the unchanged package README.
Historical seed and import records below continue to describe their original
sources and verification; the root license is not a new verification of those
upstream rights or an alteration of their provenance.

## Original workflow import

implement-rfc imported unchanged from supplied SRV portable archive. Original archive SHA-256: 1043f25111969b1270870b566a705f22e6f6cb253d1a4ff0de3a0c2461cc4a90. All 39 retained source files compared byte-for-byte to the supplied clean seed. See docs/rfcs/assets/mask-v1-2026-09-05/SEED-PROVENANCE.json. This import precedes shared-consumer adaptation.

On 2026-09-05, ASK-0007 refreshed the canonical skill from the local
SampleReview `.agents/skills/implement-rfc` source at
`c609655bc615e79e8e17eefc198c89861de0d90f` (portable schema-validated board
bookkeeping). Its parent payload matches the original 39-file seed, so the
refresh applies that commit's skill delta while retaining AgentSkills'
shared-consumer changes. The Claude skill is a generated shim, not the source.

The refresh imports the board model, validate/queue/move CLI, card schema,
bookkeeping reference, optional project policy and focused tests. The new CLI
uses the shared external-context resolver; tests use disposable consumer
contexts. The card schema also preserves this library's existing
`external_depends_on` references and `platform` labels. External integration
evidence remains an agent check; platform eligibility uses configured lanes.
SRV policy is retained only in the historical example. Source digests
are regenerated locally; SRV runtime adapters, embedded active context,
`.DS_Store` and Python caches are excluded. SampleReview and consumer
configurations are unchanged.

## Selected personal and project imports

The seven user-approved packages imported on 2026-09-05 are recorded in
[selected import provenance](selected-skill-imports-2026-09-05.json). Four personal
packages retain authored bytes, excluding caches. TRELLIS and concept-art retain
existing external formats; AST-specific sprite tooling stays in AST. The original
installation inventory and restorable backups are machine-local under
`~/.mask/migration-backups/selected-skills-2026-09-05/`.

## Adapted writing-for-agents

On 2026-09-11, ASK-0071 added `skills/writing-for-agents`, adapted from Matt
Pocock's MIT-licensed `writing-for-agents` (mattpocock/skills at `3cca18b`,
skill tree `ad29258`). The two upstream files are byte-identical to the
editorial copies retained under `docs/rfcs/assets/*/reference/writing-for-agents/`.
The package README records the adaptations and retains the upstream notice. No
project or personal selection changed.

`SKILL.md` first carried an original rewrite of that material. It now keeps the
upstream wording wherever the adaptation does not change the content, so
upstream revisions stay diffable; the MASK mechanics reference and the
RFC-ASK-0008/0010 additions remain this library's own. The card's recorded
rewrite evidence describes revision `096f3c8`, not the current text.

## Portable RFC authoring and grilling

RFC-ASK-0015 / ASK-0093 adds `author-rfc`, `grill-rfc` and `grill-me`. Adapted
material comes from Matt Pocock's MIT-licensed `mattpocock/skills` at
`d81f3a183412e71a5b1e84ca21bc1a35eea03a60`: `skills/engineering/grill-with-docs`,
`skills/productivity/grilling`, `skills/productivity/grill-me`, and
`skills/engineering/domain-modeling` (including glossary and ADR guidance).
Each adapted package retains the upstream notice in `LICENSE`.

The adaptation consolidates interview mechanics in grill-me, bounds rounds to
three independent questions with explicit answers, supports host discovery and
conversation without mandatory Skill-tool/subagent dispatch, and removes upstream
explicit-only metadata. Domain terminology and significant tradeoff criteria are
adapted into pack-local authoring guidance; live project adoption is separate.
The artifact/readiness/amendment contract and composition with implement-rfc's
existing offline kit are this library's additions. No selections, deployments or
upstream edits are part of this source import.

## Frontend design

On 2026-10-04, ASK-0107 added the original `skills/frontend-design` package. The
user supplied Anthropic's locally installed frontend-design skill as inspiration,
then clarified that the new skill should use original instructions rather than
copy upstream content or include its license. No upstream files are included.

The skill develops general ideas about purposeful visual choices and design
critique into an original workflow covering composition, implementation and
verification for web, mobile and desktop. Platform references and interface
metadata were authored for this package. This change adds the source package and
catalog entry; it does not select or install the skill for existing consumers.
