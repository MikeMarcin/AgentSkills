"""Strict, lossless card front matter and shared board validation.

The card schema describes decoded metadata. Its deliberately small vocabulary
is evaluated here without third-party packages. Front matter supports one
key/value per line, text scalars, and inline lists of text; it is not full YAML.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import project_config

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'schemas/issue-card.schema.json'
KEY_RE = re.compile(r'^[a-z][a-z0-9_]*$')
ID_RE = re.compile(r'^[A-Z]{2,8}-\d{4}$')
RFC_RE = re.compile(r'^RFC-[A-Z]{2,8}(?:-[A-Z]{2,8})?-\d{4}$')
TOKEN_RE = re.compile(r'^[a-z0-9][a-z0-9-]{0,63}$')


@dataclass(frozen=True)
class Diagnostic:
    path: str
    field: str
    reason: str

    def __str__(self) -> str:
        return f'{self.path}: {self.field}: {self.reason}'


class BoardError(ValueError):
    def __init__(self, path: Path | str, field: str, reason: str):
        self.diagnostic = Diagnostic(str(path), field, reason)
        super().__init__(str(self.diagnostic))


class ValidationError(BoardError):
    def __init__(self, root: Path, diagnostics: list[Diagnostic]):
        self.diagnostics = diagnostics
        super().__init__(root, 'board', '\n'.join(map(str, diagnostics)))


def safe_path(root: Path, path: Path) -> Path:
    """Reject symlinks, including ancestors, rather than editing through aliases."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise BoardError(path, 'path', 'outside repository') from None
    cursor = root
    for part in relative.parts:
        if part in ('.', '..'):
            raise BoardError(path, 'path', 'noncanonical path')
        cursor /= part
        if cursor.is_symlink():
            raise BoardError(path, 'path', 'symlinks are not supported')
    return path


def scalar(value: str, path: Path, key: str) -> str:
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, str) and '\n' not in parsed and '\r' not in parsed:
                return parsed
        except ValueError:
            pass
        raise BoardError(path, key, 'invalid quoted text; use JSON double quoting')
    if value.startswith("'"):
        if len(value) >= 2 and value.endswith("'") and "'" not in value[1:-1].replace("''", ''):
            return value[1:-1].replace("''", "'")
        raise BoardError(path, key, 'invalid single-quoted text')
    if (not value or value[0] in '!&*{}[]|>@`%#' or re.search(r':(?:\s|$)|(?:^|\s)#', value)):
        raise BoardError(path, key, 'unsupported plain text (including unquoted colon); quote the value')
    return value


def decode(value: str, path: Path, key: str):
    # JSON covers nested descriptive metadata without inventing a YAML dialect.
    # Plain text scalars remain convenient for hand edits. Arrays/objects are JSON.
    if value.startswith(('[', '{', '"')) or value in {'true', 'false', 'null'} or re.fullmatch(r'-?\d+(?:\.\d+)?', value):
        try:
            return json.loads(value)
        except ValueError as exc:
            raise BoardError(path, key, f'invalid JSON value: {exc}') from None
    return scalar(value, path, key)


