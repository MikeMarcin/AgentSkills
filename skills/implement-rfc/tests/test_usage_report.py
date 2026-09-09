"""Archive integrity, derived outcomes and offline report boundary."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import usage_report as r
from usage_outcomes import Outcomes,validate_experiment


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='rfc-report-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def capture(self,name='capture.zip',schema='rfc-usage-evidence.v2',extra=None):
        event={'event_id':'1','provider':'claude','session':'s','project':'p','kind':'assistant_record','response_id':'response',
               'timestamp':'2026-09-07T12:00:00Z','usage':{'input_tokens':10,'output_tokens':5},'stop_reason':'end_turn'}
        files={'events.jsonl':(json.dumps(event)+'\n').encode(),'sessions.json':b'[]','counter_baselines.json':b'[]'}
        if extra:files.update(extra)
        manifest={'schema':schema,'coverage':'partial','files':{k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in files.items()}}
        path=self.root/name
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr('manifest.json',json.dumps(manifest))
            for k,v in files.items():archive.writestr(k,v)
        return path
    def test_public_v1_v2_reports_leave_captures_immutable(self):
        for i,schema in enumerate(('rfc-usage-evidence.v1','rfc-usage-evidence.v2')):
            path=self.capture(str(i)+'.zip',schema);before=path.read_bytes();out=self.root/str(i)
            done=subprocess.run([sys.executable,'-B',r.__file__,str(path),'--out',str(out)],capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)
            summary=json.loads((out/'summary.json').read_text())
            self.assertIsNone(summary['outcomes']['accepted_task_count'])
            self.assertEqual(summary['outcomes']['outcome_input'],'missing')
            self.assertIsNone(summary['outcomes']['observed_tokens_per_accepted_task'])
            self.assertEqual(path.read_bytes(),before)
            self.assertIn('unknown',(out/'REPORT.md').read_text())
    def test_traversal_duplicates_hash_and_bomb_refuse(self):
        path=self.capture(extra={'../escape':b'bad'})
        with self.assertRaises(ValueError):r.Capture(path)
        path=self.capture('duplicate.zip')
        with zipfile.ZipFile(path,'a') as z:z.writestr('events.jsonl','changed')
        with self.assertRaises(ValueError):r.Capture(path)
        path=self.capture('corrupt.zip')
        with zipfile.ZipFile(path) as z:entries={n:z.read(n) for n in z.namelist()}
        entries['events.jsonl']=b'changed\n'
        with zipfile.ZipFile(path,'w') as z:
            for k,v in entries.items():z.writestr(k,v)
        with self.assertRaises(ValueError):r.Capture(path)
        path=self.root/'bomb.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('huge',b'0'*1000000)
        with self.assertRaises(ValueError):r.Capture(path)
    def outcome_document(self):
        return {'schema':'implement-rfc.outcomes.v1','assignments':[{'session':'s','task_id':'task','attempt_id':'attempt','evidence_ref':'native','since':'2026-09-07T00:00:00Z','until':'2026-09-08T00:00:00Z'}],
                'events':[{'event_id':str(i),'task_id':'task','state':state,'timestamp':f'2026-09-07T12:00:0{i}Z','evidence_ref':'existing-card'} for i,state in enumerate(('report_ready','collected','accepted','reopened'))]}
    def test_reopened_is_not_accepted_and_attempts_count(self):
        doc=self.outcome_document();outcome=Outcomes(doc)
        row={'session':'s','timestamp':'2026-09-07T12:00:00Z','classification':'request_reconciled','tokens':{'input_tokens':10,'output_tokens':5}}
        outcome.observe(row);outcome.observe({**row,'task_id':'task','attempt_id':'recovery'})
        self.assertEqual(outcome.summary()['all_assigned_attempt_tokens'],30)
        self.assertEqual(outcome.summary()['accepted_task_count'],0)
        self.assertTrue(outcome.summary()['tasks']['task']['collected'])
        self.assertIsNone(outcome.summary()['observed_tokens_per_accepted_task'])
    def test_ambiguous_assignment_stays_unassigned(self):
        doc=self.outcome_document();doc['assignments'].append({**doc['assignments'][0],'task_id':'other'})
        outcome=Outcomes(doc)
        self.assertIsNone(outcome.assign({'session':'s','timestamp':'2026-09-07T12:00:00Z','classification':'request_reconciled'}))
    def test_comparison_does_not_sum_copied_captures(self):
        a=self.capture();b=self.capture('copy.zip')
        summary=r.report([a,b],self.root/'report',outcomes=self.outcome_document(),compare=True)
        self.assertIsNone(summary['outcomes']['all_assigned_attempt_tokens'])
        self.assertEqual([x['outcomes']['all_assigned_attempt_tokens'] for x in summary['captures']],[15,15])
    def test_observational_experiment_cannot_claim_promotion(self):
        experiment={'schema':'implement-rfc.experiment.v1','treatment_id':'routing-pilot','dimension':'routing','comparison_basis':'observational_real_backlog',
                    'fixed':dict.fromkeys(('source','review','context','routes','topology'),'recorded'), 'ceiling':{'task_count':2,'owner_approval_ref':'explicit-owner'},'acceptance_ref':'card','decision':'inconclusive'}
        validate_experiment(experiment)
        experiment['decision']='promote'
        with self.assertRaises(ValueError):validate_experiment(experiment)


    def test_public_conflicting_cumulative_prevents_exact_outcome_ratio(self):
        from test_usage_accounting import event
        owning=event(1,kind='response_usage',owner_session='s',response_id='r',
                     usage={'input_tokens':100,'cached_input_tokens':80,'output_tokens':10,'reasoning_output_tokens':2})
        for cumulative,baseline,anomaly in ((900,True,'alternate_counter_disagreement'),
                                            (100,False,'alternate_coverage_unresolved')):
            name=f'{cumulative}-{baseline}'
            alternate=event(2,response_id='r',last=owning['usage'],
                            cumulative={'input_tokens':cumulative,'output_tokens':90 if cumulative==900 else 10})
            baselines=[event(0,cumulative={'input_tokens':0,'output_tokens':0})] if baseline else []
            path=self.capture(name+'.zip',extra={
                'events.jsonl':(''.join(json.dumps(v)+'\n' for v in (owning,alternate))).encode(),
                'counter_baselines.json':json.dumps(baselines).encode(),
                'sessions.json':json.dumps([{'key':'s','provider':'codex','project':'p','kind':'primary'}]).encode()})
            outcomes=self.outcome_document();outcomes['events']=outcomes['events'][:-1]
            outcome_path=self.root/(name+'-outcomes.json');outcome_path.write_text(json.dumps(outcomes))
            out=self.root/name
            done=subprocess.run([sys.executable,'-B',r.__file__,str(path),'--out',str(out),'--outcomes',str(outcome_path)],capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)
            summary=json.loads((out/'summary.json').read_text())
            self.assertEqual(summary['outcomes']['accepted_task_count'],1)
            self.assertEqual(summary['outcomes']['all_assigned_attempt_tokens'],110)
            self.assertIsNone(summary['outcomes']['observed_tokens_per_accepted_task'])
            self.assertEqual(summary['captures'][0]['families'][0]['unknown_rows'],1)
            self.assertEqual(summary['captures'][0]['unknown_groups'][0]['classification'],'alternate_observation')
            self.assertIn(anomaly,(out/'ledger.csv').read_text())

    def test_explicit_outcomes_without_acceptances_are_observed_zero(self):
        path=self.capture()
        summary=r.report([path],self.root/'observed-zero',outcomes={'schema':'implement-rfc.outcomes.v1','assignments':[],'events':[]})
        self.assertEqual(summary['outcomes']['accepted_task_count'],0)
        self.assertEqual(summary['outcomes']['outcome_input'],'observed')
        self.assertIsNone(summary['outcomes']['observed_tokens_per_accepted_task'])
        self.assertIn('Explicitly accepted tasks: 0.',(self.root/'observed-zero/REPORT.md').read_text())
        with self.assertRaises(ValueError):Outcomes({})

    def test_transitive_lineage_unknown_parents_and_cycles(self):
        sessions={key:{'key':key,'provider':'codex','project':'p','kind':'subagent',
                      'session_id':key,'role':'unknown','parent_session':parent}
                  for key,parent in [('root',None),('integrator-1','root'),('worker','integrator-1'),
                                     ('grandchild','worker'),('integrator-2','root'),('orphan','absent'),
                                     ('cycle-a','cycle-b'),('cycle-b','cycle-a'),('unknown',None)]}
        sessions['root']['kind']='primary'
        lineage=r.session_lineage(sessions)
        self.assertEqual(lineage['grandchild'],{'family_root':'root','lineage_depth':3,'lineage_status':'observed'})
        self.assertEqual(lineage['integrator-2']['family_root'],'root')
        for key in ('orphan','cycle-a','cycle-b','unknown'):self.assertIsNone(lineage[key]['family_root'])
        self.assertEqual(lineage['cycle-a']['lineage_status'],'parent_cycle')
        sessions['worker']['project']='different'
        self.assertIsNone(r.session_lineage(sessions)['grandchild']['family_root'])

    def test_legacy_native_parent_fields_resolve_both_providers(self):
        for provider in ('codex','claude'):
            sessions={'root':{'provider':provider,'project':'p','session_id':'root-id','agent_id':None,'kind':'primary'},
                      'integrator':{'provider':provider,'project':'p','session_id':'integrator-id' if provider=='codex' else 'root-id',
                                    'agent_id':None if provider=='codex' else 'integrator-id','kind':'subagent',
                                    'parent_agent_id':'root-id' if provider=='codex' else None},
                      'leaf':{'provider':provider,'project':'p','session_id':'leaf-id' if provider=='codex' else 'root-id',
                              'agent_id':None if provider=='codex' else 'leaf-id','kind':'subagent','parent_agent_id':'integrator-id'}}
            lineage=r.session_lineage(sessions)
            self.assertEqual(lineage['leaf']['family_root'],'root' if provider=='codex' else None)
            # Claude's missing parentAgentId cannot be guessed to mean direct-root.

    def test_alternate_agreement_is_not_an_unknown_attempt(self):
        outcome=Outcomes({'schema':'implement-rfc.outcomes.v1','assignments':[],
            'events':[{'event_id':'accepted','state':'accepted','task_id':'task','timestamp':'2026-09-07T12:00:00Z','evidence_ref':'verdict'}]})
        outcome.observe({'classification':'alternate_observation','anomalies':[]})
        outcome.observe({'task_id':'task','attempt_id':'1','classification':'request_reconciled','tokens':{'input_tokens':10,'output_tokens':1}})
        self.assertEqual(outcome.summary()['observed_tokens_per_accepted_task'],11)
        outcome.observe({'classification':'alternate_observation','anomalies':['alternate_coverage_unresolved']})
        self.assertIsNone(outcome.summary()['observed_tokens_per_accepted_task'])


if __name__=='__main__':unittest.main()


class MissingConsumptionTests(unittest.TestCase):
    def test_acceptance_without_usage_is_unknown_not_zero(self):
        from usage_outcomes import Outcomes
        outcomes=Outcomes({'schema':'implement-rfc.outcomes.v1','assignments':[],
            'events':[{'event_id':'accepted','state':'accepted','task_id':'task',
                       'timestamp':'2026-09-08T00:00:00Z','evidence_ref':'real-verdict'}]})
        self.assertIsNone(outcomes.summary()['observed_tokens_per_accepted_task'])
        outcomes.observe({'task_id':'task','attempt_id':'one','classification':'request_reconciled',
                          'tokens':{'input_tokens':0,'output_tokens':0}})
        self.assertEqual(outcomes.summary()['observed_tokens_per_accepted_task'],0)
