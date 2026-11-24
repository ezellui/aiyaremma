#!/usr/bin/env python3
"""Roots of every Neo-Quenya vocabulary word of Eldamo.

    python nq_roots.py path/to/eldamo-data.xml [out.json]

The word list is the one Eldamo prints on vocabulary-words-nq.html
(vocabulary-index.xq with id=nq): words of nq, q, mq (eq is read but filtered
out by the page), without <combine>, <deprecated>, <see>, names, phrases,
grammar, phonetics and roots, not [unglossed], and without '-' or '|' in @mark.

For each word the roots are found by walking Eldamo's links the way its word
pages read them (common.xq c:get-word / c:get-ref, word-page.xq
print-derivations), plus two links a word page does not follow but which
carry the etymology of the same word in another period:

* element   -- <element> of the word itself (a compound or a word + affix);
               when the word has none, the elements written inside one of its
               references (by @source, else by form);
* deriv     -- <deriv l v> of the word (c:get-word) and <deriv source> inside
               its valid references (c:get-ref): a root, or an intermediate form
               (a primitive word, an earlier Quenya word...) followed further;
* combine   -- words merged into this one (<combine l v> pointing here):
               ᴹQ. and ᴱQ. versions of a Q. or NQ. word;
* see       -- a stub that only says "see X";
* cognate   -- words joined by <cognate> (transitively, as the Cognates section
               of a word page), used only when nothing above gives a root, and
               only roots whose consonants are found in the word.

Priority, per word (as quettamin shared/lexicon.py _root_groups):
 1. two or more elements with roots -> the roots by element (compound);
 2. roots named by the word's derivations -> alternatives of one part;
 3. one element with roots -> it, the other elements as gaps;
 4. roots of intermediate forms the word derives from;
 5. roots of words merged into it (combine);
 6. a "see" target;
 7. cognates (checked).
Roots found by the lower steps when a higher one already answered are kept
apart in "also" (only those not already among the chosen roots).

Standard library only (Python >= 3.6).
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict

SITE = 'https://eldamo.org/content/words/word-{}.html'
# the languages of each vocabulary page (c:lang-words) and the ones the page filters out
GROUPS = {
    'nq': {'langs': ('nq', 'q', 'mq', 'eq'), 'name': 'Neo-Quenya'},
    'ns': {'langs': ('ns', 's', 'n', 'en', 'g'), 'name': 'Neo-Sindarin'},
}
FILTERED_LANGS = ('eq', 'en', 'g', 'ep')
SINDARIN_LIKE = ('ns', 's', 'n', 'en', 'g', 'on', 'os', 'norths', 'ilk', 'eilk', 'dan', 'nan')
PRIMITIVE = ('p', 'mp', 'ep', 'np')
QUENYA_LIKE = ('nq', 'q', 'mq', 'eq', 'aq', 'maq', 'eaq', 'van', 'mt', 't', 'et')
LANG_NAMES = {'nq': 'Neo-Quenya', 'q': 'Quenya', 'mq': 'Middle Quenya', 'eq': 'Early Quenya',
              'ns': 'Neo-Sindarin', 's': 'Sindarin', 'n': 'Noldorin', 'en': 'Early Noldorin', 'g': 'Gnomish'}
MAX_DEPTH = 9
WEAK_RULES = ('deprecated', 'cognate')


def deleted(mark):
    """Rejected by Tolkien: '-' anywhere in @mark ('|' is a deleted section, not a rejection)."""
    return bool(mark) and '-' in mark


class Data:
    def __init__(self, path):
        self.root = ET.parse(path).getroot()
        self.parent = {}
        for p in self.root.iter():
            for c in p:
                self.parent[c] = p
        self.words = list(self.root.iter('word'))
        self.by_id = {w.get('page-id'): w for w in self.words}
        self.by_v = defaultdict(list)
        self.by_lv = defaultdict(list)
        for w in self.words:
            self.by_v[w.get('v')].append(w)
            self.by_lv[(w.get('l'), w.get('v'))].append(w)
        self.refs = defaultdict(list)
        self.cognate_of_ref = defaultdict(list)    # source -> refs having <cognate source=...>
        self.cognate_of_word = defaultdict(list)   # (l, v) -> words having <cognate l v>
        for w in self.words:
            for r in w.findall('ref'):
                if r.get('source'):
                    self.refs[r.get('source')].append(r)
                for c in r.findall('cognate'):
                    if c.get('source'):
                        self.cognate_of_ref[c.get('source')].append(r)
            for c in w.findall('cognate'):
                self.cognate_of_word[(c.get('l'), c.get('v'))].append(w)
        # words merged into a word: <combine l v> resolved to the target page;
        # words replaced by a word: <deprecated l v>
        self.combined_from = defaultdict(list)
        self.combined_into = {}
        self.deprecated_from = defaultdict(list)
        for w in self.words:
            c = w.find('combine')
            if c is not None:
                for t in self.get_word(c):
                    if t is not w:
                        self.combined_from[t.get('page-id')].append(w)
                        self.combined_into.setdefault(w.get('page-id'), t)
                        break
            for dp in w.findall('deprecated'):
                for t in self.get_word(dp)[:1]:
                    if t is not w:
                        self.deprecated_from[t.get('page-id')].append(w)
        self._cog = {}
        # Elvish languages: those under a Primitive Elvish language in the language tree
        # (Adûnaic, Westron, Khuzdul... have "cognates" by borrowing, not by roots)
        self.elvish = set()
        for lang in self.root.iter('language'):
            p, ids = lang, []
            while p is not None and p.tag == 'language':
                ids.append(p.get('id'))
                p = self.parent.get(p)
            if any(i in PRIMITIVE for i in ids):
                self.elvish.add(lang.get('id'))

    # -- Eldamo's lookups -------------------------------------------------
    def lang(self, el):
        while el is not None:
            if el.get('l'):
                return el.get('l')
            el = self.parent.get(el)
        return None

    def speech(self, el):
        while el is not None:
            if el.get('speech'):
                return el.get('speech')
            el = self.parent.get(el)
        return None

    def get_word(self, el):
        """c:get-word: words of form @v; of language @l when given, else the only such
        word, else those of the language the element inherits."""
        cands = self.by_v.get(el.get('v'), [])
        if el.get('l'):
            return [w for w in cands if w.get('l') == el.get('l')]
        if len(cands) == 1:
            return cands
        lang = self.lang(el)
        return [w for w in cands if w.get('l') == lang]

    def get_ref(self, source):
        """c:get-ref: the one <ref> with this @source, else nothing."""
        hits = self.refs.get(source) if source else None
        return hits[0] if hits and len(hits) == 1 else None

    def word_of(self, el):
        while el is not None and el.tag != 'word':
            el = self.parent.get(el)
        return el

    def is_root(self, w):
        """speech="root", or a primitive form written in capitals: Eldamo 0.8.13 files
        np GAWAK, ᴱ✶ƷAWAKA and ᴱ√OWO as nouns, though they are roots."""
        if self.speech(w) == 'root':
            return True
        letters = re.sub(r'[^\w]|[\d_¹²³⁴⁵⁶⁷⁸⁹⁰]', '', w.get('v') or '')
        return self.lang(w) in PRIMITIVE and bool(letters) and letters.isupper()

    def cognates(self, w):
        """CustomFunctions.allReferenceCognates over the word's valid refs + allWordCognates."""
        pid = w.get('page-id')
        if pid in self._cog:
            return self._cog[pid]
        out = []
        # through references
        todo = [r for r in w.findall('ref') if self.get_ref(r.get('source')) is r]
        seen = set(map(id, todo))
        while todo:
            r = todo.pop()
            nxt = list(self.cognate_of_ref.get(r.get('source'), []))
            for c in r.findall('cognate'):
                nxt += self.refs.get(c.get('source'), [])
            for x in nxt:
                if id(x) not in seen:
                    seen.add(id(x))
                    todo.append(x)
                    out.append(self.word_of(x))
        # through the word
        todo, seenw = [w], {id(w)}
        while todo:
            x = todo.pop()
            nxt = list(self.cognate_of_word.get((self.lang(x), x.get('v')), []))
            for c in x.findall('cognate'):
                nxt += self.by_lv.get((c.get('l'), c.get('v')), [])
            for y in nxt:
                if id(y) not in seenw:
                    seenw.add(id(y))
                    todo.append(y)
                    out.append(y)
        lang = w.get('l')
        res, ids = [], set()
        for x in out:
            if x is not None and x.get('l') != lang and x.get('page-id') not in ids:
                ids.add(x.get('page-id'))
                res.append(x)
        self._cog[pid] = res
        return res


