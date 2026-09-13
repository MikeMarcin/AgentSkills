"""Public personal setup/status, source footprint and project-mode isolation."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from project_fixtures import git, write_context

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/personal_tracker.py"
CONFIG = SCRIPT.with_name("project_config.py")
BOARD = SCRIPT.with_name("issue_board.py")


def snapshot(root: Path) -> dict[str, str]:
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = "link:" + os.readlink(path)
        elif path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            result[relative] = "dir"
    return result


class PersonalBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = self.enterContext(tempfile.TemporaryDirectory())
        self.base = Path(self.temp).resolve()
        self.env = {**os.environ, "IMPLEMENT_RFC_HOME": str(self.base / "home")}

    def source(self, name: str, *, configured: bool = False) -> Path:
        root = self.base / name
        root.mkdir()
        git(root, "init", "-b", "main")
        git(root, "config", "user.name", "fixture")
        git(root, "config", "user.email", "fixture@example.invalid")
        (root / "product.txt").write_text("product\n")
        if configured:
            write_context(root, token=name)
        git(root, "add", "--", "product.txt", *([".mask"] if configured else []))
        git(root, "commit", "-m", "Initial product")
        return root

    def run_cli(self, source: Path, command: str, *extra: str, script: Path = SCRIPT):
        result = subprocess.run([sys.executable, str(script), "--repo-root", str(source),
                                 "--json", *extra, command], env=self.env, capture_output=True,
                                text=True)
        return result, json.loads(result.stdout)

    def test_managed_tracker_public_setup_status_and_exact_source_footprint(self):
        source = self.source("fresh")
        before = snapshot(source)
        missing, body = self.run_cli(source, "status")
        self.assertEqual(missing.returncode, 2)
        self.assertFalse(body["ok"])
        self.assertFalse((self.base / "home").exists())

        created, binding = self.run_cli(source, "init")
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertEqual(binding["mode"], "personal")
        tracker = Path(binding["workflow_root"])
        self.assertTrue((tracker / ".git").is_dir())
        self.assertEqual(git(tracker, "log", "-1", "--format=%s"), "Initialize personal workflow tracker")
        self.assertEqual(git(tracker, "show", "--format=", "--name-only", "HEAD").splitlines(), [
            ".mask/skill-config/implement-rfc/project.json",
            ".mask/skill-config/implement-rfc/project.md",
            "docs/issues/NEXT_ID", "docs/issues/README.md", "docs/rfcs/README.md"])
        repeated, again = self.run_cli(source, "init")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(again["workflow_root"], binding["workflow_root"])
        observed, status = self.run_cli(source, "status")
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertEqual(status, binding)
        resolved = subprocess.run([sys.executable, str(CONFIG), "--repo-root", str(source),
                                   "--json"], env=self.env, capture_output=True, text=True)
        context = json.loads(resolved.stdout)
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        self.assertEqual(context["workflow_root"], binding["workflow_root"])
        self.assertEqual(snapshot(source), before)
        self.assertEqual(git(source, "status", "--porcelain=v1", "--untracked-files=all"), "")

    def test_worktrees_share_binding_and_other_clone_requires_explicit_tracker(self):
        source = self.source("origin")
        _, first = self.run_cli(source, "init")
        lane = self.base / "lane"
        git(source, "worktree", "add", "-b", "product-lane", str(lane))
        try:
            result, seen = self.run_cli(lane, "status")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(seen["source_common_dir"], first["source_common_dir"])
            self.assertEqual(seen["workflow_root"], first["workflow_root"])
            self.assertEqual(seen["source_root"], str(lane))
        finally:
            git(source, "worktree", "remove", "--force", str(lane))

        clone = self.base / "clone"
        subprocess.run(["git", "clone", "-q", str(source), str(clone)], check=True)
        absent, _ = self.run_cli(clone, "status")
        self.assertEqual(absent.returncode, 2)
        associated, second = self.run_cli(clone, "init", "--workflow-root", first["workflow_root"])
        self.assertEqual(associated.returncode, 0, associated.stderr)
        self.assertEqual(second["workflow_root"], first["workflow_root"])
        self.assertNotEqual(second["source_common_dir"], first["source_common_dir"])

    def test_explicit_project_override_and_unsafe_paths(self):
        source = self.source("configured", configured=True)
        project, old = self.run_cli(source, "status")
        self.assertEqual(project.returncode, 0, project.stderr)
        self.assertEqual(old["mode"], "project")
        _, personal = self.run_cli(source, "init")
        selected, current = self.run_cli(source, "status")
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual(current["mode"], "personal")
        override, direct = self.run_cli(source, "status", "--mode", "project")
        self.assertEqual(override.returncode, 0, override.stderr)
        self.assertEqual(direct["workflow_root"], str(source))
        self.assertEqual(direct["project"], "configured")
        wrong, _ = self.run_cli(source, "status", "--workflow-root", str(source))
        self.assertEqual(wrong.returncode, 2)
        self.assertEqual(git(source, "status", "--porcelain=v1", "--untracked-files=all"), "")

        fresh = self.source("unsafe")
        overlap, _ = self.run_cli(fresh, "init", "--workflow-root", str(fresh))
        self.assertEqual(overlap.returncode, 2)
        self.assertFalse((self.base / "home/bindings").joinpath(
            hashlib.sha256(str(fresh / ".git").encode()).hexdigest()[:24] + ".json").exists())
        self.env["IMPLEMENT_RFC_HOME"] = str(fresh / "state")
        bad_home, _ = self.run_cli(fresh, "init")
        self.assertEqual(bad_home.returncode, 2)
        self.assertFalse((fresh / "state").exists())

    def test_project_mode_under_personal_home_remains_usable(self):
        source = self.source("project-in-home", configured=True)
        self.env["IMPLEMENT_RFC_HOME"] = str(self.base)
        project, body = self.run_cli(source, "status")
        self.assertEqual(project.returncode, 0, project.stderr)
        self.assertEqual(body["mode"], "project")
        self.assertEqual(body["workflow_root"], str(source))
        self.assertEqual(body["runtime_root"], str(source))
        refused, _ = self.run_cli(source, "init")
        self.assertEqual(refused.returncode, 2)

    def test_supplied_empty_tracker_is_initialized_without_touching_source(self):
        source = self.source("supplied-source")
        tracker = self.base / "supplied-tracker"
        tracker.mkdir()
        git(tracker, "init", "-b", "main")
        before = snapshot(source)
        observed, _ = self.run_cli(source, "status", "--mode", "personal",
                                   "--workflow-root", str(tracker))
        self.assertEqual(observed.returncode, 2)
        self.assertFalse((self.base / "home").exists())
        created, body = self.run_cli(source, "init", "--workflow-root", str(tracker))
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertEqual(body["workflow_root"], str(tracker))
        self.assertEqual(snapshot(source), before)
        self.assertTrue((tracker / ".mask/skill-config/implement-rfc/project.json").is_file())

        other = self.source("unmanaged-source")
        unmanaged = self.base / "unmanaged-tracker"
        unmanaged.mkdir()
        git(unmanaged, "init", "-b", "main")
        (unmanaged / "unmanaged.txt").write_text("keep\n")
        preserved = snapshot(unmanaged)
        refused, _ = self.run_cli(other, "init", "--workflow-root", str(unmanaged))
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(snapshot(unmanaged), preserved)

    def test_reused_checkout_path_requires_explicit_clone_association(self):
        source = self.source("replacement")
        _, original = self.run_cli(source, "init")
        saved = self.base / "saved"
        source.rename(saved)
        subprocess.run(["git", "clone", "-q", str(saved), str(source)], check=True)
        absent, body = self.run_cli(source, "status", "--mode", "personal")
        self.assertEqual(absent.returncode, 2)
        self.assertFalse(body["ok"])
        associated, replacement = self.run_cli(source, "init", "--workflow-root",
                                                original["workflow_root"])
        self.assertEqual(associated.returncode, 0, associated.stderr)
        self.assertEqual(replacement["source_common_dir"], original["source_common_dir"])
        self.assertNotEqual((saved / ".git").stat().st_ino, (source / ".git").stat().st_ino)
        self.assertEqual(replacement["workflow_root"], original["workflow_root"])

    def test_board_allocation_uses_tracker_without_source_records(self):
        source = self.source("legacy", configured=True)
        (source / "docs/issues").mkdir(parents=True)
        (source / "docs/issues/NEXT_ID").write_text("SRC-0001\n")
        git(source, "add", "--", "docs/issues/NEXT_ID")
        git(source, "commit", "-m", "Seed board")
        _, binding = self.run_cli(source, "init")
        before = snapshot(source)
        result = subprocess.run([sys.executable, str(BOARD), "--repo-root", str(source),
                                 "allocate", "--reserve-for", "private-work", "--json"],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        allocated = json.loads(result.stdout)
        self.assertEqual(allocated["ids"], ["PRS-0001"])
        self.assertTrue((Path(binding["workflow_root"]) / "docs/issues/_reservations").is_dir())
        self.assertEqual(snapshot(source), before)

    def test_linked_local_state_external_git_dir_and_staged_content_refuse(self):
        for linked in ("bindings", "trackers", "runtime"):
            source = self.source("source-" + linked)
            home = self.base / ("home-" + linked)
            home.mkdir()
            (home / linked).symlink_to(source / (".git" if linked != "runtime" else ""),
                                       target_is_directory=True)
            self.env["IMPLEMENT_RFC_HOME"] = str(home)
            before = snapshot(source)
            refused, _ = self.run_cli(source, "init")
            self.assertEqual(refused.returncode, 2, linked)
            self.assertEqual(snapshot(source), before, linked)

        source = self.source("external-common")
        home = self.base / "external-home"
        (home / "bindings").mkdir(parents=True)
        tracker = self.base / "external-tracker"
        subprocess.run(["git", "init", "-b", "main", "--separate-git-dir",
                        str(home / "bindings/tracker-git"), str(tracker)],
                       check=True, capture_output=True)
        self.env["IMPLEMENT_RFC_HOME"] = str(home)
        before = snapshot(source)
        refused, _ = self.run_cli(source, "init", "--workflow-root", str(tracker))
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(snapshot(source), before)

        staged_source = self.source("staged-source")
        staged_tracker = self.base / "staged-tracker"
        staged_tracker.mkdir()
        git(staged_tracker, "init", "-b", "main")
        (staged_tracker / "unrelated.txt").write_text("retain\n")
        git(staged_tracker, "add", "--", "unrelated.txt")
        (staged_tracker / "unrelated.txt").unlink()
        before = snapshot(staged_tracker)
        refused, _ = self.run_cli(staged_source, "init", "--workflow-root", str(staged_tracker))
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(snapshot(staged_tracker), before)

    def test_malformed_binding_reports_json_error_without_fallback(self):
        source = self.source("malformed")
        self.run_cli(source, "init")
        binding = next((self.base / "home/bindings").glob("*.json"))
        data = json.loads(binding.read_text())
        data["tracker_root"] = None
        binding.write_text(json.dumps(data))
        result, body = self.run_cli(source, "status")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(body["ok"])
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
