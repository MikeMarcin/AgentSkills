# TRELLIS Provider Reference

## Provider Identities

- `trellis1`: Space `trellis-community/TRELLIS`, host
  `https://trellis-community-trellis.hf.space`.
- `trellis2`: Space `microsoft/TRELLIS.2`, host
  `https://microsoft-trellis-2.hf.space`.
- Both are hosted Gradio/ZeroGPU providers. Local tooling uploads inputs, calls
  public endpoints, downloads outputs, and hashes evidence; it does not run
  model weights.

## Public Endpoints

Check current endpoint metadata with:

```bash
curl -fsSL https://trellis-community-trellis.hf.space/gradio_api/info
curl -fsSL https://microsoft-trellis-2.hf.space/gradio_api/info
```

TRELLIS v1 endpoints:

- `/start_session`: no public parameters. Call this before preprocessing or generation in scripted runs so the Space creates the per-session output directory.
- `/preprocess_image`: accepts one Gradio image data object and returns a preprocessed image. The Space removes background unless the input has alpha.
- `/preprocess_images`: accepts a gallery list for multi-view input and returns preprocessed images.
- `/generate_and_extract_glb`: converts the preprocessed input to a 3D asset and returns a preview video, a model file, and a GLB download file. The app source also maintains a hidden state for optional Gaussian extraction.
- `/extract_gaussian`: extracts a `.ply` Gaussian splat from the current session state after generation.

TRELLIS.2 endpoints:

- `/start_session`: creates provider session state.
- `/preprocess_image`: prepares one image prompt.
- `/image_to_3d`: generates the PBR asset state and preview from one image.
- `/extract_glb`: exports the current asset using declared decimation and
  texture-size settings.

The live hosted TRELLIS.2 Space does not currently expose multi-image input,
Gaussian extraction, or the upstream repository's existing-mesh texturing app.

## TRELLIS v1 Generation Parameters

`/generate_and_extract_glb` public parameters:

- `image`: single image input.
- `multiimages`: gallery input for multiple views.
- `seed`: integer from `0` to `2147483647`.
- `ss_guidance_strength`: sparse structure guidance, default `7.5`.
- `ss_sampling_steps`: sparse structure sampling steps, default `12`.
- `slat_guidance_strength`: structured latent guidance, default `3.0`.
- `slat_sampling_steps`: structured latent sampling steps, default `12`.
- `multiimage_algo`: `stochastic` or `multidiffusion`, default `stochastic`.
- `mesh_simplify`: default `0.95`.
- `texture_size`: `512`, `1024`, or `2048`, default `1024`.

The app UI has a hidden `is_multiimage` state that is changed by selecting the "Single Image" or "Multiple Images" tab. Programmatic multi-image runs should call the no-argument `/lambda_1` tab-select endpoint before `/generate_and_extract_glb`; single-image runs can call `/lambda`.

## Output Expectations

The v1 app renders a 120-frame preview video at 15 FPS and exports a GLB named
`sample.glb`. TRELLIS.2 returns a live 3D preview and then an extracted GLB.
The client copies returned files into the requested output directory and writes
`trellis-run.json` with exact provider, capability snapshot, API-schema digest,
settings, inputs, and output metadata.

TRELLIS.2's live defaults are resolution `1024`, decimation target `300000`,
and texture size `2048`. Its upstream model advertises base color, roughness,
metallic, and opacity attributes. Treat actual GLB channel audit as the output
gate; declared provider capability alone is not proof that a returned file is
complete.

## Free-Only And PBR Policy

Both registered adapters target public ZeroGPU Spaces and declare no paid
escalation path. A free-only quota rejection maps to ExampleWorkflow
`waiting_for_quota`; a cold start or temporary outage maps to
`waiting_for_provider`. Each provider call produces one immutable attempt
receipt. Retrying after hours or days uses the same request id with a new
attempt id and receipt path.

`pbr_required` permits only `trellis2`. After download, the client parses the
GLB v2 JSON chunk and requires `baseColorTexture` and
`metallicRoughnessTexture` on every material. The packed texture proves both
roughness and metallic channel presence. Normal, occlusion, and emissive are
reported when present but are not implied by the provider's model card.

## MCP Caveat

The app source currently launches with `mcp_server=True`, but the Hugging Face MCP dynamic Space call has exposed only `TRELLIS_start_session`, and direct invocation has failed with a streamable HTTP 404. Do not use MCP for the normal workflow; use the public Gradio API/client instead.

## ZeroGPU Quota

The generation endpoint is decorated with a 120-second ZeroGPU reservation. Anonymous Gradio calls can fail with a quota message before inference begins. Use an authenticated Hugging Face token for real generation runs when anonymous quota is unavailable.

Use `scripts/trellis_client.py --check-token` to verify local token setup without printing secrets. Use `scripts/trellis_client.py --setup-token` to store a collaborator's own token in their local Hugging Face cache; the command uses a hidden macOS dialog when available and never writes git credentials.
