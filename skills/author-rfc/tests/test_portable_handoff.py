"""Public portable pack import/binding and passive MASK package validation."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / 'skills/implement-rfc'
PACK = Path(__file__).parent / 'fixtures/portable-pack'
sys.path.insert(0, str(SKILL / 'tests'))
from project_fixtures import git, init_repo, write_context


class PortableHandoffTests(unittest.TestCase):
    def run_command(self, *command, cwd, code=0):
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        self.assertEqual(done.returncode, code, done.stdout + done.stderr)
        return done.stdout

    def test_generated_pack_two_consumer_handoff_and_selector_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            for name, prefix, docs in [('alpha', 'ALP', 'docs'), ('beta', 'BET', 'specs')]:
                root = base / name
                config = init_repo(root, token=name)
                config.update(rfc_root=f'{docs}/rfcs', issue_root=f'{docs}/items',
                              reservations_dir=f'{docs}/items/_reservations',
                              next_id={'mode': 'single-file', 'path': f'{docs}/items/NEXT_ID'})
                write_context(root, config=config)
                link = root / '.agents/skills/implement-rfc'
                link.parent.mkdir(parents=True)
                link.symlink_to(SKILL, target_is_directory=True)
                source = base / (name + '-draft')
                shutil.copytree(PACK, source)
                shutil.copyfile(SKILL / 'schemas/milestone-plan.schema.json', source / 'milestone-plan.schema.json')
                shutil.copyfile(SKILL / 'examples/milestone-plans/IMPLEMENTATION_PROMPT.md', source / 'IMPLEMENTATION_PROMPT.md')
                validator = link / 'examples/milestone-plans/validate.py'
                self.run_command(sys.executable, '-B', str(validator), str(source / 'milestone-plan.json'), cwd=base)
                view = self.run_command(sys.executable, '-B', str(validator), str(source / 'milestone-plan.json'), '--render', cwd=base)
                (source / 'MILESTONES.md').write_text(view)
                original = json.loads((source / 'milestone-plan.json').read_text())

                def cli(*args, code=0):
                    output = self.run_command(sys.executable, '-B', str(link / 'scripts/milestone_plan.py'),
                                              '--repo-root', str(root), *args, '--json', cwd=base, code=code)
                    return json.loads(output)

                discovered = cli('discover', '--source-root', str(source))
                self.assertEqual(discovered['milestone_ids'], ['single-file', 'batch-resume'])
                self.assertFalse((root / config['rfc_root']).exists())
                mapping = {f'DRAFT-{n:04}': f'{prefix}-{n:04}' for n in range(1, 4)}
                mapping['RFC-DRAFT-0001'] = f'RFC-{prefix}-0001'
                (source / 'map.json').write_text(json.dumps(mapping))

                def remap(text):
                    for old, new in sorted(mapping.items(), key=lambda pair: -len(pair[0])):
                        text = text.replace(old, new)
                    return text

                rfc = root / config['rfc_root'] / f'RFC-{prefix}-0001-ledger-export.md'
                rfc.parent.mkdir(parents=True)
                imported = remap((source / 'rfcs/RFC-DRAFT-0001-ledger-export.md').read_text())
                # Import remaps document pointers as well as typed identities.
                rfc.write_text(imported.replace('../milestone-plan.json', 'plans/ledger-export/milestone-plan.json'))
                lane = root / config['issue_root'] / config['lanes']['backlog']
                lane.mkdir(parents=True)
                for card in (source / 'issues').glob('*.md'):
                    (lane / remap(card.name)).write_text(remap(card.read_text()))
                (root / config['next_id']['path']).write_text(prefix + '-0004\n')
                git(root, 'add', '.mask', docs)
                git(root, 'commit', '-m', 'Import actual remapped documents')
                adopted = cli('adopt', '--source-root', str(source), '--id-map', 'map.json')
                plan = json.loads((root / adopted['plan_path']).read_text())
                self.assertEqual(plan['milestones'], json.loads(remap(json.dumps(original)))['milestones'])
                self.assertEqual(cli('discover', '--target', f'RFC-{prefix}-0001')['milestone_ids'],
                                 ['single-file', 'batch-resume'])
                for milestone in ('single-file', 'batch-resume'):
                    bound = cli('bind', '--target', f'RFC-{prefix}-0001', '--milestone', milestone)
                    self.assertEqual(bound['references'], 'resolved')
                    self.assertTrue(bound['obligations'])
                    self.assertTrue(all(row['source'] == f'RFC-{prefix}-0001' for row in bound['obligations']))
                text = rfc.read_text()
                rfc.write_text(text.replace('**AC02:**', '**OTHER02:**'))
                missing = cli('bind', '--target', f'RFC-{prefix}-0001', '--milestone', 'batch-resume', code=2)
                self.assertIn('missing', json.dumps(missing).lower())
                rfc.write_text(text + '\n- **AC02:** Another authoritative criterion definition.\n')
                ambiguous = cli('bind', '--target', f'RFC-{prefix}-0001', '--milestone', 'batch-resume', code=2)
                self.assertIn('ambiguous', json.dumps(ambiguous).lower())
                rfc.write_text(text)
                # A new source cannot overwrite the adopted live intent/provenance.
                changed = base / (name + '-changed')
                shutil.copytree(source, changed)
                proposal = copy.deepcopy(original)
                proposal['milestones'][0]['outcome'] = 'Changed source intent'
                (changed / 'milestone-plan.json').write_text(json.dumps(proposal))
                cli('adopt', '--source-root', str(changed), '--id-map', 'map.json', code=2)

    def test_passive_packages_through_disposable_mask(self):
        # MASK is selected explicitly; never use the live registry or real selections.
        import os
        program = os.environ.get('MASK_PROGRAM')
        if not program:
            self.skipTest('Set MASK_PROGRAM to the selected MASK checkout for package acceptance')
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = base / 'source'
            repository.mkdir()
            git(repository, 'init', '-b', 'main')
            git(repository, 'config', 'user.name', 'fixture')
            git(repository, 'config', 'user.email', 'fixture@example.invalid')
            names = ('author-rfc', 'grill-rfc', 'grill-me', 'implement-rfc')
            for name in names:
                shutil.copytree(ROOT / 'skills' / name, repository / 'skills' / name,
                                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            git(repository, 'add', 'skills')
            git(repository, 'commit', '-m', 'Exact working candidate packages')
            remote = base / 'source.git'
            self.run_command('git', 'clone', '--bare', str(repository), str(remote), cwd=base)

            def mask(*args):
                output = self.run_command(sys.executable, '-B', str(Path(program) / 'mask.py'),
                                          *args, '--home', str(base / 'mask-home'), '--json', cwd=base)
                return json.loads(output)

            mask('tap', 'candidate', str(remote))
            mask('tap', 'fetch', 'candidate')
            for name in names:
                result = mask('skill', 'validate', name)
                self.assertTrue(result['ok'], result)


if __name__ == '__main__':
    unittest.main()
