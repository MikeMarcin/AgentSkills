"""Offline artifact tests, not native-agent compliance or product acceptance."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from plan_contract import load_json, normalize, fingerprint, validate_plan, remap_plan, render, LIMIT
from validate_pack import check_packet, frontmatter, safe_member

ROOT=Path(__file__).resolve().parents[1]


class PlanContractTests(unittest.TestCase):
    def setUp(self):
        self.plan=load_json(ROOT/'fixtures/raw-pack/milestone-plan.json')

    def assert_invalid(self, plan, substring):
        errors=validate_plan(plan)
        self.assertTrue(any(substring in e for e in errors),errors)

    def test_valid_authored_plan(self):
        self.assertEqual(validate_plan(self.plan),[])
        self.assertEqual([len(m['work']) for m in self.plan['milestones']],[3,3])

    def test_defaults_have_same_fingerprint(self):
        self.assertEqual(fingerprint(self.plan),fingerprint(normalize(self.plan)))

    def test_whitespace_does_not_change_fingerprint(self):
        rebuilt=json.loads(json.dumps(self.plan,indent=4))
        self.assertEqual(fingerprint(self.plan),fingerprint(rebuilt))

    def test_authored_preference_order_is_preserved(self):
        changed=copy.deepcopy(self.plan)
        changed['milestones'].reverse()
        self.assertEqual(validate_plan(changed),[])  # Dependencies need not follow array order.
        self.assertNotEqual(fingerprint(self.plan),fingerprint(changed))

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"id":"a","id":"b"}')
            with self.assertRaisesRegex(ValueError,'duplicate'):load_json(p)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"x":NaN}')
            with self.assertRaisesRegex(ValueError,'nonfinite'):load_json(p)

    def test_input_bound(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'large.json';p.write_bytes(b' '*(LIMIT+1))
            with self.assertRaisesRegex(ValueError,'exceeds'):load_json(p)

    def test_unknown_version(self):
        self.plan['schema']='unknown'
        self.assert_invalid(self.plan,'unsupported')

    def test_live_state_and_model_not_allowed(self):
        for key in ('status','producer_id','model','commands'):
            changed=copy.deepcopy(self.plan);changed[key]='not-authored-data'
            self.assert_invalid(changed,'unknown fields')

    def test_empty_scope(self):
        self.plan['scope']={}
        self.assert_invalid(self.plan,'requires at least one')

    def test_duplicate_milestone_identity(self):
        self.plan['milestones'][1]['id']=self.plan['milestones'][0]['id']
        self.assert_invalid(self.plan,'duplicate milestone')

    def test_cycle_and_self_dependency(self):
        self.plan['milestones'][0]['depends_on']=['rename-and-remove']
        self.assert_invalid(self.plan,'cycle')
        self.plan['milestones'][0]['depends_on']=['add-and-list']
        self.assert_invalid(self.plan,'self dependency')

    def test_missing_dependency(self):
        self.plan['milestones'][1]['depends_on']=['not-in-plan']
        self.assert_invalid(self.plan,'missing milestone dependency')

    def test_empty_exit_criteria(self):
        self.plan['milestones'][0]['exit_criteria']=[]
        self.assert_invalid(self.plan,'exit_criteria')

    def test_mixed_reference_kinds(self):
        self.plan['milestones'][0]['work'][0]['rfc']='RFC-DEMO-0001'
        self.assert_invalid(self.plan,'exactly one')

    def test_empty_and_null_criterion_selectors(self):
        for selection in ([],None):
            changed=copy.deepcopy(self.plan)
            changed['milestones'][0]['work'][0]['criteria']=selection
            self.assert_invalid(changed,'criteria')

    def test_whole_issue_overlap(self):
        self.plan['milestones'][1]['work'].append({'issue':'DEMO-0001'})
        self.assert_invalid(self.plan,'overlapping work')

    def test_whole_partial_overlap(self):
        self.plan['milestones'][1]['work'].append({'issue':'DEMO-0001','criteria':['AC01']})
        self.assert_invalid(self.plan,'overlapping work')

    def test_disjoint_subsets_and_pending_remainder(self):
        partial=load_json(ROOT/'fixtures/partial/milestone-plan.json')
        self.assertEqual(validate_plan(partial),[])
        partial['unplanned_work'][0]['criteria'].append('AC01')
        self.assert_invalid(partial,'overlapping work')

    def test_partial_requires_remainder(self):
        self.plan['coverage']='partial'
        self.assert_invalid(self.plan,'needs unplanned_work')

    def test_complete_cannot_hide_unplanned(self):
        self.plan['unplanned_work']=[{'issue':'DEMO-0100'}]
        self.assert_invalid(self.plan,'cannot have unplanned_work')

    def test_unaccounted_explicit_issue(self):
        self.plan['scope']['issues'].append('DEMO-0100')
        self.assert_invalid(self.plan,'unaccounted explicit issue')

    def test_catalog_reference_and_scope(self):
        catalog={'rfcs':['RFC-DEMO-0001'],'issues':{f'DEMO-{i:04d}':{'rfcs':['RFC-DEMO-0001']} for i in range(1,7)}}
        self.assertEqual(validate_plan(self.plan,catalog),[])
        del catalog['issues']['DEMO-0002']
        self.assertTrue(any('unresolved' in e for e in validate_plan(self.plan,catalog)))

    def test_typed_remap_not_prose_or_milestone(self):
        original=copy.deepcopy(self.plan)
        original['milestones'][0]['boundary']+=' Historical label DEMO-0001 stays provenance.'
        mapping={'RFC-DEMO-0001':'RFC-DEMO-0100', **{f'DEMO-{i:04d}':f'DEMO-{i+100:04d}' for i in range(1,7)}}
        remapped=remap_plan(original,mapping)
        self.assertEqual([m['id'] for m in remapped['milestones']],[m['id'] for m in original['milestones']])
        self.assertEqual(remapped['milestones'][0]['boundary'],original['milestones'][0]['boundary'])
        self.assertEqual(remapped['milestones'][0]['work'][0],{'issue':'DEMO-0101'})
        self.assertEqual(original['scope']['rfcs'],['RFC-DEMO-0001'])

    def test_criterion_remap_explicit_only(self):
        plan=load_json(ROOT/'fixtures/partial/milestone-plan.json')
        remapped=remap_plan(plan,{'DEMO-0100':'DEMO-0200'},{('issue','DEMO-0100','AC01'):'renamed-criterion'})
        self.assertEqual(remapped['milestones'][0]['work'][0]['criteria'],['renamed-criterion','AC02'])
        self.assertEqual(remapped['unplanned_work'][0]['criteria'],['AC03','AC04'])

    def test_relative_criterion_remap_stays_with_owner(self):
        changed=copy.deepcopy(self.plan)
        changed['milestones'][0]['work'][0]['criteria']=['AC01']
        changed['milestones'][0]['work'][1]['criteria']=['AC01']
        remapped=remap_plan(changed,{}, {('issue','DEMO-0001','AC01'):'new-label'})
        self.assertEqual(remapped['milestones'][0]['work'][0]['criteria'],['new-label'])
        self.assertEqual(remapped['milestones'][0]['work'][1]['criteria'],['AC01'])

    def test_remap_collision_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlapping|duplicate'):
            remap_plan(self.plan,{'DEMO-0002':'DEMO-0001'})

    def test_generated_view_deterministic(self):
        plan=load_json(ROOT/'milestone-plan.json')
        self.assertEqual(render(plan),(ROOT/'MILESTONES.md').read_text())
        self.assertEqual(render(plan),render(normalize(plan)))

    def test_malformed_types_report_not_throw(self):
        for value in (None, [], True, {'schema':3}, {'id':{},'schema':[], 'scope':[], 'milestones':{}}):
            with self.subTest(value=value):self.assertTrue(validate_plan(value))


class PacketTests(unittest.TestCase):
    def run_cli(self,*args,script='validate_pack.py'):
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable,'-B',str(ROOT/'tools'/script),*map(str,args)],capture_output=True,text=True,env=env,timeout=15)

    def test_packet_integrity(self):
        result=check_packet(ROOT)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual((result['rfcs'],result['cards'],result['milestones'],result['criteria']),(1,7,2,12))

    def test_human_default(self):
        run=self.run_cli()
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertTrue(run.stdout.startswith('Packet checks passed.'))
        self.assertNotIn('"schema"',run.stdout)
        self.assertEqual(run.stderr,'')

    def test_explicit_json(self):
        run=self.run_cli('--json')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertTrue(json.loads(run.stdout)['ok'])
        self.assertEqual(run.stderr,'')

    def test_bad_plan_machine_and_human(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{broken')
            human=self.run_cli('--plan',p)
            machine=self.run_cli('--plan',p,'--json')
            self.assertNotEqual(human.returncode,0)
            self.assertEqual(human.stdout,'')
            self.assertIn('Validation failed',human.stderr)
            self.assertNotEqual(machine.returncode,0)
            self.assertFalse(json.loads(machine.stdout)['ok'])

    def test_renderer_public_stdout(self):
        run=self.run_cli(ROOT/'milestone-plan.json',script='render_milestones.py')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(run.stdout,(ROOT/'MILESTONES.md').read_text())

    def test_template_without_consumer_or_validation_stack(self):
        run=self.run_cli('--plan',ROOT/'authoring/milestone-plan.template.json')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn('Plan structure passed.',run.stdout)

    def test_changed_view_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'packet';shutil.copytree(ROOT,root)
            (root/'MILESTONES.md').write_text('Incorrect grouping\n')
            result=check_packet(root,check_manifest=False)
            self.assertFalse(result['ok'])
            self.assertTrue(any('MILESTONES.md' in e for e in result['errors']))

    def test_card_coverage_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'packet';shutil.copytree(ROOT,root)
            row=load_json(root/'packet-index.json')['issues'][0]
            p=root/row['path'];p.write_text(p.read_text().replace('"RFC-ASK-0011-AC01", ',''))
            result=check_packet(root,check_manifest=False)
            self.assertFalse(result['ok'])
            self.assertTrue(any('coverage mismatch' in e for e in result['errors']))

    def test_path_escape_refused(self):
        with self.assertRaisesRegex(ValueError,'escaped'):safe_member(ROOT,'../unrelated')

    def test_fixture_inputs_are_not_qualification_results(self):
        data=load_json(ROOT/'fixtures/scenarios.json')
        self.assertIs(data['executed'],False)
        self.assertEqual(len(data['cases']),26)
        raw=[frontmatter(p) for p in (ROOT/'fixtures/raw-pack/issues').glob('*.md')]
        self.assertEqual(sum(c['status']=='Ready' for c in raw),1)

    def test_check_does_not_mutate_packet(self):
        def snapshot():return {p.relative_to(ROOT).as_posix():p.read_bytes() for p in ROOT.rglob('*') if p.is_file()}
        before=snapshot()
        self.assertTrue(check_packet(ROOT)['ok'])
        self.assertEqual(snapshot(),before)

if __name__=='__main__':unittest.main()
