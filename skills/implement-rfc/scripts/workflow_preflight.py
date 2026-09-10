#!/usr/bin/env python3
"""Startup preflight: is this consumer's implement-rfc native role set ready under MASK?

Runs the selected MASK program read-only (``capabilities --json`` and
``ensure --project ROOT --check --json``) with argv arrays, never a shell, and
reports one of ``ready``, ``incomplete``, ``unsupported`` or ``error``.
A program that does not advertise ``workflow_readiness_v1`` and typed native
roles is ``unsupported``: an older MASK may ignore ``mask-workflow.json`` and
return a successful link-only result, which is never accepted as readiness.
Filesystem readiness is not host loading; ``host_load`` is reported as given.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SCHEMA = "implement-rfc.workflow-preflight.v1"
SKILL = "implement-rfc"
REQUIRED_READINESS = "workflow_readiness_v1"
EXIT = {"ready": 0, "incomplete": 1, "unsupported": 1, "error": 2}


def program_command(selected: str | None) -> list[str] | None:
    if selected:
        path = Path(selected)
        if path.suffix == ".py":
            return [sys.executable, "-B", str(path)]
        found = shutil.which(selected)
        return [found] if found else None
    env = os.environ.get("MASK_PROGRAM")
    if env:
        return program_command(env)
    found = shutil.which("mask")
    return [found] if found else None


def run(command: list[str], *args: str, cwd: Path | None = None) -> tuple[int, dict | None, str]:
    try:
        completed = subprocess.run([*command, *args, "--json"], capture_output=True, text=True, cwd=cwd, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, None, str(exc)
    try:
        return completed.returncode, json.loads(completed.stdout), completed.stderr.strip()
    except json.JSONDecodeError:
        return completed.returncode, None, (completed.stderr or completed.stdout).strip()[:2000]


def preflight(root: Path, command: list[str]) -> dict:
    result = dict(schema=SCHEMA, state="error", root=str(root), program=command, detail=None, roles=[], host_load="not_verified")
    code, caps, text = run(command, "capabilities")
    if caps is None or not caps.get("ok"):
        result["detail"] = f"MASK capabilities unavailable (exit {code}): {text}"
        return result
    workflow = (caps.get("data") or {}).get("workflow") or {}
    if workflow.get("readiness") != REQUIRED_READINESS or workflow.get("native_roles") is not True:
        result.update(state="unsupported", detail="the selected MASK program does not implement workflow_readiness_v1 typed native roles; "
                      "its link-only success is not workflow readiness")
        return result
    code, ensure, text = run(command, "ensure", "--project", str(root), "--check")
    if ensure is None:
        result["detail"] = f"MASK ensure --check returned no JSON result (exit {code}): {text}"
        return result
    data = ensure.get("data") or {}
    scope = next((row for row in data.get("scope_readiness") or [] if Path(row.get("root", "")).resolve() == root), None)
    report = next((skill for entry in data.get("workflow_readiness") or [] if Path(entry.get("root", "")).resolve() == root
                   for skill in entry.get("skills") or [] if skill.get("skill") == SKILL), None)
    if report is not None:
        result["roles"] = [dict(agent=row["agent"], name=row["name"], state=row["state"], route=row.get("route") or {})
                           for row in report.get("roles") or []]
        result["host_load"] = next((row.get("host_load") for row in report.get("roles") or [] if row.get("host_load")), "not_verified")
    error = ensure.get("error") or {}
    if scope is None or report is None or report.get("workflow") != "declared":
        result.update(state="unsupported", detail="MASK did not examine a declared implement-rfc workflow for this consumer "
                      f"(scope workflow: {scope.get('workflow') if scope else 'absent'}; error: {error.get('code') or 'none'})")
        return result
    if ensure.get("ok") and scope.get("workflow") == "complete" and report.get("complete") and data.get("readiness") in ("ready_pinned", "ready_legacy_unpinned"):
        result.update(state="ready", detail="declared native roles and inputs match; host loading is not verified by this check")
        return result
    rows = (error.get("details") or {}).get("workflow") or []
    result.update(state="incomplete", detail=error.get("message") or f"workflow {scope.get('workflow')}; readiness {data.get('readiness')}",
                  blockers=rows)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Absolute consumer root")
    parser.add_argument("--mask", help="MASK launcher on PATH or an absolute mask.py; default MASK_PROGRAM or 'mask'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    command = program_command(args.mask)
    if command is None:
        result = dict(schema=SCHEMA, state="error", root=str(root), program=None, detail="no MASK program found; pass --mask or set MASK_PROGRAM", roles=[])
    else:
        result = preflight(root, command)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"workflow preflight: {result['state']} - {result['detail']}")
        for row in result["roles"]:
            print(f"  {row['agent']}/{row['name']}: {row['state']}")
    return EXIT[result["state"]]


if __name__ == "__main__":
    raise SystemExit(main())
