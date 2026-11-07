"""clang-split: libclang-driven, behavior-preserving C++ file splitting.

Every command prints JSON on stdout. Plan-relative paths resolve against the
directory containing the plan file.
"""
import argparse
import collections
import json
import os
import sys


def _emit(obj, out=None):
    text = json.dumps(obj, indent=1, sort_keys=False)
    if out:
        with open(out, 'w', encoding='utf-8') as fh:
            fh.write(text + '\n')
        print(json.dumps({'wrote': out}))
    else:
        print(text)


def _load_plan(path):
    plan = json.load(open(path, encoding='utf-8'))
    plan['_dir'] = os.path.dirname(os.path.abspath(path))
    return plan


def cmd_doctor(a):
    from . import cx
    lib, libdir = cx.find_libclang()
    cx.load()
    _emit({'libclang': lib, 'resource_dir': cx.resource_dir(), 'macos_sdk': cx.macos_sdk(), 'python': sys.version.split()[0]})


def cmd_analyze(a):
    from . import segments
    if a.class_line:
        g = segments.analyze_class(a.build, a.source, a.class_line)
    else:
        g = segments.analyze(a.build, a.source, a.alt_build)
    _emit(g, a.output)


def cmd_segment(a):
    from . import segments
    g = json.load(open(a.graph))
    _emit(segments.segment(g, a.max_lines, a.penalty), a.output)


def cmd_plan(a):
    from . import segments
    g = json.load(open(a.graph))
    segs = json.load(open(a.segments))
    names = json.load(open(a.names))
    base = json.load(open(a.base)) if a.base else {}
    plan, sizes = segments.plan(g, segs, names, a.support, base)
    if a.output:
        _emit(plan, a.output)
        print(json.dumps({'lines_per_stem': sizes}), file=sys.stderr)
    else:
        _emit({'plan': plan, 'lines_per_stem': sizes})


def cmd_extract(a):
    from . import extract, register
    plan = _load_plan(a.plan)
    report = extract.run(plan, write=a.write)
    if a.write and plan.get('register'):
        from .cx import git_root
        spec = plan['register']
        root = os.path.join(plan['_dir'], plan['project_root']) if plan.get('project_root') else git_root(
            os.path.join(plan['_dir'], plan['source']))
        report['register'] = register.run(root, spec, write=True)
    _emit(report, a.report)


def cmd_prune(a):
    from . import prune
    _emit(prune.run(_load_plan(a.plan), write=a.write))


def cmd_register(a):
    from . import register
    spec = json.load(open(a.spec))
    spec = spec.get('register', spec)
    _emit(register.run(a.root, spec, write=not a.dry_run))


def cmd_outline(a):
    from .cx import parse, in_file, ci
    K = ci.CursorKind
    tu, errs = parse(a.build, a.source)
    result = {'errors': [str(e) for e in errs[:5]], 'entities': []}
    if a.class_line:
        cls = next((k for k in tu.cursor.walk_preorder() if k.kind in (K.CLASS_DECL, K.STRUCT_DECL)
                    and k.is_definition() and in_file(k, a.source) and k.extent.start.line == a.class_line), None)
        if cls is None:
            raise SystemExit(f'no class definition starts on line {a.class_line}')
        stats = collections.Counter()
        lines = collections.Counter()
        for k in cls.get_children():
            kind = k.kind.name + ('_DEF' if k.kind.name in ('CXX_METHOD', 'CONSTRUCTOR', 'DESTRUCTOR', 'FUNCTION_TEMPLATE') and k.is_definition() else '')
            n = k.extent.end.line - k.extent.start.line + 1
            stats[kind] += 1
            lines[kind] += n
            result['entities'].append({'kind': kind, 'name': k.spelling, 'line': k.extent.start.line, 'lines': n})
        result['summary'] = {k: {'count': stats[k], 'lines': lines[k]} for k in stats}
        _emit(result)
        return

    def walk(c, depth, prefix):
        for k in c.get_children():
            if not in_file(k, a.source):
                continue
            s, e = k.extent.start.line, k.extent.end.line
            if k.kind == K.NAMESPACE:
                name = k.spelling or '(anonymous)'
                result['entities'].append({'kind': 'namespace', 'name': prefix + name, 'line': s, 'lines': e - s + 1})
                if depth < a.depth:
                    walk(k, depth + 1, prefix + name + '::')
            else:
                result['entities'].append({'kind': k.kind.name.lower(), 'name': prefix + k.spelling, 'line': s, 'lines': e - s + 1})
    walk(tu.cursor, 0, '')
    _emit(result)


def main(argv=None):
    p = argparse.ArgumentParser(prog='clang-split', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)

    s = sub.add_parser('doctor', help='show discovered libclang, resource dir and SDK')
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser('analyze', help='entity reference graph of a source')
    s.add_argument('source')
    s.add_argument('--build', required=True, help='build directory with compile_commands.json')
    s.add_argument('--alt-build', action='append', default=[], help='second configuration whose references are merged')
    s.add_argument('--class-line', type=int, help='graph one class\'s in-class members instead')
    s.add_argument('-o', '--output')
    s.set_defaults(fn=cmd_analyze)

    s = sub.add_parser('segment', help='cohesive contiguous segments within a line budget')
    s.add_argument('graph')
    s.add_argument('--max-lines', type=int, default=1500)
    s.add_argument('--penalty', type=float, default=1.0, help='cost per segment; higher means fewer files')
    s.add_argument('-o', '--output')
    s.set_defaults(fn=cmd_segment)

    s = sub.add_parser('plan', help='extract plan from a graph, segments and segment names')
    s.add_argument('graph')
    s.add_argument('segments')
    s.add_argument('names', help='JSON mapping segment index to file stem; equal stems merge')
    s.add_argument('--support', required=True, help='stem of the header declaring shared helpers')
    s.add_argument('--base', help='plan fields to copy (source, build, namespace, register, ...)')
    s.add_argument('-o', '--output')
    s.set_defaults(fn=cmd_plan)

    s = sub.add_parser('extract', help='move planned entities into new files')
    s.add_argument('plan')
    s.add_argument('--write', action='store_true', help='write files; default is a dry run')
    s.add_argument('--report')
    s.set_defaults(fn=cmd_extract)

    s = sub.add_parser('prune-includes', help='drop includes the source no longer uses')
    s.add_argument('plan')
    s.add_argument('--write', action='store_true')
    s.set_defaults(fn=cmd_prune)

    s = sub.add_parser('register', help='run the registration hook alone')
    s.add_argument('root')
    s.add_argument('spec', help='register spec, or a plan containing "register"')
    s.add_argument('--dry-run', action='store_true')
    s.set_defaults(fn=cmd_register)

    s = sub.add_parser('outline', help='top-level entities with line spans, or one class\'s members')
    s.add_argument('source')
    s.add_argument('--build', required=True)
    s.add_argument('--depth', type=int, default=2)
    s.add_argument('--class-line', type=int)
    s.set_defaults(fn=cmd_outline)

    a = p.parse_args(argv)
    for attr in ('source', 'build'):
        if getattr(a, attr, None):
            setattr(a, attr, os.path.abspath(getattr(a, attr)))
    a.alt_build = [os.path.abspath(b) for b in getattr(a, 'alt_build', [])]
    for attr in ('output', 'report', 'graph', 'segments', 'names', 'base', 'plan', 'spec'):
        if getattr(a, attr, None):
            setattr(a, attr, os.path.abspath(getattr(a, attr)))
    from .cx import SetupError
    try:
        a.fn(a)
    except SetupError as exc:
        print(json.dumps({'error': str(exc)}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
