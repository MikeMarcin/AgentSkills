"""Admission checks for bounded work orders; validation is not authorization."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from project_config import resolve_context, git_environment

MAX_ORDER = 128 * 1024
TOKEN = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def inside(root, value):
    if not isinstance(value, str) or not value or '\0' in value:
        raise ValueError('Expected a repository-relative path')
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value:
        raise ValueError('Paths must be relative without parent traversal')
    target = root / path
    if not target.resolve().is_relative_to(root):
        raise ValueError('Path escapes physical consumer root')
    cursor = target
    while cursor != root:
        if cursor.is_symlink():
            raise ValueError('Order paths cannot traverse symlinks')
        cursor = cursor.parent
    return target


def load(path):
    with path.open('rb') as stream:
        raw = stream.read(MAX_ORDER + 1)
    if len(raw) > MAX_ORDER:
        raise ValueError('Order exceeds 128 KiB')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def validate(order):
    required = {'schema', 'example_only', 'run_id', 'slice_id', 'consumer_root', 'base_revision',
                'approved_dirty_paths', 'profile', 'routing_digest', 'permissions_ref',
                'max_parallel_mutations', 'max_agent_dispatches', 'tasks', 'input_hashes',
                'root_identity', 'invocation_root', 'routing_ref'}
    if not isinstance(order, dict) or set(order) != required:
        raise ValueError('Order has missing or unknown fields')
    if order['schema'] != 'implement-rfc.slice-order.v1' or order['example_only'] is not False:
        raise ValueError('Only admitted non-example v1 orders can execute')
    for key in ('run_id', 'slice_id', 'profile'):
        if not isinstance(order[key], str) or not TOKEN.fullmatch(order[key]):
            raise ValueError('Invalid order identity')
    root = Path(order['consumer_root'])
    if not root.is_absolute() or root.resolve(strict=True) != root:
        raise ValueError('consumer_root must be the physical absolute root')
    resolve_context(repo_root=root)
    st = root.stat()
    if order['root_identity'] != {'device': st.st_dev, 'inode': st.st_ino}:
        raise ValueError('Consumer root identity changed')
    invocation = Path(order['invocation_root'])
    if not invocation.is_absolute() or not invocation.resolve().is_relative_to(root):
        raise ValueError('Invocation root must be inside consumer')
    if type(order['max_parallel_mutations']) is not int or order['max_parallel_mutations'] != 1 or type(order['max_agent_dispatches']) is not int or not 0 <= order['max_agent_dispatches'] <= 2:
        raise ValueError('Runner supports serial execution and at most two explicit agent dispatches')
    if not isinstance(order['base_revision'], str) or not re.fullmatch('[0-9a-f]{40}([0-9a-f]{24})?', order['base_revision']):
        raise ValueError('Invalid baseline revision')
    subprocess.run(['git', '-C', str(root), 'cat-file', '-e', order['base_revision']+'^{commit}'], env=git_environment(), check=True, capture_output=True)
    hashes = order['input_hashes']
    if not isinstance(hashes, dict) or not 1 <= len(hashes) <= 256:
        raise ValueError('Bounded relevant input hashes required')
    for name, expected in hashes.items():
        path = inside(root, name)
        if not isinstance(expected, str) or file_hash(path) != expected:
            raise ValueError('Relevant input changed: '+name)
    for key in ('permissions_ref', 'routing_ref'):
        if order[key] not in hashes:
            raise ValueError('Permission and routing files must be frozen inputs')
    if order['routing_digest'] != hashes[order['routing_ref']]:
        raise ValueError('Routing digest mismatch')
    permissions = load(inside(root, order['permissions_ref']))
    if set(permissions) not in ({'schema','execution','allowed_argv'}, {'schema','execution','allowed_argv','allowed_agents'}) or permissions['schema'] != 'implement-rfc.command-permissions.v1' or permissions['execution'] != 'local_unsandboxed':
        raise ValueError('Explicit local execution policy required; path declarations are not a sandbox')
    dirty = order['approved_dirty_paths']
    if not isinstance(dirty, list) or len(dirty) > 256:
        raise ValueError('Invalid approved dirty paths')
    for name in dirty:
        inside(root, name)
        if name not in hashes:
            raise ValueError('Dirty baseline must bind exact input bytes')
    tasks = order['tasks']
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 32:
        raise ValueError('Order requires 1–32 tasks')
    seen = set()
    agents = 0
    for task in tasks:
        common = {'id','kind','depends_on','cwd','timeout_seconds','owned_paths','retry'}
        kind = task.get('kind') if isinstance(task, dict) else None
        extra = {'argv','predicate'} if kind == 'command' else {'acceptance_ref'} if kind == 'integration_gate' else {'route','task_packet'} if kind == 'agent' else set()
        if kind not in ('command','integration_gate','agent') or set(task) != common | extra:
            raise ValueError('Unsupported task kind or fields')
        if not isinstance(task['id'], str) or not TOKEN.fullmatch(task['id']) or task['id'] in seen:
            raise ValueError('Invalid or duplicate task ID')
        deps = task['depends_on']
        if not isinstance(deps,list) or len(set(deps)) != len(deps) or not set(deps) <= seen:
            raise ValueError('Dependencies must name unique preceding tasks')
        if not inside(root,task['cwd']).is_dir():
            raise ValueError('Task cwd missing')
        if type(task['timeout_seconds']) is not int or not 1 <= task['timeout_seconds'] <= 86400:
            raise ValueError('Invalid timeout')
        if task['retry'] not in ('never','safe_command_once'):
            raise ValueError('Unsupported command retry policy')
        if not isinstance(task['owned_paths'],list) or len(task['owned_paths']) > 256:
            raise ValueError('Invalid owned paths')
        for path in task['owned_paths']:
            inside(root,path)
        if kind == 'command':
            argv = task['argv']
            if not isinstance(argv,list) or not 1 <= len(argv) <= 128 or any(not isinstance(x,str) or '\0' in x for x in argv):
                raise ValueError('Commands require exact argv')
            if not isinstance(permissions['allowed_argv'], list) or argv not in permissions['allowed_argv'] or not Path(argv[0]).is_absolute():
                raise ValueError('Command lacks exact permission or absolute executable')
            if any(x in ('-c','-Command','/c','-EncodedCommand') for x in argv[1:]):
                raise ValueError('Inline evaluated command fragments are unsupported; use a reviewed script')
            for argument in argv[1:]:
                candidate = Path(argument)
                if not candidate.is_absolute():
                    candidate = inside(root, task['cwd']) / candidate
                if candidate.is_file() and candidate.resolve().is_relative_to(root):
                    relative = str(candidate.relative_to(root))
                    inside(root, relative)
                    if relative not in hashes:
                        raise ValueError('Command file input lacks a frozen hash: '+relative)
            predicate = task['predicate']
            if not isinstance(predicate,dict) or set(predicate) != {'exit_code','required_artifacts','tests'} or type(predicate['exit_code']) is not int:
                raise ValueError('Explicit exit/artifact/test predicates required')
            if predicate['tests'] not in ('none','unittest','pytest'):
                raise ValueError('Unsupported test count predicate')
            if not isinstance(predicate['required_artifacts'],list) or len(predicate['required_artifacts']) > 256:
                raise ValueError('Invalid artifacts')
            for path in predicate['required_artifacts']:
                inside(root,path)
        elif kind == 'agent':
            agents += 1
            if task['retry'] != 'never' or task['owned_paths']:
                raise ValueError('Public companion stages are read-only with no automatic retry')
            route = task['route']
            if (not isinstance(route,dict) or set(route) != {'provider','role','profile','model','effort','permission_policy'}
                    or route['provider'] not in ('codex','claude')
                    or route['role'] not in ('rfc-utility','rfc-scout','rfc-reviewer','rfc-critical-reviewer','rfc-reviewer-critical')
                    or route['profile'] != order['profile'] or route['permission_policy'] != 'read-only-leaf'
                    or route not in permissions.get('allowed_agents', [])):
                raise ValueError('Exact approved read-only agent route required')
            if task['task_packet'] not in hashes:
                raise ValueError('Task packet must be a frozen input')
            packet = load(inside(root,task['task_packet']))
            if (packet.get('cwd') != str(inside(root,task['cwd']))
                    or packet.get('model') != route['model'] or packet.get('effort') != route['effort']
                    or packet.get('timeout_seconds') != task['timeout_seconds']):
                raise ValueError('Packet contradicts admitted root, route or deadline')
            if route['provider'] == 'codex':
                from slice_codex import CodexDriver
                driver = object.__new__(CodexDriver)
                if packet.get('sandbox') != 'read-only' or packet.get('approval_policy') != 'never':
                    raise ValueError('Public Codex companion requires read-only never-approve policy')
            else:
                from slice_claude import ClaudeDriver
                driver = object.__new__(ClaudeDriver)
            driver._capabilities = {'launch':True}
            driver.validate(packet)  # Structural only; installed capability/auth checked at launch.
        else:
            if not isinstance(task['acceptance_ref'],str) or not task['acceptance_ref']:
                raise ValueError('Integrator acceptance reference required')
            if task is not tasks[-1] or set(deps) != seen:
                raise ValueError('Final gate must depend on every preceding task')
        seen.add(task['id'])
    if agents > order['max_agent_dispatches']:
        raise ValueError('Agent dispatch budget exceeded')
    if tasks[-1]['kind'] != 'integration_gate':
        raise ValueError('Final integrator gate required')
    return root
