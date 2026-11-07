"""Include-what-you-use from a translation unit's own direct includes.

Each direct include directive of the source is parsed alone (same flags) to get
the files it brings in. An entity needs, for each file declaring something it
references, the direct include with the smallest closure containing that file.
"""
import json, os, re, sys, hashlib
from .cx import ci, parse_args_for

INCLUDE_RE = re.compile(rb'^[ \t]*#[ \t]*include[ \t]*([<"][^>"]+[>"])', re.M)


def direct_includes(data):
    return [m.group(1).decode() for m in INCLUDE_RE.finditer(data)]


STD = 'algorithm any array atomic barrier bit charconv chrono cmath compare concepts condition_variable cstddef cstdint cstdlib cstring cerrno deque exception expected filesystem format fstream functional future initializer_list iomanip iostream istream iterator latch limits list map memory mutex new numeric optional ostream queue ranges ratio semaphore set shared_mutex source_location span sstream stdexcept stop_token string string_view system_error thread tuple type_traits typeindex typeinfo unordered_map unordered_set utility variant vector'.split()


def closure_index(build, source, cache_path):
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    args, directory = parse_args_for(build, source)
    data = open(source, 'rb').read()
    changed = False
    for inc in direct_includes(data) + [f'<{h}>' for h in STD]:
        if inc in cache:
            continue
        # The probe sits beside the source so quoted includes resolve the same way.
        probe = os.path.join(os.path.dirname(source), '.clang_split_probe_' + hashlib.sha1(inc.encode()).hexdigest()[:10] + '.cpp')
        open(probe, 'w').write(f'#include {inc}\n')
        try:
            os.chdir(directory)
            tu = ci.Index.create().parse(probe, args=args)
            files = sorted({os.path.realpath(i.include.name) for i in tu.get_includes()})
        finally:
            os.remove(probe)
        cache[inc] = files
        changed = True
    if changed:
        json.dump(cache, open(cache_path, 'w'))
    return cache


def needed_includes(cursors, src, cache, extra_files=()):
    files = set(extra_files)
    for c in cursors:
        for k in c.walk_preorder():
            r = k.referenced
            if r is None or r.location.file is None:
                continue
            files.add(os.path.realpath(r.location.file.name))
    files.discard(os.path.realpath(src))
    sized = sorted(cache.items(), key=lambda kv: len(kv[1]))
    chosen = []
    unresolved = []
    for f in sorted(files):
        for inc, closure in sized:
            if f in closure:
                if inc not in chosen:
                    chosen.append(inc)
                break
        else:
            unresolved.append(f)
    return chosen, unresolved
