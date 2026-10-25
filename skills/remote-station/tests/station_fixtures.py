"""Explicit local station contexts for helper tests; no host config assumptions."""
import copy
import json
import subprocess
from pathlib import Path

CONFIG = {
    "schema": "remote-station.config.v1",
    "project": "fixture",
    "display_name": "Fixture",
    "origin_repo_name": "Fixture",
    "session_prefix": "fx",
    "station_registry_doc": "docs/development/remote-stations.md",
    "workstreams": {"main": {"branch": "main"}},
}


def write_context(root: Path, *, token: str = "fixture", config: dict | None = None) -> dict:
    facts = copy.deepcopy(config if config is not None else CONFIG)
    if config is None:
        facts.update(project=token, display_name=token.title(), session_prefix=token, origin_repo_name=token)
    directory = root / ".mask/skill-config/remote-station"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "station.json").write_text(json.dumps(facts), encoding="utf-8")
    return facts


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def init_repo(root: Path, *, token: str = "fixture", auto_maintenance: bool = True) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-b", "main")
    if not auto_maintenance:
        git(root, "config", "maintenance.auto", "false")
    git(root, "config", "user.name", "fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    facts = write_context(root, token=token)
    git(root, "add", ".mask")
    git(root, "commit", "-m", "fixture context")
    return facts


def context_for(root: Path, config: dict | None = None):
    import station_config
    facts = copy.deepcopy(config if config is not None else CONFIG)
    path = root / ".mask/skill-config/remote-station/station.json"
    return station_config.ConsumerContext(station_config.SKILL_DIR, root.resolve(), path, facts)
