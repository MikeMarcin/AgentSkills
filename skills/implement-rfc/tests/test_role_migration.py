"""Public migration regressions with disposable consumers and frozen prior outputs."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import test_render_runtime_adapters as adapter_tests
from test_render_runtime_adapters import VALIDATOR_MODULE, ROUTING, PROJECT

renderer = VALIDATOR_MODULE.renderer


class RoleMigrationTests(unittest.TestCase):
    run_renderer = adapter_tests.RenderRuntimeAdaptersTests.run_renderer

    def legacy(self, root):
        result = self.run_renderer(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest_path = root / '.mask/generated/implement-rfc/runtime-adapters.json'
        manifest = json.loads(manifest_path.read_text())
        for item in manifest['files']:
            path = root / item['path']
            name = path.stem
            old = {'rfc-worker': 'rfc-worker-routine', 'rfc-worker-deep': 'rfc-worker',
                   'rfc-reviewer-critical': 'rfc-critical-reviewer'}.get(name)
            if old:
                content = path.read_text().replace(name, old) + '\n# old generation\n'
                # Delay publication to avoid the overlapping worker destination.
                item['old_path'] = str(path)
                item['content'] = content
                item['path'] = str(path.with_name(old + path.suffix).relative_to(root))
                item['sha256'] = hashlib.sha256(content.encode()).hexdigest()
        for item in manifest['files']:
            if 'old_path' in item:
                Path(item.pop('old_path')).unlink()
        for item in manifest['files']:
            if 'content' in item:
                (root / item['path']).write_text(item.pop('content'))
        manifest['assignments'] = {'rfc-worker': 'deep', 'rfc-worker-routine': 'standard',
                                   'rfc-critical-reviewer': 'critical'}
        manifest_path.write_text(json.dumps(manifest))
        return manifest_path

    def snapshot(self, root):
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*')
                if p.is_file() and not p.is_symlink() and '.git' not in p.parts}

    def test_clean_retirement_check_purity_and_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); self.legacy(root)
            before = self.snapshot(root)
            self.assertEqual(self.run_renderer(root, '--check').returncode, 1)
            self.assertEqual(before, self.snapshot(root))
            result = self.run_renderer(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            for old in renderer.RETIRED_ROLES:
                self.assertFalse((root / f'.codex/agents/{old}.toml').exists())
                self.assertFalse((root / f'.claude/agents/{old}.md').exists())
            after = self.snapshot(root)
            self.assertEqual(self.run_renderer(root).returncode, 0)
            self.assertEqual(self.run_renderer(root, '--check').returncode, 0)
            self.assertEqual(after, self.snapshot(root))

    def test_conflicts_preflight_entire_set(self):
        for name in ('rfc-worker', 'rfc-worker-routine', 'rfc-critical-reviewer', 'rfc-worker-deep'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); self.legacy(root)
                path = root / f'.codex/agents/{name}.toml'
                path.write_text((path.read_text() if path.exists() else '') + '# user edit\n')
                before = self.snapshot(root)
                result = self.run_renderer(root)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(before, self.snapshot(root))

    def test_retired_symlink_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); self.legacy(root)
            path = root / '.codex/agents/rfc-worker-routine.toml'
            content = path.read_bytes(); path.unlink()
            outside = root / 'user.txt'; outside.write_bytes(content); path.symlink_to(outside)
            before = self.snapshot(root)
            self.assertEqual(self.run_renderer(root).returncode, 2)
            self.assertTrue(path.is_symlink()); self.assertEqual(before, self.snapshot(root))

    def test_interrupted_publication_is_detected_and_retryable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); self.legacy(root)
            original = renderer.write_or_check
            count = 0
            def crash(path, content, check):
                nonlocal count
                count += 1
                if count == 5:
                    raise OSError('simulated interruption')
                return original(path, content, check)
            with mock.patch.object(renderer, 'write_or_check', side_effect=crash), mock.patch(
                    'sys.argv', ['render_runtime_adapters.py', '--repo-root', str(root)]):
                with self.assertRaises(OSError):
                    renderer.main()
            pending = root / '.mask/generated/implement-rfc/runtime-adapters.pending.json'
            self.assertTrue(pending.exists())
            before = self.snapshot(root)
            self.assertEqual(self.run_renderer(root, '--check').returncode, 1)
            self.assertEqual(before, self.snapshot(root))
            result = self.run_renderer(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(pending.exists())
            self.assertEqual(self.run_renderer(root, '--check').returncode, 0)

    def test_common_specific_and_critical_addenda(self):
        roles = renderer.validate_roles(renderer.load_json(renderer.Path(__file__).resolve().parents[1] / 'config/roles.json'))
        project = {**PROJECT, 'role_addenda': {'rfc-worker': ['common'],
            'rfc-worker-routine': ['common', 'legacy standard only'],
            'rfc-worker-deep': ['deep only'], 'rfc-critical-reviewer': ['legacy review'],
            'rfc-reviewer-critical': ['legacy review', 'new review']}}
        for name in ('rfc-worker', 'rfc-worker-deep', 'rfc-reviewer-critical'):
            lines = renderer.rendered_role_instructions(name, roles[name], {'model': 'fixture', 'effort': 'low'}, project)
            if name.startswith('rfc-worker'):
                self.assertEqual(lines.count('common'), 1)
                self.assertEqual('legacy standard only' in lines, name == 'rfc-worker')
                self.assertEqual('deep only' in lines, name == 'rfc-worker-deep')
            else:
                self.assertEqual(lines.count('legacy review'), 1)
                self.assertIn('new review', lines)

    def test_active_frozen_order_blocks_until_collected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); self.legacy(root)
            run = root / '.mask/generated/implement-rfc/runs/old'; run.mkdir(parents=True)
            order = {'tasks': [{'id': 'worker', 'kind': 'agent',
                              'route': {'role': 'rfc-worker', 'model': 'old', 'effort': 'high'}}]}
            (run / 'order.json').write_text(json.dumps(order))
            (run / 'events.jsonl').write_text('{"task_id":"worker","event":"admitted"}\n')
            before = self.snapshot(root)
            result = self.run_renderer(root)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('active assignments', result.stderr)
            self.assertEqual(before, self.snapshot(root))
            (run / 'events.jsonl').write_text('{"task_id":"worker","event":"collected"}\n')
            self.assertEqual(self.run_renderer(root).returncode, 0)
            self.assertEqual(json.loads((run / 'order.json').read_text()), order)

    def test_retired_overrides_fail_explicitly(self):
        roles = renderer.validate_roles(renderer.load_json(Path(__file__).resolve().parents[1] / 'config/roles.json'))
        profiles = {'schema': 'implement-rfc.routing-profiles.v1', 'profiles': {'baseline': {}}}
        for name in renderer.RETIRED_ROLES:
            with self.assertRaisesRegex(ValueError, 'retired role selector'):
                renderer.select_routes(ROUTING, roles, profiles, explicit_routes={
                    'codex': {name: {'model': 'fixture', 'effort': 'low'}}})

    def test_independent_worker_and_review_overrides_both_providers(self):
        roles = renderer.validate_roles(renderer.load_json(Path(__file__).resolve().parents[1] / 'config/roles.json'))
        profiles = {'schema': 'implement-rfc.routing-profiles.v1', 'profiles': {'baseline': {}}}
        capabilities = {p: {'fixture': ['high', 'medium', 'low']} for p in ('codex', 'claude')}
        for provider in capabilities:
            routes, receipt = renderer.select_routes(ROUTING, roles, profiles, capabilities=capabilities,
                order_routes={provider: {'rfc-worker': {'model': 'fixture', 'effort': 'high'}}},
                explicit_routes={provider: {'rfc-reviewer': {'model': 'fixture', 'effort': 'medium'}}})
            self.assertEqual(routes[provider]['rfc-worker']['effort'], 'high')
            self.assertEqual(routes[provider]['rfc-reviewer']['effort'], 'medium')
            self.assertEqual(receipt['origins'][provider]['rfc-worker'], 'admitted_order')
            self.assertEqual(receipt['origins'][provider]['rfc-reviewer'], 'explicit_user')
            self.assertEqual(routes[provider]['rfc-worker-deep'], ROUTING['providers'][provider]['classes']['deep'])
            self.assertIsNone(receipt['observed'])

    def test_clean_prior_snapshot_can_be_restored_with_hash_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); manifest_path = self.legacy(root)
            prior = json.loads(manifest_path.read_text())
            snapshot = {root / item['path']: (root / item['path']).read_text() for item in prior['files']}
            snapshot[manifest_path] = manifest_path.read_text()
            self.assertEqual(self.run_renderer(root).returncode, 0)
            renderer.publish_adapters(root, snapshot, manifest_path, prior, False)
            for path, content in snapshot.items():
                self.assertEqual(path.read_text(), content)
            self.assertFalse((root / '.codex/agents/rfc-worker-deep.toml').exists())
            self.assertFalse((root / '.codex/agents/rfc-reviewer-critical.toml').exists())
            self.assertEqual(self.run_renderer(root, '--check').returncode, 1)
