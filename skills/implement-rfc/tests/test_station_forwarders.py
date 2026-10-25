"""The temporary implement-rfc station forwarders reach the sibling remote-station skill."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SIBLING = SKILL_DIR.parent / "remote-station"
NAMES = ("launch_remote_station.py", "station_control.py")
STATION = {
    "schema": "remote-station.config.v1",
    "project": "relay",
    "display_name": "Relay",
    "origin_repo_name": "relay",
    "session_prefix": "relay",
    "station_registry_doc": "docs/development/remote-stations.md",
    "workstreams": {"main": {"branch": "main"}},
}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def run(script: Path, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run([sys.executable, "-B", str(script), *args], cwd=cwd, capture_output=True,
                          text=True, env=env, timeout=60)


class ForwarderTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()

    @unittest.skipUnless((SIBLING / "SKILL.md").is_file(), "remote-station source is not beside implement-rfc")
    def test_installed_forwarders_match_the_sibling_skill(self) -> None:
        root = self.base / "relay"
        root.mkdir()
        git(root, "init", "-q", "-b", "main")
        git(root, "remote", "add", "origin", "https://example.invalid/owner/relay.git")
        config = root / ".mask/skill-config/remote-station/station.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps(STATION), encoding="utf-8")
        skills = root / ".agents/skills"
        skills.mkdir(parents=True)
        (skills / "implement-rfc").symlink_to(SKILL_DIR, target_is_directory=True)
        (skills / "remote-station").symlink_to(SIBLING, target_is_directory=True)
        old, new = skills / "implement-rfc/scripts", skills / "remote-station/scripts"
        sub = root / "docs"
        sub.mkdir()
        cases = (
            ("launch_remote_station.py", ("status", "--json"), 0),
            ("launch_remote_station.py", ("--machine", "Not_A_Token"), 2),
            ("station_control.py", ("status", "--repo-root", str(root), "--json"), 0),
        )
        for name, args, code in cases:
            with self.subTest(name=name, args=args):
                forwarded, direct = run(old / name, sub, *args), run(new / name, sub, *args)
                self.assertEqual(direct.returncode, code, direct.stdout + direct.stderr)
                self.assertEqual((forwarded.returncode, forwarded.stdout, forwarded.stderr),
                                 (direct.returncode, direct.stdout, direct.stderr))
        # Wrappers that load the old helper with runpy and call main(argv) keep working.
        loader = ("import runpy, sys; helper = runpy.run_path(sys.argv[1]); "
                  "raise SystemExit(helper['main'](['status', '--repo-root', sys.argv[2], '--json']))")
        loaded = subprocess.run([sys.executable, "-B", "-c", loader, str(old / "station_control.py"), str(root)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(loaded.returncode, 0, loaded.stderr)
        self.assertEqual(json.loads(loaded.stdout)["mode"], "unmanaged")

    def test_missing_sibling_names_the_install_command(self) -> None:
        scripts = self.base / "skills/implement-rfc/scripts"
        scripts.mkdir(parents=True)
        for name in NAMES:
            shutil.copy2(SKILL_DIR / "scripts" / name, scripts / name)
            result = run(scripts / name, self.base, "status", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("mask install remote-station", result.stderr)

    def test_forwarders_hold_no_station_logic(self) -> None:
        for name in NAMES:
            text = (SKILL_DIR / "scripts" / name).read_text(encoding="utf-8")
            self.assertLess(len(text.splitlines()), 60)
            for absent in ("station_config", "project_config", "subprocess", "codex", "claude"):
                self.assertNotIn(absent, text)
        stations = sorted(path.name for path in (SKILL_DIR / "scripts").glob("*station*"))
        self.assertEqual(stations, ["launch_remote_station.py", "station_control.py"])


if __name__ == "__main__":
    unittest.main()
