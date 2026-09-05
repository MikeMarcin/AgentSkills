---
name: instamat-image-to-pbr
description: Generate reviewable PBR texture sets from concept art, material plates, scans, or reference-image crops with InstaMAT Materialize Image and the scriptable InstaMAT Pipeline CLI. Use when Codex needs to derive base color, normal, roughness, metalness, ambient occlusion, or height maps from an image; cancel baked lighting; make a source tileable; inspect the installed InstaMAT tooling; automate repeatable material generation; or prepare texture maps for later GLB/game-engine integration.
---

# InstaMAT Image to PBR

Create traceable PBR texture candidates with InstaMAT's documented `Materialize Image` graph. Treat generated maps as review candidates until the exact texture set has been inspected and approved.

## Start with the execution surface

Run:

```bash
python3 scripts/instamat_materialize.py doctor
```

InstaMAT Studio is the authoring GUI. Documented command-line graph execution uses the separately installed and licensed `InstaMATPipeline` console application. Never invent Studio flags or launch the Studio GUI binary as a headless renderer.

If Pipeline is missing, report that fact and direct the user to the official Pipeline download in their InstaMAT license portal. Machine authorization is system-wide; never request, record, or place license credentials in a command record.

Read [references/instamat-pipeline.md](references/instamat-pipeline.md) when locating Pipeline, diagnosing graph discovery, using a custom package, or exposing advanced Materialize Image parameters.

## Prepare a defensible source image

1. Find the approved concept or art-bible image that defines the material.
2. Crop a materially uniform, near-front-facing region. Use separate crops for ceramic, brass, enamel, glass, and fabric.
3. Prefer material plates or orthographic close-ups over a full environment frame. A full scene contains perspective, multiple materials, cast shadows, and lighting gradients that cannot become one truthful PBR material.
4. Preserve the approved source unchanged. Write the crop and all generated maps to a sibling review directory.
5. Record whether the crop is already de-lit. Use Materialize Image shadow cancellation for baked illumination; do not mistake artistic highlights for albedo.

## Inspect and execute Materialize Image

Inspect the graph surface before the first real run:

```bash
python3 scripts/instamat_materialize.py info
```

Generate a 16-bit candidate set:

```bash
python3 scripts/instamat_materialize.py materialize \
  /absolute/path/material-crop.png \
  /absolute/path/review-output \
  --resolution 2048 \
  --shadow-cancellation 0.8 \
  --normal-strength 1.0
```

Use `--metalness` only when the source is a conductor or when a reviewed mask/range configuration is supplied. For a dielectric such as black ceramic, leave it disabled. Use `--parameter NAME=JSON` for documented advanced parameters and `--dry-run` to audit the exact argv without executing it.

If the built-in graph cannot be found, author or save an Element Graph package in Studio that exposes a `Materialize Image` node, then pass the package with `--package /absolute/path/materialize.IMP`.

## Review before integration

Inspect every output map at native resolution:

- Base color contains material color and wear, but no cast shadow, bright specular highlight, or scene-wide illumination gradient.
- Normal and height describe surface relief rather than the silhouette or perspective of the source crop.
- Roughness preserves material identity and avoids turning black ceramic into gray chalk or a mirror.
- Metalness is zero for dielectrics and reserved for true conductors; do not use gray metalness to compensate for lighting.
- Ambient occlusion is restrained and does not rebake directional lighting into the material.
- Tile seams, synthesis artifacts, and repeated features are acceptable at the intended texel density.

Compare the shaded result against the approved concept under controlled lighting. Do not approve from texture thumbnails alone.

## Preserve provenance and promotion gates

The wrapper writes `instamat-materialize-run.json` with the input hash, exact command, graph, parameters, and output hashes. Keep that record with the maps.

Do not overwrite admitted GLBs, runtime textures, approval manifests, or promoted assets during material generation. Pack AO/roughness/metalness channels or embed maps into a sibling GLB only after the exact map set passes review. Runtime promotion still requires the project's normal human-approval gate.
