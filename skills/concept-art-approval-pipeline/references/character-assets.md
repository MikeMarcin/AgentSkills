# Modeled Character Assets

Read this for a humanoid character or fitted equipment modeled for a game. Resolve project numbers, files, naming, and acceptance limits from the actual consumer; the Array Vanguard experience motivates the checks but supplies no universal limits.

## Establish the consumer contract first

Before planning the production path, inspect the importer, runtime renderer, asset manifests, rig, and source ownership. Record the actual file and accessor limits, decoded texture and instance costs, animation clip names and durations, fitting bounds, player-camera scale, and who owns the production copy. High-poly-first sculpting is valid and need not obey runtime mesh budgets. Preserve that editable high-quality source. Plan a deliberate game-resolution derivative or retopology, UVs, high-to-low normal/material bake, LODs where useful, and portable export. Consumer constraints govern that downstream stage; source completion does not imply runtime readiness.

## Shape and review

Use region-by-region reference crops as a focus map, not an instruction to split the mesh or change an established rig or art style. At each checkpoint, compare the local form with whole-body silhouette, neighboring joins, and actual game-scale views. Preserve accepted regions and recoverable checkpoints; reopen them when the user directs it or a demonstrated join correction requires it.

Run an internal inspect → critique → revise → re-render loop before a review card. Show honest reference, current asset, and full-body views, labeled by source or native renderer. Keep editable artifacts. The user's instruction decides whether a card is a blocking approval gate or progress evidence during autonomous iteration.

Treat generated concepts as perspective illustrations, not calibrated orthographic drawings. Separate lighting and reflections from shape with front, side, rear, and high views before introducing a hard corner. Fix primary proportions and credible construction before surface decoration: shell thickness and mounting, palm and thumb web, glove articulation, and equipment grip fit should survive close and game-scale inspection. Correct equipment interfaces within a recorded bound instead of distorting anatomy or hiding contact with camera placement; retain the prior state and state what silhouette or attachment changed.

## Pose and export validation

Inspect bind and animation poses, including intermediate phases, before freezing fitted geometry. For collision or fit checks, sample triangle interiors as well as vertices; check both authoring precision and the posed Float32/export result. Distinguish intended soft overlap from visible hard intrusion. Record preexisting animation defects separately from defects introduced by the new asset.

Qualify each gate independently: art quality, source geometry validity, portable export, native runtime rendering, gameplay binding, and performance. A math check or attractive source render does not prove the later gates. Compare the same camera and light across source and exported pixels, then inspect at player-camera scale and close detail.

Simplify the derivative by part and measured visible or functional error, protecting silhouette, hard edges, attachment fit, and skinning. Bind-pose similarity alone can miss posed sleeve or equipment divergence. Bake high-detail normals and materials to the lower-detail mesh with real UV gutters and the runtime tangent basis. Check serialized accessor counts, texture decode cost, instance multiplication, and file bytes alongside triangle count. Avoid needless exact-float normal splits; consider rigid bone children when appropriate, but qualify the precise mixed or rigid export in the native importer because exporter-valid layouts can still crash a consumer.

Set numerical tolerances in proportion to the actual failure mode. Document finite precision and epsilon scope. A microscopic shared-boundary UV sliver with no texel or mip conflict is not a reason for repeated topology changes; importer validity, visible fit, and raster isolation still matter.

## Recoverable handoff

Save checkpoint, hash, and status after meaningful progress. Record actual tool session IDs and logs; inspect an uncertain job outcome before repeating it, since process listings across separate execution sandboxes may not tell its state. Make expensive per-part work atomic and resumable when useful. Prefer a bounded repair over building a new generic pipeline for a single asset.

Deliver a compact honest review card and a source that opens independently for the consumer. Verify the consumer-local transfer. Large history archives may need to remain retained separately from a smaller current editable source. State which of source, export, native render, gameplay, and performance gates have actually passed; keep pending integration pending.
