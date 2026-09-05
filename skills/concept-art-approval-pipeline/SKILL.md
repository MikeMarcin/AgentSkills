---
name: concept-art-approval-pipeline
description: Human-in-the-loop concept-art production workflow for imagegen-created game assets, including deterministic offline review pages with exact per-candidate decisions and batch-bound verdict export. Use when the agent needs to generate or revise concept art, review each kit piece with the user before approval, integrate approved images into an art bible, prepare clean alpha/keyed inputs and command records for TRELLIS image-to-3D generation, optionally route approved humanoid assets through Mixamo rigging/animation, and then hand approved/generated assets to a game/runtime integration pipeline. Configurable for projects with art-bible, generated-asset, and runtime-manifest workflows.
---

# Concept Art Approval Pipeline

## Core Rule

Treat this as a gated production pipeline, not a batch image dump. For each asset or kit piece:

1. Define what the piece is and where it appears in the target scene.
2. Generate or repair candidate image refs.
3. Show the candidate in isolation and in context.
4. Wait for explicit user approval.
5. Integrate only the approved result into art-bible and downstream handoff records.

Do not advance to the next piece, TRELLIS generation, rigging, or game integration while the current piece is unapproved.

## Related Skills

- Use `imagegen` when generating or editing bitmap concept refs, chroma-key sources, clean reference plates, context mockups, or transparent-background cutouts.
- Use `trellis-image-to-3d` when preparing or running TRELLIS image-to-3D generation. Read that skill before writing final TRELLIS commands or running generation.
- Use project-specific build/test skills when the later game integration stage becomes code/RFC work.

## Project Setup

First discover the project profile:

1. Read `<consumer>/.mask/skill-config/concept-art-approval-pipeline/project.md` when present. Resolve its paths against that consumer.
2. Otherwise read [references/project-config.md](references/project-config.md) and establish the paths from the current repo.
3. Resolve bundled scripts and assets against the absolute directory containing the loaded `SKILL.md`. Never infer the consumer from a resolved MASK symlink. The ExampleScene production profile remains in SAMPLE_STUDIO consumer context.

Minimum project fields to establish before editing:

- art-bible root, page roots, generated image catalog, and book manifest
- source concept/ref asset directories
- approved review/evidence directory
- TRELLIS runtime input root and versioning convention
- generated-asset provenance or runtime manifest files
- validation commands
- visual constraints and naming rules

## Review Loop

For each asset:

1. Identify the asset key, prompt/catalog id, dimensions, runtime family, and scene role.
2. Gather existing art-bible context images and gameplay/runtime context if available.
3. Create candidate refs with imagegen, usually as front, side, top, and optional 3/4 views on a flat chroma-key background.
4. Remove the chroma key locally and validate alpha. Do not treat a checkerboard preview as the source alpha.
5. Build a review board that shows:
   - front/side/top/optional 3/4 alpha views on checkerboard
   - a short description of what the piece is
   - a scene/context mockup showing where it is used
   - acceptance criteria and known concerns
6. Show the review board to the user and stop.
7. If the user requests changes, revise only that piece and show a new board.
8. If the user approves, promote that exact approved direction into the configured art-bible and handoff paths.

Use context mockups from the project’s actual concept scenes whenever possible. A generic schematic is acceptable only as a secondary diagram.

## Offline Batch Review

Use the bundled offline review package for multi-candidate or multi-piece waves, or whenever the user needs persistent and exportable decisions. A single immediate candidate may still use an in-chat review board.

Read [references/offline-review.md](references/offline-review.md) before building a page or processing its export. In summary:

1. Write an `sample_studio.art_review_batch_input` manifest with one stable `candidate_id` per item, isolation media, context media, and any exact non-preview identity files.
2. Build the file-local package with `scripts/build_art_review.py build`. The builder derives candidate digests from metadata and file bytes and derives a deterministic batch ID.
3. Present the generated `index.html` to the user and stop. Do not create placeholder decisions or an empty verdict when no art is awaiting review.
4. Ask the user to resolve every candidate and paste the complete exported JSON back to Codex.
5. Save the export to a temporary file and run `scripts/build_art_review.py validate-verdict` against the package manifest.
6. Apply only accepted exact candidate ID/digest pairs to the current gate’s normal integration procedure. Keep rejected candidates as evidence only.

The page stores local progress but cannot write repo evidence. Its `human_visual_isolation_only` verdict covers only the named `review_gate`; every downstream claim remains false. Never infer a complete verdict from partial page state, screenshots, conversational shorthand, or an older batch whose candidate bytes have changed.

## Image Requirements

For model-generation refs:

