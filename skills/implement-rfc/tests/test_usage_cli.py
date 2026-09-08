"""Public CLI qualification with a real disposable MASK registry."""
import hashlib
import json
import os
import shutil
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/usage.py'
MASK = Path(os.environ.get('MASK_TEST_PROGRAM', str(Path(__file__).resolve().parents[3].parent / 'ManageAgentSkills/mask.py')))


class UsageCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rfc-usage-cli-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'project ü 100%'
        self.project.mkdir()
        self.nested = self.project / 'nested'
        self.nested.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        self.home = self.root / 'mask-home'

    def mask(self, *args):
        result = subprocess.run([sys.executable, '-B', str(MASK), *map(str, args), '--home', str(self.home), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(result.stdout)

    def run_usage(self, script=SCRIPT, *args):
        return subprocess.run([sys.executable, str(script), *map(str, args)], cwd=self.nested, capture_output=True, text=True)

    def test_nested_link_dryrun_and_strict_empty_archive(self):
        link = self.project / '.agents/skills/implement-rfc'
        link.parent.mkdir(parents=True)
        link.symlink_to(SCRIPT.parents[1], target_is_directory=True)
        result = self.run_usage(link / 'scripts/usage.py', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['projects'][0]['root'], str(self.project))
        output = self.root / 'capture.zip'
        result = self.run_usage(link / 'scripts/usage.py', '--out', output, '--claude-home', self.root/'empty-claude', '--codex-home', self.root/'empty-codex', '--strict', '--json')
        self.assertEqual(result.returncode, 3, result.stderr)
        with zipfile.ZipFile(output) as archive:
            manifest = json.loads(archive.read('manifest.json'))
            for name, entry in manifest['files'].items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), entry['sha256'])
            self.assertEqual(manifest['session_count'], 0)
        self.assertEqual(list(self.nested.iterdir()), [])

    @unittest.skipIf(os.name == 'nt', 'Native POSIX read-only fixture')
    def test_read_only_package_does_not_create_bytecode(self):
        package = self.root / 'readonly-package'
        (package/'scripts').mkdir(parents=True)
        for name in ('usage.py', 'usage_capture.py', 'usage_scope.py', 'slice_events.py'):
            shutil.copyfile(SCRIPT.parent/name, package/'scripts'/name)
        files = list((package/'scripts').iterdir())
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        try:
            for path in files:
                path.chmod(stat.S_IRUSR)
            (package/'scripts').chmod(stat.S_IRUSR | stat.S_IXUSR)
            result = self.run_usage(package/'scripts/usage.py', '--out', self.root/'readonly.zip', '--claude-home', self.root/'empty', '--codex-home', self.root/'empty')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (package/'scripts').iterdir()})
        finally:
            (package/'scripts').chmod(stat.S_IRWXU)
            for path in files:
                path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    @unittest.skipUnless(MASK.is_file(), 'Set MASK_TEST_PROGRAM for native registry qualification')
    def test_real_registry_worktree_and_unavailable_root(self):
        source = self.root / 'AgentSkills'
        source.mkdir()
        subprocess.run(['git', 'init', '-q', str(source)], check=True)
        subprocess.run(['git', '-C', str(source), 'remote', 'add', 'origin', str(self.root/'AgentSkills.git')], check=True)
        (source / 'skills/example').mkdir(parents=True)
        (source / 'skills/example/SKILL.md').write_text('---\nname: example\ndescription: Fixture\n---\n')
        self.mask('init', '--source', source)
        self.mask('config', 'show')
        self.mask('source', 'status')
        subprocess.run(['git', '-C', str(self.project), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '--allow-empty', '-qm', 'base'], check=True)
        worktree = self.root / 'worktree'
        subprocess.run(['git', '-C', str(self.project), 'worktree', 'add', '-qb', 'fixture', str(worktree)], check=True)
        missing = self.root / 'missing'
        missing.mkdir()
        for root in (self.project, worktree, missing):
            self.mask('project', 'init', '--project', root)
            self.mask('project', 'register', root)
            self.mask('project', 'show', '--project', root)
        missing.rename(self.root / 'retained-missing')
        result = self.run_usage(SCRIPT, '--mask-projects', '--mask-python-entrypoint', MASK, '--mask-home', self.home, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = json.loads(result.stdout)['projects']
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(not r['available_now'] for r in rows), 1)
        output = self.root/'registry.zip'
        result = self.run_usage(SCRIPT, '--mask-projects', '--mask-python-entrypoint', MASK, '--mask-home', self.home, '--out', output, '--claude-home', self.root/'empty', '--codex-home', self.root/'empty', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(len(json.loads(archive.read('scopes.json'))['projects']), 3)


if __name__ == '__main__':
    unittest.main()
