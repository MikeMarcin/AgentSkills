from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from station_fixtures import CONFIG, context_for, init_repo, git

SCRIPTS_ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import launch_remote_station as launcher  # noqa: E402


def arguments(**overrides: object) -> argparse.Namespace:
    values = {
        "workstream": "main",
        "machine": "",
        "authority": "lane-commit",
        "reattach": False,
        "new_claude_session": False,
        "fresh_station": False,
        "new_codex_session": False,
        "no_codex": False,
        "no_claude": False,
        "pair_codex": False,
        "no_server": False,
        "_supervise": False,
        "confirm_runtime_stopped": False,
        "permission_mode": "bypassPermissions",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class FakeRemoteClient:
    def __init__(self, responses: dict[str, list[dict]], diagnostic: str = "") -> None:
        self.responses = {method: list(values) for method, values in responses.items()}
        self.calls: list[tuple[str, dict]] = []
        self._diagnostic = diagnostic
        self.closed = False

    def request(
        self, method: str, params: dict, *, timeout: float | None = None
    ) -> dict:
        self.calls.append((method, params))
        values = self.responses.get(method)
        if not values:
            raise AssertionError(f"unexpected App Server request: {method}")
        return values.pop(0)

    def diagnostic(self) -> str:
        return self._diagnostic

    def close(self) -> None:
        self.closed = True


class LauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        # Station scenarios need explicit fixtures, not the host project's lanes.
        workstreams = {
            "main": {"branch": "main"},
            "win": {"branch": "windows-lane", "platform": "win"},
            "linux": {"branch": "linux-lane", "platform": "linux"},
        }
        self.project = {**CONFIG, "workstreams": workstreams}
        self.enterContext(mock.patch.object(launcher.lifecycle, 'locked', side_effect=lambda root: contextlib.nullcontext()))
        self.enterContext(mock.patch.object(launcher.lifecycle, 'load', side_effect=lambda root: {'mode': 'managed', 'endpoints': {}}))
        self.enterContext(mock.patch.object(launcher.lifecycle, 'activate'))
        self.enterContext(mock.patch.object(launcher.lifecycle, 'save'))
        self._temporary = tempfile.TemporaryDirectory()
        root = Path(self._temporary.name).resolve()
        self.selected = context_for(root, self.project)
        self.enterContext(mock.patch.object(launcher.station_config, "resolve_context", return_value=self.selected))
        self.context = launcher.StationContext(
            root=root,
            workstream="main",
            branch="main",
            name="fx-main-mac",
            environment="macos",
            authority="lane-commit",
            lease_role="project-integrator",
            station_file=root / ".remote-station.json",
            project_context=self.selected,
        )

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def windows_context(self) -> launcher.StationContext:
        return replace(
            self.context,
            name="fx-main-win",
            environment="windows-native",
        )

    def test_station_document_is_v2_and_accepts_unprovisioned_legacy_mode(self) -> None:
        document = launcher.station_document(
            self.context,
            station_id="stn-1234abcd",
            codex=None,
        )

        self.assertEqual(document["schema"], launcher.STATION_SCHEMA)
        self.assertIsNone(document["codex"])
        self.assertIsNone(document["claude"])

    def test_reads_only_a_well_formed_claude_bridge_session(self) -> None:
        fake_home = self.context.root / "home"
        with mock.patch.object(launcher.pathlib.Path, "home", return_value=fake_home):
            pointer = launcher.claude_bridge_pointer(self.context.root)
            pointer.parent.mkdir(parents=True)
            pointer.write_text(
                json.dumps({"sessionId": "session_Acta123"}),
                encoding="utf-8",
            )

            self.assertEqual(
                launcher.read_claude_bridge_session_id(self.context.root),
                "session_Acta123",
            )
            pointer.write_text(json.dumps({"sessionId": "wrong"}), encoding="utf-8")
            self.assertIsNone(launcher.read_claude_bridge_session_id(self.context.root))

    def test_fresh_claude_isolates_cross_worktree_bridge_pointers(self) -> None:
        target = self.context.root / "target" / "bridge-pointer.json"
        sibling = self.context.root / "sibling" / "bridge-pointer.json"
        target.parent.mkdir()
        sibling.parent.mkdir()
        target.write_text("old-target", encoding="utf-8")
        sibling.write_text("old-sibling", encoding="utf-8")

        with mock.patch.object(
            launcher,
            "claude_worktree_bridge_pointers",
            return_value=(target, sibling),
        ):
            isolation = launcher.ClaudeBridgeIsolation.begin(self.context.root)

        self.assertFalse(target.exists())
        self.assertFalse(sibling.exists())
        target.write_text("new-target", encoding="utf-8")
        isolation.session_started()

        self.assertEqual(target.read_text(encoding="utf-8"), "new-target")
        self.assertEqual(sibling.read_text(encoding="utf-8"), "old-sibling")
        self.assertFalse(
            target.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists()
        )
        self.assertFalse(
            sibling.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists()
        )

    def test_failed_fresh_claude_restores_every_bridge_pointer(self) -> None:
        target = self.context.root / "target" / "bridge-pointer.json"
        sibling = self.context.root / "sibling" / "bridge-pointer.json"
        target.parent.mkdir()
        sibling.parent.mkdir()
        target.write_text("old-target", encoding="utf-8")
        sibling.write_text("old-sibling", encoding="utf-8")

        with mock.patch.object(
            launcher,
            "claude_worktree_bridge_pointers",
            return_value=(target, sibling),
        ):
            isolation = launcher.ClaudeBridgeIsolation.begin(self.context.root)
        isolation.close()

        self.assertEqual(target.read_text(encoding="utf-8"), "old-target")
        self.assertEqual(sibling.read_text(encoding="utf-8"), "old-sibling")

    def test_fresh_claude_keeps_the_checkout_environment_without_its_session(self) -> None:
        """A preserved environment blocks a second one for the same folder."""
        target = self.context.root / "target" / "bridge-pointer.json"
        sibling = self.context.root / "sibling" / "bridge-pointer.json"
        target.parent.mkdir()
        sibling.parent.mkdir()
        old_target = {
            "sessionId": "session_OldMain123",
            "environmentId": "env_OldMain123",
            "source": "standalone",
            "pid": 1234,
            "procStart": "5678",
            "activeSessionIds": ["session_OldMain123"],
            "activeSessionIdsPersistedAt": 1,
        }
        target.write_text(json.dumps(old_target), encoding="utf-8")
        sibling.write_text(
            json.dumps({**old_target, "environmentId": "env_Sibling123"}),
            encoding="utf-8",
        )

        with mock.patch.object(
            launcher,
            "claude_worktree_bridge_pointers",
            return_value=(target, sibling),
        ), mock.patch.object(
            launcher, "claude_bridge_pointer", return_value=target
        ):
            isolation = launcher.ClaudeBridgeIsolation.begin(self.context.root)
            self.assertIsNone(launcher.read_claude_bridge_session_id(self.context.root))

        self.assertEqual(
            json.loads(target.read_text(encoding="utf-8")),
            {
                "sessionId": "",
                "environmentId": "env_OldMain123",
                "source": "standalone",
                "pid": 1234,
                "procStart": "5678",
            },
        )
        self.assertFalse(sibling.exists())
        new_target = {**old_target, "sessionId": "session_NewMain456", "pid": 4321}
        target.write_text(json.dumps(new_target), encoding="utf-8")
        isolation.session_started()

        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), new_target)
        self.assertTrue(sibling.exists())
        self.assertFalse(
            target.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists()
        )

    def test_failed_fresh_claude_replaces_the_environment_placeholder(self) -> None:
        target = self.context.root / "target" / "bridge-pointer.json"
        target.parent.mkdir()
        old_target = json.dumps({
            "sessionId": "session_OldMain123",
            "environmentId": "env_OldMain123",
            "source": "standalone",
        })
        target.write_text(old_target, encoding="utf-8")

        with mock.patch.object(
            launcher, "claude_worktree_bridge_pointers", return_value=(target,)
        ), mock.patch.object(
            launcher, "claude_bridge_pointer", return_value=target
        ):
            isolation = launcher.ClaudeBridgeIsolation.begin(self.context.root)
        self.assertTrue(target.exists())
        isolation.close()

        self.assertEqual(target.read_text(encoding="utf-8"), old_target)
        self.assertFalse(
            target.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists()
        )

    def test_records_a_new_exact_claude_session_from_the_bridge(self) -> None:
        recorded: list[str] = []
        stop = launcher.threading.Event()
        with mock.patch.object(
            launcher,
            "read_claude_bridge_session_id",
            return_value="session_NewActa456",
        ):
            launcher.watch_for_claude_session(
                self.context,
                previous_session_id="session_OldMain123",
                record_session=recorded.append,
                stop=stop,
            )

        self.assertEqual(recorded, ["session_NewActa456"])

    def test_watch_outlives_the_grace_and_records_a_late_session(self) -> None:
        """`--spawn session` creates the session on first connection, not at launch."""
        recorded: list[str] = []
        released: list[str] = []
        stop = launcher.threading.Event()
        answers = iter([None, None, None, "session_LateActa789"])
        with mock.patch.object(
            launcher, "CLAUDE_BRIDGE_ISOLATION_GRACE_SECONDS", 0.0
        ), mock.patch.object(
            launcher, "CLAUDE_SESSION_RECORD_POLL_SECONDS", 0.001
        ), mock.patch.object(
            launcher,
            "read_claude_bridge_session_id",
            side_effect=lambda _root: next(answers),
        ):
            launcher.watch_for_claude_session(
                self.context,
                previous_session_id=None,
                record_session=recorded.append,
                stop=stop,
                grace_elapsed=lambda: released.append("released"),
            )

        self.assertEqual(recorded, ["session_LateActa789"])
        self.assertEqual(released, ["released"])

    def test_watch_ends_without_a_session_only_when_claude_stops(self) -> None:
        recorded: list[str] = []
        released: list[str] = []
        stop = launcher.threading.Event()
        polls: list[int] = []

        def never(_root: launcher.pathlib.Path) -> None:
            polls.append(1)
            if len(polls) == 5:
                stop.set()
            return None

        with mock.patch.object(
            launcher, "CLAUDE_BRIDGE_ISOLATION_GRACE_SECONDS", 0.0
        ), mock.patch.object(
            launcher, "CLAUDE_SESSION_RECORD_POLL_SECONDS", 0.001
        ), mock.patch.object(
            launcher, "read_claude_bridge_session_id", side_effect=never
        ):
            launcher.watch_for_claude_session(
                self.context,
                previous_session_id=None,
                record_session=recorded.append,
                stop=stop,
                grace_elapsed=lambda: released.append("released"),
            )

        self.assertEqual(recorded, [])
        self.assertEqual(released, ["released"])
        self.assertEqual(len(polls), 5)

    def test_releasing_siblings_keeps_the_stale_target_hidden(self) -> None:
        target = self.context.root / "target" / "bridge-pointer.json"
        sibling = self.context.root / "sibling" / "bridge-pointer.json"
        target.parent.mkdir()
        sibling.parent.mkdir()
        target.write_text("old-target", encoding="utf-8")
        sibling.write_text("old-sibling", encoding="utf-8")

        with mock.patch.object(
            launcher,
            "claude_worktree_bridge_pointers",
            return_value=(target, sibling),
        ), mock.patch.object(
            launcher, "claude_bridge_pointer", return_value=target
        ):
            isolation = launcher.ClaudeBridgeIsolation.begin(self.context.root)
        isolation.release_siblings()

        self.assertFalse(target.exists())
        self.assertTrue(target.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists())
        self.assertEqual(sibling.read_text(encoding="utf-8"), "old-sibling")
        self.assertFalse(
            sibling.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists()
        )

        target.write_text("new-target", encoding="utf-8")
        isolation.session_started()
        self.assertEqual(target.read_text(encoding="utf-8"), "new-target")
        self.assertFalse(
            target.with_name(launcher.CLAUDE_BRIDGE_BACKUP_NAME).exists()
        )

    def test_workstream_is_inferred_from_the_station_file(self) -> None:
        self.context.station_file.write_text(
            json.dumps({"schema": launcher.STATION_SCHEMA, "workstream": "linux"}),
            encoding="utf-8",
        )
        self.assertEqual(
            launcher.infer_workstream(self.context.station_file, "unrelated", self.project),
            "linux",
        )

    def test_workstream_is_inferred_from_the_branch(self) -> None:
        for name, workstream in self.project["workstreams"].items():
            self.assertEqual(
                launcher.infer_workstream(
                    self.context.station_file, workstream["branch"], self.project
                ),
                name,
            )

    def test_machine_suffix_is_inferred_from_the_station_file(self) -> None:
        """A relaunch keeps the recorded name without retyping `--machine`."""
        self.context.station_file.write_text(
            json.dumps(
                {"schema": launcher.STATION_SCHEMA, "station": "fx-win-example-win-host"}
            ),
            encoding="utf-8",
        )
        self.assertEqual(
            launcher.infer_machine(self.context.station_file, "fx-win"), "example-win-host"
        )

    def test_a_station_recorded_without_a_suffix_infers_none(self) -> None:
        self.context.station_file.write_text(
            json.dumps({"schema": launcher.STATION_SCHEMA, "station": "fx-win"}),
            encoding="utf-8",
        )
        self.assertEqual(launcher.infer_machine(self.context.station_file, "fx-win"), "")
        self.assertEqual(
            launcher.infer_machine(self.context.station_file, "fx-linux"), ""
        )

    def test_a_malformed_recorded_suffix_is_not_inferred(self) -> None:
        for recorded in ("fx-win-ExampleWinHost", "fx-win-", "fx-win-a b", 17, None):
            with self.subTest(recorded=recorded):
                self.context.station_file.write_text(
                    json.dumps(
                        {"schema": launcher.STATION_SCHEMA, "station": recorded}
                    ),
                    encoding="utf-8",
                )
                self.assertEqual(
                    launcher.infer_machine(self.context.station_file, "fx-win"), ""
                )

    def test_no_station_file_infers_no_machine(self) -> None:
        self.assertEqual(
            launcher.infer_machine(self.context.station_file, "fx-win"), ""
        )

    def resolve(self, argv: list[str]) -> launcher.StationContext:
        """`resolve_context` for a checkout on the `win` workstream's branch."""
        workstream = self.project["workstreams"]["win"]

        def fake_git(root: object, *command: str) -> str:
            if command[0] == "rev-parse":
                return str(self.context.root)
            if command[0] == "remote":
                return f"git@github.com:owner/{self.project['origin_repo_name']}.git"
            return workstream["branch"]

        with (
            mock.patch.object(launcher, "run_git", side_effect=fake_git),
            mock.patch.object(launcher, "host_platform", return_value=("win", "windows-native")),
        ):
            return launcher.resolve_context(launcher.parse_arguments(argv))

    def test_a_recorded_machine_suffix_survives_an_argument_free_relaunch(self) -> None:
        """The refusal this fixes: a relaunch recomputed a name its own task
        did not carry, kept the recorded task id, and then would not rename it."""
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": launcher.STATION_SCHEMA,
                    "workstream": "win",
                    "station": f"{self.project['session_prefix']}-win-example-win-host",
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(
            self.resolve([]).name,
            f"{self.project['session_prefix']}-win-example-win-host",
        )

    def test_fresh_station_takes_the_canonical_name_again(self) -> None:
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": launcher.STATION_SCHEMA,
                    "workstream": "win",
                    "station": f"{self.project['session_prefix']}-win-example-win-host",
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(
            self.resolve(["--fresh-station"]).name,
            f"{self.project['session_prefix']}-win",
        )

    def test_an_explicit_machine_that_contradicts_the_record_refuses(self) -> None:
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": launcher.STATION_SCHEMA,
                    "workstream": "win",
                    "station": f"{self.project['session_prefix']}-win-example-win-host",
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(launcher.LaunchRefusal, "disagrees"):
            self.resolve(["--machine", "nuc"])
        # The same token the record already carries is not a contradiction.
        self.assertEqual(
            self.resolve(["--machine", "example-win-host"]).name,
            f"{self.project['session_prefix']}-win-example-win-host",
        )
        # `--fresh-station` is how a station is deliberately renamed.
        self.assertEqual(
            self.resolve(["--fresh-station", "--machine", "nuc"]).name,
            f"{self.project['session_prefix']}-win-nuc",
        )

    def test_the_resolved_machine_reaches_the_supervised_child(self) -> None:
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": launcher.STATION_SCHEMA,
                    "workstream": "win",
                    "station": f"{self.project['session_prefix']}-win-example-win-host",
                }
            ),
            encoding="utf-8",
        )
        parsed = launcher.parse_arguments([])
        workstream = self.project["workstreams"]["win"]

        def fake_git(root: object, *command: str) -> str:
            if command[0] == "rev-parse":
                return str(self.context.root)
            if command[0] == "remote":
                return f"git@github.com:owner/{self.project['origin_repo_name']}.git"
            return workstream["branch"]

        with (
            mock.patch.object(launcher, "run_git", side_effect=fake_git),
            mock.patch.object(launcher, "host_platform", return_value=("win", "windows-native")),
        ):
            launcher.resolve_context(parsed)

        command = launcher.internal_supervisor_arguments(parsed)
        self.assertEqual(command[command.index("--machine") + 1], "example-win-host")

    def test_unknown_branch_without_a_station_file_refuses_to_guess(self) -> None:
        with self.assertRaisesRegex(launcher.LaunchRefusal, "cannot infer a workstream"):
            launcher.infer_workstream(self.context.station_file, "feature/x", self.project)

    def test_omitted_workstream_resolves_from_the_checkout(self) -> None:
        """`launch_remote_station.py` with no argument is the documented command."""
        parsed = launcher.parse_arguments([])
        self.assertIsNone(parsed.workstream)
        parsed = launcher.parse_arguments(["linux"])
        self.assertEqual(parsed.workstream, "linux")

    def test_main_only_project_does_not_require_platform_workstreams(self) -> None:
        project = {**self.project, "workstreams": {"main": {"branch": "main"}}}
        self.assertIsNone(launcher.parse_arguments([]).workstream)
        self.assertEqual(launcher.parse_arguments(["main"]).workstream, "main")
        self.assertEqual(launcher.infer_workstream(self.context.station_file, "main", project), "main")
        with self.assertRaisesRegex(launcher.LaunchRefusal, "cannot infer a workstream"):
            launcher.infer_workstream(self.context.station_file, "linux-lane", project)
        with mock.patch.object(launcher.station_config, "resolve_context", return_value=context_for(self.context.root, project)), mock.patch.object(launcher, "run_git", return_value="Fixture"):
            with self.assertRaisesRegex(launcher.LaunchRefusal, "unknown workstream"):
                launcher.resolve_context(launcher.parse_arguments(["linux"]))

    def test_supervisor_migrates_v1_and_preserves_station_id(self) -> None:
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": "implement-rfc.remote-station.v1",
                    "station_id": "stn-1234abcd",
                }
            ),
            encoding="utf-8",
        )
        completed = subprocess.CompletedProcess(["claude"], 0)
        codex = {
            "thread_id": "thr-station-1234",
            "thread_name": self.context.name,
            "cli_version": "0.151.0",
        }
        session = contextlib.nullcontext(codex)

        with (
            mock.patch.object(launcher, "provision_codex", return_value=session),
            mock.patch.object(launcher.subprocess, "run", return_value=completed) as run,
        ):
            result = launcher.supervise(arguments(), self.context)

        self.assertEqual(result, 0)
        migrated = json.loads(self.context.station_file.read_text(encoding="utf-8"))
        self.assertEqual(migrated["schema"], launcher.STATION_SCHEMA)
        self.assertEqual(migrated["station_id"], "stn-1234abcd")
        self.assertEqual(migrated["codex"], codex)
        self.assertIsNone(migrated["claude"])
        self.assertEqual(
            run.call_args.args[0][0:2],
            ["claude", "remote-control"],
        )

    def test_exact_session_id_is_forwarded_only_to_claude(self) -> None:
        command = launcher.claude_command(
            arguments(reattach=True),
            self.context,
            reattach=True,
            session_id="session_Acta123",
        )
        self.assertEqual(command[-2:], ["--session-id", "session_Acta123"])
        self.assertNotIn("--continue", command)
        self.assertNotIn("--name", command)
        self.assertNotIn("--spawn", command)

    def test_normal_start_reattaches_then_falls_back_to_fresh_claude(self) -> None:
        unavailable = subprocess.CompletedProcess(["claude"], 1)
        fresh = subprocess.CompletedProcess(["claude"], 0)
        with (
            mock.patch.object(
                launcher.subprocess,
                "run",
                side_effect=[unavailable, fresh],
            ) as run,
            mock.patch.object(launcher.time, "monotonic", return_value=10.0),
        ):
            result = launcher.run_claude(
                arguments(),
                self.context,
                session_id="session_Acta123",
            )

        self.assertEqual(result, 0)
        self.assertIn("--session-id", run.call_args_list[0].args[0])
        self.assertNotIn("--session-id", run.call_args_list[1].args[0])

    def test_continue_is_strict_and_does_not_fall_back(self) -> None:
        unavailable = subprocess.CompletedProcess(["claude"], 1)
        with mock.patch.object(
            launcher.subprocess,
            "run",
            return_value=unavailable,
        ) as run:
            result = launcher.run_claude(
                arguments(reattach=True),
                self.context,
                session_id="session_Acta123",
            )

        self.assertEqual(result, 1)
        self.assertEqual(run.call_count, 1)
        self.assertIn("--session-id", run.call_args.args[0])

    def test_continue_without_a_recorded_session_refuses(self) -> None:
        with self.assertRaisesRegex(launcher.LaunchRefusal, "no recorded Claude"):
            launcher.run_claude(arguments(reattach=True), self.context)

    def test_normal_start_without_a_recorded_session_starts_fresh(self) -> None:
        fresh = subprocess.CompletedProcess(["claude"], 0)
        with mock.patch.object(
            launcher.subprocess,
            "run",
            return_value=fresh,
        ) as run:
            result = launcher.run_claude(arguments(), self.context)

        self.assertEqual(result, 0)
        self.assertNotIn("--session-id", run.call_args.args[0])
        self.assertNotIn("--continue", run.call_args.args[0])
        self.assertEqual(run.call_args.args[0][:2], ["claude", "remote-control"])

    def test_explicit_new_claude_session_skips_reattachment(self) -> None:
        fresh = subprocess.CompletedProcess(["claude"], 0)
        with mock.patch.object(
            launcher.subprocess,
            "run",
            return_value=fresh,
        ) as run:
            result = launcher.run_claude(
                arguments(new_claude_session=True),
                self.context,
            )

        self.assertEqual(result, 0)
        self.assertNotIn("--continue", run.call_args.args[0])

    def test_running_claude_failure_does_not_create_a_new_session(self) -> None:
        stopped = subprocess.CompletedProcess(["claude"], 1)
        with (
            mock.patch.object(
                launcher.subprocess,
                "run",
                return_value=stopped,
            ) as run,
            mock.patch.object(launcher.time, "monotonic", side_effect=[10.0, 41.0]),
        ):
            result = launcher.run_claude(
                arguments(),
                self.context,
                session_id="session_Acta123",
            )

        self.assertEqual(result, 1)
        self.assertEqual(run.call_count, 1)

    def test_interrupted_reattachment_does_not_create_a_new_session(self) -> None:
        interrupted = subprocess.CompletedProcess(["claude"], -2)
        with (
            mock.patch.object(
                launcher.subprocess,
                "run",
                return_value=interrupted,
            ) as run,
            mock.patch.object(launcher.time, "monotonic", side_effect=[10.0, 10.1]),
        ):
            result = launcher.run_claude(
                arguments(),
                self.context,
                session_id="session_Acta123",
            )

        self.assertEqual(result, -2)
        self.assertEqual(run.call_count, 1)

    def test_outer_process_wraps_the_unified_supervisor_in_the_lease(self) -> None:
        completed = subprocess.CompletedProcess(["lease"], 0)
        with mock.patch.object(launcher.subprocess, "run", return_value=completed) as run:
            result = launcher.run_under_lease(
                arguments(reattach=True, pair_codex=True),
                self.context,
            )

        self.assertEqual(result, 0)
        command = run.call_args.args[0]
        self.assertIn("station_lease.py", command[1])
        self.assertIn("--_supervise", command)
        self.assertIn("--pair-codex", command)
        self.assertIn("--continue", command)
        self.assertEqual(command[command.index("--station") + 1], self.context.name)

    def test_pending_fresh_recovery_finishes_before_the_new_lease_starts(self) -> None:
        import station_control
        order = []
        with (
            mock.patch.object(launcher.lifecycle, 'load', return_value={'mode': 'transferring'}),
            mock.patch.object(launcher.lifecycle, 'validate'),
            mock.patch.object(station_control, 'takeover', side_effect=lambda *a, **kw: order.append('recover')) as takeover,
            mock.patch.object(launcher.subprocess, 'run', side_effect=lambda *a, **kw: (
                order.append('lease') or subprocess.CompletedProcess([], 0))),
        ):
            self.assertEqual(launcher.run_under_lease(arguments(
                new_codex_session=True, new_claude_session=True,
                confirm_runtime_stopped=True), self.context), 0)
        self.assertEqual(order, ['recover', 'lease'])
        takeover.assert_called_once_with(self.context.root, stop_previous=True,
                                         confirm_runtime_stopped=True)

    def test_unproven_fresh_recovery_does_not_start_a_new_supervisor(self) -> None:
        import station_control
        output = io.StringIO()
        with (
            mock.patch.object(launcher.lifecycle, 'load', return_value={'mode': 'transferring'}),
            mock.patch.object(launcher.lifecycle, 'validate'),
            mock.patch.object(station_control, 'takeover', side_effect=launcher.lifecycle.LifecycleError('runtime unproven')),
            mock.patch.object(launcher.subprocess, 'run') as run,
            contextlib.redirect_stderr(output),
        ):
            self.assertEqual(launcher.run_under_lease(arguments(
                new_codex_session=True, new_claude_session=True), self.context), 2)
        run.assert_not_called()
        self.assertIn('--fresh --confirm-runtime-stopped', output.getvalue())

    def test_pending_normal_or_partial_launch_requires_full_context_replacement(self) -> None:
        import station_control
        for options in ({}, {'new_codex_session': True}, {'new_claude_session': True}):
            with (
                self.subTest(options=options),
                mock.patch.object(launcher.lifecycle, 'load', return_value={'mode': 'transferring'}),
                mock.patch.object(launcher.lifecycle, 'validate'),
                mock.patch.object(station_control, 'takeover') as takeover,
                mock.patch.object(launcher.subprocess, 'run') as run,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(launcher.run_under_lease(arguments(**options), self.context), 2)
            takeover.assert_not_called()
            run.assert_not_called()

    def test_pending_identity_mismatch_refuses_before_runtime_stop(self) -> None:
        import station_control
        with (
            mock.patch.object(launcher.lifecycle, 'load', return_value={'mode': 'transferring'}),
            mock.patch.object(launcher.lifecycle, 'validate', side_effect=launcher.lifecycle.LifecycleError('wrong identity')),
            mock.patch.object(station_control, 'takeover') as takeover,
            mock.patch.object(launcher.subprocess, 'run') as run,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(launcher.run_under_lease(arguments(fresh_station=True), self.context), 2)
        takeover.assert_not_called()
        run.assert_not_called()

    def test_launch_stop_confirmation_requires_both_fresh_contexts(self) -> None:
        parsed = launcher.parse_arguments(['--fresh', '--confirm-runtime-stopped'])
        self.assertTrue(parsed.confirm_runtime_stopped)
        # Confirmation belongs to the pre-lease recovery, never the new child.
        self.assertNotIn('--confirm-runtime-stopped', launcher.internal_supervisor_arguments(parsed))
        for flags in ([], ['--fresh', 'codex'], ['--fresh', 'claude'], ['--fresh', '--no-codex']):
            with self.subTest(flags=flags), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                launcher.parse_arguments([*flags, '--confirm-runtime-stopped'])

    def test_new_claude_session_is_forwarded_to_the_supervisor(self) -> None:
        command = launcher.internal_supervisor_arguments(
            arguments(new_claude_session=True)
        )

        self.assertIn("--new-claude-session", command)
        self.assertNotIn("--continue", command)

    def test_fresh_station_is_forwarded_to_the_supervisor(self) -> None:
        command = launcher.internal_supervisor_arguments(
            arguments(fresh_station=True, new_claude_session=True)
        )

        self.assertIn("--fresh-station", command)
        self.assertNotIn("--continue", command)

    def test_fresh_station_archives_the_recorded_task_before_provisioning(self) -> None:
        """Starting over leaves nothing the new provisioning could adopt."""
        context = self.windows_context()
        client = FakeRemoteClient({})
        app_server = mock.MagicMock()
        app_server.return_value.__enter__.return_value = client

        with (
            mock.patch.object(launcher, "codex_cli_version", return_value="0.151.0"),
            mock.patch.object(launcher, "AppServerClient", app_server),
            mock.patch.object(launcher, "start_codex_desktop_app"),
            mock.patch.object(
                launcher,
                "release_named_threads",
                return_value=["thr-recorded archived"],
            ) as release,
            mock.patch.object(
                launcher,
                "provision_named_thread",
                return_value="thr-station-5678",
            ) as provision,
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                with launcher.provision_codex(
                    context,
                    existing={"codex": {"thread_id": "thr-recorded"}},
                    pair=False,
                    fresh=True,
                ) as provisioned:
                    self.assertEqual(provisioned["thread_id"], "thr-station-5678")

        release.assert_called_once_with(
            client,
            cwd=context.root,
            name=context.name,
            recorded_thread_id="thr-recorded",
        )
        self.assertIn("thr-recorded archived", output.getvalue())
        # The recorded id is forgotten, so provisioning creates rather than adopts.
        provision.assert_called_once_with(
            client,
            cwd=context.root,
            name=context.name,
            expected_thread_id=None,
            context=context.project_context,
            new_session=False,
        )

    def test_a_normal_relaunch_archives_nothing(self) -> None:
        context = self.windows_context()
        client = FakeRemoteClient({})
        app_server = mock.MagicMock()
        app_server.return_value.__enter__.return_value = client

        with (
            mock.patch.object(launcher, "codex_cli_version", return_value="0.151.0"),
            mock.patch.object(launcher, "AppServerClient", app_server),
            mock.patch.object(launcher, "start_codex_desktop_app"),
            mock.patch.object(launcher, "release_named_threads") as release,
            mock.patch.object(
                launcher,
                "provision_named_thread",
                return_value="thr-recorded",
            ) as provision,
        ):
            with launcher.provision_codex(
                context,
                existing={"codex": {"thread_id": "thr-recorded"}},
                pair=False,
            ):
                pass

        release.assert_not_called()
        self.assertEqual(
            provision.call_args.kwargs["expected_thread_id"], "thr-recorded"
        )

    def test_fresh_station_keeps_neither_station_id_nor_claude_session(self) -> None:
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": launcher.STATION_SCHEMA,
                    "station_id": "stn-1234abcd",
                    "codex": {"thread_id": "thr-recorded"},
                    "claude": {"session_id": "session_Old123"},
                }
            ),
            encoding="utf-8",
        )
        codex = {
            "thread_id": "thr-station-5678",
            "thread_name": self.context.name,
            "cli_version": "0.151.0",
        }

        with (
            mock.patch.object(
                launcher,
                "provision_codex",
                return_value=contextlib.nullcontext(codex),
            ) as provision,
            mock.patch.object(
                launcher.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(["claude"], 0),
            ) as run,
        ):
            result = launcher.supervise(
                arguments(fresh_station=True, new_claude_session=True), self.context
            )

        self.assertEqual(result, 0)
        # provision_codex still sees the recorded file, because it is what
        # tells it which task to archive.
        self.assertEqual(
            provision.call_args.kwargs["existing"]["station_id"], "stn-1234abcd"
        )
        self.assertIs(provision.call_args.kwargs["fresh"], True)
        written = json.loads(self.context.station_file.read_text(encoding="utf-8"))
        self.assertNotEqual(written["station_id"], "stn-1234abcd")
        self.assertEqual(written["codex"], codex)
        self.assertIsNone(written["claude"])
        self.assertEqual(
            run.call_args.args[0][0:2],
            ["claude", "remote-control"],
        )

    def test_pairing_is_explicit_and_follows_local_provisioning(self) -> None:
        client = FakeRemoteClient(
            {
                "remoteControl/status/read": [
                    {"status": "connecting"},
                    {"status": "connecting"},
                    {"status": "connected"},
                ],
                "remoteControl/pairing/start": [
                    {
                        "pairingCode": "do-not-print-this",
                        "manualPairingCode": "ABCD-EFGH",
                        "expiresAt": 1000,
                    }
                ],
                "remoteControl/pairing/status": [{"claimed": True}],
            }
        )
        with (
            mock.patch.object(launcher, "codex_cli_version", return_value="0.151.0"),
            mock.patch.object(
                launcher, "connect_codex_app_server", return_value=client
            ),
            mock.patch.object(
                launcher,
                "provision_named_thread",
                return_value="thr-station-1234",
            ),
            mock.patch.object(launcher.time, "time", return_value=700),
            mock.patch.object(launcher.time, "monotonic", return_value=0),
            mock.patch.object(launcher, "CODEX_REMOTE_CONNECT_WAIT_SECONDS", 0),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                with launcher.provision_codex(
                    self.context,
                    existing={},
                    pair=True,
                ) as provisioned:
                    self.assertEqual(provisioned["thread_id"], "thr-station-1234")

        self.assertEqual(
            [method for method, _ in client.calls],
            [
                "remoteControl/status/read",
                "remoteControl/status/read",
                "remoteControl/pairing/start",
                "remoteControl/pairing/status",
                "remoteControl/status/read",
            ],
        )
        self.assertEqual(client.calls[0][1], {})
        self.assertEqual(client.calls[2][1], {"manualCode": True})
        self.assertIn("ABCD-EFGH", output.getvalue())
        self.assertIn("different controller device", output.getvalue())
        self.assertNotIn("do-not-print-this", output.getvalue())
        self.assertTrue(client.closed)

    def test_pairing_refuses_an_already_errored_connection(self) -> None:
        client = FakeRemoteClient(
            {"remoteControl/status/read": [{"status": "errored"}]},
            diagnostic="HTTP 409: Remote app server already online",
        )
        with self.assertRaisesRegex(launcher.LaunchRefusal, "HTTP 409"):
            launcher.ensure_codex_remote(client, pair=True)

        self.assertEqual(len(client.calls), 1)

    def test_pairing_refuses_a_missing_manual_code(self) -> None:
        with self.assertRaisesRegex(launcher.LaunchRefusal, "manual pairing code"):
            launcher.codex_pairing_details(
                {"pairingCode": "machine-protocol-value"}
            )

    def test_unpaired_remote_is_not_reported_ready(self) -> None:
        client = FakeRemoteClient(
            {
                "remoteControl/status/read": [
                    {"status": "connecting"},
                    {"status": "connecting"},
                ],
            }
        )
        with (
            mock.patch.object(launcher.time, "monotonic", return_value=0),
            mock.patch.object(launcher, "CODEX_REMOTE_CONNECT_WAIT_SECONDS", 0),
        ):
            with self.assertRaisesRegex(launcher.LaunchRefusal, "--pair-codex"):
                launcher.ensure_codex_remote(client, pair=False)

    def test_malformed_remote_status_is_refused(self) -> None:
        client = FakeRemoteClient(
            {"remoteControl/status/read": [{"status": "unexpected"}]}
        )

        with self.assertRaisesRegex(launcher.LaunchRefusal, "malformed"):
            launcher.ensure_codex_remote(client, pair=False)

    def test_missing_remote_control_rpc_preserves_actionable_diagnostic(self) -> None:
        client = mock.MagicMock()
        client.request.side_effect = launcher.CodexStationError(
            "Codex App Server rejected remoteControl/status/read: method not found"
        )
        with (
            mock.patch.object(launcher, "codex_cli_version", return_value="0.151.0"),
            mock.patch.object(
                launcher, "connect_codex_app_server", return_value=client
            ),
        ):
            with self.assertRaisesRegex(launcher.LaunchRefusal, "method not found"):
                with launcher.provision_codex(
                    self.context,
                    existing={},
                    pair=False,
                ):
                    pass

    def test_native_windows_uses_short_lived_stdio_provisioning_only(self) -> None:
        context = self.windows_context()
        client = FakeRemoteClient({})
        app_server = mock.MagicMock()
        app_server.return_value.__enter__.return_value = client

        with (
            mock.patch.object(launcher, "codex_cli_version", return_value="0.151.0"),
            mock.patch.object(launcher, "AppServerClient", app_server),
            mock.patch.object(launcher, "start_codex_desktop_app") as start_app,
            mock.patch.object(launcher, "connect_codex_app_server") as connect,
            mock.patch.object(launcher, "ensure_codex_remote") as ensure_remote,
            mock.patch.object(
                launcher,
                "provision_named_thread",
                return_value="thr-station-1234",
            ) as provision,
        ):
            with launcher.provision_codex(
                context,
                existing={},
                pair=False,
            ) as provisioned:
                self.assertEqual(provisioned["thread_id"], "thr-station-1234")
                app_server.return_value.__exit__.assert_called_once()

        start_app.assert_called_once_with(context)
        app_server.assert_called_once_with(cwd=context.root, context=context.project_context)
        provision.assert_called_once_with(
            client,
            cwd=context.root,
            name=context.name,
            expected_thread_id=None,
            context=context.project_context,
            new_session=False,
        )
        connect.assert_not_called()
        ensure_remote.assert_not_called()
        self.assertEqual(client.calls, [])

    def test_native_windows_pairing_is_owned_by_desktop(self) -> None:
        context = self.windows_context()
        with (
            mock.patch.object(launcher, "codex_cli_version", return_value="0.151.0"),
            mock.patch.object(launcher, "start_codex_desktop_app") as start_app,
        ):
            with self.assertRaisesRegex(launcher.LaunchRefusal, "Control this PC"):
                with launcher.provision_codex(
                    context,
                    existing={},
                    pair=True,
                ):
                    pass

        start_app.assert_not_called()

    def test_native_windows_prints_the_desktop_sidebar_boundary(self) -> None:
        context = self.windows_context()
        codex = {
            "thread_id": "thr-station-1234",
            "thread_name": context.name,
            "cli_version": "0.151.0",
        }
        output = io.StringIO()
        with (
            mock.patch.object(
                launcher,
                "provision_codex",
                return_value=contextlib.nullcontext(codex),
            ),
            mock.patch.object(launcher, "run_claude", return_value=0),
            contextlib.redirect_stdout(output),
        ):
            result = launcher.supervise(arguments(), context)

        self.assertEqual(result, 0)
        self.assertIn(
            f"drag fx-main-win onto the {self.project['display_name']} project",
            output.getvalue(),
        )
        self.assertIn("no supported project-placement RPC", output.getvalue())

    def test_windows_has_no_supported_desktop_proxy_attachment(self) -> None:
        context = self.windows_context()
        with mock.patch.object(launcher, "start_codex_remote_daemon") as daemon:
            with self.assertRaisesRegex(
                launcher.LaunchRefusal, "no supported App Server proxy"
            ):
                launcher.connect_codex_app_server(context)

        daemon.assert_not_called()

    def test_start_codex_desktop_app_opens_the_station_checkout(self) -> None:
        completed = subprocess.CompletedProcess(["codex"], 0, "", "")
        with mock.patch.object(
            launcher.subprocess, "run", return_value=completed
        ) as run:
            launcher.start_codex_desktop_app(self.context)

        self.assertEqual(
            run.call_args.args[0],
            ["codex", "app", str(self.context.root)],
        )

    def test_daemon_start_rejects_malformed_json(self) -> None:
        completed = subprocess.CompletedProcess(
            ["codex"],
            0,
            "not-json\n",
            "",
        )
        with mock.patch.object(launcher.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(launcher.LaunchRefusal, "malformed JSON"):
                launcher.start_codex_remote_daemon(self.context)

    def test_supervisor_keeps_codex_process_alive_until_claude_stops(self) -> None:
        events: list[str] = []
        codex = {
            "thread_id": "thr-station-1234",
            "thread_name": self.context.name,
            "cli_version": "0.151.0",
        }

        @contextlib.contextmanager
        def session() -> object:
            events.append("codex-open")
            yield codex
            events.append("codex-closed")

        def run_claude(*_: object, **__: object) -> int:
            self.assertEqual(events, ["codex-open"])
            return 0

        with (
            mock.patch.object(launcher, "provision_codex", return_value=session()),
            mock.patch.object(launcher, "run_claude", side_effect=run_claude),
        ):
            result = launcher.supervise(arguments(), self.context)

        self.assertEqual(result, 0)
        self.assertEqual(events, ["codex-open", "codex-closed"])

    def test_minimum_codex_version_is_enforced(self) -> None:
        old = subprocess.CompletedProcess(["codex"], 0, "codex-cli 0.150.0\n", "")
        with mock.patch.object(launcher.subprocess, "run", return_value=old):
            with self.assertRaisesRegex(launcher.LaunchRefusal, "too old"):
                launcher.codex_cli_version(self.context)

    def test_no_server_marks_the_registry_as_direct_codex_mode(self) -> None:
        self.context.station_file.write_text(
            json.dumps(
                {
                    "schema": launcher.STATION_SCHEMA,
                    "station_id": "stn-1234abcd",
                    "codex": {
                        "thread_id": "thr-station-1234",
                        "thread_name": self.context.name,
                        "cli_version": "0.151.0",
                    },
                }
            ),
            encoding="utf-8",
        )

        result = launcher.run_legacy_no_server(self.context)

        self.assertEqual(result, 0)
        current = json.loads(self.context.station_file.read_text(encoding="utf-8"))
        self.assertEqual(current["station_id"], "stn-1234abcd")
        self.assertIsNone(current["codex"])

    def test_new_codex_flag_crosses_lease_boundary(self) -> None:
        parsed = launcher.parse_arguments(["main", "--new-codex-session"])
        self.assertIn("--new-codex-session", launcher.internal_supervisor_arguments(parsed))
        self.assertFalse(parsed.new_claude_session)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            launcher.parse_arguments(["main", "--new-codex-session", "--no-server"])

    def test_service_selection_and_fresh_apply_only_to_enabled_service(self) -> None:
        for flag in ("--no-codex", "--no-claude"):
            parsed = launcher.parse_arguments(["main", flag, "--fresh"])
            self.assertEqual(parsed.new_codex_session, flag == "--no-claude")
            self.assertEqual(parsed.new_claude_session, flag == "--no-codex")
            self.assertIn(flag, launcher.internal_supervisor_arguments(parsed))
        for flags in (
            ["--no-codex", "--no-claude"],
            ["--no-codex", "--pair-codex"],
            ["--no-codex", "--fresh", "codex"],
            ["--no-claude", "--continue"],
            ["--no-claude", "--fresh", "claude"],
            ["--no-claude", "--no-server"],
        ):
            with self.subTest(flags=flags):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    launcher.parse_arguments(flags)

    def test_claude_only_skips_codex_and_preserves_its_binding(self) -> None:
        codex = {"thread_id": "thr-old", "thread_name": self.context.name}
        launcher.atomic_write_json(self.context.station_file, {"codex": codex})
        def run(*args, **kwargs):
            kwargs["record_session"]("session_New123")
            return 0
        with (
            mock.patch.object(launcher, "provision_codex", side_effect=AssertionError("Codex is down")),
            mock.patch.object(launcher, "run_claude", side_effect=run),
        ):
            self.assertEqual(launcher.supervise(arguments(no_codex=True), self.context), 0)
        saved = launcher.load_station_file(self.context.station_file)
        self.assertEqual(saved["codex"], codex)
        self.assertEqual(saved["claude"]["session_id"], "session_New123")

    def test_codex_only_holds_supervisor_open_without_starting_claude(self) -> None:
        claude = {"session_id": "session_Old123"}
        launcher.atomic_write_json(self.context.station_file, {"claude": claude})
        events = []
        @contextlib.contextmanager
        def provision(*args, **kwargs):
            events.append("open")
            yield {"thread_id": "thr-new", "cli_version": "0.151.0"}
            events.append("close")
        def wait():
            self.assertEqual(events, ["open"])
            return 0
        with (
            mock.patch.object(launcher, "provision_codex", side_effect=provision),
            mock.patch.object(launcher, "run_claude", side_effect=AssertionError("Claude is down")),
            mock.patch.object(launcher, "wait_for_station_stop", side_effect=wait),
        ):
            self.assertEqual(launcher.supervise(arguments(no_claude=True), self.context), 0)
        self.assertEqual(events, ["open", "close"])
        self.assertEqual(launcher.load_station_file(self.context.station_file)["claude"], claude)

    def test_return_path_warning_precedes_every_claude_endpoint_only(self) -> None:
        @contextlib.contextmanager
        def provision(*args, **kwargs):
            yield {"thread_id": "thr-new", "thread_name": self.context.name, "cli_version": "0.151.0"}
        for flags, warned in (({}, True), ({"no_codex": True}, True), ({"no_claude": True}, False)):
            with self.subTest(flags=flags):
                errors = io.StringIO()
                with (
                    mock.patch.object(launcher, "provision_codex", side_effect=provision),
                    mock.patch.object(launcher, "run_claude", return_value=0),
                    mock.patch.object(launcher, "wait_for_station_stop", return_value=0),
                    contextlib.redirect_stderr(errors),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    self.assertEqual(launcher.supervise(arguments(**flags), self.context), 0)
                text = errors.getvalue()
                self.assertEqual(f"Claude replies from {self.context.name} reach its dispatcher" in text, warned)
                self.assertEqual('"crossSessionInbound": "accept"' in text, warned)

    def test_codex_only_wait_stops_cleanly_on_ctrl_c(self) -> None:
        with mock.patch.object(launcher.time, "sleep", side_effect=KeyboardInterrupt):
            self.assertEqual(launcher.wait_for_station_stop(), 0)

    def test_fresh_options_and_legacy_flags_reach_the_same_supervisor(self) -> None:
        for flags, codex, claude in (
            ([], False, False),
            (["--fresh"], True, True),
            (["--fresh", "both"], True, True),
            (["--fresh", "codex"], True, False),
            (["--fresh", "claude"], False, True),
            (["--new-codex-session"], True, False),
            (["--new-claude-session"], False, True),
        ):
            with self.subTest(flags=flags):
                parsed = launcher.parse_arguments(["main", *flags])
                self.assertEqual(parsed.new_codex_session, codex)
                self.assertEqual(parsed.new_claude_session, claude)
                forwarded = launcher.internal_supervisor_arguments(parsed)
                self.assertEqual("--new-codex-session" in forwarded, codex)
                self.assertEqual("--new-claude-session" in forwarded, claude)

    def test_fresh_claude_conflicts_with_strict_resume(self) -> None:
        for flags in (
            ["--fresh", "--require-claude-resume"],
            ["--fresh", "claude", "--continue"],
            ["--fresh", "--no-server"],
        ):
            with self.subTest(flags=flags):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    launcher.parse_arguments(flags)
        parsed = launcher.parse_arguments(["--fresh", "codex", "--require-claude-resume"])
        self.assertTrue(parsed.reattach)
        self.assertFalse(parsed.new_claude_session)

    def test_help_separates_everyday_and_advanced_options(self) -> None:
        for flag, advanced in (("--help", False), ("--help-all", True)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as result:
                launcher.parse_arguments([flag])
            self.assertEqual(result.exception.code, 0)
            self.assertIn("--fresh", output.getvalue())
            self.assertEqual("--permission-mode" in output.getvalue(), advanced)
            self.assertEqual("--require-claude-resume" in output.getvalue(), advanced)

    def test_new_codex_session_updates_registry_and_preserves_claude(self) -> None:
        old = launcher.station_document(
            self.context, station_id="stn-existing",
            codex={"thread_id": "thr-old"},
            claude={"session_id": "session_Existing123"},
        )
        launcher.atomic_write_json(self.context.station_file, old)
        new = {"thread_id": "thr-new", "thread_name": self.context.name,
               "cli_version": "0.151.0"}
        with (
            mock.patch.object(launcher, "provision_codex",
                              return_value=contextlib.nullcontext(new)) as provision,
            mock.patch.object(launcher, "run_claude", return_value=0) as claude,
        ):
            self.assertEqual(launcher.supervise(
                arguments(new_codex_session=True), self.context,
            ), 0)
        self.assertTrue(provision.call_args.kwargs["new_session"])
        saved = launcher.load_station_file(self.context.station_file)
        self.assertEqual(saved["codex"], new)
        self.assertEqual(saved["claude"], old["claude"])
        self.assertEqual(saved["station_id"], old["station_id"])
        self.assertEqual(claude.call_args.kwargs["session_id"], "session_Existing123")

    def test_fresh_claude_clears_old_binding_before_a_delayed_connection(self) -> None:
        old = launcher.station_document(
            self.context, station_id="stn-existing",
            codex={"thread_id": "thr-old"},
            claude={"session_id": "session_Existing123"},
        )
        launcher.atomic_write_json(self.context.station_file, old)
        with (
            mock.patch.object(launcher, "provision_codex") as provision,
            mock.patch.object(launcher, "run_claude", return_value=1) as claude,
        ):
            self.assertEqual(launcher.supervise(
                arguments(no_codex=True, new_claude_session=True), self.context,
            ), 1)
        provision.assert_not_called()
        saved = launcher.load_station_file(self.context.station_file)
        self.assertIsNone(saved["claude"])
        self.assertEqual(saved["codex"], old["codex"])
        self.assertEqual(saved["station_id"], old["station_id"])
        self.assertIsNone(claude.call_args.kwargs["session_id"])

    def test_fresh_claude_session_has_the_station_name_and_spawn_mode(self) -> None:
        command = launcher.claude_command(
            arguments(),
            self.context,
            reattach=False,
        )

        self.assertEqual(command[:2], ["claude", "remote-control"])
        self.assertEqual(command[command.index("--name") + 1], self.context.name)
        self.assertIn("--spawn", command)


class LinkedConsumerLaunchTests(unittest.TestCase):
    def test_public_main_preserves_selected_consumer_and_fresh_flags(self) -> None:
        source = SCRIPTS_ROOT.parent
        with tempfile.TemporaryDirectory() as temporary:
            for token in ("alpha", "beta"):
                root = Path(temporary) / token
                init_repo(root, token=token)
                git(root, "remote", "add", "origin", (Path(temporary) / (token + ".git")).as_posix())
                link = root / ".agents/skills/remote-station"
                link.parent.mkdir(parents=True)
                link.symlink_to(source, target_is_directory=True)
                # Execute the public entry point with only the runtime-launch boundary
                # replaced. Real Git/context resolution and argument parsing run.
                code = """
import json, runpy, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).parent))
module = runpy.run_path(sys.argv[1])
def capture(arguments, context):
    print(json.dumps({"root": str(context.root), "name": context.name,
        "codex": arguments.new_codex_session,
        "claude": arguments.new_claude_session, "skip": arguments.no_codex}))
    return 0
module["main"].__globals__["run_under_lease"] = capture
raise SystemExit(module["main"](["--repo-root", sys.argv[2], "--fresh", "--no-codex"]))
"""
                result = subprocess.run(
                    [sys.executable, "-B", "-c", code,
                     str(link / "scripts/launch_remote_station.py"), str(root)],
                    cwd=temporary, capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                observed = json.loads(result.stdout)
                self.assertEqual(observed["root"], str(root.resolve()))
                self.assertTrue(observed["name"].startswith(token + "-main-"))
                self.assertEqual((observed["codex"], observed["claude"], observed["skip"]),
                                 (False, True, True))


if __name__ == "__main__":
    unittest.main()