- Keep one object centered per image.
- Prefer true orthographic front/side/top views plus an optional 3/4 view for shape context.
- Use transparent PNGs for primary refs and a flat keyed fallback when the project needs one.
- Validate transparent corners and plausible object bounding boxes.
- Avoid readable text, logos, watermarks, shadows, contact blobs, floor planes, and arbitrary marks unless the piece physically has them.
- Do not use source contact sheets as TRELLIS inputs.

For art-bible refs:

- Use the approved imagegen direction, not programmer-art placeholders.
- Keep rejected versions as evidence only when useful; do not leave them referenced as active source.
- Re-render affected pages after replacing art-bible assets.

## Approval Integration

After explicit approval:

1. Copy approved alpha refs into the project art-bible/TRELLIS source package.
2. Copy or prepare the matching runtime TRELLIS input package under the configured generated-asset root.
3. Save the approved review board and source imagegen sheet as evidence.
4. Update kit manifests, audit records, generated-image/book inputs, and per-asset command docs.
5. Update provenance so the active candidate points to the approved source refs and request mode.
6. Preserve rejected generated models as rejected provenance, but make their notes clear that they are not active.
7. Run project validation.

Never promote a generated `.glb` into runtime use just because the source refs were approved. Source approval means “ready for generation,” not “approved for game runtime.”

## TRELLIS Handoff

Prepare commands with the repo’s TRELLIS client defaults unless the user asks otherwise:

- seed `0`
- multi-image first when multiple approved views exist
- single-image fallback only if multi-image generation fails review or the service rejects the request
- output under the configured `generated/trellis/<asset_key>/vNNN/` package

The handoff package should contain:

- alpha inputs
- keyed fallback if needed
- `prepare-run.json`
- commands markdown
- review/status note
- provenance row or manifest update

After generation, require `model.glb`, `preview.mp4`, run record, preview review, digest/provenance updates, and LFS/runtime-manifest checks before promotion.

## Post-Generation Texture Repair Gate

Use this gate only after TRELLIS generation, and only when the mesh/silhouette is acceptable but the embedded texture atlas has color or lighting drift from the approved refs.

1. Do not compare generated textures against lit approval plates. First create a fresh de-lit comparison set from the approved alpha refs using the project de-lighting policy.
2. Build a comparison board and JSON record that sample comparable material classes from:
   - freshly de-lit approved refs
   - original embedded TRELLIS texture
   - any repaired texture candidates
3. Prefer deterministic, UV-layout-preserving atlas repair over imagegen for hue/material drift. Imagegen may be used only when deterministic repair cannot solve a semantic paint problem, and then only with strict preserve-layout review because UV islands, padding, seams, and accents must not move.
4. Write repaired GLBs as non-destructive siblings such as `model_conceptmatch.glb`; never overwrite the original `model.glb`.
5. Record the repaired texture PNG, repair run JSON, review card, comparison board, and status note before any promotion decision.
6. Treat texture repair as another human gate. A repaired candidate is not runtime-approved until the user approves that exact repaired GLB/texture pair.

## Optional Mixamo Stage

Use this only for humanoid or animatable character assets. Do not apply Mixamo workflow to static environment kit pieces.

When needed:

1. Keep source character/animation files under the configured source-animation tree.
2. Record source character, animation clips, rigging assumptions, and export settings.
3. Never request or expose credentials in chat.
4. Validate pose scale, orientation, skeleton compatibility, and sampled animation frames.
5. Only then update runtime manifests or playable bindings.

## Game Integration Stage

Enter game integration only after source refs and generated assets pass their gates.

Expected work:

- promote approved runtime files into the configured runtime asset family
- update generated-asset provenance and runtime manifests
- verify LFS tracking for binary assets
- update scene/layout bindings only when requested by the wave
- run focused asset, manifest, and playable/render tests
- show previews/screenshots when visual integration is the point

Keep art-bible source material, generated candidate packages, approved runtime assets, and playable bindings as separate layers.

## Validation

Run the project’s configured checks. At minimum, validate:

- changed art-bible pages render
- generated book/PDF builds when the art bible is touched
- every manifest path exists
- alpha PNGs have transparent corners
- TRELLIS command docs use the approved input set
- post-generation texture repair, when used, compares against freshly de-lit approved refs and keeps repaired GLBs non-destructive
- offline verdicts, when used, validate against the exact generated batch manifest before any integration
- JSON/YAML manifests parse
- provenance rows distinguish rejected, needs-generation, approved-for-promotion, and promoted states correctly
- `git diff --check` is clean

Report what was integrated, what remains deferred, and exactly which gate the asset is now in.
