#!/usr/bin/env python3
"""Write version-3 example manifests: one passing question of each kind and one
manifest that fails the question checks. Standard library only; the images are
synthetic placeholders, not captures of a real build."""
import argparse
import base64
import json
from pathlib import Path
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mixed_audio import clip  # noqa: E402  Synthetic tone and its exact waveform.


def png(rgb, width=160, height=90):
    """A flat placeholder image as an inline data URL."""
    row = b"\x00" + bytes(rgb) * width
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * height)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(data).decode()


# The guide's before-and-after example (references/question-authoring.md): the
# latest reviewed BetterPullReview question, rewritten. Paths are representative.
IMPORT_PREVIEW = {
    "id": "import-preview-b",
    "kind": "build",
    "title": "Is the import preview option B as approved?",
    "revision": "workflow-import-v002",
    "why": "You chose B; this is it built with the app's widgets.",
    "criteria": [
        "Opens with everything chosen and Import enabled.",
        "Updates show yours beside the file's, changes marked.",
        "The unknown action is named and refused.",
    ],
    "reference": [{"url": png((214, 222, 230)), "label": "Option B as approved"}],
    "now": [{"url": png((196, 210, 222)), "label": "Built preview with the sample file"}],
    "launch": {"command": "python3 /Users/reviewer/workflow-import-v002/launch.py"},
    "steps": [
        {"text": "In Settings, Agents, choose Import configuration… and paste this file.",
         "value": "/Users/reviewer/workflow-import-v002/look/synthetic-org.bpr-config.json"},
        {"text": "Try one choice per item, then Cancel."},
    ],
    "not_in_round": ["The Profiles page and the settings move."],
    "metadata": {"rfc": "RFC-BPR-0112", "card": "BPR-2032", "frozen": "18a70bb96087", "built": "8af4a4501"},
}


def passing():
    tone, waveform = clip(330)
    shared = {k: v for k, v in IMPORT_PREVIEW.items() if k != "launch"}
    return {"schema_version": 3,
            "setups": {"frozen-build": {
                "launch": {"label": "Open the frozen build", "command": "python3 /Users/reviewer/workflow-import-v002/launch.py"},
                "note": "Both build questions use one frozen build with a sample workflow imported. Nothing reaches GitHub."}},
            "candidates": [
                {**shared, "setup": "frozen-build"},
                {"id": "import-shortcut", "kind": "build", "setup": "frozen-build", "revision": "workflow-import-v002",
                 "title": "Does Ctrl+I open Import configuration from anywhere?",
                 "criteria": ["Ctrl+I opens the import dialog from the main window and from Settings."],
                 "reference": "none",
                 "steps": [{"text": "Press Ctrl+I in the main window, then again in Settings."}],
                 "waivers": {"build-now-image": "No screenshot: the change is a keyboard shortcut."}},
                {"id": "toolbar-icons", "kind": "design", "revision": "icons-3",
                 "title": "Which toolbar icon style should ship?",
                 "why": "Both styles follow the approved grid; pick one or both to continue.",
                 "criteria": ["Icons read clearly at the default size in light and dark themes."],
                 "options": ["A: outlined", "B: filled"],
                 "now": [{"url": png((235, 235, 235)), "label": "Outlined set, light and dark", "option": "A: outlined"},
                         {"url": png((60, 70, 80)), "label": "Filled set, light and dark", "option": "B: filled"}]},
                {"id": "release-notes", "kind": "decision", "revision": "notes-2",
                 "title": "Do these release notes say what changed?",
                 "criteria": ["A user can tell what changed and whether to act."],
                 "document": "Import configuration now shows a preview.\n\nEach item says whether it is new, updated or unchanged. You choose what to import; nothing changes until you press Import."},
                {"id": "launcher-A", "kind": "audio", "revision": "synthetic-3",
                 "title": "Launcher A: does it fit activation?",
                 "criteria": ["Judge this clip on its own for its stated purpose."],
                 "audio": {"url": tone, "variant": "Launcher A", "purpose": "Launcher activation",
                           "scope": "Creative fit in isolation only"},
                 "media": [{"kind": "image", "url": waveform, "label": "Launcher A full-clip waveform"}]},
            ]}


def failing():
    """One question breaking several rules at once; init refuses it and saves nothing."""
    return {"schema_version": 3, "candidates": [{
        "id": "BPR-2032-import-preview-b", "kind": "build", "revision": "workflow-import-v002-18a70bb96087",
        "title": "The import preview, option B as built and frozen from 18a70bb96087 for BPR-2032 review",
        "criteria": ["Settings' Import configuration preview is option B as drawn (RFC-BPR-0112 AC02)."],
        "note": "Launch the build, then open /Users/reviewer/workflow-import-v002/look/synthetic-org.bpr-config.json. Accept keeps the preview.",
        "launch": {"command": "python3 /Users/reviewer/workflow-import-v002/launch.py"}}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Directory for passing.json and failing.json")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in (("passing", passing()), ("failing", failing())):
        (args.output / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
