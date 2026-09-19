"""Direct claim/change/public-check/evidence/commit in two linked consumers."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_fixtures import init_repo, git, write_context

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import execution_strategy as strategies
import milestone_checkpoint as checkpoint


class PrimaryCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def cli(self, root, script, *args, code=0):
        done = subprocess.run([sys.executable, '-B', str(root / '.agents/skills/implement-rfc/scripts' / script),
                               '--repo-root', str(root), *args], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(done.returncode, code, done.stdout + done.stderr)
        return json.loads(done.stdout)

    def consumer(self, name):
        root = self.base / name
        config = init_repo(root, token=name)
        config['bookkeeping'] = dict(deferring_lanes=['10-backlog','00-inbox','50-blocked'],
            parked_on=['human-review'], blocked_by_forbidden_prefixes=[], link_roots=['docs'],
            protected_globs=[], editable_globs=[])
        write_context(root, config=config)
        link = root / '.agents/skills/implement-rfc'
        link.parent.mkdir(parents=True)
        link.symlink_to(SKILL, target_is_directory=True)
        (root / '.gitignore').write_text('.agents/\nruntime/\n')
        (root / 'runtime').mkdir()
        for number in (1, 2):
            path = root / f'docs/issues/20-ready/FX-000{number}-work.md'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('---\n'+ '\n'.join(f'{k}: {json.dumps(v)}' for k, v in dict(
                schema='implement-rfc.card.v1', id=f'FX-000{number}', title='Product increment', status='Ready',
                rfcs=[], depends_on=[]).items()) + '\n---\n\n## Acceptance\n\nProduct adds correctly.\n')
        (root / 'docs/issues/NEXT_ID').write_text('FX-0003\n')
        (root / 'product.py').write_text('def add(a, b):\n    return a - b\n')
        (root / 'check_product.py').write_text('from product import add\nassert add(2, 3) == 5\n')
        (root / 'unrelated.txt').write_text('original\n')
        git(root, 'add', '.mask', '.gitignore', 'docs', 'product.py', 'check_product.py', 'unrelated.txt')
        git(root, 'commit', '-m', 'Intake')
        raw = self.base / (name + '-packet'); raw.mkdir()
        plan = dict(schema='implement-rfc.milestone-plan.v1', id='direct-demo', scope={'issues':['FX-0001','FX-0002']},
                    milestones=[dict(id='m1', outcome='Both obligations', work=[{'issue':'FX-0001'},{'issue':'FX-0002'}],
                                     depends_on=[], exit_criteria=['Product check passes'], boundary='Composed result')])
        (raw / 'milestone-plan.json').write_text(json.dumps(plan))
        self.cli(root, 'milestone_plan.py', 'adopt', '--source-root', str(raw), '--json')
        git(root, 'add', 'docs'); git(root, 'commit', '-m', 'Adopt grouping')
        return root

    def observation(self, root, bound):
        return dict(**{key:copy.deepcopy(bound[key]) for key in ('run_id','segment_id','mandate_revision','selection','binding')},
                    milestone='m1', disposition='milestone-complete', candidate_revision=git(root,'rev-parse','HEAD'),
                    handoff_ref='runtime/frontier.json', ownership='quiescent', required_pending=[],
                    evidence_refs=['runtime/check.json'], acceptance_records=[dict(id=item['id'],outcome='pass',evidence_refs=['runtime/check.json'])
                    for group in ('obligations','exit_criteria') for item in bound['binding'][group]],
                    continuation=dict(intent='stop',next_milestone=None,reason='explicit-user-request',detail='Selected boundary reached'))

    def test_two_consumers_direct_lifecycle_and_read_only_checks(self):
        for name in ('one', 'two'):
            root = self.consumer(name)
            selected = strategies.resolve('direct-astra-max')
            (root/'runtime/selection.json').write_text(json.dumps(selected))
            bound = self.cli(root,'milestone_checkpoint.py','bind','--target','FX-0001','--selection',str(root/'runtime/selection.json'),
                             '--run-id',name,'--segment-id','initial','--mandate-revision','1','--json')
            self.assertNotIn('dispatch_id',bound)
            self.assertEqual(len(bound['binding']['obligations']),2)
            self.cli(root,'issue_board.py','claim','FX-0001','--json')
            failing = subprocess.run([sys.executable,'-B','check_product.py'],cwd=root,capture_output=True)
            self.assertNotEqual(failing.returncode,0)
            (root/'product.py').write_text('def add(a, b):\n    return a + b\n')
            (root/'unrelated.txt').write_text('keep this owner edit\n')
            self.cli(root,'record_evidence.py','--criterion','adds','--output',str(root/'runtime/check.json'),'--',sys.executable,'-B','check_product.py')
            git(root,'add','product.py'); git(root,'commit','-m','Correct addition')
            source_revision = git(root,'rev-parse','HEAD')
            (root/'runtime/acceptance.json').write_text(json.dumps(dict(approved=True,decision='done',records=[dict(
                criterion='adds',outcome='pass',revision=source_revision,evidence=dict(kind='command',detail='python -B check_product.py passed'))])))
            self.cli(root,'issue_board.py','finish','FX-0001','--acceptance',str(root/'runtime/acceptance.json'),'--json')
            observed = self.observation(root,bound)
            partial=copy.deepcopy(observed); partial['acceptance_records']=partial['acceptance_records'][:1]
            self.assertEqual(checkpoint.check(root,bound,partial,'quiescent')['action'],'reconcile')
            self.cli(root,'issue_board.py','claim','FX-0002','--json')
            self.cli(root,'issue_board.py','finish','FX-0002','--acceptance',str(root/'runtime/acceptance.json'),'--json')
            observed=self.observation(root,bound)
            (root/'runtime/binding.json').write_text(json.dumps(bound));(root/'runtime/observation.json').write_text(json.dumps(observed))
            before=git(root,'status','--porcelain')
            result=self.cli(root,'milestone_checkpoint.py','check','--checkpoint',str(root/'runtime/binding.json'),
                            '--observation',str(root/'runtime/observation.json'),'--execution','quiescent','--json')
            self.assertEqual(result['action'],'stop')
            self.cli(root,'issue_board.py','queue','--all','--json')
            self.assertEqual(git(root,'status','--porcelain'),before)
            self.assertEqual((root/'unrelated.txt').read_text(),'keep this owner edit\n')
            self.assertFalse((root/'.codex/agents').exists())

    def test_resume_pending_stale_selection_and_writer_guards(self):
        root=self.consumer('resume')
        bound=checkpoint.bind(root,'FX-0001',strategies.resolve('direct'),'run','segment','1')
        observed=self.observation(root,bound)
        for execution,action in [('active','wait'),('unknown','reconcile')]:
            self.assertEqual(checkpoint.check(root,bound,observed,execution)['action'],action)
        observed['disposition']='human-pending';observed['required_pending']=['external independent review'];observed['acceptance_records']=[]
        observed['continuation']=dict(intent='wait',next_milestone='m1',reason='pending-obligation',detail='Review remains external')
        self.assertEqual(checkpoint.check(root,bound,observed,'quiescent')['action'],'pending')
        observed['disposition']='continue-milestone'
        observed['continuation']=dict(intent='continue',next_milestone='m1',reason='current-milestone',detail='Resume the same primary')
        self.assertEqual(checkpoint.check(root,bound,observed,'quiescent')['action'],'continue-context')
        observed['segment_id']='different'
        self.assertEqual(checkpoint.check(root,bound,observed,'quiescent')['action'],'ignore-stale')
        observed['segment_id']='segment';observed['candidate_revision']='0'*40
        self.assertEqual(checkpoint.check(root,bound,observed,'quiescent')['action'],'reconcile')
        observed['candidate_revision']=git(root,'rev-parse','HEAD')
        card=root/'docs/issues/20-ready/FX-0001-work.md'
        card.write_text(card.read_text().replace('adds correctly','multiplies correctly'))
        self.assertEqual(checkpoint.check(root,bound,observed,'quiescent')['action'],'reconcile')
