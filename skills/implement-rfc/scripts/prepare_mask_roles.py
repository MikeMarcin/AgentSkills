#!/usr/bin/env python3
"""MASK staged setup entrypoint: render the requested native roles into a stage.

MASK (RFC-MASK-0019) invokes this script only under explicit ``package.setup``
consent as ``python -B prepare_mask_roles.py --repo-root CONSUMER --output-root
STAGE --request-file REQUEST``. The request (``mask.setup-request.v1``) names the
action, the requested agent/role pairs, the consumer inputs with their observed
digests and declared parameters. This script writes exactly ``STAGE/AGENT/NAME.ext``
for each requested role using the renderer's shared generation path, and nothing
else: no consumer destination, no MASK state, no manifest. MASK validates the
stage, computes the portable lock and publishes through its own journal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_config  # noqa: E402
import render_runtime_adapters as renderer  # noqa: E402

REQUEST_SCHEMA = "mask.setup-request.v1"
ACTION = "prepare-roles"


class RequestError(ValueError):
    pass


def load_request(path: Path) -> dict:
    try:
        request = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RequestError(f"unreadable request: {exc}") from exc
    if not isinstance(request, dict) or request.get("schema") != REQUEST_SCHEMA:
        raise RequestError("unsupported request schema")
    if request.get("action") != ACTION:
        raise RequestError(f"unsupported action: {request.get('action')!r}")
    roles = request.get("native_roles")
    if not isinstance(roles, list) or not roles or any(
            not isinstance(row, dict) or row.get("agent") not in renderer.ROLE_SUFFIX
            or not isinstance(row.get("name"), str) or not renderer.ROLE_NAME_RE.fullmatch(row["name"]) for row in roles):
        raise RequestError("request needs supported agent/name role pairs")
    if not isinstance(request.get("inputs"), list) or not isinstance(request.get("parameters", {}), dict):
        raise RequestError("request inputs and parameters have the wrong shape")
    if request.get("parameters"):
        raise RequestError("this action declares no parameters")
    return request


def verify_inputs(root: Path, inputs: list) -> None:
    """The consumer files this render reads must be the exact bytes MASK observed."""
    for row in inputs:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RequestError("malformed request input")
        path = root / row["path"]
        expected = row.get("sha256")
        if expected is None:
            if path.exists():
                raise RequestError(f"input {row.get('id')} appeared after MASK observed it absent")
            continue
        if not path.is_file():
            raise RequestError(f"input {row.get('id')} is missing: {row['path']}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RequestError(f"input {row.get('id')} changed since MASK observed it")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--request-file", type=Path, required=True)
    args = parser.parse_args()
    request = load_request(args.request_file)
    root = args.repo_root.resolve()
    verify_inputs(root, request["inputs"])
    context = project_config.resolve_context(repo_root=root)
    generated, _ = renderer.generate_roles(context)
    stage = args.output_root
    if not stage.is_dir() or stage.is_symlink():
        raise RequestError(f"output root is not a directory: {stage}")
    written = []
    for row in request["native_roles"]:
        key = (row["agent"], row["name"])
        if key not in generated:
            raise RequestError(f"role {row['agent']}/{row['name']} is not defined by this package")
        directory = stage / row["agent"]
        directory.mkdir(exist_ok=True)
        target = directory / f"{row['name']}.{renderer.ROLE_SUFFIX[row['agent']]}"
        target.write_text(generated[key].replace("\r\n", "\n"), encoding="utf-8", newline="\n")
        written.append(f"{row['agent']}/{target.name}")
    print("staged " + ", ".join(written))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RequestError, ValueError, project_config.ProjectConfigError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
