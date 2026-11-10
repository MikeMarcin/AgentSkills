"""Registration hooks: tell the build about files a split created.

The default hook inserts generated files after an anchor line in CMake (or any
line-oriented) lists. Projects with manifests, digests or pins supply their own
command through `register.command` in the plan; it runs from the project root
with CLANG_SPLIT_FILES set to the new files (newline separated, root-relative).
"""
import os
import re
import subprocess
from pathlib import Path


def generated_files(directory, prefix, extensions=('.cpp', '.hpp', '.h', '.cc', '.cxx', '.hh')):
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(tuple(extensions)))


def insert_after_anchor(root, spec, write=True):
    """spec: {"dir", "prefix", "lists": [{"file", "anchor", "entry", "kinds"}]}.

    Each list must contain its anchor exactly once. Earlier generated entries that
    directly follow the anchor are replaced, so re-running is idempotent.
    """
    names = generated_files(os.path.join(root, spec['dir']), spec['prefix'])
    changed = []
    for lst in spec['lists']:
        path = os.path.join(root, lst['file'])
        lines = Path(path).read_text(encoding='utf-8').split('\n')
        kinds = tuple(lst.get('kinds', ['.cpp']))
        entries = [lst['entry'].format(name=n) for n in names if n.endswith(kinds)]
        prior = re.compile(re.escape(lst['entry']).replace(re.escape('{name}'), re.escape(spec['prefix']) + r'\S+'))
        out, hits, i = [], 0, 0
        while i < len(lines):
            ln = lines[i]
            out.append(ln)
            i += 1
            if ln.strip() == lst['anchor']:
                hits += 1
                indent = re.match(r'^\s*', ln).group(0)
                while i < len(lines) and prior.fullmatch(lines[i].strip()):
                    i += 1
                out += [indent + e for e in entries]
        if hits != 1:
            raise SystemExit(f'{lst["file"]}: anchor {lst["anchor"]!r} found {hits} times, expected 1')
        if write:
            Path(path).write_text('\n'.join(out), encoding='utf-8')
        changed.append(lst['file'])
    return {'files': names, 'lists': changed}


def run(root, spec, write=True):
    if spec.get('command'):
        names = generated_files(os.path.join(root, spec['dir']), spec['prefix'])
        env = dict(os.environ, CLANG_SPLIT_FILES='\n'.join(os.path.join(spec['dir'], n) for n in names))
        if not write:
            return {'files': names, 'command': spec['command'], 'ran': False}
        res = subprocess.run(spec['command'], shell=isinstance(spec['command'], str), cwd=root, env=env)
        if res.returncode:
            raise SystemExit(f'registration command failed with {res.returncode}')
        return {'files': names, 'command': spec['command'], 'ran': True}
    return insert_after_anchor(root, spec, write)
