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

ROLE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODEL_CLASSES = {"mechanical", "balanced", "standard", "deep", "critical"}
MUTATIONS = {"read-only", "build-write", "workspace-write"}
PLACEHOLDER_RE = re.compile(r"^<[^>]+>$|\$\{")
ROLES_SCHEMA = "implement-rfc.roles.v1"
ROUTING_SCHEMA = "implement-rfc.routing.v1"
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


def validate_roles(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if data.get("schema") != ROLES_SCHEMA:
        raise ValueError("roles.json has an unsupported schema")
    roles = data.get("roles")
    if not isinstance(roles, dict) or not roles:
        raise ValueError("roles.json must contain a non-empty roles object")
    for name, role in roles.items():
        if not isinstance(name, str) or not ROLE_NAME_RE.fullmatch(name):
            raise ValueError(f"invalid role name: {name!r}")
        if not isinstance(role, dict):
            raise ValueError(f"role {name} must be an object")
        if not isinstance(role.get("description"), str) or not role["description"].strip():
            raise ValueError(f"role {name} needs a description")
        if role.get("mutation") not in MUTATIONS:
            raise ValueError(f"role {name} has invalid mutation")
        if not isinstance(role.get("max_turns"), int) or role["max_turns"] < 1:
            raise ValueError(f"role {name} has invalid max_turns")
        if not isinstance(role.get("may_spawn_utility", False), bool):
            raise ValueError(f"role {name} has invalid may_spawn_utility")
        instructions = role.get("instructions")
        if not isinstance(instructions, list) or not instructions or not all(
            isinstance(item, str) and item.strip() for item in instructions
        ):
            raise ValueError(f"role {name} needs non-empty instruction strings")
    return roles


def validate_routing(
    data: dict[str, Any], roles: dict[str, dict[str, Any]]
) -> tuple[
    dict[str, str],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    if data.get("schema") != ROUTING_SCHEMA:
        raise ValueError("routing.json has an unsupported schema")
    assignments = data.get("assignments")
    providers = data.get("providers")
    if not isinstance(assignments, dict):
        raise ValueError("routing assignments must be an object")
    if set(assignments) != set(roles):
        missing = sorted(set(roles) - set(assignments))
        extra = sorted(set(assignments) - set(roles))
        raise ValueError(f"routing role mismatch; missing={missing}, extra={extra}")
    for role_name, model_class in assignments.items():
        if model_class not in MODEL_CLASSES:
            raise ValueError(f"routing assigns invalid class {model_class} to {role_name}")
    if not isinstance(providers, dict) or "codex" not in providers or "claude" not in providers:
        raise ValueError("routing providers must contain codex and claude")

    codex_classes = providers["codex"].get("classes")
    claude_classes = providers["claude"].get("classes")
    if not isinstance(codex_classes, dict) or not isinstance(claude_classes, dict):
        raise ValueError("provider classes must be objects")
    for provider_name, classes in (("codex", codex_classes), ("claude", claude_classes)):
        for model_class in set(assignments.values()):
            route = classes.get(model_class)
            if not isinstance(route, dict) or not isinstance(route.get("model"), str):
                raise ValueError(f"{provider_name} lacks model route for {model_class}")
            model = route["model"].strip()
            if not model or PLACEHOLDER_RE.search(model):
                raise ValueError(f"{provider_name} route {model_class} contains a placeholder")
            effort = route.get("effort")
            if effort is not None and not isinstance(effort, str):
                raise ValueError(f"{provider_name} route {model_class} has invalid effort")
    return assignments, codex_classes, claude_classes


def select_routes(routing, roles, profiles, profile="baseline", capabilities=None,
                  order_routes=None, explicit_routes=None):
    """Resolve per-role requests; rendering never selects the primary session."""
    assignments, codex, claude = validate_routing(routing, roles)
    if profiles.get("schema") != "implement-rfc.routing-profiles.v1":
        raise ValueError("unsupported routing profiles schema")
    selected = profiles.get("profiles", {}).get(profile)
    if not isinstance(selected, dict):
        raise ValueError("unknown routing profile")
    routes = {p: {name: dict(classes[assignments[name]]) for name in roles}
              for p, classes in (("codex", codex), ("claude", claude))}
    origins = {p: {name: "baseline" for name in roles} for p in routes}
    for origin, overlay in (("profile", selected.get("overrides", {})),
                            ("admitted_order", order_routes or {}),
                            ("explicit_user", explicit_routes or {})):
        if not isinstance(overlay, dict) or set(overlay) - set(routes):
            raise ValueError("invalid route override providers")
        for provider, changes in overlay.items():
            if not isinstance(changes, dict) or set(changes) - set(roles):
                raise ValueError("invalid route override roles")
            for name, route in changes.items():
                if (not isinstance(route, dict) or set(route) != {"model", "effort"}
                        or not isinstance(route["model"], str) or not route["model"].strip()
                        or PLACEHOLDER_RE.search(route["model"])
                        or (route["effort"] is not None and not isinstance(route["effort"], str))):
                    raise ValueError("override requires exact model and effort")
                supported = (capabilities or {}).get(provider, {}).get(route["model"], [])
                if route["effort"] not in supported:
                    raise ValueError(f"unsupported or unverified runtime capability: {provider}/{route['model']}/{route['effort']}")
                routes[provider][name] = dict(route)
                origins[provider][name] = origin
    encoded = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    return routes, {"profile": profile, "profile_digest": hashlib.sha256(encoded).hexdigest(),
                    "experiment": selected.get("experiment"), "requested": routes,
                    "origins": origins, "observed": None,
                    "enforcement": {"codex": "agents-disabled", "claude": "Agent-tool-omitted"}}


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
    name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any]
) -> list[str]:
    banner = startup_banner(name, route)
    # Routine implementation retains every project-specific worker boundary.
    addenda_roles = ("rfc-worker", name) if name == "rfc-worker-routine" else (name,)
    addenda = [line for role_name in addenda_roles for line in project["role_addenda"].get(role_name, [])]
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
    if role.get("may_spawn_utility", False):
        instructions.append(
            "Name every nested rfc-utility session with the role followed by a concise "
            "purpose. Use rfc-utility-<purpose> where accepted or the runtime-safe "
            "rfc_utility_<purpose> form for Codex task names; never use a purpose-only name."
        )
    return instructions


