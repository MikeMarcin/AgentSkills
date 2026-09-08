#!/usr/bin/env python3
"""Execute an explicitly approved command order, then return to its integrator."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time

sys.dont_write_bytecode = True
from slice_model import load, validate, digest, inside, TOKEN

OUTPUT_LIMIT = 4 * 1024 * 1024


def runs_root(root):
    from project_config import resolve_context
    root = resolve_context(repo_root=root).repo_root
    return inside(root, '.mask/generated/implement-rfc/runs')


def run_path(root, run):
    if not TOKEN.fullmatch(run):
        raise ValueError('Invalid run ID')
    return runs_root(root) / run


def event(path, task, state, **fields):
    record = {'task_id':task or '__run__', 'event':state, 'timestamp':time.time(), **fields}
    with (path/'events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, sort_keys=True)+'\n')
        stream.flush()
        os.fsync(stream.fileno())
    return record


def status(path):
    latest = {}
    warnings = []
    with (path/'events.jsonl').open('rb') as stream:
        for line in stream:
            if len(line) > 65536:
                raise ValueError('Oversized event')
            if not line.endswith(b'\n'):
                warnings.append('torn_final_event'); break
            record = json.loads(line)
            latest[record['task_id']] = record
    return {'run_id':path.name, 'tasks':latest, 'warnings':warnings,
            'semantic_acceptance':'not_decided_by_runner'}


def stop(process):
    if process.poll() is not None:
        return
    if os.name == 'posix':
        os.killpg(process.pid, signal.SIGTERM)
    else:
        process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait(timeout=2)


def command(path, task, root):
    task_id = task['id']
    attempt = task_id + '-1'
    event(path, task_id, 'dispatch_intent', attempt_id=attempt)
    if (path/'cancel.request').exists():
        return event(path, task_id, 'cancelled', attempt_id=attempt)
    output = {}
    overflow = threading.Event()
    def drain(pipe, name):
        data = bytearray()
        try:
            with (path/(attempt+'.'+name)).open('xb') as stream:
                while chunk := pipe.read(65536):
                    remaining = OUTPUT_LIMIT - len(data)
                    stream.write(chunk[:remaining])
                    data.extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        overflow.set(); break
        finally:
            pipe.close()
            output[name] = bytes(data).decode('utf-8', errors='replace')
    started = time.monotonic()
    process = subprocess.Popen(task['argv'], cwd=inside(root, task['cwd']), stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=os.name == 'posix')
    event(path, task_id, 'running', attempt_id=attempt, process_id=process.pid,
          ownership='launched_child_process', enforcement='local_unsandboxed_serial')
    readers = [threading.Thread(target=drain, args=(pipe,name), daemon=True)
               for pipe,name in ((process.stdout,'stdout'),(process.stderr,'stderr'))]
    for reader in readers:
        reader.start()
    reason = None
    try:
        while process.poll() is None:
            if (path/'cancel.request').exists():
                reason = 'cancelled'; break
            if overflow.is_set():
                reason = 'output_limit'; break
            if time.monotonic()-started >= task['timeout_seconds']:
                reason = 'timeout'; break
            time.sleep(.05)
    except KeyboardInterrupt:
        reason = 'cancelled'
    finally:
        if reason:
            stop(process)
        for reader in readers:
            reader.join(timeout=2)
    if any(reader.is_alive() for reader in readers):
        reason = reason or 'completion_unknown'
    if overflow.is_set():
        reason = reason or 'output_limit'
    combined = output.get('stdout','')+'\n'+output.get('stderr','')
    predicate = task['predicate']
    count = None
    if predicate['tests'] == 'unittest':
        found = re.search(r'\bRan (\d+) tests?\b', combined)
        count = int(found[1]) if found else 0
    elif predicate['tests'] == 'pytest':
        count = sum(int(x) for x in re.findall(r'\b(\d+) passed\b', combined))
    missing = [name for name in predicate['required_artifacts'] if not inside(root,name).is_file()]
    passed = reason is None and process.returncode == predicate['exit_code'] and not missing and (count is None or count > 0)
    # Same command evidence shape as record_evidence.py; bounded streaming adds deadline/output handling.
    evidence = {'criterion':task_id, 'outcome':'pass' if passed else 'fail',
                'revision':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
                'evidence':{'kind':'command','detail':json.dumps(task['argv']), 'exit_code':process.returncode,
                            'elapsed_seconds':round(time.monotonic()-started,3),
                            'stdout_tail':output.get('stdout','')[-4000:], 'stderr_tail':output.get('stderr','')[-4000:]},
                'selected_test_count':count, 'missing_artifacts':missing, 'termination':reason}
    with (path/(attempt+'.report.json')).open('x',encoding='utf-8') as stream:
        json.dump(evidence,stream);stream.flush();os.fsync(stream.fileno())
    event(path,task_id,'report_ready',attempt_id=attempt,report_path=attempt+'.report.json')
    return event(path, task_id, 'collected' if passed else 'cancelled' if reason == 'cancelled' else 'execution_failed',
                 attempt_id=attempt, report_path=attempt+'.report.json')


def native_driver(provider):
    if provider == 'codex':
        from slice_codex import CodexDriver
        return CodexDriver()
    from slice_claude import ClaudeDriver
    return ClaudeDriver()


def agent(path, task, root, order):
    from slice_runtime import Runtime
    driver = native_driver(task['route']['provider'])
    runtime = Runtime(path, driver, order['run_id'])
    attempt = task['id'] + '-1'
    try:
        event(path,task['id'],'dispatch_intent',attempt_id=attempt,
              requested_route=task['route'],routing_digest=order['routing_digest'])
        packet = load(inside(root,task['task_packet']))
        receipt = runtime.dispatch(task['id'],packet)
        if receipt['event'] != 'dispatched':
            return event(path,task['id'],'completion_unknown',attempt_id=attempt)
        event(path,task['id'],'running',attempt_id=attempt,
              driver_session_id=receipt['driver_session_id'],driver_turn_id=receipt['driver_turn_id'])
        def stream():
            for value in driver.events(receipt):
                if (path/'cancel.request').exists():
                    runtime.cancel(attempt)
                    return
                yield value
        records = runtime.consume(attempt,stream())
        cancelled = any(r['event'] in ('cancel_requested','cancelled') for r in records)
        delivered = any(r['event']=='awaiting_integration' for r in records)
        failure = next((r for r in reversed(records) if r['event'] in ('execution_failed','blocked')), None)
        state = 'cancelled' if cancelled else 'collected' if delivered else failure['event'] if failure else 'completion_unknown'
        return event(path,task['id'],state,reason=failure.get('reason') if failure else None,
                     attempt_id=attempt,report_path=attempt+'.report.txt' if delivered else None,
                     semantic_acceptance='not_decided_by_runner')
    except Exception as error:
        return event(path,task['id'],'completion_unknown',attempt_id=attempt,detail=type(error).__name__)
    finally:
        driver.close()


def start(order, approval):
    root = validate(order)
    if approval != digest(order):
        raise ValueError('Explicit current --approve-order digest required')
    path = run_path(root,order['run_id'])
    path.parent.mkdir(parents=True,exist_ok=True)
    path.mkdir()  # Refuse reuse, including uncertain prior dispatch; never automatically relaunch.
    with (path/'order.json').open('x',encoding='utf-8') as stream:
        json.dump(order,stream);stream.flush();os.fsync(stream.fileno())
    event(path,None,'admitted',order_digest=approval)
    for task in order['tasks']:
        if (path/'cancel.request').exists():
            event(path,task['id'],'cancelled');break
        try:
            validate(order)  # Relevant inputs, root, permission and route checked before every dispatch.
            if task['kind'] == 'integration_gate':
                event(path,task['id'],'awaiting_integration',acceptance_ref=task['acceptance_ref']);break
            result = agent(path,task,root,order) if task['kind']=='agent' else command(path,task,root)
            if result['event'] != 'collected':
                break
        except (OSError,ValueError,subprocess.SubprocessError) as error:
            event(path,task['id'],'completion_unknown',detail=str(error)[:1000]);break
    return status(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path)
    sub = parser.add_subparsers(dest='command',required=True)
    for name in ('validate','start'):
        command_parser = sub.add_parser(name)
        command_parser.add_argument('--order',type=Path,required=True)
        if name == 'start':
            command_parser.add_argument('--approve-order',required=True)
    for name in ('status','cancel','wait'):
        command_parser = sub.add_parser(name)
        command_parser.add_argument('--run',required=True)
        command_parser.add_argument('--json',action='store_true')
        if name == 'wait':
            command_parser.add_argument('--until',choices=['gate-or-terminal'],default='gate-or-terminal')
            command_parser.add_argument('--timeout',type=int,default=60)
    args = parser.parse_args()
    if args.command in ('validate','start'):
        order = load(args.order)
        root = validate(order)
        if args.repo_root and root != args.repo_root.resolve():
            raise ValueError('Explicit consumer does not match order')
        result = {'valid':True,'approval_digest':digest(order),'execution_authorized':False}
        if args.command == 'start':
            result = start(order,args.approve_order)
    else:
        path = run_path(args.repo_root,args.run)
        if args.command == 'cancel':
            with (path/'cancel.request').open('a'):
                pass
            result = {'cancellation_requested':True,'acknowledgement':'inspect events; no automatic recovery'}
        elif args.command == 'wait':
            deadline = time.monotonic()+max(0,min(args.timeout,3600))
            while True:
                result = status(path)
                if any(r['event'] in ('awaiting_integration','execution_failed','blocked','cancelled','completion_unknown') for r in result['tasks'].values()) or time.monotonic() >= deadline:
                    break
                time.sleep(.1)
        else:
            result = status(path)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,TypeError,subprocess.SubprocessError) as error:
        print(json.dumps({'error':str(error)}),file=sys.stderr)
        raise SystemExit(2)
