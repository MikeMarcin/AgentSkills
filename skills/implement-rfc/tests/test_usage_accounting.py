"""Hand-computed consumption and price-equivalent fixtures."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from usage_accounting import reconcile,estimate


def event(i,**kw):
    return {'provider':'codex','session':'s','project':'p','kind':'token_observation',
            'timestamp':f'2026-09-07T12:00:{i:02d}Z','event_id':str(i),'ownership':'explicit',**kw}


class AccountingTests(unittest.TestCase):
    def test_baseline_subsets_duplicates_and_aggregate(self):
        baseline=event(0,cumulative={'input_tokens':100,'cached_input_tokens':70,'output_tokens':20,'reasoning_output_tokens':10})
        row=event(1,cumulative={'input_tokens':140,'cached_input_tokens':100,'output_tokens':30,'reasoning_output_tokens':15},last={'input_tokens':40,'cached_input_tokens':30,'output_tokens':10,'reasoning_output_tokens':5})
        rows=list(reconcile([row,row,event(2,cumulative=row['cumulative'])],[baseline]))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['classification'],'aggregate_only')
        self.assertEqual(rows[0]['tokens'],{'input_tokens':40,'cached_input_tokens':30,'uncached_input_tokens':10,'output_tokens':10,'reasoning_output_tokens':5})
    def test_missing_baseline_and_decrease_are_not_billed(self):
        rows=list(reconcile([event(1,cumulative={'input_tokens':900,'output_tokens':100}),event(2,cumulative={'input_tokens':2,'output_tokens':1})]))
        self.assertEqual([r['classification'] for r in rows],['unknown','unknown'])
        self.assertEqual(rows[0]['anomalies'],['pre_window_baseline_missing'])
        self.assertEqual(rows[1]['anomalies'],['counter_decrease_or_reset'])
    def test_child_ownership_and_unknown_baseline(self):
        baseline=event(0,ownership='uncertain_fork_or_child',cumulative={'input_tokens':1,'output_tokens':1})
        rows=list(reconcile([event(1,ownership='uncertain_fork_or_child',cumulative={'input_tokens':5,'output_tokens':2}),event(2,cumulative={'input_tokens':8,'output_tokens':4})],[baseline]))
        self.assertEqual([r['classification'] for r in rows],['ownership_uncertain','unknown'])
    def test_claude_fragments_and_inclusive_aggregate(self):
        a=event(1,provider='claude',kind='assistant_record',response_id='response',usage={'input_tokens':10,'cache_read_input_tokens':20,'cache_creation_input_tokens':5,'cache_creation':{'ephemeral_5m_input_tokens':5},'output_tokens':2})
        b={**a,'timestamp':'2026-09-07T12:00:02Z','event_id':'2','usage':{**a['usage'],'output_tokens':7},'stop_reason':'end_turn'}
        aggregate=event(3,provider='claude',kind='runtime_result',aggregate_usage_do_not_add={'input_tokens':100})
        for schema in ('rfc-usage-evidence.v1','rfc-usage-evidence.v2'):
            rows=list(reconcile([a,b,aggregate],schema=schema))
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['tokens']['input_tokens'],35)
            self.assertEqual(rows[0]['tokens']['output_tokens'],7)
    def test_conflicting_and_incomplete_claude(self):
        a=event(1,provider='claude',kind='assistant_record',response_id='r',usage={'input_tokens':10,'output_tokens':2})
        b={**a,'event_id':'2','usage':{'input_tokens':12,'output_tokens':3}}
        row=list(reconcile([a,b]))[0]
        self.assertEqual(row['classification'],'unknown')
        self.assertIsNone(row['tokens']['output_tokens'])
        self.assertIn('conflicting_request_counters',row['anomalies'])
    def test_no_data_distinct_from_zero(self):
        self.assertEqual(list(reconcile([])),[])
        zero=event(1,provider='claude',kind='assistant_record',response_id='r',usage={'input_tokens':0,'output_tokens':0},stop_reason='end_turn')
        self.assertEqual(list(reconcile([zero]))[0]['tokens']['output_tokens'],0)
    def test_decimal_dates_tiers_and_missing_rates(self):
        row={'provider':'claude','model':'m','service_tier':'default','timestamp':'2026-09-07T12:00:00Z','classification':'request_reconciled',
             'route_evidence':'runtime_response','tokens':{'uncached_input_tokens':10,'cached_input_tokens':20,'cache_creation_input_tokens':5,'output_tokens':7}}
        rate={'provider':'claude','model':'m','service_tier':'default','effective_from':'2026-09-01T00:00:00Z','effective_until':'2026-10-01T00:00:00Z','source':'fixture—not a real price',
              'unit':'USD','tier_multiplier':'1','per_million':{'uncached_input_tokens':'2','cached_input_tokens':'.2','cache_creation_input_tokens':'2.5','output_tokens':'10'}}
        self.assertEqual(estimate(row,[rate])['amount'],'0.0001065')
        self.assertIsNone(estimate({**row,'service_tier':None},[rate])['amount'])
        self.assertIsNone(estimate({**row,'timestamp':'2026-11-01T00:00:00Z'},[rate])['amount'])
        self.assertIsNone(estimate({**row,'route_evidence':'configuration'},[rate])['amount'])
        self.assertIsNone(estimate(row,[])['amount'])
    def test_conflicting_duplicate_id_refuses(self):
        with self.assertRaises(ValueError):list(reconcile([event(1),event(1,project='other')]))


if __name__=='__main__':unittest.main()
