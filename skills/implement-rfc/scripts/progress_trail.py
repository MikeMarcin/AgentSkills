"""Read-only digest of a consumer's slice trail: board transitions, commits, in-flight paths.

The trail already exists in the consumer (claim/finish commits, scoped commits and the
owned dirty working set). This helper forwards it as compact lines and keeps no state
file. One-shot mode carries its cursor in ``--since``; follow mode holds it in memory
and coalesces events so a host that wakes an agent per emitted line pays at most one
wake per ``--min-gap`` seconds.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_config

REFUSED = 2
CARD_ID = re.compile(r"[A-Z]{2,8}-\d{4}(?![\dA-Za-z])")
LANE_ACTIONS = {"in_progress": "claim", "done": "finish", "parked": "park", "blocked": "block"}


class TrailError(Exception):
    pass


def git(root: Path, *args: str) -> str:
    """Read-only Git query; never takes optional locks, so a writer is never blocked."""
    env = dict(project_config.git_environment(), GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, timeout=60)
    if result.returncode != 0:
        raise TrailError(f"git {' '.join(args[:2])} failed: {result.stderr.strip() or result.returncode}")
    return result.stdout


@dataclass(frozen=True)
class Event:
    kind: str  # transition | pending | commit | in-flight
    time: float
    text: str
    data: dict = field(default_factory=dict, compare=False)

    def line(self, as_json: bool) -> str:
        if as_json:
            return json.dumps({"kind": self.kind, "time": round(self.time), **self.data}, sort_keys=True)
        return f"{datetime.fromtimestamp(self.time).strftime('%H:%M')} {self.text}"


class Trail:
    """One consumer's trail, resolved through the project config contract with an explicit root."""

    def __init__(self, repo_root: str):
        if not str(repo_root).strip():
            raise TrailError("explicit --repo-root required; a shared skill link never selects its consumer")
        try:
            context = project_config.resolve_context(repo_root=repo_root)
        except project_config.ProjectConfigError as exc:
            raise TrailError(str(exc)) from exc
        self.root, self.config = context.workflow_root, context.config
        self.source_root = context.source_root
        self.issue_root = PurePosixPath(self.config["issue_root"])
        self.lane_keys = {lane: key for key, lane in self.config["lanes"].items()}
        try:
            self.head()
        except TrailError as exc:
            raise TrailError(f"consumer has no readable HEAD: {exc}") from exc

    def head(self) -> str:
        return git(self.root, "rev-parse", "--verify", "HEAD^{commit}").strip()

    def check_cursor(self, since: str) -> str:
        try:
            sha = git(self.root, "rev-parse", "--verify", f"{since}^{{commit}}").strip()
            git(self.root, "merge-base", "--is-ancestor", sha, "HEAD")
        except TrailError as exc:
            raise TrailError(f"--since must name an ancestor commit of HEAD: {since}") from exc
        return sha

    def lane_of(self, path: str) -> tuple[str, str] | None:
        """(lane, card id) when ``path`` is a card inside a configured lane."""
        pure = PurePosixPath(path)
        if self.issue_root not in pure.parents or pure.suffix != ".md":
            return None
        relative = pure.relative_to(self.issue_root)
        if len(relative.parts) != 2 or relative.parts[0] not in self.lane_keys:
            return None
        match = CARD_ID.match(relative.stem)
        return (relative.parts[0], match.group(0)) if match else None

    def action(self, to_lane: str) -> str:
        return LANE_ACTIONS.get(self.lane_keys[to_lane], "move")

    def commits(self, since: str) -> list[Event]:
        events = []
        log = git(self.root, "log", "--reverse", "--format=%H%x1f%ct%x1f%s", f"{since}..HEAD")
        for row in filter(None, log.splitlines()):
            sha, stamp, subject = row.split("\x1f", 2)
            when = int(stamp)
            # A finish rewrites the card enough that Git reports delete plus add, so pair
            # lanes by card ID rather than trusting rename detection.
            gone, arrived = {}, {}
            status = git(self.root, "show", "--name-status", "--no-renames", "--format=", sha)
            for entry in filter(None, status.splitlines()):
                code, path = entry.split("\t", 1)
                card = self.lane_of(path)
                if card and code[0] == "D":
                    gone[card[1]] = card[0]
                elif card and code[0] == "A":
                    arrived[card[1]] = card[0]
            moves = sorted((card, gone[card], lane) for card, lane in arrived.items() if card in gone and gone[card] != lane)
            for card, old_lane, new_lane in moves:
                action = self.action(new_lane)
                events.append(Event("transition", when, f"{action} {card} ({old_lane} > {new_lane}) {sha[:7]}",
                                    {"action": action, "card": card, "from": old_lane, "to": new_lane, "commit": sha}))
            if not moves:
                events.append(Event("commit", when, f"commit {sha[:7]} {subject}", {"commit": sha, "subject": subject}))
        return events

    def working_set(self) -> tuple[dict[str, str], set[str]]:
        """Uncommitted card lane moves (card -> lane) and the non-board dirty path set."""
        pending, paths = {}, set()
        raw = git(self.root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
        for entry in filter(None, raw.split("\0")):
            path = entry[3:]
            card = self.lane_of(path)
            if card is None:
                paths.add(path)
            elif entry[:2] != " D" and entry[:2] != "D ":
                pending[card[1]] = card[0]
        if self.source_root != self.root:
            raw = git(self.source_root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
            paths = {entry[3:] for entry in raw.split("\0") if entry}
        return pending, paths

    def committed_lanes(self) -> dict[str, str]:
        lanes = {}
        for path in filter(None, git(self.root, "ls-tree", "-r", "--name-only", "HEAD", "--", str(self.issue_root)).splitlines()):
            card = self.lane_of(path)
            if card:
                lanes[card[1]] = card[0]
        return lanes

    def pending_moves(self, now: float) -> list[Event]:
        pending, _ = self.working_set()
        committed = self.committed_lanes()
        events = []
        for card, lane in sorted(pending.items()):
            before = committed.get(card)
            if before is not None and before != lane:
                action = self.action(lane)
                events.append(Event("pending", now, f"pending {action} {card} ({before} > {lane})",
                                    {"action": action, "card": card, "from": before, "to": lane}))
        return events

    def in_flight(self, now: float, previous: set[str] | None = None) -> Event | None:
        _, paths = self.working_set()
        if previous is not None and paths == previous:
            return None
        added = len(paths - previous) if previous is not None else len(paths)
        removed = len(previous - paths) if previous is not None else 0
        return Event("in-flight", now, f"in-flight {len(paths)} paths (+{added} -{removed})",
                     {"count": len(paths), "added": added, "removed": removed, "paths": sorted(paths)})


class Follower:
    """Coalescing cursor held in memory; ``poll(now)`` returns the lines to emit this tick."""

    def __init__(self, trail: Trail, *, min_gap: float, quiet_after: float, as_json: bool, start: float):
        self.trail, self.min_gap, self.quiet_after, self.as_json = trail, min_gap, quiet_after, as_json
        self.cursor = trail.head()
        self.pending_seen: set[tuple] = set()
        self.paths: set[str] = trail.working_set()[1]
        self.buffer: list[Event] = []
        self.last_flush = start

    def observe(self, now: float) -> None:
        head = self.trail.head()
        if head != self.cursor:
            self.buffer.extend(self.trail.commits(self.cursor))
            self.cursor = head
            self.pending_seen = set()
        for event in self.trail.pending_moves(now):
            key = (event.data["card"], event.data["to"])
            if key not in self.pending_seen:
                self.pending_seen.add(key)
                self.buffer.append(event)

    def poll(self, now: float) -> list[str]:
        self.observe(now)
        if self.buffer and now - self.last_flush >= self.min_gap:
            flight = self.trail.in_flight(now, self.paths)
            lines = [e.line(self.as_json) for e in self.buffer]
            if flight is not None:
                self.paths = set(flight.data["paths"])
                lines.append(flight.line(self.as_json))
            self.buffer, self.last_flush = [], now
            return lines
        if self.quiet_after and not self.buffer and now - self.last_flush >= self.quiet_after:
            flight = self.trail.in_flight(now, self.paths)
            self.last_flush = now
            if flight is not None:
                self.paths = set(flight.data["paths"])
                return [flight.line(self.as_json)]
        return []


def one_shot(trail: Trail, since: str | None, as_json: bool) -> list[str]:
    now = time.time()
    events = trail.commits(trail.check_cursor(since)) if since else []
    events += trail.pending_moves(now)
    events.append(trail.in_flight(now))
    lines = [e.line(as_json) for e in events]
    head = trail.head()
    lines.append(json.dumps({"kind": "cursor", "commit": head}) if as_json else f"cursor {head}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", required=True, help="explicit consumer worktree root")
    parser.add_argument("--since", help="one-shot cursor: emit trail since this ancestor commit")
    parser.add_argument("--follow", action="store_true", help="hold the cursor in memory and stream digests")
    parser.add_argument("--interval", type=float, default=30.0, help="follow poll interval in seconds")
    parser.add_argument("--min-gap", type=float, default=900.0, help="follow: least seconds between emitted digests")
    parser.add_argument("--quiet-after", type=float, default=0.0, help="follow: heartbeat after this many quiet seconds; 0 disables")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.follow and args.since:
        parser.error("--since is the one-shot cursor; --follow holds its own")
    if min(args.interval, args.min_gap, args.quiet_after) < 0 or args.interval == 0:
        parser.error("interval must be positive; gaps must not be negative")
    try:
        trail = Trail(args.repo_root)
        if not args.follow:
            for line in one_shot(trail, args.since, args.json):
                print(line)
            return 0
        follower = Follower(trail, min_gap=args.min_gap, quiet_after=args.quiet_after, as_json=args.json, start=time.time())
        while True:
            time.sleep(args.interval)
            for line in follower.poll(time.time()):
                print(line, flush=True)
    except TrailError as exc:
        print(f"progress_trail: refused: {exc}", file=sys.stderr)
        return REFUSED
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
