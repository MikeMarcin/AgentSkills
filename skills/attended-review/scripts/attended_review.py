#!/usr/bin/env python3
"""Portable, temporary attended sessions. Python 3.11+, no third-party runtime."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fnmatch
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

VERSION = 1
ASSETS = Path(__file__).resolve().parent.parent / "assets"


class ReviewError(ValueError):
    pass


class WaitTimeout(ReviewError):
    """A bounded wait ended with nothing to report; carries the sequence it watched from."""

    def __init__(self, message, sequence):
        super().__init__(message)
        self.sequence = sequence


MAXIMUM_ATTACHMENTS = 4
MAXIMUM_ATTACHMENT_BYTES = 4 * 1024 * 1024
# One verdict with its images, and headroom for the envelope around them.
MAXIMUM_REQUEST_BYTES = 20 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path, default=None):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".review-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + 8
    while True:
        try:
            path.mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ReviewError(f"Busy lock {path}; retry. After a crash, verify no review command is running before removing this lock directory.")
            time.sleep(0.03)
    try:
        yield
    finally:
        path.rmdir()


def stop_preparation(process):
    """Stop only this command tree; never a shared installation or another host."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.wait()


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{label} must be nonempty text")
    return value


def canonical(candidate):
    """Only review material binds a decision; HEAD and preparation metadata do not."""
    keys = ("id", "revision", "title", "content", "criteria", "options", "media", "resource_versions", "launch", "copy")
    material = {k: candidate[k] for k in keys if k in candidate}
    if "wizard" in candidate:
        material["wizard_instructions"] = candidate["wizard"].get("instructions", "")
    return hashlib.sha256(json.dumps(material, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def manifest(value):
    if not isinstance(value, dict) or value.get("schema_version") != VERSION:
        raise ReviewError("manifest schema_version must be 1")
    if not isinstance(value.get("candidates"), list):
        raise ReviewError("manifest candidates must be an array")
    ids = set()
    for item in value["candidates"]:
        if not isinstance(item, dict):
            raise ReviewError("candidate must be an object")
        allowed = {"id", "title", "revision", "content", "criteria", "resources", "paths", "options", "media", "wizard", "prepare", "metadata", "resource_versions", "launch", "copy"}
        if set(item) - allowed:
            raise ReviewError(f"Unknown candidate fields: {sorted(set(item) - allowed)}")
        cid = require_text(item.get("id"), "candidate id")
        if cid in ids:
            raise ReviewError(f"duplicate candidate {cid}")
        ids.add(cid)
        for key in ("title", "revision"):
            require_text(item.get(key), f"{cid} {key}")
        for key in ("criteria", "resources", "paths"):
            item.setdefault(key, [])
            if not isinstance(item[key], list) or any(not isinstance(v, str) or not v for v in item[key]):
                raise ReviewError(f"{cid} {key} must be an array of nonempty strings")
        if not item["criteria"]:
            raise ReviewError(f"{cid} needs at least one criterion")
        if "content" in item and not isinstance(item["content"], str):
            raise ReviewError(f"{cid} content must be text")
        for pattern in item["paths"]:
            if Path(pattern).is_absolute() or ".." in Path(pattern).parts:
                raise ReviewError("paths must be checkout-relative patterns")
        if "options" in item:
            opts = item["options"]
            if not isinstance(opts, list) or not opts or any(not isinstance(v, str) or not v for v in opts) or len(set(opts)) != len(opts):
                raise ReviewError("options must be unique nonempty strings")
        if "media" in item:
            if not isinstance(item["media"], list):
                raise ReviewError("media must be an array")
            for medium in item["media"]:
                if not isinstance(medium, dict) or medium.get("kind") not in ("image", "audio", "video"):
                    raise ReviewError("media requires image/audio/video kind and a data URL")
                url = medium.get("url", "")
                if not isinstance(url, str) or not url.startswith(f"data:{medium['kind']}/"):
                    raise ReviewError("inline media data URLs keep HTML fully portable")
        versions = item.get("resource_versions", {})
        if not isinstance(versions, dict) or any(k not in item["resources"] or not isinstance(v, str) or not v for k, v in versions.items()):
            raise ReviewError("resource_versions maps declared resources to stable candidate versions")
        if "wizard" in item and (not isinstance(item["wizard"], dict) or any(not isinstance(v, str) for v in item["wizard"].values())):
            raise ReviewError("wizard must contain textual instructions/state/url")
        # A reviewer asked to look at something must be able to open it. A
        # packet that names a path in prose makes them navigate a file tree by
        # hand; this is the command, shown for copying and never run.
        if "launch" in item:
            launch = item["launch"]
            if not isinstance(launch, dict) or set(launch) - {"label", "command"}:
                raise ReviewError("launch holds a label and a command")
            require_text(launch.get("command"), f"{cid} launch command")
            if "label" in launch and not isinstance(launch["label"], str):
                raise ReviewError("launch label must be text")
        # What the candidate asks the reviewer to paste somewhere else: a
        # pull request link, an identifier. Offered for copying, next to the
        # command that opens what they are looking at.
        if "copy" in item:
            values = item["copy"]
            if not isinstance(values, list) or not values:
                raise ReviewError("copy is a nonempty array of labelled values")
            for entry in values:
                if not isinstance(entry, dict) or set(entry) - {"label", "value"}:
                    raise ReviewError("a copied value is a label and a value")
                require_text(entry.get("label"), f"{cid} copy label")
                require_text(entry.get("value"), f"{cid} copy value")
        prep = item.get("prepare")
        if prep is not None:
            if not isinstance(prep, dict) or prep.get("speed", "quick") not in ("quick", "slow"):
                raise ReviewError("prepare must specify quick/slow speed")
            argv = prep.get("argv")
            if not isinstance(argv, list) or not argv or any(not isinstance(v, str) or not v for v in argv):
                raise ReviewError("prepare argv must be a nonempty argument array")
            timeout = prep.get("timeout_seconds", 300)
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
                raise ReviewError("prepare timeout_seconds must be between 0 and 86400")
    return value


class Session:
    def __init__(self, root, registry=None):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ReviewError("checkout root must exist")
        self.directory = self.root / ".mask" / "attended-review"
        self.path = self.directory / "session.json"
        self.registry = Path(registry or os.environ.get("ATTENDED_REVIEW_REGISTRY", Path.home() / ".mask" / "attended-review-resources")).resolve()

    @contextmanager
    def transaction(self):
        # One lock order, including across processes and independent worktrees.
        with lock(self.registry / ".lock"):
            with lock(self.directory / ".lock"):
                state = read_json(self.path)
                resources = read_json(self.registry / "resources.json", {})
                before_state = json.dumps(state, sort_keys=True)
                before_resources = json.dumps(resources, sort_keys=True)
                yield state, resources
                # Publish acquisitions before readiness, and invalidation before
                # releases. A crash at either boundary leaves conservative claims.
                previous_resources = json.loads(before_resources)
                retained = {key: list(entries) for key, entries in previous_resources.items()}
                for key, entries in resources.items():
                    union = retained.setdefault(key, [])
                    union.extend(entry for entry in entries if entry not in union)
                if json.dumps(retained, sort_keys=True) != before_resources:
                    atomic_json(self.registry / "resources.json", retained)
                if state is not None and json.dumps(state, sort_keys=True) != before_state:
                    atomic_json(self.path, state)
                if resources != retained:
                    atomic_json(self.registry / "resources.json", resources)

    def load(self):
        with lock(self.directory / ".lock"):
            state = read_json(self.path)
            if state is None:
                raise ReviewError("No attended session; run init with a manifest")
            return state

    @staticmethod
    def event(state, kind, **fields):
        state["sequence"] += 1
        state["events"].append({"sequence": state["sequence"], "time": now(), "kind": kind, **fields})

    def owner(self, state, cid):
        return {"checkout": str(self.root), "session": state["id"], "candidate": cid}

    def acquire(self, state, resources, item):
        owner = self.owner(state, item["id"])
        for key in item["resources"]:
            entries = resources.get(key, [])
            version = item.get("resource_versions", {}).get(key)
            conflicts = [v for v in entries if not (v["session"] == state["id"] and v["candidate"] == item["id"]) and not (version and v.get("version") == version and v.get("shareable") is True and not item.get("prepare"))]
            if conflicts:
                raise ReviewError(f"Resource {key!r} protected by {conflicts[0]['checkout']} candidate {conflicts[0]['candidate']}; explicitly release there first")
        for key in item["resources"]:
            entries = resources.setdefault(key, [])
            claim = {**owner, "version": item.get("resource_versions", {}).get(key), "shareable": not bool(item.get("prepare"))}
            if claim not in entries:
                entries.append(claim)
        item["protected"] = True

    def release(self, state, resources, item):
        owner = self.owner(state, item["id"])
        for key in list(resources):
            resources[key] = [v for v in resources[key] if any(v.get(k) != value for k, value in owner.items())]
            if not resources[key]:
                del resources[key]
        item["protected"] = False

    def initialize(self, value):
        value = manifest(value)
        # Bootstrap under same locks as all subsequent operations.
        with lock(self.registry / ".lock"):
            with lock(self.directory / ".lock"):
                state = read_json(self.path)
                if state is None:
                    state = {"schema_version": VERSION, "id": secrets.token_hex(16), "checkout": str(self.root), "sequence": 0, "events": [], "candidates": {}, "history": [], "paused": False, "host": None}
                for candidate in value["candidates"]:
                    cid = candidate["id"]
                    fingerprint = canonical(candidate)
                    previous = state["candidates"].get(cid)
                    if previous and previous["fingerprint"] != fingerprint:
                        if previous.get("protected"):
                            raise ReviewError(f"{cid} is protected; resume-development for its affected paths/resources before replacing its candidate")
                        state["history"].append(previous)
                        previous = None
                    if previous:
                        # Changing protection/preparation definitions must be deliberate too.
                        if previous.get("protected") and any(previous.get(k) != candidate.get(k) for k in ("resources", "resource_versions", "paths", "prepare")):
                            raise ReviewError(f"{cid} protection changed; release it before updating")
                        previous.update(candidate)
                    else:
                        state["candidates"][cid] = {**candidate, "fingerprint": fingerprint, "phase": "waiting", "protected": False, "decision": None, "observations": []}
                        state["handed_back"] = None
                    self.event(state, "candidate", candidate=cid, fingerprint=fingerprint)
                atomic_json(self.path, state)
        return self.status()

    def status(self, after=None, full=False):
        state = self.load()
        result = {"session": state["id"], "checkout": state["checkout"], "sequence": state["sequence"], "paused": state["paused"], "handed_back": state.get("handed_back"), "candidates": []}
        for item in state["candidates"].values():
            record = {k: item.get(k) for k in ("id", "title", "revision", "fingerprint", "phase", "protected", "decision")}
            if item.get("superseded"):
                record["superseded"] = item["superseded"]
            if item.get("error"):
                record["error"] = item["error"]
            if full:
                record = dict(item)
            result["candidates"].append(record)
        result["candidates"].sort(key=lambda c: (c["phase"] != "ready", bool(c["decision"]), c["id"]))
        if after is not None:
            result["events"] = [e for e in state["events"] if e["sequence"] > after]
        if state.get("host"):
            result["host"] = state["host"]
        return result

    def ready(self, cid, evidence=None):
        with self.transaction() as (state, resources):
            item = self.item(state, cid)
            if item.get("decision"):
                return
            if item["phase"] in ("preparing", "cancelling"):
                raise ReviewError("Wait for preparation to finish or cancel before marking ready")
            self.acquire(state, resources, item)
            item["phase"] = "ready"
            item.pop("error", None)
            state["handed_back"] = None
            if evidence:
                item["observations"].append({"time": now(), "evidence": evidence})
            self.event(state, "ready", candidate=cid)

    @staticmethod
    def item(state, cid):
        if state is None or cid not in state["candidates"]:
            raise ReviewError(f"Unknown candidate {cid}")
        return state["candidates"][cid]

    def prepare(self, selected=None, include_slow=False, max_items=None):
        snapshot = self.load()
        candidates = [v for v in snapshot["candidates"].values() if not selected or v["id"] in selected]
        candidates.sort(key=lambda v: (bool(v.get("prepare")), v.get("prepare", {}).get("speed", "quick") == "slow", v["id"]))
        processed = 0
        epoch = snapshot.get("preparation_epoch", 0)
        for candidate in candidates:
            cid = candidate["id"]
            if candidate["phase"] in ("ready", "preparing", "cancelling") or candidate.get("decision"):
                continue
            preparation_id = None
            prep = candidate.get("prepare")
            if prep and prep.get("speed") == "slow" and not include_slow:
                continue
            if max_items is not None and processed >= max_items:
                break
            try:
                with self.transaction() as (state, resources):
                    if state.get("preparation_epoch", 0) != epoch:
                        break
                    item = self.item(state, cid)
                    if item.get("preparation_epoch", 0) != candidate.get("preparation_epoch", 0):
                        continue
                    if item["phase"] in ("ready", "preparing", "cancelling") or item.get("decision"):
                        continue
                    prep = item.get("prepare")
                    self.acquire(state, resources, item)
                    item["phase"] = "preparing"
                    item["preparation_id"] = secrets.token_hex(8)
                    preparation_id = item["preparation_id"]
                    self.event(state, "preparing", candidate=cid)
                processed += 1
                evidence = "Static review material prepared"
                if prep:
                    # Argument arrays only; this is an explicit driver command, never HTTP.
                    self.directory.mkdir(parents=True, exist_ok=True)
                    log = self.directory / f"prepare-{preparation_id}.log"
                    with log.open("wb") as output:
                        process = subprocess.Popen(prep["argv"], cwd=self.root, stdout=output, stderr=subprocess.STDOUT, start_new_session=os.name != "nt", creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
                        deadline = time.monotonic() + prep.get("timeout_seconds", 300)
                        try:
                            while process.poll() is None:
                                if time.monotonic() >= deadline:
                                    raise ReviewError(f"Preparation timed out; see {log}")
                                current = self.load()["candidates"][cid]
                                if current.get("preparation_id") != preparation_id or current["phase"] != "preparing":
                                    raise ReviewError("Preparation interrupted by review-start or resume-development")
                                time.sleep(0.15)
                        except BaseException:
                            stop_preparation(process)
                            raise
                    if process.returncode:
                        raise ReviewError(f"Preparation exited {process.returncode}; see {log}")
                    evidence = f"Preparation exit 0; log {log}"
                with self.transaction() as (state, resources):
                    item = self.item(state, cid)
                    if state.get("preparation_epoch", 0) != epoch or item.get("preparation_id") != preparation_id or item["phase"] != "preparing":
                        raise ReviewError("Preparation interrupted before publication")
                    item["phase"] = "ready"
                    item.pop("error", None)
                    state["handed_back"] = None
                    item["observations"].append({"time": now(), "evidence": evidence})
                    self.event(state, "ready", candidate=cid)
            except (ReviewError, OSError, KeyboardInterrupt) as exc:
                with self.transaction() as (state, resources):
                    item = self.item(state, cid)
                    if item["phase"] != "ready" and (preparation_id is None or item.get("preparation_id") == preparation_id):
                        item["phase"] = "waiting"
                        item["error"] = str(exc) or "Preparation interrupted"
                        self.release(state, resources, item)
                        self.event(state, "preparation-stopped", candidate=cid, reason=item["error"])
                if isinstance(exc, KeyboardInterrupt):
                    break
        return self.status()

    def observe(self, cid, evidence):
        require_text(evidence, "evidence")
        with self.transaction() as (state, _):
            item = self.item(state, cid)
            item["observations"].append({"time": now(), "evidence": evidence})
            self.event(state, "observation", candidate=cid, evidence=evidence)
        return self.status()

    def intake(self, payload):
        if not isinstance(payload, dict) or payload.get("schema_version") != VERSION or not isinstance(payload.get("decisions"), list):
            raise ReviewError("decision payload requires schema_version 1 and decisions array")
        with self.transaction() as (state, _):
            if state is None or payload.get("session") != state["id"]:
                raise ReviewError("Decision belongs to a different session")
            accepted = []
            for decision in payload["decisions"]:
                if not isinstance(decision, dict):
                    raise ReviewError("decision must be an object")
                item = self.item(state, decision.get("candidate"))
                if decision.get("fingerprint") != item["fingerprint"]:
                    raise ReviewError(f"Stale decision for {item['id']}; prepare the current candidate")
                require_text(decision.get("decision_id"), "decision_id")
                if decision.get("outcome") not in ("accept", "reject", "select", "withdrawn"):
                    raise ReviewError("outcome must be accept, reject, select or withdrawn; skip/pause are not verdicts")
                if not isinstance(decision.get("note", ""), str):
                    raise ReviewError("decision note must be text")
                attachments = decision.get("attachments", [])
                if not isinstance(attachments, list) or len(attachments) > MAXIMUM_ATTACHMENTS:
                    raise ReviewError(f"a verdict carries at most {MAXIMUM_ATTACHMENTS} attachments")
                for attachment in attachments:
                    if not isinstance(attachment, dict) or set(attachment) - {"name", "data"}:
                        raise ReviewError("an attachment is a name and an inline data URL")
                    require_text(attachment.get("name"), "attachment name")
                    data = attachment.get("data", "")
                    if not isinstance(data, str) or not data.startswith("data:image/"):
                        raise ReviewError("attachments are inline image data URLs")
                    if len(data) > MAXIMUM_ATTACHMENT_BYTES:
                        raise ReviewError("attachment exceeds the per-image bound")
                if "options" in item and decision["outcome"] == "accept":
                    raise ReviewError("Selection group requires select or reject")
                if decision["outcome"] == "select":
                    selected = decision.get("selected")
                    if "options" not in item or not isinstance(selected, list) or not selected or any(not isinstance(v, str) for v in selected) or len(selected) != len(set(selected)) or any(v not in item["options"] for v in selected):
                        raise ReviewError("selected must name nonempty unique group options")
                clean = {k: decision[k] for k in ("candidate", "fingerprint", "decision_id", "outcome", "selected", "note", "attachments") if k in decision}
                if item["phase"] != "ready" or not item.get("protected"):
                    raise ReviewError(f"{item['id']} is not prepared/protected")
                # A reviewer who pressed the wrong button, or thought better of
                # a verdict, can say so. The verdict they land on is the record
                # and every earlier one is kept beside it, so changing a mind
                # costs nothing and hides nothing.
                if item.get("decision"):
                    previous = {k: v for k, v in item["decision"].items() if k not in ("saved_at", "actor")}
                    if previous == clean:
                        continue
                    item.setdefault("superseded", []).append(item["decision"])
                if clean["outcome"] == "withdrawn":
                    item["decision"] = None
                    self.event(state, "decision", candidate=item["id"], decision=None, withdrawn=True)
                    accepted.append(item["id"])
                    continue
                clean.update(saved_at=now(), actor="human")
                item["decision"] = clean
                self.event(state, "decision", candidate=item["id"], decision=clean)
                accepted.append(item["id"])
        return {"accepted": accepted, "sequence": self.load()["sequence"]}

    def hand_back(self):
        """The reviewer has finished. Nothing is decided here; the driver is told."""
        with self.transaction() as (state, _):
            if state is None:
                raise ReviewError("No session")
            decided = sorted(cid for cid, item in state["candidates"].items() if item.get("decision"))
            pending = sorted(cid for cid, item in state["candidates"].items() if not item.get("decision"))
            state["handed_back"] = now()
            self.event(state, "handed-back", decided=decided, pending=pending)
        return {"handed_back": self.load()["handed_back"], "decided": decided, "pending": pending}

    def wait(self, after=None, kinds=("handed-back", "decision"), timeout=None, interval=0.5):
        """Block until the human acts. A driver arms this before ending its turn; the exit is its wake.

        Only the file's modification time is polled while idle. The session file
        is read under the ordinary lock, and only when that time has moved.
        """
        kinds = tuple(kinds) or ("handed-back", "decision")
        state = self.load()
        cursor = state["sequence"] if after is None else after
        deadline = None if timeout is None else time.monotonic() + timeout
        seen = None
        while True:
            try:
                stamp = self.path.stat().st_mtime_ns
            except FileNotFoundError:
                raise ReviewError("Session file removed while waiting") from None
            if stamp != seen:
                seen = stamp
                state = self.load()
                events = [e for e in state["events"] if e["sequence"] > cursor and e["kind"] in kinds]
                if events:
                    return {"session": state["id"], "sequence": state["sequence"], "handed_back": state.get("handed_back"), "events": events}
            if deadline is not None and time.monotonic() >= deadline:
                raise WaitTimeout(f"No {'/'.join(kinds)} event after sequence {cursor} within {timeout:g}s", state["sequence"])
            time.sleep(interval)

    def pause(self, paused=True, interrupt=False):
        with self.transaction() as (state, _):
            if state is None:
                raise ReviewError("No session")
            state["paused"] = paused
            if not paused:
                state["handed_back"] = None
            if interrupt:
                state["preparation_epoch"] = state.get("preparation_epoch", 0) + 1
                for item in state["candidates"].values():
                    if item["phase"] == "preparing":
                        item["phase"] = "cancelling"
            self.event(state, "paused" if paused else "review-start", interrupt_preparation=interrupt)
        return self.status()

    def resume_development(self, paths=(), resource_keys=(), selected=(), all_candidates=False, preparation_stopped=False):
        if not (paths or resource_keys or selected or all_candidates):
            raise ReviewError("Select affected --paths, --resources or --candidate; --all explicitly releases everything")
        with self.transaction() as (state, resources):
            if state is None:
                raise ReviewError("No session")
            affected = []
            for item in state["candidates"].values():
                overlap = all_candidates or item["id"] in selected or set(resource_keys).intersection(item["resources"]) or any(fnmatch.fnmatch(p, pattern) or p == pattern or p.startswith(pattern.rstrip("/") + "/") for p in paths for pattern in item["paths"])
                if overlap:
                    item["preparation_epoch"] = item.get("preparation_epoch", 0) + 1
                    if item["phase"] in ("preparing", "cancelling") and not preparation_stopped:
                        item["phase"] = "cancelling"
                    else:
                        self.release(state, resources, item)
                        item["preparation_id"] = None
                        if not item.get("decision"):
                            item["phase"] = "waiting"
                    affected.append(item["id"])
            if affected:
                state["handed_back"] = None
            self.event(state, "resume-development", candidates=affected, preparation_stopped=preparation_stopped)
        return {"affected": affected, "status": self.status()}

    def conflicts(self, paths=(), resource_keys=()):
        with self.transaction() as (state, resources):
            result = []
            if state:
                for item in state["candidates"].values():
                    if item.get("protected") and any(fnmatch.fnmatch(p, pattern) or p == pattern or p.startswith(pattern.rstrip("/") + "/") for p in paths for pattern in item["paths"]):
                        result.append({"candidate": item["id"], "checkout": str(self.root), "reason": "protected paths"})
            for key in resource_keys:
                result.extend({**v, "resource": key} for v in resources.get(key, []))
        return {"conflicts": result}

    def html(self, output):
        snapshot = self.status(full=True)
        snapshot.pop("host", None)
        # A static file cannot know what was decided after it was written; it
        # says when it was written so nobody mistakes its silence for a record.
        snapshot["generated_at"] = now()
        text = (ASSETS / "review.html").read_text(encoding="utf-8")
        data = json.dumps(snapshot, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        text = text.replace("/*SESSION_DATA*/null", data)
        destination = Path(output).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        return {"html": str(destination), "session": snapshot["session"]}


def host_request(host, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(f"http://127.0.0.1:{host['port']}{path}", data=data, headers={"Authorization": f"Bearer {host['token']}", "Content-Type": "application/json", "Origin": f"http://127.0.0.1:{host['port']}"})
    with urllib.request.urlopen(request, timeout=2) as response:
        return json.loads(response.read())


def serve(session):
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def answer(self, status, value, content_type="application/json"):
            body = json.dumps(value).encode() if content_type == "application/json" else value.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; media-src data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def permitted(self):
            expected = f"127.0.0.1:{self.server.server_port}"
            if self.headers.get("Host") != expected:
                self.answer(403, {"error": "Unexpected host"})
                return False
            origin = self.headers.get("Origin")
            if origin is not None and origin != f"http://{expected}":
                self.answer(403, {"error": "Unexpected origin"})
                return False
            if self.path != "/" and not secrets.compare_digest(self.headers.get("Authorization", ""), f"Bearer {token}"):
                self.answer(403, {"error": "Missing session token"})
                return False
            return True

        def do_GET(self):
            if not self.permitted():
                return
            if self.path == "/":
                html = (ASSETS / "review.html").read_text(encoding="utf-8")
                self.answer(200, html, "text/html")
            elif self.path == "/api/ping":
                self.answer(200, {"token": token})
            elif self.path == "/api/status":
                result = session.status(full=True)
                result.pop("host", None)
                self.answer(200, result)
            else:
                self.answer(404, {"error": "Unknown endpoint"})

        def do_POST(self):
            if not self.permitted():
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAXIMUM_REQUEST_BYTES:
                    raise ReviewError("Request must be between 1 byte and the intake bound")
                value = json.loads(self.rfile.read(length))
                if not isinstance(value, dict):
                    raise ReviewError("Request must be a JSON object")
                if self.path == "/api/decisions":
                    result = session.intake(value)
                elif self.path == "/api/pause":
                    result = session.pause()
                elif self.path == "/api/hand-back":
                    result = session.hand_back()
                elif self.path == "/api/start":
                    result = session.pause(False, interrupt=bool(value.get("interrupt", True)))
                elif self.path == "/api/stop":
                    result = {"stopped": True}
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                else:
                    self.answer(404, {"error": "Unknown endpoint"})
                    return
                self.answer(200, result)
            except (ReviewError, ValueError, TypeError) as exc:
                self.answer(400, {"error": str(exc)})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    host = {"port": server.server_port, "token": token, "pid": os.getpid(), "hostname": socket.gethostname()}
    host["url"] = f"http://127.0.0.1:{host['port']}/#token={token}"
    with session.transaction() as (state, _):
        if state is None:
            server.server_close()
            raise ReviewError("No session")
        previous = state.get("host")
        if previous:
            try:
                ping = host_request(previous, "/api/ping")
                if isinstance(ping, dict) and ping.get("token") == previous["token"]:
                    server.server_close()
                    print(json.dumps({"attached": True, **previous}), flush=True)
                    return
            except (OSError, ValueError):
                pass
        state["host"] = host
    print(json.dumps({"hosting": True, **host}), flush=True)
    try:
        server.serve_forever(poll_interval=.2)
    finally:
        server.server_close()
        with session.transaction() as (state, _):
            if state and (state.get("host") or {}).get("token") == token:
                state["host"] = None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--registry", help="Shared resource registry; all drivers using a resource must use the same registry")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init").add_argument("--manifest", required=True)
    p = sub.add_parser("status"); p.add_argument("--after", type=int); p.add_argument("--full", action="store_true")
    p = sub.add_parser("prepare"); p.add_argument("--candidate", action="append"); p.add_argument("--include-slow", action="store_true"); p.add_argument("--max-items", type=int)
    p = sub.add_parser("ready"); p.add_argument("candidate"); p.add_argument("--evidence", required=True)
    p = sub.add_parser("observe"); p.add_argument("candidate"); p.add_argument("--evidence", required=True)
    sub.add_parser("import").add_argument("--file", required=True, help="JSON path or - for stdin")
    sub.add_parser("html").add_argument("--output", required=True)
    sub.add_parser("pause")
    sub.add_parser("hand-back")
    p = sub.add_parser("wait", help="Block until the reviewer hands back or decides; arm it as a background watch whose exit wakes the driver"); p.add_argument("--after", type=int, help="Sequence cursor; defaults to the current sequence"); p.add_argument("--kind", action="append", default=[], help="Event kind to wait for (repeatable); default handed-back and decision"); p.add_argument("--timeout", type=float, help="Seconds before giving up with exit 1 and the current sequence")
    p = sub.add_parser("start"); p.add_argument("--keep-preparing", action="store_true")
    p = sub.add_parser("resume-development"); p.add_argument("--paths", nargs="*", default=[]); p.add_argument("--resources", nargs="*", default=[]); p.add_argument("--candidate", action="append", default=[]); p.add_argument("--all", action="store_true"); p.add_argument("--preparation-stopped", action="store_true", help="Recovery attestation: driver has verified the interrupted preparation command tree is stopped")
    p = sub.add_parser("conflicts"); p.add_argument("--paths", nargs="*", default=[]); p.add_argument("--resources", nargs="*", default=[])
    sub.add_parser("serve"); sub.add_parser("stop")
    args = parser.parse_args(argv)
    try:
        session = Session(args.repo_root, args.registry)
        command = args.command
        if command == "init": result = session.initialize(read_json(Path(args.manifest)))
        elif command == "status": result = session.status(args.after, args.full)
        elif command == "prepare": result = session.prepare(args.candidate, args.include_slow, args.max_items)
        elif command == "ready": session.ready(args.candidate, args.evidence); result = session.status()
        elif command == "observe": result = session.observe(args.candidate, args.evidence)
        elif command == "import": result = session.intake(json.load(sys.stdin) if args.file == "-" else read_json(Path(args.file)))
        elif command == "html": result = session.html(args.output)
        elif command == "pause": result = session.pause()
        elif command == "hand-back": result = session.hand_back()
        elif command == "wait": result = session.wait(args.after, args.kind, args.timeout)
        elif command == "start": result = session.pause(False, not args.keep_preparing)
        elif command == "resume-development": result = session.resume_development(args.paths, args.resources, args.candidate, args.all, args.preparation_stopped)
        elif command == "conflicts": result = session.conflicts(args.paths, args.resources)
        elif command == "serve": serve(session); return 0
        elif command == "stop":
            host = session.load().get("host")
            result = host_request(host, "/api/stop", {}) if host else {"stopped": False, "reason": "No host"}
        print(json.dumps(result))
        return 0
    except (ReviewError, OSError, ValueError) as exc:
        failure = {"error": str(exc)}
        if isinstance(exc, WaitTimeout):
            failure["sequence"] = exc.sequence
        print(json.dumps(failure), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
