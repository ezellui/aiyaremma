"""Classification of Eldamo rule formulas for the sound graph."""
from __future__ import annotations

import unicodedata

from .interpreter import nfc, phonemes, position_of

NULL = '∅'
# Characters that make a side a pattern rather than a literal sound sequence.
PATTERN_CHARS = set('{}|()[]/_+*?=<>⁺⁻ ') | set('₁₂₃₄₅₆₇₈₉0123456789')


def literal_side(text: str | None):
    """Return (value, position) for a literal side, or (None, position) for a pattern.

    A side consisting only of ø is the empty sound and is returned as NULL.
    """
    if text is None:
        return None, 'any'
    core, position = position_of(text)
    core = nfc(core)
    if core == 'ø':
        return NULL, position
    if not core or 'ø' in core:
        return None, position
    if any(ch in PATTERN_CHARS for ch in core):
        return None, position
    if any(ch.isupper() for ch in unicodedata.normalize('NFD', core)):
        return None, position  # V, C, X, S and other classes
    return core, position


def classify_pair(src: str, dst: str) -> dict:
    """Describe one <rule from=... rule=...> pair."""
    a, pa = literal_side(src)
    b, pb = literal_side(dst)
    if a is not None and b is not None and pa == pb:
        if a == b:
            kind = 'identity'
        elif a == NULL:
            kind = 'insertion'
        elif b == NULL:
            kind = 'loss'
        else:
            kind = 'literal'
        return {'kind': kind, 'a': a, 'b': b, 'position': pa}
    return {'kind': 'contextual', 'a': None, 'b': None, 'position': pa if pa == pb else 'mixed'}


def segments(value: str, inventory: list[str]) -> list[str]:
    """Split a literal sequence into inventory phonemes, longest match first."""
    if value in (None, NULL):
        return []
    inv = sorted(set(inventory), key=len, reverse=True)
    out, i, s = [], 0, nfc(value)
    while i < len(s):
        for p in inv:
            if p and s.startswith(p, i):
                out.append(p)
                i += len(p)
                break
        else:
            ph = phonemes(s[i:])[0]
            out.append(ph)
            i += len(ph)
    return out
