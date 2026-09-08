"""Synthetic fixtures only. No model tasks, credentials, or external network."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import usage_capture as u
import usage_quota as q

STAMP = '2026-09-07T12:00:00Z'

def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows), encoding='utf-8')
    return path


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.project = self.root/'repo'; self.project.mkdir()
        self.other = self.root/'other'; self.other.mkdir()
        self.ch, self.cx, self.out = self.root/'claude', self.root/'codex', self.root/'out'; self.out.mkdir()
        self.projects = u.Projects([f'Example={self.project}'])

    def audit(self):
        a = u.Collector(self.projects, u.dt('2026-09-07T00:00:00Z'), u.dt('2026-09-08T00:00:00Z'),
                        self.out, 1024**2, 1024**2)
        a.scan(self.ch, self.cx)
        self.events = [json.loads(x) for x in (self.out/'events.jsonl').read_text().splitlines()]
        return a

    def ce(self, typ='assistant', **kw):
        e = {'type': typ, 'sessionId': 'parent', 'cwd': str(self.project), 'timestamp': STAMP,
             'message': {'id': 'm1', 'model': 'claude-opus-5', 'content': [{'type': 'text', 'text': 'PRIVATE SOURCE'}],
                         'usage': {'input_tokens': 30, 'output_tokens': 5, 'cache_read_input_tokens': 400}}}
        e.update(kw); return e

    def xe(self, typ, payload): return {'type': typ, 'timestamp': STAMP, 'payload': payload}

    def test_project_boundaries_and_worktree_alias(self):
        self.assertEqual(self.projects.match(str(self.project/'sub')), 'Example')
        self.assertIsNone(self.projects.match(str(self.project)+'-other'))
        p = u.Projects([f'Example={self.project}'], ['Example=/old/deleted-worktree'])
        self.assertEqual(p.match('/old/deleted-worktree/src'), 'Example')
        self.assertTrue(u.within(u.norm(r'C:\code\test\src'), u.norm(r'C:\code\test')))
        self.assertFalse(u.within(u.norm(r'C:\code\testing'), u.norm(r'C:\code\test')))

    def test_registered_worktree(self):
        with patch.object(u, 'git', return_value='worktree /registered/tree\nHEAD abc\n'):
            p = u.Projects([f'Example={self.project}'])
        self.assertEqual(p.match('/registered/tree/subdir'), 'Example')

    def test_primary_child_exclusion_and_synthetic(self):
        write(self.ch/'projects/r/parent.jsonl', [self.ce()])
        child = self.ce(agentId='child', message={'id': 'm2', 'model': '<synthetic>',
                  'content': [{'type': 'text', 'text': 'You hit your usage limit'}], 'usage': {'input_tokens': 0}},
                  isApiErrorMessage=True)
        path = write(self.ch/'projects/r/parent/subagents/agent-child.jsonl', [child])
        path.with_suffix('.meta.json').write_text(json.dumps({'agentType': 'rfc-scout', 'toolUseId': 'call1'}))
        write(self.ch/'projects/other/a.jsonl', [self.ce(cwd=str(self.other))])
        a = self.audit()
        self.assertEqual(len(a.sessions), 2)
        s = next(s for s in a.sessions.values() if s['kind']=='subagent')
        self.assertEqual(s['launch_tool_use_id'], u.ident('call1'))
        errors = [e for e in self.events if e.get('synthetic_or_api_error')]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_class_text_candidate'], 'quota_or_rate_limit')
        raw=(self.out/'events.jsonl').read_text()
        self.assertNotIn('PRIVATE SOURCE', raw); self.assertNotIn(str(self.project), raw)

    def test_streamed_responses_remain_reconcilable_not_summed(self):
        a = self.ce(); b = self.ce(); b['message']['usage']['output_tokens'] = 9
        write(self.ch/'projects/r/p.jsonl', [a,a,b])
        audit = self.audit()
        rows=[e for e in self.events if e['kind']=='assistant_record']
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['response_id'], rows[1]['response_id'])
        self.assertGreater(audit.stats['duplicate_normalized_events'], 0)
        self.assertNotIn('billed_tokens', rows[0])

    def test_tool_limit_join_does_not_count_bash_grep(self):
        calls = self.ce(message={'id':'m1','model':'claude-opus-5','content':[
          {'type':'tool_use','id':'agentcall','name':'Agent','input':{'subagent_type':'rfc-scout','prompt':'private'}},
          {'type':'tool_use','id':'bashcall','name':'Bash','input':{'command':'grep private'}}]})
        results = self.ce('user', message={'content':[
          {'type':'tool_result','tool_use_id':'agentcall','content':'Maximum turns reached. Partial result.\nagentId: child'},
          {'type':'tool_result','tool_use_id':'bashcall','content':'Maximum turns reached. Partial result.'}]})
        resume = self.ce(message={'id':'m2','model':'claude-opus-5','content':[
          {'type':'tool_use','id':'resume','name':'SendMessage','input':{'to':'child','message':'report only'}}]})
        write(self.ch/'projects/r/p.jsonl', [calls, results, resume]); self.audit()
        stop=[e for e in self.events if e.get('turn_limit_text_candidate')]
        self.assertEqual(len(stop), 1)
        self.assertEqual(stop[0]['tool'], 'Agent')
        control=next(e for e in self.events if e.get('tool')=='SendMessage')
        self.assertEqual(control['target'],stop[0]['returned_agent_id'])

    def test_codex_child_ownership_cumulative_and_last_separate(self):
        rows=[self.xe('session_meta', {'id':'child','cwd':str(self.project),
                  'source': {'subagent': {'thread_spawn': {'parent_thread_id':'parent','agent_role':'rfc-worker'}}}}),
              self.xe('turn_context', {'turn_id':'t0','model':'gpt-5.6-sol','effort':'high'}),
              self.xe('event_msg', {'type':'token_count','info': {'total_token_usage':{'input_tokens':100}}}),
              self.xe('event_msg', {'type':'task_started','thread_id':'child','turn_id':'t1'}),
              self.xe('turn_context', {'turn_id':'t1','model':'gpt-6-astra','effort':'low'}),
              self.xe('event_msg', {'type':'token_count','turn_id':'t1','info': {
                 'total_token_usage': {'input_tokens':150,'cached_input_tokens':100,'output_tokens':50,'reasoning_output_tokens':40},
                 'last_token_usage': {'input_tokens':50,'output_tokens':10}},
                 'rate_limits': {'primary': {'used_percent': 20}}})]
        write(self.cx/'sessions/r.jsonl',rows)
        a=self.audit(); tok=[e for e in self.events if e['kind']=='token_observation']
        self.assertEqual([e['ownership'] for e in tok], ['uncertain_fork_or_child','explicit'])
        self.assertEqual(tok[1]['cumulative']['output_tokens'],50)
        self.assertEqual(tok[1]['last']['output_tokens'],10)
        self.assertEqual(a.stats['coverage_warnings'],0)

    def test_codex_string_child_source_not_primary(self):
        write(self.cx/'sessions/r.jsonl',[self.xe('session_meta', {'id':'child','cwd':str(self.project),'source': {'subagent':'review'}}),
             self.xe('turn_context', {'turn_id':'t','model':'gpt-6-astra','effort':'low'})])
        a=self.audit(); self.assertEqual(next(iter(a.sessions.values()))['kind'],'subagent')

    def test_malformed_and_missing_time_are_coverage_warnings(self):
        path=write(self.ch/'projects/r/p.jsonl',[self.ce(),self.ce(timestamp='not a timestamp')])
        with path.open('a') as f:f.write('not json\n')
        a=self.audit(); self.assertEqual(a.stats['coverage_warnings'],2)

    def test_claude_structured_rates_no_argument_collision(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce(rate_limits={'five_hour':{'used_percentage':40,'resets_at':1788811200}})])
        a=self.audit(); self.assertEqual(a.stats['coverage_warnings'],0)
        self.assertEqual(len([e for e in self.events if e['kind']=='quota_observation']),1)

    def test_date_window_excludes_old_activity(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce(timestamp='2026-09-06T23:00:00Z'),self.ce()])
        self.audit(); self.assertEqual(len(self.events),1)

    def test_config_secret_allowlist(self):
        self.ch.mkdir(parents=True)
        (self.ch/'settings.json').write_text(json.dumps({'model':'claude-opus-5','env':{'TOKEN':'DO_NOT_EXPORT'},
            'hooks':{'Stop':[{'command':'DO_NOT_EXPORT'}]},'statusLine':{'command':'DO_NOT_EXPORT'}}))
        (self.ch/'auth.json').write_text('DO_NOT_EXPORT')
        out=u.inventory(self.projects,self.ch,self.cx)
        self.assertNotIn('DO_NOT_EXPORT',json.dumps(out)); self.assertEqual(out['config_allowlist'][0]['settings']['model'],'claude-opus-5')

    def test_size_limit_is_not_zero_usage(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce(message={'content':'x'*(1024**2+1)})])
        a=self.audit(); self.assertGreater(a.stats['coverage_warnings'],0)

    def test_cli_archive_and_no_overwrite(self):
        write(self.ch/'projects/r/p.jsonl',[self.ce()])
        output=self.root/'result.zip'
        command=[sys.executable,str(Path(u.__file__).with_name('usage.py')), '--project',f'Example={self.project}', '--since','2026-09-07',
                  '--until','2026-09-08','--claude-home',str(self.ch),'--codex-home',str(self.cx),'--out',str(output)]
        done=subprocess.run(command,capture_output=True,text=True); self.assertEqual(done.returncode,0,done.stderr)
        with zipfile.ZipFile(output) as z:
            manifest=json.loads(z.read('manifest.json'))
            self.assertIn('SUMMARY.md',manifest['files'])
            self.assertFalse(manifest['billing_or_quota_estimates'])
            for name in z.namelist(): self.assertNotIn(b'PRIVATE SOURCE',z.read(name))
        again=subprocess.run(command,capture_output=True,text=True); self.assertNotEqual(again.returncode,0)


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


if __name__=='__main__':unittest.main()
