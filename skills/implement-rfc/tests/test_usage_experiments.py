"""Variable arms and native inclusive/partial evidence through existing reports."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import usage_experiments as study
from usage_outcomes import Outcomes, validate_experiment
import usage_report
from usage_accounting import reconcile
import test_usage_report as report_fixture


def fixture():
    arm=dict(arm_id='native',strategy='native-astra-ultra',topology_id='native',recipe_revision='1',
             requested_routing={'primary':dict(provider='codex',model='gpt-6-astra',effort='ultra')},
             child_route_ownership='native_system',effective_configuration_reference='fixture:config',
             observed_serving_reference=None,source_worktree='fixture:source',tracker_worktree=None)
    return dict(schema=study.SCHEMA,status='frozen',study_id='fixture-study',
        comparison_kind='practical_strategy_comparison_not_topology_only',common_inputs=dict.fromkeys(study.COMMON,'fixture:input'),
        arms=[arm],judges=[dict(family='Astra',exact_model='fixture-model',effort='high')],
        order=dict(implementation=['native'],candidate_labels_private=True,judge_orders={'Astra':['candidate-a']}))


def assignment(session='s',**changes):
    return dict(session=session,task_id='fixture-study:native:task',attempt_id='initial-1',evidence_ref='fixture:assignment',
        since='2026-09-19T00:00:00Z',until='2026-09-20T00:00:00Z',study_id='fixture-study',arm_id='native',
        strategy='native-astra-ultra',topology_id='native',recipe_revision='1',phase='initial',cost_bucket='arm',
        coverage='partial',route_ownership='system',**changes)


def outcomes(*assignments):
    return Outcomes(dict(schema='implement-rfc.outcomes.v1',assignments=list(assignments),events=[]))


def event(session='s',number=1):
    return dict(event_id=str(number),provider='codex',provider_account_alias='account',device_alias='device',
        session=session,owner_session=session,ownership='explicit',response_id='response-'+str(number),
        timestamp='2026-09-19T12:00:00Z',kind='response_usage',usage=dict(input_tokens=10,output_tokens=5))


def aggregate(**changes):
    value=dict(observation_id='aggregate',arm_id='native',attempt_id='initial-1',provider='codex',provider_account_alias='account',
        device_alias='device',since='2026-09-19T00:00:00Z',until='2026-09-20T00:00:00Z',usage=dict(input_tokens=100,output_tokens=20),
        semantics='inclusive',coverage='whole_attempt',evidence_ref='fixture:native-inclusive',phase='initial')
    value.update(changes);return value


class ExperimentTests(unittest.TestCase):
    def test_draft_freeze_and_open_topology(self):
        value=fixture();value['arms'][0]['topology_id']='fifth-synthetic';validate_experiment(value)
        value['status']='draft_not_runnable';value['common_inputs']['task_reference']=None
        self.assertIn('task_reference',study.validate(value))
        value['status']='frozen'
        with self.assertRaisesRegex(ValueError,'unresolved'):study.validate(value)
        value=fixture();value['arms'].append(copy.deepcopy(value['arms'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):study.validate(value)

    def test_partial_unknown_role_usage_is_retained_without_exact_claim(self):
        result=study.summarize(fixture(),outcomes(assignment()),reconcile([event()]))
        row=result['arms'][0]['attempts'][0]
        self.assertEqual(row['observed_tokens'],15);self.assertIsNone(row['exact_tokens'])
        self.assertEqual(row['route_ownership'],['system']);self.assertEqual(result['production_deliveries'],0)
        self.assertIsNone(result['total_exact_tokens'])

    def test_zero_children_and_inclusive_total_with_visible_children_count_once(self):
        value=fixture();value['inclusive_observations']=[aggregate()]
        for events,assignments in [([],[]),([event()],[assignment()]),([event(),event('child',2)],[assignment(),assignment('child')])]:
            result=study.summarize(value,outcomes(*assignments),reconcile(events))
            row=result['arms'][0]['attempts'][0]
            self.assertEqual((row['observed_tokens'],row['exact_tokens'],row['phase']),(120,120,'initial'))
            self.assertEqual(result['total_observed_tokens'],120)

    def test_unknown_conflicting_overlapping_and_partial_totals_are_not_exact(self):
        for observations in ([aggregate(semantics='unknown')],[aggregate(coverage='partial')],
                             [aggregate(usage=dict(input_tokens=1,output_tokens=1))],
                             [aggregate(),aggregate(observation_id='other')]):
            value=fixture();value['inclusive_observations']=observations
            row=study.summarize(value,outcomes(assignment()),reconcile([event()]))['arms'][0]['attempts'][0]
            self.assertIsNone(row['exact_tokens'])
            self.assertEqual(row['observed_tokens'],15)
            self.assertTrue(row['aggregate_observations'])

    def test_missing_arm_coverage_and_deviations_stay_visible(self):
        value=fixture();extra=copy.deepcopy(value['arms'][0]);extra['arm_id']='other';value['arms'].append(extra)
        value['order']['implementation'].append('other');value['order']['judge_orders']['Astra'].append('candidate-b')
        assigned=assignment();assigned.update(coverage='complete',deviations=['planner_takeover'])
        result=study.summarize(value,outcomes(assigned),reconcile([event()]))
        self.assertEqual(result['arms'][0]['attempts'][0]['deviations'],['planner_takeover'])
        self.assertEqual(result['arms'][1]['attempts'],[]);self.assertIsNone(result['total_exact_tokens'])

    def test_repairs_and_shared_setup_are_separate(self):
        initial=assignment();initial['coverage']='complete'
        repair=assignment('repair');repair.update(attempt_id='repair-1',phase='repair',coverage='complete')
        setup=assignment('setup');setup.update(arm_id=None,attempt_id='setup-1',cost_bucket='setup',coverage='complete')
        result=study.summarize(fixture(),outcomes(initial,repair,setup),reconcile([event(),event('repair',2),event('setup',3)]))
        self.assertEqual({r['phase'] for r in result['arms'][0]['attempts']},{'initial','repair'})
        self.assertEqual(result['shared_costs'][0]['cost_bucket'],'setup')
        self.assertEqual(result['total_observed_tokens'],45)
        self.assertEqual(result['total_exact_tokens'],45)
        repair['strategy']='unplanned-upgrade'
        with self.assertRaisesRegex(ValueError,'differs'):
            study.summarize(fixture(),outcomes(repair),reconcile([event('repair',2)]))

    def test_three_captures_share_one_reconciliation_and_preserve_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            self.root=Path(directory)
            capture=lambda name:report_fixture.ReportTests.capture(self,name,extra={'events.jsonl':(json.dumps(event())+'\n').encode()})
            paths=[capture(name+'.zip') for name in ('a','b','c')]
            value=fixture();value['inclusive_observations']=[aggregate()]
            doc=dict(schema='implement-rfc.outcomes.v1',assignments=[assignment()],events=[])
            result=usage_report.report(paths,self.root/'report',outcomes=doc,experiment=value,compare=True)
            self.assertEqual(result['study']['total_observed_tokens'],120)
            self.assertEqual(result['study']['arms'][0]['attempts'][0]['observed_components_tokens'],15)
            ledger=(self.root/'report/ledger.csv').read_text()
            self.assertIn('native-astra-ultra',ledger);self.assertIn('route_ownership',ledger)
            self.assertEqual(result['acceptance_unit'],'experiment_alternative')
