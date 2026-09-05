#!/usr/bin/env python3
"""Build and validate deterministic, offline art-isolation review packages."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


INPUT_SCHEMA = "sample_studio.art_review_batch_input"
OUTPUT_SCHEMA = "sample_studio.art_review_batch"
VERDICT_SCHEMA = "sample_studio.art_isolation_review_verdict"
SCHEMA_VERSION = 1
REVIEW_SCOPE = "human_visual_isolation_only"
ALLOWED_GATES = {
    "concept_source",
    "generated_model",
    "texture_repair",
    "runtime_visual",
}
IMAGE_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".webm"}
DOWNSTREAM_CLAIMS = {
    "art_bible_integrated": False,
    "source_generation_ready": False,
    "generated_asset_approved": False,
    "texture_repair_approved": False,
    "runtime_promotion_approved": False,
    "rights_clearance_approved": False,
    "in_game_approval_claimed": False,
}


class ReviewError(ValueError):
    """A user-correctable review package error."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{field} must be a non-empty string")
    return value.strip()


def optional_string(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ReviewError(f"{field} must be a string")
    return value.strip()


def string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ReviewError(f"{field} must be an array of strings")
    return [require_string(item, f"{field}[{index}]") for index, item in enumerate(value)]


def slug(value: str, fallback: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (result or fallback)[:64]


def resolve_source(base: Path, value: Any, field: str) -> Path:
    source_text = require_string(value, field)
    source = Path(source_text).expanduser()
    if not source.is_absolute():
        source = base / source
    source = source.resolve()
    if not source.is_file():
        raise ReviewError(f"{field} does not name a file: {source_text}")
    return source


def prepare_files(
    items: Any,
    *,
    field: str,
    source_base: Path,
    destination_root: Path,
    relative_root: Path,
    previewable: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(items, list):
        raise ReviewError(f"{field} must be an array")
    output: list[dict[str, Any]] = []
    identity: list[dict[str, Any]] = []
    for index, raw in enumerate(items):
        item_field = f"{field}[{index}]"
        if not isinstance(raw, dict):
            raise ReviewError(f"{item_field} must be an object")
        label = require_string(raw.get("label"), f"{item_field}.label")
        source = resolve_source(source_base, raw.get("path"), f"{item_field}.path")
        extension = source.suffix.lower()
        if previewable and extension not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            allowed = ", ".join(sorted(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS))
            raise ReviewError(f"{item_field}.path must use a previewable extension: {allowed}")
        media_kind = "image" if extension in IMAGE_EXTENSIONS else "video" if extension in VIDEO_EXTENSIONS else "file"
        filename = f"{index + 1:02d}-{slug(label, 'item')}{extension}"
        destination = destination_root / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        digest = sha256_file(destination)
        relative_path = (relative_root / filename).as_posix()
        record = {
            "label": label,
            "media_kind": media_kind,
            "path": relative_path,
            "sha256": digest,
        }
        output.append(record)
        identity.append(
            {
                "label": label,
                "media_kind": media_kind,
                "sha256": digest,
            }
        )
    return output, identity


def prepare_candidate(
    raw: Any,
    *,
    index: int,
    source_base: Path,
    output_root: Path,
) -> dict[str, Any]:
    field = f"candidates[{index}]"
    if not isinstance(raw, dict):
        raise ReviewError(f"{field} must be an object")

    candidate_id = require_string(raw.get("candidate_id"), f"{field}.candidate_id")
    asset_key = require_string(raw.get("asset_key"), f"{field}.asset_key")
    display_name = require_string(raw.get("display_name"), f"{field}.display_name")
    description = optional_string(raw.get("description"), f"{field}.description")
    scene_role = optional_string(raw.get("scene_role"), f"{field}.scene_role")
    acceptance_criteria = string_list(raw.get("acceptance_criteria"), f"{field}.acceptance_criteria")
    known_concerns = string_list(raw.get("known_concerns"), f"{field}.known_concerns")

    candidate_dir_name = f"{index + 1:03d}-{slug(asset_key, 'candidate')}"
    candidate_root = output_root / "candidates" / candidate_dir_name
    relative_candidate_root = Path("candidates") / candidate_dir_name
    isolation, isolation_identity = prepare_files(
        raw.get("isolation_media"),
        field=f"{field}.isolation_media",
        source_base=source_base,
        destination_root=candidate_root / "isolation",
        relative_root=relative_candidate_root / "isolation",
        previewable=True,
    )
    context, context_identity = prepare_files(
        raw.get("context_media"),
        field=f"{field}.context_media",
        source_base=source_base,
        destination_root=candidate_root / "context",
        relative_root=relative_candidate_root / "context",
        previewable=True,
    )
    if not isolation:
        raise ReviewError(f"{field}.isolation_media must contain at least one item")
    if not context:
        raise ReviewError(f"{field}.context_media must contain at least one item")

    identity_files_raw = raw.get("identity_files", [])
    identity_files, file_identity = prepare_files(
        identity_files_raw,
        field=f"{field}.identity_files",
        source_base=source_base,
        destination_root=candidate_root / "identity",
        relative_root=relative_candidate_root / "identity",
        previewable=False,
    )

    digest_input = {
        "candidate_id": candidate_id,
        "asset_key": asset_key,
        "display_name": display_name,
        "description": description,
        "scene_role": scene_role,
        "acceptance_criteria": acceptance_criteria,
        "known_concerns": known_concerns,
        "isolation_media": isolation_identity,
        "context_media": context_identity,
        "identity_files": file_identity,
    }
    return {
        "candidate_id": candidate_id,
        "candidate_digest": sha256_bytes(canonical_bytes(digest_input)),
        "asset_key": asset_key,
        "display_name": display_name,
        "description": description,
        "scene_role": scene_role,
        "acceptance_criteria": acceptance_criteria,
        "known_concerns": known_concerns,
        "isolation_media": isolation,
        "context_media": context,
        "identity_files": identity_files,
    }


def build_manifest(source: dict[str, Any], input_path: Path, output_root: Path) -> dict[str, Any]:
    if source.get("schema_name") != INPUT_SCHEMA:
        raise ReviewError(f"schema_name must be {INPUT_SCHEMA!r}")
    if source.get("schema_version") != SCHEMA_VERSION:
        raise ReviewError(f"schema_version must be {SCHEMA_VERSION}")
    project_id = require_string(source.get("project_id"), "project_id")
    title = require_string(source.get("title"), "title")
    review_gate = require_string(source.get("review_gate"), "review_gate")
    if review_gate not in ALLOWED_GATES:
        raise ReviewError(f"review_gate must be one of: {', '.join(sorted(ALLOWED_GATES))}")
    raw_candidates = source.get("candidates")
    if not isinstance(raw_candidates, list) or not raw_candidates:
        raise ReviewError("candidates must be a non-empty array")

    candidates = [
        prepare_candidate(
            raw,
            index=index,
            source_base=input_path.parent,
            output_root=output_root,
        )
        for index, raw in enumerate(raw_candidates)
    ]
    candidate_ids = [candidate["candidate_id"] for candidate in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ReviewError("candidate_id values must be unique within a batch")

    batch_identity = {
        "project_id": project_id,
        "title": title,
        "review_gate": review_gate,
        "candidates": [
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_digest": candidate["candidate_digest"],
            }
            for candidate in candidates
        ],
    }
    batch_hash = hashlib.sha256(canonical_bytes(batch_identity)).hexdigest()[:24]
    batch_id = f"sample_studio:/art-review/{slug(project_id, 'project')}/{batch_hash}"
    return {
        "schema_name": OUTPUT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "batch_id": batch_id,
        "project_id": project_id,
        "title": title,
        "review_gate": review_gate,
        "review_scope": REVIEW_SCOPE,
        "candidates": candidates,
        "downstream_claims": DOWNSTREAM_CLAIMS,
    }


def media_html(items: list[dict[str, Any]]) -> str:
    figures: list[str] = []
    for item in items:
        source = html.escape(item["path"], quote=True)
        label = html.escape(item["label"])
        if item["media_kind"] == "video":
            media = f'<video controls preload="metadata" src="{source}"></video>'
        else:
            media = f'<img loading="lazy" src="{source}" alt="{label}">'
        figures.append(f"<figure>{media}<figcaption>{label}</figcaption></figure>")
    return "\n".join(figures)


def list_html(items: list[str], empty: str) -> str:
    if not items:
        return f'<p class="muted">{html.escape(empty)}</p>'
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def candidate_html(candidate: dict[str, Any]) -> str:
    candidate_id = html.escape(candidate["candidate_id"], quote=True)
    digest = html.escape(candidate["candidate_digest"], quote=True)
    identity_files = candidate["identity_files"]
    if identity_files:
        links = "<ul>" + "".join(
            f'<li><a href="{html.escape(item["path"], quote=True)}">{html.escape(item["label"])}</a> '
            f'<span class="identity">{html.escape(item["sha256"])}</span></li>'
            for item in identity_files
        ) + "</ul>"
    else:
        links = '<p class="muted">No additional identity files.</p>'
    description = html.escape(candidate["description"]) or "No description supplied."
    scene_role = html.escape(candidate["scene_role"]) or "No scene role supplied."
    return f"""<article class="candidate" data-candidate-id="{candidate_id}" data-candidate-digest="{digest}" data-review-state="pending">
  <div class="candidate-head">
    <div>
      <h2>{html.escape(candidate["display_name"])}</h2>
      <p>{description}</p>
      <p><strong>Scene role:</strong> {scene_role}</p>
    </div>
    <div class="identity">{candidate_id}<br>{digest}</div>
  </div>
  <div class="media-groups">
    <section><h3>Isolation</h3><div class="media-grid">{media_html(candidate["isolation_media"])}</div></section>
    <section><h3>Context</h3><div class="media-grid">{media_html(candidate["context_media"])}</div></section>
  </div>
  <div class="criteria">
    <section><h3>Acceptance criteria</h3>{list_html(candidate["acceptance_criteria"], "No additional criteria supplied.")}</section>
    <section><h3>Known concerns</h3>{list_html(candidate["known_concerns"], "No known concerns recorded.")}</section>
  </div>
  <section class="identity-files"><h3>Identity-bound files</h3>{links}</section>
  <div class="decision-row" role="group" aria-label="Decision for {html.escape(candidate["display_name"], quote=True)}">
    <button type="button" data-decision="accept" aria-pressed="false">Accept exact candidate</button>
    <button type="button" data-decision="reject" aria-pressed="false">Reject exact candidate</button>
    <button type="button" data-decision="clear" aria-pressed="false">Clear decision</button>
  </div>
  <label class="notes">Review notes<textarea data-review-notes placeholder="Optional candidate-specific notes"></textarea></label>
</article>"""


def render_html(manifest: dict[str, Any], css: str, runtime: str) -> str:
    config_json = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    config_json = config_json.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    cards = "\n".join(candidate_html(candidate) for candidate in manifest["candidates"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(manifest["title"])}</title>
  <style>\n{css}\n</style>
</head>
<body>
  <header>
    <h1>{html.escape(manifest["title"])}</h1>
    <p class="lede">Project: {html.escape(manifest["project_id"])} · Gate: {html.escape(manifest["review_gate"])} · Batch: {html.escape(manifest["batch_id"])}</p>
    <p class="scope-warning"><strong>Scope:</strong> This page records human visual-isolation decisions for this exact batch and gate only. It stores choices in this browser and cannot write repository evidence. Acceptance does not approve art-bible integration, generation, texture repair, runtime promotion, rights, or in-game use. Export the complete verdict and return it to Codex for validation.</p>
  </header>
  <main>
    <section class="review-controls" aria-label="Review progress and export">
      <div class="review-controls-row">
        <div class="review-summary">
          <span id="review-progress">0/{len(manifest["candidates"])} reviewed</span>
          <span id="review-totals">0 accepted · 0 rejected · {len(manifest["candidates"])} pending</span>
        </div>
        <div class="review-actions">
          <label><input id="pending-only" type="checkbox"> Show pending only</label>
          <button id="export-verdict" type="button" disabled>Copy verdict for Codex</button>
        </div>
      </div>
      <p id="review-status" role="status" aria-live="polite" aria-atomic="true">Resolve every exact candidate to unlock the final verdict.</p>
    </section>
    {cards}
    <section class="export-panel">
      <h2>Final result</h2>
      <p>The pinned copy button unlocks after every exact candidate has Accept or Reject selected. Its result stays visible in the top review bar, and the complete JSON remains below as a manual-copy fallback.</p>
      <textarea id="verdict-output" readonly aria-label="Exported verdict JSON"></textarea>
    </section>
  </main>
  <script id="art-review-config" type="application/json">{config_json}</script>
  <script>\n{runtime}\n</script>
</body>
</html>
"""


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ReviewError(f"cannot read {label}: {error}") from error
    except json.JSONDecodeError as error:
        raise ReviewError(f"{label} is not valid JSON: {error}") from error


def build(input_path: Path, output_root: Path) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_root = output_root.resolve()
    if output_root.exists():
        if not output_root.is_dir():
            raise ReviewError(f"output path is not a directory: {output_root}")
        if any(output_root.iterdir()):
            raise ReviewError(f"output directory must be empty: {output_root}")
    else:
        output_root.mkdir(parents=True)
    source = load_json(input_path, "input manifest")
    if not isinstance(source, dict):
        raise ReviewError("input manifest must contain a JSON object")
    manifest = build_manifest(source, input_path, output_root)
    skill_root = Path(__file__).resolve().parent.parent
    css = (skill_root / "assets" / "art_review.css").read_text(encoding="utf-8")
    runtime = (skill_root / "assets" / "art_review_runtime.js").read_text(encoding="utf-8")
    (output_root / "art-review-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "index.html").write_text(
        render_html(manifest, css, runtime), encoding="utf-8"
    )
    return manifest


def identity_tuple(value: Any, field: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise ReviewError(f"{field} must be an object")
    candidate_id = require_string(value.get("candidate_id"), f"{field}.candidate_id")
    candidate_digest = require_string(value.get("candidate_digest"), f"{field}.candidate_digest")
    if set(value) != {"candidate_id", "candidate_digest"}:
        raise ReviewError(f"{field} may contain only candidate_id and candidate_digest")
    return candidate_id, candidate_digest


def validate_verdict(manifest: dict[str, Any], verdict: dict[str, Any]) -> None:
    if manifest.get("schema_name") != OUTPUT_SCHEMA or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ReviewError("review manifest has an unsupported schema")
    expected_scalars = {
        "schema_name": VERDICT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "batch_id": manifest.get("batch_id"),
        "review_gate": manifest.get("review_gate"),
        "review_scope": REVIEW_SCOPE,
    }
    for field, expected in expected_scalars.items():
        if verdict.get(field) != expected:
            raise ReviewError(f"verdict {field} must equal {expected!r}")

    expected = {
        (candidate["candidate_id"], candidate["candidate_digest"])
        for candidate in manifest.get("candidates", [])
    }
    decided: list[tuple[str, str]] = []
    for collection in ("accepted_candidates", "rejected_candidates"):
        values = verdict.get(collection)
        if not isinstance(values, list):
            raise ReviewError(f"verdict {collection} must be an array")
        decided.extend(
            identity_tuple(value, f"{collection}[{index}]")
            for index, value in enumerate(values)
        )
    if len(decided) != len(set(decided)):
        raise ReviewError("verdict contains a duplicate candidate identity")
    if set(decided) != expected:
        missing = expected - set(decided)
        extra = set(decided) - expected
        raise ReviewError(f"verdict candidate partition is not exact; missing={sorted(missing)!r}, extra={sorted(extra)!r}")

    notes = verdict.get("notes_by_candidate_identity")
    if not isinstance(notes, dict):
        raise ReviewError("verdict notes_by_candidate_identity must be an object")
    valid_note_keys = {f"{candidate_id}@{digest}" for candidate_id, digest in expected}
    for key, value in notes.items():
        if key not in valid_note_keys or not isinstance(value, str):
            raise ReviewError(f"invalid candidate note entry: {key!r}")
    if verdict.get("downstream_claims") != DOWNSTREAM_CLAIMS:
        raise ReviewError("verdict downstream_claims must contain the complete false-only claim set")

    expected_fields = set(expected_scalars) | {
        "accepted_candidates",
        "rejected_candidates",
        "notes_by_candidate_identity",
        "downstream_claims",
    }
    if set(verdict) != expected_fields:
        raise ReviewError("verdict contains missing or unsupported top-level fields")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build", help="build an offline review package")
    build_parser.add_argument("--input", required=True, type=Path)
    build_parser.add_argument("--out", required=True, type=Path)
    validate_parser = subparsers.add_parser("validate-verdict", help="validate a complete exported verdict")
    validate_parser.add_argument("--manifest", required=True, type=Path)
    validate_parser.add_argument("--verdict", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "build":
            manifest = build(args.input, args.out)
            print(f"built {manifest['batch_id']} at {args.out.resolve() / 'index.html'}")
        else:
            manifest = load_json(args.manifest.resolve(), "review manifest")
            verdict = load_json(args.verdict.resolve(), "verdict")
            if not isinstance(manifest, dict) or not isinstance(verdict, dict):
                raise ReviewError("manifest and verdict must contain JSON objects")
            validate_verdict(manifest, verdict)
            print(f"valid complete verdict for {manifest['batch_id']}")
        return 0
    except ReviewError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