def encode(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


@dataclass
class Matter:
    raw: dict[str, str]
    values: dict[str, str | list[str]]
    lines: list[str]
    indices: dict[str, int]
    end: int

    def updated(self, updates: dict[str, str | None]) -> bytes:
        lines = list(self.lines)
        newline = '\r\n' if lines[0].endswith('\r\n') else '\n'
        for key, value in updates.items():
            if key in self.indices:
                index = self.indices[key]
                if value is None:
                    lines[index] = ''
                elif self.values[key] != value:
                    lines[index] = f'{key}: {encode(value)}{newline}'
        additions = [f'{key}: {encode(value)}{newline}' for key, value in updates.items()
                     if key not in self.indices and value is not None]
        lines[self.end:self.end] = additions
        return ''.join(lines).encode('utf-8')


def parse_matter(data: bytes, path: Path) -> Matter:
    try:
        lines = data.decode('utf-8').splitlines(keepends=True)
    except UnicodeDecodeError:
        raise BoardError(path, 'front_matter', 'invalid UTF-8') from None
    if not lines or lines[0].rstrip('\r\n') != '---':
        raise BoardError(path, 'front_matter', 'missing front matter')
    raw: dict[str, str] = {}
    values: dict[str, str | list[str]] = {}
    indices: dict[str, int] = {}
    for index, line in enumerate(lines[1:], 1):
        if line.rstrip('\r\n') == '---':
            return Matter(raw, values, lines, indices, index)
        key, separator, value = line.rstrip('\r\n').partition(':')
        if not separator or not KEY_RE.fullmatch(key):
            raise BoardError(path, 'front_matter', f'unsupported field syntax on line {index + 1}')
        if key in raw:
            raise BoardError(path, key, 'duplicate front-matter key')
        raw[key] = value.strip()
        values[key] = decode(value.strip(), path, key)
        indices[key] = index
    raise BoardError(path, 'front_matter', 'missing closing fence')


def schema_errors(values: dict, path: Path, config: dict) -> list[Diagnostic]:
    """Evaluate our small schema vocabulary, including descriptive JSON metadata."""
    errors = []
    def check(value, rule, key):
        types = {'string': str, 'array': list, 'object': dict}
        if not isinstance(value, types[rule['type']]):
            errors.append(Diagnostic(str(path), key, f"expected {rule['type']}"))
            return
        reason = None
        if 'enum' in rule and value not in rule['enum']:
            reason = 'invalid value'
        if isinstance(value, str):
            if len(value.strip()) < rule.get('minLength', 0):
                reason = 'must be nonempty'
            if 'pattern' in rule and not re.fullmatch(rule['pattern'], value):
                reason = 'invalid value format'
        elif isinstance(value, list):
            if rule.get('uniqueItems') and len(value) != len({encode(v) for v in value}):
                reason = 'duplicate array value'
            for i, item in enumerate(value):
                check(item, rule['items'], f'{key}[{i}]')
        else:
            for required in rule.get('required', []):
                if required not in value:
                    errors.append(Diagnostic(str(path), f'{key}.{required}'.lstrip('.'), 'required field missing'))
            for name, item in value.items():
                if name in rule.get('properties', {}):
                    check(item, rule['properties'][name], f'{key}.{name}'.lstrip('.'))
                elif rule.get('additionalProperties') is False:
                    errors.append(Diagnostic(str(path), name, 'unknown card field; descriptive data belongs in metadata'))
        if reason:
            errors.append(Diagnostic(str(path), key, reason))
    check(values, CARD_SCHEMA, '')
    if set(values.get('closeout_for', [])) - set(values.get('rfcs', [])):
        errors.append(Diagnostic(str(path), 'closeout_for', 'must be a subset of rfcs'))
    return errors


CARD_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))


@dataclass
class Card:
    path: Path
    lane: str
    matter: Matter
    config: dict

    @property
    def id(self) -> str:
        return self.matter.values['id']

    @property
    def fields(self) -> dict:
        return self.matter.values

    @property
    def deps(self) -> list[str]:
        return self.fields['depends_on']

    @property
    def rfcs(self) -> list[str]:
        return self.fields['rfcs']

    @property
    def body(self) -> str:
        return ''.join(self.matter.lines)


def policy(config: dict) -> dict:
    lanes = config['lanes']
    return config.get('bookkeeping', {
        'deferring_lanes': [lanes['inbox'], lanes['backlog'], lanes['blocked'], lanes['parked']],
        'parked_on': [], 'blocked_by_forbidden_prefixes': [],
        'link_roots': [], 'protected_globs': [], 'editable_globs': [],
    })


def read_cards(root: Path, config: dict, overrides: dict[Path, bytes | None] | None = None
               ) -> tuple[dict[str, Card], list[Diagnostic]]:
    overrides = overrides or {}
    board = safe_path(root, root / config['issue_root'])
    errors: list[Diagnostic] = []
    cards: dict[str, Card] = {}
    if not board.is_dir():
        return cards, [Diagnostic(str(board), 'path', 'issue root missing')]
    lanes = project_config.lane_names(config)
    for entry in sorted(board.iterdir()):
        if entry.is_dir() and not entry.name.startswith('_') and entry.name not in lanes:
            errors.append(Diagnostic(str(entry), 'lane', f'non-canonical board folder: {entry.name}'))
    for lane in lanes:
        directory = safe_path(root, board / lane)
        paths = set(directory.glob('*.md')) | {p for p in overrides if p.parent == directory}
        for path in sorted(paths):
            if path in overrides and overrides[path] is None:
                continue
            try:
                safe_path(root, path)
                data = overrides[path] if path in overrides else path.read_bytes()
                matter = parse_matter(data, path)
                found = schema_errors(matter.values, path, config)
                errors.extend(found)
                if found:
                    continue
                card = Card(path, lane, matter, config)
                if not path.name.startswith(card.id + '-'):
                    errors.append(Diagnostic(str(path), 'id', 'filename/id mismatch'))
                if card.id in cards:
                    errors.append(Diagnostic(str(path), 'id', f'duplicate card id {card.id}'))
                else:
                    cards[card.id] = card
            except BoardError as exc:
                errors.append(exc.diagnostic)
    return cards, errors


