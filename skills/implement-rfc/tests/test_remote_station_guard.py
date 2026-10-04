from __future__ import annotations

import json
import base64
import hashlib
import importlib.util
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    Draft202012Validator = None

PACK = Path(__file__).resolve().parent.parent
GUARD = PACK / "scripts" / "remote_station_guard.py"
LEASE = PACK / "scripts" / "station_lease.py"
PROJECT_CONFIG_MODULE = PACK / "scripts" / "project_config.py"
PERSONAL_STATE_MODULE = PACK / "scripts" / "personal_state.py"
from project_fixtures import CONFIG

FIXTURE_PROJECT = {
    **CONFIG,
    "origin_repo_name": "fixture",
    "workstreams": {"main": {"branch": "main"}, "acta": {"branch": "codex/acta"}},
}
SCHEMA = PACK / "schemas" / "remote-station.schema.json"
REQUEST = PACK / "scripts" / "station_task_admission.py"
_spec = importlib.util.spec_from_file_location("station_task_admission", REQUEST)
admission = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(admission)


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class RemoteStationGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self._temporary.name) / "repo"
        self.repo.mkdir()
        _git(self.repo, "init", "-b", "main")
        _git(self.repo, "config", "user.name", "station-test")
        _git(self.repo, "config", "user.email", "station@example.invalid")
        _git(self.repo, "remote", "add", "origin", "https://example.invalid/fixture.git")
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        _git(self.repo, "add", "seed.txt")
        _git(self.repo, "commit", "-m", "seed")
        self.head = _git(self.repo, "rev-parse", "HEAD")
        lease_target = (
            self.repo
            / ".agents"
            / "skills"
            / "implement-rfc"
            / "scripts"
            / "station_lease.py"
        )
        lease_target.parent.parent.mkdir(parents=True)
        lease_target.parent.symlink_to(PACK / "scripts", target_is_directory=True)
        self.request_helper = lease_target.with_name("station_task_admission.py")
        config_dir = self.repo / ".mask/skill-config/implement-rfc"
        config_dir.mkdir(parents=True)
        (config_dir / "project.md").write_text("Fixture rules")
        (config_dir / "project.json").write_text(
            json.dumps(FIXTURE_PROJECT, indent=2) + "\n", encoding="utf-8"
        )
        self.station = {
            "schema": "implement-rfc.remote-station.v2",
            "station_id": "stn-1234abcd",
            "station": "fx-main-mac",
            "project": "fixture",
            "workstream": "main",
            "environment": "macos",
            "branch": "main",
            "authority": "lane-commit",
            "codex": {
                "thread_id": "thr-station-1234",
                "thread_name": "fx-main-mac",
                "cli_version": "0.151.0",
            },
        }
        self._write_station()
        self.holder = subprocess.Popen(
            [
                sys.executable,
                str(lease_target),
                "run",
                "--role",
                "project-integrator",
                "--repo",
                str(self.repo),
                "--station",
                "fx-main-mac",
                "--",
                sys.executable,
                "-c",
                "import time; print('held', flush=True); time.sleep(30)",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert self.holder.stdout is not None
        readiness = self.holder.stdout.readline().strip()
        if readiness != "held":
            _, error = self.holder.communicate(timeout=5)
            self._temporary.cleanup()
            self.fail(f"lease fixture failed to start: {error}")

    def tearDown(self) -> None:
        if self.holder.poll() is None:
            self.holder.kill()
            self.holder.wait()
        if self.holder.stdout is not None:
            self.holder.stdout.close()
        if self.holder.stderr is not None:
            self.holder.stderr.close()
        self._temporary.cleanup()

    def _write_station(self) -> None:
        (self.repo / ".remote-station.json").write_text(
            json.dumps(self.station, indent=2) + "\n",
            encoding="utf-8",
        )

    def _envelope(self, **overrides: str) -> str:
        values = {
            "station": "fx-main-mac",
            "workstream": "main",
            "branch": "main",
            "authority": "lane-commit",
            "base_commit": self.head,
        }
        values.update(overrides)
        return f"""```yaml
envelope: implement-rfc.remote-task.v1
task_id: task-20990101-test
project: fixture
station: {values["station"]}
workstream: {values["workstream"]}
branch: {values["branch"]}
checkout: {self.repo}
rfcs: [RFC-FX-0005]
cards: []
rfc_base_sha: {self.head}
base_commit: {values["base_commit"]}
authority: {values["authority"]}
id_reservations: []
expires_at: 2099-01-01T00:00:00Z
reply_to: fx-main-mac
done_when: test the station guard
```"""

    def _event(self, event_name: str, **values: object) -> dict:
        event = {
            "session_id": "thr-station-1234",
            "turn_id": "turn-test-1234",
            "cwd": str(self.repo),
            "hook_event_name": event_name,
            "permission_mode": "bypassPermissions",
        }
        event.update(values)
        return event

    def _request_values(self, **overrides: object) -> dict:
        values = {
            "envelope": "implement-rfc.remote-task.v1", "task_id": "task-20990101-request",
            "project": "fixture", "station": "fx-main-mac", "workstream": "main",
            "branch": "main", "rfcs": [], "cards": [], "rfc_base_sha": self.head,
            "checkout": str(self.repo),
            "base_commit": self.head, "authority": "lane-commit", "id_reservations": [],
            "expires_at": "2099-01-01T00:00:00Z", "reply_to": "fx-main-mac",
            "done_when": "test delegated admission",
        }
        values.update(overrides)
        return values

    def _request_command(self, **overrides: object) -> str:
        encoded = base64.b64encode(json.dumps(self._request_values(**overrides)).encode()).decode()
        return f'python3 -B "{self.request_helper}" --envelope-base64 {encoded}'

    def _request_event(self, **overrides: object) -> dict:
        return self._event("PreToolUse", tool_name="Bash", tool_input={"cmd": self._request_command()}, **overrides)

    def _assert_denied(self, event: dict, detail: str | None = None) -> None:
        result = self._run_guard(event)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        if detail:
            self.assertIn(detail, output["permissionDecisionReason"])

    def _authorization_files(self) -> list[Path]:
        return list((self.repo / ".git/implement-rfc-remote-station-turns").glob("*.json"))

    def test_delegated_request_uses_host_identity_and_preserves_writer(self) -> None:
        registry = (self.repo / ".remote-station.json").read_bytes()
        holder = self.holder.pid
        for index in range(2):
            turn = f"turn-delegated-{index}"
            event = self._request_event(turn_id=turn)
            event["tool_input"]["cmd"] = self._request_command(task_id=f"task-20990101-request-{index}")
            result = self._run_guard(event)
            output = json.loads(result.stdout)["hookSpecificOutput"]
            context = output["additionalContext"]
            self.assertNotIn("permissionDecision", output)
            self.assertIn('"admission_source": "PreToolUse"', context)
            self.assertIn(f'"turn_id": "{turn}"', context)
            files = self._authorization_files()
            self.assertEqual(len(files), 1)
            state = json.loads(files[0].read_text())
            self.assertEqual(state["session_id"], event["session_id"])
            self.assertEqual(state["turn_id"], turn)
            self.assertEqual(state["admission_source"], "PreToolUse")
            self.assertEqual(self._run_guard(self._event("PreToolUse", turn_id=turn, tool_name="Write")).stdout, "")
            self._run_guard(self._event("Stop", turn_id=turn))
            self.assertEqual(self._authorization_files(), [])
            self.assertEqual(self.holder.pid, holder)
            self.assertIsNone(self.holder.poll())
            self.assertEqual((self.repo / ".remote-station.json").read_bytes(), registry)

    def test_request_cannot_replace_authority_or_replay_after_stop(self) -> None:
        accepted = self._run_guard(self._request_event())
        self.assertIn("accepted", accepted.stdout)
        request = self._request_event()
        request["tool_input"]["cmd"] = self._request_command(task_id="task-20990101-another", authority="read-only-proof")
        self._assert_denied(request, "already admitted")
        self._assert_denied(self._event("PreToolUse", turn_id="turn-other", tool_name="Write"), "no accepted")
        self._run_guard(self._event("Stop"))
        self._assert_denied(self._request_event(turn_id="turn-new"), "already used")
        self._assert_denied(self._event("PreToolUse", turn_id="turn-new", tool_name="Write"), "no accepted")

    def test_request_rejects_envelope_mismatches_before_state_write(self) -> None:
        invalid = (
            {"project": "other"}, {"station": "fx-other-mac"}, {"workstream": "other"}, {"checkout": str(self.repo.parent)},
            {"branch": "other"}, {"base_commit": "0" * 40}, {"expires_at": "2000-01-01T00:00:00Z"},
            {"authority": "owner"}, {"session_id": "caller"}, {"turn_id": "caller"},
            {"expires_at": "2099-99-99T00:00:00Z"}, {"rfcs": "RFC-FX-0001"},
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                event = self._request_event()
                event["tool_input"]["cmd"] = self._request_command(**overrides)
                self._assert_denied(event)
                self.assertEqual(self._authorization_files(), [])
        event = self._request_event()
        event["tool_input"]["command"] = "git add seed.txt"
        self._assert_denied(event, "conflicting")

    def test_request_rejects_wrong_host_identity_and_missing_turn(self) -> None:
        for values in ({"session_id": "thr-other"}, {"turn_id": ""}, {"turn_id": None}, {"turn_id": {"caller": 1}}):
            with self.subTest(values=values):
                self._assert_denied(self._request_event(**values))
                self.assertEqual(self._authorization_files(), [])

    def test_request_rejects_live_origin_branch_and_station_identity_drift(self) -> None:
        _git(self.repo, "remote", "set-url", "origin", "https://example.invalid/other.git")
        self._assert_denied(self._request_event(), "repository")
        _git(self.repo, "remote", "set-url", "origin", "https://example.invalid/fixture.git")
        _git(self.repo, "switch", "-c", "other")
        self._assert_denied(self._request_event(), "branch")
        _git(self.repo, "switch", "main")
        self.station["project"] = "other"
        self._write_station()
        self._assert_denied(self._request_event(), "project")
        self.assertEqual(self._authorization_files(), [])

    def test_request_requires_expected_held_lease(self) -> None:
        self.holder.kill()
        self.holder.wait()
        self.holder.stdout.close()
        self.holder.stderr.close()
        self._assert_denied(self._request_event(), "lease is not held")
        self.holder = subprocess.Popen([
            sys.executable, str(self.request_helper.with_name("station_lease.py")), "run",
            "--role", "project-integrator", "--repo", str(self.repo), "--station", "fx-other-mac", "--",
            sys.executable, "-c", "import time; print('held', flush=True); time.sleep(30)",
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(self.holder.stdout.readline().strip(), "held")
        self._assert_denied(self._request_event(), "lease belongs")
        self.assertEqual(self._authorization_files(), [])

    def test_request_receipt_capacity_is_bounded_and_io_failures_deny(self) -> None:
        spec = importlib.util.spec_from_file_location("guard_capacity_fixture", GUARD)
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        event = self._request_event()
        envelope = self._request_values()
        receipt_dir = self.repo / ".git/implement-rfc-remote-station-turns/requests" / hashlib.sha256(event["session_id"].encode()).hexdigest()
        receipt_dir.mkdir(parents=True)
        (receipt_dir / "one.json").write_text("{}")
        (receipt_dir / "two.json").write_text("{}")
        with patch.object(guard, "MAX_REQUEST_RECEIPTS", 2), self.assertRaisesRegex(guard.GuardRefusal, "capacity"):
            guard._admit_request(self.repo, event, envelope)
        self.assertEqual(self._authorization_files(), [])
        with patch.object(guard, "_write_turn_state", side_effect=OSError("fixture write failed")):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                guard._handle_tool(self.repo.resolve(), self.station, FIXTURE_PROJECT, event)
            self.assertIn("cannot write turn admission", output.getvalue())
        self.assertEqual(self._authorization_files(), [])
        self._assert_denied(event, "already used")

    def test_request_read_only_remains_narrow_and_cannot_widen_station(self) -> None:
        self.station["authority"] = "read-only-proof"
        self._write_station()
        self._assert_denied(self._request_event(), "exceeds read-only")
        event = self._request_event()
        event["tool_input"]["cmd"] = self._request_command(authority="read-only-proof")
        self.assertIn("accepted", self._run_guard(event).stdout)
        self._assert_denied(self._event("PreToolUse", tool_name="Write"), "cannot edit")
        self._assert_denied(self._event("PreToolUse", tool_name="Bash", tool_input={"cmd": "git add seed.txt"}), "mutating")
        self.assertEqual(self._run_guard(self._event("PreToolUse", tool_name="Bash", tool_input={"cmd": "git status --short"})).stdout, "")

    def test_request_rejects_shell_composition_and_helper_copies(self) -> None:
        command = self._request_command()
        copied = self.repo / "station_task_admission.py"
        shutil.copy2(REQUEST, copied)
        for invalid in (command + "; git add seed.txt", command + " && git status", "FOO=1 " + command,
                        "powershell -Command " + command, command.replace("python3 -B", "python3 -c"),
                        command.replace(str(self.request_helper), str(copied)),
                        command + " --session-id caller", command.replace('"', "")):
            with self.subTest(command=invalid):
                event = self._request_event()
                event["tool_input"]["cmd"] = invalid
                self._assert_denied(event)
                self.assertEqual(self._authorization_files(), [])

    def test_current_installed_link_target_is_the_same_trusted_helper(self) -> None:
        event = self._request_event()
        event["tool_input"]["cmd"] = self._request_command().replace(str(self.request_helper), str(self.request_helper.resolve()))
        self.assertIn("accepted", self._run_guard(event).stdout)

    def test_request_lifecycle_retirement_and_transfer_still_fence(self) -> None:
        identity = {name: self.station[name] for name in ("station_id", "station", "project", "branch", "workstream")}
        identity["root"] = str(self.repo.resolve())
        state = {"schema": "implement-rfc.station-lifecycle.v1", "mode": "managed", "generation": 1,
                 "identity": identity, "endpoints": {"codex": "thr-station-1234"}, "retired": [], "history": []}
        path = self.repo / ".git/implement-rfc-station-lifecycle.json"
        for change in ({"retired": [{"runtime": "codex", "id": "thr-station-1234"}]},
                       {"mode": "transferring", "transfer": {"target": "local", "from_generation": 1}}):
            with self.subTest(change=change):
                path.write_text(json.dumps({**state, **change}))
                self._assert_denied(self._request_event())
                self.assertEqual(self._authorization_files(), [])
        state["identity"]["station_id"] = "stn-ffffffff"
        path.write_text(json.dumps(state))
        self._assert_denied(self._request_event(), "durable lifecycle")

    def test_admitted_request_expiry_is_checked_on_later_tools(self) -> None:
        self.assertIn("accepted", self._run_guard(self._request_event()).stdout)
        path = self._authorization_files()[0]
        state = json.loads(path.read_text())
        state["expires_at"] = "2000-01-01T00:00:00Z"
        path.write_text(json.dumps(state))
        self._assert_denied(self._event("PreToolUse", tool_name="Write"), "expired")

    def test_direct_cli_cannot_admit_or_supply_identity(self) -> None:
        encoded = self._request_command().rsplit(" ", 1)[-1]
        result = subprocess.run([sys.executable, "-B", str(self.request_helper), "--envelope-base64", encoded], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["admission"], "hook-controlled")
        self.assertFalse((self.repo / ".git/implement-rfc-remote-station-turns").exists())
        denied = subprocess.run([sys.executable, "-B", str(self.request_helper), "--envelope-base64", encoded, "--turn-id", "caller"], cwd=self.repo, capture_output=True, text=True)
        self.assertNotEqual(denied.returncode, 0)
        self._assert_denied(self._event("PreToolUse", tool_name="Write"), "no accepted")

    def _run_guard(self, event: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GUARD)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_turn_allows_writer_tools_until_stop(self) -> None:
        accepted = self._run_guard(
            self._event("UserPromptSubmit", prompt=self._envelope())
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        output = json.loads(accepted.stdout)
        self.assertIn("accepted", output["hookSpecificOutput"]["additionalContext"])

        tool = self._run_guard(
            self._event(
                "PreToolUse",
                tool_name="apply_patch",
                tool_use_id="tool-test",
                tool_input={"command": "*** Begin Patch"},
            )
        )
        self.assertEqual(tool.stdout, "")

        stopped = self._run_guard(self._event("Stop"))
        self.assertEqual(stopped.stdout, "")
        denied = self._run_guard(
            self._event(
                "PreToolUse",
                tool_name="apply_patch",
                tool_use_id="tool-test-2",
                tool_input={"command": "*** Begin Patch"},
            )
        )
        self.assertEqual(
            json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_successive_turns_preserve_the_held_supervisor_and_binding(self) -> None:
        registry = (self.repo / ".remote-station.json").read_bytes()
        holder_pid = self.holder.pid
        for index in range(2):
            event = self._event("UserPromptSubmit", turn_id=f"turn-continuation-{index}", prompt=self._envelope())
            accepted = self._run_guard(event)
            self.assertIn("accepted", accepted.stdout, accepted.stderr)
            tool = self._run_guard(self._event("PreToolUse", turn_id=event["turn_id"], tool_name="Write"))
            self.assertEqual(tool.stdout, "", tool.stderr)
            self._run_guard(self._event("Stop", turn_id=event["turn_id"]))
            self.assertIsNone(self.holder.poll())
            self.assertEqual(self.holder.pid, holder_pid)
            self.assertEqual((self.repo / ".remote-station.json").read_bytes(), registry)

    def test_unknown_bound_schema_does_not_disable_enforcement(self) -> None:
        for marker in ("other.implement-rfc.remote-station.v2", None, [], {}):
            with self.subTest(marker=marker):
                self.station["schema"] = marker
                self._write_station()
                result = self._run_guard(self._event("PreToolUse", tool_name="Write"))
                output = json.loads(result.stdout)["hookSpecificOutput"]
                self.assertEqual(output["permissionDecision"], "deny")
                self.assertIn("unsupported schema", output["permissionDecisionReason"])

    def test_wrong_thread_accepts_prompt_for_bounded_recovery(self) -> None:
        result = self._run_guard(
            self._event(
                "UserPromptSubmit",
                session_id="thr-other-1234",
                prompt=self._envelope(),
            )
        )

        output = json.loads(result.stdout)
        self.assertNotIn('decision', output)
        self.assertIn('replacement chat', output['hookSpecificOutput']['additionalContext'])

    def test_station_mismatch_yields_remote_refusal_context(self) -> None:
        result = self._run_guard(
            self._event(
                "UserPromptSubmit",
                prompt=self._envelope(station="fx-acta-linux"),
            )
        )

        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("implement-rfc.remote-refusal.v1", context)
        self.assertIn("reason: station-mismatch", context)
        self.assertIn("correct_station: fx-main-mac", context)

    def test_branch_mismatch_yields_remote_refusal_context(self) -> None:
        result = self._run_guard(
            self._event(
                "UserPromptSubmit",
                prompt=self._envelope(branch="codex/wrong-branch"),
            )
        )

        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("reason: branch-mismatch", context)

    def test_non_ancestor_base_yields_remote_refusal_context(self) -> None:
        result = self._run_guard(
            self._event(
                "UserPromptSubmit",
                prompt=self._envelope(base_commit="0" * 40),
            )
        )

        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("reason: base-not-ancestor", context)

    def test_absent_supervisor_lease_refuses_the_turn(self) -> None:
        self.holder.kill()
        self.holder.wait()

        result = self._run_guard(
            self._event("UserPromptSubmit", prompt=self._envelope())
        )

        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("reason: authority-exceeded", context)
        self.assertIn("supervisor lease is not held", context)

    def test_read_only_authority_denies_repository_edits(self) -> None:
        self.station["authority"] = "read-only-proof"
        self._write_station()
        accepted = self._run_guard(
            self._event(
                "UserPromptSubmit",
                prompt=self._envelope(authority="read-only-proof"),
            )
        )
        self.assertIn("accepted", accepted.stdout)

        denied = self._run_guard(
            self._event(
                "PreToolUse",
                tool_name="apply_patch",
                tool_use_id="tool-read-only",
                tool_input={"command": "*** Begin Patch"},
            )
        )
        output = json.loads(denied.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("read-only-proof", output["permissionDecisionReason"])

    def test_envelope_cannot_widen_read_only_station_authority(self) -> None:
        self.station["authority"] = "read-only-proof"
        self._write_station()

        result = self._run_guard(
            self._event("UserPromptSubmit", prompt=self._envelope())
        )

        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("reason: authority-exceeded", context)

    def test_v1_station_file_leaves_the_guard_inactive(self) -> None:
        self.station = {
            "schema": "implement-rfc.remote-station.v1",
            "station_id": "stn-1234abcd",
            "station": "fx-main-mac",
            "project": "fixture",
            "role": "main",
            "environment": "macos",
            "branch": "main",
            "authority": "lane-commit",
        }
        self._write_station()

        result = self._run_guard(
            self._event("UserPromptSubmit", prompt="ordinary work under a v1 file")
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("guard inactive", result.stderr)

    def test_legacy_null_endpoint_requires_inspection_or_takeover(self) -> None:
        self.station["codex"] = None
        self._write_station()

        result = self._run_guard(
            self._event(
                "UserPromptSubmit",
                session_id="thr-direct-session",
                prompt="ordinary direct Codex work",
            )
        )

        self.assertIn('no Codex endpoint', result.stdout)


class ProjectPrefixedStationGuardTests(RemoteStationGuardTests):
    def setUp(self) -> None:
        super().setUp()
        self.station["schema"] = "aito.implement-rfc.remote-station.v2"
        self._write_station()


class AdmissionRequestParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.values = {
            "envelope": "implement-rfc.remote-task.v1", "task_id": "task-20990101-parse",
            "project": "fixture", "station": "fx-main-win", "workstream": "main",
            "branch": "main", "rfcs": [], "cards": [], "rfc_base_sha": "a" * 40,
            "base_commit": "a" * 40, "authority": "lane-commit", "id_reservations": [],
            "expires_at": "2099-01-01T00:00:00Z", "reply_to": "fx-main-mac", "done_when": "test parsing",
        }
        self.encoded = base64.b64encode(json.dumps(self.values).encode()).decode()

    def test_exact_native_py_command_retains_quoted_drive_path(self) -> None:
        script = r"C:\code\git\aito\.agents\skills\implement-rfc\scripts\station_task_admission.py"
        command = f'py -3 -B "{script}" --envelope-base64 {self.encoded}'
        parsed_script, envelope = admission.command_request(command)
        self.assertEqual(parsed_script, script)
        self.assertEqual(envelope, self.values)
        for invalid in (command.replace("py -3 -B", "py -B"), command.replace("py -3 -B", "py -3 -c"),
                        "powershell -Command " + command, command + " | more", command + "\nwhoami",
                        command.replace("C:\\code", "C:\\$code")):
            with self.subTest(command=invalid):
                self.assertIsNone(admission.command_request(invalid))

    def test_malformed_oversized_duplicate_and_noncanonical_payloads_refuse(self) -> None:
        raw = json.dumps(self.values)
        duplicate = raw[:-1] + ', "authority": "read-only-proof"}'
        for encoded in ("!", "", "A" * (admission.MAX_BASE64_CHARS + 1), "ZE==",
                        base64.b64encode(b"\xff").decode(), base64.b64encode(b"[]").decode(),
                        base64.b64encode(duplicate.encode()).decode(),
                        base64.b64encode(b" " * (admission.MAX_JSON_BYTES + 1)).decode()):
            with self.subTest(payload=encoded[:32]):
                with self.assertRaises(admission.RequestError):
                    admission.decode_envelope(encoded)

    def test_strict_request_field_types_limits_and_schema_agree(self) -> None:
        invalid = ({"done_when": "x" * 513}, {"notes": "x" * 4097}, {"checkout": 7},
                   {"cards": ["bad"]}, {"rfcs": ["RFC-FX-0001"] * 65},
                   {"id_reservations": [{"session_id": "caller"}]}, {"session_id": "caller"},
                   {"turn_id": "caller"}, {"authority": {"lane-commit": True}})
        for changes in invalid:
            with self.subTest(changes=changes):
                encoded = base64.b64encode(json.dumps({**self.values, **changes}).encode()).decode()
                with self.assertRaises(admission.RequestError):
                    admission.decode_envelope(encoded)
        if Draft202012Validator is not None:
            validator = Draft202012Validator(json.loads((PACK / "schemas/remote-task-envelope.schema.json").read_text()))
            validator.validate(admission.decode_envelope(self.encoded))


@unittest.skipIf(Draft202012Validator is None, "jsonschema is required for schema validation")
class RemoteStationSchemaTests(unittest.TestCase):
    def test_v2_accepts_provisioned_and_legacy_direct_modes(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        station = {
            "schema": "implement-rfc.remote-station.v2",
            "station_id": "stn-1234abcd",
            "station": "fx-main-mac",
            "project": "fixture",
            "workstream": "main",
            "environment": "macos",
            "branch": "main",
            "authority": "lane-commit",
            "codex": {
                "thread_id": "thr-station-1234",
                "thread_name": "fx-main-mac",
                "cli_version": "0.151.0",
            },
        }
        validator.validate(station)
        station["claude"] = {"session_id": "session_Acta123"}
        validator.validate(station)
        station["claude"] = None
        station["codex"] = None
        validator.validate(station)

    def test_supported_project_prefixed_v2_preserves_schema_validation(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        station = {
            "schema": "aito.implement-rfc.remote-station.v2",
            "station_id": "stn-1234abcd",
            "station": "fx-main-mac",
            "project": "fixture",
            "workstream": "main",
            "environment": "macos",
            "branch": "main",
            "authority": "lane-commit",
            "codex": {"thread_id": "thr-station-1234", "thread_name": "fx-main-mac", "cli_version": "0.151.0"},
        }
        validator.validate(station)
        station["schema"] = "other.implement-rfc.remote-station.v2"
        self.assertTrue(list(validator.iter_errors(station)))

    def test_v1_is_rejected_after_migration(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        station = {
            "schema": "implement-rfc.remote-station.v1",
            "station_id": "stn-1234abcd",
            "station": "fx-main-mac",
            "project": "fixture",
            "workstream": "main",
            "environment": "macos",
            "branch": "main",
            "authority": "lane-commit",
            "codex": None,
        }
        self.assertTrue(list(validator.iter_errors(station)))


if __name__ == "__main__":
    unittest.main()
