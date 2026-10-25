#!/usr/bin/env python3
"""Resolve and validate one consumer project independently of shared skill assets.

Every other script in this directory imports this module instead of naming a
project, a tracker path, a lane, or a session prefix. The checks here mirror
`schemas/project.schema.json` so the skill stays runnable on a bare Python
without a JSON Schema library.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

SKILL_DIR = Path(__file__).resolve().parents[1]
CONTEXT_DIR = Path(".mask/skill-config/implement-rfc")
PROJECT_ROOT_ENV = "IMPLEMENT_RFC_PROJECT_ROOT"
SCHEMA = "implement-rfc.project.v2"
TOKEN_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLATFORM_TOKENS = ("win", "linux", "mac")
REQUIRED_KEYS = (
    "schema", "project", "display_name", "origin_repo_name",
    "rfc_root", "issue_root", "next_id", "reservations_dir", "allocate_id_command",
    "lanes", "lane_statuses", "terminal_rfc_status",
    "structure_gate", "attended_review_skill", "workstreams",
    "role_addenda",
)
# Station identity moved to the remote-station skill's station.json. These keys
# remain accepted and validated so existing project.json files stay valid.
LEGACY_STATION_KEYS = ("session_prefix", "station_registry_doc")
OPTIONAL_KEYS = ("bookkeeping", "sequencing", "allocation", *LEGACY_STATION_KEYS)
LANE_KEYS = ("inbox", "backlog", "ready", "in_progress", "parked", "blocked", "done")


class ProjectConfigError(ValueError):
    """Consumer context is missing, unreadable, or violates the contract."""


def _require_token(config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if not isinstance(value, str) or not TOKEN_RE.fullmatch(value):
        raise ProjectConfigError(f"{key} must be a lowercase hyphenated token, got {value!r}")


def _require_text(config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectConfigError(f"{key} must be a non-empty string")


def _require_relative_path(config: dict[str, Any], key: str) -> None:
    _require_text(config, key)
    value = config[key]
    if (Path(value).is_absolute() or value.endswith("/") or "\n" in value
            or "\\" in value or ".." in Path(value).parts or re.match(r"^[A-Za-z]:", value)):
        raise ProjectConfigError(f"{key} must be a repository-relative path without a trailing slash")


def validate(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ProjectConfigError("project.json must be a JSON object")
    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        raise ProjectConfigError(f"project.json lacks required keys: {', '.join(missing)}")
    extra = sorted(set(config) - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS))
    if extra:
        raise ProjectConfigError(f"project.json has unknown keys: {', '.join(extra)}")
    if config["schema"] != SCHEMA:
        raise ProjectConfigError(f"project.json schema must be {SCHEMA!r}")
    _require_token(config, "project")
    if "session_prefix" in config:
        _require_token(config, "session_prefix")
    _require_text(config, "display_name")
    _require_text(config, "origin_repo_name")
    for key in ("rfc_root", "issue_root", "reservations_dir"):
        _require_relative_path(config, key)
    if "station_registry_doc" in config:
        _require_relative_path(config, "station_registry_doc")
    _require_text(config, "allocate_id_command")
    _require_text(config, "terminal_rfc_status")

    next_id = config["next_id"]
    if not isinstance(next_id, dict) or next_id.get("mode") not in {"single-file", "per-area"}:
        raise ProjectConfigError("next_id.mode must be 'single-file' or 'per-area'")
    _require_relative_path(next_id, "path")

    lanes = config["lanes"]
    if not isinstance(lanes, dict) or set(lanes) != set(LANE_KEYS):
        raise ProjectConfigError(f"lanes must define exactly {', '.join(LANE_KEYS)}")
    for key in LANE_KEYS:
        _require_token(lanes, key)
    if len(set(lane_names(config))) != len(lane_names(config)):
        raise ProjectConfigError("lane directory names must be distinct")

    statuses = config["lane_statuses"]
    if not isinstance(statuses, dict) or set(statuses) != set(lane_names(config)):
        raise ProjectConfigError("lane_statuses must name every lane exactly once")
    for lane, status in statuses.items():
        if not isinstance(status, str) or not status.strip():
            raise ProjectConfigError(f"lane_statuses[{lane!r}] must be a non-empty string")

    if config.get("sequencing", "dependency") not in {"dependency", "ordered-index"}:
        raise ProjectConfigError("sequencing must be dependency or ordered-index")
    allocation = config.get("allocation", {})
    if not isinstance(allocation, dict) or set(allocation) - {"history_limit", "rewind_overrides"}:
        raise ProjectConfigError("allocation has unknown keys")
    limit = allocation.get("history_limit", 2000)
    if type(limit) is not int or not 1 <= limit <= 100000:
        raise ProjectConfigError("allocation.history_limit must be 1..100000")
    overrides = allocation.get("rewind_overrides", [])
    if not isinstance(overrides, list):
        raise ProjectConfigError("allocation.rewind_overrides must be a list")
    for override in overrides:
        if (not isinstance(override, dict) or set(override) != {"area", "floor", "waived_through", "date", "reason"}
            or not re.fullmatch(r"[A-Z]{2,8}", str(override["area"]))
            or type(override["floor"]) is not int or type(override["waived_through"]) is not int
            or not 1 <= override["floor"] <= override["waived_through"] <= 9999
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(override["date"]))
            or not isinstance(override["reason"], str) or not override["reason"].strip()):
            raise ProjectConfigError("invalid deliberate counter rewind override")

    gate = config["structure_gate"]
    if not isinstance(gate, list) or not all(isinstance(item, str) and item.strip() for item in gate):
        raise ProjectConfigError("structure_gate must be a list of command strings")

    attended = config["attended_review_skill"]
    if attended is not None and (not isinstance(attended, str) or not attended.strip()):
        raise ProjectConfigError("attended_review_skill must be a skill name or null")

    workstreams = config["workstreams"]
    if not isinstance(workstreams, dict) or "main" not in workstreams:
        raise ProjectConfigError("workstreams must be an object containing 'main'")
    for name, spec in workstreams.items():
        if not TOKEN_RE.fullmatch(name):
            raise ProjectConfigError(f"workstream name {name!r} is not a token")
        if not isinstance(spec, dict) or not isinstance(spec.get("branch"), str) or not spec["branch"]:
            raise ProjectConfigError(f"workstream {name!r} needs a branch")
        if set(spec) - {"branch", "platform"}:
            raise ProjectConfigError(f"workstream {name!r} has unknown keys")
        if "platform" in spec and spec["platform"] not in PLATFORM_TOKENS:
            raise ProjectConfigError(f"workstream {name!r} names an unknown platform")

    addenda = config["role_addenda"]
    if not isinstance(addenda, dict) or not all(
        isinstance(role, str)
        and isinstance(lines, list)
        and all(isinstance(line, str) and line.strip() for line in lines)
        for role, lines in addenda.items()
    ):
        raise ProjectConfigError("role_addenda must map role names to lists of instruction strings")
    if "bookkeeping" in config:
        rules = config["bookkeeping"]
        keys = {"deferring_lanes", "parked_on", "blocked_by_forbidden_prefixes",
                "link_roots", "protected_globs", "editable_globs"}
        if not isinstance(rules, dict) or set(rules) != keys:
            raise ProjectConfigError("bookkeeping must define exactly " + ", ".join(sorted(keys)))
        for key, values in rules.items():
            if not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values):
                raise ProjectConfigError(f"bookkeeping.{key} must be a list of nonempty strings")
            if len(values) != len(set(values)):
                raise ProjectConfigError(f"bookkeeping.{key} contains duplicates")
        if set(rules["deferring_lanes"]) - set(lane_names(config)):
            raise ProjectConfigError("bookkeeping.deferring_lanes names an unknown lane")
        for key in ("parked_on", "blocked_by_forbidden_prefixes"):
            if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", v) for v in rules[key]):
                raise ProjectConfigError(f"bookkeeping.{key} contains an invalid token")
        for key in ("link_roots", "protected_globs", "editable_globs"):
            for value in rules[key]:
                if value.startswith("/") or ".." in value.split("/") or "\\" in value or "\n" in value:
                    raise ProjectConfigError(f"bookkeeping.{key} must use repository-relative paths")
    return config


def load(path: Path | None = None, *, repo_root: Path | str | None = None) -> dict[str, Any]:
    """Read explicit facts, or resolve the invocation consumer when omitted."""
    if path is None:
        return resolve_context(repo_root=repo_root).config
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProjectConfigError(f"missing project configuration: {path}; create consumer project.json and project.md under {CONTEXT_DIR}") from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ProjectConfigError(f"invalid JSON in {path}: {exc}") from exc
    return validate(data)


def lane_names(config: dict[str, Any]) -> list[str]:
    """Every board lane directory, in board order."""
    lanes = config["lanes"]
    return [lanes[key] for key in LANE_KEYS]



def active_lanes(config: dict[str, Any]) -> list[str]:
    return [lane for lane in lane_names(config) if lane != config["lanes"]["done"]]


class ProjectContext:
    """One invocation's assets and consumer facts; never cached globally."""

    def __init__(self, asset_root: Path, repo_root: Path, project_config_path: Path,
                 project_rules_path: Path, config: dict[str, Any], *, legacy: bool = False,
                 mode: str = "project", workflow_root: Path | None = None,
                 runtime_root: Path | None = None, source_common_dir: Path | None = None,
                 workflow_common_dir: Path | None = None):
        self.asset_root = asset_root
        self.source_root = repo_root
        self.workflow_root = workflow_root or repo_root
        self.runtime_root = runtime_root
        self.mode = mode
        self.source_common_dir = source_common_dir
        self.workflow_common_dir = workflow_common_dir
        self.project_config_path = project_config_path
        self.project_rules_path = project_rules_path
        self.config = config
        self.legacy = legacy

    @property
    def repo_root(self) -> Path:
        """Compatibility accessor for helpers not yet routed through both roots."""
        if self.mode == "personal":
            raise ProjectConfigError("helper is not yet personal-mode aware; use source_root and workflow_root explicitly")
        return self.source_root


