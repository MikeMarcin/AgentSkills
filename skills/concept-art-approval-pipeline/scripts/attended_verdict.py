#!/usr/bin/env python3
"""Validate a handed-back attended-review session against an exact art batch."""

from __future__ import annotations

import argparse
import base64
import binascii
from collections import Counter
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


def check_media(folder, candidate, card):
    # Design questions carry stills under Now and Reference. Video uses the
    # attended media player. Extra stills can illustrate a video-only question.
    videos = displayed_digests([m for m in card.get("media", []) if m["kind"] == "video"])
    for group, column in (("isolation_media", "now"), ("context_media", "reference"), ("identity_files", None)):
        images = displayed_digests(card.get(column, [])) if column else Counter()
        for item in candidate[group]:
            path = (folder / item["path"]).resolve()
            digest = item["sha256"]
            if not path.is_relative_to(folder) or sha256_file(path) != digest:
                raise ReviewError(f"changed art package file: {item['path']}")
            if column:
                shown = videos if item["media_kind"] == "video" else images
                if not shown[digest]:
                    raise ReviewError(f"submitted {group} file was not shown on {card['id']}")
                shown[digest] -= 1


def collect(manifest_path, prepared, returned):
    manifest = load_json(manifest_path, "art batch")
    if manifest.get("schema_name") != OUTPUT_SCHEMA or manifest.get("review_scope") != REVIEW_SCOPE:
        raise ReviewError("expected a visual isolation review batch")
    if not prepared.get("session") or returned.get("session") != prepared["session"]:
        raise ReviewError("handback belongs to a different attended session")
    handed = [e["sequence"] for e in returned.get("events", [])
              if e["kind"] == "handed-back" and e["sequence"] > prepared["sequence"]]
    if not returned.get("handed_back") or not handed:
        raise ReviewError("no new saved handback for this preparation")
    started = {c["id"]: c for c in prepared["candidates"]}
    art = {c["candidate_id"]: c for c in manifest["candidates"]}
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
        if any(e.get("candidate") == card["id"] and e["sequence"] > max(handed)
               for e in returned["events"]):
            raise ReviewError(f"question changed after handback: {cid}")
        check_media(manifest_path.resolve().parent, candidate, card)
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
    args = parser.parse_args()
    try:
        verdict = collect(args.manifest, load_json(args.prepared, "prepared status"),
                          load_json(args.handback, "attended status"))
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
