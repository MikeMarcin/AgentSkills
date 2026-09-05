"""Explicit local project contexts for helper tests; no host config assumptions."""
import copy
import json
import subprocess
from pathlib import Path

CONFIG = {
    "schema": "implement-rfc.project.v2",
    "project": "fixture",
    "display_name": "Fixture",
    "session_prefix": "fx",
    "origin_repo_name": "Fixture",
    "rfc_root": "docs/rfcs",
    "issue_root": "docs/issues",
    "next_id": {"mode": "single-file", "path": "docs/issues/NEXT_ID"},
    "reservations_dir": "docs/issues/_reservations",
    "allocate_id_command": "python3 scripts/allocate_issue_id.py",
    "lanes": {
        "backlog": "10-backlog",
        "ready": "20-ready",
        "inbox": "00-inbox",
        "in_progress": "30-in-progress",
        "parked": "40-parked",
        "blocked": "50-blocked",
        "done": "60-done",
    },
    "lane_statuses": {
        "10-backlog": "Backlog",
        "20-ready": "Ready",
        "00-inbox": "Inbox",
        "30-in-progress": "In Progress",
        "40-parked": "Parked",
        "50-blocked": "Blocked",
        "60-done": "Done",
    },
    "terminal_rfc_status": "Auto-Verified",
    "structure_gate": [],
    "attended_review_skill": None,
    "station_registry_doc": "docs/development/remote-stations.md",
    "workstreams": {"main": {"branch": "main"}},
    "role_addenda": {},
}

def write_context(root: Path, *, token: str = "fixture", config: dict | None = None) -> dict:
    facts = copy.deepcopy(config if config is not None else CONFIG)
    if config is None:
        facts.update(project=token, display_name=token.title(), session_prefix=token, origin_repo_name=token)
    directory = root / ".mask/skill-config/implement-rfc"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "project.json").write_text(json.dumps(facts), encoding="utf-8")
    (directory / "project.md").write_text(f"# {facts['display_name']} rules\n", encoding="utf-8")
    return facts


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def init_repo(root: Path, *, token: str = "fixture") -> dict:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    facts = write_context(root, token=token)
    git(root, "add", ".mask")
    git(root, "commit", "-m", "fixture context")
    return facts


def context_for(root: Path, config: dict | None = None):
    import project_config
    facts = copy.deepcopy(config if config is not None else CONFIG)
    directory = root / ".mask/skill-config/implement-rfc"
    return project_config.ProjectContext(project_config.SKILL_DIR, root.resolve(),
        directory / "project.json", directory / "project.md", facts)
