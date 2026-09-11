#!/usr/bin/env python3
"""Render Claude Code and Codex custom agents from the portable role/routing data.

Generate optional role adapters in a selected consumer. This does not install
or upgrade skills. Portable source manifests are a separate authoring operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import stat
import tempfile

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_config  # noqa: E402
import slice_events  # noqa: E402

ROLE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODEL_CLASSES = {"mechanical", "balanced", "standard", "deep", "review", "critical", "integration"}
MUTATIONS = {"read-only", "build-write", "workspace-write"}
PLACEHOLDER_RE = re.compile(r"^<[^>]+>$|\$\{")
ROLES_SCHEMA = "implement-rfc.roles.v2"
ROUTING_SCHEMA = "implement-rfc.routing.v2"
ADAPTERS_SCHEMA = "implement-rfc.runtime-adapters.v1"
PORTABLE_MANIFEST_SCHEMA = "implement-rfc.portable-manifest.v1"
SKILL_NAME = "implement-rfc"
ATTENDED_PLACEHOLDER = "{attended_review_skill}"
ATTENDED_FALLBACK_INSTRUCTION = (
    "When the slice's remaining evidence is an attended human verdict, never stop on it, "
    "fabricate it, or placeholder it: record the pending checkpoint and its exact ask in "
    "your report, and complete the slice's remaining unattended work."
)
# Paths inside the skill directory that are project-specific or generated, and
# therefore outside the portable set.
NON_PORTABLE = {
    Path("config/project.json"),
    Path("references/project.md"),
}
NON_PORTABLE_DIRS = ("generated", "__pycache__")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            merged[key] = deep_merge(merged[key], value) if key in merged else value
        return merged
    return override


LEAF_ROLES = {"rfc-utility", "rfc-scout", "rfc-test-runner", "rfc-worker",
              "rfc-worker-deep", "rfc-reviewer", "rfc-reviewer-critical"}
INTEGRATOR = "rfc-integrator"
# Resume, collect from and release delegated children. A delegating role cannot
# reuse the same slice owner for correction without these.
COORDINATION_TOOLS = ("SendMessage", "TaskOutput", "TaskStop")


def validate_roles(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    legacy = data.get("schema") == "implement-rfc.roles.v1"
    if data.get("schema") not in (ROLES_SCHEMA, "implement-rfc.roles.v1"):
        raise ValueError("roles.json has an unsupported schema")
    if set(data) != {"schema", "roles"}:
        raise ValueError("unknown roles fields")
    roles = data.get("roles")
    if not isinstance(roles, dict) or not roles:
        raise ValueError("roles.json must contain a non-empty roles object")
    known = LEAF_ROLES | (set(RETIRED_ROLES) if legacy else {INTEGRATOR})
    if set(roles) - known:
        raise ValueError("unknown role selector")
    normalized = {}
    for name, original in roles.items():
        if not isinstance(original, dict):
            raise ValueError(f"role {name} must be an object")
        role = dict(original)
        allowed = {"description", "mutation", "max_turns", "instructions"}
        allowed |= {"may_spawn_utility"} if legacy else {"delegation", "entrypoint"}
        if set(role) - allowed:
            raise ValueError(f"unknown fields for role {name}")
        if legacy:
            if role.pop("may_spawn_utility", False) is not False:
                raise ValueError("v1 delegation requires explicit migration; only leaves are readable")
            role["delegation"] = {"allowed_roles": []}
        delegation = role.get("delegation")
        if not isinstance(delegation, dict) or set(delegation) != {"allowed_roles"}:
            raise ValueError(f"role {name} needs typed delegation")
        children = delegation["allowed_roles"]
        if (not isinstance(children, list) or not all(isinstance(child, str) for child in children)
                or len(set(children)) != len(children) or set(children) - LEAF_ROLES
                or (name != INTEGRATOR and children)):
            raise ValueError(f"invalid child-role allowlist for {name}")
        entrypoint = role.get("entrypoint")
        if entrypoint is not None and (not isinstance(entrypoint, str)
                or not re.fullmatch(r"references/[a-z0-9][a-z0-9/-]*\.md", entrypoint)
                or "//" in entrypoint):
            raise ValueError(f"invalid role entrypoint for {name}")
        if not isinstance(role.get("description"), str) or not role["description"].strip():
            raise ValueError(f"role {name} needs a description")
        if role.get("mutation") not in MUTATIONS:
            raise ValueError(f"role {name} has invalid mutation")
        if name != INTEGRATOR or "max_turns" in role:
            if type(role.get("max_turns")) is not int or role["max_turns"] < 1:
                raise ValueError(f"role {name} has invalid max_turns")
        instructions = role.get("instructions")
        if not isinstance(instructions, list) or not instructions or not all(
            isinstance(item, str) and item.strip() for item in instructions
        ):
            raise ValueError(f"role {name} needs non-empty instruction strings")
        normalized[name] = role
    return normalized


def validate_route(route, label):
    if (not isinstance(route, dict) or set(route) != {"model", "effort"}
            or not isinstance(route["model"], str) or not route["model"].strip()
            or PLACEHOLDER_RE.search(route["model"])
            or (route["effort"] is not None and (not isinstance(route["effort"], str)
                                                or not route["effort"].strip()))):
        raise ValueError(f"{label} requires exact model and effort without placeholders")


def validate_capability(provider, route, capabilities):
    validate_route(route, "override")
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get(provider, {}), dict):
        raise ValueError("unsupported or unverified runtime capability")
    supported = capabilities.get(provider, {}).get(route["model"], [])
    if not isinstance(supported, list):
        raise ValueError("invalid runtime capability efforts")
    if route["effort"] not in supported:
        raise ValueError(f"unsupported or unverified runtime capability: {provider}/{route['model']}/{route['effort']}")


def validate_routing(data, roles):
    legacy = data.get("schema") == "implement-rfc.routing.v1"
    if data.get("schema") not in (ROUTING_SCHEMA, "implement-rfc.routing.v1"):
        raise ValueError("routing.json has an unsupported schema")
    allowed = {"schema", "verified_as_of", "assignments", "providers"}
    if not legacy:
        allowed.add("session_routes")
    if set(data) - allowed:
        raise ValueError("unknown routing fields")
    assignments, providers = data.get("assignments"), data.get("providers")
    if not isinstance(assignments, dict):
        raise ValueError("routing assignments must be an object")
    if set(assignments) & set(RETIRED_ROLES) and not set(roles) & set(RETIRED_ROLES):
        raise ValueError("retired role selector in routing assignments; explicitly migrate to current roles")
    if set(assignments) != set(roles):
        raise ValueError(f"routing role mismatch; missing={sorted(set(roles) - set(assignments))}, extra={sorted(set(assignments) - set(roles))}")
    classes_allowed = MODEL_CLASSES - {"integration"} if legacy else MODEL_CLASSES
    for name, model_class in assignments.items():
        if not isinstance(model_class, str) or model_class not in classes_allowed:
            raise ValueError(f"routing assigns invalid class {model_class} to {name}")
        if (name == INTEGRATOR) != (model_class == "integration"):
            raise ValueError("integrator requires its independent integration class")
    if not isinstance(providers, dict) or set(providers) != {"codex", "claude"}:
        raise ValueError("routing providers must contain codex and claude only")
    for provider, definition in providers.items():
        if not isinstance(definition, dict) or set(definition) - {"classes", "minimum_cli_version"}:
            raise ValueError("invalid provider definition")
        classes = definition.get("classes")
        if not isinstance(classes, dict) or set(classes) - classes_allowed:
            raise ValueError(f"{provider} has unknown route classes")
        for model_class in set(assignments.values()) | set(classes):
            validate_route(classes.get(model_class), f"{provider} route {model_class}")
    if not legacy:
        sessions = data.get("session_routes")
        if not isinstance(sessions, dict) or set(sessions) != {"rfc-coordinator"}:
            raise ValueError("routing requires the session-only rfc-coordinator route")
        coordinator = sessions["rfc-coordinator"]
        if not isinstance(coordinator, dict) or set(coordinator) != set(providers):
            raise ValueError("coordinator session route requires both providers")
        for provider, route in coordinator.items():
            validate_route(route, f"{provider} coordinator")
    return assignments, providers["codex"]["classes"], providers["claude"]["classes"]


def select_routes(routing, roles, profiles, profile="baseline", capabilities=None,
                  order_routes=None, explicit_routes=None, preserved_integrator_routes=None):
    """Resolve per-role requests; rendering never selects the primary session."""
    assignments, codex, claude = validate_routing(routing, roles)
    if profiles.get("schema") != "implement-rfc.routing-profiles.v1":
        raise ValueError("unsupported routing profiles schema")
    selected = profiles.get("profiles", {}).get(profile)
    if not isinstance(selected, dict):
        raise ValueError("unknown routing profile")
    routes = {p: {name: dict(classes[assignments[name]]) for name in roles}
              for p, classes in (("codex", codex), ("claude", claude))}
    origins = {p: {name: "integration_default" if name == INTEGRATOR else "baseline"
                   for name in roles} for p in routes}
    preserved = preserved_integrator_routes or {}
    if not isinstance(preserved, dict) or set(preserved) - set(routes):
        raise ValueError("invalid preserved integrator providers")
    preserved_overlay = {provider: {INTEGRATOR: route} for provider, route in preserved.items()}
    for origin, overlay in (("profile", selected.get("overrides", {})),
                            ("admitted_order", order_routes or {}),
                            ("preserved_owner", preserved_overlay),
                            ("explicit_user", explicit_routes or {})):
        if not isinstance(overlay, dict) or set(overlay) - set(routes):
            raise ValueError("invalid route override providers")
        for provider, changes in overlay.items():
            if isinstance(changes, dict) and set(changes) & set(RETIRED_ROLES):
                raise ValueError("retired role selector; explicitly reissue using rfc-worker or rfc-reviewer-critical; preserve old assignment evidence")
            if not isinstance(changes, dict) or set(changes) - set(roles):
                raise ValueError("invalid route override roles")
            for name, route in changes.items():
                validate_capability(provider, route, capabilities)
                routes[provider][name] = dict(route)
                origins[provider][name] = origin
    encoded = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    return routes, {"profile": profile, "profile_digest": hashlib.sha256(encoded).hexdigest(),
                    "experiment": selected.get("experiment"), "requested": routes,
                    "origins": origins, "rendered": routes, "observed": None,
                    "session_selection": {
                        "requested": routing.get("session_routes", {}), "observed": None,
                        "applied": False,
                        "instructions": "Bind the integrator model and effort before selecting the coordinator in the native interactive session. Preserve an explicit owner session choice and report requested versus effective settings. This manifest does not select a session or change global defaults."},
                    "enforcement": {
                        "codex": "role agents.enabled; integrator child allowlist is policy",
                        "claude": "leaf Agent tool omitted; delegated integrator child allowlist is policy",
                        "observed": None}}


FALLBACK_REASONS = {"synthetic_error", "unknown_effort", "unsupported_effort",
                    "server_unavailability", "model_quota", "shared_quota",
                    "authentication_permissions", "request_size", "task_difficulty"}


def fallback_receipt(requested, reason, *, observed=None, alternative=None,
                     approval=None, attempt=0):
    """Record an explicit decision; never launch, purchase, or redeem capacity."""
    if reason not in FALLBACK_REASONS:
        raise ValueError("unknown fallback reason")
    if alternative is not None:
        if (not isinstance(approval, dict) or approval.get("alternative") != alternative
                or not approval.get("scope") or not approval.get("risk_floor")
                or not approval.get("permission_billing_boundary")
                or type(approval.get("max_attempts")) is not int
                or not 1 <= approval["max_attempts"] <= 3
                or type(attempt) is not int or not 1 <= attempt <= approval["max_attempts"]):
            raise ValueError("fallback needs exact bounded approval")
    return {"schema": "implement-rfc.route-receipt.v1", "requested": requested,
            "reason": reason, "observed": observed, "alternative": alternative,
            "approval": approval, "attempt": attempt,
            "synthetic": reason == "synthetic_error"}


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def effort_label(route: dict[str, Any]) -> str:
    return route["effort"] if route.get("effort") is not None else "none (unsupported)"


def startup_banner(name: str, route: dict[str, Any]) -> str:
    return f"Role: {name} | Model: {route['model']} | Effort: {effort_label(route)}"


def project_instructions(role: dict[str, Any], project: dict[str, Any]) -> list[str]:
    """The role's portable instructions with project facts substituted."""
    attended = project["attended_review_skill"]
    rendered: list[str] = []
    for line in role["instructions"]:
        if ATTENDED_PLACEHOLDER in line:
            if attended is None:
                rendered.append(ATTENDED_FALLBACK_INSTRUCTION)
            else:
                rendered.append(line.replace(ATTENDED_PLACEHOLDER, attended))
        else:
            rendered.append(line)
    return rendered


