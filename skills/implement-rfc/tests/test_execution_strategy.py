"""Recipe selection is passive, open-ended and independent of storage/host loading."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import execution_strategy as strategy


class StrategyTests(unittest.TestCase):
    def test_selection_precedence_and_exact_resume(self):
        direct = strategy.resolve('direct-astra-max')
        self.assertEqual(strategy.resolve()['topology_id'], 'coordinator-integrator')
        self.assertEqual(strategy.resolve(preserved=direct, preference='coordinator-integrator'), direct)
        self.assertEqual(strategy.resolve('coordinator-integrator', preserved=direct)['topology_id'], 'coordinator-integrator')
        self.assertEqual(strategy.resolve(preference='direct')['topology_id'], 'direct')
        self.assertEqual(direct['routing']['primary']['effort'], 'max')
        self.assertEqual(direct['host_load'], 'not_verified')
        self.assertNotIn('mode', direct)

    def test_only_selected_instruction_bytes_are_loaded(self):
        original = Path.read_bytes
        read = []
        def observe(path):
            read.append(path.name)
            return original(path)
        with patch.object(Path, 'read_bytes', observe):
            strategy.resolve('direct')
        self.assertEqual(read, ['engineering-contract.md', 'direct.md'])

    def test_unknown_duplicate_escape_incompatible_and_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            shutil.copytree(strategy.PACKAGE / 'config', package / 'config')
            shutil.copytree(strategy.PACKAGE / 'references', package / 'references')
            shutil.copy(strategy.PACKAGE / 'mask-workflow.json', package / 'mask-workflow.json')
            path = package / 'config/strategy-catalog.json'
            original = json.loads(path.read_text())
            for change in ('duplicate', 'escape', 'contract', 'unknown-default', 'profile', 'malformed', 'symlink'):
                value = copy.deepcopy(original)
                if change == 'duplicate':
                    value['recipes'].append(copy.deepcopy(value['recipes'][0]))
                elif change == 'escape':
                    value['recipes'][0]['entrypoint'] = '../outside.md'
                elif change == 'contract':
                    value['recipes'][0]['common_contract'] = 'future'
                elif change == 'unknown-default':
                    value['default'] = 'missing'
                elif change == 'profile':
                    value['recipes'][0]['requirement_profile'] = 'missing'
                elif change == 'malformed':
                    value['recipes'][0]['unexpected'] = True
                else:
                    (package / 'alias.md').symlink_to(package / 'references/engineering-contract.md')
                    value['recipes'][0]['entrypoint'] = 'alias.md'
                path.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    strategy.resolve('direct', package=package)
            path.write_text(json.dumps(original))
            selected = strategy.resolve('direct', package=package)
            (package / 'references/strategies/direct.md').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'changed'):
                strategy.resolve(preserved=selected, package=package)
            with self.assertRaises(ValueError):
                strategy.resolve('unregistered', package=package)
            path.write_text('{"schema":1,"schema":2}')
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                strategy.load_catalog(package)
