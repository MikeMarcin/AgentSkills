"""TRELLIS v1 Gradio endpoint binding."""

from __future__ import annotations

from typing import Any, Callable

from .common import (
    ProviderBinding,
    ProviderRun,
    as_gallery_upload,
    as_upload,
    upload_file,
    upload_gallery,
)


BINDING = ProviderBinding(
    name="trellis1",
    provider_id="skill:trellis1",
    space_id="trellis-community/TRELLIS",
    host="https://trellis-community-trellis.hf.space",
    generation_endpoint="/generate_and_extract_glb",
    required_endpoints=(
        "/start_session",
        "/preprocess_image",
        "/preprocess_images",
        "/generate_and_extract_glb",
    ),
    free_only_supported=True,
    supports_multi_image=True,
    supports_gaussian=True,
    declared_pbr_channels=("base_color",),
)


def generate(
    client: Any,
    handle_file: Callable[[str], Any],
    args: Any,
    predict: Callable[..., Any],
) -> ProviderRun:
    settings = {
        "seed": args.selected_seed,
        "ss_guidance_strength": args.ss_guidance_strength,
        "ss_sampling_steps": args.ss_sampling_steps,
        "slat_guidance_strength": args.slat_guidance_strength,
        "slat_sampling_steps": args.slat_sampling_steps,
        "multiimage_algo": args.multiimage_algo,
        "mesh_simplify": args.mesh_simplify,
        "texture_size": args.texture_size,
    }

    predict(client, "/start_session")
    if args.multi_image:
        predict(client, "/lambda_1")
        raw_gallery = upload_gallery(args.multi_image, handle_file)
        preprocessed = predict(client, "/preprocess_images", raw_gallery)
        multiimages = as_gallery_upload(preprocessed, handle_file) or raw_gallery
        image = multiimages[0]["image"] if multiimages else upload_file(args.multi_image[0], handle_file)
    else:
        predict(client, "/lambda")
        raw_image = upload_file(args.image, handle_file)
        preprocessed = predict(client, "/preprocess_image", raw_image)
        image = as_upload(preprocessed, handle_file)
        multiimages = []

    result = predict(
        client,
        BINDING.generation_endpoint,
        image,
        multiimages,
        args.selected_seed,
        args.ss_guidance_strength,
        args.ss_sampling_steps,
        args.slat_guidance_strength,
        args.slat_sampling_steps,
        args.multiimage_algo,
        args.mesh_simplify,
        args.texture_size,
    )

    if args.extract_gaussian:
        try:
            gaussian = predict(client, "/extract_gaussian")
            result = (result, gaussian)
        except Exception as exc:  # Generation succeeded; preserve the GLB result.
            print(f"Gaussian extraction failed after GLB generation: {exc}", file=args.stderr)

    return ProviderRun(settings=settings, raw_result=result)
