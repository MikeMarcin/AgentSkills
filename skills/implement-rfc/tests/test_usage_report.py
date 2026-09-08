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
            self.assertEqual(summary['outcomes']['accepted_task_count'],0)
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
