---
name: trellis-image-to-3d
description: Generate 3D assets from concept art or reference images with provider-aware hosted TRELLIS v1 and Microsoft TRELLIS.2 Gradio adapters. Use when the agent needs to prepare or isolate concept art, probe and record live provider capabilities, preserve existing TRELLIS v1 single or multi-image workflows, request TRELLIS.2 PBR-capable outputs, execute ExampleWorkflow provider work orders, write redacted attempt receipts, troubleshoot Hugging Face quota or Space API changes, or capture reproducible GLB and preview settings.
---

# Trellis Image To 3d

## Overview

Use hosted Hugging Face Spaces through provider modules in
`scripts/providers/`. `trellis1` preserves the established
`trellis-community/TRELLIS` single/multi-image GLB, preview, and optional
Gaussian workflow. `trellis2` binds the live `microsoft/TRELLIS.2` image-to-3D
and PBR GLB export endpoints. Do not run either model locally; the local client
prepares inputs, probes the complete API schema, uploads images, waits for the
remote job, downloads artifacts, and writes redacted evidence.

## Installed location

Resolve `trellis_skill_root` to the directory containing the loaded `SKILL.md`,
using its absolute installation path. The examples below use that variable;
they work through project or personal MASK links from any working directory.
The optional ExampleWorkflow work-order mode does not require an SAMPLE_STUDIO checkout for ordinary
image generation, preparation, probing, or GLB audit.

```bash
trellis_skill_root="/absolute/path/to/installed/trellis-image-to-3d"
```

## Workflow

1. Start from an absolute path to one or more concept art images. Prefer isolated objects on a plain or transparent background; if the image has an alpha channel, TRELLIS uses it as the mask.
2. Read `references/input-preparation.md` when the source is a sheet, scene render, material board, or any image where the target object is not already isolated. Read `references/trellis-space.md` when the endpoint shape, defaults, or troubleshooting details matter.
3. Probe the exact provider before a generation run. Persist a capability
   snapshot when the result will become durable source history:

```bash
python3 "$trellis_skill_root/scripts/trellis_client.py" \
  --provider trellis1 \
  --probe \
  --capabilities-out /absolute/path/trellis1-capabilities.json

python3 "$trellis_skill_root/scripts/trellis_client.py" \
  --provider trellis2 \
  --probe \
  --free-only \
  --capabilities-out /absolute/path/trellis2-capabilities.json
```

`--info` remains a backward-compatible alias for probing `trellis1` when no
provider is named.

4. Install client dependencies only when the script reports they are missing. Prefer a local or temporary virtual environment over changing the system Python:

```bash
python3 -m venv /tmp/trellis-gradio-client
/tmp/trellis-gradio-client/bin/python -m pip install --upgrade pip gradio_client huggingface_hub pillow
```

5. Check whether the collaborator already has a Hugging Face token configured:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" --check-token
```

6. If no token is configured, walk them through creating a Hugging Face read token at `https://huggingface.co/settings/tokens`, then run:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" --setup-token
```

In Codex Desktop on macOS this opens a hidden system dialog for the token. In a real interactive terminal it falls back to a hidden terminal prompt. If neither is available, tell the collaborator to run the same command from their local Terminal. Never ask them to paste a token into chat, and never commit a token.

7. Prepare sheet-style concept art before generation. Use `--crop-box` to select the object view, then feed the produced `_alpha.png` into generation:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --prepare-image /absolute/path/sample_object_sheet.png \
  --prepare-output-dir /absolute/path/trellis-input \
  --crop-box 60,45,600,665 \
  --output-stem sample_object_three_quarter
```

8. Generate a single-image GLB:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --image /absolute/path/trellis-input/sample_object_three_quarter_alpha.png \
  --output-dir /absolute/path/trellis-output \
  --seed 0
```

Omitting `--provider` preserves this TRELLIS v1 command. Add
`--provider trellis1` when recording a durable attempt.

9. Generate from multiple views when the user provides consistent front/side/back or similar images:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --multi-image /absolute/path/front.png \
  --multi-image /absolute/path/side.png \
  --multi-image /absolute/path/back.png \
  --output-dir /absolute/path/trellis-output \
  --seed 0
```

10. Use TRELLIS.2 for a single-image PBR-capable proposal only after its live
    probe passes:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --provider trellis2 \
  --free-only \
  --pbr-required \
  --image /absolute/path/reference.png \
  --output-dir /absolute/path/trellis2-output \
  --resolution 1024 \
  --texture-size 2048 \
  --seed 0
```

11. For durable ExampleWorkflow execution, pass a schema-valid
    `example_workflow.provider_work_order` and write its attempt receipt separately:

```bash
/tmp/trellis-gradio-client/bin/python "$trellis_skill_root/scripts/trellis_client.py" \
  --work-order /absolute/path/work-order.json \
  --output-dir /absolute/path/attempt-output \
  --capabilities-out /absolute/path/capabilities.json \
  --attempt-receipt /absolute/path/attempt-receipt.json
