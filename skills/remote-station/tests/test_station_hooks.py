from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACK / 'scripts'))
import station_hooks


class StationHookRemovalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / '.codex/hooks.json'
        self.path.parent.mkdir()
        self.station = dict(type='command', command='python3 /checkout/.agents/skills/implement-rfc/scripts/remote_station_guard.py')
        self.other = dict(type='command', command='project-format-check', timeout=7)
        self.data = dict(description='project hooks', metadata={'preserved': True}, hooks={
            'PreToolUse': [dict(matcher='Bash', hooks=[self.station, self.other], extra='keep')],
            'UserPromptSubmit': [dict(hooks=[self.station])],
            'Stop': [dict(hooks=[self.other])], 'EmptyEvent': []})
        self.path.write_text(json.dumps(self.data), encoding='utf-8')

    def test_inspection_and_preview_preserve_exact_bytes(self):
        before = self.path.read_bytes()
        status = station_hooks.inspect(self.root)
        preview = station_hooks.inspect(self.root, off=True, dry_run=True)
        self.assertEqual(status['station_commands'], 2)
        self.assertFalse(status['would_change'])
        self.assertTrue(preview['would_change'])
        self.assertFalse(preview['changed'])
        self.assertEqual(self.path.read_bytes(), before)

    def test_removal_preserves_unrelated_commands_groups_and_settings(self):
        result = station_hooks.inspect(self.root, off=True)
        self.assertTrue(result['changed'])
        expected = dict(self.data, hooks=dict(self.data['hooks']))
        expected['hooks'].pop('UserPromptSubmit')
        expected['hooks']['PreToolUse'] = [dict(matcher='Bash', hooks=[self.other], extra='keep')]
        self.assertEqual(json.loads(self.path.read_text()), expected)
        before = self.path.read_bytes()
        self.assertFalse(station_hooks.inspect(self.root, off=True)['changed'])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse((self.root / '.git').exists())
        self.assertFalse((self.root / '.remote-station.json').exists())

    def test_windows_guard_spelling_is_removed(self):
        self.data['hooks'] = {'Stop': [dict(hooks=[dict(type='command', command_windows=
            r'py -3 C:\project\.agents\skills\implement-rfc\scripts\remote_station_guard.py')])]}
        self.path.write_text(json.dumps(self.data))
        self.assertEqual(station_hooks.inspect(self.root, off=True)['station_commands'], 1)
        self.assertEqual(json.loads(self.path.read_text())['hooks'], {})

    def test_mixed_platform_commands_are_preserved_for_review(self):
        self.data['hooks'] = {'Stop': [dict(hooks=[dict(self.station, command_windows='unrelated-task')])]}
        self.path.write_text(json.dumps(self.data))
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'unrelated platform command'):
            station_hooks.inspect(self.root, off=True)
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_configuration_does_not_create_files(self):
        self.path.unlink()
        self.assertFalse(station_hooks.inspect(self.root, off=True)['changed'])
        self.assertFalse(self.path.exists())

    def test_malformed_and_duplicate_configuration_is_preserved(self):
        for text in ('{', '{"hooks":[],"metadata":1}', '{"hooks":{},"hooks":{}}',
                     '{"hooks":{"Stop":[{"unknown":1}]}}'):
            self.path.write_text(text)
            with self.assertRaises(ValueError):
                station_hooks.inspect(self.root, off=True)
            self.assertEqual(self.path.read_text(), text)

    def test_linked_configuration_and_parent_are_refused(self):
        original = self.path.read_bytes()
        other = self.root / 'other.json'
        other.write_bytes(original)
        self.path.unlink()
        self.path.symlink_to(other)
        with self.assertRaises(ValueError):
            station_hooks.inspect(self.root, off=True)
        self.assertEqual(other.read_bytes(), original)
        self.path.unlink()
        self.path.parent.rmdir()
        directory = self.root / 'shared'
        directory.mkdir()
        (directory / 'hooks.json').write_bytes(original)
        self.path.parent.symlink_to(directory, target_is_directory=True)
        with self.assertRaises(ValueError):
            station_hooks.inspect(self.root, off=True)
        self.assertEqual((directory / 'hooks.json').read_bytes(), original)

    def test_public_launcher_does_not_need_workflow_readiness_or_station_metadata(self):
        # Two consumers share one installed package; no origin/config/station is
        # needed to remove the hook that would otherwise obstruct their repair.
        for root in (self.root, self.root / 'second-consumer'):
            root.mkdir(exist_ok=True)
            link = root / '.agents/skills/remote-station'
            link.parent.mkdir(parents=True)
            link.symlink_to(PACK, target_is_directory=True)
            result = subprocess.run([sys.executable, '-B', str(link / 'scripts/launch_remote_station.py'),
                'hooks', 'off', '--dry-run', '--json'], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            parsed = json.loads(result.stdout)
            self.assertEqual(Path(parsed['path']), root.resolve() / '.codex/hooks.json')
            self.assertFalse(parsed['changed'])

    def test_guard_commands_from_either_skill_location_are_station_commands(self):
        windows = r'py -3 C:\checkout\.agents\skills\remote-station\scripts\remote_station_guard.py --enforce'
        current = dict(type='command', command='python3 /checkout/.agents/skills/remote-station/scripts/remote_station_guard.py --enforce',
                       command_windows=windows)
        self.assertTrue(station_hooks.station_command(current))
        self.assertTrue(station_hooks.station_command(self.station))
        self.assertFalse(station_hooks.station_command(self.other))

    def test_default_root_is_the_git_root_of_a_subdirectory(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        nested = self.root / 'a' / 'b'
        nested.mkdir(parents=True)
        result = subprocess.run([sys.executable, '-B', str(PACK / 'scripts/station_hooks.py'), 'status', '--json'],
                                cwd=nested, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertEqual(Path(parsed['path']).resolve(), self.path.resolve())
        self.assertEqual(parsed['station_commands'], 2)


if __name__ == '__main__':
    unittest.main()