def rendered_role_instructions(
    name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any],
    *, provider: str = "codex",
) -> list[str]:
    banner = startup_banner(name, route)
    addenda_roles = {
        "rfc-worker": ("rfc-worker", "rfc-worker-routine"),
        "rfc-worker-deep": ("rfc-worker", "rfc-worker-deep"),
        "rfc-reviewer-critical": ("rfc-critical-reviewer", "rfc-reviewer-critical"),
    }.get(name, (name,))
    addenda = [line for role_name in addenda_roles for line in project["role_addenda"].get(role_name, [])]
    addenda = list(dict.fromkeys(addenda))
    if name == "rfc-worker" and project["role_addenda"].get("rfc-worker-routine"):
        addenda.append("Legacy routine restrictions are retained; flag stricter local constraints for owner review without erasing them.")
    instructions = [
        "Before any analysis or tool call, emit exactly this startup line: "
        f"`{banner}`. If the runtime exposes an effective model or effort that differs "
        "from this configured route, replace only the differing banner value with the "
        "effective value. Repeat the effective banner as the first line of the Status "
        "section in your final report; some runtimes return only the final report to "
        "the launching agent, so the repetition is what the launcher verifies.",
        *project_instructions(role, project),
        *addenda,
    ]
    if role.get("entrypoint"):
        discovery = ".claude" if provider == "claude" else ".agents"
        instructions.append(f"Read the assigned integrator entrypoint {discovery}/skills/implement-rfc/{role['entrypoint']} before engineering; do not restart the outer coordinator loop.")
    children = role.get("delegation", {}).get("allowed_roles", [])
    if children:
        instructions.append("Delegate only to these leaf roles: " + ", ".join(children) +
                            ". Never spawn peer integrators or coordinators. The child allowlist is policy in delegated contexts; runtime-loaded enforcement remains unverified.")
    return instructions


