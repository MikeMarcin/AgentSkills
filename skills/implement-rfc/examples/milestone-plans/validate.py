#!/usr/bin/env python3
"""Validate or render an offline plan without selecting a consumer repository."""
import argparse
from pathlib import Path
import sys

# This module has only standard-library dependencies and never resolves a consumer.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from milestone_plan_contract import load_json, validate_plan, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--render', action='store_true', help='print generated Markdown to stdout')
    args = parser.parse_args()
    try:
        plan = load_json(args.plan.resolve())
        errors = validate_plan(plan)
        if errors:
            raise ValueError('; '.join(errors))
        print(render(plan), end='') if args.render else print('Structurally valid; references and semantic coverage unchecked.')
        return 0
    except (ValueError, OSError, TypeError, RecursionError) as exc:
        print(f'Invalid plan: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
