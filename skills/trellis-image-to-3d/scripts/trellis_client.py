#!/usr/bin/env python3
"""Run provider-aware hosted TRELLIS image-to-3D generation through Gradio."""

from __future__ import annotations

import argparse
import colorsys
from collections import deque
import getpass
import hashlib
import inspect
import json
import mimetypes
import os
import platform
import random
import shlex
import shutil
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from providers import get_provider
from providers.common import capability_snapshot

MAX_SEED = 2_147_483_647
GLB_JSON_CHUNK = 0x4E4F534A
PBR_REQUIRED_CHANNELS = {"base_color", "roughness", "metallic"}

TRELLIS1_DEFAULTS = {
    "ss_guidance_strength": 7.5,
    "ss_sampling_steps": 12,
    "slat_guidance_strength": 3.0,
    "slat_sampling_steps": 12,
    "multiimage_algo": "stochastic",
    "mesh_simplify": 0.95,
    "texture_size": 1024,
}

TRELLIS2_DEFAULTS = {
    "resolution": "1024",
    "ss_guidance_strength": 7.5,
    "ss_guidance_rescale": 0.7,
    "ss_sampling_steps": 12,
    "ss_rescale_t": 5.0,
    "shape_slat_guidance_strength": 7.5,
    "shape_slat_guidance_rescale": 0.5,
    "shape_slat_sampling_steps": 12,
    "shape_slat_rescale_t": 3.0,
    "tex_slat_guidance_strength": 1.0,
    "tex_slat_guidance_rescale": 0.0,
    "tex_slat_sampling_steps": 12,
    "tex_slat_rescale_t": 3.0,
    "decimation_target": 300_000,
    "texture_size": 2048,
}


