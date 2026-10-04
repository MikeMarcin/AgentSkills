#!/usr/bin/env python3
"""Validate a bounded admission request; only the host hook can admit a turn."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re

MAX_JSON_BYTES = 16 * 1024
MAX_BASE64_CHARS = 4 * ((MAX_JSON_BYTES + 2) // 3)
TASK_ENVELOPE = "implement-rfc.remote-task.v1"
REQUIRED = {
    "envelope", "task_id", "project", "station", "workstream", "branch", "rfcs",
    "cards", "rfc_base_sha", "base_commit", "authority", "id_reservations",
    "reply_to", "done_when",
}
OPTIONAL = {"checkout", "expires_at", "notes"}
PATTERNS = {
    "task_id": r"task-[0-9a-z-]{4,64}",
    "project": r"[a-z0-9]+(?:-[a-z0-9]+)*",
    "station": r"[a-z0-9]+(?:-[a-z0-9]+)+",
    "workstream": r"[a-z0-9]+(?:-[a-z0-9]+)*",
    "branch": r"[A-Za-z0-9._/-]{1,255}",
    "rfc_base_sha": r"[0-9a-f]{40}",
    "base_commit": r"[0-9a-f]{40}",
    "reply_to": r"[a-z0-9]+(?:-[a-z0-9]+)+",
    "expires_at": r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})",
}
COMMAND = re.compile(
    r'(?:py -3|python3|python) -B "([^"\r\n]+)" --envelope-base64 ([A-Za-z0-9+/]+={0,2})'
)


class RequestError(ValueError):
    pass


def _object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise RequestError(f"remote-task repeats field {key}")
        result[key] = value
    return result


def _pattern(name: str, value: object, pattern: str) -> None:
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise RequestError(f"remote-task {name} is invalid")


def decode_envelope(encoded: str) -> dict:
    if not isinstance(encoded, str) or not 1 <= len(encoded) <= MAX_BASE64_CHARS:
        raise RequestError("admission payload exceeds its base64 size bound")
    try:
        raw = base64.b64decode(encoded, validate=True)
        if len(raw) > MAX_JSON_BYTES or base64.b64encode(raw).decode("ascii") != encoded:
            raise RequestError("admission payload is oversized or noncanonical base64")
        envelope = json.loads(raw.decode("utf-8"), object_pairs_hook=_object)
    except (binascii.Error, UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise RequestError("admission payload must be base64 UTF-8 JSON") from error
    if not isinstance(envelope, dict) or REQUIRED - envelope.keys() or envelope.keys() - REQUIRED - OPTIONAL:
        raise RequestError("remote-task fields are missing or unsupported; caller identity is not accepted")
    if envelope["envelope"] != TASK_ENVELOPE:
        raise RequestError("remote-task envelope is invalid")
    for name, pattern in PATTERNS.items():
        if name in envelope:
            _pattern(name, envelope[name], pattern)
    if envelope["authority"] not in ("lane-commit", "read-only-proof"):
        raise RequestError("remote-task authority is invalid")
    for name, minimum, maximum in (("done_when", 1, 512), ("checkout", 0, 4096), ("notes", 0, 4096)):
        if name in envelope and (not isinstance(envelope[name], str) or not minimum <= len(envelope[name]) <= maximum):
            raise RequestError(f"remote-task {name} is invalid")
    for name, maximum, pattern in (("rfcs", 64, r"RFC-[A-Z]{2,8}-[0-9]{4}"), ("cards", 256, r"[A-Z]{2,8}-[0-9]{4}")):
        values = envelope[name]
        if not isinstance(values, list) or len(values) > maximum:
            raise RequestError(f"remote-task {name} is invalid")
        for value in values:
            _pattern(name, value, pattern)
    reservations = envelope["id_reservations"]
    if not isinstance(reservations, list) or len(reservations) > 32:
        raise RequestError("remote-task id_reservations is invalid")
    fields = {"reservation_id", "area", "range", "reservation_commit"}
    for reservation in reservations:
        if not isinstance(reservation, dict) or reservation.keys() != fields:
            raise RequestError("remote-task reservation fields are invalid")
        for name, pattern in (("reservation_id", r"idr-[a-z0-9-]{4,64}"), ("area", r"[A-Z]{2,8}"), ("range", r"[A-Z]{2,8}-[0-9]{4}\.\.[A-Z]{2,8}-[0-9]{4}"), ("reservation_commit", r"[0-9a-f]{40}")):
            _pattern(name, reservation[name], pattern)
    return envelope


def command_request(command: str) -> tuple[str, dict] | None:
    """Parse exact portable argv, retaining quoted Windows path backslashes."""
    if not isinstance(command, str) or len(command) > MAX_BASE64_CHARS + 4096 + 100:
        return None
    match = COMMAND.fullmatch(command)
    if match is None:
        return None
    script, encoded = match.groups()
    if any(char in script for char in ';|&`$<>%!*?') or len(script) > 4096:
        return None
    return script, decode_envelope(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--envelope-base64", required=True)
    args = parser.parse_args()
    try:
        envelope = decode_envelope(args.envelope_base64)
    except RequestError as error:
        parser.error(str(error))
    print(json.dumps({"schema": "implement-rfc.admission-request.v1", "task_id": envelope["task_id"], "admission": "hook-controlled"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
