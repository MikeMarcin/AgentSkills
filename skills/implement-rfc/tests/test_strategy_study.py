"""Kit shape checks and a fifth recipe use ordinary board, checkpoint and usage paths."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import execution_strategy as strategy
import strategy_study
import usage_experiments
from usage_accounting import reconcile
from project_fixtures import git
import test_primary_checkpoint as primary_fixture
import test_usage_experiments as usage_fixture


class StrategyStudyTests(unittest.TestCase):
    def test_template_is_valid_and_not_runnable(self):
        value = strategy.read_json(SKILL / 'references/strategy-study/study.template.json')
        result = strategy_study.check(value)
        self.assertEqual(result['state'], 'draft_not_runnable')
        self.assertFalse(result['launch_authorized'])
        self.assertEqual(len(value['arms']), 3)
        self.assertIn('task_reference', result['unresolved'])
        self.assertTrue(all(v is None for v in value['common_inputs'].values()))
        self.assertTrue(all(a['source_worktree'] is None for a in value['arms']))
        value['status'] = 'frozen'
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            strategy_study.check(value)
        done = subprocess.run([sys.executable, '-B', str(SKILL / 'scripts/strategy_study.py'), '--study',
            str(SKILL / 'references/strategy-study/study.template.json'), '--require-frozen'], capture_output=True, text=True)
        self.assertEqual(done.returncode, 1, done.stderr)

    def test_frozen_registration_and_judge_consistency(self):
        value = usage_fixture.fixture()
        self.assertEqual(strategy_study.check(value)['state'], 'frozen')
        for key, change in [('strategy', 'missing'), ('topology_id', 'other'), ('recipe_revision', 'future'),
                            ('child_route_ownership', 'recipe')]:
            changed = copy.deepcopy(value)
            changed['arms'][0][key] = change
            with self.assertRaises(ValueError):
                strategy_study.check(changed)
        value['judges'].append(dict(family='Fable', exact_model='fixture-judge', effort='high'))
        value['order']['judge_orders']['Fable'] = ['different-candidate']
        with self.assertRaisesRegex(ValueError, 'same candidate'):
            strategy_study.check(value)
        value['order']['judge_orders']['Fable'] = [{}]
        with self.assertRaises(ValueError):
            strategy_study.check(value)

    def test_fifth_recipe_uses_existing_board_acceptance_and_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            package = base / 'package'
            shutil.copytree(SKILL, package, ignore=shutil.ignore_patterns('__pycache__'))
            catalog_path = package / 'config/strategy-catalog.json'
            catalog = strategy.read_json(catalog_path)
            self.assertEqual(len(catalog['recipes']), 4)
            recipe = copy.deepcopy(next(r for r in catalog['recipes'] if r['id'] == 'direct'))
            recipe.update(id='fifth-synthetic', entrypoint='references/strategies/fifth-synthetic.md')
            (package / recipe['entrypoint']).write_text('# Synthetic fixture\n\nPrimary owns engineering and bookkeeping under the common contract.\n')
            catalog['recipes'].append(recipe)
            catalog_path.write_text(json.dumps(catalog))
            selected = strategy.resolve('fifth-synthetic', package=package)
            self.assertEqual(selected['instruction_paths'][1], recipe['entrypoint'])
            case = primary_fixture.PrimaryCheckpointTests()
            case.base = base
            root = case.consumer('fifth')
            link = root / '.agents/skills/implement-rfc'
            link.unlink()
            link.symlink_to(package, target_is_directory=True)
            selected_path = root / 'runtime/selection.json'
            selected_path.write_text(json.dumps(selected))
            bound = case.cli(root, 'milestone_checkpoint.py', 'bind', '--target', 'FX-0001',
                '--selection', str(selected_path), '--run-id', 'fifth', '--segment-id', 'initial', '--mandate-revision', '1', '--json')
            (root / 'product.py').write_text('def add(a, b):\n    return a + b\n')
            case.cli(root, 'record_evidence.py', '--criterion', 'adds', '--output', str(root / 'runtime/check.json'),
                     '--', sys.executable, '-B', 'check_product.py')
            git(root, 'add', 'product.py')
            git(root, 'commit', '-m', 'Synthetic product correction')
            acceptance = root / 'runtime/acceptance.json'
            acceptance.write_text(json.dumps(dict(approved=True, decision='done', records=[dict(criterion='adds', outcome='pass',
                revision=git(root, 'rev-parse', 'HEAD'), evidence=dict(kind='command', detail='python -B check_product.py passed'))])))
            for card in ('FX-0001', 'FX-0002'):
                case.cli(root, 'issue_board.py', 'claim', card, '--json')
                case.cli(root, 'issue_board.py', 'finish', card, '--acceptance', str(acceptance), '--json')
            (root / 'runtime/checkpoint.json').write_text(json.dumps(bound))
            (root / 'runtime/observation.json').write_text(json.dumps(case.observation(root, bound)))
            checked = case.cli(root, 'milestone_checkpoint.py', 'check', '--checkpoint', str(root / 'runtime/checkpoint.json'),
                '--observation', str(root / 'runtime/observation.json'), '--execution', 'quiescent', '--json')
            self.assertEqual(checked['action'], 'stop')
            study = usage_fixture.fixture()
            arm = study['arms'][0]
            arm.update(strategy='fifth-synthetic', topology_id='fifth-synthetic', child_route_ownership='disabled')
            strategy_study.check(study, package=package)
            assigned = usage_fixture.assignment()
            assigned.update(strategy='fifth-synthetic', topology_id='fifth-synthetic', coverage='complete')
            summary = usage_experiments.summarize(study, usage_fixture.outcomes(assigned), reconcile([usage_fixture.event()]))
            self.assertEqual(summary['total_exact_tokens'], 15)
            self.assertEqual(summary['production_deliveries'], 0)
