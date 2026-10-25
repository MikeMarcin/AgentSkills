from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

from project_fixtures import CONFIG, init_repo, write_context, git
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "project_config.py"
SPEC = importlib.util.spec_from_file_location("project_config_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ProjectConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = module.validate(copy.deepcopy(CONFIG))

    def test_checked_in_project_config_validates(self) -> None:
        self.assertEqual(self.config["schema"], module.SCHEMA)

    def test_schema_and_loader_agree_on_required_keys(self) -> None:
        schema = json.loads((SKILL_DIR / "schemas" / "project.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(module.REQUIRED_KEYS))
        self.assertEqual(set(schema["properties"]), set(module.REQUIRED_KEYS) | set(module.OPTIONAL_KEYS))

    def test_lane_order_and_activity(self) -> None:
        lanes = module.lane_names(self.config)
        self.assertEqual(lanes[0], self.config["lanes"]["inbox"])
        self.assertEqual(lanes[-1], self.config["lanes"]["done"])
        self.assertEqual(module.active_lanes(self.config), lanes[:-1])
        self.assertEqual(set(self.config["lane_statuses"]), set(lanes))

    def test_station_keys_are_optional_but_still_validated(self) -> None:
        config = copy.deepcopy(self.config)
        for key in module.LEGACY_STATION_KEYS:
            config.pop(key, None)
        self.assertEqual(module.validate(config)["project"], self.config["project"])
        for key, bad in (("session_prefix", "Not A Token"), ("station_registry_doc", "docs/")):
            broken = dict(config, **{key: bad})
            with self.assertRaises(module.ProjectConfigError):
                module.validate(broken)

    def test_explicit_closeout_membership(self):
        matcher = module.closeout_card_matcher(self.config)
        self.assertTrue(matcher(Path('card.md'), {'closeout_for': ['RFC-AAA-0001']}))
        self.assertFalse(matcher(Path('closeout.md'), {}))

    def test_rejects_unknown_key_missing_key_and_bad_lane(self) -> None:
        config = copy.deepcopy(self.config)
        config["extra"] = 1
        with self.assertRaises(module.ProjectConfigError):
            module.validate(config)
        config = copy.deepcopy(self.config)
        del config["lanes"]
        with self.assertRaises(module.ProjectConfigError):
            module.validate(config)
        config = copy.deepcopy(self.config)
        config["lanes"]["done"] = "Done Lane"
        with self.assertRaises(module.ProjectConfigError):
            module.validate(config)
        config = copy.deepcopy(self.config)
        config["closeout_card"] = {"filename_pattern": "x", "front_matter": {"closeout": "true"}}
        with self.assertRaises(module.ProjectConfigError):
            module.validate(config)


class ConsumerContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = self.enterContext(tempfile.TemporaryDirectory())
        self.base = Path(self.temp).resolve()
        self.a, self.b = self.base / "alpha", self.base / "beta"
        init_repo(self.a, token="alpha")
        init_repo(self.b, token="beta")
        self.enterContext(mock.patch.dict(os.environ, {}, clear=False))
        os.environ.pop(module.PROJECT_ROOT_ENV, None)

    def test_shared_assets_sequential_consumers_nested_and_links(self):
        for root in (self.a, self.b, self.a):
            entry = root / ".agents/skills/implement-rfc"
            entry.parent.mkdir(parents=True, exist_ok=True)
            if not entry.exists():
                entry.symlink_to(SKILL_DIR, target_is_directory=True)
            nested = root / "src/deep"
            nested.mkdir(parents=True, exist_ok=True)
            context = module.resolve_context(cwd=nested)
            self.assertEqual(context.repo_root, root)
            self.assertEqual(context.asset_root, SKILL_DIR)
            self.assertEqual(context.config["project"], root.name)
            result = subprocess.run([sys.executable, str(entry / "scripts/project_config.py")],
                                    cwd=nested, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(root), result.stdout)
            self.assertIn(root.name, result.stdout)

    def test_explicit_environment_and_invalid_explicit_never_fall_through(self):
        os.environ[module.PROJECT_ROOT_ENV] = str(self.b)
        self.assertEqual(module.resolve_context(cwd=self.a).repo_root, self.b)
        self.assertEqual(module.resolve_context(repo_root=self.a, cwd=self.b).repo_root, self.a)
        with self.assertRaises(module.ProjectConfigError):
            module.resolve_context(repo_root=self.base / "absent", cwd=self.a)
        os.environ[module.PROJECT_ROOT_ENV] = str(self.base / "absent")
        with self.assertRaises(module.ProjectConfigError):
            module.resolve_context(cwd=self.a)
        self.assertEqual(module.resolve_context(repo_root=self.a).repo_root, self.a)

    def test_real_worktree_uses_own_context(self):
        worktree = self.base / "worktree"
        git(self.a, "worktree", "add", "-b", "fixture-lane", str(worktree))
        try:
            write_context(worktree, token="worktree")
            nested = worktree / "nested"
            nested.mkdir()
            self.assertEqual(module.resolve_context(cwd=nested).repo_root, worktree)
            self.assertEqual(module.resolve_context(repo_root=worktree).config["project"], "worktree")
        finally:
            git(self.a, "worktree", "remove", "--force", str(worktree))

    def test_missing_invalid_rules_identity_and_escape_refuse(self):
        directory = self.a / module.CONTEXT_DIR
        (directory / "project.json").unlink()
        with self.assertRaisesRegex(module.ProjectConfigError, "missing project configuration"):
            module.resolve_context(repo_root=self.a)
        write_context(self.a, token="alpha")
        (directory / "project.md").unlink()
        with self.assertRaisesRegex(module.ProjectConfigError, "missing project rules"):
            module.resolve_context(repo_root=self.a)
        write_context(self.a, token="alpha")
        (directory / "project.json").write_text("{}")
        with self.assertRaisesRegex(module.ProjectConfigError, "required keys"):
            module.resolve_context(repo_root=self.a)
        write_context(self.a, token="alpha")
        git(self.a, "remote", "add", "origin", "https://example.invalid/wrong.git")
        with self.assertRaisesRegex(module.ProjectConfigError, "identity mismatch"):
            module.resolve_context(repo_root=self.a)
        git(self.a, "remote", "remove", "origin")
        (directory / "project.json").unlink()
        (directory / "project.json").symlink_to(self.b / module.CONTEXT_DIR / "project.json")
        with self.assertRaisesRegex(module.ProjectConfigError, "escapes selected consumer"):
            module.resolve_context(repo_root=self.a)
        with self.assertRaisesRegex(module.ProjectConfigError, "escapes selected consumer"):
            module.resolve_context(repo_root=self.a, project_config_path=self.b / module.CONTEXT_DIR / "project.json")

    def test_legacy_requires_physical_local_assets_and_agreeing_identity(self):
        directory = self.a / module.CONTEXT_DIR
        config = (directory / "project.json").read_text()
        shutil.rmtree(directory)
        local = self.a / ".agents/skills/implement-rfc"
        (local / "config").mkdir(parents=True)
        (local / "references").mkdir()
        (local / "SKILL.md").write_text("local skill")
        (local / "config/project.json").write_text(config)
        (local / "references/project.md").write_text("alpha rules")
        with mock.patch.object(module, "SKILL_DIR", local):
            with self.assertRaisesRegex(module.ProjectConfigError, "missing project configuration"):
                module.resolve_context(repo_root=self.a)
        with self.assertRaisesRegex(module.ProjectConfigError, "missing project configuration"):
            module.resolve_context(repo_root=self.a)
        moved = self.base / "shared"
        local.rename(moved)
        local.symlink_to(moved, target_is_directory=True)
        with mock.patch.object(module, "SKILL_DIR", moved):
            with self.assertRaisesRegex(module.ProjectConfigError, "missing project configuration"):
                module.resolve_context(repo_root=self.a)

    def test_git_environment_cannot_redirect_selection(self):
        with mock.patch.dict(os.environ, {"GIT_DIR": str(self.b / ".git"), "GIT_WORK_TREE": str(self.b)}):
            self.assertEqual(module.resolve_context(repo_root=self.a).repo_root, self.a)
            self.assertEqual(module.resolve_context(cwd=self.a).config["project"], "alpha")

    def test_selected_context_survives_later_cwd_change(self):
        selected = module.resolve_context(repo_root=self.a)
        with mock.patch.object(Path, "cwd", return_value=SKILL_DIR / "scripts"):
            self.assertEqual(selected.repo_root, self.a)
            self.assertEqual(module.resolve_context(repo_root=selected.repo_root).config["project"], "alpha")

    def test_helpers_import_outside_any_repository(self):
        scripts = SKILL_DIR / "scripts"
        code = f"import sys; sys.path.insert(0, {str(scripts)!r}); " + "; ".join(
            f"import {name}" for name in ("project_config", "audit_board", "codex_lane"))
        result = subprocess.run([sys.executable, "-c", code], cwd=self.base, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


    def test_optional_helpers_keep_sequential_consumer_identity(self):
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        import codex_lane
        role, route = codex_lane.load_role_route("rfc-reviewer")
        for root in (self.a, self.b, self.a):
            selected = module.resolve_context(repo_root=root)
            prompt = codex_lane.compose_prompt("rfc-reviewer", role, route, "rfc_reviewer_check", "Check", selected.config)
            self.assertTrue(prompt.startswith(root.name.title() + " lane"))
            self.assertEqual(codex_lane.lane_log_path(root, selected.config).name, f"{root.name}-codex-lanes.jsonl")


if __name__ == "__main__":
    unittest.main()
