"""Entity graph, cohesive segmentation and plan generation for one source.

analyze: every top-level entity (inside named or anonymous namespaces) with the
  same-file entities it references. Helpers in anonymous namespaces are also
  matched by name in the text, because uses inside templates and generic
  lambdas are not always resolved; same-named overloads are one node.
segment: contiguous runs of member definitions within a line budget, minimizing
  references that cross a cut (dynamic programming over source order).
plan: turns named segments into an extract plan. Helpers used by one file stay
  private to it; helpers shared by several are declared in the support header.
"""
import json, os, re

RECORD_KINDS = ('STRUCT_DECL', 'CLASS_DECL', 'CLASS_TEMPLATE')
METHOD_KINDS = ('CXX_METHOD', 'CONSTRUCTOR', 'DESTRUCTOR', 'CONVERSION_FUNCTION', 'FUNCTION_TEMPLATE')


def analyze(build, src, alt_builds=()):
    from .cx import parse, in_file, ci
    K = ci.CursorKind
    tu, errs = parse(build, src)
    if errs:
        raise SystemExit(f'parse errors: {[str(e) for e in errs[:3]]}')
    alt = []
    for b in alt_builds:
        atu, aerrs = parse(b, src)
        if aerrs:
            raise SystemExit(f'parse errors in {b}: {[str(e) for e in aerrs[:3]]}')
        alt.append(atu)
    ents, seen = [], {}

    def collect(c, anon):
        for k in c.get_children():
            if not in_file(k, src):
                continue
            if k.kind == K.NAMESPACE:
                collect(k, anon or k.spelling == '')
                continue
            if k.kind in (K.USING_DECLARATION, K.USING_DIRECTIVE, K.NAMESPACE_ALIAS):
                continue
            key = k.spelling or k.kind.name
            if key in seen:
                key = f'{key}@{k.extent.start.line}'
            seen[key] = True
            ents.append((key, k, anon))

    collect(tu.cursor, False)
    spans = sorted((k.extent.start.offset, k.extent.end.offset, key) for key, k, _ in ents)

    def owner(off):
        for a, b, key in spans:
            if a <= off <= b:
                return key
        return None

    lines = open(src).read().split('\n')
    helper_names = {}
    for key, k, anon in ents:
        if anon:
            helper_names.setdefault(key.split('@')[0], []).append(key)
    word = re.compile(r'\b(' + '|'.join(re.escape(n) for n in helper_names if n and not n.isupper()) + r')\b') if helper_names else None
    alt_index = {}
    for atu in alt:
        def acollect(c):
            for k in c.get_children():
                if not in_file(k, src):
                    continue
                if k.kind == K.NAMESPACE:
                    acollect(k)
                    continue
                alt_index.setdefault((k.spelling, k.extent.start.offset), []).append(k)
        acollect(atu.cursor)
    graph = {}
    for key, k, anon in ents:
        refs = set()
        walks = [k] + alt_index.get((k.spelling, k.extent.start.offset), [])
        for x in (x for w in walks for x in w.walk_preorder()):
            r = x.referenced
            if r is None or r.location.file is None or not in_file(r, src):
                continue
            o = owner(r.extent.start.offset)
            if o and o != key:
                refs.add(o)
        if word is not None:
            text = '\n'.join(lines[k.extent.start.line - 1:k.extent.end.line])
            for m in set(word.findall(text)):
                for h in helper_names[m]:
                    if h != key:
                        refs.add(h)
        graph[key] = {'line': k.extent.start.line, 'end': k.extent.end.line, 'helper': anon,
                      'kind': k.kind.name, 'refs': sorted(refs)}
    return graph


def segment(g, max_lines, penalty=1.0):
    methods = [k for k in sorted(g, key=lambda k: g[k]['line']) if not g[k]['helper'] and g[k]['kind'] in METHOD_KINDS]
    idx = {k: i for i, k in enumerate(methods)}
    size = [g[k]['end'] - g[k]['line'] + 1 for k in methods]
    adj = [set() for _ in methods]
    for k in methods:
        for r in g[k]['refs']:
            if r in idx:
                adj[idx[k]].add(idx[r])
                adj[idx[r]].add(idx[k])
    n = len(methods)
    pre = [0]
    for s_ in size:
        pre.append(pre[-1] + s_)
    best = [float('inf')] * (n + 1)
    cut = [0] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            if pre[j] - pre[i] > max_lines and j - i > 1:
                break
            inside = range(i, j)
            leaving = sum(1 for a in inside for b in adj[a] if not (i <= b < j))
            c = best[i] + leaving / 2 + penalty
            if c < best[j]:
                best[j], cut[j] = c, i
    segs, j = [], n
    while j > 0:
        i = cut[j]
        segs.append(methods[i:j])
        j = i
    segs.reverse()
    return [{'index': si, 'first_line': g[s_[0]]['line'], 'last_line': g[s_[-1]]['end'],
             'lines': sum(g[k]['end'] - g[k]['line'] + 1 for k in s_), 'entities': s_}
            for si, s_ in enumerate(segs)]


