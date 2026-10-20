#!/usr/bin/env python3
"""Write a self-contained synthetic mixed-question manifest. Standard library only."""
import argparse
import base64
import io
import json
import math
from pathlib import Path
import wave


def clip(frequency):
    stream = io.BytesIO()
    with wave.open(stream, "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(1)
        sound.setframerate(8000)
        sound.writeframes(bytes(int(128 + 24 * math.sin(2 * math.pi * frequency * n / 8000)) for n in range(12 * 8000)))
    return "data:audio/wav;base64," + base64.b64encode(stream.getvalue()).decode()


def example():
    candidates = [{"id": "brief", "title": "Ordinary review — audition brief", "revision": "synthetic-1",
                   "criteria": ["The brief separates creative fit from rights and integration approval"],
                   "content": "These synthetic tones exercise the portable review UI. They are not game assets. Audio acceptance applies only to the stated purpose and scope."}]
    for group in ("launcher", "death"):
        for index, variant in enumerate("ABC"):
            candidates.append({"id": f"{group}-{variant}", "title": f"{group.title()} {variant} — synthetic tone", "revision": "synthetic-1",
                "question_type": "audio", "comparison_group": group,
                "criteria": ["Judge this clip independently for its stated purpose", "Leave any other clips unanswered if you have no verdict"],
                "content": "Several alternatives may be acceptable, or none. Use comparison buttons to switch; each answer and comment stays with its exact clip.",
                "audio": {"url": clip(220 + index * 110 + (55 if group == "death" else 0)), "variant": f"{group.title()} {variant}",
                    "purpose": "Launcher activation" if group == "launcher" else "Death cue",
                    "scope": "Creative fit in isolation only; no rights or in-game approval",
                    "context": "Plays once when the named event occurs", "listen_for": "Clear onset and appropriate character",
                    "reject_if": "It suggests another event or is distracting"},
                "metadata": {"provenance": "Generated synthetic PCM tone; no external source or asset admission"}})
    candidates.append({"id": "broken", "title": "Decode failure — negative control", "revision": "synthetic-1", "question_type": "audio",
        "criteria": ["The failure stays visible and supplies no implicit verdict"],
        "audio": {"url": "data:audio/wav;base64,aW52YWxpZA==", "purpose": "Failure behavior", "scope": "UI diagnostic only"}})
    return {"schema_version": 2, "candidates": candidates}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(example(), indent=2) + "\n", encoding="utf-8")
