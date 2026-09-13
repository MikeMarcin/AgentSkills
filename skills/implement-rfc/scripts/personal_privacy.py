"""Fail closed on known private references in proposed product surfaces."""
from __future__ import annotations

import re
from pathlib import Path

import personal_state as state


def private_tokens(context) -> set[str]:
    root = Path(context.workflow_root)
    tokens = {'implement-rfc.card.v1', 'rfc_base_sha', 'closeout_for', 'criterion_coverage',
              'private tracker', 'tracker acceptance'}
    tokens.update((str(root), str(context.runtime_root)))
    home = state.home_for(Path(context.source_root))
    tokens.add(str(home))
    binding = state.read_binding(home, Path(context.source_root))
    if binding:
        tokens.add(binding['tracker_root'])
    # Include reserved IDs and historical references, not just the active card.
    for relative in state.git(root, 'ls-files').splitlines():
        path = root / relative
        if (relative.startswith((context.config['issue_root'] + '/', context.config['rfc_root'] + '/'))
                and path.name not in ('README.md', 'NEXT_ID')):
            tokens.add(relative)
        if path.is_file() and not path.is_symlink():
            text = path.read_bytes().decode('utf-8', errors='replace')
            tokens.update(re.findall(r'\b(?:RFC-)?[A-Z][A-Z0-9_]*-\d{4,}\b', text))
    return {token.casefold().replace('\\', '/') for token in tokens if token}


def validate_text(context, text: str, surface: str) -> None:
    normalized = text.casefold().replace('\\', '/')
    if any(token in normalized for token in private_tokens(context)):
        raise state.PersonalStateError(f'{surface} contains a private identifier, tracker path or bookkeeping text')


def validate_bytes(context, content: bytes, surface: str) -> None:
    """Inspect supported text encodings; opaque binary content is unsupported."""
    if content.startswith((b'\xff\xfe\0\0', b'\0\0\xfe\xff')):
        encoding = 'utf-32'
    elif content.startswith((b'\xff\xfe', b'\xfe\xff')):
        encoding = 'utf-16'
    else:
        encoding = 'utf-8-sig'
    try:
        text = content.decode(encoding)
    except UnicodeError as exc:
        raise state.PersonalStateError(f'{surface} has an unsupported text encoding; privacy review required') from exc
    if any(ord(char) < 32 and char not in '\n\r\t' for char in text):
        raise state.PersonalStateError(f'{surface} is binary or has an unsupported text encoding; privacy review required')
    validate_text(context, text, surface)


def validate_branch(context, branch: str) -> None:
    state.git(Path(context.source_root), 'check-ref-format', '--branch', branch)
    validate_text(context, branch, 'source branch')