# -- root resolution -----------------------------------------------------
# A result is a list of parts; a part is a list of alternatives; an alternative is
# {'id': page-id, 'via': [step, ...]} for a root, or {'gap': page-id, 'via': [...]}
# for an element without a root.  A step is (relation, page-id of the word passed).

class Resolver:
    def __init__(self, d: Data):
        self.d = d
        self.memo = {}
        self.path = set()
        self.cuts = 0

    def live(self, el, w):
        return not deleted(el.get('mark')) or deleted(w.get('mark'))

    def valid_refs(self, w):
        return [r for r in w.findall('ref') if self.d.get_ref(r.get('source')) is r and self.live(r, w)]

    def elements(self, w):
        """Element words in order: the word's own <element>, else those of one of its
        references (the one with the word's own form, else the first that has any)."""
        d = self.d
        out = []
        for el in w.findall('element'):
            if el.get('v') in (None, '?') or not self.live(el, w):
                continue
            hit = self._pick(d.get_word(el))
            out.append(hit if hit is not None else ('missing', el))
        if out:
            return out, 'word'
        refs = [r for r in self.valid_refs(w) if r.findall('element')]
        if not refs:
            return [], None
        own = [r for r in refs if _loose(r.get('v')) == _loose(w.get('v'))]
        for el in (own or refs)[0].findall('element'):
            if el.get('v') in (None, '?') or not self.live(el, w):
                continue
            r = d.get_ref(el.get('source'))
            hit = d.word_of(r) if r is not None else self._pick(d.get_word(el))
            out.append(hit if hit is not None else ('missing', el))
        return out, 'ref'

    def _pick(self, ws):
        if not ws:
            return None
        live = [x for x in ws if not deleted(x.get('mark'))]
        return (live or ws)[0]

    def derived_from(self, w):
        """Words the word derives from: its <deriv> (c:get-word) and the words whose
        reference a <deriv source> of its valid references names (c:get-ref); plus
        roots named as elements inside its references (Q. firya: PHIR)."""
        d = self.d
        out = []
        for dv in w.findall('deriv'):
            if self.live(dv, w):
                out += d.get_word(dv)
        for r in self.valid_refs(w):
            for dv in r.findall('deriv'):
                if not self.live(dv, w):
                    continue
                hit = d.get_ref(dv.get('source'))
                if hit is not None:
                    out.append(d.word_of(hit))
                elif dv.get('v'):
                    # a written primitive form without a reference: a root of that form
                    for code in ('p', 'mp', 'ep', 'np'):
                        rs = [x for x in d.by_lv.get((code, dv.get('v')), []) if d.is_root(x)]
                        if rs:
                            out.append(rs[0])
                            break
            for el in r.findall('element'):
                hit = d.get_ref(el.get('source')) if self.live(el, w) else None
                if hit is not None and d.is_root(d.word_of(hit)):
                    out.append(d.word_of(hit))
        res, seen = [], set()
        for x in out:
            if x is not None and x is not w and x.get('page-id') not in seen:
                seen.add(x.get('page-id'))
                res.append(x)
        return res

    def roots(self, w, depth=MAX_DEPTH, cognates=True):
        """(parts, rule): the chosen roots of a word and the rule that gave them."""
        pid = w.get('page-id')
        if pid in self.path:
            self.cuts += 1
            return [], None                  # a cycle (Q. nelquë ~ quainel) gives nothing
        key = (pid, depth, cognates)
        if key in self.memo:
            return self.memo[key]
        cuts = self.cuts
        self.path.add(pid)
        try:
            res = self._roots(w, depth, cognates)
        finally:
            self.path.discard(pid)
        if self.cuts == cuts:
            # a result cut short by a cycle depends on the path that led here: not cached
            self.memo[key] = res
        return res

    def candidates(self, w, depth, cognates):
        """Every rule's answer for a word: [(rule, parts)] in priority order."""
        d = self.d
        out = []
        if d.is_root(w):
            return [('self', [[{'id': w.get('page-id'), 'via': []}]])]
        if depth <= 0:
            return out
        pid = w.get('page-id')
        # elements
        parts = []
        els, where = self.elements(w)
        for e in els:
            if isinstance(e, tuple):
                parts.append([{'gap': None, 'form': e[1].get('v'), 'lang': e[1].get('l') or d.lang(e[1]), 'via': []}])
                continue
            step = ('element', e.get('page-id'))
            if d.is_root(e):
                parts.append([{'id': e.get('page-id'), 'via': [], 'named': True}])
                continue
            # no cognates below the word itself: a chain through a cognate of an element
            # (Q. -on² ~ S. -on²...) is too loose to name a root
            sub, _ = self.roots(e, depth - 1, cognates=False)
            if any(_real(g) for g in sub):
                for g in sub:
                    parts.append([dict(a, via=[step] + a['via']) for a in g])
            else:
                parts.append([{'gap': e.get('page-id'), 'via': []}])
        real = [g for g in parts if _real(g)]
        derived = self.derived_from(w)
        direct = [{'id': x.get('page-id'), 'via': []} for x in derived if d.is_root(x)]
        # intermediate forms
        found = []
        for x in derived:
            if d.is_root(x):
                continue
            sub, _ = self.roots(x, depth - 1, cognates=False)
            if any(_real(g) for g in sub):
                step = ('deriv', x.get('page-id'))
                found.append([[dict(a, via=[step] + a['via']) for a in g] for g in sub])
        inter = _merge(found) if found else []
        if len(real) >= 2:
            out.append(('elements', parts))
        if direct:
            # a root named by one derivation and a root reached through an intermediate
            # form of another are alternatives of the same word (Q. alda < √GAL², and
            # < ✶galadā < √GALAD); a compound intermediate form stays apart
            alts = list(direct)
            if len(inter) == 1:
                alts += [a for a in _real(inter[0]) if all(a['id'] != b['id'] for b in alts)]
            out.append(('deriv', [alts]))
        if len(real) == 1:
            out.append(('element', parts))
        if inter:
            out.append(('intermediate', inter))
        # words merged into this one
        found = []
        for x in d.combined_from.get(pid, []):
            sub, _ = self.roots(x, depth - 1, cognates=False)
            if any(_real(g) for g in sub):
                step = ('combine', x.get('page-id'))
                found.append([[dict(a, via=[step] + a['via']) for a in g] for g in sub])
        if found:
            out.append(('combine', _merge(found)))
        # see
        found = []
        for s in w.findall('see'):
            for x in d.get_word(s)[:1]:
                if x is w:
                    continue
                sub, _ = self.roots(x, depth - 1, cognates=False)
                if any(_real(g) for g in sub):
                    step = ('see', x.get('page-id'))
                    found.append([[dict(a, via=[step] + a['via']) for a in g] for g in sub])
        if found:
            out.append(('see', _merge(found)))
        # a word this one replaced (<deprecated>): sometimes an earlier form of the same
        # word (ᴱQ. milt > NQ. miltë), sometimes another word (ᴱQ. nardilea > NQ.
        # nisilëa); taken only when the consonants of every part are found in this word
        found = []
        for x in d.deprecated_from.get(pid, []):
            # the replaced word must look like an earlier form of this one: the same
            # beginning (NQ. sin > latúcen "tin", Q. engë > né "was" are other words)
            if not same_onset(x.get('v'), w.get('v')):
                continue
            sub, _ = self.roots(x, depth - 1, cognates=False)
            checked = self.checked(w, sub, ('deprecated', x.get('page-id')), strict=True)
            if checked:
                found.append(checked)
        if found:
            out.append(('deprecated', _merge(found)))
        # cognates: the parts whose consonants are found in this word; a part of the
        # cognate that is not found here is a gap (S. suilanna- = suil + anna-)
        if cognates:
            found = []
            for x in d.cognates(w):
                if d.lang(x) in PRIMITIVE or d.lang(x) not in d.elvish:
                    continue
                sub, _ = self.roots(x, depth - 1, cognates=False)
                checked = self.checked(w, sub, ('cognate', x.get('page-id')), strict=False)
                if checked:
                    if len(sub) > 1:
                        # a compound cognate (N. anrand = ann + rand for ᴹQ. randa) may
                        # share only a part with this word: its roots are not offered
                        # as alternatives ("also") to roots found otherwise
                        checked = [[dict(a, partial=True) for a in g] for g in checked]
                    found.append(checked)
            if found:
                # the cognate with most parts found, then fewest gaps
                found.sort(key=lambda g: (-sum(1 for x in g if _real(x)), sum(1 for x in g if not _real(x))))
                best = [g for g in found
                        if [bool(_real(x)) for x in g] == [bool(_real(x)) for x in found[0]]]
                out.append(('cognate', _merge(best)))
        return out

    def checked(self, w, parts, step, strict):
        """parts of another word kept for this one: alternatives whose consonants are
        found in this word; a part with none becomes a gap (strict: the whole is refused)."""
        if not any(_real(g) for g in parts):
            return None
        res = []
        for g in parts:
            real = _real(g)
            sind = is_sindarin(self.d.lang(w))
            ok = [a for a in real if consonants_match(w.get('v'), self.d.by_id[a['id']].get('v'), sind)]
            if ok:
                res.append([dict(a, via=[step] + a['via']) for a in ok])
            elif real and strict:
                return None
            elif real:
                res.append([{'gap': step[1], 'via': [], 'unmatched': [a['id'] for a in real]}])
            elif strict:
                res.append([dict(a, via=[step] + a['via']) for a in g])
            # a cognate's own rootless parts (S. estolad: -ad) say nothing about this word
        return res if any(_real(g) for g in res) else None

    def _roots(self, w, depth, cognates):
        cands = self.candidates(w, depth, cognates)
        if not cands:
            return [], None
        rule, parts = cands[0]
        return parts, rule


