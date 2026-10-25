#!/usr/bin/env python3
"""Per-section token cost of remote-station turns from recorded transcripts.

Evidence for RFC-ASK-0017 AC09 (ASK-0128). Reads, never writes, a Codex rollout
(``.jsonl`` or ``.jsonl.zst``) and a Claude Code session transcript, and prints a
redacted JSON report: token counts and digests only, no transcript text.

Sections of one station turn:

- ``transport_wrapper``: the ``<codex_delegation>`` tags around a delegated prompt.
- ``fenced_envelope``: a fenced remote-task envelope block in the prompt.
- ``admission_command``: the ``station_task_admission.py --envelope-base64`` line
  in the prompt.
- ``dispatch_prose_repeated``: prompt sentences (at least 40 characters) already
  sent verbatim in an earlier prompt of the same thread.
- ``dispatch_prose_novel``: the rest of the prompt.
- ``model_admission_echo``: the station model's own tool call that re-types the
  admission command (generated output tokens).
- ``admission_helper_output``: what the admission helper printed back.
- ``hook_context``: guard hook ``additionalContext`` injected into the turn.

``--format v2`` re-expresses the same turns in the compact v2 protocol: the
envelope is rebuilt as ``implement-rfc.remote-task.v2`` without the fields the
station identity file supplies, the admission command, helper output and hook
acknowledgement take their v2 shapes, and everything else is unchanged. Prose is
never rewritten.

Tokenizer: ``o200k_base`` through tiktoken when importable (the report records
the version and a fixed probe); otherwise a documented ``chars/4`` proxy.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import re
import sys

SENTENCE = re.compile(r"(?<=[.!?;:])\s+|\n+")
PAYLOAD = re.compile(r"--envelope-base64 ([A-Za-z0-9+/]+={0,2})")
FENCED = re.compile(r"```(?:yaml|yml|json)?\s*\n(.*?)\n```", re.DOTALL)
WRAPPER = re.compile(r"^(<codex_delegation>\s*<source_thread_id>[^<]*</source_thread_id>\s*<input>)(.*)(</input>\s*</codex_delegation>)\s*$", re.DOTALL)
SECTIONS = (
    "transport_wrapper",
    "fenced_envelope",
    "admission_command",
    "dispatch_prose_repeated",
    "dispatch_prose_novel",
    "model_admission_echo",
    "admission_helper_output",
    "hook_context",
)
STATION_FIELDS = ("project", "station", "workstream", "branch", "checkout")


class Tokenizer:
    def __init__(self, requested: str):
        self.name = "chars/4"
        self.detail: dict = {"rule": "ceil(len(text) / 4) Unicode code points"}
        self._encode = None
        if requested == "o200k":
            try:
                import tiktoken  # type: ignore
            except ImportError:
                self.detail["fallback_reason"] = "tiktoken not importable"
            else:
                encoding = tiktoken.get_encoding("o200k_base")
                self._encode = encoding.encode
                probe = "envelope: implement-rfc.remote-task.v1 eyJlbnZlbG9wZSI6"
                self.name = "o200k_base"
                self.detail = {
                    "library": "tiktoken",
                    "version": tiktoken.__version__,
                    "probe_text": probe,
                    "probe_tokens": len(encoding.encode(probe)),
                }

    def count(self, text: str) -> int:
        if not text:
            return 0
        if self._encode is not None:
            return len(self._encode(text, disallowed_special=()))
        return -(-len(text) // 4)


def read_jsonl(path: pathlib.Path):
    if path.suffix == ".zst":
        from compression import zstd  # Python 3.14+

        stream = zstd.open(path, "rt", encoding="utf-8")
    else:
        stream = path.open(encoding="utf-8")
    with stream:
        for number, line in enumerate(stream, 1):
            yield number, json.loads(line)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def message_text(payload: dict) -> str:
    return "".join(
        part.get("text", "") for part in payload.get("content", []) if isinstance(part, dict)
    )


def tool_output_text(payload: dict) -> str:
    output = payload.get("output")
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        return "".join(part.get("text", "") for part in output if isinstance(part, dict))
    return ""


def decode_envelope(encoded: str) -> dict | None:
    try:
        value = json.loads(base64.b64decode(encoded, validate=True).decode("utf-8"))
    except (ValueError, UnicodeError):
        return None
    return value if isinstance(value, dict) else None


def fenced_envelopes(text: str) -> list[tuple[str, dict | None]]:
    found = []
    for block in FENCED.findall(text):
        if "implement-rfc.remote-task" not in block:
            continue
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            parsed = None
        found.append((block, parsed if isinstance(parsed, dict) else None))
    return found


# --- v2 re-expression (mirrors skills/remote-station v2 exactly) ---------------
# Envelope: implement-rfc.remote-task.v2 without the station-file fields
# (project, workstream, branch, checkout), without empty lists, and without
# rfc_base_sha when no RFC is named. done_when and notes are kept as recorded.
# Admission: the v2 plain-flag request in place of --envelope-base64. A prompt
# that carried both a fenced envelope and a request line keeps only the line.
# Helper output: the v2 one-object line. Hook context: the one-line ack.


def compact_envelope(envelope: dict) -> dict:
    compact = {"envelope": "implement-rfc.remote-task.v2"}
    for key, value in envelope.items():
        if key == "envelope" or key in STATION_FIELDS:
            continue
        if key in ("rfcs", "cards", "id_reservations") and value == []:
            continue
        if key == "rfc_base_sha" and not envelope.get("rfcs"):
            continue
        compact[key] = value
    return compact


def v2_fenced(envelope: dict) -> str:
    return "```json\n" + json.dumps(compact_envelope(envelope), indent=2, ensure_ascii=False) + "\n```"


def v2_flags(envelope: dict) -> str:
    words = ["--task", envelope["task_id"], "--station", envelope["station"], "--base", envelope["base_commit"],
             "--authority", envelope["authority"], "--reply-to", envelope["reply_to"]]
    if envelope.get("rfcs"):
        words += ["--rfc-base", envelope["rfc_base_sha"]]
    for flag, field in (("--rfc", "rfcs"), ("--card", "cards")):
        for value in envelope.get(field, []):
            words += [flag, value]
    for item in envelope.get("id_reservations", []):
        words += ["--reservation", ":".join(item[key] for key in ("reservation_id", "area", "range", "reservation_commit"))]
    if envelope.get("expires_at"):
        words += ["--expires", envelope["expires_at"]]
    return " ".join(words)


def v2_payload_line(text: str, match: re.Match, envelope: dict) -> str:
    """Replace '--envelope-base64 PAYLOAD' by the v2 flags; the rest is unchanged."""
    return text[: match.start(0)] + v2_flags(envelope) + text[match.end(0):]


def v2_parses(envelope: dict) -> bool:
    """Prove the re-expressed request is one the skill's own parser admits as syntax."""
    scripts = pathlib.Path(__file__).resolve().parents[5] / "skills" / "remote-station" / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        import station_task_admission as admission  # noqa: PLC0415
    finally:
        sys.path.remove(str(scripts))
    command = f'py -3 -B "C:\\fixture\\station_task_admission.py" {v2_flags(envelope)}'
    try:
        parsed = admission.command_request(command)
    except admission.RequestError:
        return False
    return parsed is not None and parsed[1]["task_id"] == envelope["task_id"]


