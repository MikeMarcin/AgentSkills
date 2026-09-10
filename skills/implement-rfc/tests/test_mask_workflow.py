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

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
DESCRIPTOR = SKILL_DIR / "mask-workflow.json"
ENTRYPOINT = SCRIPTS / "prepare_mask_roles.py"
PREFLIGHT = SCRIPTS / "workflow_preflight.py"
sys.path.insert(0, str(SCRIPTS))
from project_fixtures import init_repo  # noqa: E402
import project_config  # noqa: E402
import render_runtime_adapters as renderer  # noqa: E402


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


STUB = '''#!/usr/bin/env python3
import json, sys
mode = {mode!r}
args = sys.argv[1:]
if args[0] == "capabilities":
    workflow = {{"readiness": "workflow_readiness_v1", "native_roles": True, "staged_setup": True, "host_load": "not_verified"}}
    data = {{"workflow": workflow}} if mode != "old" else {{}}
    print(json.dumps({{"ok": True, "schema_version": 1, "data": data, "error": None}}))
    raise SystemExit(0)
root = args[args.index("--project") + 1]
if mode == "old":
    print(json.dumps({{"ok": True, "schema_version": 1, "data": {{"readiness": "ready_pinned"}}, "error": None}}))
    raise SystemExit(0)
roles = [dict(agent="codex", name="rfc-integrator", state="ok" if mode == "ready" else "missing", route={{"model": "m"}}, host_load="not_verified")]
report = dict(skill="implement-rfc", workflow="declared", complete=mode == "ready", roles=roles)
data = dict(readiness="ready_pinned" if mode == "ready" else "workflow_incomplete",
            scope_readiness=[dict(root=root, readiness="ready_pinned", workflow="complete" if mode == "ready" else "incomplete")],
            workflow_readiness=[dict(root=root, complete=mode == "ready", skills=[report])])
error = None if mode == "ready" else dict(code="workflow.incomplete", message="incomplete", details=dict(workflow=["implement-rfc codex/rfc-integrator: missing"]))
print(json.dumps({{"ok": mode == "ready", "schema_version": 1, "data": data, "error": error}}))
raise SystemExit(0 if mode == "ready" else 4)
'''


class PreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mask-preflight-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def preflight(self, mode: str) -> tuple[int, dict]:
        stub = self.base / f"{mode}-mask.py"
        stub.write_text(STUB.format(mode=mode), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(PREFLIGHT), "--repo-root", str(self.base), "--mask", str(stub), "--json"],
                                capture_output=True, text=True)
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


if __name__ == "__main__":
    unittest.main()