def _real(group):
    return [a for a in group if 'id' in a]


def _merge(found):
    """Several sources of the same rank: the one with the most parts; one of the same
    shape adds its roots as alternatives part by part."""
    found = sorted(found, key=lambda g: -len(g))
    out = [list(x) for x in found[0]]
    for g in found[1:]:
        if len(g) == len(out):
            for k, x in enumerate(g):
                out[k] += [a for a in x if all(a.get('id') != y.get('id') or 'id' not in a for y in out[k])]
    return out


# -- consonant check for cognates ------------------------------------------
# Classes of consonants as Quenya keeps them: þ/th > s, w > v, kh > h, ñ > n, mb > m,
# nd > n, initial g- lost. A root's classes must appear in order in the word's.
_CLS = [
    set('kgcqxhɣ'), set('tdθþðs'), set('pbfvwɸβ'), set('m'), set('nñŋ'),
    set('l'), set('r'), set('yj'),
]


def _norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰√✶*!^#†()\-\s]', '', s)
    return s


def _classes(s, sindarin=False):
    """Consonant classes of a form, a repeated class once. Sindarin (sindarin=True):
    ch, dh, lh, rh, mh are single sounds, and m joins the labials (lenition m > v)."""
    s = _norm(s)
    if sindarin:
        s = s.replace('ch', 'x').replace('dh', 'ð').replace('lh', 'l').replace('rh', 'r').replace('mh', 'v')
    s = s.replace('kh', 'x').replace('th', 'θ').replace('ph', 'f').replace('qu', 'q') \
        .replace('kw', 'q').replace('gw', 'w').replace('ng', 'ŋ').replace('hy', 'h').replace('hl', 'l').replace('hr', 'r')
    out = []
    for ch in s:
        k = next((i for i, c in enumerate(_CLS) if ch in c), None)
        if k == 3 and sindarin:
            k = 2
        if k is not None and (not out or out[-1] != k):
            out.append(k)
    return out


