#!/usr/bin/env python3
"""AC07 differential: version-1 and version-2 manifests that break the new rules
run through the RFC_BASE_SHA helper and the candidate helper in disposable
checkouts. Session state and command output must match after normalizing
random and time fields; only init's added legacy report may differ.

Usage: ac07_differential.py --repo-root AGENTSKILLS [--base SHA] [--output FILE]
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

NOISE = re.compile(r'"(id|session|time|saved_at|checkout|preparation_id|handed_back)": "[^"]*"')


def normalize(value):
    text = json.dumps(value, sort_keys=True)
    text = NOISE.sub(lambda m: f'"{m.group(1)}": "*"', text)
    return json.loads(re.sub(r"prepare-[0-9a-f]+\.log|/[^\"]*?/checkout", "*", text))


def flow(helper, base, manifest_version):
    root, registry = base / "checkout", base / "registry"
    root.mkdir(parents=True)
    run = lambda *args, stdin=None: subprocess.run([sys.executable, "-B", str(helper), "--repo-root", str(root), "--registry", str(registry), *args],
                                                  capture_output=True, text=True, input=stdin, timeout=30)
    candidates = [
        {"id": "APP-0042-layout", "title": "Review the revised layout for BPR-2032 at build 18a70bb96087 before the release goes out",
         "revision": "prepared-build-2", "criteria": ["Labels are readable", "Open /Users/reviewer/app and look"],
         "content": "Open the prepared build at /Users/reviewer/app. Accept keeps it.",
         "launch": {"label": "Open", "command": "open /Applications/Thing.app"},
         "copy": [{"label": "PR", "value": "https://example.test/pull/7"}]},
        {"id": "pick", "title": "Pick", "revision": "r1", "criteria": ["One"], "options": ["A", "B", "C", "D", "E", "F", "G"]},
    ]
    if manifest_version == 2:
        candidates.append({"id": "death-C", "title": "Death C", "revision": "synthetic-2", "criteria": ["Judge"],
                           "question_type": "audio", "comparison_group": "death",
                           "audio": {"url": "data:audio/wav;base64,UklGRg==", "purpose": "Death cue", "scope": "Creative fit only"}})
    path = base / "manifest.json"
    path.write_text(json.dumps({"schema_version": manifest_version, "candidates": candidates}))
    outputs = {}
    outputs["init"] = json.loads(run("init", "--manifest", str(path)).stdout)
    outputs["prepare"] = json.loads(run("prepare").stdout)
    fp = {c["id"]: c["fingerprint"] for c in outputs["prepare"]["candidates"]}
    session = outputs["prepare"]["session"]
    packet = {"schema_version": manifest_version, "session": session, "decisions": [
        {"candidate": "APP-0042-layout", "fingerprint": fp["APP-0042-layout"], "decision_id": "d1", "outcome": "accept", "note": "ok"},
        {"candidate": "pick", "fingerprint": fp["pick"], "decision_id": "d2", "outcome": "select", "selected": ["B"]}]}
    if manifest_version == 2:
        packet["feedback"] = [{"candidate": "death-C", "fingerprint": fp["death-C"], "feedback_id": "f1", "note": "consider for pain"}]
    outputs["import"] = json.loads(run("import", "--file", "-", stdin=json.dumps(packet)).stdout)
    outputs["reimport"] = json.loads(run("import", "--file", "-", stdin=json.dumps(packet)).stdout)
    outputs["hand-back"] = json.loads(run("hand-back").stdout)
    outputs["status"] = json.loads(run("status", "--after", "0", "--full").stdout)
    state = json.loads((root / ".mask/attended-review/session.json").read_text())
    return outputs, state, fp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--base", default="5fd9ad3951934469593be781e6078927c9e20c23")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"base": args.base, "cases": []}
    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        baseline = temporary / "base" / "scripts" / "attended_review.py"
        baseline.parent.mkdir(parents=True)
        (temporary / "base" / "assets").mkdir()
        for relative, target in (("scripts/attended_review.py", baseline), ("assets/review.html", temporary / "base/assets/review.html")):
            target.write_bytes(subprocess.run(["git", "-C", str(args.repo_root), "show", f"{args.base}:skills/attended-review/{relative}"],
                                              capture_output=True, check=True).stdout)
        candidate = args.repo_root / "skills/attended-review/scripts/attended_review.py"
        for version in (1, 2):
            old_out, old_state, old_fp = flow(baseline, temporary / f"old-{version}", version)
            new_out, new_state, new_fp = flow(candidate, temporary / f"new-{version}", version)
            report = new_out["init"].pop("checks")
            same_output = normalize(old_out) == normalize(new_out)
            same_state = normalize(old_state) == normalize(new_state)
            result["cases"].append({"manifest_version": version, "fingerprints_equal": old_fp == new_fp, "fingerprints": new_fp,
                                    "outputs_equal_except_legacy_report": same_output, "session_state_equal": same_state,
                                    "state_schema_version": new_state["schema_version"],
                                    "legacy_report": {"format": report["format"], "refused": report["refused"],
                                                      "rules": sorted({v["rule"] for v in report["violations"]})}})
    result["pass"] = all(c["fingerprints_equal"] and c["outputs_equal_except_legacy_report"] and c["session_state_equal"]
                         and c["legacy_report"]["format"] == "unchecked legacy format" and not c["legacy_report"]["refused"]
                         and c["legacy_report"]["rules"] for c in result["cases"])
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