def git_environment() -> dict[str, str]:
    """Keep Git repository selectors from overriding an explicit consumer root."""
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def _git(root: Path, *args: str) -> str | None:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=git_environment())
    return result.stdout.strip() if result.returncode == 0 else None


def _origin_name(origin: str) -> str:
    return origin.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1].rsplit(":", 1)[-1]


def resolve_context(*, repo_root: Path | str | None = None,
                    cwd: Path | str | None = None,
                    project_config_path: Path | str | None = None,
                    mode: str | None = None,
                    workflow_root: Path | str | None = None) -> ProjectContext:
    """Select explicit root, environment, or invocation Git root, in that order.

    Explicit config overrides are fixture/authoring inputs beneath the selected
    consumer; they never choose the repository or redirect generated output.
    """
    invocation = Path(cwd) if cwd is not None else Path.cwd()
    selected = repo_root if repo_root is not None else os.environ.get(PROJECT_ROOT_ENV)
    if selected is not None and not str(selected).strip():
        raise ProjectConfigError("selected repository root must not be empty")
    candidate = Path(selected).expanduser() if selected is not None else invocation
    if not candidate.is_absolute():
        candidate = invocation / candidate
    candidate = candidate.resolve()
    top = _git(candidate, "rev-parse", "--show-toplevel")
    if top is None:
        raise ProjectConfigError(f"not a Git consumer repository: {candidate}; pass --repo-root PATH")
    root = Path(top).resolve()
    if selected is not None and candidate != root:
        raise ProjectConfigError(f"selected --repo-root must be the Git worktree root: {root}")
    if mode not in (None, "project", "personal"):
        raise ProjectConfigError("mode must be project or personal")
    import personal_state
    try:
        home = personal_state.home_for(root) if mode != "project" else None
        binding = personal_state.read_binding(home, root) if home is not None else None
        chosen_mode = mode or ("personal" if binding else "project")
        if chosen_mode == "personal":
            personal_state.ensure_home_separate(home, root)
            if workflow_root is not None:
                workflow = personal_state.git_root(Path(workflow_root))
                if binding and personal_state.common_dir(workflow) != Path(binding["tracker_common_dir"]):
                    raise ProjectConfigError("explicit workflow root conflicts with the personal binding")
            elif binding:
                workflow = Path(binding["tracker_root"])
            else:
                raise ProjectConfigError("personal mode has no binding; run personal_tracker.py init explicitly")
            import personal_lanes
            paired = personal_lanes.paired_root(root, workflow)
            if workflow_root is not None and paired != workflow:
                raise ProjectConfigError("explicit workflow root conflicts with the paired source lane")
            workflow = personal_state.git_root(paired)
            if binding and personal_state.common_dir(workflow) != Path(binding["tracker_common_dir"]):
                raise ProjectConfigError("paired worktree differs from the bound tracker repository")
            personal_state.ensure_separate(root, workflow)
            personal_state.ensure_local_state_separate(home, workflow)
        else:
            workflow = root
            if workflow_root is not None and Path(workflow_root).expanduser().resolve() != root:
                raise ProjectConfigError("project mode workflow root must equal the source root")
        source_common = personal_state.common_dir(root)
        workflow_common = personal_state.common_dir(workflow)
        runtime = home / "runtime" / personal_state.binding_key(root) if chosen_mode == "personal" else root
        if chosen_mode == "personal":
            personal_state._check_local_path(home, runtime)
    except personal_state.PersonalStateError as exc:
        raise ProjectConfigError(str(exc)) from exc
    assets = SKILL_DIR.resolve()
    context_dir = workflow / CONTEXT_DIR
    config_path = context_dir / "project.json"
    rules_path = context_dir / "project.md"
    legacy = False
    if project_config_path is not None:
        config_path = Path(project_config_path).expanduser()
        if not config_path.is_absolute():
            config_path = workflow / config_path
    for path in (config_path, rules_path):
        if not path.resolve().is_relative_to(workflow):
            raise ProjectConfigError(f"project context escapes selected consumer {workflow}: {path}")
    config = load(config_path)
    if not rules_path.is_file():
        raise ProjectConfigError(f"missing project rules: {rules_path}; create both files under {context_dir}")
    origin = _git(workflow, "remote", "get-url", "origin")
    if origin and _origin_name(origin) != config["origin_repo_name"]:
        raise ProjectConfigError(f"project identity mismatch: origin does not name configured repository {config['origin_repo_name']!r}")
    if legacy and not origin and root.name not in (config["origin_repo_name"], config["project"]):
        raise ProjectConfigError(f"legacy project identity mismatch for {root}")
    return ProjectContext(assets, root, config_path.resolve(), rules_path.resolve(), config,
                          legacy=legacy, mode=chosen_mode, workflow_root=workflow,
                          runtime_root=runtime, source_common_dir=source_common,
                          workflow_common_dir=workflow_common)


