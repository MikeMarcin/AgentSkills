# Selected skill migration, 2026-09-05

The user approved seven imports and the following deployment scopes. All live
changes used MASK's public CLI with matching previews and plan guards. No source
fetch/update, push, publication, or credential changes were performed.

| Consumer | Selected skills added or enrolled | Agent targets |
|---|---|---|
| Personal home | coauthoring, code-simplifier, technical-book-humanizer, instamat-image-to-pbr, existing manage-agent-skills | Claude and Codex |
| sample_studio | trellis-image-to-3d, concept-art-approval-pipeline | Claude and Codex |
| SampleAssets | sprite-sheet-animation-updater | Codex |

The three project-derived skills are not in the personal selection. SAMPLE_STUDIO keeps
its writing copies, including the pre-existing humanizer edit and the
SAMPLE_STUDIO-specific code-simplifier rules. PBR refinement, Stable Audio, SAMPLE_STUDIO agent
docs, AST release publishing, and AST promo capture remain local. SRV, PLN, LOG,
and IMG received no changes.

## Ownership and restoration

Sixteen original directories or symlinks were fingerprint-checked and moved to
`~/.mask/migration-backups/selected-skills-2026-09-05/originals/`, outside discovery
roots. The existing exact Claude manage-agent-skills link was adopted in place.
New personal links use `.agents/skills` and `.claude/skills`; the five selected
legacy `.codex/skills` entries were retired. The old sample_studio Claude wrappers were
replaced with direct managed links.

`migration.json` in that backup directory records before-trees, exact raw link
values, previews/results and completed phases. `migrate.py` can resume incomplete
phases; `RESTORE.md` describes public-CLI ownership removal and guarded restoration
from the preserved originals. These originals are intentionally retained.
No MASK internal state file was edited by the migration.

SAMPLE_STUDIO consumer commit: `970834ef0`.
SampleAssets consumer commit: `40b77fd`.
AgentSkills import commit: `b22549b`.
MASK user-scope implementation commit: `40dd1e7`.

SAMPLE_STUDIO owns the active ExampleScene profile under its consumer context. AST owns its
SampleCharacter generator and validation/build wrapper under `tools/`, plus full local
contributor instructions. AST's build and tests do not depend on private skill
access. Shared scripts resolve from their installed location, independently of
consumer working directories.

## Direct verification

- MASK integration: 80 tests passed, with three native-platform skips.
- Imports: seven package validations and seven skill-shape checks passed.
- Installed-path verification: 12 TRELLIS, four concept-review and one sprite
  scenario passed through temporary managed project/personal links from an
  unrelated working directory. The sprite scenario checks dimensions, gutters,
  and optional body detection. No remote generation or authentication occurred.
- Executable management examples: project and personal sequences passed.
- AST: all 15 SampleCharacter strips validated; the existing Swift tests and CMake debug app
  build completed with exit 0. Compilation reported warnings in untouched Swift
  actor-isolation code. No assets were regenerated.
- SAMPLE_STUDIO: focused agent-doc validation passed all six checks with zero errors or
  warnings; the pre-existing humanizer bytes remain unchanged.
- Live: personal, sample_studio and AST plans converged and `doctor --check` passed.

This is native macOS filesystem and command evidence. Native Windows user-scope
behavior and actual loading by already-running agent UIs were not verified.
