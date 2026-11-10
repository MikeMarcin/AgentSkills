"""Turn in-class member definitions into declarations plus out-of-line definitions.

Works on exact libclang extents and tokens of one translation unit. Text outside
function bodies is preserved byte for byte in the generated class definition.
"""
import os, sys
from .cx import ci

K = ci.CursorKind
FUNCS = (K.CXX_METHOD, K.CONSTRUCTOR, K.DESTRUCTOR, K.CONVERSION_FUNCTION)
RECORDS = (K.CLASS_DECL, K.STRUCT_DECL)
DROP_BEFORE_NAME = {'virtual', 'static', 'explicit', 'inline'}
DROP_AFTER_PARAMS = {'override', 'final'}
# One indentation level of the project's style; extract sets it from the plan.
UNIT = b'\t'


class Unsupported(Exception):
    pass


def toks(tu, start, end):
    ext = ci.SourceRange.from_locations(start, end)
    return [t for t in tu.get_tokens(extent=ext)]


def body_of(c):
    for k in c.get_children():
        if k.kind in (K.COMPOUND_STMT, K.CXX_TRY_STMT):
            return k
    return None


def is_outlinable(c):
    if c.kind not in FUNCS or not c.is_definition():
        return False
    if c.is_default_method() or c.is_deleted_method():
        return False
    if body_of(c) is None:
        return False
    return True


def declarator_end(tu, c, body):
    """Offset where the declaration ends: before a ctor-initializer or the body."""
    ts = toks(tu, c.location, body.extent.start)
    depth = 0
    seen_params = False
    for t in ts:
        s = t.spelling
        if t.extent.start.offset >= body.extent.start.offset:
            break
        if s in ('(', '[', '{'):
            depth += 1
            if s == '(':
                seen_params = True
        elif s in (')', ']', '}'):
            depth -= 1
        elif s == ':' and depth == 0 and seen_params:
            return t.extent.start.offset
    return body.extent.start.offset


def strip_default_args(tu, c, text, base):
    """Return list of (start, end) byte ranges (absolute) to delete for default args."""
    cuts = []
    for p in c.get_children():
        if p.kind != K.PARM_DECL:
            continue
        depth = 0
        for t in toks(tu, p.extent.start, p.extent.end):
            s = t.spelling
            if s in ('(', '[', '{', '<'):
                depth += 1
            elif s in (')', ']', '}', '>'):
                depth -= 1
            elif s == '>>':
                depth -= 2
            elif s == '=' and depth == 0:
                # Remove the whitespace before '=' too.
                a = t.extent.start.offset
                while a > p.extent.start.offset and text[a - 1 - base:a - base] in (b' ', b'\t'):
                    a -= 1
                cuts.append((a, p.extent.end.offset))
                break
    return cuts


def function_parts(tu, c, data, qualifier):
    """(declaration_text, definition_text) for one in-class function definition."""
    body = body_of(c)
    start = c.extent.start.offset
    end = c.extent.end.offset
    dend = declarator_end(tu, c, body)
    decl = data[start:dend].rstrip() + b';'
    # Definition: drop specifiers before the name, override/final after the
    # parameters, default arguments; qualify the name.
    name = c.location.offset
    edits = []  # (start, end, replacement) absolute
    pre = toks(tu, c.extent.start, c.location)
    i = 0
    while i < len(pre):
        t = pre[i]
        if t.extent.start.offset >= name:
            break
        s = t.spelling
        if s in DROP_BEFORE_NAME:
            a, b = t.extent.start.offset, t.extent.end.offset
            while data[b:b + 1] in (b' ', b'\t'):
                b += 1
            edits.append((a, b, b''))
        elif s == '[' and i + 1 < len(pre) and pre[i + 1].spelling == '[':
            # Attribute: [[ ... ]]
            j = i + 2
            while j + 1 < len(pre) and not (pre[j].spelling == ']' and pre[j + 1].spelling == ']'):
                j += 1
            a, b = t.extent.start.offset, pre[j + 1].extent.end.offset
            while data[b:b + 1] in (b' ', b'\t'):
                b += 1
            edits.append((a, b, b''))
            i = j + 1
        i += 1
    for a, b in strip_default_args(tu, c, data, 0):
        edits.append((a, b, b''))
    post = toks(tu, c.location, body.extent.start)
    depth = 0
    params_closed = False
    for t in post:
        if t.extent.start.offset >= dend:
            break
        s = t.spelling
        if s == '(':
            depth += 1
        elif s == ')':
            depth -= 1
            if depth == 0:
                params_closed = True
        elif depth == 0 and params_closed and s in DROP_AFTER_PARAMS:
            a, b = t.extent.start.offset, t.extent.end.offset
            while a > 0 and data[a - 1:a] in (b' ', b'\t'):
                a -= 1
            edits.append((a, b, b''))
    edits.append((name, name, qualifier.encode() + b'::'))
    edits.sort(key=lambda e: (e[0], e[1]))
    out = bytearray()
    pos = start
    for a, b, r in edits:
        if a < pos:
            raise Unsupported(f'overlapping edit in {c.spelling}')
        out += data[pos:a] + r
        pos = b
    out += data[pos:end]
    leading_return = _leading_return_needs_check(pre, name)
    return decl, bytes(out), leading_return


