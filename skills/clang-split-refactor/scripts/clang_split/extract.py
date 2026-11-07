"""Move top-level entities of one source into per-responsibility header/source pairs.

Driven by a plan (see references/plan-schema.md). Without write=True nothing is
changed and only the report is produced.
"""
import json, os, re, sys
import subprocess
from . import outliner
from .cx import parse, in_file, ci, git_root, include_dirs, defined_macros, is_system, is_stdlib, parse_args_for
from .outliner import outline_record, function_parts, is_outlinable, body_of, dedent, indent_of, toks
from .includes import closure_index

K = ci.CursorKind
DIRECTIVE = re.compile(rb'^[ \t]*#[ \t]*(if|ifdef|ifndef|elif|else|endif)\b(.*)$')


def _type_decl(t):
    """The class a type needs complete for member access or a value: pointee of pointers/references."""
    seen = 0
    while t is not None and seen < 4 and t.kind in (ci.TypeKind.POINTER, ci.TypeKind.LVALUEREFERENCE, ci.TypeKind.RVALUEREFERENCE):
        t = t.get_pointee()
        seen += 1
    if t is None:
        return None
    d = t.get_declaration()
    if d is None or d.kind == K.NO_DECL_FOUND:
        return None
    return d


def implied_refs(cursors):
    """Each cursor's referenced declaration, plus complete types its expression needs."""
    for k in cursors:
        yield k, k.referenced
        if k.kind == K.MEMBER_REF_EXPR:
            kids = list(k.get_children())
            # Look through implicit casts: a derived-to-base conversion needs
            # the derived type complete, and only the inner expression names it.
            depth = 0
            while kids and depth < 6:
                d = _type_decl(kids[0].type)
                if d is not None:
                    yield k, d
                if kids[0].kind != K.UNEXPOSED_EXPR:
                    break
                kids = list(kids[0].get_children())
                depth += 1
        elif k.kind == K.UNEXPOSED_EXPR:
            # An implicit conversion of a pointer or reference to a base needs
            # the operand's class complete.
            for kid in k.get_children():
                d = _type_decl(kid.type)
                if d is not None:
                    yield k, d
        elif k.kind == K.VAR_DECL:
            d = _type_decl(k.type) if k.type.kind not in (ci.TypeKind.POINTER, ci.TypeKind.LVALUEREFERENCE, ci.TypeKind.RVALUEREFERENCE) else None
            if d is not None:
                yield k, d


def condition_frames(lines):
    """For each 1-based line: tuple of frames (directive_line, branch) active there."""
    stack = []  # each: {'if': text, 'prior': [conds], 'cur': cond-text}
    frames = [()] * (len(lines) + 2)
    for i, ln in enumerate(lines, start=1):
        m = DIRECTIVE.match(ln)
        if m:
            kind, rest = m.group(1).decode(), m.group(2).decode().strip()
            if kind in ('if', 'ifdef', 'ifndef'):
                cond = {'if': rest, 'ifdef': f'defined({rest})', 'ifndef': f'!defined({rest})'}[kind]
                stack.append({'conds': [cond], 'text': ln.decode().strip(), 'branch': 0})
            elif kind == 'elif':
                stack[-1]['conds'].append(rest)
                stack[-1]['branch'] = len(stack[-1]['conds']) - 1
            elif kind == 'else':
                stack[-1]['branch'] = -1
            elif kind == 'endif':
                stack.pop()
            frames[i] = None  # directive line itself
            continue
        frames[i] = tuple(_frame_directive(f) for f in stack)
    return frames


def _frame_directive(f):
    conds, b = f['conds'], f['branch']
    if b == 0:
        # Keep the original spelling where possible.
        t = f['text']
        if t.startswith('#ifdef'):
            return f'#if defined({conds[0][8:-1]})'
        if t.startswith('#ifndef'):
            return f'#if !defined({conds[0][9:-1]})'
        return re.sub(r'^#\s*if\s+', '#if ', t)
    prior = conds if b == -1 else conds[:b]
    parts = [f'!({c})' for c in prior]
    if b != -1:
        parts.append(f'({conds[b]})')
    if len(prior) == 1 and b == -1:
        c = prior[0]
        m = re.fullmatch(r'defined\(([A-Za-z_0-9]+)\)', c)
        if m:
            return f'#if !defined({m.group(1)})'
        m = re.fullmatch(r'!defined\(([A-Za-z_0-9]+)\)', c)
        if m:
            return f'#if defined({m.group(1)})'
    return '#if ' + ' && '.join(parts)


def wrap(blocks, indent=''):
    """blocks: list of (frames, text). Merge adjacent same-frame blocks, emit #if nests."""
    out = []
    cur = ()
    for frames, text in blocks:
        # Close frames not shared.
        common = 0
        while common < len(cur) and common < len(frames) and cur[common] == frames[common]:
            common += 1
        for _ in range(len(cur) - common):
            out.append('#endif')
        for f in frames[common:]:
            out.append(f)
        if out and cur == frames and common == len(frames):
            out.append('')
        cur = frames
        out.append(text)
    for _ in range(len(cur)):
        out.append('#endif')
    return '\n'.join(out)