def repo_root() -> Path:
    """Compatibility accessor; selection occurs at the call, never at import."""
    return resolve_context().repo_root


def lane_log_name(config: dict[str, Any]) -> str:
    return f"{config['project']}-codex-lanes.jsonl"


def closeout_card_matcher(config: dict[str, Any]):
    """Return a predicate (path, front_matter) -> bool for closeout-card detection."""
    return lambda _path, matter: bool(matter.get("closeout_for"))



if __name__ == "__main__":
    import sys

    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--repo-root", type=Path)
        parser.add_argument("--mode", choices=("project", "personal"))
        parser.add_argument("--workflow-root", type=Path)
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args()
        context = resolve_context(repo_root=args.repo_root, mode=args.mode,
                                  workflow_root=args.workflow_root)
        loaded = context.config
    except ProjectConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
    if args.json:
        print(json.dumps({"mode": context.mode, "source_root": str(context.source_root),
                          "source_common_dir": str(context.source_common_dir),
                          "workflow_root": str(context.workflow_root),
                          "workflow_common_dir": str(context.workflow_common_dir),
                          "runtime_root": str(context.runtime_root) if context.runtime_root else None,
                          "project": loaded["project"]}))
    else:
        print(f"consumer: {context.source_root}")
        print(f"workflow: {context.workflow_root} ({context.mode})")
        print(f"project.json valid: {loaded['project']} ({loaded['display_name']})")