def v2_helper_output(envelope: dict) -> str:
    return json.dumps({"task_id": envelope.get("task_id"), "admission": "hook-controlled"}, separators=(",", ":"))


def v2_hook_ack(envelope: dict) -> str:
    receipt = hashlib.sha256(envelope["task_id"].encode()).hexdigest()[:16]
    return f"Remote-task {envelope['task_id']} accepted for this turn ({envelope['authority']}); receipt {receipt}."


# --- measurement ----------------------------------------------------------------


def split_prose(prose: str, seen: set[str]) -> tuple[str, str]:
    repeated, novel = [], []
    for sentence in SENTENCE.split(prose):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) >= 40 and sentence in seen:
            repeated.append(sentence)
        else:
            novel.append(sentence)
    return "\n".join(repeated), "\n".join(novel)


def remember(prose: str, seen: set[str]) -> None:
    for sentence in SENTENCE.split(prose):
        sentence = sentence.strip()
        if len(sentence) >= 40:
            seen.add(sentence)


def measure_codex(path: pathlib.Path, station: dict, fmt: str, tok: Tokenizer) -> dict:
    turns: list[dict] = []
    current: dict | None = None
    seen: set[str] = set()
    turn_id = None
    for number, record in read_jsonl(path):
        kind, payload = record.get("type"), record.get("payload")
        if kind == "turn_context":
            turn_id = payload.get("turn_id")
            continue
        if not isinstance(payload, dict):
            continue
        if kind == "token_usage_record" and current is not None and payload.get("turn_id") == current["turn_id"]:
            current["model_requests"] += 1
            for name in current["_pending"]:
                current["_carried_requests"][name] = current["_carried_requests"].get(name, 0) + 1
            continue
        if kind != "response_item":
            continue
        item = payload.get("type")
        if item == "function_call_output" and payload.get("name") == "send_message_to_thread":
            text = tool_output_text(payload)
            wrapped = WRAPPER.match(text)
            if wrapped is None:
                continue
            head, body, tail = wrapped.groups()
            current = {
                "line": number,
                "turn_id": turn_id,
                "prompt_sha256_16": digest(body),
                "task_id": None,
                "envelope_forms": [],
                "model_requests": 0,
                "_texts": {name: [] for name in SECTIONS},
                "_pending": set(),
                "_carried_requests": {},
                "_envelope": None,
            }
            turns.append(current)
            current["_texts"]["transport_wrapper"].append(head + tail)
            prose = body
            for block, parsed in fenced_envelopes(body):
                current["envelope_forms"].append("fenced")
                envelope = parsed
                current["_envelope"] = current["_envelope"] or envelope
                if fmt == "v2" and envelope and PAYLOAD.search(body):
                    replacement = ""  # v2 dispatch sends the request line only
                elif fmt == "v2" and envelope:
                    replacement = v2_fenced(envelope)
                else:
                    replacement = "```json\n" + block + "\n```"
                current["_texts"]["fenced_envelope"].append(replacement)
                prose = prose.replace(block, "")
            for line in body.splitlines():
                match = PAYLOAD.search(line)
                if match is None:
                    continue
                # Plain argv or a {"cmd": ...} object: the whole line is protocol.
                current["envelope_forms"].append("admission-command")
                envelope = decode_envelope(match.group(1))
                current["_envelope"] = envelope or current["_envelope"]
                current["_texts"]["admission_command"].append(
                    v2_payload_line(line, match, envelope) if (fmt == "v2" and envelope) else line
                )
                if fmt == "v2" and envelope:
                    current.setdefault("_parsed", []).append(v2_parses(envelope))
                prose = prose.replace(line, "")
            prose = re.sub(r"```(?:json|yaml|yml)?\s*\n\s*\n```", "", prose)
            repeated, novel = split_prose(prose, seen)
            remember(prose, seen)
            current["_texts"]["dispatch_prose_repeated"].append(repeated)
            current["_texts"]["dispatch_prose_novel"].append(novel)
            if current["_envelope"]:
                current["task_id"] = current["_envelope"].get("task_id")
            current["_pending"] = {
                name for name in SECTIONS if any(current["_texts"][name])
            }
            continue
        if current is None or turn_id != current["turn_id"]:
            continue
        if item == "custom_tool_call" or item == "function_call":
            text = payload.get("input") or payload.get("arguments") or ""
            match = PAYLOAD.search(text)
            if match:
                envelope = decode_envelope(match.group(1))
                echoed = v2_payload_line(text, match, envelope) if (fmt == "v2" and envelope) else text
                current["_texts"]["model_admission_echo"].append(echoed)
                current["_pending"].add("model_admission_echo")
                current["_admission_call"] = payload.get("call_id")
            continue
        if item in ("custom_tool_call_output", "function_call_output") and payload.get("call_id") == current.get("_admission_call"):
            text = tool_output_text(payload)
            if fmt == "v2" and current["_envelope"] and "implement-rfc.admission-request.v1" in text:
                original = '{\\"schema\\": \\"implement-rfc.admission-request.v1\\", \\"task_id\\": \\"%s\\", \\"admission\\": \\"hook-controlled\\"}' % current["_envelope"].get("task_id")
                text = text.replace(original, v2_helper_output(current["_envelope"]).replace('"', '\\"'))
            current["_texts"]["admission_helper_output"].append(text)
            current["_pending"].add("admission_helper_output")
            continue
        if item == "message" and payload.get("role") == "developer":
            kinds = (payload.get("internal_chat_message_metadata_passthrough") or {}).get("content_item_kinds") or []
            text = message_text(payload)
            if "hooks.additional_context" in kinds or text.startswith("Remote-task "):
                if fmt == "v2" and text.startswith("Remote-task admission accepted") and current["_envelope"]:
                    text = v2_hook_ack(current["_envelope"])
                current["_texts"]["hook_context"].append(text)
                current["_pending"].add("hook_context")
    return finish(turns, tok)


