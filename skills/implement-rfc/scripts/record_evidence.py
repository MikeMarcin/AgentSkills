#!/usr/bin/env python3
"""Capture one selected command mechanically; the agent judges criterion relevance."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from project_config import resolve_context, git_environment


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path)
    parser.add_argument('--mode',choices=('project','personal'))
    parser.add_argument('--workflow-root',type=Path)
    parser.add_argument('--criterion',required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    if not command: parser.error('supply a command after --')
    context=resolve_context(repo_root=args.repo_root, mode=args.mode, workflow_root=args.workflow_root)
    output = args.output
    if context.mode == 'personal':
        import personal_lanes
        import personal_state
        personal_lanes.validate_pair(context)
        if output is not None:
            output = output if output.is_absolute() else context.runtime_root / output
            personal_state._check_local_path(personal_state.home_for(context.source_root), output)
    revision=subprocess.run(['git','-C',str(context.source_root),'rev-parse','HEAD'],env=git_environment(),capture_output=True,text=True,check=True).stdout.strip()
    started=time.monotonic()
    result=subprocess.run(command,cwd=context.source_root,capture_output=True,text=True)
    record={'criterion':args.criterion,'outcome':'pass' if result.returncode==0 else 'fail','revision':revision,
            'evidence':{'kind':'command','detail':json.dumps(command),'exit_code':result.returncode,
                        'elapsed_seconds':round(time.monotonic()-started,3),
                        'stdout_tail':result.stdout[-4000:],'stderr_tail':result.stderr[-4000:]}}
    text=json.dumps(record,indent=2)+'\n'
    if output:
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x',encoding='utf-8') as stream: stream.write(text)
    print(text,end='')
    return 0 if result.returncode==0 else 1


if __name__=='__main__':
    try: sys.exit(main())
    except (OSError,ValueError,subprocess.SubprocessError) as error:
        print(str(error),file=sys.stderr);sys.exit(2)
