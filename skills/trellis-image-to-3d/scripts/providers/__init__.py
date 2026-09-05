"""TRELLIS provider registry."""

from __future__ import annotations

from types import ModuleType

from . import trellis1, trellis2


PROVIDERS: dict[str, ModuleType] = {
    "trellis1": trellis1,
    "trellis2": trellis2,
}


def get_provider(name: str) -> ModuleType:
    try:
        return PROVIDERS[name]
    except KeyError as exc:
        raise ValueError(f"unknown TRELLIS provider: {name}") from exc