def require_pillow() -> tuple[Any, Any]:
    try:
        from PIL import Image, ImageFilter
    except ImportError:
        print(
            "Pillow is required for local TRELLIS input preparation. Install it in the same venv:\n"
            "  /tmp/trellis-gradio-client/bin/python -m pip install --upgrade pillow",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return Image, ImageFilter


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-trellis-skill/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def probe_provider(provider_name: str, capabilities_out: Path | None = None) -> dict[str, Any]:
    provider = get_provider(provider_name)
    binding = provider.BINDING
    snapshot = capability_snapshot(
        binding,
        fetch_json(binding.info_url),
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    if capabilities_out:
        capabilities_out.parent.mkdir(parents=True, exist_ok=True)
        capabilities_out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    return snapshot


def require_gradio_client() -> tuple[Any, Any]:
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        print(
            "gradio_client is required for generation. Install it in a local venv, for example:\n"
            "  python3 -m venv /tmp/trellis-gradio-client\n"
            "  /tmp/trellis-gradio-client/bin/python -m pip install --upgrade pip gradio_client huggingface_hub pillow\n"
            "  /tmp/trellis-gradio-client/bin/python "
            ".agents/skills/trellis-image-to-3d/scripts/trellis_client.py --image /path/image.png --output-dir /path/out",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return Client, handle_file


def make_client(client_class: Any, space_id: str, token: str | None) -> Any:
    if token:
        parameters = inspect.signature(client_class).parameters
        if "hf_token" in parameters:
            return client_class(space_id, hf_token=token)
        return client_class(space_id, token=token)
    return client_class(space_id)


def get_configured_token() -> str | None:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if token:
        return token
    try:
        from huggingface_hub import get_token
    except ImportError:
        return None
    return get_token()


def require_huggingface_hub() -> tuple[Any, Any, Any]:
    try:
        from huggingface_hub import get_token, login, whoami
    except ImportError:
        print(
            "huggingface_hub is required for token setup. Install it in the same venv:\n"
            "  /tmp/trellis-gradio-client/bin/python -m pip install --upgrade huggingface_hub",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return get_token, login, whoami


def print_token_status() -> int:
    get_token, _, whoami = require_huggingface_hub()
    token = get_configured_token() or get_token()
    if not token:
        print_token_setup_guidance()
        return 2

    user = whoami(token=token).get("name", "unknown")
    print(f"Hugging Face token is configured for {user}")
    return 0


def print_token_setup_guidance() -> None:
    setup_command = " ".join(
        shlex.quote(part)
        for part in (sys.executable, sys.argv[0], "--setup-token")
    )
    print(
        "No Hugging Face token is configured for this user.\n\n"
        "1. Create a read token at https://huggingface.co/settings/tokens.\n"
        "2. Run:\n"
        f"   {setup_command}\n"
        "3. Paste the token into the hidden prompt. Do not paste tokens into chat or commit them.\n\n"
        "In a regular terminal, you can also run `hf auth login` or set `HF_TOKEN` for one command.",
        file=sys.stderr,
    )


def setup_token(provided_token: str | None) -> int:
    _, login, whoami = require_huggingface_hub()
    token = provided_token or prompt_for_token()
    if not token:
        print_token_setup_guidance()
        return 2
    token = token.strip()
    if not token.startswith("hf_"):
        print("Token does not look like a Hugging Face token.", file=sys.stderr)
        return 2

    login(token=token, add_to_git_credential=False)
    user = whoami(token=token).get("name", "unknown")
    print(f"Hugging Face token stored in local cache for {user}")
    return 0


def prompt_for_token() -> str | None:
    if platform.system() == "Darwin" and shutil.which("osascript"):
        token = prompt_for_token_macos()
        if token:
            return token

    if sys.stdin.isatty():
        return getpass.getpass("Paste Hugging Face token: ")

    return None


def prompt_for_token_macos() -> str | None:
    script = """
set dialogResult to display dialog "Paste the new Hugging Face token. It will be hidden and stored in the local Hugging Face cache only." default answer "" with hidden answer buttons {"Cancel", "OK"} default button "OK" cancel button "Cancel" with title "Hugging Face Token"
text returned of dialogResult
"""
    completed = subprocess.run(
        ["osascript"],
        input=script,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def existing_file(path: str) -> Path:
    candidate = Path(path).expanduser().resolve()
    if not candidate.is_file():
        raise argparse.ArgumentTypeError(f"not a file: {candidate}")
    return candidate


def output_dir(path: str) -> Path:
    candidate = Path(path).expanduser().resolve()
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def output_file(path: str) -> Path:
    return Path(path).expanduser().resolve()


def parse_crop_box(value: str) -> tuple[int, int, int, int]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("crop box must be left,top,right,bottom")
    try:
        left, top, right, bottom = (int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("crop box values must be integers") from exc
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("crop box right/bottom must be greater than left/top")
    return left, top, right, bottom


def parse_rgb(value: str) -> tuple[int, int, int]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("RGB value must be red,green,blue")
    try:
        rgb = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("RGB values must be integers") from exc
    if any(channel < 0 or channel > 255 for channel in rgb):
        raise argparse.ArgumentTypeError("RGB values must be between 0 and 255")
    return rgb  # type: ignore[return-value]


def run_prepare_image(args: argparse.Namespace) -> dict[str, Any]:
    Image, ImageFilter = require_pillow()
    source = args.prepare_image
    output = args.prepare_output_dir or (source.parent / f"{source.stem}_trellis_input")
    output.mkdir(parents=True, exist_ok=True)
    stem = args.output_stem or source.stem

    image = Image.open(source).convert("RGB")
    validate_crop_box(args.crop_box, image.size)
    crop = image.crop(args.crop_box) if args.crop_box else image
    canvas = square_canvas(
        crop,
        Image,
        size=args.canvas_size,
        padding=args.padding,
        background=args.background_rgb,
    )

    crop_path = output / f"{stem}_crop.png"
    alpha_path = output / f"{stem}_alpha.png"
    manifest_path = output / f"{stem}_prepare-run.json"

    canvas.save(crop_path)
    rgba = canvas.convert("RGBA")
    alpha = neutral_border_alpha(
        rgba,
        Image,
        ImageFilter,
        saturation_threshold=args.alpha_sat_threshold,
        value_min=args.alpha_value_min,
        value_max=args.alpha_value_max,
        blur_radius=args.alpha_blur,
    )
    rgba.putalpha(alpha)
    rgba.save(alpha_path)

    manifest = {
        "source": str(source),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "preparation": {
            "crop_box": list(args.crop_box) if args.crop_box else None,
            "canvas_size": args.canvas_size,
            "padding": args.padding,
            "background_rgb": list(args.background_rgb),
            "alpha_sat_threshold": args.alpha_sat_threshold,
            "alpha_value_min": args.alpha_value_min,
            "alpha_value_max": args.alpha_value_max,
            "alpha_blur": args.alpha_blur,
        },
        "outputs": {
            "rgb_crop": str(crop_path),
            "alpha_image": str(alpha_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def validate_crop_box(crop_box: tuple[int, int, int, int] | None, image_size: tuple[int, int]) -> None:
    if crop_box is None:
        return
    left, top, right, bottom = crop_box
    width, height = image_size
    if left < 0 or top < 0 or right > width or bottom > height:
        raise SystemExit(f"crop box {crop_box} is outside source image bounds {image_size}")


def square_canvas(
    image: Any,
    image_module: Any,
    *,
    size: int,
    padding: int,
    background: tuple[int, int, int],
) -> Any:
    if size <= 0:
        raise SystemExit("--canvas-size must be positive")
    if padding < 0 or padding * 2 >= size:
        raise SystemExit("--padding must be non-negative and leave room for the image")

    max_width = size - (padding * 2)
    scale = min(max_width / image.width, max_width / image.height)
    resized_size = (round(image.width * scale), round(image.height * scale))
    resized = image.resize(resized_size, image_module.Resampling.LANCZOS)
    canvas = image_module.new("RGB", (size, size), background)
    offset = ((size - resized.width) // 2, (size - resized.height) // 2)
    canvas.paste(resized, offset)
    return canvas


def neutral_border_alpha(
    rgba: Any,
    image_module: Any,
    image_filter_module: Any,
    *,
    saturation_threshold: float,
    value_min: float,
    value_max: float,
    blur_radius: float,
) -> Any:
    width, height = rgba.size
    pixels = rgba.load()
    total = width * height
    eligible = bytearray(total)
    seen = bytearray(total)

    for y in range(height):
        row = y * width
        for x in range(width):
            red, green, blue, _ = pixels[x, y]
            _, saturation, value = colorsys.rgb_to_hsv(red / 255.0, green / 255.0, blue / 255.0)
            eligible[row + x] = saturation < saturation_threshold and value_min < value < value_max

    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        for y in (0, height - 1):
            enqueue_if_eligible(x, y, width, eligible, seen, queue)
    for y in range(height):
        for x in (0, width - 1):
            enqueue_if_eligible(x, y, width, eligible, seen, queue)

    while queue:
        x, y = queue.popleft()
        for next_x, next_y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= next_x < width and 0 <= next_y < height:
                enqueue_if_eligible(next_x, next_y, width, eligible, seen, queue)

    alpha = image_module.new("L", (width, height), 255)
    alpha_pixels = alpha.load()
    for y in range(height):
        row = y * width
        for x in range(width):
            if seen[row + x]:
                alpha_pixels[x, y] = 0

    if blur_radius > 0:
        alpha = alpha.filter(image_filter_module.GaussianBlur(radius=blur_radius))
    return alpha


def enqueue_if_eligible(
    x: int,
    y: int,
    width: int,
    eligible: bytearray,
    seen: bytearray,
    queue: deque[tuple[int, int]],
) -> None:
    index = y * width + x
    if eligible[index] and not seen[index]:
        seen[index] = 1
        queue.append((x, y))


def choose_seed(seed: int, randomize_seed: bool) -> int:
    return random.randint(0, MAX_SEED) if randomize_seed else seed


def predict(client: Any, api_name: str, *args: Any, **kwargs: Any) -> Any:
    started = time.time()
    print(f"Calling {api_name}...", file=sys.stderr)
    result = client.predict(*args, api_name=api_name, **kwargs)
    print(f"{api_name} completed in {time.time() - started:.1f}s", file=sys.stderr)
    return result


class ProviderAttemptError(RuntimeError):
    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


def selected_provider_name(requested: str | None, pbr_required: bool = False) -> str:
    if requested in {None, "auto"}:
        return "trellis2" if pbr_required else "trellis1"
    return requested


def apply_provider_defaults(args: argparse.Namespace) -> None:
    defaults = TRELLIS1_DEFAULTS if args.provider == "trellis1" else TRELLIS2_DEFAULTS
    shared = (
        "ss_guidance_strength",
        "ss_sampling_steps",
        "texture_size",
    )
    for name in shared:
        if getattr(args, name) is None:
            setattr(args, name, defaults[name])

    for name, value in TRELLIS2_DEFAULTS.items():
        if getattr(args, name, None) is None:
            setattr(args, name, value)

    for name, value in TRELLIS1_DEFAULTS.items():
        if getattr(args, name, None) is None:
            setattr(args, name, value)


def classify_provider_error(exc: Exception) -> tuple[str, str]:
    message = str(exc)
    normalized = message.lower()
    if "zerogpu quota" in normalized or "exceeded your zerogpu quota" in normalized or "quota" in normalized:
        return "waiting_for_quota", "free_provider_quota_unavailable"
    if any(
        token in normalized
        for token in ("cold start", "sleeping", "timeout", "timed out", "503", "502", "unavailable")
    ):
        return "waiting_for_provider", "provider_temporarily_unavailable"
    return "retryable_failure", "provider_request_failed"


def write_attempt_receipt(
    path: Path,
    args: argparse.Namespace,
    provider_id: str,
    capability_digest: str,
    copied: list[dict[str, Any]],
    status: str,
    message: str,
) -> None:
    if path.exists():
        raise SystemExit(f"attempt receipts are immutable; refusing to replace {path}")
    receipt = build_attempt_receipt(
        args,
        provider_id,
        capability_digest,
        copied,
        status=status,
        message=message,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")


def persist_run_manifest(
    args: argparse.Namespace,
    binding: Any,
    capabilities: dict[str, Any],
    *,
    status: str,
    settings: dict[str, Any],
    copied: list[dict[str, Any]],
    raw_result: Any,
    normalized_provider_message: str,
    pbr_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = {
        "space": binding.space_id,
        "host": binding.host,
        "provider": binding.name,
        "provider_id": binding.provider_id,
        "capability_snapshot_digest": capabilities["snapshot_digest"],
        "api_schema_digest": capabilities["api_schema_digest"],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "policy": {
            "free_only": args.free_only,
            "quota_wait": args.quota_wait,
            "pbr_required": args.pbr_required,
            "paid_escalation": False,
        },
        "settings": settings,
        "inputs": {
            "image": str(args.image) if args.image else None,
            "multi_image": [str(path) for path in args.multi_image],
        },
        "outputs": copied,
        "normalized_provider_message": normalized_provider_message,
        "raw_result": make_jsonable(raw_result),
    }
    if pbr_audit is not None:
        manifest["pbr_audit"] = pbr_audit
    manifest_path = args.output_dir / "trellis-run.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def run_generation(args: argparse.Namespace) -> dict[str, Any]:
    provider = get_provider(args.provider)
    binding = provider.BINDING
    capabilities = probe_provider(args.provider, args.capabilities_out)
    if not capabilities["available"]:
        missing = ", ".join(capabilities["missing_required_endpoints"])
        raise SystemExit(f"{args.provider} is missing required endpoints: {missing}")
    if args.free_only and not capabilities["capabilities"]["free_only"]:
        raise ProviderAttemptError("terminal_failure", "selected provider is not free-only compatible")
    declared_channels = set(capabilities["capabilities"]["pbr_channels"])
    if args.pbr_required and not PBR_REQUIRED_CHANNELS.issubset(declared_channels):
        raise ProviderAttemptError(
            "terminal_failure",
            f"{args.provider} does not declare required PBR channels: {sorted(PBR_REQUIRED_CHANNELS - declared_channels)}",
        )

    Client, handle_file = require_gradio_client()
    token = args.token or get_configured_token()
    if not token:
        print(
            "No Hugging Face token is configured. The script will try an anonymous request, "
            "but ZeroGPU quota is limited. Run `--setup-token` first for collaborator machines.",
            file=sys.stderr,
        )
    client = make_client(Client, binding.space_id, token)
    args.selected_seed = choose_seed(args.seed, args.randomize_seed)
    args.stderr = sys.stderr
    try:
        provider_run = provider.generate(client, handle_file, args, predict)
    except Exception as exc:
        status, message = classify_provider_error(exc)
        if status == "waiting_for_quota" and not args.quota_wait:
            status = "retryable_failure"
            message = "free_provider_quota_unavailable_and_wait_disabled"
        manifest = persist_run_manifest(
            args,
            binding,
            capabilities,
            status=status,
            settings={},
            copied=[],
            raw_result=None,
            normalized_provider_message=message,
        )
        if args.attempt_receipt:
            write_attempt_receipt(
                args.attempt_receipt,
                args,
                binding.provider_id,
                capabilities["snapshot_digest"],
                [],
                status,
                message,
            )
            manifest["attempt_receipt"] = str(args.attempt_receipt)
        raise ProviderAttemptError(status, message) from exc

    copied = copy_outputs(provider_run.raw_result, args.output_dir)
    status = "captured"
    message = "provider outputs captured and hashed"
    pbr_report: dict[str, Any] | None = None
    if args.pbr_required:
        model = next((Path(row["path"]) for row in copied if Path(row["path"]).suffix.lower() == ".glb"), None)
        if model is None:
            pbr_report = {"pbr_required_complete": False, "diagnostic": "missing_glb_output"}
        else:
            try:
                pbr_report = audit_glb(model)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                pbr_report = {"pbr_required_complete": False, "diagnostic": f"invalid_glb:{exc}"}
        audit_path = args.audit_out or (args.output_dir / "pbr-audit.json")
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(json.dumps(pbr_report, indent=2) + "\n", encoding="utf-8")
        if not pbr_report["pbr_required_complete"]:
            status = "terminal_failure"
            message = "pbr_required_output_missing_required_channels"

    manifest = persist_run_manifest(
        args,
        binding,
        capabilities,
        status=status,
        settings=provider_run.settings,
        copied=copied,
        raw_result=provider_run.raw_result,
        normalized_provider_message=message,
        pbr_audit=pbr_report,
    )

    if args.attempt_receipt:
        write_attempt_receipt(
            args.attempt_receipt,
            args,
            binding.provider_id,
            capabilities["snapshot_digest"],
            copied,
            status,
            message,
        )
        manifest["attempt_receipt"] = str(args.attempt_receipt)
    if status != "captured":
        raise ProviderAttemptError(status, message)
    return manifest


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("GLB is shorter than its header and first chunk")
    magic, version, declared_length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(data):
        raise ValueError("invalid GLB v2 header or declared length")

    offset = 12
    while offset + 8 <= len(data):
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        end = offset + chunk_length
        if end > len(data):
            raise ValueError("GLB chunk exceeds declared file length")
        if chunk_type == GLB_JSON_CHUNK:
            return json.loads(data[offset:end].rstrip(b" \t\r\n\0").decode("utf-8"))
        offset = end
    raise ValueError("GLB has no JSON chunk")


def audit_glb(path: Path) -> dict[str, Any]:
    document = glb_json(path)
    materials = document.get("materials", [])
    rows: list[dict[str, Any]] = []
    aggregate_channels: set[str] = set()
    for index, material in enumerate(materials):
        pbr = material.get("pbrMetallicRoughness", {})
        channels: set[str] = set()
        if "baseColorTexture" in pbr:
            channels.add("base_color")
        if "metallicRoughnessTexture" in pbr:
            channels.update(("roughness", "metallic"))
        if "normalTexture" in material:
            channels.add("normal")
        if "occlusionTexture" in material:
            channels.add("occlusion")
        if "emissiveTexture" in material:
            channels.add("emissive")
        if material.get("alphaMode", "OPAQUE") != "OPAQUE":
            channels.add("opacity")
        aggregate_channels.update(channels)
        missing = sorted(PBR_REQUIRED_CHANNELS - channels)
        rows.append(
            {
                "material_index": index,
                "name": material.get("name", ""),
                "channels": sorted(channels),
                "missing_required_channels": missing,
                "pbr_required_complete": not missing,
            }
        )

    return {
        "schema_name": "example-scene.trellis_glb_pbr_audit",
        "schema_version": 1,
        "path": str(path),
        "sha256": sha256_file(path),
        "byte_length": path.stat().st_size,
        "material_count": len(materials),
        "texture_count": len(document.get("textures", [])),
        "image_count": len(document.get("images", [])),
        "channels": sorted(aggregate_channels),
        "required_channels": sorted(PBR_REQUIRED_CHANNELS),
        "pbr_required_complete": bool(rows) and all(row["pbr_required_complete"] for row in rows),
        "materials": rows,
    }


def artifact_record(path: Path, role: str, stored_path: str) -> dict[str, Any]:
    suffix = path.suffix.lower()
    kind_by_suffix = {
        ".glb": "sample_studio:/asset-kind/model",
        ".mp4": "sample_studio:/asset-kind/video-preview",
        ".ply": "sample_studio:/asset-kind/gaussian-splat",
        ".png": "sample_studio:/asset-kind/image-reference",
        ".jpg": "sample_studio:/asset-kind/image-reference",
        ".jpeg": "sample_studio:/asset-kind/image-reference",
        ".webp": "sample_studio:/asset-kind/image-reference",
    }
    media_type = mimetypes.guess_type(path.name)[0]
    if suffix == ".glb":
        media_type = "model/gltf-binary"
    elif suffix == ".ply":
        media_type = "application/ply"
    return {
        "role": role,
        "asset_kind_uri": kind_by_suffix.get(suffix, "sample_studio:/asset-kind/provider-output"),
        "media_type": media_type or "application/octet-stream",
        "path": stored_path,
        "sha256": sha256_file(path),
        "byte_length": path.stat().st_size,
    }


def build_attempt_receipt(
    args: argparse.Namespace,
    provider_id: str,
    capability_digest: str,
    copied: list[dict[str, Any]],
    *,
    status: str = "captured",
    message: str = "provider outputs captured and hashed",
) -> dict[str, Any]:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    request_id = args.request_id or f"example_workflow:/generation-request/trellis/{args.provider}/{timestamp}"
    attempt_id = args.attempt_id or request_id.replace("/generation-request/", "/generation-attempt/", 1)
    inputs = list(args.work_order_data.get("inputs", [])) if args.work_order_data else []
    if not inputs:
        paths = args.multi_image or ([args.image] if args.image else [])
        inputs = [
            artifact_record(path, "reference", f"inputs/{path.name}")
            for path in paths
        ]

    outputs: list[dict[str, Any]] = []
    role_counts: dict[str, int] = {}
    for row in copied:
        path = Path(row["path"])
        base_role = {
            ".glb": "model",
            ".mp4": "preview",
            ".ply": "gaussian",
        }.get(path.suffix.lower(), "provider_output")
        role_counts[base_role] = role_counts.get(base_role, 0) + 1
        role = base_role if role_counts[base_role] == 1 else f"{base_role}_{role_counts[base_role]}"
        outputs.append(artifact_record(path, role, f"outputs/{path.name}"))

    return {
        "schema_name": "example_workflow.provider_attempt_receipt",
        "schema_version": 1,
        "attempt_id": attempt_id,
        "request_id": request_id,
        "provider_id": provider_id,
        "provider_job_id_redacted": "job:<redacted>",
        "status": status,
        "capability_snapshot_digest": capability_digest,
        "inputs": inputs,
        "outputs": outputs,
        "normalized_provider_message": message,
    }


PROHIBITED_SECRET_KEYS = {
    "authorization",
    "cookie",
    "credential",
    "hf_token",
    "huggingfacehub_api_token",
    "password",
    "secret",
    "session",
    "token",
}


def assert_secret_free(value: Any, path: str = "work_order") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in PROHIBITED_SECRET_KEYS:
                raise SystemExit(f"{path}.{key} is prohibited secret material")
            assert_secret_free(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            assert_secret_free(child, f"{path}[{index}]")
        return
    if isinstance(value, str) and (value.startswith("hf_") or value.lower().startswith("bearer ")):
        raise SystemExit(f"{path} contains prohibited secret material")


def load_work_order(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert_secret_free(data)
    required = {
        "schema_name",
        "schema_version",
        "request_id",
        "source_intent_id",
        "provider_id",
        "inputs",
        "parameters",
        "free_only",
        "quota_wait",
        "staging_directory",
    }
    if set(data) != required:
        missing = sorted(required - set(data))
        extra = sorted(set(data) - required)
        raise SystemExit(f"invalid ExampleWorkflow provider work order fields: missing={missing}, extra={extra}")
    if data["schema_name"] != "example_workflow.provider_work_order" or data["schema_version"] != 1:
        raise SystemExit("--work-order requires example_workflow.provider_work_order schema version 1")
    if not str(data["request_id"]).startswith("example_workflow:/generation-request/"):
        raise SystemExit("work-order request_id must use example_workflow:/generation-request/")
    if data["provider_id"] not in {"trellis1", "trellis2", "skill:trellis1", "skill:trellis2"}:
        raise SystemExit("work-order provider_id must name trellis1 or trellis2")
    return data


def flag_present(argv: list[str], flag: str) -> bool:
    return any(value == flag or value.startswith(f"{flag}=") for value in argv)


def apply_work_order(parser: argparse.ArgumentParser, args: argparse.Namespace, argv: list[str]) -> None:
    args.work_order_data = {}
    if not args.work_order:
        return

    data = load_work_order(args.work_order)
    args.work_order_data = data
    if not flag_present(argv, "--provider"):
        args.provider = str(data["provider_id"]).removeprefix("skill:")
    if not flag_present(argv, "--request-id"):
        args.request_id = data["request_id"]
    if not flag_present(argv, "--free-only"):
        args.free_only = bool(data["free_only"])
    if not flag_present(argv, "--no-quota-wait"):
        args.quota_wait = bool(data["quota_wait"])

    if not args.image and not args.multi_image:
        paths: list[Path] = []
        for artifact in data["inputs"]:
            artifact_path = Path(artifact["path"])
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                parser.error("work-order input paths must be relative and traversal-free")
            resolved = (args.work_order.parent / artifact_path).resolve()
            if not resolved.is_file():
                parser.error(f"work-order input does not exist: {resolved}")
            if resolved.stat().st_size != artifact["byte_length"] or sha256_file(resolved) != artifact["sha256"]:
                parser.error(f"work-order input digest mismatch: {artifact_path}")
            paths.append(resolved)
        if len(paths) == 1:
            args.image = paths[0]
        elif paths:
            args.multi_image = paths

    known_parameters = {
        "seed",
        "ss_guidance_strength",
        "ss_sampling_steps",
        "slat_guidance_strength",
        "slat_sampling_steps",
        "multiimage_algo",
        "mesh_simplify",
        "texture_size",
        "resolution",
        "ss_guidance_rescale",
        "ss_rescale_t",
        "shape_slat_guidance_strength",
        "shape_slat_guidance_rescale",
        "shape_slat_sampling_steps",
        "shape_slat_rescale_t",
        "tex_slat_guidance_strength",
        "tex_slat_guidance_rescale",
        "tex_slat_sampling_steps",
        "tex_slat_rescale_t",
        "decimation_target",
        "pbr_required",
    }
    unknown = sorted(set(data["parameters"]) - known_parameters)
    if unknown:
        parser.error(f"work-order contains unsupported TRELLIS parameters: {unknown}")
    for name, value in data["parameters"].items():
        flag = f"--{name.replace('_', '-')}"
        if not flag_present(argv, flag):
            setattr(args, name, value)


def iter_file_values(value: Any) -> Iterable[tuple[str, str | None]]:
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from iter_file_values(item)
        return

    if isinstance(value, dict):
        path = value.get("path")
        url = value.get("url")
        if isinstance(path, str):
            yield path, url if isinstance(url, str) else None
        for key, child in value.items():
            if key not in {"path", "url"}:
                yield from iter_file_values(child)
        return

    if isinstance(value, str):
        yield value, None


def copy_outputs(result: Any, destination: Path) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    used_names: set[str] = set()
    for path_string, url in iter_file_values(result):
        local_path = Path(path_string).expanduser()
        suffix = local_path.suffix.lower()
        if suffix not in {".glb", ".mp4", ".ply", ".png", ".webp", ".jpg", ".jpeg"}:
            continue

        source_key = f"{path_string}|{url or ''}"
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)

        name = preferred_name(suffix, local_path.name, used_names)
        target = destination / name

        if local_path.is_file():
            shutil.copy2(local_path, target)
        elif url:
            download(url, target)
        else:
            continue

        used_names.add(name)
        copied.append({"path": str(target), "bytes": target.stat().st_size, "source": path_string})
    return copied


def preferred_name(suffix: str, fallback: str, used_names: set[str]) -> str:
    stem_by_suffix = {
        ".glb": "model",
        ".mp4": "preview",
        ".ply": "gaussian",
    }
    stem = stem_by_suffix.get(suffix, Path(fallback).stem or "artifact")
    candidate = f"{stem}{suffix}"
    counter = 2
    while candidate in used_names:
        candidate = f"{stem}-{counter}{suffix}"
        counter += 1
    return candidate


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-trellis-skill/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        target.write_bytes(response.read())


def make_jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [make_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): make_jsonable(item) for key, item in value.items()}
    return repr(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["trellis1", "trellis2", "auto"], help="Hosted TRELLIS provider; omitted and auto preserve the v1 path until policy selection is requested.")
    parser.add_argument("--probe", action="store_true", help="Capture the selected provider's live API schema and capabilities, then exit.")
    parser.add_argument("--info", action="store_true", help="Backward-compatible alias for --probe.")
    parser.add_argument("--free-only", action="store_true", help="Forbid paid compute escalation and map exhausted free quota to waiting_for_quota.")
    parser.add_argument("--pbr-required", action="store_true", help="Require TRELLIS.2 plus audited base-color, roughness, and metallic GLB textures.")
    parser.add_argument("--no-quota-wait", dest="quota_wait", action="store_false", help="Treat unavailable free quota as a failed attempt instead of a durable wait.")
    parser.set_defaults(quota_wait=True)
    parser.add_argument("--capabilities-out", type=output_file, help="Write the exact provider capability snapshot as JSON.")
    parser.add_argument("--work-order", type=existing_file, help="ExampleWorkflow provider work-order JSON used to populate provider, inputs, and parameters.")
    parser.add_argument("--attempt-receipt", type=output_file, help="Write a redacted example_workflow.provider_attempt_receipt JSON after generation.")
    parser.add_argument("--request-id", help="ExampleWorkflow generation request identity for an ad hoc attempt receipt.")
    parser.add_argument("--attempt-id", help="ExampleWorkflow generation attempt identity for an ad hoc attempt receipt.")
    parser.add_argument("--audit-glb", type=existing_file, help="Audit one local GLB for material channels without contacting a provider.")
    parser.add_argument("--audit-out", type=output_file, help="Write GLB PBR audit JSON; generation defaults to <output-dir>/pbr-audit.json.")
    parser.add_argument("--check-token", action="store_true", help="Verify that a Hugging Face token is configured without printing it.")
    parser.add_argument("--setup-token", action="store_true", help="Store a Hugging Face token in the local cache using a hidden prompt when possible.")
    parser.add_argument("--prepare-image", type=existing_file, help="Prepare one concept-art image for TRELLIS and exit.")
    parser.add_argument("--prepare-output-dir", type=output_dir, help="Directory for prepared TRELLIS input images.")
    parser.add_argument("--crop-box", type=parse_crop_box, help="Crop source before preparation: left,top,right,bottom.")
    parser.add_argument("--output-stem", help="Stem for prepared image filenames.")
    parser.add_argument("--canvas-size", type=int, default=768, help="Square prepared image size in pixels.")
    parser.add_argument("--padding", type=int, default=64, help="Padding around fitted crop in pixels.")
    parser.add_argument("--background-rgb", type=parse_rgb, default=(128, 128, 128), help="Neutral canvas RGB, e.g. 128,128,128.")
    parser.add_argument("--alpha-sat-threshold", type=float, default=0.13, help="Maximum HSV saturation for neutral border background.")
    parser.add_argument("--alpha-value-min", type=float, default=0.22, help="Minimum HSV value for neutral border background.")
    parser.add_argument("--alpha-value-max", type=float, default=0.86, help="Maximum HSV value for neutral border background.")
    parser.add_argument("--alpha-blur", type=float, default=1.1, help="Gaussian blur radius for the generated alpha mask.")
    parser.add_argument("--image", type=existing_file, help="Single concept image path.")
    parser.add_argument("--multi-image", type=existing_file, action="append", default=[], help="One view image path. Repeat for multi-image input.")
    parser.add_argument("--output-dir", type=output_dir, default=Path.cwd() / "trellis-output", help="Directory for copied outputs and manifest.")
    parser.add_argument("--token", help="Hugging Face token. Defaults to HF_TOKEN, HUGGINGFACEHUB_API_TOKEN, or the local Hugging Face cache.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--randomize-seed", action="store_true")
    parser.add_argument("--ss-guidance-strength", type=float)
    parser.add_argument("--ss-sampling-steps", type=int)
    parser.add_argument("--slat-guidance-strength", type=float)
    parser.add_argument("--slat-sampling-steps", type=int)
    parser.add_argument("--multiimage-algo", choices=["stochastic", "multidiffusion"])
    parser.add_argument("--mesh-simplify", type=float)
    parser.add_argument("--texture-size", type=int, choices=[512, 1024, 2048, 4096])
    parser.add_argument("--resolution", choices=["512", "1024", "1536"])
    parser.add_argument("--ss-guidance-rescale", type=float)
    parser.add_argument("--ss-rescale-t", type=float)
    parser.add_argument("--shape-slat-guidance-strength", type=float)
    parser.add_argument("--shape-slat-guidance-rescale", type=float)
    parser.add_argument("--shape-slat-sampling-steps", type=int)
    parser.add_argument("--shape-slat-rescale-t", type=float)
    parser.add_argument("--tex-slat-guidance-strength", type=float)
    parser.add_argument("--tex-slat-guidance-rescale", type=float)
    parser.add_argument("--tex-slat-sampling-steps", type=int)
    parser.add_argument("--tex-slat-rescale-t", type=float)
    parser.add_argument("--decimation-target", type=int)
    parser.add_argument("--extract-gaussian", action="store_true")
    return parser


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.info or args.probe or args.check_token or args.setup_token:
        return
    if args.audit_glb:
        if args.audit_glb.suffix.lower() != ".glb":
            parser.error("--audit-glb requires a .glb file")
        return
    if args.prepare_image:
        validate_prepare_args(parser, args)
        return
    if args.image and args.multi_image:
        parser.error("use either --image or repeated --multi-image, not both")
    if not args.image and not args.multi_image:
        parser.error("provide --image or at least one --multi-image")
    if args.provider == "trellis2" and args.multi_image:
        parser.error("the live TRELLIS.2 Space does not expose multi-image generation")
    if args.provider == "trellis2" and args.extract_gaussian:
        parser.error("the live TRELLIS.2 Space does not expose Gaussian extraction")
    if args.pbr_required and args.provider != "trellis2":
        parser.error("--pbr-required requires trellis2 and never falls back to trellis1")
    if args.provider == "trellis1" and args.texture_size == 4096:
        parser.error("the live TRELLIS v1 Space supports texture sizes up to 2048")
    if not 0 <= args.seed <= MAX_SEED:
        parser.error(f"--seed must be between 0 and {MAX_SEED}")
    if not 0.0 <= args.ss_guidance_strength <= 10.0:
        parser.error("--ss-guidance-strength must be between 0.0 and 10.0")
    if not 1 <= args.ss_sampling_steps <= 50:
        parser.error("--ss-sampling-steps must be between 1 and 50")
    if not 0.0 <= args.slat_guidance_strength <= 10.0:
        parser.error("--slat-guidance-strength must be between 0.0 and 10.0")
    if not 1 <= args.slat_sampling_steps <= 50:
        parser.error("--slat-sampling-steps must be between 1 and 50")
    if not 0.9 <= args.mesh_simplify <= 0.98:
        parser.error("--mesh-simplify must be between 0.9 and 0.98")
    if args.decimation_target <= 0:
        parser.error("--decimation-target must be positive")


def validate_prepare_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.image or args.multi_image:
        parser.error("--prepare-image is a preparation-only operation; run generation in a second command")
    if args.canvas_size <= 0:
        parser.error("--canvas-size must be positive")
    if args.padding < 0 or args.padding * 2 >= args.canvas_size:
        parser.error("--padding must be non-negative and leave room for the image")
    if not 0.0 <= args.alpha_sat_threshold <= 1.0:
        parser.error("--alpha-sat-threshold must be between 0.0 and 1.0")
    if not 0.0 <= args.alpha_value_min <= 1.0:
        parser.error("--alpha-value-min must be between 0.0 and 1.0")
    if not 0.0 <= args.alpha_value_max <= 1.0:
        parser.error("--alpha-value-max must be between 0.0 and 1.0")
    if args.alpha_value_max <= args.alpha_value_min:
        parser.error("--alpha-value-max must be greater than --alpha-value-min")
    if args.alpha_blur < 0:
        parser.error("--alpha-blur must be non-negative")


def main() -> int:
    parser = build_parser()
    argv = sys.argv[1:]
    args = parser.parse_args(argv)
    apply_work_order(parser, args, argv)
    args.provider = selected_provider_name(args.provider, args.pbr_required)
    apply_provider_defaults(args)
    validate_args(parser, args)

    try:
        if args.info or args.probe:
            print(json.dumps(probe_provider(args.provider, args.capabilities_out), indent=2))
            return 0
        if args.check_token:
            return print_token_status()
        if args.setup_token:
            return setup_token(args.token)
        if args.audit_glb:
            report = audit_glb(args.audit_glb)
            if args.audit_out:
                args.audit_out.parent.mkdir(parents=True, exist_ok=True)
                args.audit_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
            return 0 if not args.pbr_required or report["pbr_required_complete"] else 1
        if args.prepare_image:
            manifest = run_prepare_image(args)
            print(json.dumps(manifest, indent=2))
            return 0
        manifest = run_generation(args)
    except ProviderAttemptError as exc:
        print(f"TRELLIS attempt {exc.status}: {exc}", file=sys.stderr)
        return 2 if exc.status in {"waiting_for_quota", "waiting_for_provider"} else 1
    except urllib.error.URLError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        message = str(exc)
        if "ZeroGPU quota" in message or "exceeded your ZeroGPU quota" in message:
            print(
                "TRELLIS generation was rejected by Hugging Face ZeroGPU quota.\n"
                f"{message}\n"
                "Set HF_TOKEN or pass --token with a Hugging Face token, or retry after the reset time.",
                file=sys.stderr,
            )
            return 2
        raise

    print(json.dumps({"manifest": manifest["manifest"], "outputs": manifest["outputs"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
