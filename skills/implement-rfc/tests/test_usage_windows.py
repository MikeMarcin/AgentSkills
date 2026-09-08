"""Run on native Windows with MASK_TEST_PROGRAM; skips never qualify Windows."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import zipfile
import test_usage_cli as fixtures


@unittest.skipUnless(os.name == 'nt', 'Requires native Windows; no POSIX substitute')
@unittest.skipUnless(fixtures.MASK.is_file(), 'Set MASK_TEST_PROGRAM to the native public MASK entrypoint')
class WindowsUsageTests(unittest.TestCase):
    setUp = fixtures.UsageCliTests.setUp
    mask = fixtures.UsageCliTests.mask
    run_usage = fixtures.UsageCliTests.run_usage

    def test_native_registry_launcher_percent_paths_and_case_alias(self):
        # Two separately registered worktrees plus an unavailable registration.
        fixtures.UsageCliTests.test_real_registry_worktree_and_unavailable_root(self)
        bin_dir=self.root/'bin ü 100%'
        self.mask('self','install','--bin-dir',bin_dir,'--dry-run')
        self.mask('self','install','--bin-dir',bin_dir)
        launcher=bin_dir/'mask.cmd'
        self.assertTrue(launcher.is_file())
        before=hashlib.sha256(launcher.read_bytes()).hexdigest()
        result=self.run_usage(fixtures.SCRIPT,'--mask-projects','--mask-executable',launcher,
                              '--mask-home',self.home,'--dry-run')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['projects']),3)
        self.assertEqual(hashlib.sha256(launcher.read_bytes()).hexdigest(),before)
        alias=Path(str(self.nested).swapcase())
        self.assertTrue(alias.samefile(self.nested))
        result=subprocess.run([sys.executable,str(fixtures.SCRIPT),'--dry-run'],cwd=alias,
                              capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(Path(json.loads(result.stdout)['projects'][0]['root']).samefile(self.project))
        custom=bin_dir/'custom.cmd';custom.write_text('@echo off\necho UNSUPPORTED\n')
        result=self.run_usage(fixtures.SCRIPT,'--mask-projects','--mask-executable',custom,'--dry-run')
        self.assertEqual(result.returncode,2)
        self.assertIn('--mask-python-entrypoint',result.stderr)

    def test_native_link_and_readonly_package(self):
        # A failure to create a native link is a qualification failure, not copy fallback.
        fixtures.UsageCliTests.test_nested_link_dryrun_and_strict_empty_archive(self)
        package=self.root/'pinned ü 100%'/ 'scripts';package.mkdir(parents=True)
        for name in ('usage.py','usage_scope.py','usage_capture.py','slice_events.py'):
            shutil.copyfile(fixtures.SCRIPT.parent/name,package/name)
        files=list(package.iterdir())
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        # Windows read-only file attributes, not a claim about directory ACL enforcement.
        try:
            for path in files:os.chmod(path,0o444)
            result=self.run_usage(package/'usage.py','--out',self.root/'pinned.zip',
                                  '--claude-home',self.root/'empty','--codex-home',self.root/'empty','--json')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir()})
            with zipfile.ZipFile(self.root/'pinned.zip') as archive:
                self.assertEqual(json.loads(archive.read('manifest.json'))['platform'],'Windows')
        finally:
            for path in files:os.chmod(path,0o666)