def dedent_all(text, tabs):
    return dedent(b'\n' + text, tabs)[1:]


def wrap_tight(blocks):
    out = []
    cur = ()
    for frames, text in blocks:
        common = 0
        while common < len(cur) and common < len(frames) and cur[common] == frames[common]:
            common += 1
        for _ in range(len(cur) - common):
            out.append('#endif')
        for f in frames[common:]:
            out.append(f)
        cur = frames
        out.append(text)
    for _ in range(len(cur)):
        out.append('#endif')
    return '\n'.join(out)


def leading_comment_start(lines, start_line):
    i = start_line - 1
    while i >= 1:
        s = lines[i - 1].strip()
        if s.startswith(b'//') or s.startswith(b'/*') or s.startswith(b'*'):
            i -= 1
            continue
        break
    return i + 1


def span_end_offset(data, c):
    """End offset including a trailing ';' of a declaration, and balanced directives."""
    e = c.extent.end.offset
    j = e
    while j < len(data) and data[j:j + 1] in (b' ', b'\t'):
        j += 1
    if data[j:j + 1] == b';':
        e = j + 1
    return balanced_end(data, line_start(data, c.extent.start.offset), e)


def balanced_end(data, start, end):
    """Extend `end` through the #endif of any conditional opened inside [start, end).

    libclang's extent stops at the active branch, so an initializer written as
    `#if A` / `x;` / `#else` / `y;` / `#endif` would otherwise be cut in half.
    """
    depth = 0
    for ln in data[start:end].split(b'\n'):
        m = DIRECTIVE.match(ln)
        if m:
            k = m.group(1)
            depth += 1 if k in (b'if', b'ifdef', b'ifndef') else -1 if k == b'endif' else 0
    pos = end
    while depth > 0:
        nl = data.find(b'\n', pos)
        if nl < 0:
            return len(data)
        pos = nl + 1
        eol = data.find(b'\n', pos)
        ln = data[pos:eol if eol >= 0 else len(data)]
        m = DIRECTIVE.match(ln)
        if m:
            k = m.group(1)
            depth += 1 if k in (b'if', b'ifdef', b'ifndef') else -1 if k == b'endif' else 0
        if depth == 0:
            return eol if eol >= 0 else len(data)
    return end


def line_start(data, off):
    return data.rfind(b'\n', 0, off) + 1


PLATFORM_MACROS = {'_WIN32', '_WIN64', '__APPLE__', '__linux__', '__unix__', '__ANDROID__', '__FreeBSD__',
                   '_MSC_VER', '__clang__', '__GNUC__', '__MINGW32__', '__EMSCRIPTEN__'}
HEADER_GLOBS = ['*.h', '*.hh', '*.hpp', '*.hxx', '*.inl']


def enclosing_namespace(c):
    parts = []
    p = c.semantic_parent
    while p is not None and p.kind != K.TRANSLATION_UNIT:
        if p.kind == K.NAMESPACE and p.spelling:
            parts.append(p.spelling)
        p = p.semantic_parent
    return '::'.join(reversed(parts))