def role_prompt(name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any],
                *, provider: str = "codex") -> str:
    return "\n\n".join(rendered_role_instructions(name, role, route, project, provider=provider)) + "\n"


def render_codex_agent(
    name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any], digest: str
) -> str:
    sandbox = "read-only" if role["mutation"] == "read-only" else "workspace-write"
    nested_agents = "true" if role.get("delegation", {}).get("allowed_roles", []) else "false"
    lines = [
        f"# Generated by implement-rfc/scripts/render_runtime_adapters.py ({digest}).",
        "# Do not edit directly; update config/roles.json, config/routing.json, or the consumer project.json.",
        f"name = {q(name)}",
        f"description = {q(role['description'])}",
        f"model = {q(route['model'])}",
    ]
    if route.get("effort") is not None:
        lines.append(f"model_reasoning_effort = {q(route['effort'])}")
    lines.extend(
        [
            f"sandbox_mode = {q(sandbox)}",
            f"developer_instructions = {q(role_prompt(name, role, route, project))}",
            "",
            "[agents]",
            f"enabled = {nested_agents}",
            "",
        ]
    )
    return "\n".join(lines)


def render_claude_agent(
    name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any], digest: str
) -> str:
    read_only = role["mutation"] == "read-only"
    source_edit = role["mutation"] == "workspace-write"
    tools = "Read, Grep, Glob, Bash"
    if source_edit:
        tools += ", Edit, Write, Skill"
    if role.get("delegation", {}).get("allowed_roles", []):
        tools += ", Agent(" + ",".join(role["delegation"]["allowed_roles"]) + ")"
        tools += ", " + ", ".join(COORDINATION_TOOLS)
    permission_mode = "plan" if read_only else "acceptEdits"
    frontmatter = [
        "---",
        f"name: {name}",
        f"description: {q(role['description'])}",
        f"tools: {tools}",
        f"model: {q(route['model'])}",
        *([f"permissionMode: {permission_mode}"] if name != INTEGRATOR else []),
        *([f"maxTurns: {role['max_turns']}"] if "max_turns" in role else []),
    ]
    if route.get("effort") is not None:
        frontmatter.append(f"effort: {route['effort']}")
    frontmatter.extend(["---", ""])
    body = [
        f"<!-- Generated by implement-rfc/scripts/render_runtime_adapters.py ({digest}). -->",
        "<!-- Do not edit directly; update config/roles.json, config/routing.json, or the consumer project.json. -->",
        "",
        f"# {name}",
        "",
    ]
    for instruction in rendered_role_instructions(name, role, route, project, provider="claude"):
        body.append(f"- {instruction}")
    body.append("")
    return "\n".join(frontmatter + body)


