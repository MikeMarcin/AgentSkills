#!/usr/bin/env python3
"""Resolve trusted passive execution recipes; never launch models or change config."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

PACKAGE = Path(__file__).resolve().parents[1]
CATALOG = 'implement-rfc.strategy-catalog.v1'
SELECTION = 'implement-rfc.strategy-selection.v1'
CONTRACT = 'implement-rfc.engineering.v1'
TOKEN = re.compile(r'[a-z0-9][a-z0-9-]{0,95}')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    path = Path(path)
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('strategy input exceeds 1 MiB')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def fingerprint(value):
    return 'sha256:' + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def token(value):
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        raise ValueError('expected a bounded lowercase identifier')
    return value


def package_file(package, relative):
    if (not isinstance(relative, str) or not relative or relative.startswith('/') or '\\' in relative
            or ':' in relative or any(part in ('', '.', '..') for part in relative.split('/'))):
        raise ValueError('recipe paths must be contained package-relative files')
    current = Path(package).resolve()
    for part in relative.split('/'):
        current = current / part
        if current.is_symlink():
            raise ValueError('recipe entries cannot be symlinks')
    if not current.is_file() or current.stat().st_size > 1024 * 1024:
        raise ValueError('missing or oversized recipe entrypoint: ' + relative)
    return current


def routes(value):
    if not isinstance(value, dict) or len(value) > 32:
        raise ValueError('routing must be a bounded map of exact route slots')
    for slot, route in value.items():
        token(slot)
        if (not isinstance(route, dict) or set(route) != {'provider', 'model', 'effort'}
                or any(not isinstance(item, str) or not 1 <= len(item) <= 128
                       or re.search(r'[\s<>${}]', item) for item in route.values())):
            raise ValueError('each selected route needs exact provider, model and effort')
    return value


def load_catalog(package=PACKAGE):
    value = read_json(Path(package) / 'config/strategy-catalog.json')
    if (not isinstance(value, dict) or set(value) != {'schema', 'common_contract', 'default', 'recipes', 'presets'}
            or value['schema'] != CATALOG):
        raise ValueError('unsupported strategy catalog')
    common = value['common_contract']
    if not isinstance(common, dict) or set(common) != {'id', 'entrypoint'} or common['id'] != CONTRACT:
        raise ValueError('incompatible common contract')
    package_file(package, common['entrypoint'])
    workflow = read_json(Path(package) / 'mask-workflow.json')
    if not isinstance(workflow, dict) or not isinstance(workflow.get('scopes', {}), dict):
        raise ValueError('invalid workflow contract')
    scopes = [workflow, *workflow.get('scopes', {}).values()]
    if any(not isinstance(scope, dict) or not isinstance(scope.get('profiles', {}), dict) for scope in scopes):
        raise ValueError('invalid workflow requirement profiles')
    found = {}
    if not isinstance(value['recipes'], list) or not 1 <= len(value['recipes']) <= 64:
        raise ValueError('catalog requires a bounded recipe list')
    fields = {'id', 'revision', 'common_contract', 'entrypoint', 'requirement_profile',
              'owners', 'delegation', 'required_routes', 'hosts'}
    for recipe in value['recipes']:
        if not isinstance(recipe, dict) or set(recipe) != fields:
            raise ValueError('invalid recipe descriptor')
        name = token(recipe['id'])
        if name in found or recipe['common_contract'] != CONTRACT:
            raise ValueError('duplicate or incompatible recipe')
        if not isinstance(recipe['revision'], str) or not recipe['revision'].strip():
            raise ValueError('recipe revision required')
        package_file(package, recipe['entrypoint'])  # Validate location without loading unselected text.
        if recipe['requirement_profile'] is not None:
            token(recipe['requirement_profile'])
            if any(recipe['requirement_profile'] not in scope.get('profiles', {}) for scope in scopes):
                raise ValueError('recipe requires an undeclared workflow profile')
        if recipe['delegation'] not in ('none', 'system', 'recipe'):
            raise ValueError('invalid delegation authority')
        if (not isinstance(recipe['owners'], dict) or set(recipe['owners']) != {'engineering', 'bookkeeping', 'product_edits'}
                or any(not isinstance(v, str) or not v for v in recipe['owners'].values())):
            raise ValueError('explicit engineering, bookkeeping and edit owners required')
        required = recipe['required_routes']
        if not isinstance(required, list) or len(required) > 32 or any(not isinstance(v, str) for v in required) or len(set(required)) != len(required):
            raise ValueError('invalid required route slots')
        for slot in required:
            token(slot)
        if (not isinstance(recipe['hosts'], dict) or not recipe['hosts']
                or any(not isinstance(k, str) or not isinstance(v, str) or not v for k, v in recipe['hosts'].items())):
            raise ValueError('explicit host qualification facts required')
        found[name] = recipe
    presets = {}
    if not isinstance(value['presets'], list) or len(value['presets']) > 64:
        raise ValueError('invalid preset list')
    for preset in value['presets']:
        if not isinstance(preset, dict) or set(preset) != {'id', 'topology_id', 'routing'}:
            raise ValueError('invalid preset')
        name = token(preset['id'])
        if name in found or name in presets or preset['topology_id'] not in found:
            raise ValueError('duplicate preset or unknown recipe')
        routes(preset['routing'])
        presets[name] = preset
    if value['default'] not in found and value['default'] not in presets:
        raise ValueError('unknown default recipe or preset')
    return value, found, presets


def resolve(explicit=None, *, preserved=None, preference=None, routing=None, package=PACKAGE):
    catalog, recipes, presets = load_catalog(package)
    if preserved is not None:
        validate_selection(preserved, package=package)
    name = explicit or (preserved['strategy'] if preserved else None) or preference or catalog['default']
    if name not in recipes and name not in presets:
        raise ValueError('unknown strategy: ' + str(name))
    topology = presets[name]['topology_id'] if name in presets else name
    recipe = recipes[topology]
    selected_routes = dict(presets[name]['routing']) if name in presets else {}
    if preserved is not None and explicit is None:
        selected_routes.update(preserved['routing'])
    if routing is not None:
        selected_routes.update(routes(routing))
    if any(route['provider'] not in recipe['hosts'] for route in selected_routes.values()):
        raise ValueError('selected route provider is unsupported by this recipe')
    paths = [catalog['common_contract']['entrypoint'], recipe['entrypoint']]
    source = {path: hashlib.sha256(package_file(package, path).read_bytes()).hexdigest() for path in paths}
    missing = sorted(set(recipe['required_routes']) - set(selected_routes))
    return dict(schema=SELECTION, strategy=name, topology_id=topology, recipe_revision=recipe['revision'],
                recipe_fingerprint=fingerprint({'descriptor': recipe, 'instructions': source}),
                routing=selected_routes, requirement_profile=recipe['requirement_profile'],
                owners=recipe['owners'], delegation=recipe['delegation'], instruction_paths=paths,
                configuration_complete=not missing, missing_routes=missing, host_load='not_verified')


def validate_selection(value, *, package=PACKAGE):
    if not isinstance(value, dict) or value.get('schema') != SELECTION:
        raise ValueError('unsupported preserved selection')
    expected = resolve(value.get('strategy'), routing=routes(value.get('routing')), package=package)
    if value != expected:
        raise ValueError('selection is malformed or recipe changed; reconcile before a new segment')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['resolve', 'check'])
    parser.add_argument('--strategy')
    parser.add_argument('--preserved', type=Path)
    parser.add_argument('--preference')
    parser.add_argument('--routing', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        preserved = read_json(args.preserved) if args.preserved else None
        if args.operation == 'check':
            result = validate_selection(preserved)
        else:
            result = resolve(args.strategy, preserved=preserved, preference=args.preference,
                             routing=read_json(args.routing) if args.routing else None)
        print(json.dumps(result) if args.json else f"Strategy: {result['strategy']}; configuration {'complete' if result['configuration_complete'] else 'needs routes'}; host not verified")
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({'state': 'invalid', 'detail': str(exc)}) if args.json else str(exc))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