def is_sindarin(lang):
    return lang in SINDARIN_LIKE


def same_onset(a, b):
    """Two forms begin alike: both with a vowel, or with consonants of the same class;
    a lost initial g-/w- (ᴱQ. gwes- ~ S. suil) also counts."""
    na, nb = _norm(a), _norm(b)
    va = bool(re.match(r'[aeiouy]', na))
    vb = bool(re.match(r'[aeiouy]', nb))
    ca, cb = _classes(a), _classes(b)
    if va and vb:
        return True
    if not va and not vb:
        return bool(ca and cb and ca[0] == cb[0])
    first = ca[0] if not va and ca else (cb[0] if cb else None)
    return first in (0, 2)


def _found(r, wc, skippable):
    """How many classes of r are found in order in wc when the classes in `skippable`
    may be missing from the word; None if some other class is not found."""
    best = None

    def go(i, j, n):
        nonlocal best
        if i == len(r):
            best = n if best is None else max(best, n)
            return
        for k in range(j, len(wc)):
            if wc[k] == r[i]:
                go(i + 1, k + 1, n + 1)
                break
        if r[i] in skippable:
            go(i + 1, j, n)
    go(0, 0, 0)
    return best


def consonants_match(word, root_form, sindarin=False):
    """The consonants of the root, in order, among the word's. At least two must be
    found, unless root and word both have a single consonant (Q. se < √S); a lost
    initial g-/w- of the root is allowed when the word begins with a vowel. In
    Sindarin a velar or y of the root may be missing anywhere (medial g lost, y > i),
    but the two consonants found are still required."""
    wc = _classes(word, sindarin)
    initial_vowel = bool(re.match(r'[aeiouáéíóúâêîôûäëïöüy]', _norm(word)))
    skippable = {0, 7} if sindarin else set()
    for variant in (root_form or '').split('/'):
        rc = _classes(variant, sindarin)
        if not rc:
            continue
        tries = [rc]
        if initial_vowel and rc[0] in (0, 2) and len(rc) > 1:
            tries.append(rc[1:])
        for r in tries:
            n = _found(r, wc, skippable)
            if n is None:
                continue
            if n >= 2 or (len(rc) == 1 and len(wc) == 1 and n == 1):
                return True
    return False


