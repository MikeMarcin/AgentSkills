#!/usr/bin/env python3
"""Install the version-free `launch_remote_station` command into a bin directory.

Writes `launch_remote_station` (POSIX shell) and `launch_remote_station.cmd`
(Windows) from this skill's assets. Nothing is elevated and PATH is not edited;
add the directory to PATH yourself. The forwarders run the current checkout's
own `.agents/skills/remote-station` link, so reinstalling from a newer skill
version never changes station behavior. Rerunning is idempotent. A file that is
not a forwarder written by this script is refused, never overwritten.

usage: install_command.py --bin-dir DIR [--dry-run] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "command"
MARKER = "launch_remote_station: version-free forwarder installed by the remote-station skill."
SCHEMA = "remote-station.install-command.v1"
# The POSIX forwarder needs LF; cmd.exe parses labels reliably only with CRLF.
FILES = (("launch_remote_station", "\n"), ("launch_remote_station.cmd", "\r\n"))


class InstallRefusal(Exception):
    """A named reason the command was not installed."""


def forwarder_bytes(name: str, newline: str) -> bytes:
    text = (ASSETS / name).read_text(encoding="utf-8")
    return newline.join(text.splitlines()).encode("utf-8") + newline.encode("utf-8")


def plan(bin_dir: Path) -> list[dict]:
    if bin_dir.exists() and not bin_dir.is_dir():
        raise InstallRefusal(f"--bin-dir is not a directory: {bin_dir}")
    actions = []
    for name, newline in FILES:
        path = bin_dir / name
        content = forwarder_bytes(name, newline)
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise InstallRefusal(f"refusing to replace a link or non-file: {path}")
        if not path.exists():
            action = "create"
        else:
            existing = path.read_bytes()
            if existing == content:
                action = "unchanged"
            elif MARKER.encode("utf-8") in existing:
                action = "update"
            else:
                raise InstallRefusal(
                    f"refusing to overwrite {path}: it is not a launch_remote_station "
                    "forwarder written by this skill; move it aside and retry")
        actions.append(dict(path=str(path), action=action, content=content))
    return actions


def write(path: Path, content: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        mode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install(bin_dir: Path, *, dry_run: bool = False) -> dict:
    bin_dir = Path(bin_dir).expanduser().absolute()
    actions = plan(bin_dir)
    changed = any(row["action"] != "unchanged" for row in actions)
    if changed and not dry_run:
        bin_dir.mkdir(parents=True, exist_ok=True)
        for row in actions:
            if row["action"] != "unchanged":
                write(Path(row["path"]), row["content"])
    on_path = any(Path(entry).expanduser().absolute() == bin_dir
                  for entry in os.environ.get("PATH", "").split(os.pathsep) if entry)
    return dict(schema=SCHEMA, bin_dir=str(bin_dir), dry_run=dry_run, changed=changed and not dry_run,
                files=[dict(path=row["path"], action=row["action"]) for row in actions],
                on_path=on_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bin-dir", required=True, type=Path, help="directory to write both forwarders into")
    parser.add_argument("--dry-run", action="store_true", help="report the actions without writing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = install(args.bin_dir, dry_run=args.dry_run)
    except (InstallRefusal, OSError) as error:
        if args.json:
            print(json.dumps(dict(schema=SCHEMA, ok=False, error=str(error))))
        else:
            print(f"install refused: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(dict(result, ok=True)))
        return 0
    for row in result["files"]:
        verb = row["action"] if not args.dry_run or row["action"] == "unchanged" else f"would {row['action']}"
        print(f"{verb}: {row['path']}")
    if not result["on_path"]:
        print(f"{result['bin_dir']} is not on PATH; add it to run launch_remote_station from any checkout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
