from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "install_command.py"
sys.path.insert(0, str(SCRIPT.parent))

import install_command  # noqa: E402

NAMES = ("launch_remote_station", "launch_remote_station.cmd")


class InstallCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.bin = Path(temporary.name).resolve() / "bin"

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--bin-dir", str(self.bin), "--json", *args],
                              capture_output=True, text=True)

    def test_writes_both_forwarders_and_reports_path_membership(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"] and report["changed"])
        self.assertFalse(report["on_path"])
        self.assertEqual([row["action"] for row in report["files"]], ["create", "create"])
        self.assertEqual(sorted(path.name for path in self.bin.iterdir()), sorted(NAMES))
        posix = (self.bin / NAMES[0]).read_bytes()
        windows = (self.bin / NAMES[1]).read_bytes()
        self.assertTrue(posix.startswith(b"#!/bin/sh\n"))
        self.assertNotIn(b"\r", posix)
        self.assertEqual(windows.count(b"\r\n"), windows.count(b"\n"))
        if os.name == "posix":
            self.assertTrue(os.access(self.bin / NAMES[0], os.X_OK))

    def test_forwarders_are_version_free_and_hold_no_station_logic(self) -> None:
        install_command.install(self.bin)
        for name in NAMES:
            text = (self.bin / name).read_text(encoding="utf-8")
            self.assertIn(install_command.MARKER, text)
            self.assertIn(".agents/skills/remote-station/scripts/launch_remote_station.py".replace("/", "\\" if name.endswith(".cmd") else "/"), text)
            self.assertIn("mask install remote-station", text)
            for absent in ("import ", "station.json", "station_config", str(SKILL_DIR)):
                self.assertNotIn(absent, text)
        self.assertIn("py -3", (self.bin / NAMES[1]).read_text(encoding="utf-8"))
        self.assertIn("exec python3", (self.bin / NAMES[0]).read_text(encoding="utf-8"))

    def test_reinstall_is_idempotent_and_updates_only_its_own_forwarders(self) -> None:
        install_command.install(self.bin)
        again = json.loads(self.run_cli().stdout)
        self.assertFalse(again["changed"])
        self.assertEqual([row["action"] for row in again["files"]], ["unchanged", "unchanged"])
        older = self.bin / NAMES[0]
        older.write_text("#!/bin/sh\n# " + install_command.MARKER + "\necho older\n", encoding="utf-8")
        preview = json.loads(self.run_cli("--dry-run").stdout)
        self.assertEqual(preview["files"][0]["action"], "update")
        self.assertIn(b"echo older", older.read_bytes())
        updated = json.loads(self.run_cli().stdout)
        self.assertTrue(updated["changed"])
        self.assertEqual(older.read_bytes(), install_command.forwarder_bytes(NAMES[0], "\n"))

    def test_refuses_to_overwrite_foreign_files_or_links(self) -> None:
        self.bin.mkdir()
        foreign = self.bin / NAMES[1]
        foreign.write_text("@echo off\necho someone else's command\n", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", json.loads(result.stdout)["error"])
        self.assertIn(b"someone else", foreign.read_bytes())
        self.assertFalse((self.bin / NAMES[0]).exists())
        foreign.unlink()
        target = self.bin / "elsewhere"
        target.write_text("x", encoding="utf-8")
        try:
            (self.bin / NAMES[0]).symlink_to(target)
        except OSError:
            self.skipTest("file symlinks unavailable")
        self.assertIn("link or non-file", json.loads(self.run_cli().stdout)["error"])
        self.assertEqual(target.read_text(encoding="utf-8"), "x")


if __name__ == "__main__":
    unittest.main()
