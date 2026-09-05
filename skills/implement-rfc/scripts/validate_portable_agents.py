#!/usr/bin/env python3
"""Observational validation of shared portable source or selected role adapters."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_runtime_adapters as renderer


def load_manifest(skill_dir: Path) -> dict[str, str]:
    data = json.loads((skill_dir / 'generated/portable-manifest.json').read_text(encoding='utf-8'))
    return {entry['path']: entry['sha256'] for entry in data['files']}


def actual_manifest(skill_dir: Path) -> dict[str, str]:
    return {entry['path']: entry['sha256'] for entry in renderer.portable_manifest(skill_dir)['files']}


def compare_manifests(ours: dict[str, str], theirs: dict[str, str]) -> list[str]:
    findings = []
    for path in sorted(set(ours) | set(theirs)):
        if path not in theirs:
            findings.append(f'only here: {path}')
        elif path not in ours:
            findings.append(f'only there: {path}')
        elif ours[path] != theirs[path]:
            findings.append(f'differs: {path}')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--compare', type=Path)
    parser.add_argument('--skip-tests', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    if args.source_only and args.repo_root:
        parser.error('select source-only or a consumer')
    if args.source_only or args.compare:
        findings = compare_manifests(actual_manifest(skill_dir), load_manifest(skill_dir))
        if args.compare:
            findings += compare_manifests(actual_manifest(skill_dir), actual_manifest(args.compare.resolve()))
        for finding in findings:
            print(finding)
        if findings:
            return 1
        print('portable source valid')
        if not args.repo_root:
            return 0
    command = [sys.executable, '-B', str(skill_dir / 'scripts/render_runtime_adapters.py'), '--check']
    if args.repo_root:
        command.extend(['--repo-root', str(args.repo_root)])
    return subprocess.call(command)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(f'error: {error}', file=sys.stderr)
        raise SystemExit(2)
