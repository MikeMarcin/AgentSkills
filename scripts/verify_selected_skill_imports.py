#!/usr/bin/env python3
"""Exercise committed imports through two disposable public MASK consumers."""
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
    parser.add_argument('--source-revision', help='Exact committed source candidate (defaults to HEAD)')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    entry = args.mask_program.resolve() / 'mask.py'
    skills = ('manage-agent-skills', 'trellis-image-to-3d', 'concept-art-approval-pipeline', 'sprite-sheet-animation-updater')
    if not entry.is_file():
        parser.error('Select the ManageAgentSkills checkout containing mask.py.')

    def git(root, *arguments):
        return subprocess.run(['git', '-C', str(root), *map(str, arguments)],
                              capture_output=True, text=True, check=True).stdout.strip()

    revision = git(source, 'rev-parse', '--verify', (args.source_revision or 'HEAD') + '^{commit}')
    with tempfile.TemporaryDirectory(prefix='mask-selected-imports-') as directory:
        root = Path(directory).resolve()
        project, second, unrelated = (root / name for name in ('project', 'second-consumer', 'unrelated'))
        for path in (project, second, unrelated):
            path.mkdir()
        for consumer in (project, second):
            git(consumer, 'init', '-b', 'main')
        upstream = root / 'AgentSkills.git'
        git(root, 'clone', '--bare', source, upstream)
        git(upstream, 'update-ref', 'refs/heads/main', revision)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_TERMINAL_PROMPT='0')

        def mask(*arguments):
            run = subprocess.run([sys.executable, '-B', str(entry), *map(str, arguments),
                                  '--home', str(root / 'machine'), '--json'],
                                 cwd=unrelated, env=environment, capture_output=True, text=True, timeout=90)
            result = json.loads(run.stdout)
            if run.returncode or not result['ok']:
                raise RuntimeError(run.stdout + run.stderr)
            return result

        mask('tap', 'agentskills', upstream, '--ref', 'refs/heads/main')
        mask('tap', 'fetch', 'agentskills')
        catalog = {row['id'] for row in mask('search')['data']['skills']}
        assert set(skills) <= catalog, catalog
        for consumer in (project, second):
            preview = mask('install', *skills, '--project', consumer, '--dry-run')
            mask('install', *skills, '--project', consumer, '--no-update',
                 '--approve-plan', preview['data']['plan_hash'])
            mask('status', '--project', consumer, '--check')

        scripts = (
            project / '.agents/skills/trellis-image-to-3d/tests/test_trellis_client.py',
            project / '.claude/skills/concept-art-approval-pipeline/scripts/test_build_art_review.py',
            second / '.agents/skills/sprite-sheet-animation-updater/tests/test_validate_sprite_sheet.py',
        )
        for script in scripts:
            subprocess.run([sys.executable, '-B', str(script)], cwd=unrelated, env=environment, check=True)
        for consumer in (project, second):
            for adapter in ('.agents', '.claude'):
                for identifier in skills:
                    linked = consumer / adapter / 'skills' / identifier
                    assert linked.is_symlink(), linked
                    # Normal installs resolve locked artifacts, not authoring links.
                    expected = git(source, 'show', f'{revision}:skills/{identifier}/SKILL.md')
                    assert linked.joinpath('SKILL.md').read_text().strip() == expected
        preview = mask('uninstall', 'manage-agent-skills', '--project', project, '--dry-run')
        mask('uninstall', 'manage-agent-skills', '--project', project,
             '--approve-plan', preview['data']['plan_hash'])
        assert not (project / '.agents/skills/manage-agent-skills').exists()
        assert (second / '.agents/skills/manage-agent-skills').is_symlink()
        assert (project / '.agents/skills/trellis-image-to-3d').is_symlink()
        mask('status', '--all', '--check')
        print(f'PASS: source {revision}; public tap/fetch/search/install/status/uninstall; '
              'both adapters and two consumers; offline tool tests; temporary roots removed.')


if __name__ == '__main__':
    main()
