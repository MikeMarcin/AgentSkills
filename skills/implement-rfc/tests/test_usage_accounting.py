"""Hand-computed consumption and price-equivalent fixtures."""
from pathlib import Path
import sys
import json
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


    def native(self,i=1,**kw):
        return event(i,kind='response_usage',owner_session='s',response_id='r',turn_id='t',
                     usage={'input_tokens':100,'cached_input_tokens':80,'output_tokens':10,'reasoning_output_tokens':2},**kw)

    def test_supplied_owning_response_totals(self):
        fixture=Path(__file__).resolve().parents[3]/'docs/rfcs/assets/agent-skills-interactive-coordinator-2026-09-08/fixtures/owning-response.synthetic.json'
        value=json.loads(fixture.read_text());events=[]
        for i,record in enumerate(value['records'],1):
            payload=record['payload']
            events.append(event(i,kind='response_usage',session=record['file_thread'],
                owner_session=payload['thread_id'],response_id=payload['response_id'],turn_id=payload['turn_id'],usage=payload['usage']))
        rows=list(reconcile(reversed(events)))
        self.assertEqual(len(rows),value['expected']['unique_owning_responses'])
        for key in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens','reasoning_output_tokens'):
            self.assertEqual(sum(r['tokens'][key] for r in rows),value['expected'][key])
        self.assertEqual(sum(r['tokens']['input_tokens']+r['tokens']['output_tokens'] for r in rows),825)

    def test_owner_and_response_identity_deduplicate_copies_and_resumes(self):
        a=self.native()
        rows=list(reconcile([a,{**a,'event_id':'copy','timestamp':'2026-09-07T12:00:02Z','turn_id':None},
            {**a,'event_id':'retained','session':'child','ownership':'other_thread'},
            {**a,'event_id':'different-owner','session':'child','owner_session':'child'},
            {**a,'event_id':'resumed','response_id':'r2','turn_id':'t2'}]))
        requests=[r for r in rows if r['classification']=='request_reconciled']
        self.assertEqual(len(requests),3)
        self.assertEqual(sum(r['tokens']['input_tokens'] for r in requests),300)
        self.assertEqual([r['classification'] for r in rows].count('alternate_observation'),1)

    def test_native_wins_over_legacy_but_disagreement_remains_visible(self):
        a=self.native();baseline=event(0,cumulative={'input_tokens':0,'output_tokens':0})
        for count,anomalies in ((100,[]),(90,['alternate_counter_disagreement'])):
            alternate=event(2,cumulative={'input_tokens':count,'output_tokens':10})
            rows=list(reconcile([alternate,a,{**alternate,'event_id':'repeated-total','timestamp':'2026-09-07T12:00:03Z'}],[baseline]))
            self.assertEqual([r['classification'] for r in rows],['alternate_observation','request_reconciled'])
            self.assertEqual(rows[0]['anomalies'],anomalies)
            self.assertIsNone(rows[0]['tokens'])
            self.assertEqual(rows[1]['tokens']['input_tokens'],100)

    def test_alternate_request_and_unbounded_thread_total_are_not_extra_usage(self):
        a=self.native()
        last=event(2,response_id='r',last=a['usage'])
        total=event(3,cumulative={'input_tokens':900,'output_tokens':90})
        rows=list(reconcile([a,last,total]))
        self.assertEqual(rows[0]['anomalies'],[])
        self.assertEqual(rows[1]['anomalies'],['alternate_coverage_unresolved'])
        self.assertEqual(sum(r['tokens']['input_tokens'] for r in rows if r['tokens']),100)

    def test_each_supplied_alternate_surface_must_reconcile(self):
        owning=self.native();baseline=event(0,cumulative={'input_tokens':0,'output_tokens':0})
        cases=[(owning['usage'],{'input_tokens':900,'output_tokens':90},[baseline],'alternate_counter_disagreement'),
               ({'input_tokens':900,'output_tokens':90},{'input_tokens':100,'output_tokens':10},[baseline],'alternate_counter_disagreement'),
               (owning['usage'],{'input_tokens':100,'output_tokens':10},[],'alternate_coverage_unresolved'),
               (owning['usage'],{'input_tokens':100,'output_tokens':10},[baseline],None)]
        for last,cumulative,baselines,anomaly in cases:
            with self.subTest(last=last,cumulative=cumulative,baseline=bool(baselines)):
                alternate=event(2,response_id='r',last=last,cumulative=cumulative)
                rows=list(reconcile([owning,alternate],baselines))
                self.assertEqual(rows[0]['anomalies'],[anomaly] if anomaly else [])
                self.assertIsNone(rows[0]['tokens'])
                self.assertEqual(rows[1]['tokens']['input_tokens'],100)

    def test_conflicting_native_and_missing_owner_or_response_are_unknown(self):
        a=self.native()
        rows=list(reconcile([a,{**a,'event_id':'conflict','usage':{**a['usage'],'input_tokens':101}},
            {**a,'event_id':'missing-owner','owner_session':None,'ownership':'owner_missing'},
            {**a,'event_id':'missing-response','response_id':None}]))
        self.assertEqual(sorted(r['classification'] for r in rows),['ownership_uncertain','unknown','unknown'])
        self.assertTrue(all(r['tokens'] is None for r in rows))
        self.assertIn('conflicting_request_counters',[a for r in rows for a in r['anomalies']])

    def test_native_nested_subsets_and_total_consistency(self):
        a=self.native()
        usage={'input_tokens':100,'output_tokens':10,'input_tokens_details':{'cached_tokens':80},
               'output_tokens_details':{'reasoning_tokens':2},'total_tokens':110}
        good=list(reconcile([{**a,'usage':usage}]))[0]
        self.assertEqual(good['tokens']['uncached_input_tokens'],20)
        for bad in ({**usage,'total_tokens':999},{**usage,'cached_input_tokens':79},
                    {**usage,'output_tokens_details':{'reasoning_tokens':11}}):
            self.assertEqual(list(reconcile([{**a,'usage':bad}]))[0]['classification'],'unknown')

    def test_native_does_not_suppress_an_unrelated_legacy_session(self):
        rows=list(reconcile([self.native(),event(2,session='legacy',cumulative={'input_tokens':5,'output_tokens':1})],
                            [event(0,session='legacy',cumulative={'input_tokens':0,'output_tokens':0})]))
        self.assertEqual(sorted(r['classification'] for r in rows),['aggregate_only','request_reconciled'])


if __name__=='__main__':unittest.main()
