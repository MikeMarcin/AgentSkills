"""Disposable consumers and forwarder runners for public entry-contract tests."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from station_fixtures import git, init_repo

SKILL_DIR = Path(__file__).resolve().parents[1]
RUNTIME_NAMES = ("codex", "claude")

PROBE = '''import json, os, sys
argv = sys.argv[1:]
data = sys.stdin.read()
print(json.dumps({"version": VERSION, "argv": argv, "cwd": os.getcwd(), "stdin": data}))
print("probe stderr " + VERSION, file=sys.stderr)
raise SystemExit(int(argv[argv.index("--exit") + 1]) if "--exit" in argv else 0)
'''


def link_skill(root: Path, source: Path) -> Path:
    """Install a skill the way MASK does: a directory link under .agents/skills."""
    link = root / ".agents/skills/remote-station"
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(source, target_is_directory=True)
    except OSError:
        shutil.copytree(source, link)
    return link


def probe_skill(base: Path, version: str) -> Path:
    """A different skill version whose entry script reports what it received."""
    skill = base / f"remote-station-{version}"
    (skill / "scripts").mkdir(parents=True)
    (skill / "scripts/launch_remote_station.py").write_text(
        f"VERSION = {version!r}\n" + PROBE, encoding="utf-8")
    return skill


def consumer(base: Path, token: str, skill: Path | None) -> Path:
    root = base / token
    init_repo(root, token=token)
    git(root, "remote", "add", "origin", f"https://example.invalid/owner/{token}.git")
    if skill is not None:
        link_skill(root, skill)
    return root


def environment(*, without_runtimes: bool = False) -> dict[str, str]:
    """Inherited environment without Git selectors; optionally no Codex/Claude on PATH."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if without_runtimes:
        suffixes = ("", ".exe", ".cmd", ".bat")
        kept = [entry for entry in env.get("PATH", "").split(os.pathsep)
                if entry and not any(os.path.isfile(os.path.join(entry, name + suffix))
                                     for name in RUNTIME_NAMES for suffix in suffixes)]
        env["PATH"] = os.pathsep.join(kept)
    return env


def posix_shell() -> str | None:
    """A POSIX sh for the extensionless forwarder; Git for Windows' sh on Windows."""
    if os.name != "nt":
        return "/bin/sh"
    found = shutil.which("sh")
    return found if found and "system32" not in found.lower() else None


def forwarder_kinds() -> list[str]:
    kinds = ["cmd"] if os.name == "nt" else []
    if posix_shell() is not None:
        kinds.append("sh")
    return kinds


def run_forwarder(kind: str, bin_dir: Path, cwd: Path, *args: str, stdin: str = "",
                  env: dict[str, str] | None = None, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    if kind == "cmd":
        command = [str(bin_dir / "launch_remote_station.cmd"), *args]
    else:
        command = [posix_shell(), str(bin_dir / "launch_remote_station"), *args]
    return subprocess.run(command, cwd=cwd, input=stdin, capture_output=True, text=True,
                          env=env or environment(), timeout=timeout)


def run_direct(root: Path, cwd: Path, *args: str, env: dict[str, str] | None = None,
               timeout: float = 60) -> subprocess.CompletedProcess[str]:
    """The entry script itself, invoked as a script by the caller's interpreter."""
    script = root / ".agents/skills/remote-station/scripts/launch_remote_station.py"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True,
                          text=True, env=env or environment(), timeout=timeout)