def finish(turns: list[dict], tok: Tokenizer) -> dict:
    station_turns = [turn for turn in turns if turn["envelope_forms"]]
    totals = {name: 0 for name in SECTIONS}
    carried = {name: 0 for name in SECTIONS}
    rows = []
    for turn in station_turns:
        counts = {name: sum(tok.count(text) for text in turn["_texts"][name]) for name in SECTIONS}
        for name in SECTIONS:
            totals[name] += counts[name]
            carried[name] += counts[name] * turn["_carried_requests"].get(name, 0)
        rows.append(
            {
                "line": turn["line"],
                "turn_id": turn["turn_id"],
                "task_id": turn["task_id"],
                "prompt_sha256_16": turn["prompt_sha256_16"],
                "envelope_forms": sorted(set(turn["envelope_forms"])),
                "model_requests": turn["model_requests"],
                "tokens": counts,
                "total": sum(counts.values()),
            }
        )
    station_overhead = (
        "fenced_envelope", "admission_command", "model_admission_echo",
        "admission_helper_output", "hook_context",
    )
    grand = sum(totals.values())
    overhead = sum(totals[name] for name in station_overhead)
    parsed = [ok for turn in station_turns for ok in turn.get("_parsed", [])]
    report = {
        "delegated_prompts": len(turns),
        "station_task_turns": len(station_turns),
        "sum_tokens": totals,
        "sum_total": grand,
        "station_protocol_tokens": overhead,
        "station_protocol_share": round(overhead / grand, 4) if grand else 0.0,
        "mean_per_turn": {name: round(totals[name] / len(station_turns), 1) for name in SECTIONS} if station_turns else {},
        "mean_station_protocol_per_turn": round(overhead / len(station_turns), 1) if station_turns else 0.0,
        "re_read_tokens_within_turn": carried,
        "turns": rows,
    }
    if parsed:
        report["v2_requests_admissible_by_skill_parser"] = f"{sum(parsed)}/{len(parsed)}"
    return report


