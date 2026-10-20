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
    samples = bytes(int(128 + 24 * math.sin(2 * math.pi * frequency * n / 8000)) for n in range(12 * 8000))
    stream = io.BytesIO()
    with wave.open(stream, "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(1)
        sound.setframerate(8000)
        sound.writeframes(samples)
    return "data:audio/wav;base64," + base64.b64encode(stream.getvalue()).decode(), waveform(samples)


def waveform(samples):
    """Preview this fixture's exact unsigned 8-bit mono PCM, without resampling it."""
    upper, lower = [], []
    for column in range(600):
        bucket = samples[column * len(samples) // 600:(column + 1) * len(samples) // 600]
        x = 50 + column
        upper.append(f"{x},{100 - (max(bucket) - 128) / 2:g}")
        lower.append(f"{x},{100 - (min(bucket) - 128) / 2:g}")
    points = " ".join(upper + lower[::-1])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 200">
<title>Full-clip waveform</title>
<desc>12 seconds of mono PCM. Each column spans 160 samples and shows their minimum and maximum. Amplitude uses the full PCM scale.</desc>
<rect width="700" height="200" fill="#fafafa"/>
<path d="M50 36V164H650M50 100H650" fill="none" stroke="#889099"/>
<polygon points="{points}" fill="#126782"/>
<g fill="#202830" font-family="sans-serif" font-size="14">
<text x="50" y="22">Waveform · full clip · min/max envelope</text>
<text x="18" y="40">+1</text><text x="26" y="104">0</text><text x="18" y="168">−1</text>
<text x="50" y="186">0 s</text><text x="620" y="186">12 s</text>
</g></svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def example():
    candidates = [{"id": "brief", "title": "Ordinary review — audition brief", "revision": "synthetic-2",
                   "criteria": ["The brief separates creative fit from rights and integration approval"],
                   "content": "These synthetic tones exercise the portable review UI. They are not game assets. Audio acceptance applies only to the stated purpose and scope."}]
    for group in ("launcher", "death"):
        for index, variant in enumerate("ABC"):
            audio_url, waveform_url = clip(220 + index * 110 + (55 if group == "death" else 0))
            candidates.append({"id": f"{group}-{variant}", "title": f"{group.title()} {variant} — synthetic tone", "revision": "synthetic-2",
                "question_type": "audio", "comparison_group": group,
                "criteria": ["Judge this clip independently for its stated purpose", "Leave any other clips unanswered if you have no verdict"],
                "content": "Several alternatives may be acceptable, or none. Use comparison buttons to switch; each answer and comment stays with its exact clip.",
                "audio": {"url": audio_url, "variant": f"{group.title()} {variant}",
                    "purpose": "Launcher activation" if group == "launcher" else "Death cue",
                    "scope": "Creative fit in isolation only; no rights or in-game approval",
                    "context": "Plays once when the named event occurs", "listen_for": "Clear onset and appropriate character",
                    "reject_if": "It suggests another event or is distracting"},
                "media": [{"kind": "image", "url": waveform_url, "label": f"{group.title()} {variant} — full-clip waveform (12 s; full-scale PCM amplitude)"}],
                "metadata": {"provenance": "Generated synthetic PCM tone and exact-sample waveform; no external source or asset admission"}})
    candidates.append({"id": "broken", "title": "Decode failure — negative control", "revision": "synthetic-2", "question_type": "audio",
        "criteria": ["The failure stays visible and supplies no implicit verdict"],
        "content": "Waveform unavailable: this intentionally invalid audio has no decodable samples. It tests the visible playback failure.",
        "audio": {"url": "data:audio/wav;base64,aW52YWxpZA==", "purpose": "Failure behavior", "scope": "UI diagnostic only"}})
    return {"schema_version": 2, "candidates": candidates}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(example(), indent=2) + "\n", encoding="utf-8")
