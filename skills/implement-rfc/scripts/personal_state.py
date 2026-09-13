"""Machine-local personal tracker bindings; no source repository writes."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

SCHEMA = "implement-rfc.personal-binding.v1"
HOME_ENV = "IMPLEMENT_RFC_HOME"


class PersonalStateError(ValueError):
    pass


def git(root: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            text=True, env=env)
    if result.returncode:
        raise PersonalStateError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def git_root(path: Path) -> Path:
    candidate = path.expanduser().resolve()
    root = Path(git(candidate, "rev-parse", "--show-toplevel")).resolve()
    if candidate != root:
        raise PersonalStateError(f"selected path must be a Git worktree root: {root}")
    return root


def common_dir(root: Path) -> Path:
    value = Path(git(root, "rev-parse", "--git-common-dir"))
    return (value if value.is_absolute() else root / value).resolve()


def _disjoint(a: Path, b: Path) -> bool:
    return not (a == b or a.is_relative_to(b) or b.is_relative_to(a))


def _check_no_symlink(path: Path) -> None:
    if path.is_symlink():
        raise PersonalStateError(f"writable path is a symlink: {path}")


def _check_local_path(home: Path, path: Path) -> None:
    if not path.is_relative_to(home):
        raise PersonalStateError(f"local state escapes {home}: {path}")
    current = path
    while current != home:
        _check_no_symlink(current)
        current = current.parent


def home_for(source_root: Path) -> Path:
    raw = os.environ.get(HOME_ENV, "~/.implement-rfc")
    if not raw.strip():
        raise PersonalStateError(f"{HOME_ENV} must not be empty")
    home = Path(raw).expanduser()
    if not home.is_absolute():
        raise PersonalStateError(f"{HOME_ENV} must be absolute")
    _check_no_symlink(home)
    home = home.resolve()
    return home


def ensure_home_separate(home: Path, source_root: Path) -> None:
    if not _disjoint(home, source_root) or not _disjoint(home, common_dir(source_root)):
        raise PersonalStateError(f"{HOME_ENV} overlaps the source repository")


def binding_key(source_root: Path) -> str:
    path = common_dir(source_root)
    identity = _common_identity(path)
    value = f"{path}\0{identity['device']}\0{identity['inode']}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _common_identity(path: Path) -> dict[str, int]:
    try:
        stat = path.stat()
    except OSError as exc:
        raise PersonalStateError(f"cannot inspect Git common directory: {path}: {exc}") from exc
    if stat.st_ino <= 0:
        raise PersonalStateError(f"Git common directory lacks a stable local identity: {path}")
    return {"device": stat.st_dev, "inode": stat.st_ino}


def binding_path(home: Path, source_root: Path) -> Path:
    path = home / "bindings" / f"{binding_key(source_root)}.json"
    _check_local_path(home, path)
    return path


def read_binding(home: Path, source_root: Path) -> dict | None:
    path = binding_path(home, source_root)
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise PersonalStateError(f"unsafe personal binding: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PersonalStateError(f"invalid personal binding: {path}: {exc}") from exc
    if (not isinstance(data, dict) or set(data) != {"schema", "mode", "source_common_dir",
                                                   "source_common_identity", "tracker_root", "tracker_common_dir"}
            or data["schema"] != SCHEMA or data["mode"] != "personal"
            or data["source_common_dir"] != str(common_dir(source_root))
            or data["source_common_identity"] != _common_identity(common_dir(source_root))
            or not isinstance(data["tracker_root"], str)
            or not isinstance(data["tracker_common_dir"], str)):
        raise PersonalStateError(f"personal binding does not match source identity: {path}")
    tracker = Path(data["tracker_root"])
    if not tracker.is_absolute() or git_root(tracker) != tracker or str(common_dir(tracker)) != data["tracker_common_dir"]:
        raise PersonalStateError(f"personal tracker identity changed: {tracker}")
    ensure_separate(source_root, tracker)
    ensure_local_state_separate(home, tracker)
    return data


def ensure_separate(source_root: Path, tracker_root: Path) -> None:
    for source_part in (source_root, common_dir(source_root)):
        for tracker_part in (tracker_root, common_dir(tracker_root)):
            if not _disjoint(source_part, tracker_part):
                raise PersonalStateError("source and tracker repositories overlap")


def ensure_local_state_separate(home: Path, tracker_root: Path) -> None:
    for state in (home / "bindings", home / "runtime"):
        _check_local_path(home, state)
        for tracker_part in (tracker_root, common_dir(tracker_root)):
            if not _disjoint(state, tracker_part):
                raise PersonalStateError("personal bindings or runtime state overlap the tracker")


def _tracker_config(name: str) -> dict:
    from project_config import LANE_KEYS, SCHEMA as PROJECT_SCHEMA

    lanes = dict(zip(LANE_KEYS, ("00-inbox", "10-backlog", "20-ready", "30-in-progress",
                                   "40-parked", "50-blocked", "60-done")))
    return {
        "schema": PROJECT_SCHEMA, "project": "personal", "display_name": "Personal RFC tracker",
        "session_prefix": "personal", "origin_repo_name": name,
        "rfc_root": "docs/rfcs", "issue_root": "docs/issues",
        "next_id": {"mode": "single-file", "path": "docs/issues/NEXT_ID"},
        "reservations_dir": "docs/issues/_reservations",
        "allocate_id_command": "python3 scripts/allocate_issue_id.py",
        "lanes": lanes,
        "lane_statuses": dict(zip(lanes.values(), ("Inbox", "Backlog", "Ready", "In Progress",
                                                  "Parked", "Blocked", "Done"))),
        "terminal_rfc_status": "Auto-Verified", "structure_gate": [],
        "attended_review_skill": "attended-review",
        "station_registry_doc": "docs/development/remote-stations.md",
        "workstreams": {"main": {"branch": "main"}}, "role_addenda": {},
    }


def _scaffold(tracker: Path) -> None:
    from project_config import CONTEXT_DIR, _origin_name, load

    if git(tracker, "symbolic-ref", "--quiet", "--short", "HEAD") != "main":
        raise PersonalStateError("tracker setup requires its main branch")
    context = tracker / CONTEXT_DIR
    if context.exists():
        config_path, rules_path = context / "project.json", context / "project.md"
        for path in (context, config_path, rules_path):
            if path.is_symlink() or not path.resolve().is_relative_to(tracker):
                raise PersonalStateError(f"unsafe tracker context path: {path}")
        config = load(config_path)
        if not rules_path.is_file():
            raise PersonalStateError("tracker project rules are missing")
        if "origin" in git(tracker, "remote").splitlines():
            if _origin_name(git(tracker, "remote", "get-url", "origin")) != config["origin_repo_name"]:
                raise PersonalStateError("tracker origin does not match its project identity")
        return
    if any(tracker.iterdir()):
        # A newly initialized repository contains only its Git directory.
        if (any(path.name != ".git" for path in tracker.iterdir())
                or git(tracker, "rev-list", "--all", "--count") != "0"
                or git(tracker, "ls-files")):
            raise PersonalStateError("supplied tracker has unmanaged content; configure it explicitly")
    context.mkdir(parents=True)
    config = _tracker_config(tracker.name)
    (context / "project.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (context / "project.md").write_text("# Personal tracker rules\n\nSource paths and process state are local. Product commits target the bound source checkout. Preserve explicit publication authority.\n", encoding="utf-8")
    (tracker / "docs/rfcs").mkdir(parents=True)
    (tracker / "docs/issues").mkdir(parents=True)
    (tracker / "docs/rfcs/README.md").write_text("# Personal RFC tracker\n", encoding="utf-8")
    (tracker / "docs/issues/README.md").write_text("# Personal issue board\n", encoding="utf-8")
    (tracker / "docs/issues/NEXT_ID").write_text("PRS-0001\n", encoding="utf-8")
    git(tracker, "add", "--", str(CONTEXT_DIR), "docs/rfcs/README.md",
        "docs/issues/README.md", "docs/issues/NEXT_ID")
    git(tracker, "-c", "user.name=implement-rfc", "-c", "user.email=implement-rfc@localhost",
        "commit", "-m", "Initialize personal workflow tracker")


def initialize(source_root: Path, tracker_path: Path | None = None) -> dict:
    source_root = git_root(source_root)
    home = home_for(source_root)
    ensure_home_separate(home, source_root)
    old = read_binding(home, source_root)
    if old:
        if tracker_path is not None and git_root(tracker_path) != Path(old["tracker_root"]):
            raise PersonalStateError("source is already bound to a different tracker")
        return old
    if tracker_path is None:
        tracker = home / "trackers" / binding_key(source_root)
        _check_local_path(home, tracker)
        if tracker.exists():
            raise PersonalStateError(f"unbound managed tracker already exists: {tracker}")
        tracker.parent.mkdir(parents=True, exist_ok=True)
        tracker.mkdir()
        git(tracker, "init", "-b", "main")
    else:
        _check_no_symlink(tracker_path.expanduser())
        tracker = git_root(tracker_path)
    ensure_separate(source_root, tracker)
    ensure_local_state_separate(home, tracker)
    _scaffold(tracker)
    data = {"schema": SCHEMA, "mode": "personal", "source_common_dir": str(common_dir(source_root)),
            "source_common_identity": _common_identity(common_dir(source_root)),
            "tracker_root": str(tracker), "tracker_common_dir": str(common_dir(tracker))}
    path = binding_path(home, source_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    except FileExistsError as exc:
        raise PersonalStateError(f"personal binding appeared concurrently: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return data
