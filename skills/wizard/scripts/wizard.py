#!/usr/bin/env python3
"""Portable, local guided steps. No shell execution and no third-party imports."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import threading
import time
from urllib import request
from urllib.parse import urlsplit
import uuid
import webbrowser

MAX_BODY = 1_000_000
PORTABLE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}$")


class WizardError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise WizardError(message)


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix=".wizard-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encode(value) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def file_lock(path, blocking=True):
    """Kernel-owned locks release on exit/crash on both native Windows and Unix."""
    require(not path.is_symlink(), "wizard lock path cannot be a symlink")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    # O_NOFOLLOW closes the check/open race on hosts that provide it. The
    # explicit check also gives a clear refusal on other hosts.
    with os.fdopen(os.open(path, flags, 0o600), "a+b") as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            # msvcrt.LK_LOCK has a fixed retry limit. Poll for bounded operations.
            while True:
                try:
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if not blocking:
                        raise BlockingIOError("wizard lock held")
                    time.sleep(0.05)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def validate_definition(definition):
    require(isinstance(definition, dict), "definition must be an object")
    require(set(definition) == {"schema_version", "id", "title", "steps"}, "unknown or missing definition fields")
    require(type(definition["schema_version"]) is int and definition["schema_version"] == 1, "schema_version must be 1")
    require(isinstance(definition["id"], str) and PORTABLE_ID.fullmatch(definition["id"]), "invalid definition id")
    require(isinstance(definition["title"], str) and definition["title"].strip(), "title required")
    require(isinstance(definition["steps"], list) and 0 < len(definition["steps"]) <= 200, "steps must contain 1–200 entries")
    ids = set()
    for step in definition["steps"]:
        required = {"id", "title", "instruction", "expected", "response"}
        require(isinstance(step, dict) and required <= set(step) <= required | {"url", "options"}, "unknown or missing step fields")
        require(isinstance(step["id"], str) and PORTABLE_ID.fullmatch(step["id"]), "invalid step id")
        require(step["id"] not in ids, "duplicate step id")
        ids.add(step["id"])
        for field in ("title", "instruction", "expected"):
            require(isinstance(step[field], str) and step[field].strip() and len(step[field]) <= 8000, f"invalid {field}")
        require(step["response"] in ("ack", "choice", "text", "observation"), "invalid response type")
        if step["response"] == "choice":
            options = step.get("options")
            require(isinstance(options, list) and 1 < len(options) <= 30 and all(isinstance(s, str) and s.strip() and len(s) <= 500 for s in options), "choice needs 2–30 nonempty options")
            require(len(set(options)) == len(options), "duplicate choices")
        else:
            require("options" not in step, "options only apply to choice steps")
        if "url" in step:
            require(isinstance(step["url"], str), "url must be a string")
            parsed = urlsplit(step["url"])
            require(parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username and not parsed.password, "url must be HTTP(S) without credentials")
    return definition


def digest(definition):
    return hashlib.sha256(encode(definition).encode()).hexdigest()


def event(state, kind, **data):
    state["revision"] += 1
    state["events"].append({"revision": state["revision"], "kind": kind, **data})


def summary(state, since=None):
    steps = state["definition"]["steps"]
    pending = [step for step in steps if step["id"] not in state["answers"]]
    result = {"schema_version": 1, "session_id": state["session_id"], "definition_id": state["definition"]["id"],
              "revision": state["revision"], "status": "complete" if not pending else "paused" if state["paused"] else "active",
              "completed": len(steps) - len(pending), "total": len(steps), "next": pending[0] if pending else None}
    if since is not None:
        result["events"] = [item for item in state["events"] if item["revision"] > since]
    return result


def apply_answer(state, step_id, value, actor):
    steps = state["definition"]["steps"]
    step = next((item for item in steps if item["id"] == step_id), None)
    require(step is not None, "unknown step")
    require(actor in ("human", "agent"), "actor must be human or agent")
    require((actor == "agent") == (step["response"] == "observation"), "observations require agent capture; other responses require a human")
    response = step["response"]
    if response == "observation":
        require(isinstance(value, dict) and set(value) == {"summary", "evidence"}, "observation needs summary and evidence")
        require(all(isinstance(v, str) and v.strip() and len(v) <= 8000 for v in value.values()), "observation summary/evidence must be nonempty strings")
    elif response == "ack":
        require(value is True, "ack must be true")
    elif response == "choice":
        require(isinstance(value, str) and value in step["options"], "value is not an offered choice")
    else:
        require(isinstance(value, str) and value.strip() and len(value) <= 8000, "text must contain 1–8000 characters")
    previous = state["answers"].get(step_id)
    if previous:
        require(previous["value"] == value and previous["actor"] == actor, "step already answered differently; use a new wizard for changed results")
        return
    require(not state["paused"], "wizard is paused; resume before recording")
    first_pending = next(item["id"] for item in steps if item["id"] not in state["answers"])
    require(step_id == first_pending, f"complete prerequisite {first_pending} first")
    state["answers"][step_id] = {"value": value, "actor": actor}
    event(state, "answered", step=step_id, actor=actor)


class Store:
    def __init__(self, directory, source_root=None):
        selected = Path(directory).expanduser()
        require(".." not in selected.parts, "state path cannot traverse parents")
        selected = selected if selected.is_absolute() else Path.cwd() / selected
        cursor = selected
        while cursor != cursor.parent:
            # Root-level aliases such as macOS /var -> /private/var are part of
            # the host path layout. Reject links below that boundary, including
            # links hidden in an otherwise external state directory.
            require(not cursor.is_symlink() or cursor.parent == Path(cursor.anchor),
                    "state path cannot traverse symlinks")
            cursor = cursor.parent
        self.directory = selected.resolve()
        if source_root is not None:
            source = Path(source_root).expanduser().resolve()
            require(source.is_dir(), "source root must be an existing directory")
            protected = [source]
            common = subprocess.run(["git", "-C", str(source), "rev-parse", "--git-common-dir"],
                                    capture_output=True, text=True)
            if common.returncode == 0:
                common_path = Path(common.stdout.strip())
                protected.append((common_path if common_path.is_absolute() else source / common_path).resolve())
                worktrees = subprocess.run(["git", "-C", str(source), "worktree", "list", "--porcelain"],
                                           capture_output=True, text=True)
                require(worktrees.returncode == 0, "cannot inspect source worktrees for external state")
                protected.extend(Path(line.removeprefix("worktree ")).resolve() for line in worktrees.stdout.splitlines()
                                 if line.startswith("worktree "))
            require(all(self.directory != root and self.directory not in root.parents and root not in self.directory.parents
                        for root in protected), "state must be separate from the source repository")
        self.path = self.directory / "state.json"

    def load(self, locked=False):
        require(self.path.is_file(), "wizard not initialized")
        if not locked:
            with file_lock(self.directory / "state.lock"):
                return self.load(locked=True)
        state = read_json(self.path)
        require(state.get("schema_version") == 1, "unsupported wizard state")
        return state

    def init(self, definition):
        validate_definition(definition)
        self.directory.mkdir(parents=True, exist_ok=True)
        with file_lock(self.directory / "state.lock"):
            if self.path.exists():
                state = self.load(locked=True)
                require(state["definition_digest"] == digest(definition), "definition changed; use a new state directory")
                return summary(state)
            state = {"schema_version": 1, "session_id": str(uuid.uuid4()), "definition": definition,
                     "definition_digest": digest(definition), "revision": 0, "paused": False, "answers": {}, "events": []}
            atomic_json(self.path, state)
            return summary(state)

    def mutate(self, operation, expected_revision=None):
        require(self.path.is_file(), "wizard not initialized")
        with file_lock(self.directory / "state.lock"):
            state = self.load(locked=True)
            require(expected_revision is None or expected_revision == state["revision"], "progress changed; refresh before submitting")
            operation(state)
            atomic_json(self.path, state)
            return summary(state)

    def record(self, step, value, actor, expected_revision=None):
        return self.mutate(lambda state: apply_answer(state, step, value, actor), expected_revision)

    def pause(self, paused, expected_revision=None):
        def change(state):
            if state["paused"] != paused:
                state["paused"] = paused
                event(state, "paused" if paused else "resumed")
        return self.mutate(change, expected_revision)

    def import_responses(self, packet):
        require(isinstance(packet, dict) and set(packet) == {"schema_version", "session_id", "definition_digest", "answers"}, "invalid response export fields")
        require(type(packet["schema_version"]) is int and packet["schema_version"] == 1, "invalid response export version")
        require(isinstance(packet["answers"], dict), "answers must be an object")
        def change(state):
            require(packet["session_id"] == state["session_id"] and packet["definition_digest"] == state["definition_digest"], "export belongs to another wizard")
            ids = {item["id"] for item in state["definition"]["steps"]}
            require(set(packet["answers"]) <= ids, "unknown step in export")
            for step in state["definition"]["steps"]:
                if step["id"] in packet["answers"]:
                    apply_answer(state, step["id"], packet["answers"][step["id"]], "human")
        return self.mutate(change)


def html(state=None):
    template = (Path(__file__).resolve().parent.parent / "assets" / "wizard.html").read_text(encoding="utf-8")
    return template.replace("__WIZARD_STATE__", encode(state).replace("<", "\\u003c"))


def emit(value):
    print(encode(value), flush=True)


def serve(store, open_browser=False):
    store.load()
    try:
        with file_lock(store.directory / "host.lock", blocking=False):
            token = secrets.token_urlsafe(32)

            class Handler(BaseHTTPRequestHandler):
                def setup(self):
                    super().setup()
                    self.connection.settimeout(5)

                def log_message(self, *_):
                    pass

                def reply(self, status, body, content_type="application/json; charset=utf-8"):
                    payload = body.encode("utf-8")
                    self.send_response(status)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(payload)))
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
                    self.end_headers()
                    self.wfile.write(payload)

                def authorized(self, public=False):
                    expected_host = f"127.0.0.1:{self.server.server_port}"
                    if self.headers.get("Host") != expected_host:
                        return False
                    origin = self.headers.get("Origin")
                    if origin is not None and origin != f"http://{expected_host}":
                        return False
                    return public or secrets.compare_digest(self.headers.get("Authorization", ""), f"Bearer {token}")

                def do_GET(self):
                    if not self.authorized(public=self.path == "/"):
                        return self.reply(403, encode({"error": "local capability required"}))
                    if self.path == "/":
                        return self.reply(200, html(), "text/html; charset=utf-8")
                    if self.path == "/state":
                        return self.reply(200, encode(store.load()))
                    self.reply(404, encode({"error": "not found"}))

                def do_POST(self):
                    if not self.authorized():
                        return self.reply(403, encode({"error": "local capability required"}))
                    try:
                        length = int(self.headers.get("Content-Length", "0"))
                        require(0 < length <= MAX_BODY, "invalid body size")
                        data = json.loads(self.rfile.read(length))
                        require(isinstance(data, dict), "body must be an object")
                        if self.path == "/record":
                            require(set(data) == {"step", "value", "revision"} and type(data["revision"]) is int, "record needs step, value and revision")
                            result = store.record(data["step"], data["value"], "human", data["revision"])
                        elif self.path in ("/pause", "/resume"):
                            require(set(data) == {"revision"} and type(data["revision"]) is int, "revision required")
                            result = store.pause(self.path == "/pause", data["revision"])
                        elif self.path == "/stop":
                            result = {"stopped": True}
                            threading.Thread(target=self.server.shutdown, daemon=True).start()
                        else:
                            return self.reply(404, encode({"error": "not found"}))
                        self.reply(200, encode(result))
                    except (ValueError, KeyError, TypeError) as error:
                        self.reply(409, encode({"error": str(error)}))

            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            server.daemon_threads = True
            url = f"http://127.0.0.1:{server.server_port}/#token={token}"
            host = {"url": url, "port": server.server_port, "token": token}
            atomic_json(store.directory / "host.json", host)
            emit({"serving": True, "attached": False, "url": url})
            if open_browser:
                webbrowser.open(url)
            try:
                server.serve_forever(poll_interval=0.1)
            finally:
                server.server_close()
                (store.directory / "host.json").unlink(missing_ok=True)
    except BlockingIOError:
        # The lock holder may still be binding/writing its endpoint.
        for _ in range(20):
            if (store.directory / "host.json").is_file():
                try:
                    host = read_json(store.directory / "host.json")
                    req = request.Request(f"http://127.0.0.1:{host['port']}/state", headers={"Authorization": f"Bearer {host['token']}"})
                    with request.build_opener(request.ProxyHandler({})).open(req, timeout=0.2) as response:
                        attached = json.load(response)
                    if attached["session_id"] == store.load()["session_id"]:
                        emit({"serving": True, "attached": True, "url": host["url"]})
                        if open_browser:
                            webbrowser.open(host["url"])
                        return
                except (OSError, ValueError, KeyError):
                    pass
            time.sleep(0.05)
        raise WizardError("host is starting; retry attachment")


def stop(store):
    host_path = store.directory / "host.json"
    if not host_path.is_file():
        return {"stopped": False, "reason": "no host"}
    host = read_json(host_path)
    require(type(host.get("port")) is int and 0 < host["port"] < 65536, "invalid local host port")
    endpoint = f"http://127.0.0.1:{host['port']}/stop"
    req = request.Request(endpoint, data=b"{}", headers={"Authorization": f"Bearer {host['token']}", "Content-Type": "application/json"})
    # Explicitly bypass proxy environment settings for this local capability.
    with request.build_opener(request.ProxyHandler({})).open(req, timeout=3) as response:
        return json.load(response)


def interactive(store):
    store.pause(False)
    try:
        while True:
            result = summary(store.load())
            step = result["next"]
            if step is None:
                return result
            print(f"\n{result['completed'] + 1}/{result['total']}: {step['title']}\n{step['instruction']}\nExpected: {step['expected']}", file=sys.stderr)
            if "url" in step:
                print(step["url"], file=sys.stderr)
            if step["response"] == "observation":
                print("Waiting for agent capture; progress is saved.", file=sys.stderr)
                return result
            if step["response"] == "choice":
                print("\n".join(f"{i + 1}. {choice}" for i, choice in enumerate(step["options"])), file=sys.stderr)
            prompt = "Type yes to confirm" if step["response"] == "ack" else "Choice number" if step["response"] == "choice" else "Non-secret response"
            print(f"{prompt} (or /pause): ", end="", flush=True, file=sys.stderr)
            answer = input()
            if answer == "/pause":
                return store.pause(True)
            if step["response"] == "ack":
                if answer.lower() != "yes":
                    continue
                value = True
            elif step["response"] == "choice":
                if not answer.isdigit() or not 1 <= int(answer) <= len(step["options"]):
                    continue
                value = step["options"][int(answer) - 1]
            else:
                if not answer.strip():
                    continue
                value = answer
            store.record(step["id"], value, "human", result["revision"])
    except (EOFError, KeyboardInterrupt):
        return store.pause(True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "status", "record", "pause", "resume", "html", "import", "serve", "stop", "cli"):
        sub = commands.add_parser(name)
        sub.add_argument("--state", required=True, help="Explicit durable state directory (use external runtime storage in personal mode)")
        sub.add_argument("--source-root", help="Source checkout to protect from state writes in personal mode")
        if name == "init":
            sub.add_argument("--definition", required=True)
        elif name == "status":
            sub.add_argument("--since", type=int)
        elif name == "record":
            sub.add_argument("--step", required=True)
            sub.add_argument("--actor", choices=("human", "agent"), required=True)
            values = sub.add_mutually_exclusive_group(required=True)
            values.add_argument("--value")
            values.add_argument("--value-file")
        elif name == "html":
            sub.add_argument("--output", required=True)
        elif name == "import":
            sub.add_argument("--file", required=True, help="JSON export file, or - for stdin")
        elif name == "serve":
            sub.add_argument("--open", action="store_true")
    args = parser.parse_args(argv)
    try:
        store = Store(args.state, args.source_root)
        if args.command == "init":
            result = store.init(read_json(args.definition))
        elif args.command == "status":
            result = summary(store.load(), args.since)
        elif args.command == "record":
            value = read_json(args.value_file) if args.value_file else json.loads(args.value)
            result = store.record(args.step, value, args.actor)
        elif args.command in ("pause", "resume"):
            result = store.pause(args.command == "pause")
        elif args.command == "html":
            output = Path(args.output).resolve()
            require(output != store.path and not output.exists(), "HTML output already exists; choose a new file")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(html(store.load()))
            result = {"html": str(output)}
        elif args.command == "import":
            result = store.import_responses(json.load(sys.stdin) if args.file == "-" else read_json(args.file))
        elif args.command == "serve":
            serve(store, args.open)
            return 0
        elif args.command == "stop":
            result = stop(store)
        else:
            result = interactive(store)
        emit(result)
        return 0
    except KeyboardInterrupt:
        emit({"interrupted": True})
        return 130
    except (WizardError, OSError, ValueError, KeyError, TypeError) as error:
        emit({"error": str(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