def _leading_return_needs_check(pre, name):
    words = [t.spelling for t in pre if t.extent.start.offset < name]
    # Skip attributes and specifiers.
    filtered = []
    skip = 0
    for w in words:
        if w == '[':
            skip += 1
            continue
        if w == ']':
            skip -= 1
            continue
        if skip:
            continue
        if w in DROP_BEFORE_NAME or w in ('constexpr', 'friend'):
            continue
        filtered.append(w)
    if not filtered or filtered[0] in ('auto', 'void', 'bool', 'int', 'char', 'double', 'float', '~'):
        return False
    return ' '.join(filtered)


def dedent(text, tabs):
    if tabs <= 0:
        return text
    lines = text.split(b'\n')
    out = [lines[0]]
    for ln in lines[1:]:
        n = 0
        while n < tabs and ln.startswith(UNIT, n * len(UNIT)):
            n += 1
        out.append(ln[n * len(UNIT):])
    return b'\n'.join(out)


def indent_of(data, offset):
    a = data.rfind(b'\n', 0, offset) + 1
    n = 0
    while data.startswith(UNIT, a + n * len(UNIT)):
        n += 1
    return n


def leading_comment_offset(data, start):
    """Offset of the comment block directly above `start` (same lines only)."""
    ls = data.rfind(b'\n', 0, start) + 1
    pos = ls
    while pos > 0:
        prev = data.rfind(b'\n', 0, pos - 1) + 1
        line = data[prev:pos - 1].strip()
        if line.startswith(b'//') or line.startswith(b'/*') or line.startswith(b'*'):
            pos = prev
            continue
        break
    return pos


def outline_record(tu, rec, data, qualifier, target_indent, keep=lambda c: False, defs=None, notes=None, move_comments=False, hoist=(), hoisted=None):
    """Return (class_text, defs) where class_text has bodies replaced by declarations.

    defs is a list of dicts {qualifier, name, line, text}. `keep(cursor)` keeps a
    member function inline (templates, constexpr).
    """
    if defs is None:
        defs = []
    if notes is None:
        notes = []
    start, end = rec.extent.start.offset, rec.extent.end.offset
    rec_indent = indent_of(data, start)
    pieces = []
    pos = start
    for m in rec.get_children():
        ms, me = m.extent.start.offset, m.extent.end.offset
        if ms < start or me > end:
            continue
        if m.kind in RECORDS and m.is_definition() and m.spelling in hoist:
            # Lifted to namespace scope: cut with its comment and trailing ';'.
            cs = leading_comment_offset(data, ms)
            cut_from = cs if cs >= pos else data.rfind(b'\n', 0, ms) + 1
            e = me
            while data[e:e + 1] in (b' ', b'\t'):
                e += 1
            if data[e:e + 1] == b';':
                e += 1
            if data[e:e + 1] == b'\n':
                e += 1
            pieces.append(data[pos:cut_from])
            pos = e
            if hoisted is not None:
                hoisted.append(m)
            continue
        if m.kind in RECORDS and m.is_definition():
            inner, _ = outline_record(tu, m, data, qualifier + '::' + m.spelling, target_indent, keep, defs, notes, move_comments)
            pieces.append(data[pos:ms])
            pieces.append(inner)
            pos = me
            continue
        if m.kind == K.FUNCTION_TEMPLATE or not is_outlinable(m) or keep(m):
            continue
        tokens_before = [t.spelling for t in toks(tu, m.extent.start, m.location)]
        if 'constexpr' in tokens_before or 'consteval' in tokens_before:
            notes.append(f'kept constexpr {qualifier}::{m.spelling} line {m.extent.start.line}')
            continue
        decl, definition, lead = function_parts(tu, m, data, qualifier)
        if lead:
            notes.append(f'leading return "{lead}" on {qualifier}::{m.spelling} line {m.extent.start.line}')
        mind = indent_of(data, ms)
        comment = b''
        cs = leading_comment_offset(data, ms)
        if move_comments and cs < data.rfind(b'\n', 0, ms) + 1 and cs >= pos:
            comment = data[cs:data.rfind(b'\n', 0, ms) + 1]
            pieces.append(data[pos:cs])
            pieces.append(data[data.rfind(b'\n', 0, ms) + 1:ms])
        else:
            pieces.append(data[pos:ms])
        pieces.append(decl)
        pos = me
        if comment:
            # Keep original indentation; the definition's own dedent applies to all lines.
            definition = comment.lstrip(b' \t') + UNIT * mind + definition
        defs.append({
            'qualifier': qualifier,
            'name': m.spelling,
            'kind': m.kind.name,
            'line': m.extent.start.line,
            'end_line': m.extent.end.line,
            'text': dedent(definition, mind - target_indent),
        })
    pieces.append(data[pos:end])
    return b''.join(pieces), defs
