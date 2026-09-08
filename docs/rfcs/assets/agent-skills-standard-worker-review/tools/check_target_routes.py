#!/usr/bin/env python3
"""Check RFC target configuration and rendered requests, without launching models.

Use after implementation. Imports the selected repository's trusted renderer;
performs no rendering writes, deployment, quota polling, or provider requests.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PACK = Path(__file__).resolve().parents[1]


def version(value: str) -> tuple[int, int, int]:
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Expected numeric three-part CLI floor, received {value!r}")
    return tuple(int(part) for part in value.split('.'))


def configuration_findings(roles: dict, routing: dict, target: dict) -> list[str]:
    findings: list[str] = []
    actual = roles.get('roles', {})
    if set(actual) != set(target['roles']):
        findings.append('Canonical roles differ from target (retire routine; add worker-deep).')
    if routing.get('assignments') != target['assignments']:
        findings.append('Role/class assignments differ from target; review must be independent.')
    for name, limits in target['roles'].items():
        value = actual.get(name, {})
        for field, wanted in limits.items():
            default = False if field == 'may_spawn_utility' else None
            if value.get(field, default) != wanted:
                findings.append(f'{name}: {field} differs from the preserved boundary.')
    for provider, expected in target['provider_classes'].items():
        actual_classes = routing.get('providers', {}).get(provider, {}).get('classes', {})
        if actual_classes != expected:
            findings.append(f'{provider}: provider routes differ from the exact target.')
    try:
        floor = routing.get('providers', {}).get('claude', {}).get('minimum_cli_version')
        if version(floor) < version(target['minimum_claude_cli']):
            findings.append('Claude CLI floor is below the documented Fable 5.1 minimum.')
    except ValueError as exc:
        findings.append(str(exc))
    return findings


def rendering_findings(root: Path, roles_data: dict, routing: dict, target: dict) -> list[str]:
    scripts = root / 'skills/implement-rfc/scripts'
    spec = importlib.util.spec_from_file_location('target_renderer', scripts / 'render_runtime_adapters.py')
    if spec is None or spec.loader is None:
        return ['Cannot load the selected repository renderer.']
    renderer = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(scripts))
    spec.loader.exec_module(renderer)
    roles = renderer.validate_roles(roles_data)
    renderer.validate_routing(routing, roles)
    project = {'attended_review_skill': None, 'role_addenda': {
        'rfc-worker': ['COMMON_WORKER_BOUNDARY_SENTINEL'],
        'rfc-worker-routine': ['LEGACY_STANDARD_BOUNDARY_SENTINEL'],
        'rfc-worker-deep': ['DEEP_ONLY_BOUNDARY_SENTINEL'],
    }}
    findings: list[str] = []
    for name, role in roles.items():
        model_class = target['assignments'][name]
        for provider in ('codex', 'claude'):
            route = target['provider_classes'][provider][model_class]
            fn = renderer.render_codex_agent if provider == 'codex' else renderer.render_claude_agent
            text = fn(name, role, route, project, 'offline-target-check')
            if provider == 'codex':
                model_line = 'model = ' + json.dumps(route['model'])
                effort_line = 'model_reasoning_effort = ' + json.dumps(route['effort'])
                if model_line not in text or (route['effort'] is not None and effort_line not in text):
                    findings.append(f'{provider}/{name}: exact model/effort missing in rendered request.')
                if route['effort'] is None and 'model_reasoning_effort =' in text:
                    findings.append(f'{provider}/{name}: unsupported effort emitted.')
                if 'enabled = false' not in text:
                    findings.append(f'{provider}/{name}: expected leaf-agent configuration.')
            else:
                if 'model: ' + json.dumps(route['model']) not in text:
                    findings.append(f'{provider}/{name}: exact model missing in frontmatter.')
                frontmatter = text.split('---', 2)[1]
                if route['effort'] is not None and f"effort: {route['effort']}" not in frontmatter:
                    findings.append(f'{provider}/{name}: exact effort missing in frontmatter.')
                if route['effort'] is None and re.search(r'^effort:', frontmatter, re.M):
                    findings.append(f'{provider}/{name}: unsupported effort emitted.')
                tools_line = next((s for s in frontmatter.splitlines() if s.startswith('tools:')), '')
                if re.search(r'\bAgent\b', tools_line):
                    findings.append(f'{provider}/{name}: Agent tool enabled for leaf role.')
            if name in ('rfc-worker', 'rfc-worker-deep'):
                common = text.count('COMMON_WORKER_BOUNDARY_SENTINEL')
                legacy = text.count('LEGACY_STANDARD_BOUNDARY_SENTINEL')
                deep = text.count('DEEP_ONLY_BOUNDARY_SENTINEL')
                if (common, legacy, deep) != (1, int(name == 'rfc-worker'), int(name == 'rfc-worker-deep')):
                    findings.append(f'{provider}/{name}: common/legacy/deep addenda inheritance is incorrect.')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    args = parser.parse_args()
    try:
        root = args.repo_root.resolve(strict=True)
        config = root / 'skills/implement-rfc/config'
        roles = json.loads((config / 'roles.json').read_text(encoding='utf-8'))
        routing = json.loads((config / 'routing.json').read_text(encoding='utf-8'))
        target = json.loads((PACK / 'fixtures/target-routing.json').read_text(encoding='utf-8'))
        findings = configuration_findings(roles, routing, target)
        if not findings:
            findings += rendering_findings(root, roles, routing, target)
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(f'ERROR {exc}', file=sys.stderr)
        return 2
    for finding in findings:
        print('FAIL ' + finding)
    if not findings:
        print('PASS target configuration and in-memory native requests; no serving or quality claim.')
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
