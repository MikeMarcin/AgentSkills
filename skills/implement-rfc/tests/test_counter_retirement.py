"""Removed categories retain allocation safety through Git, without tombstones."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import CONFIG, write_context


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'issue_board.py'


class CounterRetirementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = copy.deepcopy(CONFIG)
        self.config['next_id'] = {'mode': 'per-area', 'path': 'tracker/counters'}
        write_context(self.root, config=self.config)
        for lane in self.config['lanes'].values():
            (self.root / self.config['issue_root'] / lane).mkdir(parents=True)
        (self.root / self.config['rfc_root']).mkdir(parents=True, exist_ok=True)
        self.counter = self.root / 'tracker/counters/AAA'
        self.counter.parent.mkdir(parents=True)
        self.counter.write_text('AAA-0005\n')
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.email', 'fixture@example.test')
        self.git('config', 'user.name', 'Fixture')
        self.commit()
        self.counter.unlink()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args],
                              check=True, capture_output=True, text=True)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'Fixture counter')

    def public(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPT), '--repo-root',
                                 str(self.root), *args, '--json'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_removed_category_validates_and_resumes_other_branch_high_water(self):
        self.git('restore', str(self.counter))
        self.git('checkout', '-qb', 'other')
        self.counter.write_text('AAA-0020\n')
        self.commit()
        self.git('checkout', '-q', 'main')
        self.counter.unlink()
        self.commit()
        self.assertTrue(self.public('validate')['valid'])
        result = self.public('allocate', '--area', 'AAA', '--count', '2',
                             '--reserve-for', 'fixture')
        self.assertEqual(result['ids'], ['AAA-0020', 'AAA-0021'])
        self.assertEqual(self.counter.read_text(), 'AAA-0022\n')
        self.assertTrue(self.public('validate')['valid'])

    def test_current_card_still_requires_counter(self):
        lane = self.config['lanes']['backlog']
        card = self.root / self.config['issue_root'] / lane / 'AAA-0001-card.md'
        card.write_text('---\nschema: implement-rfc.card.v1\nid: AAA-0001\n'
                        'title: Fixture\nstatus: Backlog\nrfcs: []\ndepends_on: []\n---\n')
        result = self.public('validate', expected=1)
        self.assertIn('missing counter for AAA', str(result['errors']))

    def test_current_reservation_still_requires_counter(self):
        receipt = self.root / self.config['reservations_dir'] / 'fixture.json'
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({'ids': ['AAA-0004']}))
        result = self.public('validate', expected=1)
        self.assertIn('missing counter for AAA', str(result['errors']))

    def test_reintroduced_counter_cannot_rewind(self):
        self.counter.write_text('AAA-0001\n')
        result = self.public('allocate', '--area', 'AAA', '--count', '1',
                             '--reserve-for', 'fixture', expected=1)
        self.assertIn('rewinds historical high water AAA-0005', str(result['errors']))
        self.assertEqual(self.counter.read_text(), 'AAA-0001\n')

    def test_exhausted_category_cannot_restart(self):
        self.counter.write_text('AAA-9999\n')
        self.commit()
        self.counter.unlink()
        result = self.public('allocate', '--area', 'AAA', '--count', '1',
                             '--reserve-for', 'fixture', expected=1)
        self.assertIn('ID space exhausted', str(result['errors']))
        self.assertFalse(self.counter.exists())

    def test_new_category_still_starts_at_one(self):
        result = self.public('allocate', '--area', 'BBB', '--count', '1',
                             '--reserve-for', 'fixture')
        self.assertEqual(result['ids'], ['BBB-0001'])

    def test_single_file_counter_remains_required(self):
        self.config['next_id'] = {'mode': 'single-file', 'path': 'tracker/counters/AAA'}
        write_context(self.root, config=self.config)
        result = self.public('validate', expected=1)
        self.assertIn('counter file missing', str(result['errors']))


if __name__ == '__main__':
    unittest.main()
