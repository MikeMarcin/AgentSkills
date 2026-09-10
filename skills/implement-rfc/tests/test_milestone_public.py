"""Raw pack → linked consumer → bound multi-card progress → checked boundary."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import init_repo, write_context

SKILL = Path(__file__).resolve().parents[1]
RAW = SKILL.parents[1] / 'docs/rfcs/assets/agent-skills-milestone-handling/fixtures/raw-pack'


class PublicMilestoneTests(unittest.TestCase):
    def test_raw_two_consumers_checked_boundary_and_amendment(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            for token in ('alpha', 'beta'):
                root = base / token
                config = init_repo(root, token=token)
                config['bookkeeping'] = {'deferring_lanes':['00-inbox','10-backlog','50-blocked'],
                    'parked_on':['human-review'],'blocked_by_forbidden_prefixes':[],
                    'link_roots':['docs/issues','docs/rfcs'],'protected_globs':[],'editable_globs':[]}
                write_context(root, config=config)
                link = root / '.agents/skills/implement-rfc'
                link.parent.mkdir(parents=True)
                link.symlink_to(SKILL, target_is_directory=True)
                def write(path, value):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(value) if not isinstance(value, str) else value)
                def cli(script, *args, expected=0):
                    command = [sys.executable, '-B', str(link / 'scripts' / script),
                               '--repo-root', str(root), *args, '--json']
                    run = subprocess.run(command, cwd=base, capture_output=True, text=True)
                    self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
                    return json.loads(run.stdout)
                discovered = cli('milestone_plan.py', 'discover', '--source-root', str(RAW))
                self.assertEqual(discovered['milestone_ids'], ['add-and-list', 'rename-and-remove'])
                self.assertFalse((root / 'docs/rfcs/plans').exists())
                # Normal intake creates actual live documents before typed adoption.
                for original in (RAW / 'issues').glob('*.md'):
                    text = original.read_text().replace('DEMO-', 'LIVE-')
                    lane = '20-ready' if 'status: "Ready"' in text else '10-backlog'
                    write(root / 'docs/issues' / lane / (original.stem.replace('DEMO-', 'LIVE-') + '-demo.md'), text)
                write(root / 'docs/rfcs/RFC-LIVE-0001-demo.md', (RAW / 'RFC-DEMO-0001.md').read_text().replace('DEMO-', 'LIVE-'))
                write(root / 'docs/issues/NEXT_ID', 'LIVE-0007\n')
                source = base / ('raw-' + token)
                source.mkdir()
                write(source / 'milestone-plan.json', (RAW / 'milestone-plan.json').read_text())
                write(source / 'map.json', {**{f'DEMO-{i:04}': f'LIVE-{i:04}' for i in range(1,7)}, 'RFC-DEMO-0001':'RFC-LIVE-0001'})
                cli('milestone_plan.py', 'adopt', '--source-root', str(source), '--id-map', 'map.json')
                assigned = cli('coordinator_handoff.py', 'assign', '--target', 'RFC-LIVE-0001',
                               '--run-id', token, '--dispatch-id', 'one', '--producer-id', 'native-one', '--mandate-revision', '1')
                self.assertEqual(assigned['milestone'], 'add-and-list')
                binding = assigned['binding']
                self.assertEqual([item['source'] for item in binding['obligations']], ['LIVE-0001','LIVE-0002','LIVE-0003'])
                write(root / 'assignment.json', assigned)
                write(root / 'evidence.md', 'Fixture observer evidence; no native qualification claim.\n')
                reply = {key: assigned[key] for key in ('run_id','dispatch_id','producer_id','mandate_revision','milestone')}
                reply.update(schema='implement-rfc.milestone-return.v2', disposition='continue-milestone', summary='first card',
                    candidate_revision='a'*40, handoff_ref='evidence.md', ownership='quiescent', next_objective='finish add/list',
                    required_pending=['remaining cards and public path'], evidence_refs=['evidence.md'], binding=binding,
                    acceptance_records=[{'id':binding['obligations'][0]['id'],'outcome':'pass','evidence_refs':['evidence.md']}],
                    continuation={'intent':'continue','next_milestone':'add-and-list','reason':'current-milestone','detail':'Two cards and composed evidence remain.'})
                def check(expected=0, **extra):
                    write(root / 'return.json', reply)
                    return cli('coordinator_handoff.py','check','--assignment','assignment.json','--return-file','return.json',
                               '--execution','quiescent', expected=expected, **extra)
                self.assertEqual(check()['action'], 'resume-integrator')
                reply['disposition']='milestone-complete'
                self.assertEqual(check(expected=2)['action'], 'clarify')
                reply['disposition']='continue-milestone'
                # Public board lane move does not change requirement fingerprints.
                cli('issue_board.py','move','LIVE-0001','--to','60-done')
                self.assertEqual(check()['action'], 'resume-integrator')
                reply['disposition']='milestone-complete'; reply['required_pending']=[]
                reply['acceptance_records']=[{'id':item['id'],'outcome':'pass','evidence_refs':['evidence.md']} for item in binding['obligations']]
                self.assertEqual(check(expected=2)['action'],'clarify')
                reply['acceptance_records'] += [{'id':item['id'],'outcome':'pass','evidence_refs':['evidence.md']} for item in binding['exit_criteria']]
                reply['continuation'].update(intent='fresh',next_milestone='rename-and-remove',reason='integrated-boundary',detail='Public add/list boundary accepted; mutation design is next.')
                self.assertEqual(check()['action'], 'fresh-integrator')
                intact_assignment=copy.deepcopy(assigned)
                intact_reply=copy.deepcopy(reply)
                assigned['binding']['obligations']=assigned['binding']['obligations'][:1]
                assigned['binding']['exit_criteria']=assigned['binding']['exit_criteria'][:1]
                write(root/'assignment.json',assigned)
                reply['binding']=assigned['binding']
                reply['acceptance_records']=[{'id':item['id'],'outcome':'pass','evidence_refs':['evidence.md']}
                    for field in ('obligations','exit_criteria') for item in assigned['binding'][field]]
                self.assertEqual(check(expected=2)['action'],'reconcile')
                assigned=intact_assignment;write(root/'assignment.json',assigned);reply=intact_reply
                for malformed in (dict(assigned,binding=[]),dict(assigned,unexpected=True)):
                    write(root/'assignment.json',malformed)
                    self.assertEqual(check(expected=2)['action'],'reconcile')
                write(root/'assignment.json',assigned)
                reply.update(disposition='pack-complete',next_objective=None)
                reply['continuation'].update(intent='stop',next_milestone=None,reason='target-complete')
                self.assertEqual(check(expected=2)['action'],'clarify')
                assigned['target_milestones']=['add-and-list'];write(root/'assignment.json',assigned)
                self.assertEqual(check(expected=2)['action'],'reconcile')
                assigned['target_milestones']=['add-and-list','rename-and-remove'];write(root/'assignment.json',assigned)
                reply['disposition']='milestone-complete';reply['next_objective']='second'
                reply['continuation'].update(intent='fresh',next_milestone='rename-and-remove',reason='integrated-boundary')
                next_assignment=cli('coordinator_handoff.py','assign','--target','LIVE-0001','--accepted-milestone','add-and-list',
                    '--run-id',token,'--dispatch-id','two','--producer-id','native-two','--mandate-revision','1')
                self.assertEqual(next_assignment['milestone'],'rename-and-remove')
                planpath=root/binding['plan_path']; plan=json.loads(planpath.read_text())
                plan['milestones'][1]['outcome'] += ' Refined future wording.'
                write(planpath,plan)
                self.assertEqual(check()['action'],'fresh-integrator')
                plan['milestones'][0]['exit_criteria'].append('New current requirement')
                write(planpath,plan)
                self.assertEqual(check(expected=2)['action'],'reconcile')


if __name__ == '__main__':
    unittest.main()
