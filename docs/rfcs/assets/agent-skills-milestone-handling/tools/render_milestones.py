#!/usr/bin/env python3
"""Render a plan's human view to stdout; redirect explicitly to write a file."""
import argparse
from pathlib import Path
import sys
from plan_contract import load_json, render

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path)
    args=parser.parse_args(argv)
    try:
        output=render(load_json(args.plan))
    except (OSError,ValueError,TypeError,KeyError,RecursionError) as exc:
        print(f'Cannot render milestone plan: {exc}',file=sys.stderr)
        return 1
    print(output,end='')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
