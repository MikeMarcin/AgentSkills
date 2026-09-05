# Project Configuration

Use this reference when the project does not already provide `.mask/skill-config/concept-art-approval-pipeline/project.md`. Keep active product paths, commands, and visual rules in that consumer file.

## Minimal Profile

Establish these fields before editing files:

```yaml
project_key: example_project
art_bible:
  root: art_bible/projects/example_project
  pages_root: src/pages
  book_manifest: book.yaml
  generated_catalog: src/generated_images.yaml
  prompt_catalog: src/prompt_catalog.yaml
  source_refs_dir: src/assets/trellis_inputs/<kit_or_pack>
  approved_reviews_dir: src/assets/<kit_or_pack>/approved_reviews
runtime:
  root: code/example_game
  generated_trellis_root: assets/generated/trellis
  provenance_manifest: assets/manifests/generated_asset_provenance.json
  runtime_asset_root: assets/runtime
  texture_repair_tool: "<optional project command>"
asset:
  key: asset_key
  prompt_id: PROJECT_AB_000
  dimensions: unknown
  role: unknown
  runtime_family: runtime/environment
visual_constraints:
  - no readable text
  - no logos
  - clean alpha refs for TRELLIS
validation:
  render_page: "<project command>"
  build_art_bible: "<project command>"
  project_checks:
    - "<project command>"
```

If fields are missing, infer them from nearby manifests and existing project conventions before inventing new paths.

## Asset State Vocabulary

Use clear state transitions:

- `draft`: concept exists but has not passed user review.
- `needs_revision`: user rejected or requested changes.
- `source_approved_needs_generation`: image refs are approved and ready for TRELLIS.
- `generated_needs_review`: model output exists but preview/model review is pending.
- `approved_for_promotion`: generated model passed review but is not wired into runtime.
- `promoted`: runtime files/manifests/bindings were updated and verified.
- `rejected`: retain only as evidence; never use as active source.

Projects may use different enum strings, but keep the semantic distinction.

## Review Board Contents

Create a single image or PDF per review attempt containing:

- asset key and prompt/catalog id
- approved or candidate view set: front, side, top, optional 3/4
- alpha/checkerboard proof, not just a flattened preview
- short description of the piece
- actual scene context or concept-art crop with callout
- repeated/module mockup when the piece is kit-bashed
- acceptance question
- current gate/status

Keep boards temporary until approved unless the project wants review artifacts saved.

## Handoff Records

For every approved asset, update or create:

- source art paths
- approved review evidence path
- alpha/keyed input paths
- TRELLIS command markdown
- prepare/run JSON
- kit manifest or asset manifest row
- provenance record
- generated output status/review note

Do not overwrite old generated model evidence unless the user explicitly asks. Prefer a new version folder for new generation attempts.

## Texture Repair Records

When a generated model has acceptable geometry but the embedded texture atlas drifts from the approved colors, add a post-generation repair gate instead of immediately regenerating. The project profile should define, or the agent should infer:

- command for creating freshly de-lit approved comparison refs
- command for UV-layout-preserving atlas repair
- repaired GLB sibling name, such as `model_conceptmatch.glb`
- repaired texture path
- repair run JSON path
- comparison board path
- review card/status note path

Do not compare repaired textures against lit approval plates. Compare them against freshly de-lit approved refs using material-class sampling appropriate for the project. Do not overwrite the original generated model.

## Validation Pattern

Use focused checks before broad checks:

1. Confirm all paths referenced by manifests exist.
2. Parse JSON/YAML.
3. Inspect alpha PNG corners and bounding boxes.
4. Render touched art-bible pages.
5. Build the art bible if book inputs changed.
6. Run project asset/provenance checks.
7. Validate repaired GLBs and embedded textures when the texture repair gate is used.
8. Run game/playable tests only when runtime integration changed.
