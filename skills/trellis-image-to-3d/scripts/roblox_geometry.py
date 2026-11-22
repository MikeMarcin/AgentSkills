"""Measure the declared geometry of each mesh primitive that Studio imports."""

from __future__ import annotations

from typing import Any


MAX_TRIANGLES_PER_PART = 20_000


def accessor(document: dict, index: Any, shape: str) -> dict:
    items = document.get("accessors", [])
    if type(index) is not int or not isinstance(items, list) or not 0 <= index < len(items):
        raise ValueError(f"invalid {shape} accessor index {index!r}")
    item = items[index]
    if not isinstance(item, dict) or item.get("type") != shape:
        raise ValueError(f"expected a {shape} accessor at index {index}")
    count = item.get("count")
    if type(count) is not int or count < 1:
        raise ValueError(f"invalid element count in accessor {index}")
    return item


def triangle_count(document: dict, primitive: dict) -> int:
    attributes = primitive.get("attributes")
    if not isinstance(attributes, dict) or "POSITION" not in attributes:
        raise ValueError("missing POSITION attribute")
    positions = accessor(document, attributes["POSITION"], "VEC3")
    count = positions["count"]
    if "indices" in primitive:
        indices = accessor(document, primitive["indices"], "SCALAR")
        if indices.get("componentType") not in (5121, 5123, 5125):
            raise ValueError("indices require an unsigned integer accessor")
        count = indices["count"]

    mode = primitive.get("mode", 4)
    if type(mode) is not int or mode not in (4, 5, 6):
        raise ValueError(f"primitive mode {mode!r} has no triangle surface")
    if count < 3 or (mode == 4 and count % 3 != 0):
        raise ValueError(f"invalid element count {count} for triangle mode {mode}")
    return count // 3 if mode == 4 else count - 2


def audit_geometry(document: dict, budget: int) -> dict:
    parts = []
    errors = []
    meshes = document.get("meshes")
    if not isinstance(meshes, list) or not meshes:
        errors.append("the GLB has no mesh definitions")
        meshes = []
    for mesh_index, mesh in enumerate(meshes):
        primitives = mesh.get("primitives") if isinstance(mesh, dict) else None
        if not isinstance(primitives, list) or not primitives:
            errors.append(f"mesh {mesh_index} has no primitives")
            continue
        for index, primitive in enumerate(primitives):
            part = {"mesh": mesh_index, "name": mesh.get("name"), "primitive": index, "triangles": None}
            parts.append(part)
            try:
                if not isinstance(primitive, dict):
                    raise ValueError("expected a primitive object")
                triangles = triangle_count(document, primitive)
                part["triangles"] = triangles
                if triangles > budget:
                    raise ValueError(f"{triangles} triangles exceed the {budget} limit")
            except ValueError as error:
                errors.append(f"mesh {mesh_index}, primitive {index}: {error}")
    return {
        "max_triangles_per_part": budget,
        "parts": parts,
        "within_budget": bool(parts) and not errors,
        "errors": errors,
    }