def source_digest(*paths: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(paths, key=lambda candidate: str(candidate)):
        hasher.update(path.name.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()[:16]


def portable_files(skill_dir: Path) -> list[Path]:
    """Every file in the skill directory that must be byte-identical across projects."""
    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir)
        if relative in NON_PORTABLE or relative.parts[0] in NON_PORTABLE_DIRS:
            continue
        if path.name.startswith(".") or path.suffix in {".pyc", ".tmp"}:
            continue
        files.append(path)
    return files


def portable_manifest(skill_dir: Path) -> dict[str, Any]:
    entries = []
    combined = hashlib.sha256()
    for path in portable_files(skill_dir):
        relative = path.relative_to(skill_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({"path": relative, "sha256": digest})
        combined.update(f"{relative}\0{digest}\0".encode("utf-8"))
    return {
        "schema": PORTABLE_MANIFEST_SCHEMA,
        "portable_digest": combined.hexdigest()[:16],
        "files": entries,
    }


def write_or_check(path: Path, content: str, check: bool) -> bool:
    normalized = content.replace("\r\n", "\n")
    if check:
        if not path.exists():
            print(f"missing generated file: {path}", file=sys.stderr)
            return False
        actual = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if actual != normalized:
            print(f"stale generated file: {path}", file=sys.stderr)
            return False
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(normalized)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def safe_destination(root: Path, path: Path) -> None:
    """Refuse linked parents, special leaves, and destinations outside the consumer."""
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError(f"linked adapter destination: {current}")
        expected_type = stat.S_ISREG if current == path else stat.S_ISDIR
        if not expected_type(info.st_mode):
            raise ValueError(f"unsafe adapter destination type: {current}")


RETIRED_ROLES = ("rfc-worker-routine", "rfc-critical-reviewer")
ADAPTER_MARKER = "Generated by implement-rfc/scripts/render_runtime_adapters.py ("
MASK_LOCK = ".mask/skill-config/implement-rfc/native-roles.lock.json"
MASK_LOCK_SCHEMA = "mask.native-role-lock.v1"


def mask_lock_hashes(root: Path) -> dict[str, str] | None:
    """Digests MASK published for this consumer's native roles; None when MASK does not manage it."""
    path = root / MASK_LOCK
    if not path.exists():
        return None
    safe_destination(root, path)
    lock = load_json(path)
    roles = lock.get("roles") if isinstance(lock, dict) else None
    if not isinstance(lock, dict) or lock.get("schema") != MASK_LOCK_SCHEMA or not isinstance(roles, list):
        raise ValueError(f"unrecognized MASK native role lock: {path}")
    result: dict[str, str] = {}
    for row in roles:
        if (not isinstance(row, dict) or row.get("agent") not in ROLE_SUFFIX
                or not isinstance(row.get("name"), str) or not ROLE_NAME_RE.fullmatch(row["name"])
                or not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise ValueError(f"unrecognized MASK native role lock: {path}")
        result[role_relative(row["agent"], row["name"])] = row["sha256"]
    return result


def check_locked_consumer(root: Path, generated: dict, manifest_path: Path, lock: dict[str, str]) -> bool:
    """Under a MASK lock the installed roles answer to the fresh render and to the lock.

    MASK stages roles through prepare_mask_roles.py and publishes them under its
    own lock; it never writes the renderer's publication manifest, so that
    manifest cannot be the verdict here. A file equal to the fresh render is
    current, one that differs is stale, and a lock that disagrees with the
    files is drift for mask ensure to reconcile.
    """
    ok = True
    expected = {path.relative_to(root).as_posix(): hashlib.sha256(content.encode("utf-8")).hexdigest()
                for path, content in generated.items() if path != manifest_path}
    for relative in sorted(set(expected) | set(lock)):
        path = root / relative
        safe_destination(root, path)
        if not path.exists():
            print(f"missing generated file: {path}", file=sys.stderr)
            ok = False
            continue
        digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if relative not in expected:
            print(f"retired generated file: {path}", file=sys.stderr)
            ok = False
        elif digest != expected[relative]:
            print(f"stale generated file: {path}", file=sys.stderr)
            ok = False
        if relative not in lock:
            print(f"unlocked generated file: {path}; run mask ensure", file=sys.stderr)
            ok = False
        elif digest != lock[relative]:
            print(f"lock drift: {path} differs from {MASK_LOCK}; run mask ensure", file=sys.stderr)
            ok = False
    for role in RETIRED_ROLES:
        for provider in ROLE_SUFFIX:
            path = root / role_relative(provider, role)
            if path.exists():
                print(f"retired generated file: {path}", file=sys.stderr)
                ok = False
    if manifest_path.exists():
        print(f"ignored legacy adapter manifest under a MASK lock: {manifest_path}", file=sys.stderr)
    return ok


def complete_outer_events(path: Path) -> list[dict[str, Any]] | None:
    """Read the runner projection only when every event is complete and valid."""
    if not path.exists():
        return None
    records = []
    with path.open("rb") as stream:
        for raw in stream:
            if len(raw) > slice_events.MAX_EVENT or not raw.endswith(b"\n"):
                return None
            try:
                record = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return None
            if (not isinstance(record, dict)
                    or not isinstance(record.get("task_id"), str)
                    or not isinstance(record.get("event"), str)):
                return None
            records.append(record)
            if len(records) > 10000:
                return None
    return records


def handled_max_turn_failure(root: Path, run: Path, order: dict[str, Any],
                             outer_records: list[dict[str, Any]] | None,
                             task_id: str) -> bool:
    """Recognize the one terminal native failure shape qualified for retirement."""
    run_id = run.name
    if (outer_records is None
            or [record.get("event") for record in outer_records] != [
                "admitted", "dispatch_intent", "running", "completion_unknown"]
            or order.get("run_id") != run_id
            or not isinstance(task_id, str)):
        return False
    admitted, dispatch, running, completion = outer_records
    attempt_id = completion.get("attempt_id")
    if (admitted.get("task_id") != "__run__"
            or any(record.get("task_id") != task_id
                   for record in (dispatch, running, completion))
            or any(record.get("attempt_id") != attempt_id
                   for record in (dispatch, running))
            or attempt_id != f"{task_id}-1"
            or completion.get("semantic_acceptance") != "not_decided_by_runner"
            or completion.get("report_path") is not None):
        return False
    lifecycle = run / "lifecycle.jsonl"
    safe_destination(root, lifecycle)
    if not lifecycle.exists():
        return False
    try:
        records, warning = slice_events.EventStore(run).read()
    except (OSError, ValueError, TypeError, AttributeError):
        return False
    expected_events = [
        "dispatch_intent", "native_identity", "dispatched",
        "execution_failed", "native_event_handled",
    ]
    if warning or [record.get("event") for record in records] != expected_events:
        return False
    for sequence, record in enumerate(records):
        if (record.get("run_id") != run_id or record.get("task_id") != task_id
                or record.get("attempt_id") != attempt_id
                or type(record.get("sequence")) is not int
                or record["sequence"] != sequence):
            return False
    identity, dispatched = records[1], records[2]
    session_id = identity.get("driver_session_id")
    turn_id = identity.get("driver_turn_id")
    if (not isinstance(session_id, str) or not session_id
            or not isinstance(turn_id, str) or not turn_id
            or running.get("driver_session_id") != session_id
            or running.get("driver_turn_id") != turn_id
            or dispatched.get("driver_session_id") != session_id
            or dispatched.get("driver_turn_id") != turn_id):
        return False
    failure, handled = records[3], records[4]
    native_event_id = failure.get("native_event_id")
    return (failure.get("reason") == "max_turns"
            and isinstance(native_event_id, str) and bool(native_event_id)
            and handled.get("native_event_id") == native_event_id)


def active_assignments(root: Path) -> list[str]:
    """Inventory existing admitted runs without changing their frozen requests."""
    runs = root / ".mask/generated/implement-rfc/runs"
    safe_destination(root, runs / ".probe")
    active = []
    for path in sorted(runs.glob("*/order.json")):
        safe_destination(root, path)
        order = load_json(path)
        events = path.with_name("events.jsonl")
        safe_destination(root, events)
        latest = {}
        records = complete_outer_events(events)
        if records is not None:
            for event in records:
                latest[event.get("task_id")] = event
        for task in order.get("tasks", []):
            task_id = task.get("id")
            outer = latest.get(task_id, {})
            released = outer.get("event") in ("collected", "cancelled")
            if (task.get("kind") == "agent" and not released
                    and not handled_max_turn_failure(root, path.parent, order, records, task_id)):
                active.append(f"{path.parent.name}/{task_id}")
    return active


def manifest_hashes(manifest, project):
    if manifest is None:
        return {}
    if manifest.get("schema") != ADAPTERS_SCHEMA or manifest.get("project") != project:
        raise ValueError("unrecognized consumer adapter manifest")
    files = manifest.get("files")
    if not isinstance(files, list) or not all(isinstance(item, dict) for item in files):
        raise ValueError("invalid consumer adapter manifest files")
    result = {}
    for item in files:
        relative, digest = item.get("path"), item.get("sha256")
        if (not isinstance(relative, str) or not re.fullmatch(
                r"\.(?:codex/agents/rfc-[a-z-]+\.toml|claude/agents/rfc-[a-z-]+\.md)", relative)
                or relative in result or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ValueError("invalid consumer adapter manifest files")
        result[relative] = digest
    if not result:
        raise ValueError("invalid consumer adapter manifest files")
    return result


def publish_adapters(root, generated, manifest_path, manifest, check):
    """Preflight the entire set; publish the manifest last and retain crash recovery."""
    pending_path = manifest_path.with_name("runtime-adapters.pending.json")
    for path in (*generated, pending_path):
        safe_destination(root, path)
    lock = mask_lock_hashes(root)
    if lock is not None:
        if not check:
            raise ValueError(f"consumer is MASK-managed ({MASK_LOCK} present); run mask ensure instead of rendering directly")
        return check_locked_consumer(root, generated, manifest_path, lock)
    prior = load_json(manifest_path) if manifest_path.exists() else None
    pending = load_json(pending_path) if pending_path.exists() else None
    if pending is not None:
        if (pending.get("schema") != "implement-rfc.adapter-publication.v1"
                or pending.get("target") != manifest
                or prior not in (pending.get("prior"), manifest)):
            raise ValueError("interrupted adapter publication: restore the selected source/configuration before retry")
        prior = pending.get("prior")
    old = manifest_hashes(prior, manifest["project"])
    new = manifest_hashes(manifest, manifest["project"])
    retired = set(old) - set(new)
    for role in RETIRED_ROLES:
        for family, suffix in (("codex", "toml"), ("claude", "md")):
            relative = f".{family}/agents/{role}.{suffix}"
            if relative not in new:
                retired.add(relative)
    for relative in sorted(set(old) | set(new) | retired):
        path = root / relative
        safe_destination(root, path)
        if not path.exists():
            continue
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        allowed = {old.get(relative)}
        if pending is not None:
            allowed.add(new.get(relative))
        if ADAPTER_MARKER.encode() not in content or digest not in allowed:
            if check:
                print(f"stale generated file or unrecognized existing adapter: {path}", file=sys.stderr)
                return False
            raise ValueError(f"modified or unrecognized existing adapter: {path}")
    stale_retired = [root / p for p in retired if (root / p).exists()]
    if check:
        ok = pending is None and not stale_retired
        for path in stale_retired:
            print(f"retired generated file: {path}", file=sys.stderr)
        if pending is not None:
            print("interrupted adapter publication; retry the same render", file=sys.stderr)
        for path, content in generated.items():
            ok = write_or_check(path, content, True) and ok
        return ok
    if all(p.exists() and p.read_text() == content for p, content in generated.items()) and not stale_retired and pending is None:
        return True
    active = active_assignments(root)
    if active:
        raise ValueError("collect or explicitly reissue active assignments before regeneration: " + ", ".join(active))
    if pending is None:
        write_or_check(pending_path, json.dumps({"schema": "implement-rfc.adapter-publication.v1",
                       "prior": prior, "target": manifest}, indent=2) + "\n", False)
    for path, content in generated.items():
        if path != manifest_path:
            write_or_check(path, content, False)
    for path in stale_retired:
        path.unlink()
    write_or_check(manifest_path, generated[manifest_path], False)
    pending_path.unlink()
    return True


def coupling_findings(relative: Path, text: str, identities: list[str]) -> list[str]:
    """Find embedded project facts, without banning harmless protocol words/URLs."""
    if relative.parts[0] in {"examples", "tests", "generated"}:
        return []
    findings = []
    for identity in identities:
        if re.search(r"(?:github\.com[:/][^/\s]+/" + re.escape(identity) + r"(?:\.git)?\b)", text, re.I):
            findings.append(f"concrete repository identity: {identity}")
        for line in text.splitlines():
            if re.search(r"[\"']?(?:project|display_name|origin_repo_name|session_prefix)[\"']?\s*[:=]\s*[\"']?" + re.escape(identity) + r"(?:[\"']|\s*$)", line, re.I):
                findings.append(f"embedded project fact: {identity}")
    inherited = "Better" + "PullReview"
    if inherited in text:
        findings.append("inherited project instruction")
    return findings


ROLE_SUFFIX = {"codex": "toml", "claude": "md"}


def role_relative(provider: str, name: str) -> str:
    """Consumer-relative destination of one native role file."""
    return f".{provider}/agents/{name}.{ROLE_SUFFIX[provider]}"


def generate_roles(
    context: "project_config.ProjectContext", *, profile: str | None = None,
    routing_override: Path | None = None, capabilities_path: Path | None = None,
    integrator_route_path: Path | None = None, preserved_route_path: Path | None = None,
    skill_dir: Path | None = None,
) -> tuple[dict[tuple[str, str], str], dict[str, Any]]:
    """Pure generation: every (provider, role) -> rendered content for the selected consumer.

    Nothing is written. The standalone renderer publishes the result into the
    consumer; the MASK staging entrypoint writes a requested subset into a stage.
    """
    script_path = Path(__file__).resolve()
    skill_dir = (skill_dir or script_path.parents[1]).resolve()
    roles_path = skill_dir / "config" / "roles.json"
    routing_path = skill_dir / "config" / "routing.json"
    project_path = context.project_config_path
    skill_path = skill_dir / "SKILL.md"
    roles_data = load_json(roles_path)
    routing_data = load_json(routing_path)
    project = context.config
    digest_paths = [script_path, skill_path, roles_path, routing_path, project_path]
    original_routing = routing_data
    if routing_override:
        override_path = routing_override.resolve()
        overlay = load_json(override_path)
        for provider in overlay.get("providers", {}).values():
            for route in provider.get("classes", {}).values():
                validate_route(route, "candidate override")
        routing_data = deep_merge(routing_data, overlay)
        digest_paths.append(override_path)

    roles = validate_roles(roles_data)
    assignments, codex_classes, claude_classes = validate_routing(routing_data, roles)

    profiles_path = skill_dir / "config/routing-profiles.json"
    digest_paths.append(profiles_path)
    selection_path = context.repo_root / ".mask/generated/implement-rfc/execution-selection.json"
    if profile is None and selection_path.exists():
        safe_destination(context.repo_root, selection_path)
        selection = load_json(selection_path)
        if selection.get("schema") != "implement-rfc.execution-selection.v1":
            raise ValueError("unsupported execution selection schema")
        profile = selection.get("profile", "baseline")
        digest_paths.append(selection_path)
    capabilities = load_json(capabilities_path) if capabilities_path else None
    if capabilities_path:
        digest_paths.append(capabilities_path)
    for provider, definition in routing_data["providers"].items():
        for name, route in definition["classes"].items():
            if route != original_routing["providers"][provider]["classes"].get(name):
                validate_capability(provider, route, capabilities)
    for provider, route in routing_data.get("session_routes", {}).get("rfc-coordinator", {}).items():
        if route != original_routing.get("session_routes", {}).get("rfc-coordinator", {}).get(provider):
            validate_capability(provider, route, capabilities)
    preserved = load_json(preserved_route_path) if preserved_route_path else None
    explicit = load_json(integrator_route_path) if integrator_route_path else {}
    if set(explicit) - {"codex", "claude"}:
        raise ValueError("invalid explicit integrator providers")
    for path in (integrator_route_path, preserved_route_path):
        if path:
            digest_paths.append(path)
    reference_texts = {}
    for name, role in roles.items():
        if role.get("entrypoint"):
            reference = skill_dir / role["entrypoint"]
            if not reference.is_file() or reference.is_symlink():
                raise ValueError(f"missing or linked role entrypoint: {reference}")
            reference_texts[name] = reference.read_text()
            digest_paths.append(reference)
    routes, provenance = select_routes(routing_data, roles, load_json(profiles_path),
                                       profile or "baseline", capabilities,
                                       explicit_routes={p: {INTEGRATOR: r} for p, r in explicit.items()},
                                       preserved_integrator_routes=preserved)
    digest = hashlib.sha256((source_digest(*digest_paths) + json.dumps(provenance, sort_keys=True)).encode()).hexdigest()
    generated: dict[tuple[str, str], str] = {}
    for name, role in sorted(roles.items()):
        for provider, render in (("codex", render_codex_agent), ("claude", render_claude_agent)):
            # Other roles/providers/session choices do not change this request.
            route = routes[provider][name]
            role_digest = hashlib.sha256(json.dumps({
                "renderer": script_path.read_text(), "role": role,
                "prompt": role_prompt(name, role, route, project, provider=provider), "route": route,
                "reference": reference_texts.get(name),
            }, sort_keys=True).encode()).hexdigest()
            generated[(provider, name)] = render(name, role, route, project, role_digest)
    facts = dict(project=project, assignments=assignments, provenance=provenance, digest=digest,
                 routing=routing_data, roles=roles)
    return generated, facts


def main() -> int:
    script_path = Path(__file__).resolve()
    skill_dir = script_path.parents[1]

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--write-source-manifest", action="store_true", help="Author the canonical portable digest; never render consumer adapters.")
    parser.add_argument(
        "--routing-override",
        type=Path,
        help="Optional candidate routing overlay; use with a temporary --repo-root for evaluation.",
    )
    parser.add_argument("--profile", help="Explicit consumer adapter profile; absent uses local selection or baseline.")
    parser.add_argument("--capabilities", type=Path, help="Verified provider/model to supported efforts JSON for overrides.")
    parser.add_argument("--integrator-route", type=Path, help="Explicit provider-to-model/effort pairs for this task; requires verified capabilities.")
    parser.add_argument("--preserved-integrator-route", type=Path, help="Owner-selected engineering pairs captured before coordinator selection; requires verified capabilities.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write_source_manifest:
        if args.repo_root or args.routing_override or args.profile or args.capabilities or args.integrator_route or args.preserved_integrator_route:
            parser.error("source manifest authoring does not accept consumer/routing options")
        owner = project_config._git(skill_dir, "rev-parse", "--show-toplevel")
        if owner is None or skill_dir != Path(owner).resolve() / "skills" / SKILL_NAME:
            raise ValueError("source manifest authoring requires the canonical skills/implement-rfc checkout")
        path = skill_dir / "generated/portable-manifest.json"
        safe_destination(skill_dir, path)
        return 0 if write_or_check(path, json.dumps(portable_manifest(skill_dir), indent=2, sort_keys=True) + "\n", args.check) else 1

    context = project_config.resolve_context(repo_root=args.repo_root)
    roles_by_key, facts = generate_roles(
        context, profile=args.profile, routing_override=args.routing_override,
        capabilities_path=args.capabilities, integrator_route_path=args.integrator_route,
        preserved_route_path=args.preserved_integrator_route,
    )
    project, assignments, provenance, digest, routing_data = (
        facts["project"], facts["assignments"], facts["provenance"], facts["digest"], facts["routing"])
    repo_root = context.repo_root
    generated: dict[Path, str] = {}
    for (provider, name), content in roles_by_key.items():
        generated[repo_root / role_relative(provider, name)] = content

    manifest_entries: list[dict[str, str]] = []
    for path, content in sorted(generated.items(), key=lambda item: str(item[0])):
        relative = path.relative_to(repo_root).as_posix()
        manifest_entries.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
        )
    manifest = {
        "schema": ADAPTERS_SCHEMA,
        "project": project["project"],
        "source_digest": digest,
        "assignments": assignments,
        "routing_provenance": provenance,
        "verified_as_of": routing_data.get("verified_as_of"),
        "files": manifest_entries,
    }
    generated_dir = repo_root / ".mask/generated" / SKILL_NAME
    generated[generated_dir / "runtime-adapters.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    manifest_path = generated_dir / "runtime-adapters.json"
    ok = publish_adapters(repo_root, generated, manifest_path, manifest, args.check)
    if not ok:
        return 1
    action = "validated" if args.check else "rendered"
    print(f"{action} {len(generated)} files for source={digest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, project_config.ProjectConfigError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
