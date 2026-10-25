from __future__ import annotations

import json
import base64
import hashlib
import importlib.util
import contextlib
import io
import shutil
import shlex
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
sys.path.insert(0, str(PACK / 'scripts'))
GUARD = PACK / "scripts" / "remote_station_guard.py"
LEASE = PACK / "scripts" / "station_lease.py"
from station_fixtures import CONFIG

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
            / "remote-station"
            / "scripts"
            / "station_lease.py"
        )
        lease_target.parent.parent.mkdir(parents=True)
        lease_target.parent.symlink_to(PACK / "scripts", target_is_directory=True)
        self.request_helper = lease_target.with_name("station_task_admission.py")
        config_dir = self.repo / ".mask/skill-config/remote-station"
        config_dir.mkdir(parents=True)
        (config_dir / "station.json").write_text(
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
            task_id = f"task-20990101-request-{index}"
            self.assertEqual(context, self._ack(task_id))
            receipt = json.loads(self._receipt_path(event["session_id"], task_id).read_text(encoding="utf-8"))
            self.assertEqual((receipt["session_id"], receipt["turn_id"], receipt["admission_source"]),
                             (event["session_id"], turn, "PreToolUse"))
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

    # --- compact v2 messaging (ASK-0128) ------------------------------------

    def _ack(self, task_id: str, authority: str = "lane-commit") -> str:
        receipt = hashlib.sha256(task_id.encode()).hexdigest()[:16]
        return f"Remote-task {task_id} accepted for this turn ({authority}); receipt {receipt}."

    def _receipt_path(self, session_id: str, task_id: str) -> Path:
        return (self.repo / ".git/implement-rfc-remote-station-turns/requests"
                / hashlib.sha256(session_id.encode()).hexdigest()
                / f"{hashlib.sha256(task_id.encode()).hexdigest()}.json")

    def _v2_command(self, **overrides: object) -> str:
        values: dict = {"task_id": "task-20990101-request", "station": "fx-main-mac", "base_commit": self.head,
                        "authority": "lane-commit", "reply_to": "fx-main-mac", "expires_at": "2099-01-01T00:00:00Z"}
        values.update(overrides)
        words = ["--task", values["task_id"], "--station", values["station"], "--base", values["base_commit"],
                 "--authority", values["authority"], "--reply-to", values["reply_to"]]
        if values.get("rfc_base_sha"):
            words += ["--rfc-base", values["rfc_base_sha"]]
        for flag, field in (("--rfc", "rfcs"), ("--card", "cards")):
            for value in values.get(field, []):
                words += [flag, value]
        if values.get("expires_at"):
            words += ["--expires", values["expires_at"]]
        words += values.get("extra", [])
        return f'python3 -B "{self.request_helper}" ' + " ".join(words)

    def _v2_prompt(self, **overrides: str) -> str:
        values = {"station": "fx-main-mac", "authority": "lane-commit", "base_commit": self.head,
                  "expires_at": "2099-01-01T00:00:00Z", "extra": ""}
        values.update(overrides)
        return f"""Do the fixture task.

```yaml
envelope: implement-rfc.remote-task.v2
task_id: task-20990101-test
station: {values["station"]}
base_commit: {values["base_commit"]}
authority: {values["authority"]}
expires_at: {values["expires_at"]}
reply_to: fx-main-mac{values["extra"]}
```"""

    def _command_for(self, version: str, **overrides: object) -> str:
        if version == "v1":
            return self._request_command(**overrides)
        if "project" in overrides:
            # v2 flags have no project; a v2 JSON envelope may name one, and then it binds.
            values = {"envelope": "implement-rfc.remote-task.v2", "task_id": overrides["task_id"],
                      "station": "fx-main-mac", "base_commit": self.head, "authority": "lane-commit",
                      "reply_to": "fx-main-mac", "project": overrides["project"]}
            encoded = base64.b64encode(json.dumps(values).encode()).decode()
            return f'python3 -B "{self.request_helper}" --envelope-base64 {encoded}'
        return self._v2_command(**overrides)

    def _request_for(self, version: str, turn: str, **overrides: object) -> dict:
        event = self._event("PreToolUse", turn_id=turn, tool_name="Bash", tool_input={})
        event["tool_input"]["cmd"] = self._command_for(version, **overrides)
        return event

    def _request_refusal_reason(self, event: dict) -> str:
        """The protocol reason _handle_tool would deny with (deny output carries only detail)."""
        import remote_station_guard as guard
        root = self.repo.resolve()
        with self.assertRaises(guard.GuardRefusal) as caught:
            guard._validate_live_checkout(root, self.station, FIXTURE_PROJECT)
            envelope = guard._request_envelope(root, event)
            envelope = guard._expand_envelope(self.station, envelope)
            guard._validate_envelope(root, self.station, envelope)
            guard._admit_request(root, event, envelope)
        return caught.exception.reason

    def test_v2_request_admits_with_compact_flags_and_one_line_ack(self) -> None:
        registry = (self.repo / ".remote-station.json").read_bytes()
        event = self._request_for("v2", "turn-v2", cards=["FX-0001"], rfcs=["RFC-FX-0005"], rfc_base_sha=self.head)
        result = self._run_guard(event)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", output)
        self.assertEqual(output["additionalContext"], self._ack("task-20990101-request"))
        receipt = json.loads(self._receipt_path(event["session_id"], "task-20990101-request").read_text(encoding="utf-8"))
        expanded = {"envelope": "implement-rfc.remote-task.v2", "task_id": "task-20990101-request",
                    "station": "fx-main-mac", "base_commit": self.head, "authority": "lane-commit",
                    "reply_to": "fx-main-mac", "rfc_base_sha": self.head, "rfcs": ["RFC-FX-0005"],
                    "cards": ["FX-0001"], "expires_at": "2099-01-01T00:00:00Z", "project": "fixture",
                    "workstream": "main", "branch": "main", "id_reservations": []}
        digest = hashlib.sha256(json.dumps(expanded, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(receipt["envelope_sha256"], digest)
        self.assertEqual(self._run_guard(self._event("PreToolUse", turn_id="turn-v2", tool_name="Write")).stdout, "")
        self.assertEqual((self.repo / ".remote-station.json").read_bytes(), registry)

    def test_v2_prompt_envelope_is_expanded_and_admitted(self) -> None:
        accepted = self._run_guard(self._event("UserPromptSubmit", prompt=self._v2_prompt()))
        self.assertIn("accepted", json.loads(accepted.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(self._run_guard(self._event("PreToolUse", tool_name="Write")).stdout, "")

    def test_guard_refusals_fire_for_v1_and_v2_requests(self) -> None:
        """AC10 on the delegated request route, the route that keeps task receipts."""
        for version in ("v1", "v2"):
            with self.subTest(version=version, refusal="replayed task_id"):
                task = f"task-20990101-replay-{version}"
                self.assertIn("accepted", self._run_guard(self._request_for(version, f"turn-a-{version}", task_id=task)).stdout)
                self._run_guard(self._event("Stop", turn_id=f"turn-a-{version}"))
                replay = self._request_for(version, f"turn-b-{version}", task_id=task)
                self._assert_denied(replay, "already used")
                # Existing protocol code for replay; unchanged by v2.
                self.assertEqual(self._request_refusal_reason(replay), "authority-exceeded")
            with self.subTest(version=version, refusal="project mismatch in envelope"):
                event = self._request_for(version, f"turn-p-{version}", task_id=f"task-20990101-proj-{version}", project="other")
                self._assert_denied(event, "project")
                self.assertEqual(self._request_refusal_reason(event), "project-mismatch")
            with self.subTest(version=version, refusal="project mismatch in station file"):
                self.station["project"] = "other"
                self._write_station()
                event = self._request_for(version, f"turn-q-{version}", task_id=f"task-20990101-projf-{version}")
                self._assert_denied(event, "project")
                self.assertEqual(self._request_refusal_reason(event), "project-mismatch")
                self.station["project"] = "fixture"
                self._write_station()
            with self.subTest(version=version, refusal="authority exceeded"):
                self.station["authority"] = "read-only-proof"
                self._write_station()
                event = self._request_for(version, f"turn-r-{version}", task_id=f"task-20990101-auth-{version}")
                self._assert_denied(event, "exceeds read-only")
                self.assertEqual(self._request_refusal_reason(event), "authority-exceeded")
                self.station["authority"] = "lane-commit"
                self._write_station()
            with self.subTest(version=version, refusal="expired"):
                event = self._request_for(version, f"turn-e-{version}", task_id=f"task-20990101-exp-{version}",
                                          expires_at="2000-01-01T00:00:00Z")
                self._assert_denied(event, "expired")
                self.assertEqual(self._request_refusal_reason(event), "expired")
            with self.subTest(version=version, refusal="station mismatch"):
                event = self._request_for(version, f"turn-s-{version}", task_id=f"task-20990101-stn-{version}",
                                          station="fx-other-mac")
                self._assert_denied(event, "station")
                self.assertEqual(self._request_refusal_reason(event), "station-mismatch")
        self.assertEqual(len(self._authorization_files()), 0)

    def test_guard_refusals_fire_for_v1_and_v2_prompts(self) -> None:
        """AC10 on the fenced-prompt route; the refusal envelope carries the reason."""
        cases = (
            ("project-mismatch", {"v1": self._envelope().replace("project: fixture", "project: other"),
                                  "v2": self._v2_prompt(extra="\nproject: other")}, None),
            ("authority-exceeded", {"v1": self._envelope(), "v2": self._v2_prompt()}, "read-only-proof"),
            ("expired", {"v1": self._envelope().replace("2099-01-01T00:00:00Z", "2000-01-01T00:00:00Z"),
                         "v2": self._v2_prompt(expires_at="2000-01-01T00:00:00Z")}, None),
            ("station-mismatch", {"v1": self._envelope(station="fx-acta-linux"),
                                  "v2": self._v2_prompt(station="fx-acta-linux")}, None),
        )
        for reason, prompts, station_authority in cases:
            for version, prompt in prompts.items():
                with self.subTest(reason=reason, version=version):
                    self.station["authority"] = station_authority or "lane-commit"
                    self._write_station()
                    result = self._run_guard(self._event("UserPromptSubmit", prompt=prompt))
                    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
                    self.assertIn(f"reason: {reason}", context)
                    self.assertEqual(self._authorization_files(), [])
        self.station["authority"] = "lane-commit"
        self.station["project"] = "other"
        self._write_station()
        for version, prompt in (("v1", self._envelope()), ("v2", self._v2_prompt())):
            with self.subTest(reason="station file project drift", version=version):
                context = json.loads(self._run_guard(self._event("UserPromptSubmit", prompt=prompt)).stdout)
                self.assertIn("reason: project-mismatch", context["hookSpecificOutput"]["additionalContext"])

    def test_v2_cannot_carry_caller_identity_or_unknown_flags(self) -> None:
        for extra in (["--session-id", "caller"], ["--turn-id", "caller"], ["--authority", "owner"],
                      ["--expires", "2099-01-01T00:00:00Z"], [";", "git", "add", "seed.txt"], ["&&", "git", "status"]):
            with self.subTest(extra=extra):
                event = self._request_for("v2", "turn-x")
                event["tool_input"]["cmd"] = self._v2_command(extra=extra)
                self._assert_denied(event)
                self.assertEqual(self._authorization_files(), [])

    def test_v1_dispatcher_envelopes_are_still_admitted(self) -> None:
        """AC11: the v1 shapes existing dispatchers send keep working unchanged."""
        registry = (self.repo / ".remote-station.json").read_bytes()
        lifecycle_path = self.repo / ".git/implement-rfc-station-lifecycle.json"
        lifecycle_before = lifecycle_path.read_bytes() if lifecycle_path.exists() else None
        # Recorded dispatcher shape: base64 JSON with checkout and notes.
        task = "task-20990101-dispatcher-v1"
        command = self._request_command(task_id=task, notes="free text from a v1 dispatcher",
                                        cards=["FX-0001"], rfcs=["RFC-FX-0005"])
        event = self._event("PreToolUse", turn_id="turn-v1", tool_name="Bash", tool_input={"command": command})
        self.assertEqual(json.loads(self._run_guard(event).stdout)["hookSpecificOutput"]["additionalContext"], self._ack(task))
        self._run_guard(self._event("Stop", turn_id="turn-v1"))
        # v1 fenced YAML and fenced JSON prompts.
        json_prompt = "```json\n" + json.dumps(self._request_values(task_id="task-20990101-json")) + "\n```"
        for prompt in (self._envelope(), json_prompt):
            with self.subTest(prompt=prompt[:12]):
                accepted = self._run_guard(self._event("UserPromptSubmit", turn_id="turn-v1-prompt", prompt=prompt))
                self.assertIn("accepted", accepted.stdout)
                self._run_guard(self._event("Stop", turn_id="turn-v1-prompt"))
        # The v1 request helper output is byte-compatible.
        encoded = command.rsplit(" ", 1)[-1]
        result = subprocess.run([sys.executable, "-B", str(self.request_helper), "--envelope-base64", encoded],
                                cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout), {"schema": "implement-rfc.admission-request.v1",
                                                     "task_id": task, "admission": "hook-controlled"})
        # Station identity is untouched.
        self.assertEqual((self.repo / ".remote-station.json").read_bytes(), registry)
        self.assertEqual(lifecycle_path.read_bytes() if lifecycle_path.exists() else None, lifecycle_before)

    def test_v2_direct_cli_reports_hook_control_only(self) -> None:
        words = [str(self.request_helper), *self._v2_command().split('" ', 1)[1].split(" ")]
        result = subprocess.run([sys.executable, "-B", *words], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"task_id": "task-20990101-request", "admission": "hook-controlled"})
        denied = subprocess.run([sys.executable, "-B", *words, "--turn-id", "caller"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(denied.returncode, 2)
        self.assertFalse((self.repo / ".git/implement-rfc-remote-station-turns").exists())

    def _run_guard(self, event: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GUARD), '--enforce'],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_default_hooks_are_inactive_even_for_replacement_tools_and_invalid_input(self):
        for event in (self._event('UserPromptSubmit', prompt=self._envelope()),
                      self._event('PreToolUse', session_id='replacement', tool_name='Bash',
                                  tool_input={'command': 'mask repair --json'}),
                      self._event('Stop'), {'malformed': True}):
            result = subprocess.run([sys.executable, '-B', str(GUARD)],
                                    input=json.dumps(event), capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))
        self.assertFalse((self.repo / '.git/implement-rfc-remote-station-turns').exists())
        import station_lifecycle
        self.assertIsNone(station_lifecycle.load(self.repo))

    def test_public_recovery_accepts_flag_order_and_refuses_shell_suffixes(self):
        import remote_station_guard as guard
        wrapper = self.repo / 'scripts/launch_remote_station.py'
        wrapper.parent.mkdir()
        wrapper.write_text('# fixture project wrapper\n')
        for args in (['status'], ['status', '--json', '--observe-runtime'],
                     ['takeover'], ['takeover', '--confirm-runtime-stopped', '--json'],
                     ['hooks', 'off', '--dry-run', '--json']):
            command = shlex.join([sys.executable, str(wrapper), *args])
            self.assertTrue(guard._bounded_recovery_command(self.repo.resolve(), command))
            self.assertFalse(guard._bounded_recovery_command(self.repo.resolve(), command + '; git reset --hard'))
        helper = GUARD.with_name('station_control.py')
        self.assertTrue(guard._bounded_recovery_command(self.repo.resolve(), shlex.join([
            sys.executable, str(helper), 'status', '--json', '--repo-root', str(self.repo)])))
        self.assertFalse(guard._bounded_recovery_command(self.repo.resolve(), shlex.join([
            sys.executable, str(wrapper), 'takeover', '--repo-root', str(self.repo.parent)])))

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

    V2_SCRIPT = r"C:\code\git\aito\.agents\skills\remote-station\scripts\station_task_admission.py"

    def _v2(self, *words: str) -> str:
        required = ["--task", "task-20990101-parse", "--station", "fx-main-win", "--base", "a" * 40,
                    "--authority", "lane-commit", "--reply-to", "fx-main-mac"]
        return f'py -3 -B "{self.V2_SCRIPT}" ' + " ".join([*required, *words])

    def test_v2_flags_parse_into_the_compact_envelope(self) -> None:
        reservation = "idr-fx-20990101-01:FX:FX-0037..FX-0044:" + "b" * 40
        command = self._v2("--rfc-base", "c" * 40, "--rfc", "RFC-FX-0005", "--rfc", "RFC-FX-0006",
                           "--card", "FX-0031", "--reservation", reservation, "--expires", "2099-01-01T00:00:00Z")
        script, envelope = admission.command_request(command)
        self.assertEqual(script, self.V2_SCRIPT)
        self.assertEqual(envelope, {
            "envelope": "implement-rfc.remote-task.v2", "task_id": "task-20990101-parse",
            "station": "fx-main-win", "base_commit": "a" * 40, "authority": "lane-commit",
            "reply_to": "fx-main-mac", "rfc_base_sha": "c" * 40, "rfcs": ["RFC-FX-0005", "RFC-FX-0006"],
            "cards": ["FX-0031"], "expires_at": "2099-01-01T00:00:00Z",
            "id_reservations": [{"reservation_id": "idr-fx-20990101-01", "area": "FX",
                                 "range": "FX-0037..FX-0044", "reservation_commit": "b" * 40}],
        })
        self.assertEqual(admission.command_request(self._v2())[1]["envelope"], "implement-rfc.remote-task.v2")
        if Draft202012Validator is not None:
            schema = json.loads((PACK / "schemas/remote-task-envelope.v2.schema.json").read_text(encoding="utf-8"))
            Draft202012Validator(schema).validate(envelope)

    def test_v2_flags_refuse_order_repeats_identity_and_shell_text(self) -> None:
        good = self._v2("--card", "FX-0031")
        invalid = (
            self._v2("--card", "FX-0031", "--rfc-base", "c" * 40),  # out of order
            self._v2("--expires", "2099-01-01T00:00:00Z", "--expires", "2099-01-01T00:00:00Z"),
            self._v2("--rfc", "RFC-FX-0005"),  # rfcs need --rfc-base
            self._v2("--session-id", "caller"), self._v2("--turn-id", "caller"), self._v2("--project", "fixture"),
            self._v2("--card", "FX-0031;whoami"), self._v2("--card", "$(whoami)"),
            self._v2("--reservation", "idr-x:FX"), self._v2("--card"),
            good.replace("--authority lane-commit", "--authority owner"),
            good.replace("--base " + "a" * 40, "--base HEAD"),
        )
        for command in invalid:
            with self.subTest(command=command[-60:]):
                with self.assertRaises(admission.RequestError):
                    admission.command_request(command)
        swapped = good.replace("--task task-20990101-parse --station fx-main-win",
                               "--station fx-main-win --task task-20990101-parse")
        for command in (swapped, good + " ; git add seed.txt", good + "  ", good.replace(" --card", "  --card"),
                        good + "\nwhoami", "powershell -Command " + good, good.replace("py -3 -B", "py -3 -c")):
            with self.subTest(command=command[-40:]):
                try:
                    self.assertIsNone(admission.command_request(command))
                except admission.RequestError:
                    pass

    def test_v2_json_envelope_requires_station_and_refuses_v1_only_identity(self) -> None:
        compact = {"envelope": "implement-rfc.remote-task.v2", "task_id": "task-20990101-parse",
                   "station": "fx-main-win", "base_commit": "a" * 40, "authority": "lane-commit",
                   "reply_to": "fx-main-mac"}
        self.assertEqual(admission.validate_envelope(dict(compact)), compact)
        for changes in ({"station": None}, {"session_id": "caller"}, {"rfcs": ["RFC-FX-0001"]}):
            with self.subTest(changes=changes):
                value = {key: item for key, item in {**compact, **changes}.items() if item is not None}
                with self.assertRaises(admission.RequestError):
                    admission.validate_envelope(value)


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
