#!/usr/bin/env python3
"""Validate a bounded admission request; only the host hook can admit a turn.

Two request shapes are accepted. v1 carries the whole remote-task envelope as
canonical base64 JSON (``--envelope-base64``). v2 renders the compact
``implement-rfc.remote-task.v2`` envelope as plain flags in a fixed order; the
station identity file supplies project, workstream and branch.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys

MAX_JSON_BYTES = 16 * 1024
MAX_BASE64_CHARS = 4 * ((MAX_JSON_BYTES + 2) // 3)
MAX_COMMAND_CHARS = MAX_BASE64_CHARS + 4096 + 100
TASK_ENVELOPE = "implement-rfc.remote-task.v1"
TASK_ENVELOPE_V2 = "implement-rfc.remote-task.v2"
TASK_ENVELOPES = (TASK_ENVELOPE, TASK_ENVELOPE_V2)
REQUIRED = {
    "envelope", "task_id", "project", "station", "workstream", "branch", "rfcs",
    "cards", "rfc_base_sha", "base_commit", "authority", "id_reservations",
    "reply_to", "done_when",
}
OPTIONAL = {"checkout", "expires_at", "notes"}
# v2 omits what the station identity file already binds. A v2 envelope may still
# name project, workstream, branch or checkout; a named value must then match.
REQUIRED_V2 = {"envelope", "task_id", "station", "base_commit", "authority", "reply_to"}
OPTIONAL_V2 = {
    "rfc_base_sha", "rfcs", "cards", "id_reservations", "expires_at", "done_when",
    "notes", "project", "workstream", "branch", "checkout",
}
FIELDS = {TASK_ENVELOPE: (REQUIRED, OPTIONAL), TASK_ENVELOPE_V2: (REQUIRED_V2, OPTIONAL_V2)}
# The v2 request flags, in their only accepted order: (flag, field, repeatable, required).
V2_FLAGS = (
    ("--task", "task_id", False, True),
    ("--station", "station", False, True),
    ("--base", "base_commit", False, True),
    ("--authority", "authority", False, True),
    ("--reply-to", "reply_to", False, True),
    ("--rfc-base", "rfc_base_sha", False, False),
    ("--rfc", "rfcs", True, False),
    ("--card", "cards", True, False),
    ("--reservation", "id_reservations", True, False),
    ("--expires", "expires_at", False, False),
)
RESERVATION_FIELDS = ("reservation_id", "area", "range", "reservation_commit")
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
# Single spaces between printable, space-free words; values never need quoting.
COMMAND_V2 = re.compile(r'(?:py -3|python3|python) -B "([^"\r\n]+)" (--task [!-~]+(?: [!-~]+)*)')


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
    return validate_envelope(envelope)


def validate_envelope(envelope: object) -> dict:
    """Check one v1 or v2 envelope's field set and the shape of every field."""
    if not isinstance(envelope, dict):
        raise RequestError("remote-task fields are missing or unsupported; caller identity is not accepted")
    if envelope.get("envelope") not in FIELDS:
        raise RequestError("remote-task envelope is invalid")
    required, optional = FIELDS[envelope["envelope"]]
    if required - envelope.keys() or envelope.keys() - required - optional:
        raise RequestError("remote-task fields are missing or unsupported; caller identity is not accepted")
    for name, pattern in PATTERNS.items():
        if name in envelope:
            _pattern(name, envelope[name], pattern)
    if envelope["authority"] not in ("lane-commit", "read-only-proof"):
        raise RequestError("remote-task authority is invalid")
    for name, minimum, maximum in (("done_when", 1, 512), ("checkout", 0, 4096), ("notes", 0, 4096)):
        if name in envelope and (not isinstance(envelope[name], str) or not minimum <= len(envelope[name]) <= maximum):
            raise RequestError(f"remote-task {name} is invalid")
    for name, maximum, pattern in (("rfcs", 64, r"RFC-[A-Z]{2,8}-[0-9]{4}"), ("cards", 256, r"[A-Z]{2,8}-[0-9]{4}")):
        values = envelope.get(name, [])
        if not isinstance(values, list) or len(values) > maximum:
            raise RequestError(f"remote-task {name} is invalid")
        for value in values:
            _pattern(name, value, pattern)
    if envelope.get("rfcs") and "rfc_base_sha" not in envelope:
        raise RequestError("remote-task rfc_base_sha is required when rfcs are named")
    reservations = envelope.get("id_reservations", [])
    if not isinstance(reservations, list) or len(reservations) > 32:
        raise RequestError("remote-task id_reservations is invalid")
    fields = set(RESERVATION_FIELDS)
    for reservation in reservations:
        if not isinstance(reservation, dict) or reservation.keys() != fields:
            raise RequestError("remote-task reservation fields are invalid")
        for name, pattern in (("reservation_id", r"idr-[a-z0-9-]{4,64}"), ("area", r"[A-Z]{2,8}"), ("range", r"[A-Z]{2,8}-[0-9]{4}\.\.[A-Z]{2,8}-[0-9]{4}"), ("reservation_commit", r"[0-9a-f]{40}")):
            _pattern(name, reservation[name], pattern)
    return envelope


def parse_v2_arguments(arguments: list[str]) -> dict:
    """Parse v2 request flags, in their fixed order, into a validated v2 envelope."""
    envelope: dict = {"envelope": TASK_ENVELOPE_V2}
    index = 0
    for flag, field, repeatable, required in V2_FLAGS:
        values: list = []
        while index < len(arguments) and arguments[index] == flag and (repeatable or not values):
            if index + 1 >= len(arguments) or arguments[index + 1].startswith("--"):
                raise RequestError(f"remote-task {flag} needs a value")
            values.append(arguments[index + 1])
            index += 2
        if required and not values:
            raise RequestError(f"remote-task {flag} is required in v2 flag order")
        if not values:
            continue
        if field == "id_reservations":
            parsed = []
            for value in values:
                parts = value.split(":")
                if len(parts) != len(RESERVATION_FIELDS):
                    raise RequestError("remote-task reservation fields are invalid")
                parsed.append(dict(zip(RESERVATION_FIELDS, parts)))
            values = parsed
        envelope[field] = values if repeatable else values[0]
    if index != len(arguments):
        raise RequestError("remote-task v2 flags are unknown, repeated or out of order; caller identity is not accepted")
    return validate_envelope(envelope)


def command_request(command: str) -> tuple[str, dict] | None:
    """Parse exact portable argv, retaining quoted Windows path backslashes."""
    if not isinstance(command, str) or len(command) > MAX_COMMAND_CHARS:
        return None
    match = COMMAND.fullmatch(command)
    match_v2 = None if match else COMMAND_V2.fullmatch(command)
    if match is None and match_v2 is None:
        return None
    script = (match or match_v2).group(1)
    if any(char in script for char in ';|&`$<>%!*?') or len(script) > 4096:
        return None
    if match is not None:
        return script, decode_envelope(match.group(2))
    return script, parse_v2_arguments(match_v2.group(2).split(" "))


def main() -> int:
    if sys.argv[1:2] == ["--task"]:
        try:
            envelope = parse_v2_arguments(sys.argv[1:])
        except RequestError as error:
            print(f"station_task_admission.py: error: {error}", file=sys.stderr)
            return 2
        print(json.dumps({"task_id": envelope["task_id"], "admission": "hook-controlled"}, separators=(",", ":")))
        return 0
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
