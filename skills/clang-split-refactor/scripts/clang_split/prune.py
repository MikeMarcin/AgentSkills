"""Drop a source's include directives that nothing it still contains uses.

Kept: includes chosen for declarations referenced in any configured build,
headers defining macros the source tests in directives, includes under a
platform guard (their branch was not parsed), and the plan's `keep_includes`.
"""
import os
import re
import subprocess

from .cx import parse, parse_args_for, include_dirs, git_root, is_system, ci
from .includes import closure_index
from .stdmap import std_header, qt_header
from .extract import DIRECTIVE, HEADER_GLOBS, PLATFORM_MACROS

INCLUDE = re.compile(r'^\s*#\s*include\s*([<"][^>"]+[>"])')


def run(plan, write=False):
    K = ci.CursorKind
    base_dir = plan.get('_dir', os.getcwd())
    src = os.path.realpath(os.path.join(base_dir, plan['source']))
    build = os.path.join(base_dir, plan['build'])
    builds = [build] + [os.path.join(base_dir, b) for b in plan.get('alt_builds', [])]
    closures = os.path.join(base_dir, plan.get('closures', os.path.join(build, 'clang_split_closures.json')))
    root = os.path.realpath(os.path.join(base_dir, plan['project_root']) if plan.get('project_root') else git_root(src))
    keep = set(plan.get('keep_includes', []))
    platform_guards = PLATFORM_MACROS | set(plan.get('platform_macros', []))
    text = open(src, encoding='utf-8').read()
    lines = text.split('\n')
    cache = closure_index(build, src, closures)
    sized = sorted(cache.items(), key=lambda kv: len(kv[1]))
    pargs, _ = parse_args_for(build, src)
    idirs = [os.path.realpath(d) for d in include_dirs(pargs)]
    qt_dirs = [d for d in idirs if os.path.basename(d.rstrip('/')).startswith('Qt')]

    def project_include(f):
        if not f.startswith(root + os.sep) or is_system(f):
            return None
        if os.path.dirname(f) == os.path.dirname(src):
            return f'"{os.path.basename(f)}"'
        best = min((f[len(d) + 1:] for d in idirs if f.startswith(d + os.sep)), key=len, default=None)
        return f'"{best}"' if best else None

    needed_files, needed = set(), set()
    for b in builds:
        tu, errs = parse(b, src, detailed=True)
        if errs:
            raise SystemExit(f'parse errors in {b}: {[str(e) for e in errs[:2]]}')
        for c in tu.cursor.walk_preorder():
            if c.location.file is None or os.path.realpath(c.location.file.name) != src:
                continue
            if c.is_definition() and c.canonical is not None and c.canonical.location.file is not None:
                # A definition keeps the header that declares it.
                cf = os.path.realpath(c.canonical.location.file.name)
                if cf != src and not is_system(cf):
                    needed_files.add(cf)
            r = c.referenced
            if r is None or r.location.file is None or r.kind in (K.NAMESPACE, K.NAMESPACE_ALIAS):
                continue
            rd = r.get_definition()
            if rd is not None and rd.location.file is not None:
                r = rd
            f = os.path.realpath(r.location.file.name)
            if f == src:
                continue
            canon = std_header(r) or qt_header(r, qt_dirs)
            if canon:
                needed.add(canon)
            elif not is_system(f):
                needed_files.add(f)
    for f in needed_files:
        rel = project_include(f)
        if rel:
            needed.add(rel)
            continue
        for inc, closure in sized:
            if f in closure:
                needed.add(inc)
                break
    tested = set()
    for ln in lines:
        m = DIRECTIVE.match(ln.encode())
        if m and m.group(1) != b'endif':
            tested |= set(re.findall(r'[A-Za-z_]\w*', m.group(2).decode())) - {'defined'}
    if tested:
        out = subprocess.run(['git', '-C', root, 'grep', '-l', '-E',
                              r'^\s*#\s*define\s+(' + '|'.join(sorted(tested)) + r')\b', '--'] + HEADER_GLOBS,
                             capture_output=True, text=True).stdout
        for path in out.splitlines():
            rel = project_include(os.path.realpath(os.path.join(root, path)))
            if rel:
                needed.add(rel)
    kept_lines, dropped, stack = [], [], []
    for ln in lines:
        d = re.match(r'^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)', ln)
        if d:
            if d.group(1) in ('if', 'ifdef', 'ifndef'):
                stack.append(d.group(2))
            elif d.group(1) == 'endif' and stack:
                stack.pop()
            kept_lines.append(ln)
            continue
        m = INCLUDE.match(ln)
        if m:
            inc = m.group(1)
            guarded = any(set(re.findall(r'[A-Za-z_]\w*', s)) & platform_guards for s in stack)
            if inc in needed or inc in keep or guarded:
                kept_lines.append(ln)
            else:
                dropped.append(inc)
            continue
        kept_lines.append(ln)
    result = '\n'.join(kept_lines)
    empty = re.compile(r'\n[ \t]*#[ \t]*if[^\n]*\n(?:[ \t]*\n)*[ \t]*#[ \t]*endif[^\n]*(?=\n)')
    while True:
        t2 = empty.sub('', result)
        if t2 == result:
            break
        result = t2
    result = re.sub(r'\n{3,}', '\n\n', result)
    if write:
        open(src, 'w', encoding='utf-8').write(result)
    return {'dropped': dropped, 'kept': sum(1 for ln in kept_lines if INCLUDE.match(ln)), 'written': bool(write)}
