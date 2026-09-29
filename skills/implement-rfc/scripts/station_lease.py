#!/usr/bin/env python3
"""Exclusive writer lease for remote stations and the project integrator.

`run` wraps a command in an OS-level exclusive lock that lives exactly as long
as the wrapped process, so a second writer is denied mechanically and a crash
releases the lease without cleanup. `status` reports whether a lease is held
and by whom. The lease guarantees single-writer per scope; it does not
authenticate the writer — ownership rules and push credentials do that.

Scopes:
- station-writer: one writer per checkout (lock lives in the checkout's own
  git dir, so each worktree leases independently).
- project-integrator: one integrator per repository (lock lives in the common
  git dir, shared by every worktree).

Exit codes: 0 success/free, 10 held (status), 75 lease denied (run),
2 usage or environment error.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import hashlib
import os
import socket
import secrets
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, build_opener, ProxyHandler
import subprocess
import sys
from pathlib import Path

ROLES = ("station-writer", "project-integrator")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_config  # noqa: E402


if os.name == "posix":
    import fcntl

    def _try_lock(fd: int) -> bool:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)

else:  # native Windows
    import msvcrt

    def _try_lock(fd: int) -> bool:
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _unlock(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)


def _git_dir(role: str, repo: Path) -> Path:
    flag = "--git-common-dir" if role == "project-integrator" else "--git-dir"
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", flag],
        env=project_config.git_environment(),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(f"not a git repository: {repo}\n{proc.stderr}")
        raise SystemExit(2)
    path = Path(proc.stdout.strip())
    if not path.is_absolute():
        path = (repo / path).resolve()
    return path


def _lock_path(role: str, repo: Path, config: dict) -> Path:
    context = project_config.resolve_context(repo_root=repo)
    if context.mode == "personal":
        scope = "common" if role == "project-integrator" else hashlib.sha256(str(repo.resolve()).encode()).hexdigest()
        from slice_model import inside
        path = inside(context.runtime_root, f"leases/{scope}-{role}.lock")
        inside(context.runtime_root, str(path.with_suffix(".holder.json").relative_to(context.runtime_root)))
        return path
    return _git_dir(role, repo) / f"{config['project']}-{role}.lock"


def _holder_path(lock_path: Path) -> Path:
    return lock_path.with_suffix(".holder.json")


def _holder_record(args: argparse.Namespace, command: list[str]) -> dict:
    return {
        "schema": "implement-rfc.station-lease.v1",
        "project": args.context.config["project"],
        "role": args.role,
        "station": args.station,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "command": command[0] if command else None,
        "acquired_at": _dt.datetime.now(_dt.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    }


def _read_holder(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
        return text or "(no holder record)"
    except OSError:
        return "(no holder record)"


def _public_holder(text):
    try:
        holder = json.loads(text)
    except ValueError:
        return '(unreadable holder record)'
    if isinstance(holder, dict) and isinstance(holder.get('control'), dict):
        holder['control'] = dict(holder['control'], token='[redacted]')
    return json.dumps(holder)


def cmd_run(args: argparse.Namespace) -> int:
    if not args.command:
        sys.stderr.write("run: missing command after --\n")
        return 2
    path = _lock_path(args.role, args.repo, args.context.config)
    holder_path = _holder_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    if not _try_lock(fd):
        sys.stderr.write(
            f"{args.role} lease is held; refusing a second writer.\n"
            f"holder: {_public_holder(_read_holder(holder_path))}\n"
        )
        os.close(fd)
        return 75
    if getattr(args, "controlled", False):
        return _run_controlled(args, fd, holder_path)
    record = json.dumps(_holder_record(args, args.command), indent=2) + "\n"
    holder_path.write_text(record, encoding="utf-8")
    if os.name == "posix":
        # Drop close-on-exec so the lock outlives the exec into the command.
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, flags & ~fcntl.FD_CLOEXEC)
        try:
            os.execvp(args.command[0], args.command)
        except OSError as error:
            sys.stderr.write(f"exec failed: {error}\n")
            return 2
    proc = subprocess.run(args.command)
    _unlock(fd)
    os.close(fd)
    return proc.returncode


def snapshot(repo, role, context):
    path = _lock_path(role, repo, context.config)
    if not path.exists():
        return dict(held=False, holder=None)
    fd = os.open(path, os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0))
    try:
        free = _try_lock(fd)
        if free:
            _unlock(fd)
        try:
            holder = json.loads(_read_holder(_holder_path(path)))
        except ValueError:
            holder = None
        return dict(held=not free, holder=holder, stale_holder=free and holder is not None)
    finally:
        os.close(fd)


def _run_controlled(args, fd, holder_path):
    """The lease owner stops only its own child process group, never a sidecar PID."""
    if os.name != 'posix':
        sys.stderr.write('Controlled supervisor stop is unavailable on this host; use the owning terminal.\n')
        os.close(fd)
        return 2
    token = secrets.token_hex(32)
    stopping = threading.Event()
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if (self.path != '/stop' or self.headers.get('Authorization') != 'Bearer ' + token
                    or self.headers.get('X-Station') != args.station):
                self.send_error(403)
                return
            stopping.set()
            self.send_response(202)
            self.end_headers()
        def log_message(self, *unused):
            pass
    server = HTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    record = _holder_record(args, args.command)
    record['control'] = dict(port=server.server_port, token=token, protocol='implement-rfc.supervisor-stop.v1')
    holder_path.write_text(json.dumps(record, indent=2) + '\n')
    holder_path.chmod(0o600)
    child = None
    worker.start()
    try:
        child = subprocess.Popen(args.command, start_new_session=True, pass_fds=(fd,))
        while child.poll() is None and not stopping.wait(0.1):
            pass
        # A completed parent may have left descendants. Reconcile its owned group
        # on every exit, with the lease retained until that group has stopped.
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            try:
                os.killpg(child.pid, 0)
            except ProcessLookupError:
                record['stop_result'] = dict(commands_stopped=True, child_group=child.pid)
                holder_path.write_text(json.dumps(record, indent=2) + '\n')
                break
            time.sleep(0.1)
        return 0 if stopping.is_set() else child.returncode
    except KeyboardInterrupt:
        if child is not None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
        return 130
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
        _unlock(fd)
        os.close(fd)


def stop_supervisor(repo, role, context, station):
    observed = snapshot(repo, role, context)
    if not observed['held']:
        return observed
    holder = observed['holder']
    control = holder.get('control') if isinstance(holder, dict) else None
    if (holder is None or holder.get('station') != station or holder.get('project') != context.config['project']
            or holder.get('role') != role or not isinstance(control, dict)
            or control.get('protocol') != 'implement-rfc.supervisor-stop.v1'
            or type(control.get('port')) is not int or not 1 <= control['port'] <= 65535
            or not isinstance(control.get('token'), str) or len(control['token']) != 64):
        raise ValueError('Stop the recorded station supervisor in its owning terminal (Ctrl+C), then rerun takeover; no trusted stop control is available.')
    request = Request(f"http://127.0.0.1:{control['port']}/stop", data=b'',
                      headers={'Authorization': 'Bearer ' + control['token'], 'X-Station': station}, method='POST')
    with build_opener(ProxyHandler({})).open(request, timeout=3) as response:
        if response.status != 202:
            raise ValueError('Supervisor did not accept scoped stop; stop it in its owning terminal.')
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        observed = snapshot(repo, role, context)
        if not observed['held']:
            final_holder = observed.get('holder')
            stopped = (isinstance(final_holder, dict) and final_holder.get('control') == control
                       and final_holder.get('stop_result', {}).get('commands_stopped') is True)
            return dict(observed, controlled_stop=stopped)
        time.sleep(0.1)
    raise ValueError('Supervisor lease remains held after stop. Stop remaining commands in its owning terminal and retry; the lock is preserved.')


def cmd_status(args):
    observed = snapshot(args.repo, args.role, args.context)
    if getattr(args, 'json', False):
        # The stop token remains private to the helper, even in JSON status.
        holder = dict(observed['holder']) if isinstance(observed['holder'], dict) else None
        if holder and 'control' in holder:
            holder['control'] = dict(holder['control'], token='[redacted]')
        print(json.dumps(dict(observed, holder=holder)))
    else:
        print(f"{args.role}: {'held' if observed['held'] else 'free'}")
        if observed['held']:
            print(_public_holder(json.dumps(observed['holder'])))
    return 10 if observed['held'] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--role", choices=ROLES, default="station-writer")
        p.add_argument("--repo", "--repo-root", dest="repo", type=Path, default=None)

    run_p = sub.add_parser("run", help="acquire the lease and run a command")
    common(run_p)
    run_p.add_argument("--station", default=None, help="station name for the holder record")
    run_p.add_argument("--controlled", action="store_true", help="enable scoped stop of this supervisor on POSIX")
    run_p.add_argument("command", nargs=argparse.REMAINDER, help="-- command to wrap")

    status_p = sub.add_parser("status", help="report the lease state")
    common(status_p)
    status_p.add_argument("--json", action="store_true")
    status_p.set_defaults(station=None)

    args = parser.parse_args(argv)
    try:
        args.context = project_config.resolve_context(repo_root=args.repo)
    except project_config.ProjectConfigError as error:
        parser.error(str(error))
    args.repo = args.context.source_root
    if args.mode == "run":
        if args.command and args.command[0] == "--":
            args.command = args.command[1:]
        return cmd_run(args)
    return cmd_status(args)


if __name__ == "__main__":
    raise SystemExit(main())