# -- the word list and the output --------------------------------------------

def group_words(d: Data, group: str):
    """The words vocabulary-index.xq lists for a group (id=nq or id=ns)."""
    langs = GROUPS[group]['langs']
    out = []
    for w in d.words:
        lang = d.lang(w)
        if lang not in langs or w.find('combine') is not None:
            continue
        sp = d.speech(w) or ''
        if sp.endswith('-name') or sp in ('text', 'phrase', 'grammar', 'root') or sp.startswith('phone'):
            continue
        if w.find('deprecated') is not None or w.find('see') is not None:
            continue
        if w.get('gloss') == '[unglossed]' or lang in FILTERED_LANGS:
            continue
        m = w.get('mark') or ''
        if '-' in m or '|' in m:
            continue
        out.append(w)
    return out


def normalize_spelling(v):
    """c:normalize-spelling (common.xq): the spelling of the Neo-Quenya list."""
    v1 = v.replace('q', 'qu').replace('quu', 'qu').replace('ks', 'x').replace('k', 'c')
    v2 = v1.replace('oa', 'öa').replace('ea', 'ëa')
    if v2 in ('nye', 'lye', 'tye') or len(re.sub('[¹²³⁴]', '', v2)) < 3:
        return v2
    m = re.match(r'^(.*)e(\)|¹|²|³|⁴)?$', v2)
    if m:
        return m.group(1) + 'ë' + (m.group(2) or '')
    return v2


