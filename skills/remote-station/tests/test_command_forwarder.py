"""Public entry contract: the version-free command and the per-version entry script."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import install_command  # noqa: E402
from command_fixtures import (  # noqa: E402
    consumer, environment, forwarder_kinds, link_skill, probe_skill, run_direct, run_forwarder,
)
from station_fixtures import git  # noqa: E402


def in_git_repository(path: Path) -> bool:
    return subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, env=environment()).returncode == 0


@unittest.skipUnless(forwarder_kinds(), "no shell available for the installed forwarders")
class CommandForwarderTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.bin = self.base / "bin"
        install_command.install(self.bin)
        # A: this source version. B and its linked worktree: other pinned versions.
        self.a = consumer(self.base, "alpha", SKILL_DIR)
        self.b = consumer(self.base, "beta", probe_skill(self.base, "B"))
        self.worktree = self.base / "beta-worktree"
        git(self.b, "worktree", "add", "-q", "-b", "beta-lane", str(self.worktree))
        link_skill(self.worktree, probe_skill(self.base, "C"))

    def probe(self, kind: str, cwd: Path, *args: str, stdin: str = "") -> tuple[dict, subprocess.CompletedProcess[str]]:
        result = run_forwarder(kind, self.bin, cwd, *args, stdin=stdin)
        self.assertEqual(result.stdout.count("\n"), 1, result.stdout + result.stderr)
        return json.loads(result.stdout), result

    def test_each_checkout_runs_its_own_pinned_version(self) -> None:
        nested = self.b / "src" / "deep"
        nested.mkdir(parents=True)
        for kind in forwarder_kinds():
            with self.subTest(kind=kind):
                for cwd, version in ((self.b, "B"), (nested, "B"), (self.worktree, "C")):
                    observed, result = self.probe(kind, cwd)
                    self.assertEqual(observed["version"], version, cwd)
                    self.assertEqual(Path(observed["cwd"]).resolve(), cwd.resolve())
                    self.assertEqual(result.stderr, f"probe stderr {version}\n")
                status = run_forwarder(kind, self.bin, self.a / ".mask", "status", "--json")
                self.assertEqual(status.returncode, 0, status.stderr)
                self.assertEqual(json.loads(status.stdout)["mode"], "unmanaged")

    def test_arguments_stdio_and_exit_status_pass_through_unchanged(self) -> None:
        arguments = ["--fresh", "two words", "--machine=x-y", "status", "--exit", "7"]
        for kind in forwarder_kinds():
            with self.subTest(kind=kind):
                observed, result = self.probe(kind, self.b, *arguments, stdin="line one\nline two\n")
                self.assertEqual(observed["argv"], arguments)
                self.assertEqual(observed["stdin"], "line one\nline two\n")
                self.assertEqual(result.returncode, 7)

    def test_real_entry_matches_direct_invocation_for_status_refusal_and_launch(self) -> None:
        sub = self.a / "docs"
        sub.mkdir()
        bare = environment(without_runtimes=True)
        cases = (
            (("status", "--json"), environment(), 0),
            (("--machine", "Not_A_Token"), environment(), 2),
            # A launch with Codex and Claude absent from PATH reaches the lease, the
            # supervisor and the Codex probe, then refuses without starting a runtime.
            ((), bare, 2),
        )
        for kind in forwarder_kinds():
            for arguments, env, code in cases:
                with self.subTest(kind=kind, arguments=arguments):
                    direct = run_direct(self.a, sub, *arguments, env=env)
                    forwarded = run_forwarder(kind, self.bin, sub, *arguments, env=env)
                    self.assertEqual(direct.returncode, code, direct.stdout + direct.stderr)
                    self.assertEqual((forwarded.returncode, forwarded.stdout, forwarded.stderr),
                                     (direct.returncode, direct.stdout, direct.stderr))
        launch = run_direct(self.a, sub, env=bare)
        self.assertIn("starting or resuming unified station alpha-main-", launch.stdout)
        self.assertIn("Claude replies from alpha-main-", launch.stderr)
        self.assertIn("station refused: Codex CLI", launch.stderr)
        self.assertFalse((self.a / ".remote-station.json").exists())

    def test_refuses_outside_a_repository_and_without_the_skill_and_runs_nothing(self) -> None:
        outside = self.base / "not-a-repository"
        outside.mkdir()
        if in_git_repository(outside):
            self.skipTest("temporary directory is inside a Git repository")
        # A nested repository inside a consumer that has the skill must not fall back to it.
        nested = self.a / "vendor" / "nested"
        nested.mkdir(parents=True)
        git(nested, "init", "-q", "-b", "main")
        for kind in forwarder_kinds():
            with self.subTest(kind=kind):
                outside_result = run_forwarder(kind, self.bin, outside, "status", "--json")
                self.assertEqual(outside_result.returncode, 3)
                self.assertEqual(outside_result.stdout, "")
                self.assertIn("not inside a Git repository", outside_result.stderr)
                self.assertIn("not-a-repository", outside_result.stderr)
                missing = run_forwarder(kind, self.bin, nested, "status", "--json")
                self.assertEqual(missing.returncode, 4)
                self.assertEqual(missing.stdout, "")
                self.assertIn("has no remote-station skill", missing.stderr)
                self.assertIn("mask install remote-station", missing.stderr)
                self.assertIn("nested", missing.stderr)
                self.assertNotEqual(outside_result.stderr, missing.stderr)


class StationConfigRefusalTests(unittest.TestCase):
    """A consumer with only remote-station: station.json alone gates every launch."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = consumer(Path(temporary.name).resolve(), "solo", SKILL_DIR)
        self.config = self.root / ".mask/skill-config/remote-station/station.json"
        self.assertFalse((self.root / ".agents/skills/implement-rfc").exists())
        self.assertFalse((self.root / ".mask/skill-config/implement-rfc").exists())

    def test_station_json_alone_configures_status_and_launch(self) -> None:
        status = run_direct(self.root, self.root, "status", "--json")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertTrue(json.loads(status.stdout)["ok"])
        launch = run_direct(self.root, self.root, env=environment(without_runtimes=True))
        self.assertIn("starting or resuming unified station solo-main-", launch.stdout)
        self.assertIn("station refused: Codex CLI", launch.stderr)

    def test_missing_malformed_and_unknown_key_configuration_refuses_before_runtime(self) -> None:
        valid = self.config.read_text(encoding="utf-8")
        cases = (
            (None, "missing station configuration"),
            ("{not json", "invalid JSON"),
            (valid[:-1] + ', "moira": {}}', "unknown keys: moira"),
        )
        lock = self.root / ".git/implement-rfc-station-control.lock"
        for content, message in cases:
            with self.subTest(message=message):
                if content is None:
                    self.config.unlink(missing_ok=True)
                else:
                    self.config.write_text(content, encoding="utf-8")
                result = run_direct(self.root, self.root, env=environment(without_runtimes=True))
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)
                self.assertNotIn("starting or resuming", result.stdout)
                self.assertFalse(lock.exists())
                self.assertFalse((self.root / ".remote-station.json").exists())


if __name__ == "__main__":
    unittest.main()
