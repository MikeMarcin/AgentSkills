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
