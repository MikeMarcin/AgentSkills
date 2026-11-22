---
name: concept-art-approval-pipeline
description: Concept-art and character-asset production for games, from reference review through generated 3D assets and runtime handoff. Use for imagegen refs, art-bible approval, TRELLIS preparation, humanoid modeling, rigging and export, or game asset integration including Roblox Studio. Uses attended-review for hosted human visual gates and preserves exact offline verdicts.
---

# Concept Art Approval Pipeline

## Core Rule

Treat this as a production pipeline with distinct visual, source, export, and runtime gates. For each asset or kit piece:

1. Define what the piece is and where it appears in the target scene.
2. Generate or repair candidate image refs.
3. Show the candidate in isolation and in context.
4. Review against the user's criteria. Default to an explicit user decision at each visual gate unless the user authorizes autonomous progression; follow any stricter project gate.
5. Integrate the accepted result into the appropriate art-bible or downstream handoff records, recording what was actually verified.

Keep an explicit pending human decision pending. Acceptance of appearance alone does not establish export or runtime readiness.

## Related Skills

- Human visual review requires the `attended-review` companion. Resolve it by name in the current host. Its hosted session, hub registration, partial decisions and handback are the default for one candidate or a batch.

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

For modeled humanoid characters and equipment, read [references/character-assets.md](references/character-assets.md) before planning or exporting. Establish the actual consumer contract and source ownership so the high-detail source has a deliberate game-resolution conversion stage.

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
6. Inspect, critique, revise, and re-render obvious defects before presenting the board.
7. Route each required human decision through the hosted visual review below. When the user delegates visual review, retain the evidence and continue within that authorization.
8. If the user requests changes, revise the directed piece and show a new board. Promote the accepted direction into configured art-bible and handoff paths.

Use context mockups from the project’s actual concept scenes whenever possible. A generic schematic is acceptable only as a secondary diagram.

## Hosted visual review

Build the exact art batch with the [package builder](references/offline-review.md#build-and-review). Use one stable candidate ID per decision. Read [the attended art handoff](references/attended-review.md) and use `attended-review` to present each candidate’s isolation and context media in the consumer’s hosted queue. Serve it privately, verify publication on the configured review hub, and share the private link. Wait for the owner’s saved decisions while unrelated work can proceed.

Consume the attended handback directly. Validate accepted and rejected identities against the art batch and gate. An unanswered question stays pending. A visual decision applies only at its recorded gate. Keep every downstream claim false in the visual verdict.

When the owner chooses offline review or hosted transport is unavailable, explain the applicable fallback and follow [offline review](references/offline-review.md). A missing companion or hub setup should be reported when it prevents the requested hosted review. Honor an explicitly requested in-chat review or delegated approval cadence.

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

After the applicable user decision or an authorized autonomous review:

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

For a Roblox experience, use the [Roblox asset handoff](references/roblox.md) when preparing generation inputs, reviewing a game-resolution export or binding the model in Studio. Reference preparation and generation can run alongside gameplay once the applicable source decision is recorded.

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
- hosted and offline visual verdicts validate against the exact generated batch and gate before integration
- JSON/YAML manifests parse
- provenance rows distinguish rejected, needs-generation, approved-for-promotion, and promoted states correctly
- `git diff --check` is clean

Report what was integrated, what remains deferred, and exactly which gate the asset is now in.
