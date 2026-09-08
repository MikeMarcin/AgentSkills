import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import usage_capture as u
import usage_quota as q
STAMP='2026-09-07T12:00:00Z'

class QuotaTests(unittest.TestCase):
    def test_multi_bucket_precedence(self):
        v={'rateLimits':{'primary':{'usedPercent':99}}, 'rateLimitsByLimitId':{
            'codex':{'primary':{'usedPercent':20,'resetsAt':1788811200},'credits':{'balance':'4.2'}},
            'other':{'secondary':{'usedPercent':15}}},'rateLimitResetCredits':{'availableCount':2,'credits':[{'id':'NEVER_EXPORT'}]}}
        data=u.quota_buckets(v)
        self.assertEqual(len(data['buckets']),2); self.assertNotIn('NEVER_EXPORT',json.dumps(data))
        self.assertEqual(data['buckets'][0]['windows'][0]['used_percent'],20)

    def test_sanitizer_rebuilds_schema(self):
        clean=q.sanitize_snapshot({'schema':'rfc-quota.v1','provider':'claude','source':'manual','observed_at':STAMP,
             'password':'NEVER_EXPORT','data':{'buckets':[{'pool':'default','windows':[{'window':'five_hour','used_percent':35,'secret':'NEVER_EXPORT'}]}]}})
        self.assertNotIn('NEVER_EXPORT',json.dumps(clean));self.assertEqual(clean['data']['buckets'][0]['windows'][0]['used_percent'],35)

    def test_absence_is_not_zero(self):
        self.assertEqual(u.quota_buckets({})['buckets'],[])
        self.assertIsNone(q.percent(101));self.assertIsNone(q.percent(-1));self.assertIsNone(q.percent(True))
        self.assertEqual(q.percent(0),0)

    def test_spend_limit_can_exceed_one_hundred(self):
        snap=q.sanitize_snapshot({'schema':'rfc-quota.v1','provider':'claude','source':'claude_statusline','observed_at':STAMP,
             'data':{'buckets':[{'pool':'default','windows':[{'window':'spend_limit','used_percent':125}]}]}})
        self.assertEqual(snap['data']['buckets'][0]['windows'][0]['used_percent'],125)

    def test_reject_arbitrary_files(self):
        with self.assertRaises(ValueError):q.sanitize_snapshot({'api_key':'NEVER_EXPORT'})

    def test_native_protocol_only_three_methods(self):
        class Fake:
            def __init__(self,*a,**k):
                self.stdin=io.BytesIO();self.stdout=io.BytesIO(b'{"id":0,"result":{}}\n{"id":1,"result":{"rateLimits":{"primary":{"usedPercent":8}}}}\n')
            def poll(self):return 0
        process=Fake();sent=[]
        class Sink(io.BytesIO):
            def write(self,v):sent.append(json.loads(v));return super().write(v)
            def close(self):pass
        process.stdin=Sink()
        with patch.object(q.shutil,'which',return_value='/fake/codex'),patch.object(q.subprocess,'Popen',return_value=process):
            result=q.codex_rates('codex',1)
        self.assertEqual([s['method'] for s in sent],['initialize','initialized','account/rateLimits/read'])
        self.assertEqual(result['rateLimits']['primary']['usedPercent'],8)


    def test_interactive_and_malformed_protocol_refuse(self):
        for incoming in (b'{"id":9,"method":"account/chatgptAuthTokens/refresh"}\n', b'not json\n'):
            sent=[]
            class Sink(io.BytesIO):
                def write(self,value):sent.append(json.loads(value));return super().write(value)
                def close(self):pass
            class Fake:
                def __init__(self):self.stdin=Sink();self.stdout=io.BytesIO(incoming)
                def poll(self):return 0
            with patch.object(q.shutil,'which',return_value='/fake/codex'),patch.object(q.subprocess,'Popen',return_value=Fake()):
                with self.assertRaises(RuntimeError):q.codex_rates('codex',1)
            self.assertEqual([x.get('method') for x in sent],['initialize'])

if __name__=='__main__':unittest.main()