def run(plan, write=False):
    base_dir = plan.get('_dir', os.getcwd())
    src = os.path.realpath(os.path.join(base_dir, plan['source']))
    build = os.path.join(base_dir, plan['build'])
    plan = dict(plan, alt_builds=[os.path.join(base_dir, b) for b in plan.get('alt_builds', [])],
                closures=os.path.join(base_dir, plan.get('closures', os.path.join(build, 'clang_split_closures.json'))))
    plan.setdefault('subdir', '')
    unit = plan.get('indent', '\t')
    unit = ' ' * unit if isinstance(unit, int) else unit
    outliner.UNIT = unit.encode()
    NS = int(plan.get('namespace_indent', 1))
    IND = unit * NS
    tu, errs = parse(build, src, detailed=True)
    if errs:
        raise SystemExit(f'parse errors: {errs[:3]}')
    data = open(src, 'rb').read()
    lines = data.split(b'\n')
    frames = condition_frames(lines)
    cache = closure_index(build, src, plan['closures'])
    sized = sorted(cache.items(), key=lambda kv: len(kv[1]))

    # Top-level entities.
    ents = {}
    def collect(c):
        for k in c.get_children():
            if not in_file(k, src):
                continue
            if k.kind == K.NAMESPACE:
                collect(k)
                continue
            key = k.spelling
            if key in ents:
                key = f'{k.spelling}@{k.extent.start.line}'
            ents[key] = k
    collect(tu.cursor)
    macros = [m for m in tu.cursor.get_children() if m.kind == K.MACRO_INSTANTIATION and in_file(m, src)]
    alt_tus = []
    for ab in plan.get('alt_builds', []):
        atu, aerrs = parse(ab, src, detailed=True)
        if aerrs:
            raise SystemExit(f'alt parse errors in {ab}: {aerrs[:3]}')
        alt_ents = {}
        def acollect(c):
            for k in c.get_children():
                if not in_file(k, src):
                    continue
                if k.kind == K.NAMESPACE:
                    acollect(k)
                    continue
                alt_ents[(k.spelling, k.extent.start.offset)] = k
        acollect(atu.cursor)
        amacros = [m for m in atu.cursor.get_children() if m.kind == K.MACRO_INSTANTIATION and in_file(m, src)]
        alt_tus.append((alt_ents, amacros))

    owner = {}  # entity key -> group stem
    for g in plan['groups']:
        for n in g['entities'] + g.get('private', []) + g.get('source_only', []):
            if n not in ents:
                raise SystemExit(f'unknown entity {n}')
            owner[n] = g['stem']
    ext_of = {n: (ents[n].extent.start.offset, ents[n].extent.end.offset) for n in owner}
    source_only_names = {n for g_ in plan['groups'] for n in g_.get('source_only', [])}
    header_of = {g_['stem']: g_.get('header', True) for g_ in plan['groups']}

    def owner_of_offset(off):
        for n, (a, b) in ext_of.items():
            if a <= off <= b:
                return n
        return None

    pargs, _ = parse_args_for(build, src)
    idirs = include_dirs(pargs)
    root = os.path.realpath(os.path.join(base_dir, plan['project_root']) if plan.get('project_root') else git_root(src))
    excluded = [os.path.realpath(os.path.join(root, d)) for d in plan.get('exclude_dirs', [])]
    excluded += [os.path.realpath(b) for b in [build] + plan['alt_builds']]
    def project_include(f):
        if not f.startswith(root + os.sep) or is_system(f) or any(f.startswith(d + os.sep) for d in excluded):
            return None
        if any(part in f for part in ('/_deps/', '/.cpm-cache/', '/vcpkg_installed/', '/third_party/')):
            return None
        here = os.path.realpath(os.path.dirname(src))
        if os.path.dirname(f) == here:
            return f'"{os.path.basename(f)}"'  # beside the source, as the source spells it
        best = None
        for d in idirs:
            d = os.path.realpath(d)
            if f.startswith(d + '/'):
                r = f[len(d) + 1:]
                if best is None or len(r) < len(best):
                    best = r
        return f'"{best}"' if best else None

    from .stdmap import std_header, qt_header
    import glob as _glob
    namespace = plan.get('namespace')
    if namespace is None:
        first = next((n for g_ in plan['groups'] for n in g_['entities'] + g_.get('private', []) + g_.get('source_only', [])), None)
        namespace = enclosing_namespace(ents[first]) if first else ''
    ns_open = [f'namespace {namespace} {{'] if namespace else []
    ns_close = ['}'] if namespace else []
    guard_prefix = plan.get('guard_prefix', '')
    qt_dirs = []
    for i, a in enumerate(pargs):
        if a == '-iframework':
            qt_dirs += _glob.glob(os.path.join(pargs[i + 1], 'Qt*.framework', 'Headers'))
    for d in idirs:
        for m in ('QtCore', 'QtGui', 'QtWidgets', 'QtNetwork'):
            for cand in (os.path.join(d, m), os.path.join(d, m + '.framework', 'Headers')):
                if os.path.isdir(cand):
                    qt_dirs.append(cand)
        if os.path.basename(d.rstrip('/')) == 'Headers' or os.path.basename(d.rstrip('/')).startswith('Qt'):
            qt_dirs.append(d)

    # Headers that #define a macro the source tests in a directive: a moved
    # entity whose guard or text names that macro must include the header, or
    # `#if NAME` silently becomes false in the new file.
    tested = set()
    for ln_ in lines:
        m_ = DIRECTIVE.match(ln_)
        if m_ and m_.group(1) != b'endif':
            tested |= set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', m_.group(2).decode('utf-8', 'replace'))) - {'defined'}
    macro_header = {}
    if tested:
        pattern = r'^\s*#\s*define\s+(' + '|'.join(sorted(tested)) + r')\b'
        out_ = subprocess.run(['git', '-C', root, 'grep', '-n', '-E', pattern, '--'] + HEADER_GLOBS,
                              capture_output=True, text=True).stdout
        for line_ in out_.splitlines():
            path_, _, rest_ = line_.split(':', 2)
            m_ = re.search(r'#\s*define\s+([A-Za-z_][A-Za-z_0-9]*)', rest_)
            full_ = os.path.realpath(os.path.join(root, path_))
            if m_ and full_ != src and not any(full_.startswith(d + os.sep) for d in excluded):
                macro_header.setdefault(m_.group(1), full_)
    # Only command-line and platform macros may guard a generated include:
    # their value is the same in every file of the build.
    SAFE_GUARDS = PLATFORM_MACROS | set(plan.get('guard_macros', []))
    for b_ in [build] + plan['alt_builds']:
        SAFE_GUARDS |= defined_macros(parse_args_for(b_, src)[0])
    def safe_frames(fr_):
        out_ = []
        for f_ in fr_:
            names_ = set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', f_)) - {'if', 'defined'}
            if not names_ <= SAFE_GUARDS:
                break
            out_.append(f_)
        return tuple(out_)

    # Guards the source itself put on its includes; a generated include of the
    # same header is never less guarded than the original was.
    root_inc_frames = {}
    root_direct = []
    for i_, ln_ in enumerate(lines, start=1):
        m0_ = re.match(rb'^[ \t]*#[ \t]*include[ \t]*([<"][^>"]+[>"])', ln_)
        if m0_:
            root_direct.append(m0_.group(1).decode())
        m_ = re.match(rb'^[ \t]*#[ \t]*include[ \t]*([<"][^>"]+[>"])', ln_)
        if m_ and frames[i_]:
            root_inc_frames[m_.group(1).decode()] = safe_frames(frames[i_])

    pfx0_ = f"{plan['subdir']}/" if plan['subdir'] else ''
    generated_ = {f'"{pfx0_}{g_[k_]}.hpp"' for g_ in plan['groups'] for k_ in ('stem', 'hoist_stem') if g_.get(k_)}
    original_quoted = [i_ for i_ in root_direct if i_.startswith('"') and i_ not in generated_
                       and not (plan['subdir'] and i_.startswith('"' + plan['subdir'] + '/'))]
    text_type_header = {}
    _counts = {}
    for inc_ in root_direct:
        if not inc_.startswith('"') or (plan['subdir'] and inc_.startswith('"' + plan['subdir'] + '/')):
            continue
        for f_ in cache.get(inc_, [])[:0] or []:
            pass
        cand_ = None
        for d_ in idirs:
            pth_ = os.path.join(d_, inc_.strip('"'))
            if os.path.exists(pth_):
                cand_ = os.path.realpath(pth_)
                break
        if cand_ is None:
            pth_ = os.path.join(os.path.dirname(src), inc_.strip('"'))
            if os.path.exists(pth_):
                cand_ = os.path.realpath(pth_)
        if cand_ is None:
            continue
        for nm_ in set(re.findall(r'^\s*(?:class|struct|enum class)\s+([A-Za-z_]\w*)\b(?!\s*;)', open(cand_).read(), re.M)):
            _counts[nm_] = _counts.get(nm_, 0) + 1
            text_type_header[nm_] = cand_
    text_type_header = {k_: v_ for k_, v_ in text_type_header.items() if _counts[k_] == 1 and len(k_) > 8}

    qualify = plan.get('qualify', {})
    def qualify_text(t):
        for name, q in qualify.items():
            t = re.sub(rf'(?<![:\w]){re.escape(name)}\b', q, t)
        return t

    removals = []
    report = {'notes': [], 'files': {}}
    target_tabs = NS
    for g in plan['groups']:
        stem = g['stem']
        header_blocks, source_blocks, private_blocks = [], [], []
        unit_of_name = {}
        for u, names in g.get('method_files', {}).items():
            for nm in names:
                unit_of_name[nm] = u
        default_unit = g.get('default_unit', stem)
        def route(name, line):
            return unit_of_name.get(f'{name}@{line}') or unit_of_name.get(name, default_unit)
        units = {default_unit: []}
        unit_refs = {default_unit: set()}
        header_refs = set()
        hoist_blocks, hoist_ranges, hoist_refs = [], [], set()
        ref_frames = {}
        def note_frames(key, line):
            fr2 = frames[line] or ()
            if key in ref_frames:
                old = ref_frames[key]
                n = 0
                while n < len(old) and n < len(fr2) and old[n] == fr2[n]:
                    n += 1
                ref_frames[key] = old[:n]
            else:
                ref_frames[key] = fr2
        header_offsets, body_ranges = [], []  # body_ranges: (a, b, unit)
        for n in g.get('private', []) + g['entities'] + g.get('source_only', []):
            c = ents[n]
            private = n in g.get('private', [])
            sline = leading_comment_start(lines, c.extent.start.line)
            soff = sum(len(l) + 1 for l in lines[:sline - 1])
            eoff = span_end_offset(data, c)
            comment = data[soff:line_start(data, c.extent.start.offset)]
            cur_indent = indent_of(data, c.extent.start.offset)
            fr = frames[c.extent.start.line]
            removals.append((soff, eoff, n))
            lead = dedent(b'\n' + comment, cur_indent - (2 if private else 1))[1:]
            if private:
                text = data[line_start(data, c.extent.start.offset):eoff]
                body = lead + dedent_all(text, cur_indent - NS - 1)
                private_blocks.append((fr, body.decode().rstrip('\n')))
                body_ranges.append((c.extent.start.offset, c.extent.end.offset, default_unit))
                continue
            if c.kind in (K.CXX_METHOD, K.CONSTRUCTOR, K.DESTRUCTOR) and c.is_definition() or n in g.get('source_only', []):
                # Already out of line: source only.
                u = unit_of_name.get(c.spelling, default_unit)
                text = data[line_start(data, c.extent.start.offset):eoff]
                units.setdefault(u, []).append((fr, (lead + dedent_all(text, cur_indent - NS)).decode().rstrip('\n')))
                body_ranges.append((c.extent.start.offset, c.extent.end.offset, u))
                continue
            if c.kind in (K.CLASS_DECL, K.STRUCT_DECL) and c.is_definition():
                qual = c.spelling
                par = c.semantic_parent
                while par is not None and par.kind in (K.CLASS_DECL, K.STRUCT_DECL):
                    qual = par.spelling + '::' + qual
                    par = par.semantic_parent
                hoisted = []
                cls, defs = outline_record(tu, c, data, qual, target_tabs, notes=report['notes'], move_comments=g.get('comments_follow_definitions', False), hoist=set(g.get('hoist', [])), hoisted=hoisted)
                for hm in hoisted:
                    hstart = leading_comment_start(lines, hm.extent.start.line)
                    hsoff = sum(len(l) + 1 for l in lines[:hstart - 1])
                    hcomment = data[hsoff:line_start(data, hm.extent.start.offset)]
                    hind = indent_of(data, hm.extent.start.offset)
                    hcls, hdefs = outline_record(tu, hm, data, hm.spelling, target_tabs, notes=report['notes'])
                    hpre = data[line_start(data, hm.extent.start.offset):hm.extent.start.offset]
                    htext2 = dedent(b'\n' + hcomment, hind - NS)[1:] + dedent_all(hpre + hcls, hind - NS) + b';'
                    hoist_blocks.append((frames[hm.extent.start.line], htext2.decode()))
                    for d in hdefs:
                        units.setdefault(g['hoist_stem'], []).append((frames[d['line']], IND + d['text'].decode()))
                    hoist_ranges.append((hm.extent.start.offset, hm.extent.end.offset))
                pre = data[line_start(data, c.extent.start.offset):c.extent.start.offset]
                htext = lead + dedent_all(pre + cls, cur_indent - NS) + b';'
                header_blocks.append((fr, htext.decode()))
                for d in defs:
                    dfr = frames[d['line']]
                    u = route(d['name'], d['line'])
                    units.setdefault(u, []).append((dfr, IND + d['text'].decode()))
                for m in c.walk_preorder():
                    if m.kind in (K.CXX_METHOD, K.CONSTRUCTOR, K.DESTRUCTOR, K.CONVERSION_FUNCTION) and is_outlinable(m):
                        b = body_of(m)
                        u = route(m.spelling, m.extent.start.line)
                        # The ctor-initializer belongs to the source too.
                        body_ranges.append((b.extent.start.offset, b.extent.end.offset, u))
            elif c.kind == K.FUNCTION_DECL and c.is_definition():
                tbefore = [t.spelling for t in toks(tu, c.extent.start, c.location)]
                btoks = [t.spelling for t in toks(tu, c.location, body_of(c).extent.start)]
                deduced = 'auto' in [t for t in tbefore if t not in ('[', ']', 'nodiscard', 'maybe_unused', ',')][:1] and '->' not in btoks
                if 'constexpr' in tbefore or 'consteval' in tbefore or deduced:
                    text = data[line_start(data, c.extent.start.offset):eoff]
                    if deduced and 'constexpr' not in tbefore and 'inline' not in tbefore:
                        # A deduced return type needs the body where it is used; inline keeps one definition.
                        ind_ = text[:len(text) - len(text.lstrip(b' \t'))]
                        body_ = text.lstrip(b' \t')
                        m_ = re.match(rb'((?:\[\[[^\]]*\]\]\s*)*)', body_)
                        text = ind_ + body_[:m_.end()] + b'inline ' + body_[m_.end():]
                    header_blocks.append((fr, (lead + dedent_all(text, cur_indent - NS)).decode()))
                    report['notes'].append(f'{"deduced-return" if deduced else "constexpr"} function {n} kept whole in {stem}.hpp')
                    continue
                decl, definition, _ = function_parts_free(tu, c, data)
                pre = data[line_start(data, c.extent.start.offset):c.extent.start.offset]
                header_blocks.append((fr, (lead + dedent_all(pre + decl, cur_indent - NS)).decode()))
                u = unit_of_name.get(c.spelling, default_unit)
                units.setdefault(u, []).append((fr, IND + dedent(definition, cur_indent - NS).decode()))
                b = body_of(c)
                body_ranges.append((b.extent.start.offset, b.extent.end.offset, u))
            else:
                text = data[line_start(data, c.extent.start.offset):eoff]
                if c.kind == K.VAR_DECL:
                    vt = [t_.spelling for t_ in toks(tu, c.extent.start, c.location)]
                    if not ({'constexpr', 'extern', 'inline', 'static', 'thread_local'} & set(vt)) and not c.type.is_const_qualified():
                        # A mutable variable defined in a header needs inline to stay one object.
                        ind_ = text[:len(text) - len(text.lstrip(b' \t'))]
                        text = ind_ + b'inline ' + text.lstrip(b' \t')
                        report['notes'].append(f'mutable variable {n} made inline in {stem}.hpp')
                header_blocks.append((fr, (lead + dedent_all(text, cur_indent - NS)).decode()))
        # References: header vs body.
        def body_unit(off):
            for a, b, u in body_ranges:
                if a <= off <= b:
                    return u
            return None
        group_names = g.get('private', []) + g['entities'] + g.get('source_only', [])
        cross = {'header': set()}
        def all_walks(n):
            yield from ents[n].walk_preorder()
            key = (ents[n].spelling, ents[n].extent.start.offset)
            for alt_ents, _ in alt_tus:
                if key in alt_ents:
                    yield from alt_ents[key].walk_preorder()
        for n in group_names:
            # A definition outside its class or header includes its declaration.
            canon = ents[n].canonical
            if canon is not None and canon.location.file is not None:
                cf = os.path.realpath(canon.location.file.name)
                if cf != src:
                    header_refs.add(cf) if n not in g.get('source_only', []) and ents[n].kind not in (K.CXX_METHOD, K.CONSTRUCTOR, K.DESTRUCTOR) else unit_refs.setdefault(unit_of_name.get(ents[n].spelling, default_unit), set()).add(cf)
            for k, r in implied_refs(all_walks(n)):
                if r is None or r.location.file is None:
                    continue
                if r.kind in (K.NAMESPACE, K.NAMESPACE_ALIAS):
                    continue
                rd = r.get_definition()
                if rd is not None and rd.location.file is not None:
                    r = rd
                where = body_unit(k.location.offset) or ('header' if n not in g.get('private', []) else default_unit)
                if where == 'header' and any(a_ <= k.location.offset <= b_ for a_, b_ in hoist_ranges):
                    where = 'hoist'
                f = os.path.realpath(r.location.file.name)
                if f == src:
                    o = owner_of_offset(r.extent.start.offset)
                    if o and owner[o] != stem and (o in source_only_names or not header_of.get(owner[o], True)):
                        # A definition elsewhere: include where it is declared.
                        cdecl = r.canonical
                        if cdecl is not None and cdecl.location.file is not None and os.path.realpath(cdecl.location.file.name) != src:
                            (header_refs if where == 'header' else unit_refs.setdefault(where, set())).add(os.path.realpath(cdecl.location.file.name))
                    elif o and owner[o] != stem:
                        cross.setdefault(where, set()).add(owner[o])
                    elif o is None and not (ents[n].extent.start.offset <= r.extent.start.offset <= ents[n].extent.end.offset):
                        # Something staying in the source: must not be needed.
                        rn = r.spelling
                        report['notes'].append(f'{stem}: {n} references {rn} that stays in the source (line {r.location.line})')
                    continue
                canon = std_header(r) or qt_header(r, qt_dirs)
                if canon:
                    (header_refs if where == 'header' else hoist_refs if where == 'hoist' else unit_refs.setdefault(where, set())).add('INC:' + canon)
                    note_frames('INC:' + canon, k.location.line)
                    continue
                note_frames(f, k.location.line)
                if is_system(f):
                    report.setdefault('std_fallback', {}).setdefault(stem, set()).add(r.displayname)
                    continue
                (header_refs if where == 'header' else hoist_refs if where == 'hoist' else unit_refs.setdefault(where, set())).add(f)
            a, b = ents[n].extent.start.offset, ents[n].extent.end.offset
            etext = data[a:b].decode('utf-8', 'replace') + ' '.join(frames[ents[n].extent.start.line] or ())
            for mac_, hdr_ in macro_header.items():
                if hdr_ != src and re.search(rf'\b{mac_}\b', etext):
                    wu_ = body_unit(a) if ents[n].kind in (K.CXX_METHOD, K.CONSTRUCTOR, K.DESTRUCTOR) else None
                    header_refs.add(hdr_)
                    ref_frames[hdr_] = ()
            for m in macros + [x for _, am in alt_tus for x in am]:
                if a <= m.location.offset <= b and m.referenced is not None and m.referenced.location.file is not None:
                    f = os.path.realpath(m.referenced.location.file.name)
                    if f != src:
                        wu = body_unit(m.location.offset)
                        (unit_refs.setdefault(wu, set()) if wu else header_refs).add(f)
        for a_, b_, u_ in body_ranges:
            body_text_ = data[a_:b_].decode('utf-8', 'replace')
            for nm_, hf_ in text_type_header.items():
                if hf_ != src and re.search(rf'\b{nm_}\b', body_text_):
                    unit_refs.setdefault(u_, set()).add(hf_)
        inc_frames = {}
        project_file_of = {}
        def choose(inc, f, chosen):
            fr2 = safe_frames(ref_frames.get(f, ()))
            if inc in inc_frames:
                old = inc_frames[inc]
                n = 0
                while n < len(old) and n < len(fr2) and old[n] == fr2[n]:
                    n += 1
                inc_frames[inc] = old[:n]
            else:
                inc_frames[inc] = fr2
            if inc not in chosen:
                chosen.append(inc)
        def pick(files):
            chosen, unresolved = [], []
            for f in sorted(files):
                if f.startswith('INC:'):
                    choose(f[4:], f, chosen)
                    continue
                rel = project_include(f)
                if rel:
                    # Keep the source's include vocabulary: reach the file through
                    # the smallest original include that brings it in, as the
                    # original spells it. Boundary rules may allow only that one.
                    via_ = [i_ for i_ in original_quoted if f in cache.get(i_, ())]
                    if via_:
                        rel = min(via_, key=lambda i_: len(cache[i_]))
                    project_file_of[rel] = f
                    choose(rel, f, chosen)
                    continue
                for inc, closure in sized:
                    if is_system(f) and not (inc.startswith('<') and '.' not in inc and not inc.startswith('<Q')):
                        continue
                    if ('/Qt' in f or '/qt' in f) and not is_stdlib(f) and not (inc.startswith('<Q') or inc.startswith('<q')):
                        continue
                    if f in closure:
                        choose(inc, f, chosen)
                        break
                else:
                    unresolved.append(f)
            return chosen, unresolved
        if hoist_blocks:
            hoinc, _ = pick(hoist_refs)
            hname = (f"{plan['subdir']}/" if plan['subdir'] else '') + f"{g['hoist_stem']}.hpp"
            hguard = guard_prefix + re.sub(r'[^A-Za-z0-9]', '_', hname).upper()
            header_refs.add('INC:"' + hname + '"')
            inc_frames['"' + hname + '"'] = ()
        hinc, hun = pick(header_refs)
        for u in hun:
            report['notes'].append(f'{stem}: unresolved include for {u}')
        sub = plan['subdir']
        pfx = f'{sub}/' if sub else ''
        hdr_name = f'{pfx}{stem}.hpp'
        guard = guard_prefix + re.sub(r'[^A-Za-z0-9]', '_', hdr_name).upper()
        def inc_lines(incs, own):
            proj = sorted(i for i in incs if i.startswith('"'))
            qt = sorted(i for i in incs if i.startswith('<Q') or i.startswith('<q'))
            std = sorted(i for i in incs if i.startswith('<') and i not in qt)
            out = []
            if own:
                out.append(f'#include "{own}"')
                out.append('')
            for i_ in list(incs):
                if root_inc_frames.get(i_):
                    inc_frames[i_] = root_inc_frames[i_]
                    continue
                f_ = project_file_of.get(i_)
                if f_ and not inc_frames.get(i_):
                    # Brought in only through guarded root includes: same guard.
                    via = [r_ for r_ in root_direct if not (plan['subdir'] and r_.startswith('"' + plan['subdir'] + '/')) and f_ in cache.get(r_, ())]
                    if via and all(root_inc_frames.get(r_) for r_ in via):
                        inc_frames[i_] = root_inc_frames[via[0]]
            cond = []
            for grp in (proj, qt, std):
                plain = [i for i in grp if not inc_frames.get(i)]
                cond += [i for i in grp if inc_frames.get(i)]
                if plain:
                    out += [f'#include {i}' for i in plain]
                    out.append('')
            if cond:
                blocks = sorted(((inc_frames[i], f'{unit}#include {i}') for i in cond), key=lambda b: b[0])
                merged = []
                for fr3, t in blocks:
                    merged.append((fr3, t))
                out.append(wrap_tight(merged))
                out.append('')
            return out
        if hoist_blocks:
            htxt = [f'#ifndef {hguard}', f'#define {hguard}'] + inc_lines(hoinc, None)
            if g.get('hoist_doc'):
                htxt += ['// ' + l if l else '//' for l in g['hoist_doc'].split('\n')]
            htxt += ns_open + [qualify_text(wrap(hoist_blocks))] + ns_close + ['#endif', '']
            if write:
                open(os.path.join(os.path.dirname(src), hname), 'w').write('\n'.join(htxt))
            report.setdefault('hoisted', {})[g['hoist_stem']] = len(htxt)
        hcross = sorted(f'"{pfx}{x}.hpp"' for x in cross['header'])
        header = [f'#ifndef {guard}', f'#define {guard}'] + inc_lines(hcross + hinc, None)
        if g.get('doc'):
            header += ['// ' + l if l else '//' for l in g['doc'].split('\n')]
        header += ns_open + [qualify_text(wrap(header_blocks))] + ns_close + ['#endif', '']
        sources = {}
        if '__root__' in units:
            # Kept verbatim: the root keeps its own using-declarations.
            root_text = wrap(units.pop('__root__')).rstrip('\n') + '\n'
            # Replace the first (class) entity's span with the definitions kept in the root.
            for i, r in enumerate(removals):
                if r[2] == g['entities'][0]:
                    removals[i] = (r[0], r[1], r[2], root_text.encode())
        for u, blocks in units.items():
            if not blocks and not (u == default_unit and private_blocks):
                continue
            sinc, sun = pick(unit_refs.get(u, set()))
            if g.get('header', True):
                sinc = [i for i in sinc if i not in hinc]
            else:
                # No header carries the group's declarations' includes: each unit takes them.
                sinc, sun2 = pick(unit_refs.get(u, set()) | header_refs)
                sun = sorted(set(sun) | set(sun2))
            for x in sun:
                report['notes'].append(f'{u}: unresolved include for {x}')
            scross = sorted(f'"{pfx}{x}.hpp"' for x in cross.get(u, set()) - (cross['header'] if g.get('header', True) else set()))
            source = inc_lines(scross + sinc, hdr_name if g.get('header', True) else None)
            source += ns_open
            if u == default_unit and private_blocks:
                source += [IND + 'namespace {', qualify_text(wrap(private_blocks)), IND + '}', '']
            source += [qualify_text(wrap(blocks)).rstrip('\n')] + ns_close + ['']
            sources[u] = source
        report['files'][stem] = {'header_lines': len('\n'.join(header).split('\n')), 'cross_header': sorted(cross['header']),
                                 'sources': {u: len('\n'.join(t).split('\n')) for u, t in sources.items()}}
        if write:
            if sub:
                os.makedirs(os.path.join(os.path.dirname(src), sub), exist_ok=True)
            if g.get('header', True):
                open(os.path.join(os.path.dirname(src), hdr_name), 'w').write('\n'.join(header))
            for u, t in sources.items():
                open(os.path.join(os.path.dirname(src), f'{pfx}{u}.cpp'), 'w').write('\n'.join(t))
    # Remove spans from the source.
    removals.sort()
    out = bytearray()
    pos = 0
    for r in removals:
        a, b = r[0], r[1]
        out += data[pos:a]
        if len(r) > 3:
            out += r[3]
        pos = b
        # swallow the rest of the line and one blank line
        if data[pos:pos + 1] == b'\n':
            pos += 1
        if data[pos:pos + 1] == b'\n':
            pos += 1
    out += data[pos:]
    text = bytes(out)
    if plan.get('source_includes', True):
        # The remaining source includes every new header; prune-includes later
        # drops the ones it does not use.
        pfx_ = f"{plan['subdir']}/" if plan['subdir'] else ''
        new_ = [f'#include "{pfx_}{g_["stem"]}.hpp"'.encode() for g_ in plan['groups'] if g_.get('header', True)]
        new_ = [n_ for n_ in new_ if n_ not in text]
        if new_:
            depth_, last_ = 0, None
            src_lines_ = text.split(b'\n')
            for i_, ln_ in enumerate(src_lines_):
                m_ = DIRECTIVE.match(ln_)
                if m_:
                    k_ = m_.group(1)
                    depth_ += 1 if k_ in (b'if', b'ifdef', b'ifndef') else -1 if k_ == b'endif' else 0
                elif depth_ == 0 and re.match(rb'^\s*#\s*include\b', ln_):
                    last_ = i_
            at_ = (last_ + 1) if last_ is not None else 0
            src_lines_[at_:at_] = new_
            text = b'\n'.join(src_lines_)
    # Drop now-empty preprocessor blocks.
    empty = re.compile(rb'\n[ \t]*#[ \t]*if[^\n]*\n(?:[ \t]*\n)*[ \t]*#[ \t]*endif[^\n]*(?=\n)')
    empty_ns = re.compile(rb'\n[ \t]*namespace[ \t]*\{[ \t]*\n(?:[ \t]*\n)*[ \t]*\}[^\n]*(?=\n)')
    while True:
        t2 = empty_ns.sub(b'', empty.sub(b'', text))
        if t2 == text:
            break
        text = t2
    if write:
        open(src, 'wb').write(text)
    report['std_fallback'] = {k: sorted(v) for k, v in report.get('std_fallback', {}).items()}
    report['written'] = bool(write)
    return report


def function_parts_free(tu, c, data):
    """Free-function variant: no qualifier, keep everything but default args and [[nodiscard]]."""
    from .outliner import strip_default_args, declarator_end
    body = body_of(c)
    start = c.extent.start.offset
    dend = body.extent.start.offset
    decl = data[start:dend].rstrip() + b';'
    edits = [(a, b, b'') for a, b in strip_default_args(tu, c, data, 0)]
    pre = toks(tu, c.extent.start, c.location)
    i = 0
    while i < len(pre):
        t = pre[i]
        if t.spelling == '[' and i + 1 < len(pre) and pre[i + 1].spelling == '[':
            j = i + 2
            while j + 1 < len(pre) and not (pre[j].spelling == ']' and pre[j + 1].spelling == ']'):
                j += 1
            a, b = t.extent.start.offset, pre[j + 1].extent.end.offset
            while data[b:b + 1] in (b' ', b'\t'):
                b += 1
            edits.append((a, b, b''))
            i = j + 1
        i += 1
    edits.sort()
    out = bytearray()
    pos = start
    for a, b, r in edits:
        out += data[pos:a] + r
        pos = b
    out += data[pos:c.extent.end.offset]
    return decl, bytes(out), None