def payload_analysis(path: pathlib.Path, station: dict, tok: Tokenizer) -> dict:
    """Where the admission payload's tokens go, measured before any design.

    Per field: tokens the base64 payload loses when that one field is removed.
    Encodings: the same recorded envelopes rendered readable, base64 without
    station-invariant fields, and plain argv.
    """
    def b64(value: dict) -> str:
        return base64.b64encode(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()).decode()

    fields: dict[str, int] = {}
    sums = {"base64_payload": 0, "readable_json": 0, "base64_without_station_fields": 0,
            "base64_without_station_fields_or_prose": 0, "plain_argv_values": 0}
    count = 0
    for _, record in read_jsonl(path):
        payload = record.get("payload")
        if record.get("type") != "response_item" or not isinstance(payload, dict):
            continue
        if payload.get("name") != "send_message_to_thread":
            continue
        match = PAYLOAD.search(tool_output_text(payload))
        envelope = decode_envelope(match.group(1)) if match else None
        if envelope is None:
            continue
        count += 1
        encoded = match.group(1)
        full = tok.count(encoded)
        sums["base64_payload"] += full
        sums["readable_json"] += tok.count(json.dumps(envelope, separators=(",", ":"), ensure_ascii=False))
        for key in envelope:
            rest = {name: value for name, value in envelope.items() if name != key}
            fields[key] = fields.get(key, 0) + full - tok.count(b64(rest))
        lean = {k: v for k, v in envelope.items() if k not in STATION_FIELDS + ("envelope",) and v != []}
        sums["base64_without_station_fields"] += tok.count(b64(lean))
        sums["base64_without_station_fields_or_prose"] += tok.count(
            b64({k: v for k, v in lean.items() if k not in ("done_when", "notes")}))
        argv = [envelope.get("task_id", ""), envelope.get("station", ""), envelope.get("base_commit", ""),
                envelope.get("authority", ""), envelope.get("reply_to", "")]
        if envelope.get("rfcs"):
            argv += [envelope.get("rfc_base_sha", ""), *envelope["rfcs"]]
        argv += envelope.get("cards", []) + ([envelope["expires_at"]] if envelope.get("expires_at") else [])
        sums["plain_argv_values"] += tok.count(" ".join(str(item) for item in argv))
    return {
        "payloads": count,
        "sum_tokens": sums,
        "mean_tokens": {name: round(value / count, 1) for name, value in sums.items()} if count else {},
        "base64_field_cost_sum": dict(sorted(fields.items(), key=lambda item: -item[1])),
    }


