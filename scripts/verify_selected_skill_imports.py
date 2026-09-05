#!/usr/bin/env python3
"""Exercise imported tools through disposable MASK links from an unrelated cwd."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mask-program', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    entry = args.mask_program.resolve() / 'mask.py'
    skills = ('trellis-image-to-3d', 'concept-art-approval-pipeline', 'sprite-sheet-animation-updater')
    with tempfile.TemporaryDirectory(prefix='mask-selected-imports-') as directory:
        root = Path(directory).resolve()
        project, personal, unrelated = (root / name for name in ('project', 'personal', 'unrelated'))
        for path in (project, personal, unrelated):
            path.mkdir()
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

        def mask(*arguments):
            run = subprocess.run([sys.executable, '-B', str(entry), *map(str, arguments),
                                  '--home', str(root / 'machine'), '--json'],
                                 cwd=unrelated, env=environment, capture_output=True, text=True)
            result = json.loads(run.stdout)
            if run.returncode or not result['ok']:
                raise RuntimeError(run.stdout + run.stderr)
            return result

        mask('init', '--source', source)
        mask('project', 'init', '--project', project)
        mask('project', 'register', project)
        preview = mask('project', 'require', *skills, '--project', project, '--apply', '--dry-run')
        mask('project', 'require', *skills, '--project', project, '--apply', '--expect-plan-hash', preview['data']['plan_hash'])
        mask('user', 'init')
        mask('user', 'require', *skills)
        preview = mask('user', 'register', '--user-home', personal, '--apply', '--dry-run')
        mask('user', 'register', '--user-home', personal, '--apply', '--expect-plan-hash', preview['data']['plan_hash'])

        scripts = (
            project / '.agents/skills/trellis-image-to-3d/tests/test_trellis_client.py',
            project / '.claude/skills/concept-art-approval-pipeline/scripts/test_build_art_review.py',
            personal / '.agents/skills/sprite-sheet-animation-updater/tests/test_validate_sprite_sheet.py',
        )
        for script in scripts:
            subprocess.run([sys.executable, '-B', str(script)], cwd=unrelated, env=environment, check=True)
        for consumer in (project, personal):
            for adapter in ('.agents', '.claude'):
                for identifier in skills:
                    assert (consumer / adapter / 'skills' / identifier).resolve() == source / 'skills' / identifier
        mask('doctor', '--all', '--check')
        print('PASS: imported tools through both scoped adapters; offline tests; all temporary consumers removed on exit.')


if __name__ == '__main__':
    main()
