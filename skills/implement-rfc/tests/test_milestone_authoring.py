"""Offline authoring and normal source exports use the canonical artifacts."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[1]
KIT = SKILL / 'examples/milestone-plans'
sys.path.insert(0, str(SKILL / 'scripts'))
import render_runtime_adapters

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None


class AuthoringTests(unittest.TestCase):
    @unittest.skipIf(Draft202012Validator is None, 'jsonschema required for published-schema check')
    def test_template_matches_published_schema(self):
        schema = json.loads((SKILL / 'schemas/milestone-plan.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads((KIT / 'milestone-plan.json').read_text()))

    def test_offline_validation_render_and_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = root / 'milestone-plan.json'
            shutil.copyfile(KIT / plan.name, plan)
            command = [sys.executable, '-B', str(KIT / 'validate.py'), str(plan)]
            checked = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn('references and semantic coverage unchecked', checked.stdout)
            rendered = subprocess.run(command + ['--render'], cwd=root, capture_output=True, text=True)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertEqual(rendered.stdout, (KIT / 'MILESTONES.md').read_text())
            self.assertFalse((root / '.mask').exists())
            malformed = json.loads(plan.read_text())
            malformed['milestones'][0]['depends_on'] = ['usable-fix']
            plan.write_text(json.dumps(malformed))
            refused = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(refused.returncode, 2)
            self.assertIn('dependency', refused.stderr)

    def test_manifest_and_actual_dump_include_authoring_and_live_linkage(self):
        portable = {row['path'] for row in render_runtime_adapters.portable_manifest(SKILL)['files']}
        expected = {'examples/milestone-plans/' + path.name for path in KIT.iterdir() if path.is_file()}
        expected.add('schemas/milestone-plan.schema.json')
        self.assertTrue(expected <= portable)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.mask.json').write_text('{}')
            for relative in expected:
                destination = root / 'skills/implement-rfc' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(SKILL / relative, destination)
            live_paths = ['docs/rfcs/RFC-ASK-0012-authored-milestone-plans-and-continuation.md',
                'docs/rfcs/plans/agent-skills-milestone-handling/milestone-plan.json']
            for relative in live_paths:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            for relative in ['.codex/sessions/private.json', '.claude/projects/private.json',
                             '.mask/runs/private.json', 'artifacts/session.md']:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('PRIVATE_SESSION_MARKER')
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/make_project_source_dumps.py'),
                '--root', str(root), '--stdout'], capture_output=True, text=True, cwd=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            for relative in expected:
                self.assertIn('### skills/implement-rfc/' + relative, result.stdout)
            for relative in live_paths:
                self.assertIn('### ' + relative, result.stdout)
            self.assertIn('plans/agent-skills-milestone-handling/milestone-plan.json', result.stdout)
            self.assertNotIn('PRIVATE_SESSION_MARKER', result.stdout)


if __name__ == '__main__':
    unittest.main()