def validate_cards(cards: dict[str, Card], config: dict, scope: set[str] | None = None) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    lanes = config['lanes']
    rules = policy(config)
    done = lanes['done']
    for card in cards.values():
        if scope is not None and card.id not in scope:
            continue
        def error(field: str, reason: str) -> None:
            errors.append(Diagnostic(str(card.path), field, reason))
        expected = config['lane_statuses'][card.lane]
        if card.fields['status'] != expected:
            error('status', f"status '{card.fields['status']}' != '{expected}'")
        for key, destination in (('parked_on', lanes['parked']), ('blocked_by', lanes['blocked'])):
            value = card.fields.get(key)
            if card.lane == destination:
                if not value:
                    error(key, f'{key} required in {destination}')
                elif key == 'parked_on' and rules['parked_on'] and value not in rules['parked_on']:
                    error(key, 'unknown parked_on token')
                elif key == 'blocked_by' and any(value.startswith(p) for p in rules['blocked_by_forbidden_prefixes']):
                    error(key, 'a platform is a lane, not a blocker')
            elif value is not None:
                error(key, f'{key} outside its lane')
        for dep in card.deps:
            if dep == card.id:
                error('depends_on', 'self dependency')
            elif dep not in cards:
                error('depends_on', f'depends_on {dep} not found')
            elif card.lane not in rules['deferring_lanes'] and cards[dep].lane != done:
                error('depends_on', f'{dep} is not Done ({cards[dep].lane})')
    # Iterative DFS handles large boards without Python recursion limits.
    visited: set[str] = set()
    for start in cards:
        if (scope is not None and start not in scope) or start in visited:
            continue
        stack = [(start, iter(cards[start].deps))]
        active = {start}
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                visited.add(node)
                active.remove(node)
                stack.pop()
            elif child in active:
                errors.append(Diagnostic(str(cards[node].path), 'depends_on', f'issue dependency cycle through {child}'))
            elif child in cards and child not in visited:
                active.add(child)
                stack.append((child, iter(cards[child].deps)))
    return errors


def validate_board(root: Path, config: dict, overrides: dict[Path, bytes | None] | None = None, *, scope: set[str] | None = None
                   ) -> tuple[dict[str, Card], list[Diagnostic]]:
    cards, errors = read_cards(root, config, overrides)
    if callable(scope):
        scope = scope(cards)
    errors.extend(validate_cards(cards, config, scope))
    rfcs: dict[str, Path] = {}
    rfc_root = safe_path(root, root / config['rfc_root'])
    for path in sorted(rfc_root.glob('RFC-*.md')):
        if path.name == 'README.md':
            continue
        try:
            safe_path(root, path)
            metadata = parse_matter(path.read_bytes(), path).values
            rfc_id = metadata.get('id', '')
            if not isinstance(rfc_id, str) or not RFC_RE.fullmatch(rfc_id) or not path.name.startswith(rfc_id + '-'):
                raise BoardError(path, 'id', 'invalid RFC identity or filename')
            if rfc_id in rfcs:
                raise BoardError(path, 'id', f'duplicate RFC id {rfc_id}')
            rfcs[rfc_id] = path
        except BoardError as exc:
            errors.append(exc.diagnostic)
    for card in cards.values():
        for rfc in card.rfcs:
            if rfc not in rfcs:
                errors.append(Diagnostic(str(card.path), 'rfcs', f'linked {rfc} has no RFC file'))
    import allocation
    _, counter_errors, _ = allocation.inspect_counters(root, config, cards)
    errors.extend(counter_errors)
    return cards, errors


def dependency_scope(cards: dict[str, Card], selected: set[str]) -> set[str]:
    # A completed prerequisite is evidence, not a request to replay its history.
    # Explicitly selected Done cards (and full validation) still inspect history.
    pending = list(selected)
    result = set(selected)
    while pending:
        card = cards.get(pending.pop())
        for dep in card.deps if card else []:
            if dep not in result and (dep not in cards or cards[dep].lane != cards[dep].config['lanes']['done']):
                result.add(dep)
                pending.append(dep)
    return result
