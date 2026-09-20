"""MASK workflow readiness surface (RFC-ASK-0011): descriptor, staging entrypoint and preflight.

The end-to-end proof (MASK's real CLI deploying and retiring these roles in
disposable consumers) is recorded on ASK-0059; these tests pin the package-side
contract without requiring a MASK checkout.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
DESCRIPTOR = SKILL_DIR / "mask-workflow.json"
ENTRYPOINT = SCRIPTS / "prepare_mask_roles.py"
PREFLIGHT = SCRIPTS / "workflow_preflight.py"
sys.path.insert(0, str(SCRIPTS))
from project_fixtures import init_repo  # noqa: E402
import project_config  # noqa: E402
import render_runtime_adapters as renderer  # noqa: E402
import personal_state  # noqa: E402
import personal_lanes  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DescriptorTests(unittest.TestCase):
    def test_descriptor_declares_every_current_role_for_both_agents(self) -> None:
        value = json.loads(DESCRIPTOR.read_text(encoding="utf-8"))
        roles = set(json.loads((SKILL_DIR / "config/roles.json").read_text(encoding="utf-8"))["roles"])
        declared = {(row["agent"], row["name"]) for row in value["native_roles"]}
        self.assertEqual(declared, {(agent, role) for role in roles for agent in ("codex", "claude")})
        self.assertTrue(all(row["setup"] == "prepare-roles" for row in value["native_roles"]))
        (action,) = value["setup"]
        self.assertEqual(action["entrypoint"], "scripts/prepare_mask_roles.py")
        self.assertIn(action["entrypoint"], action["package_inputs"])
        for relative in action["package_inputs"]:
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)
        self.assertEqual({row["id"] for row in value["inputs"]}, set(action["inputs"]))
        self.assertEqual(action["effects"], "staged-native-roles")
        self.assertTrue(1 <= action["timeout_seconds"] <= 120)
        self.assertEqual(action["parameters"], {})
        personal = value["scopes"]["user"]
        self.assertEqual(personal["inputs"], [])
        self.assertEqual({(row["agent"], row["name"]) for row in personal["native_roles"]}, declared)
        self.assertEqual(personal["setup"][0]["inputs"], [])


class StagingEntrypointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mask-stage-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.consumer = self.base / "consumer"
        init_repo(self.consumer, token="alpha")
        self.stage = self.base / "work/output"
        self.stage.mkdir(parents=True)
        self.descriptor = json.loads(DESCRIPTOR.read_text(encoding="utf-8"))

    def request(self, roles, *, action="prepare-roles", inputs=None, parameters=None) -> Path:
        if inputs is None:
            inputs = []
            for row in self.descriptor["inputs"]:
                path = self.consumer / row["path"]
                inputs.append(dict(id=row["id"], path=row["path"], sha256=sha(path) if path.is_file() else None))
        request = self.base / "work/request.json"
        request.write_text(json.dumps(dict(schema="mask.setup-request.v1", action=action, native_roles=roles,
                                           inputs=inputs, parameters=parameters or {})), encoding="utf-8")
        return request

    def run_entrypoint(self, request: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(ENTRYPOINT), "--repo-root", str(self.consumer), "--output-root", str(self.stage),
                               "--request-file", str(request)], capture_output=True, text=True, cwd=str(self.base / "work"),
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))

    def staged(self) -> list[str]:
        return sorted(path.relative_to(self.stage).as_posix() for path in self.stage.rglob("*") if path.is_file())

    def test_stages_exactly_the_requested_roles_with_renderer_bytes(self) -> None:
        roles = [dict(agent="codex", name="rfc-integrator"), dict(agent="claude", name="rfc-worker")]
        result = self.run_entrypoint(self.request(roles))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.staged(), ["claude/rfc-worker.md", "codex/rfc-integrator.toml"])
        generated, _ = renderer.generate_roles(project_config.resolve_context(repo_root=self.consumer))
        self.assertEqual((self.stage / "codex/rfc-integrator.toml").read_text(encoding="utf-8"), generated[("codex", "rfc-integrator")])
        self.assertEqual((self.stage / "claude/rfc-worker.md").read_text(encoding="utf-8"), generated[("claude", "rfc-worker")])
        self.assertFalse((self.consumer / ".codex/agents").exists())
        self.assertFalse((self.consumer / ".claude/agents").exists())
        self.assertEqual(sorted(path.name for path in (self.base / "work").iterdir()), ["output", "request.json"])

    def test_changed_or_appeared_inputs_are_refused_before_staging(self) -> None:
        roles = [dict(agent="codex", name="rfc-integrator")]
        request = self.request(roles)
        (self.consumer / ".mask/skill-config/implement-rfc/project.md").write_text("# edited after observation\n", encoding="utf-8")
        result = self.run_entrypoint(request)
        self.assertEqual(result.returncode, 2)
        self.assertIn("changed since MASK observed it", result.stderr)
        self.assertEqual(self.staged(), [])
        request = self.request(roles)
        selection = self.consumer / ".mask/generated/implement-rfc/execution-selection.json"
        selection.parent.mkdir(parents=True)
        selection.write_text('{"schema": "implement-rfc.execution-selection.v1", "profile": "baseline"}', encoding="utf-8")
        result = self.run_entrypoint(request)
        self.assertEqual(result.returncode, 2)
        self.assertIn("appeared after MASK observed it absent", result.stderr)
        self.assertEqual(self.staged(), [])

    def test_unknown_action_role_or_parameters_are_refused(self) -> None:
        for request in (self.request([dict(agent="codex", name="rfc-integrator")], action="other"),
                        self.request([dict(agent="codex", name="rfc-nonexistent")]),
                        self.request([dict(agent="codex", name="rfc-integrator")], parameters={"x": 1})):
            result = self.run_entrypoint(request)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(self.staged(), [])

    def test_personal_roles_render_without_a_git_consumer_or_project_addenda(self) -> None:
        roles = [dict(agent="codex", name="rfc-integrator"), dict(agent="claude", name="rfc-worker")]
        for source in (self.base / "home-a", self.base / "home-b"):
            source.mkdir()
            request = self.base / f"request-{source.name}.json"
            request.write_text(json.dumps(dict(schema="mask.setup-request.v1", scope="user", action="prepare-roles",
                                               native_roles=roles, inputs=[], parameters={})), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ENTRYPOINT), "--repo-root", str(source),
                                     "--output-root", str(self.stage), "--request-file", str(request)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((source / ".git").exists())
        generated, _ = renderer.generate_roles(None, scope="user")
        for role in roles:
            path = self.stage / role["agent"] / f"{role['name']}.{renderer.ROLE_SUFFIX[role['agent']]}"
            self.assertEqual(path.read_text(), generated[(role["agent"], role["name"])])
            self.assertNotIn("AgentSkills", path.read_text())
            self.assertNotIn("{attended_review_skill}", path.read_text())

    def test_explicit_project_setup_survives_remembered_personal_binding(self) -> None:
        with patch.dict(os.environ, {"IMPLEMENT_RFC_HOME": str(self.base / "personal-state")}):
            personal_state.initialize(self.consumer)
            role = dict(agent="codex", name="rfc-integrator")
            result = self.run_entrypoint(self.request([role]))
        self.assertEqual(result.returncode, 0, result.stderr)
        expected, _ = renderer.generate_roles(project_config.resolve_context(repo_root=self.consumer, mode="project"))
        self.assertEqual((self.stage / "codex/rfc-integrator.toml").read_text(), expected[("codex", "rfc-integrator")])


STUB = '''#!/usr/bin/env python3
import json, sys
mode = {mode!r}
args = sys.argv[1:]
if args[0] == "capabilities":
    workflow = {{"readiness": "workflow_readiness_v1", "native_roles": True, "staged_setup": True, "host_load": "not_verified"}}
    data = {{"workflow": workflow}} if mode != "old" else {{}}
    print(json.dumps({{"ok": True, "schema_version": 1, "data": data, "error": None}}))
    raise SystemExit(0)
user = "--user" in args
root = "personal-user" if user else args[args.index("--project") + 1]
scope = "user" if user else "project"
if mode == "old":
    print(json.dumps({{"ok": True, "schema_version": 1, "data": {{"readiness": "ready_pinned"}}, "error": None}}))
    raise SystemExit(0)
roles = [dict(agent="codex", name="rfc-integrator", state="ok" if mode == "ready" else "missing", route={{"model": "m"}}, host_load="not_verified")]
report = dict(skill="implement-rfc", workflow="declared", complete=mode == "ready", roles=roles)
data = dict(readiness="ready_pinned" if mode == "ready" else "workflow_incomplete",
            scope_readiness=[dict(root=root, scope=scope, readiness="ready_pinned", workflow="complete" if mode == "ready" else "incomplete")],
            workflow_readiness=[dict(root=root, scope=scope, complete=mode == "ready", skills=[report])])
error = None if mode == "ready" else dict(code="workflow.incomplete", message="incomplete", details=dict(workflow=["implement-rfc codex/rfc-integrator: missing"]))
print(json.dumps({{"ok": mode == "ready", "schema_version": 1, "data": data, "error": error}}))
raise SystemExit(0 if mode == "ready" else 4)
'''


class PreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mask-preflight-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        init_repo(self.base, token="alpha")

    def preflight(self, mode: str, *, root: Path | None = None,
                  extra: tuple[str, ...] = (), env: dict | None = None) -> tuple[int, dict]:
        stub = self.base / f"{mode}-mask.py"
        stub.write_text(STUB.format(mode=mode), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(PREFLIGHT), "--repo-root", str(root or self.base),
                                 "--mask", str(stub), "--strategy", "coordinator-integrator", "--json", *extra],
                                capture_output=True, text=True, env=env)
        return result.returncode, json.loads(result.stdout)

    def test_old_program_link_only_success_is_unsupported(self) -> None:
        code, result = self.preflight("old")
        self.assertEqual((code, result["state"]), (1, "unsupported"))
        self.assertIn("workflow_readiness_v1", result["detail"])

    def test_complete_declared_readiness_is_ready(self) -> None:
        code, result = self.preflight("ready")
        self.assertEqual((code, result["state"], result["host_load"]), (0, "ready", "not_verified"))
        self.assertEqual(result["roles"], [dict(agent="codex", name="rfc-integrator", state="ok", route={"model": "m"})])

    def test_incomplete_readiness_reports_blockers(self) -> None:
        code, result = self.preflight("incomplete")
        self.assertEqual((code, result["state"]), (1, "incomplete"))
        self.assertEqual(result["blockers"], ["implement-rfc codex/rfc-integrator: missing"])

    def test_missing_program_is_an_error(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(PREFLIGHT), "--repo-root", str(self.base), "--mask", "no-such-mask-program", "--json"],
                                capture_output=True, text=True)
        self.assertEqual((result.returncode, json.loads(result.stdout)["state"]), (2, "error"))

    def test_personal_preflight_requires_binding_then_checks_user_roles(self) -> None:
        source = self.base / "source"
        init_repo(source, token="alpha")
        private_home = self.base / "private-home"
        env = dict(os.environ, IMPLEMENT_RFC_HOME=str(private_home))
        code, result = self.preflight("ready", root=source, extra=("--mode", "personal"), env=env)
        self.assertEqual((code, result["state"]), (1, "incomplete"))
        self.assertIn("binding", result["detail"])
        self.assertFalse(private_home.exists())
        prior = os.environ.get("IMPLEMENT_RFC_HOME")
        os.environ["IMPLEMENT_RFC_HOME"] = str(private_home)
        try:
            personal_state.initialize(source)
        finally:
            if prior is None:
                os.environ.pop("IMPLEMENT_RFC_HOME", None)
            else:
                os.environ["IMPLEMENT_RFC_HOME"] = prior
        code, result = self.preflight("ready", root=source, env=env)
        self.assertEqual((code, result["state"], result["mode"], result["host_load"]),
                         (0, "ready", "personal", "not_verified"))
        self.assertNotEqual(result["workflow_root"], result["source_root"])
        tracker = Path(result["workflow_root"])
        binding = personal_state.binding_path(private_home, source)
        hidden = binding.with_suffix(".hidden")
        binding.rename(hidden)
        try:
            code, result = self.preflight("ready", root=source, extra=("--mode", "personal", "--workflow-root", str(tracker)), env=env)
            self.assertEqual((code, result["state"]), (1, "incomplete"))
            self.assertIn("binding is missing", result["detail"])
        finally:
            hidden.rename(binding)
        prior = os.environ.get("IMPLEMENT_RFC_HOME")
        os.environ["IMPLEMENT_RFC_HOME"] = str(private_home)
        try:
            personal_lanes.bind_pair(source)
        finally:
            if prior is None:
                os.environ.pop("IMPLEMENT_RFC_HOME", None)
            else:
                os.environ["IMPLEMENT_RFC_HOME"] = prior
        subprocess.run(["git", "-C", str(source), "switch", "-c", "other"], check=True, capture_output=True)
        code, result = self.preflight("ready", root=source, extra=("--mode", "personal"), env=env)
        self.assertEqual((code, result["state"]), (1, "incomplete"))
        self.assertIn("explicit rebind", result["detail"])


if __name__ == "__main__":
    unittest.main()