def plan(g, segs, names, support, base):
    segs = [s['entities'] if isinstance(s, dict) else s for s in segs]
    names = {str(k): v for k, v in names.items()}
    home = {}
    for si, s_ in enumerate(segs):
        for k in s_:
            home[k] = names[str(si)]
    order = sorted(g, key=lambda k: g[k]['line'])
    # Records defined here (often a class's nested types, defined out of class)
    # are needed by every member file: they go to the support header.
    for k in order:
        if not g[k]['helper'] and g[k]['kind'] in RECORD_KINDS and k not in home:
            home[k] = support
    # Other non-helper, non-method entities (namespace-scope statics) go with the next method.
    pending = []
    for k in order:
        if k in home:
            for p in pending:
                home[p] = home[k]
            pending = []
        elif not g[k]['helper']:
            pending.append(k)
    for p in pending:
        home[p] = names[str(len(segs) - 1)]
    users = {k: set() for k in g}
    for k, v in g.items():
        for r in v['refs']:
            if r in users:
                users[r].add(k)
    helpers = [k for k in order if g[k]['helper']]
    place = {}
    for _ in range(20):
        changed = False
        for h in helpers:
            files = set()
            for u in users[h]:
                files.add(place.get(u) if g[u]['helper'] else home.get(u))
            files.discard(None)
            want = files.pop() if len(files) == 1 else (support if files else support)
            if place.get(h) != want:
                place[h], changed = want, True
        if not changed:
            break
    # Overloads share a name, so a use matched by text cannot tell them apart:
    # they move together, into the support header when their users disagree.
    by_name = {}
    for h in helpers:
        by_name.setdefault(h.split('@')[0], []).append(h)
    for same in by_name.values():
        targets = {place[h] for h in same}
        if len(targets) > 1:
            for h in same:
                place[h] = support
    groups = {}
    for k in order:
        if g[k]['kind'] == 'STATIC_ASSERT' or k.split('@')[0] == 'STATIC_ASSERT':
            continue  # stays in the source beside what it checks
        if g[k]['helper']:
            stem = place[k]
            key = 'entities' if stem == support else 'private'
        else:
            stem = home[k]
            key = 'entities' if g[k]['kind'] in RECORD_KINDS else 'source_only'
        groups.setdefault(stem, {'stem': stem, 'entities': [], 'private': [], 'source_only': []})[key].append(k)
    base = dict(base)
    base['groups'] = []
    if support in groups:
        sg = groups.pop(support)
        sg['doc'] = base.get('support_doc', '')
        base['groups'].append(sg)
    for stem, grp in groups.items():
        grp['header'] = False
        base['groups'].append(grp)
    sizes = {}
    for k in order:
        stem = place.get(k) if g[k]['helper'] else home[k]
        sizes[stem] = sizes.get(stem, 0) + g[k]['end'] - g[k]['line'] + 1
    return base, sizes



def analyze_class(build, src, line):
    """Graph of one class's in-class member definitions, for segmenting before outlining."""
    from .cx import parse, in_file, ci
    from .outliner import is_outlinable
    K = ci.CursorKind
    tu, errs = parse(build, src)
    if errs:
        raise SystemExit(f'parse errors: {[str(e) for e in errs[:3]]}')
    cls = next((k for k in tu.cursor.walk_preorder()
                if k.kind in (K.CLASS_DECL, K.STRUCT_DECL) and k.is_definition() and in_file(k, src)
                and k.extent.start.line == line), None)
    if cls is None:
        raise SystemExit(f'no class definition starts on line {line}')
    methods = [m for m in cls.get_children() if is_outlinable(m) or m.kind == K.FUNCTION_TEMPLATE]
    keys, by_name = [], {}
    for m in methods:
        key = m.spelling if m.spelling not in by_name else f'{m.spelling}@{m.extent.start.line}'
        by_name.setdefault(m.spelling, []).append(key)
        keys.append(key)
    graph = {}
    for key, m in zip(keys, methods):
        refs = set()
        for k in m.walk_preorder():
            r = k.referenced
            if r is None or r.semantic_parent is None or r.semantic_parent.hash != cls.hash:
                continue
            refs.update(x for x in by_name.get(r.spelling, []) if x != key)
        graph[key] = {'line': m.extent.start.line, 'end': m.extent.end.line, 'helper': False,
                      'kind': m.kind.name, 'refs': sorted(refs)}
    return graph