class Out:
    def __init__(self, d: Data):
        self.d = d

    def word(self, pid):
        w = self.d.by_id[pid]
        rec = {'form': w.get('v'), 'lang': w.get('l'), 'url': SITE.format(pid)}
        if w.get('gloss'):
            rec['gloss'] = w.get('gloss')
        return rec

    def path(self, via):
        return [dict(self.word(pid), rel=rel) for rel, pid in via]

    def canonical(self, pid):
        """Where Eldamo merges a root: <combine> links followed to the end, then the
        Neo-Primitive root it is filed under, if any."""
        d = self.d
        chain, seen = [], {pid}
        cur = pid
        while cur in d.combined_into:
            nxt = d.combined_into[cur].get('page-id')
            if nxt in seen:
                break
            seen.add(nxt)
            chain.append(nxt)
            cur = nxt
        p = d.parent.get(d.by_id[cur])
        while p is not None and p.tag == 'word':
            if p.get('l') == 'np' and d.is_root(p) and p.get('page-id') not in seen:
                chain.append(p.get('page-id'))
                break
            p = d.parent.get(p)
        return chain

    def alt(self, a, part, several):
        if 'id' in a:
            rec = self.word(a['id'])
        elif a.get('gap'):
            rec = self.word(a['gap'])
        else:
            rec = {'form': a.get('form'), 'lang': a.get('lang'), 'url': None}
        if several:
            rec['part'] = part
        if a.get('via'):
            rec['via'] = self.path(a['via'])
        if a.get('partial'):
            rec['compound_cognate'] = True
        if a.get('unmatched'):
            # roots of a cognate's part whose consonants are not found in the word
            rec['not_matched'] = [self.word(x) for x in a['unmatched']]
        if 'id' in a:
            canon = self.canonical(a['id'])
            if canon:
                rec['same_as'] = [self.word(x) for x in canon]
        return rec


