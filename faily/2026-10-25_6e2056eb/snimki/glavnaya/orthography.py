"""Tolkien's spelling of Quenya and Sindarin words -> Eldamo's phonetic notation.

Derivations in Eldamo end in phonetic forms (Quendi -> kwendi, nehta- ->
nexta-, Thû -> θū, rhaed -> r̥aed). Word formation at the latest stage starts
from dictionary forms, so they are converted the same way. The conversion is
checked against the attested pairs (tests/test_lexicon.py).
"""
from __future__ import annotations

import re
import unicodedata

ACUTE, CIRCUMFLEX, DIAERESIS, MACRON = '́', '̂', '̈', '̄'
SUPERSCRIPT = re.compile(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]')

QUENYA = [
    ('nqu', 'ŋkw'), ('ngw', 'ŋgw'), ('qu', 'kw'), ('nc', 'ŋk'), ('ng', 'ŋg'), ('ñ', 'ŋ'),
    ('hy', 'j̊'), ('hw', 'w̥'), ('hl', 'l̥'), ('hr', 'r̥'), ('ht', 'xt'),
    ('x', 'ks'), ('c', 'k'), ('þ', 'θ'), ('y', 'j'),
]
SINDARIN = [
    ('ch', 'x'), ('th', 'θ'), ('dh', 'ð'), ('ph', 'f'), ('lh', 'l̥'), ('rh', 'r̥'), ('mh', 'ṽ'),
    ('nc', 'ŋk'), ('ng', 'ŋg'), ('ñ', 'ŋ'), ('c', 'k'), ('þ', 'θ'), ('k', 'k'),
]


def _long(text: str) -> str:
    """Acute and circumflex mark long vowels; the diaeresis only shows a
    vowel is pronounced (ë)."""
    out = []
    for ch in unicodedata.normalize('NFD', text):
        if ch in (ACUTE, CIRCUMFLEX):
            out.append(MACRON)
        elif ch == DIAERESIS:
            continue
        else:
            out.append(ch)
    return unicodedata.normalize('NFC', ''.join(out))


def clean(form: str) -> str:
    """Drop homonym numbers and optional parts: riel(lë) -> riel, ur(u) -> ur."""
    f = SUPERSCRIPT.sub('', form.strip())
    return re.sub(r'\([^)]*\)', '', f).strip()


def to_phonetic(form: str, family: str) -> str:
    """family: 'quenya' or 'sindarin'."""
    f = _long(clean(form)).lower()
    if family == 'quenya':
        if f.startswith('ñ'):
            f = 'n' + f[1:]      # initial [ŋ] became [n] (Q.)
        for a, b in QUENYA:
            f = f.replace(a, b)
        return f
    for a, b in SINDARIN:
        f = f.replace(a, b)
    f = re.sub(r'ŋg$', 'ŋ', f)                       # final ng is [ŋ]
    f = re.sub(r'(?<=[aeiouyāēīōūȳ])w$', 'u', f)     # final aw is a diphthong: maw -> mau
    f = re.sub(r'^i(?=[aeouāēōū])', 'j', f)          # initial i before a vowel: iant -> jant
    f = re.sub(r'(?<=[aeiouyāēīōūȳ])f$', 'v', f)    # final f is [v]
    return f
