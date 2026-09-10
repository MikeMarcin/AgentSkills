"""Published schema structure and representative strict-boundary checks."""
import copy
import json
from pathlib import Path
import unittest

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    Draft202012Validator = None

SCHEMAS = Path(__file__).resolve().parents[1] / 'schemas'


@unittest.skipIf(Draft202012Validator is None, 'jsonschema required for schema validation')
class MilestoneSchemas(unittest.TestCase):
    def setUp(self):
        self.schemas = {name: json.loads((SCHEMAS / name).read_text()) for name in (
            'milestone-plan.schema.json', 'milestone-assignment.schema.json',
            'milestone-return-v2.schema.json')}
        self.registry = Registry().with_resources((name, Resource.from_contents(value))
            for name, value in self.schemas.items())
        self.binding = dict(plan_id='demo', plan_path='docs/rfcs/plans/demo/milestone-plan.json',
            milestone_id='usable', definition_fingerprint='sha256:' + 'a'*64,
            obligation_fingerprint='sha256:' + 'b'*64, prerequisite_fingerprint='sha256:' + 'c'*64,
            obligations=[dict(id='ONE-0001:*', source='ONE-0001', selector=None,
                              source_fingerprint='sha256:' + 'd'*64)],
            exit_criteria=[dict(id='usable:exit:1', text='Public path passes')],
            structural='valid', references='resolved', semantic_coverage='unknown',
            diagnostics=[], diagnostics_truncated=False)
        self.identity = dict(run_id='run', dispatch_id='dispatch', producer_id='producer',
                             mandate_revision='1', milestone='usable')

    def errors(self, name, value):
        return list(Draft202012Validator(self.schemas[name], registry=self.registry).iter_errors(value))

    def test_assignment_is_closed_and_requires_resolved_binding(self):
        name = 'milestone-assignment.schema.json'
        assignment = dict(self.identity, schema='implement-rfc.milestone-assignment.v1',
                          consumer_root='/tmp/consumer', branch='main', binding=self.binding,
                          target_milestones=['usable', 'followup'])
        self.assertEqual(self.errors(name, assignment), [])
        missing = dict(assignment)
        del missing['target_milestones']
        self.assertTrue(self.errors(name, missing))
        for targets in ([], ['usable', 'usable'], [' '], [1]):
            self.assertTrue(self.errors(name, dict(assignment, target_milestones=targets)))
        for field, value in [('consumer_root', 'relative'), ('unknown', True)]:
            bad = dict(assignment, **{field: value})
            self.assertTrue(self.errors(name, bad))
        bad = copy.deepcopy(assignment)
        bad['binding']['references'] = 'unresolved'
        self.assertTrue(self.errors(name, bad))

    def test_return_extension_and_completion_structure(self):
        name = 'milestone-return-v2.schema.json'
        returned = dict(self.identity, schema='implement-rfc.milestone-return.v2',
            disposition='continue-milestone', summary='More work remains', candidate_revision=None,
            handoff_ref=None, ownership='quiescent', next_objective='Finish public path',
            required_pending=[], evidence_refs=[], binding=self.binding,
            continuation=dict(intent='continue', next_milestone='usable',
                              reason='current-milestone', detail='Public evidence remains'),
            acceptance_records=[])
        self.assertEqual(self.errors(name, returned), [])
        bad = copy.deepcopy(returned)
        bad['continuation']['automatic'] = True
        self.assertTrue(self.errors(name, bad))
        bad = copy.deepcopy(returned)
        bad.update(disposition='milestone-complete', handoff_ref='handoff.md', evidence_refs=['test.md'])
        self.assertTrue(self.errors(name, bad))
        bad['acceptance_records'] = [dict(id='ONE-0001:*', outcome='pass', evidence_refs=['test.md'])]
        self.assertEqual(self.errors(name, bad), [])
        # Cross-reference coverage of exits is deliberately enforced by runtime.

    def test_schemas_are_valid(self):
        for schema in self.schemas.values():
            Draft202012Validator.check_schema(schema)


if __name__ == '__main__':
    unittest.main()