```

The client verifies work-order input byte lengths and SHA-256 digests, rejects
secret-bearing payloads, and records the exact provider and live API-schema
digest. Provider-native job ids remain `job:<redacted>`.

`--free-only` never requests or escalates to paid compute. Exhausted ZeroGPU
quota writes an immutable `waiting_for_quota` receipt when the work order allows
quota waiting. Resume the request later as a new attempt id and receipt path;
do not replace the earlier receipt. Provider cold starts and temporary outages
map to `waiting_for_provider`.

12. Inspect the output directory for `model.glb`, provider previews, and
    `trellis-run.json`. Report absolute output paths, provider, capability
    snapshot digest, seed, and settings.
13. If the mesh is acceptable but the embedded texture color drifts from the approved refs, use the project workflow for a non-destructive, UV-preserving texture repair before regenerating. Compare against freshly de-lit approved refs, not lit approval plates. Keep the original `model.glb` unchanged and write repaired candidates as sibling GLBs with their own run records.

## Generation Defaults

TRELLIS v1 keeps the established defaults unless the user asks for quality or
runtime changes:

- `seed`: `0` for reproducibility; use `--randomize-seed` only when exploration matters more than repeatability.
- Sparse structure guidance: `7.5`
- Sparse structure sampling steps: `12`
- Structured latent guidance: `3.0`
- Structured latent sampling steps: `12`
- Multi-image algorithm: `stochastic`
- Mesh simplify: `0.95`
- Texture size: `1024`

TRELLIS.2 defaults to 1024³ generation, 300,000-face GLB decimation, and a
2048 texture. Its shape and texture guidance settings come from the current
live Space defaults and are recorded in every run manifest.

`--pbr-required` selects TRELLIS.2 when the provider is `auto` and rejects an
explicit TRELLIS v1 selection before upload. After download it parses the GLB
and requires textured base color plus metallic/roughness channels on every
material. Declared provider capability is not sufficient. Audit an existing
file without provider access with:

```bash
python3 "$trellis_skill_root/scripts/trellis_client.py" \
  --audit-glb /absolute/path/model.glb \
  --pbr-required \
  --audit-out /absolute/path/pbr-audit.json
```

For higher quality, increase sampling steps gradually and consider `--texture-size 2048`. For faster tests, keep defaults and use a low-detail concept image.

## Tooling Rule

Use the remote Space's Gradio API through `scripts/trellis_client.py` by default.
Provider modules own Space ids, endpoint order, settings, and output extraction;
generic work-order, capability, receipt, token, preparation, and copy logic stays
in the client. Do not use the Space MCP bridge unless the user explicitly asks
for MCP.

## Input Preparation

Use `--prepare-image` for art-bible renders before calling the remote Space unless the input is already a single isolated object. The local preparation writes:

- `<stem>_crop.png`: square RGB crop on neutral gray.
- `<stem>_alpha.png`: same image with connected neutral border background removed to alpha.
- `<stem>_prepare-run.json`: source, crop box, alpha thresholds, and output paths.

Feed `_alpha.png` to TRELLIS first. Use `_crop.png` only if the alpha mask damages the object.

## Troubleshooting

- Either Space may cold-start or queue for several minutes because it uses ZeroGPU. Do not assume failure until the client returns an exception or the queue times out.
- Anonymous requests may hit ZeroGPU quota before generation starts. If `--check-token` reports no configured token, use `--setup-token` before generation. If the script reports a ZeroGPU quota error even after authentication, wait for the reset time in the error.
- Treat `waiting_for_quota` as a durable non-failure state. Keep the receipt,
  let ExampleWorkflow preserve the request queue entry, and retry with a new immutable
  attempt after its scheduling window opens.
- If generation fails after upload, rerun `--provider <name> --probe` and compare the schema digest and required endpoints with `references/trellis-space.md`; update only that provider module when the Space changed.
- TRELLIS.2 currently exposes single-image generation. Do not silently reroute a requested multi-image or PBR-required attempt to TRELLIS v1.
- A TRELLIS.2 run can still fail the PBR gate if the returned GLB lacks actual
  base-color or packed metallic/roughness textures. Preserve the failed
  candidate and terminal receipt as evidence; do not classify channel names in
  a provider description as output proof.
- If the output has unwanted background geometry, edit the source image into a clean transparent PNG and retry.
- If the output models a whole sheet or scene instead of one object, rerun `--prepare-image` with a tighter `--crop-box`; do not send full prop sheets directly to TRELLIS.
- If only the texture hue/material color is wrong, do not regenerate first. Prefer deterministic atlas repair that preserves UV layout. Use imagegen to repaint an atlas only after review, because it can move UV islands, seams, padding, or accents.
- If Gaussian extraction is requested, expect a large `.ply`; only request it when the user explicitly needs splat data.