def measure_claude(path: pathlib.Path, tok: Tokenizer) -> dict:
    prompts, hooks = [], []
    for _, record in read_jsonl(path):
        if record.get("type") == "user":
            content = record.get("message", {}).get("content")
            if isinstance(content, str):
                prompts.append(content)
            elif isinstance(content, list):
                prompts.extend(part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text")
        elif record.get("type") == "attachment":
            attachment = record.get("attachment") or {}
            if "hook" in str(attachment.get("type", "")):
                hooks.append(json.dumps(attachment.get("content", attachment)))
    envelope_prompts = [text for text in prompts if "implement-rfc.remote-task" in text]
    return {
        "user_prompts": len(prompts),
        "prompt_tokens": [tok.count(text) for text in prompts],
        "prompt_sha256_16": [digest(text) for text in prompts],
        "prompts_with_remote_task_envelope": len(envelope_prompts),
        "hook_attachments": len(hooks),
        "hook_tokens": sum(tok.count(text) for text in hooks),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--codex-rollout", type=pathlib.Path, required=True)
    parser.add_argument("--claude-transcript", type=pathlib.Path)
    parser.add_argument("--station-file", type=pathlib.Path, required=True)
    parser.add_argument("--format", choices=("v1", "v2"), default="v1")
    parser.add_argument("--tokenizer", choices=("o200k", "chars4"), default="o200k")
    parser.add_argument("--summary", action="store_true", help="omit per-turn rows")
    parser.add_argument("--output", type=pathlib.Path, help="write LF-terminated JSON here")
    args = parser.parse_args()
    station = json.loads(args.station_file.read_text(encoding="utf-8"))
    tok = Tokenizer(args.tokenizer)
    report = {
        "schema": "remote-station.token-measurement.v1",
        "format": args.format,
        "tokenizer": {"name": tok.name, **tok.detail},
        "station": {key: station.get(key) for key in ("station_id", "station", "project", "workstream", "branch")},
        "codex": {
            "rollout_name": args.codex_rollout.name,
            "rollout_sha256_16": hashlib.sha256(args.codex_rollout.read_bytes()).hexdigest()[:16],
            **measure_codex(args.codex_rollout, station, args.format, tok),
        },
    }
    if args.claude_transcript:
        report["claude"] = {
            "transcript_name": args.claude_transcript.name,
            **measure_claude(args.claude_transcript, tok),
        }
    if args.format == "v1":
        report["admission_payload_analysis"] = payload_analysis(args.codex_rollout, station, tok)
    if args.summary:
        report["codex"].pop("turns")
    text = json.dumps(report, indent=1) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
