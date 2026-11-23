#!/usr/bin/env python3
"""Validate a handed-back attended-review session against an exact art batch."""

from __future__ import annotations

import argparse
import base64
import binascii
from collections import Counter, defaultdict
import json
from pathlib import Path

from build_art_review import (
    DOWNSTREAM_CLAIMS, OUTPUT_SCHEMA, REVIEW_SCOPE, VERDICT_SCHEMA, ReviewError,
    load_json, sha256_bytes, sha256_file, validate_verdict,
)


def displayed_digests(items):
    digests = Counter()
    for item in items:
        prefix, comma, encoded = item["url"].partition(",")
        if not (comma and prefix.startswith("data:") and prefix.endswith(";base64")):
            raise ReviewError("art review media must contain the submitted file bytes")
        digests[sha256_bytes(base64.b64decode(encoded, validate=True))] += 1
    return digests


def check_media(folder, candidate, card, context_in_now):
    # Design questions carry stills under Now and Reference. Video uses the
    # attended media player. Extra stills can illustrate a video-only question.
    videos = displayed_digests([m for m in card.get("media", []) if m["kind"] == "video"])
    stills = {column: displayed_digests(card.get(column, [])) for column in ("now", "reference")}
    if context_in_now:
        isolation = {i["sha256"] for i in candidate["isolation_media"] if i["media_kind"] == "image"}
        context = {i["sha256"] for i in candidate["context_media"] if i["media_kind"] == "image"}
        if not context_in_now <= context or context_in_now & isolation:
            raise ReviewError("context-in-now requires a distinct submitted context still")
        if not isolation or not (context - context_in_now - isolation):
            raise ReviewError("context-in-now requires a separate isolation still and reference still")
    for group, column in (("isolation_media", "now"), ("context_media", "reference"), ("identity_files", None)):
        for item in candidate[group]:
            path = (folder / item["path"]).resolve()
            digest = item["sha256"]
            if not path.is_relative_to(folder) or sha256_file(path) != digest:
                raise ReviewError(f"changed art package file: {item['path']}")
            if column:
                placement = "now" if group == "context_media" and digest in context_in_now else column
                shown = videos if item["media_kind"] == "video" else stills[placement]
                if not shown[digest]:
                    raise ReviewError(f"submitted {group} file was not shown on {card['id']}")
                shown[digest] -= 1


def check_saved_answers(card, initial, events, prepared_sequence, handback):
    if card["id"] not in handback.get("decided", []):
        raise ReviewError("handback does not record this decision")
    for kind in ("decision", "feedback"):
        matching = [e for e in events if e["kind"] == kind and e.get("candidate") == card["id"]
                    and prepared_sequence < e["sequence"] <= handback["sequence"]]
        latest = max(matching, key=lambda e: e["sequence"], default=initial)
        saved = latest.get(kind)
        if card.get(kind) != saved or (saved and (
            saved.get("candidate") != card["id"] or saved.get("fingerprint") != card["fingerprint"]
            or saved.get("actor") != "human"
        )):
            raise ReviewError(f"{kind} or saved note differs from the attended record")


def collect(manifest_path, prepared, returned, context_in_now=()):
    manifest = load_json(manifest_path, "art batch")
    if manifest.get("schema_name") != OUTPUT_SCHEMA or manifest.get("review_scope") != REVIEW_SCOPE:
        raise ReviewError("expected a visual isolation review batch")
    if not prepared.get("session") or returned.get("session") != prepared["session"]:
        raise ReviewError("handback belongs to a different attended session")
    handed = [e for e in returned.get("events", [])
              if e["kind"] == "handed-back" and e["sequence"] > prepared["sequence"]]
    if not returned.get("handed_back") or not handed:
        raise ReviewError("no new saved handback for this preparation")
    started = {c["id"]: c for c in prepared["candidates"]}
    art = {c["candidate_id"]: c for c in manifest["candidates"]}
    placements = defaultdict(set)
    digests = {c["candidate_digest"] for c in art.values()}
    for candidate_sha, image_sha in context_in_now:
        if candidate_sha not in digests or image_sha in placements[candidate_sha]:
            raise ReviewError("unknown candidate or duplicate context-in-now binding")
        placements[candidate_sha].add(image_sha)
    handback = max(handed, key=lambda event: event["sequence"])
    tracked = set()
    verdict = dict(schema_name=VERDICT_SCHEMA, schema_version=1, batch_id=manifest["batch_id"],
                   review_gate=manifest["review_gate"], review_scope=REVIEW_SCOPE,
                   accepted_candidates=[], rejected_candidates=[], notes_by_candidate_identity={},
                   downstream_claims=DOWNSTREAM_CLAIMS.copy())
    for card in returned["candidates"]:
        meta = card.get("metadata", {})
        if meta.get("batch_id") != manifest["batch_id"]:
            continue
        cid = meta["candidate_id"]
        candidate = art.get(cid)
        if candidate is None or cid in tracked:
            raise ReviewError("unexpected or duplicate art candidate in handback")
        tracked.add(cid)
        digest = candidate["candidate_digest"]
        initial = started.get(card["id"], {})
        if (meta.get("candidate_digest") != digest or meta.get("gate") != manifest["review_gate"]
                or card["revision"] != f"{manifest['batch_id']}@{digest}"
                or initial.get("revision") != card["revision"]
                or initial.get("fingerprint") != card["fingerprint"]):
            raise ReviewError(f"art identity or prepared question changed: {cid}")
        if any(e.get("candidate") == card["id"] and e["sequence"] > handback["sequence"]
               for e in returned["events"]):
            raise ReviewError(f"question changed after handback: {cid}")
        binding = placements.get(digest, set())
        check_media(manifest_path.resolve().parent, candidate, card, binding)
        if binding:
            check_saved_answers(card, initial, returned["events"], prepared["sequence"], handback)
        decision = card.get("decision")
        if not decision:
            raise ReviewError(f"decision pending: {cid}")
        if (decision.get("actor") != "human" or decision.get("candidate") != card["id"]
                or decision.get("fingerprint") != card["fingerprint"]
                or decision.get("outcome") not in ("accept", "reject")):
            raise ReviewError(f"unbound visual decision: {cid}")
        collection = "accepted_candidates" if decision["outcome"] == "accept" else "rejected_candidates"
        verdict[collection].append({"candidate_id": cid, "candidate_digest": digest})
        feedback = card.get("feedback") or {}
        note = feedback.get("note", decision.get("note", ""))
        if note:
            verdict["notes_by_candidate_identity"][f"{cid}@{digest}"] = note
    validate_verdict(manifest, verdict)
    return verdict


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("manifest", "prepared", "handback", "out"):
        parser.add_argument("--" + arg, type=Path, required=True)
    parser.add_argument("--context-in-now", action="append", nargs=2, default=[],
                        metavar=("CANDIDATE_SHA256", "IMAGE_SHA256"),
                        help="Verify this submitted context still in the original card's Now column")
    args = parser.parse_args()
    try:
        verdict = collect(args.manifest, load_json(args.prepared, "prepared status"),
                          load_json(args.handback, "attended status"), args.context_in_now)
        if args.out.exists():
            if load_json(args.out, "existing verdict") != verdict:
                raise ReviewError("destination already contains a different verdict")
        else:
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(verdict, indent=2, ensure_ascii=False) + "\n")
        print(f"Validated {len(verdict['accepted_candidates'])} accepted and "
              f"{len(verdict['rejected_candidates'])} rejected for {verdict['review_gate']}")
    except (ValueError, KeyError, TypeError, OSError, binascii.Error) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
