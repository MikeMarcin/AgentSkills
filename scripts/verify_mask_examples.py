#!/usr/bin/env python3
"""Run the canonical public-CLI example scenario from the selected MASK checkout."""
import argparse
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--mask-program', type=Path, required=True)
args = parser.parse_args()
root = args.mask_program.resolve()
if not (root / 'mask.py').is_file() or not (root / 'tests/test_end_to_end.py').is_file():
    parser.error('Select the completed ManageAgentSkills checkout with its acceptance fixtures.')
raise SystemExit(subprocess.run([sys.executable, '-B', '-m', 'unittest', 'tests.test_end_to_end.EndToEndTests.test_public_management_sequence'], cwd=root).returncode)