def canon_key(o: Out, pid):
    c = o.canonical(pid)
    return c[-1] if c else pid


def build(path):
    d = Data(path)
    R = Resolver(d)
    o = Out(d)
    entries = []
    for w in nq_words(d):
        pid = w.get('page-id')
        R.path.add(pid)
        cands = R.candidates(w, MAX_DEPTH, True)
        R.path.discard(pid)
        rule, parts = cands[0] if cands else (None, [])
        several = len(parts) > 1
        roots, gaps, seen = [], [], set()
        for k, g in enumerate(parts):
            for a in g:
                rec = o.alt(a, k, several)
                key = (k, rec.get('url'), rec.get('form'), 'id' in a)
                if key in seen:
                    continue
                seen.add(key)
                (roots if 'id' in a else gaps).append(rec)
        chosen = {canon_key(o, a['id']) for g in parts for a in g if 'id' in a}
        also = []
        for r2, p2 in cands[1:]:
            if r2 == 'cognate' and len(parts) > 1:
                continue            # a compound word: a cognate's root cannot be placed
            # the part is given when the other source has the same parts as the chosen one
            same_shape = several and len(p2) == len(parts)
            for k, g in enumerate(p2):
                for a in _real(g):
                    if a.get('partial'):
                        continue
                    ck = canon_key(o, a['id'])
                    if ck in chosen:
                        continue
                    chosen.add(ck)
                    rec = o.alt(a, k, same_shape)
                    rec['rule'] = r2
                    also.append(rec)
        lang = w.get('l')
        e = {
            'word': w.get('v'),
            'spelling': normalize_spelling(w.get('v')),
            'lang': lang,
            'lang_name': LANG_NAMES.get(lang, lang),
            'speech': w.get('speech') or d.speech(w),
            'gloss': w.get('gloss') or w.get('ngloss') or '',
            'url': SITE.format(pid),
        }
        if w.get('mark'):
            e['mark'] = w.get('mark')
        e['rule'] = rule
        weak = sorted({rel for g in parts for a in g for rel, _ in a.get('via', ()) if rel in WEAK_RULES})
        if rule in WEAK_RULES and rule not in weak:
            weak.insert(0, rule)
        if weak:
            # a root reached through a link that is not a derivation of the same word
            e['uncertain'] = weak
        e['roots'] = roots
        if gaps:
            e['gaps'] = gaps
        if also:
            e['also'] = also
        entries.append(e)
    entries.sort(key=lambda e: (_sort_key(e['spelling']), e['lang'], e['url']))
    return d, entries


def _sort_key(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(ch for ch in s if not unicodedata.combining(ch) and ch not in '¹²³⁴-()')


def _loose(form):
    return _norm(form).replace('k', 'c')


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    d, entries = build(argv[1])
    out = argv[2] if len(argv) > 2 else 'nq-roots.json'
    doc = {
        'source': {
            'eldamo_version': d.root.get('version'),
            'list': 'https://eldamo.org/content/vocabulary-indexes/vocabulary-words-nq.html',
        },
        'count': len(entries),
        'with_roots': sum(1 for e in entries if e['roots']),
        'by_rule': {k or 'none': v for k, v in sorted(
            __import__('collections').Counter(e['rule'] for e in entries).items(), key=lambda kv: -kv[1])},
        'uncertain': sum(1 for e in entries if e.get('uncertain')),
        'words': entries,
    }
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    from collections import Counter
    c = Counter(e['rule'] for e in entries)
    print(len(entries), 'words;', 'with roots:', sum(1 for e in entries if e['roots']), dict(c))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
