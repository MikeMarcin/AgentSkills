#!/usr/bin/env python3
"""Temporary forwarder to the remote-station skill's `station_control.py`.

Station scripts moved from implement-rfc to the sibling remote-station skill.
This forwarder keeps existing wrappers and documentation working for one
release; it will be removed in a later one. It runs the sibling script in this
process with the same arguments, stdio and exit status, and exposes `main` for
callers that load it with runpy. It contains no station logic.
"""

from __future__ import annotations

import os
import pathlib
import runpy
import sys

NAME = "station_control.py"


def sibling_script() -> pathlib.Path | None:
    """The sibling skill's script, beside this skill's link or its source."""
    unresolved = pathlib.Path(os.path.abspath(__file__)).parents[2]
    resolved = pathlib.Path(__file__).resolve().parents[2]
    for skills in dict.fromkeys((unresolved, resolved)):
        candidate = skills / "remote-station" / "scripts" / NAME
        if candidate.is_file():
            return candidate
    return None


def _load() -> dict:
    target = sibling_script()
    if target is None:
        print(
            "station scripts moved from implement-rfc to the remote-station skill, "
            "which is not installed beside it; run: mask install remote-station",
            file=sys.stderr,
        )
        raise SystemExit(2)
    sys.path.insert(0, str(target.parent))
    return runpy.run_path(str(target))


def main(argv: list[str] | None = None) -> int:
    return _load()["main"](argv)


if __name__ == "__main__":
    raise SystemExit(main())
