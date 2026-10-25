#!/usr/bin/env python3
"""Resolve and validate one consumer's station configuration.

Every station script reads consumer identity through this module. The file is
`.mask/skill-config/remote-station/station.json` in the invoking checkout; the
skill's own physical path never selects a consumer. The checks mirror
`schemas/station-config.schema.json` so the skill runs on a bare Python
without a JSON Schema library. Key rules and messages match implement-rfc's
`project_config` for the identity keys both files carry.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
CONTEXT_DIR = Path(".mask/skill-config/remote-station")
CONFIG_NAME = "station.json"
PROJECT_ROOT_ENV = "REMOTE_STATION_PROJECT_ROOT"
SCHEMA = "remote-station.config.v1"
TOKEN_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLATFORM_TOKENS = ("win", "linux", "mac")
REQUIRED_KEYS = (
    "schema", "project", "display_name", "origin_repo_name", "session_prefix",
    "station_registry_doc", "workstreams",
)


class StationConfigError(ValueError):
    """Station configuration is missing, unreadable, or violates the contract."""


def _require_token(config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if not isinstance(value, str) or not TOKEN_RE.fullmatch(value):
        raise StationConfigError(f"{key} must be a lowercase hyphenated token, got {value!r}")


def _require_text(config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise StationConfigError(f"{key} must be a non-empty string")


def _require_relative_path(config: dict[str, Any], key: str) -> None:
    _require_text(config, key)
    value = config[key]
    if (Path(value).is_absolute() or value.endswith("/") or "\n" in value
            or "\\" in value or ".." in Path(value).parts or re.match(r"^[A-Za-z]:", value)):
        raise StationConfigError(f"{key} must be a repository-relative path without a trailing slash")


def validate(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise StationConfigError("station.json must be a JSON object")
    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        raise StationConfigError(f"station.json lacks required keys: {', '.join(missing)}")
    extra = sorted(set(config) - set(REQUIRED_KEYS))
    if extra:
        raise StationConfigError(f"station.json has unknown keys: {', '.join(extra)}")
    if config["schema"] != SCHEMA:
        raise StationConfigError(f"station.json schema must be {SCHEMA!r}")
    _require_token(config, "project")
    _require_token(config, "session_prefix")
    _require_text(config, "display_name")
    _require_text(config, "origin_repo_name")
    _require_relative_path(config, "station_registry_doc")
    workstreams = config["workstreams"]
    if not isinstance(workstreams, dict) or "main" not in workstreams:
        raise StationConfigError("workstreams must be an object containing 'main'")
    for name, spec in workstreams.items():
        if not TOKEN_RE.fullmatch(name):
            raise StationConfigError(f"workstream name {name!r} is not a token")
        if not isinstance(spec, dict) or not isinstance(spec.get("branch"), str) or not spec["branch"]:
            raise StationConfigError(f"workstream {name!r} needs a branch")
        if set(spec) - {"branch", "platform"}:
            raise StationConfigError(f"workstream {name!r} has unknown keys")
        if "platform" in spec and spec["platform"] not in PLATFORM_TOKENS:
            raise StationConfigError(f"workstream {name!r} names an unknown platform")
    return config


def load(path: Path) -> dict[str, Any]:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StationConfigError(
            f"missing station configuration: {path}; create {CONTEXT_DIR.as_posix()}/{CONFIG_NAME} "
            "in the consumer checkout") from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise StationConfigError(f"invalid JSON in {path}: {exc}") from exc
    return validate(data)


class ConsumerContext:
    """One invocation's skill assets and consumer facts; never cached globally."""

    def __init__(self, asset_root: Path, repo_root: Path, station_config_path: Path,
                 config: dict[str, Any]):
        self.asset_root = asset_root
        self.source_root = repo_root
        self.repo_root = repo_root
        self.station_config_path = station_config_path
        self.config = config


def git_environment() -> dict[str, str]:
    """Keep Git repository selectors from overriding an explicit consumer root."""
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def _git(root: Path, *args: str) -> str | None:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=git_environment())
    return result.stdout.strip() if result.returncode == 0 else None


def origin_name(origin: str) -> str:
    """The repository token of SSH and URL-style Git origins."""
    return origin.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1].rsplit(":", 1)[-1]


def resolve_context(*, repo_root: Path | str | None = None,
                    cwd: Path | str | None = None) -> ConsumerContext:
    """Select explicit root, environment, or invocation Git root, in that order."""
    invocation = Path(cwd) if cwd is not None else Path.cwd()
    selected = repo_root if repo_root is not None else os.environ.get(PROJECT_ROOT_ENV)
    if selected is not None and not str(selected).strip():
        raise StationConfigError("selected repository root must not be empty")
    candidate = Path(selected).expanduser() if selected is not None else invocation
    if not candidate.is_absolute():
        candidate = invocation / candidate
    candidate = candidate.resolve()
    top = _git(candidate, "rev-parse", "--show-toplevel")
    if top is None:
        raise StationConfigError(f"not a Git consumer repository: {candidate}; pass --repo-root PATH")
    root = Path(top).resolve()
    if selected is not None and candidate != root:
        raise StationConfigError(f"selected --repo-root must be the Git worktree root: {root}")
    config_path = root / CONTEXT_DIR / CONFIG_NAME
    if not config_path.resolve().is_relative_to(root):
        raise StationConfigError(f"station configuration escapes selected consumer {root}: {config_path}")
    config = load(config_path)
    origin = _git(root, "remote", "get-url", "origin")
    if origin and origin_name(origin) != config["origin_repo_name"]:
        raise StationConfigError(
            f"project identity mismatch: origin does not name configured repository {config['origin_repo_name']!r}")
    return ConsumerContext(SKILL_DIR.resolve(), root, config_path.resolve(), config)


def station_name(config: dict[str, Any], workstream: str, platform: str, machine: str = "") -> str:
    """`<prefix>-<workstream>-<platform>[-<machine>]`, omitting the platform token
    when the workstream is itself platform-bound (so `<prefix>-win-example-win-host`, not
    `<prefix>-win-win-example-win-host`, and `<prefix>-main-mac` for the integrator)."""
    spec = config["workstreams"][workstream]
    parts = [config["session_prefix"], workstream]
    if "platform" not in spec:
        parts.append(platform)
    if machine:
        parts.append(machine)
    return "-".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        context = resolve_context(repo_root=args.repo_root)
    except StationConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    config = context.config
    if args.json:
        print(json.dumps({"source_root": str(context.source_root),
                          "station_config": str(context.station_config_path),
                          "project": config["project"],
                          "workstreams": sorted(config["workstreams"])}))
    else:
        print(f"consumer: {context.source_root}")
        print(f"station.json valid: {config['project']} ({config['display_name']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
