#!/usr/bin/env python3
"""Verify the committed canonical RFC bundle through a disposable public MASK consumer."""
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
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    program = args.mask_program.resolve()
    def git(root, *words):
        return subprocess.run(['git', '-C', str(root), *map(str, words)], check=True, capture_output=True, text=True).stdout.strip()
    revision = git(source, 'rev-parse', '--verify', (args.source_revision or 'HEAD') + '^{commit}')
    index = json.loads(git(source, 'show', revision + ':mask-source.json'))
    expected = {path.split('/')[1]: '/'.join(path.split('/')[:-1]) for path in git(source, 'ls-tree', '-r', '--name-only', revision, 'skills').splitlines()
                if path.endswith('/SKILL.md') and len(path.split('/')) == 3}
    assert index['packages'] == expected, (index['packages'], expected)
    names = ['author-rfc', 'grill-rfc', 'grill-me', 'implement-rfc']
    assert index['bundles']['rfc']['skills'] == [dict(source='agentskills', id=name) for name in names]
    with tempfile.TemporaryDirectory(prefix='agentskills-rfc-bundle-') as temporary:
        base = Path(temporary).resolve()
        upstream, home, consumer = base / 'AgentSkills.git', base / 'machine', base / 'consumer'
        git(base, 'clone', '--bare', source, upstream)
        consumer.mkdir()
        git(consumer, 'init', '-b', 'main')
        context = consumer / '.mask/skill-config/implement-rfc'
        context.mkdir(parents=True)
        config = json.loads((source / '.mask/skill-config/implement-rfc/project.json').read_text())
        config.update(project='rfc-bundle-fixture', display_name='RFC bundle fixture', session_prefix='rfc-bundle-fixture', origin_repo_name='consumer')
        (context / 'project.json').write_text(json.dumps(config, indent=2) + '\n')
        (context / 'project.md').write_text('# Disposable RFC bundle consumer\nOnly local fixture checks are authorized.\n')
        environment = dict(os.environ, MASK_HOME=str(home), PYTHONDONTWRITEBYTECODE='1', GIT_TERMINAL_PROMPT='0')
        commands = []
        def mask(*words):
            run = subprocess.run([sys.executable, '-B', str(program / 'mask.py'), *map(str, words), '--json'],
                                 capture_output=True, text=True, cwd=consumer, env=environment, timeout=90)
            result = json.loads(run.stdout)
            assert run.returncode == 0 and not run.stderr and result['ok'], (words, run.returncode, result, run.stderr)
            commands.append(dict(argv=list(map(str, words)), exit_code=run.returncode))
            return result
        mask('tap', 'agentskills', upstream, '--ref', revision)
        mask('tap', 'fetch', 'agentskills')
        catalog = mask('search')['data']['skills']
        assert {row['id']: row['path'] for row in catalog} == expected
        validation = mask('skill', 'validate', '--all')
        shown = mask('bundle', 'show', 'agentskills/rfc')['data']['bundle']
        assert shown['commit'] == revision
        preview = mask('bundle', 'apply', 'agentskills/rfc', '--dry-run')
        assert not (consumer / '.mask.json').exists()
        assert preview['data']['setup']['actions'], preview
        installed = mask('bundle', 'apply', 'agentskills/rfc', '--approve-plan', preview['data']['plan_hash'])
        assert all((consumer / parent / name).is_symlink() for parent in ('.agents/skills', '.claude/skills') for name in names)
        assert {row['id'] for row in json.loads((consumer / '.mask.json').read_text())['skills']} == set(names)
        assert all(row['state'] == 'published' for row in installed['data']['setup']['actions']), installed
        status = mask('status', '--check')
        assert status['data']['healthy']
        assert not mask('bundle', 'apply', 'agentskills/rfc')['changed']
        receipt = dict(source_revision=revision, mask_revision=git(program, 'rev-parse', 'HEAD'),
                       bundle=shown, packages_discovered=len(expected), package_validation=validation['ok'],
                       selected=names, workflow_readiness=status['data'].get('workflow_readiness'),
                       setup=[dict(skill=row.get('skill'), action=row.get('action'), state=row['state']) for row in installed['data']['setup']['actions']],
                       healthy=True, host_load='not_verified', platform=sys.platform, commands=commands,
                       fixture_cleanup='TemporaryDirectory removed on completion')
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(f"Canonical agentskills/rfc ready: {len(names)} skills; {len(expected)} packages preserved; reviewed setup published.")


if __name__ == '__main__':
    main()
