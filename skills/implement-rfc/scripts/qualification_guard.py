"""Cooperative disposable-root command guard; deliberately not a sandbox."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


def absolute(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(f"absolute path required: {value}")
    return path


def contains(root: Path, path: Path) -> bool:
    return path == root or root in path.parents


def snapshot(path: Path) -> bytes | None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(mode):
        raise ValueError(f"live declaration must be a regular file or missing: {path}")
    return path.read_bytes()


@dataclass(frozen=True)
class LiveSnapshot:
    roots: tuple[Path, ...]
    files: tuple[tuple[Path, bytes | None], ...]


def capture_live(live_roots: list[str], live_files: list[str]) -> LiveSnapshot:
    """Capture explicit live declarations for an attended/native course in one caller."""
    roots = [absolute(p).resolve(strict=True) for p in live_roots]
    if not roots or not live_files or not all(p.is_dir() for p in roots):
        raise ValueError("explicit existing live roots and declaration files required")
    files = [absolute(p) for p in live_files]
    if any(not any(contains(root, p.resolve()) for root in roots) for p in files):
        raise ValueError("live declaration escapes declared live roots")
    return LiveSnapshot(tuple(roots), tuple((p, snapshot(p)) for p in files))


def check_live(before: LiveSnapshot) -> list[str]:
    """Return changed/unreadable declaration paths; never restore their contents."""
    changed = []
    for path, data in before.files:
        try:
            unchanged = any(contains(root, path.resolve()) for root in before.roots) and snapshot(path) == data
        except (OSError, ValueError, RuntimeError):
            unchanged = False
        if not unchanged:
            changed.append(str(path))
    return changed


def describe(data: bytes | None) -> dict:
    return {"exists": data is not None, "sha256": None if data is None else hashlib.sha256(data).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowed-root", action="append", required=True)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--live-root", action="append", required=True)
    parser.add_argument("--live-file", action="append", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    report = {"status": "refused", "command_returncode": None, "live_files": []}
    try:
        allowed = [absolute(p).resolve(strict=True) for p in args.allowed_root]
        live = [absolute(p).resolve(strict=True) for p in args.live_root]
        target = absolute(args.target_root).resolve(strict=True)
        if not all(p.is_dir() for p in allowed + live + [target]):
            raise ValueError("all roots must be existing directories")
        if any(contains(a, b) or contains(b, a) for a in allowed for b in live):
            raise ValueError("disposable and live roots overlap")
        if not any(contains(root, target) for root in allowed):
            raise ValueError("target escapes declared disposable roots")
        files = [absolute(p) for p in args.live_file]
        if any(not any(contains(root, p.resolve()) for root in live) for p in files):
            raise ValueError("live declaration escapes declared live roots")
        before = [snapshot(p) for p in files]
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            raise ValueError("command required after --")
        report.update(target_root=str(target), allowed_roots=list(map(str, allowed)), live_roots=list(map(str, live)))
        try:
            env = dict(os.environ, QUALIFICATION_TARGET_ROOT=str(target))
            # Keep stdout a single guard receipt; child output remains visible on stderr.
            result = subprocess.run(command, cwd=target, env=env, stdout=sys.stderr)
            report["command_returncode"] = result.returncode
        except (OSError, KeyboardInterrupt) as exc:
            report["command_error"] = str(exc) or type(exc).__name__
        drift = False
        for path, original in zip(files, before):
            item = {"path": str(path), "before": describe(original)}
            try:
                if not any(contains(root, path.resolve()) for root in live):
                    raise ValueError("live declaration now escapes live roots")
                current = snapshot(path)
                item.update(after=describe(current), unchanged=current == original)
            except (OSError, ValueError, RuntimeError) as exc:
                item.update(unchanged=False, error=str(exc))
            drift |= not item["unchanged"]
            report["live_files"].append(item)
        report["status"] = "drift" if drift else "passed" if report["command_returncode"] == 0 else "command-failed"
    except (OSError, ValueError, RuntimeError) as exc:
        report["error"] = str(exc)
    print(json.dumps(report, sort_keys=True))
    return {"passed": 0, "refused": 2, "drift": 3, "command-failed": 4}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
