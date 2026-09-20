#!/usr/bin/env python3
"""Startup preflight: is this consumer's implement-rfc native role set ready under MASK?

Runs the selected MASK program read-only (``capabilities --json`` and
``status --project ROOT --check --json``, or an advertised older interface) with argv arrays, never a shell, and
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_config  # noqa: E402

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


def preflight(root: Path, command: list[str], *, mode: str | None = None,
              workflow_root: Path | None = None, strategy: str | None = None,
              selection: dict | None = None) -> dict:
    result = dict(schema=SCHEMA, state="error", root=str(root), program=command, detail=None, roles=[], host_load="not_verified")
    import execution_strategy
    try:
        chosen = execution_strategy.resolve(strategy, preserved=selection)
        profile = chosen['requirement_profile']
        result['selection'] = chosen
        if not chosen['configuration_complete']:
            result.update(state='incomplete', detail='selected recipe requires exact routing: ' + ', '.join(chosen['missing_routes']))
            return result
    except (ValueError, OSError, TypeError) as exc:
        result.update(state='incomplete', detail=str(exc))
        return result
    try:
        context = project_config.resolve_context(repo_root=root, mode=mode, workflow_root=workflow_root)
    except project_config.ProjectConfigError as exc:
        result.update(state="incomplete", detail=f"source/tracker binding: {exc}")
        return result
    result.update(mode=context.mode, source_root=str(context.source_root),
                  workflow_root=str(context.workflow_root),
                  runtime_root=str(context.runtime_root) if context.runtime_root else None)
    if context.mode == "personal":
        import personal_lanes
        import personal_state
        try:
            binding = personal_state.read_binding(personal_state.home_for(context.source_root), context.source_root)
            if binding is None:
                result.update(state="incomplete", detail="source/tracker binding is missing; select personal mode explicitly")
                return result
            if personal_lanes._read(context.source_root) is not None:
                personal_lanes.validate_pair(context)
        except personal_state.PersonalStateError as exc:
            result.update(state="incomplete", detail=f"source/tracker lane: {exc}")
            return result
    code, caps, text = run(command, "capabilities")
    if caps is None or not caps.get("ok"):
        result["detail"] = f"MASK capabilities unavailable (exit {code}): {text}"
        return result
    workflow = (caps.get("data") or {}).get("workflow") or {}
    if workflow.get("readiness") != REQUIRED_READINESS or workflow.get("native_roles") is not True:
        result.update(state="unsupported", detail="the selected MASK program does not implement workflow_readiness_v1 typed native roles; "
                      "its link-only success is not workflow readiness")
        return result
    if profile is not None and workflow.get('requirement_profiles') != 'workflow_requirement_profiles_v1':
        result.update(state='unsupported', detail='selected MASK does not support explicit requirement profiles; core failures cannot be filtered away')
        return result
    selected = ("--user",) if context.mode == "personal" else ("--project", str(root))
    profile_args = ('--workflow-profile', f'{SKILL}={profile}') if profile is not None else ()
    commands = {entry.get("name") for entry in (caps.get("data") or {}).get("commands", [])}
    inspection = "status" if "status" in commands else "ensure"
    code, ensure, text = run(command, inspection, *selected, "--check", *profile_args)
    if ensure is None:
        result["detail"] = f"MASK {inspection} --check returned no JSON result (exit {code}): {text}"
        return result
    data = ensure.get("data") or {}
    entries = data.get("workflow_readiness") or []
    selected_entry = next((entry for entry in entries if entry.get("scope") == "user"), None) if context.mode == "personal" else next(
        (entry for entry in entries if Path(entry.get("root", "")).resolve() == root), None)
    selected_root = Path(selected_entry["root"]).resolve() if selected_entry is not None else None
    scope = next((row for row in data.get("scope_readiness") or []
                  if selected_root is not None and Path(row.get("root", "")).resolve() == selected_root), None)
    report = next((skill for entry in entries if entry is selected_entry
                   for skill in entry.get("skills") or [] if skill.get("skill") == SKILL), None)
    if report is not None:
        result["roles"] = [dict(agent=row["agent"], name=row["name"], state=row["state"], route=row.get("route") or {})
                           for row in report.get("roles") or []]
        result["host_load"] = next((row.get("host_load") for row in report.get("roles") or [] if row.get("host_load")), "not_verified")
    error = ensure.get("error") or {}
    if profile is not None and report is not None and report.get('selected_profile') != profile:
        result.update(state='unsupported', detail='MASK did not examine the selected requirement profile')
        return result
    if scope is None or report is None or report.get("workflow") != "declared":
        if error:
            # The program supports the contract but could not examine this consumer (unregistered, unapproved, drifted...).
            result.update(state="incomplete", detail=f"{error.get('code')}: {error.get('message')}")
            return result
        result.update(state="unsupported", detail="MASK returned success without examining a declared implement-rfc workflow "
                      f"for this consumer (scope workflow: {scope.get('workflow') if scope else 'absent'}); "
                      "link-only success is not workflow readiness")
        return result
    if ensure.get("ok") and scope.get("workflow") == "complete" and report.get("complete") and data.get("readiness") in ("ready_pinned", "ready_legacy_unpinned", "ready_dev_link"):
        result['deployment_readiness'] = data['readiness']
        result.update(state="ready", detail="selected declared requirements and inputs match the scope and source/tracker binding; host loading is not verified by this check")
        return result
    rows = (error.get("details") or {}).get("workflow") or []
    result.update(state="incomplete", detail=error.get("message") or f"workflow {scope.get('workflow')}; readiness {data.get('readiness')}",
                  blockers=rows)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Absolute consumer root")
    parser.add_argument("--mode", choices=("project", "personal"), help="Explicit storage selection; absent uses the remembered binding")
    parser.add_argument("--workflow-root", type=Path, help="Explicit external tracker worktree for personal mode")
    parser.add_argument('--strategy', help='Explicit registered strategy/preset; separate from storage --mode')
    parser.add_argument('--selection', type=Path, help='Preserved resolved strategy snapshot')
    parser.add_argument("--mask", help="MASK launcher on PATH or an absolute mask.py; default MASK_PROGRAM or 'mask'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    command = program_command(args.mask)
    if command is None:
        result = dict(schema=SCHEMA, state="error", root=str(root), program=None, detail="no MASK program found; pass --mask or set MASK_PROGRAM", roles=[])
    else:
        import execution_strategy
        try:
            selection = execution_strategy.read_json(args.selection) if args.selection else None
            result = preflight(root, command, mode=args.mode, workflow_root=args.workflow_root,
                               strategy=args.strategy, selection=selection)
        except (ValueError, OSError) as exc:
            result = dict(state='error', detail=str(exc), roles=[])
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"workflow preflight: {result['state']} - {result['detail']}")
        for row in result["roles"]:
            print(f"  {row['agent']}/{row['name']}: {row['state']}")
    return EXIT[result["state"]]


if __name__ == "__main__":
    raise SystemExit(main())
