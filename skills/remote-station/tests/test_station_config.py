from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import station_config  # noqa: E402
from station_fixtures import CONFIG, git, init_repo, write_context  # noqa: E402

SCRIPT = SKILL_DIR / "scripts" / "station_config.py"


class ValidationTests(unittest.TestCase):
    def test_schema_and_loader_agree_on_keys(self) -> None:
        schema = json.loads((SKILL_DIR / "schemas" / "station-config.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(station_config.REQUIRED_KEYS))
        self.assertEqual(set(schema["properties"]), set(station_config.REQUIRED_KEYS))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["schema"]["const"], station_config.SCHEMA)

    def test_refuses_missing_unknown_and_malformed_values(self) -> None:
        self.assertEqual(station_config.validate(copy.deepcopy(CONFIG))["project"], "fixture")
        cases = []
        for key in station_config.REQUIRED_KEYS:
            config = copy.deepcopy(CONFIG)
            del config[key]
            cases.append((config, "lacks required keys: " + key))
        cases += [
            (dict(CONFIG, extra=1), "unknown keys: extra"),
            (dict(CONFIG, schema="implement-rfc.project.v2"), "schema must be"),
            (dict(CONFIG, session_prefix="Not A Token"), "session_prefix must be"),
            (dict(CONFIG, project=""), "project must be"),
            (dict(CONFIG, station_registry_doc="C:/registry.md"), "repository-relative"),
            (dict(CONFIG, workstreams={"win": {"branch": "w"}}), "containing 'main'"),
            (dict(CONFIG, workstreams={"main": {"branch": "main", "extra": 1}}), "unknown keys"),
            (dict(CONFIG, workstreams={"main": {"branch": "main", "platform": "bsd"}}), "unknown platform"),
            ([], "JSON object"),
        ]
        for config, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(station_config.StationConfigError, message):
                station_config.validate(config)

    def test_station_name_omits_platform_for_platform_bound_workstreams(self) -> None:
        config = dict(CONFIG, workstreams={
            "main": {"branch": "main"},
            "win": {"branch": "windows-lane", "platform": "win"},
        })
        self.assertEqual(station_config.station_name(config, "main", "mac"), "fx-main-mac")
        self.assertEqual(station_config.station_name(config, "win", "win", "example-win-host"), "fx-win-example-win-host")


class ResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "consumer"
        init_repo(self.root, token="consumer")
        self.enterContext(mock.patch.dict(os.environ))
        os.environ.pop(station_config.PROJECT_ROOT_ENV, None)

    def test_resolves_the_invoking_checkout_from_a_subdirectory(self) -> None:
        nested = self.root / "a" / "b"
        nested.mkdir(parents=True)
        context = station_config.resolve_context(cwd=nested)
        self.assertEqual(context.source_root, self.root)
        self.assertEqual(context.config["project"], "consumer")
        self.assertEqual(context.station_config_path, self.root / ".mask/skill-config/remote-station/station.json")
        # The skill's own location never selects a consumer.
        self.assertFalse(context.source_root.is_relative_to(SKILL_DIR))

    def test_explicit_root_must_be_the_worktree_root(self) -> None:
        (self.root / "sub").mkdir()
        with self.assertRaisesRegex(station_config.StationConfigError, "Git worktree root"):
            station_config.resolve_context(repo_root=self.root / "sub")
        with self.assertRaisesRegex(station_config.StationConfigError, "not a Git consumer"):
            station_config.resolve_context(repo_root=self.base)

    def test_missing_malformed_and_unknown_key_files_refuse(self) -> None:
        path = self.root / ".mask/skill-config/remote-station/station.json"
        path.unlink()
        with self.assertRaisesRegex(station_config.StationConfigError, "missing station configuration"):
            station_config.resolve_context(repo_root=self.root)
        path.write_text("{not json", encoding="utf-8")
        with self.assertRaisesRegex(station_config.StationConfigError, "invalid JSON"):
            station_config.resolve_context(repo_root=self.root)
        write_context(self.root, config=dict(CONFIG, origin_repo_name="consumer", extra=True))
        with self.assertRaisesRegex(station_config.StationConfigError, "unknown keys: extra"):
            station_config.resolve_context(repo_root=self.root)

    def test_origin_must_name_the_configured_repository(self) -> None:
        git(self.root, "remote", "add", "origin", "git@example.invalid:owner/other.git")
        with self.assertRaisesRegex(station_config.StationConfigError, "identity mismatch"):
            station_config.resolve_context(repo_root=self.root)
        git(self.root, "remote", "set-url", "origin", "https://example.invalid/owner/consumer.git")
        self.assertEqual(station_config.resolve_context(repo_root=self.root).config["project"], "consumer")

    def test_implement_rfc_project_json_alone_is_not_station_configuration(self) -> None:
        (self.root / ".mask/skill-config/remote-station/station.json").unlink()
        legacy = self.root / ".mask/skill-config/implement-rfc"
        legacy.mkdir(parents=True)
        (legacy / "project.json").write_text(json.dumps(dict(CONFIG, schema="implement-rfc.project.v2")), encoding="utf-8")
        with self.assertRaisesRegex(station_config.StationConfigError, "missing station configuration"):
            station_config.resolve_context(repo_root=self.root)

    def test_cli_reports_and_refuses_with_project_config_exit_code(self) -> None:
        ok = subprocess.run([sys.executable, "-B", str(SCRIPT), "--json"], cwd=self.root,
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["project"], "consumer")
        (self.root / ".mask/skill-config/remote-station/station.json").write_text("[]", encoding="utf-8")
        refused = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=self.root,
                                 capture_output=True, text=True)
        self.assertEqual(refused.returncode, 2)
        self.assertIn("error: station.json must be a JSON object", refused.stderr)


class SequentialConsumerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.a, self.b = self.base / "alpha", self.base / "beta"
        init_repo(self.a, token="alpha")
        init_repo(self.b, token="beta")

    def test_helpers_import_outside_any_repository(self) -> None:
        names = ("station_config", "codex_station", "launch_remote_station", "station_lease",
                 "remote_station_guard", "station_control", "station_hooks", "install_command")
        code = f"import sys; sys.path.insert(0, {str(SKILL_DIR / 'scripts')!r}); " + "; ".join(
            f"import {name}" for name in names)
        result = subprocess.run([sys.executable, "-c", code], cwd=self.base, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_helpers_keep_sequential_consumer_identity(self) -> None:
        import codex_station
        import launch_remote_station
        import remote_station_guard
        import station_lease
        for root in (self.a, self.b, self.a):
            selected = station_config.resolve_context(repo_root=root)
            self.assertEqual(station_lease._lock_path("station-writer", root, selected.config).name,
                             f"{root.name}-station-writer.lock")
            self.assertIn(root.name.title(), codex_station.station_bootstrap_text(selected.config))
            self.assertEqual(remote_station_guard._load_project(root)["project"], root.name)
            with mock.patch.dict(os.environ, {station_config.PROJECT_ROOT_ENV: str(self.b)}):
                station = launch_remote_station.StationContext(
                    root, "main", "main", root.name + "-main-mac", "macos", "lane-commit",
                    "project-integrator", root / ".remote-station.json", selected)
                document = launch_remote_station.station_document(station, station_id="fixture", codex=None)
                self.assertEqual(document["project"], root.name)


if __name__ == "__main__":
    unittest.main()
