"""Strict recipe routing, iterative feedback and visible ownership deviations."""
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import execution_strategy as strategy
import planner_worker
import strategy_host


def selection():
    return strategy.resolve('planner-cheaper-worker-strict', routing={
        'worker': dict(provider='codex', model='fixture-worker', effort='low')})


def event(kind, actor='worker-1', **extras):
    return dict(kind=kind, actor=actor, evidence_ref='fixture:host-event', **extras)


def record():
    routes = selection()['routing']
    return dict(schema=planner_worker.SCHEMA, coverage='complete', events=[
        event('start', 'planner', role='planner', route=routes['primary']),
        event('start', role='worker', route=routes['worker']), event('product-edit'),
        event('feedback', 'planner'), event('product-edit'), event('stop'),
        event('bookkeeping', 'planner')])


class PlannerWorkerTests(unittest.TestCase):
    def test_missing_exact_route_and_scoped_settings(self):
        incomplete = strategy.resolve('planner-cheaper-worker-strict')
        self.assertEqual(incomplete['missing_routes'], ['worker'])
        with self.assertRaisesRegex(ValueError, 'exact'):
            strategy_host.render(incomplete)
        selected = selection()
        self.assertEqual(selected['owners']['product_edits'], 'worker')
        config = strategy_host.render(selected)
        agents = tomllib.loads(config)['agents']
        self.assertEqual(agents['max_concurrent_threads_per_session'], 1)
        self.assertEqual(agents['default_subagent_model'], 'fixture-worker')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'requested.toml'
            path.write_text(config)
            result = strategy_host.inspect(selected, [path], complete_inputs=True)
            self.assertEqual(result['state'], 'configuration_consistent')
            self.assertEqual(result['host_load'], 'not_verified')
            path.write_text(config.replace('fixture-worker', 'unplanned-upgrade'))
            self.assertIn('worker_route_mismatch_or_unknown', {f['kind'] for f in strategy_host.inspect(selected, [path])['findings']})
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            strategy.resolve('planner-worker', routing={'worker': dict(provider='other', model='x', effort='low')})
        with self.assertRaisesRegex(ValueError, 'exact'):
            strategy.resolve('planner-worker', routing={'worker': dict(provider='codex', model='<worker-model>', effort='low')})

    def test_iterative_feedback_and_ownership_deviations(self):
        self.assertEqual(planner_worker.check(selection(), record())['state'], 'consistent')
        cases = [(event('product-edit', 'planner'), 'planner_takeover'),
                 (event('bookkeeping'), 'worker_owned_bookkeeping'),
                 (event('delegate'), 'recursive_delegation'),
                 (event('start', 'worker-2', role='worker', route=selection()['routing']['worker']), 'multiple_active_workers'),
                 (event('start', 'reviewer', role='reviewer', route=selection()['routing']['worker']), 'unexpected_child_or_role'),
                 (event('route', route=dict(provider='codex', model='upgraded', effort='high')), 'route_change')]
        for extra, deviation in cases:
            value = record()
            value['events'].insert(3, extra)
            checked = planner_worker.check(selection(), value)
            self.assertEqual(checked['state'], 'deviated')
            self.assertIn(deviation, checked['deviations'])

    def test_unknown_active_and_malformed_observations(self):
        value = record()
        value['events'] = value['events'][:3]
        self.assertEqual(planner_worker.check(selection(), value)['state'], 'incomplete')
        value = record()
        value['events'][1].pop('route')
        self.assertTrue(planner_worker.check(selection(), value)['unknown'])
        value['events'][0]['mystery'] = True
        with self.assertRaises(ValueError):
            planner_worker.check(selection(), value)