def role_prompt(name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any]) -> str:
    return "\n\n".join(rendered_role_instructions(name, role, route, project)) + "\n"


def render_codex_agent(
    name: str, role: dict[str, Any], route: dict[str, Any], project: dict[str, Any], digest: str
) -> str:
    sandbox = "read-only" if role["mutation"] == "read-only" else "workspace-write"
    nested_agents = "true" if role.get("may_spawn_utility", False) else "false"
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
    if role.get("may_spawn_utility", False):
        tools += ", Agent(rfc-utility)"
    permission_mode = "plan" if read_only else "acceptEdits"
    frontmatter = [
        "---",
        f"name: {name}",
        f"description: {q(role['description'])}",
        f"tools: {tools}",
        f"model: {q(route['model'])}",
        f"permissionMode: {permission_mode}",
        f"maxTurns: {role['max_turns']}",
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
    for instruction in rendered_role_instructions(name, role, route, project):
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
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write_source_manifest:
        if args.repo_root or args.routing_override or args.profile or args.capabilities:
            parser.error("source manifest authoring does not accept consumer/routing options")
        owner = project_config._git(skill_dir, "rev-parse", "--show-toplevel")
        if owner is None or skill_dir != Path(owner).resolve() / "skills" / SKILL_NAME:
            raise ValueError("source manifest authoring requires the canonical skills/implement-rfc checkout")
        path = skill_dir / "generated/portable-manifest.json"
        safe_destination(skill_dir, path)
        return 0 if write_or_check(path, json.dumps(portable_manifest(skill_dir), indent=2, sort_keys=True) + "\n", args.check) else 1

    context = project_config.resolve_context(repo_root=args.repo_root)
    roles_path = skill_dir / "config" / "roles.json"
    routing_path = skill_dir / "config" / "routing.json"
    project_path = context.project_config_path
    skill_path = skill_dir / "SKILL.md"
    roles_data = load_json(roles_path)
    routing_data = load_json(routing_path)
    project = context.config
    digest_paths = [script_path, skill_path, roles_path, routing_path, project_path]
    if args.routing_override:
        override_path = args.routing_override.resolve()
        routing_data = deep_merge(routing_data, load_json(override_path))
        digest_paths.append(override_path)

    roles = validate_roles(roles_data)
    assignments, codex_classes, claude_classes = validate_routing(routing_data, roles)

    profiles_path = skill_dir / "config/routing-profiles.json"
    digest_paths.append(profiles_path)
    selection_path = context.repo_root / ".mask/generated/implement-rfc/execution-selection.json"
    profile = args.profile
    if profile is None and selection_path.exists():
        safe_destination(context.repo_root, selection_path)
        selection = load_json(selection_path)
        if selection.get("schema") != "implement-rfc.execution-selection.v1":
            raise ValueError("unsupported execution selection schema")
        profile = selection.get("profile", "baseline")
        digest_paths.append(selection_path)
    capabilities = load_json(args.capabilities) if args.capabilities else None
    if args.capabilities:
        digest_paths.append(args.capabilities)
    routes, provenance = select_routes(routing_data, roles, load_json(profiles_path),
                                       profile or "baseline", capabilities)
    digest = hashlib.sha256((source_digest(*digest_paths) + json.dumps(provenance, sort_keys=True)).encode()).hexdigest()
    repo_root = context.repo_root
    generated: dict[Path, str] = {}
    for name, role in sorted(roles.items()):
        model_class = assignments[name]
        generated[repo_root / ".codex" / "agents" / f"{name}.toml"] = render_codex_agent(
            name, role, routes["codex"][name], project, digest
        )
        generated[repo_root / ".claude" / "agents" / f"{name}.md"] = render_claude_agent(
            name, role, routes["claude"][name], project, digest
        )

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
    for path in generated:
        safe_destination(repo_root, path)
    prior = load_json(manifest_path) if manifest_path.exists() else None
    if prior is not None and (prior.get("schema") != ADAPTERS_SCHEMA or prior.get("project") != project["project"]):
        raise ValueError("unrecognized consumer adapter manifest")
    if prior is not None and (not isinstance(prior.get("files"), list) or not all(
        isinstance(item, dict) and isinstance(item.get("path"), str) for item in prior["files"]
    )):
        raise ValueError("invalid consumer adapter manifest files")
    prior_paths = {item["path"] for item in prior["files"]} if prior else set()
    for path in generated:
        if path == manifest_path or not path.exists():
            continue
        if path.relative_to(repo_root).as_posix() not in prior_paths or "Generated by implement-rfc/scripts/render_runtime_adapters.py (" not in path.read_text(encoding="utf-8"):
            raise ValueError(f"unrecognized existing adapter: {path}")

    ok = True
    for path, content in sorted(generated.items(), key=lambda item: str(item[0])):
        safe_destination(repo_root, path)
        ok = write_or_check(path, content, args.check) and ok
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
