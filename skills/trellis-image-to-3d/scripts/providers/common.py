"""Provider-neutral records and Gradio helpers for the TRELLIS client."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable


Predict = Callable[..., Any]


@dataclass(frozen=True)
class ProviderBinding:
    name: str
    provider_id: str
    space_id: str
    host: str
    generation_endpoint: str
    required_endpoints: tuple[str, ...]
    free_only_supported: bool
    supports_multi_image: bool
    supports_gaussian: bool
    declared_pbr_channels: tuple[str, ...]

    @property
    def info_url(self) -> str:
        return f"{self.host}/gradio_api/info"


@dataclass(frozen=True)
class ProviderRun:
    settings: dict[str, Any]
    raw_result: Any


def upload_file(path: Any, handle_file: Callable[[str], Any]) -> Any:
    return handle_file(str(path))


def upload_gallery(paths: list[Any], handle_file: Callable[[str], Any]) -> list[dict[str, Any]]:
    return [{"image": upload_file(path, handle_file), "caption": None} for path in paths]


def as_upload(value: Any, handle_file: Callable[[str], Any]) -> Any:
    if isinstance(value, str):
        return handle_file(value)
    if isinstance(value, dict) and value.get("path"):
        return handle_file(value["path"])
    return value


def as_gallery_upload(value: Any, handle_file: Callable[[str], Any]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    gallery: list[dict[str, Any]] = []
    for item in value:
        image = item.get("image") if isinstance(item, dict) else item
        gallery.append({"image": as_upload(image, handle_file), "caption": None})
    return gallery


def canonical_json_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def summarize_endpoint(endpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "parameters": [
            {
                "name": parameter.get("parameter_name"),
                "component": parameter.get("component"),
                "default": parameter.get("parameter_default"),
            }
            for parameter in endpoint.get("parameters", [])
        ],
        "returns": [
            {
                "label": value.get("label"),
                "component": value.get("component"),
            }
            for value in endpoint.get("returns", [])
        ],
        "description": endpoint.get("description", ""),
        "show_api": endpoint.get("show_api"),
    }


def capability_snapshot(binding: ProviderBinding, api_schema: dict[str, Any], captured_at: str) -> dict[str, Any]:
    endpoints = api_schema.get("named_endpoints", {})
    missing = [name for name in binding.required_endpoints if name not in endpoints]
    snapshot = {
        "schema_name": "example-scene.trellis_provider_capabilities",
        "schema_version": 1,
        "captured_at": captured_at,
        "provider": binding.name,
        "provider_id": binding.provider_id,
        "space": binding.space_id,
        "host": binding.host,
        "api_schema_digest": canonical_json_digest(api_schema),
        "available": not missing,
        "missing_required_endpoints": missing,
        "capabilities": {
            "image_to_3d": binding.generation_endpoint in endpoints,
            "free_only": binding.free_only_supported,
            "paid_escalation": False,
            "multi_image": binding.supports_multi_image,
            "gaussian_splat": binding.supports_gaussian,
            "pbr_channels": list(binding.declared_pbr_channels),
        },
        "endpoints": {
            name: summarize_endpoint(endpoints[name])
            for name in sorted(endpoints)
        },
    }
    snapshot["snapshot_digest"] = canonical_json_digest(snapshot)
    return snapshot
