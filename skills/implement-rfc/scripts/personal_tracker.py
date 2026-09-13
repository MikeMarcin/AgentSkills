#!/usr/bin/env python3
"""Explicit personal tracker setup and observational status for one source Git repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import personal_state
import personal_lanes
import project_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True,
                        help="actual source worktree root")
    parser.add_argument("--mode", choices=("project", "personal"),
                        help="explicit status override; init always selects personal")
    parser.add_argument("--workflow-root", type=Path,
                        help="existing tracker root for init or explicit status")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("command", choices=("init", "status"))
    args = parser.parse_args()
    try:
        if args.command == "init":
            if args.mode not in (None, "personal"):
                raise personal_state.PersonalStateError("init selects personal mode")
            source = personal_state.git_root(args.repo_root)
            personal_state.initialize(source, args.workflow_root)
            try:
                personal_lanes.bind_pair(source)
            except personal_lanes.PairOccupiedError:
                # Association remains useful for observation; mutation needs a separate lane.
                if args.workflow_root is None:
                    raise
            selected = project_config.resolve_context(repo_root=source, mode="personal")
        else:
            selected = project_config.resolve_context(repo_root=args.repo_root, mode=args.mode,
                                                      workflow_root=args.workflow_root)
    except (personal_state.PersonalStateError, project_config.ProjectConfigError, OSError) as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2
    result = {"ok": True, "mode": selected.mode,
              "source_root": str(selected.source_root),
              "source_common_dir": str(selected.source_common_dir),
              "workflow_root": str(selected.workflow_root),
              "workflow_common_dir": str(selected.workflow_common_dir),
              "runtime_root": str(selected.runtime_root) if selected.runtime_root else None,
              "project": selected.config["project"]}
    if args.json:
        print(json.dumps(result))
    else:
        print(f"{result['mode']} workflow: {result['source_root']} -> {result['workflow_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
