"""Microsoft TRELLIS.2 Gradio endpoint binding."""

from __future__ import annotations

from typing import Any, Callable

from .common import ProviderBinding, ProviderRun, as_upload, upload_file


BINDING = ProviderBinding(
    name="trellis2",
    provider_id="skill:trellis2",
    space_id="microsoft/TRELLIS.2",
    host="https://microsoft-trellis-2.hf.space",
    generation_endpoint="/image_to_3d",
    required_endpoints=(
        "/start_session",
        "/preprocess_image",
        "/image_to_3d",
        "/extract_glb",
    ),
    free_only_supported=True,
    supports_multi_image=False,
    supports_gaussian=False,
    declared_pbr_channels=("base_color", "roughness", "metallic", "opacity"),
)


def generate(
    client: Any,
    handle_file: Callable[[str], Any],
    args: Any,
    predict: Callable[..., Any],
) -> ProviderRun:
    settings = {
        "seed": args.selected_seed,
        "resolution": args.resolution,
        "ss_guidance_strength": args.ss_guidance_strength,
        "ss_guidance_rescale": args.ss_guidance_rescale,
        "ss_sampling_steps": args.ss_sampling_steps,
        "ss_rescale_t": args.ss_rescale_t,
        "shape_slat_guidance_strength": args.shape_slat_guidance_strength,
        "shape_slat_guidance_rescale": args.shape_slat_guidance_rescale,
        "shape_slat_sampling_steps": args.shape_slat_sampling_steps,
        "shape_slat_rescale_t": args.shape_slat_rescale_t,
        "tex_slat_guidance_strength": args.tex_slat_guidance_strength,
        "tex_slat_guidance_rescale": args.tex_slat_guidance_rescale,
        "tex_slat_sampling_steps": args.tex_slat_sampling_steps,
        "tex_slat_rescale_t": args.tex_slat_rescale_t,
        "decimation_target": args.decimation_target,
        "texture_size": args.texture_size,
    }

    predict(client, "/start_session")
    predict(client, "/lambda")
    raw_image = upload_file(args.image, handle_file)
    preprocessed = predict(client, "/preprocess_image", raw_image)
    image = as_upload(preprocessed, handle_file)
    preview = predict(
        client,
        BINDING.generation_endpoint,
        image,
        args.selected_seed,
        args.resolution,
        args.ss_guidance_strength,
        args.ss_guidance_rescale,
        args.ss_sampling_steps,
        args.ss_rescale_t,
        args.shape_slat_guidance_strength,
        args.shape_slat_guidance_rescale,
        args.shape_slat_sampling_steps,
        args.shape_slat_rescale_t,
        args.tex_slat_guidance_strength,
        args.tex_slat_guidance_rescale,
        args.tex_slat_sampling_steps,
        args.tex_slat_rescale_t,
    )
    glb = predict(client, "/extract_glb", args.decimation_target, args.texture_size)
    # Put the explicit export first so generic copying names it model.glb and
    # the PBR gate audits the shipping-shaped output rather than the UI preview.
    return ProviderRun(settings=settings, raw_result=(glb, preview))
