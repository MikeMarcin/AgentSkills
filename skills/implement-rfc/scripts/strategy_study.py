#!/usr/bin/env python3
"""Validate a study manifest against the installed catalog without creating or running it."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import execution_strategy as strategy
import usage_experiments as experiments


def check(value, *, package=strategy.PACKAGE):
    missing = experiments.validate(value)
    selections = []
    for arm in value['arms']:
        selection = strategy.resolve(arm['strategy'], routing=arm['requested_routing'], package=package)
        if arm['topology_id'] != selection['topology_id']:
            raise ValueError('arm topology disagrees with selected recipe')
        if arm['recipe_revision'] is not None and arm['recipe_revision'] != selection['recipe_revision']:
            raise ValueError('arm recipe revision disagrees with installed catalog')
        ownership = {'none': 'disabled', 'system': 'native_system', 'recipe': 'recipe'}[selection['delegation']]
        if arm['child_route_ownership'] != ownership:
            raise ValueError('arm child-route ownership disagrees with selected recipe')
        if not selection['configuration_complete']:
            missing.append(arm['arm_id'] + ': required routes ' + ', '.join(selection['missing_routes']))
        # A frozen arm records the entire resolved routing, including preset defaults.
        if arm['requested_routing'] != selection['routing']:
            missing.append(arm['arm_id'] + ': full resolved routing snapshot')
        selections.append(selection)
    if value['status'] != 'draft_not_runnable' and missing:
        raise ValueError('frozen study has unresolved strategy inputs: ' + ', '.join(missing))
    return dict(state=value['status'], unresolved=sorted(set(missing)), selections=selections,
                launch_authorized=False, host_load='not_verified',
                limitation='Shape and catalog validation only; referenced evidence and run authority require separate review.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', required=True, type=Path)
    parser.add_argument('--require-frozen', action='store_true')
    args = parser.parse_args()
    try:
        result = check(strategy.read_json(args.study))
        print(json.dumps(result))
        return 1 if args.require_frozen and result['state'] == 'draft_not_runnable' else 0
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps(dict(state='invalid', detail=str(exc))))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
