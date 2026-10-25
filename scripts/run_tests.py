#!/usr/bin/env python3
"""Run the shipped offline tests; optionally include real disposable MASK checks."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mask-program', type=Path, help='ManageAgentSkills checkout containing mask.py')
    args = parser.parse_args()
    try:
        import jsonschema  # noqa: F401: absence must fail, rather than skip schema tests
    except ImportError:
        parser.error('Install requirements-dev.txt before running the test suite.')
    root = Path(__file__).resolve().parents[1]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if args.mask_program is not None:
        program = args.mask_program.resolve() / 'mask.py'
        if not program.is_file():
            parser.error('--mask-program must name a checkout containing mask.py.')
        environment['MASK_TEST_PROGRAM'] = str(program)
        environment['MASK_PROGRAM'] = str(program.parent)
    for skill, directory, pattern in (
        ('implement-rfc', 'tests', 'test_*.py'),
        ('remote-station', 'tests', 'test_*.py'),
        ('attended-review', 'tests', 'test_*.py'),
        ('author-rfc', 'tests', 'test_*.py'),
        ('wizard', 'tests', 'test_*.py'),
        ('trellis-image-to-3d', 'tests', 'test_*.py'),
        ('sprite-sheet-animation-updater', 'tests', 'test_*.py'),
        ('concept-art-approval-pipeline', 'scripts', 'test_build_art_review.py'),
    ):
        print(f'Testing {skill}', flush=True)
        result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                                 '-s', str(root / 'skills' / skill / directory), '-p', pattern, '-v'],
                                cwd=root, env=environment)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
