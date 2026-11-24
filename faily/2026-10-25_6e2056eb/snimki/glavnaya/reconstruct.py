"""Reconstruction of a word's form for another period (docs/period-reconstruction-plan.md).

A period is (branch, era, stage): Quenya or Sindarin; Tolkien's late, middle
or early conception; a stage of the language (0 = the primitive form as Eldamo
writes it, before the rules of Primitive Elvish; s >= 1 = the form at the end
of that stage's rules).

Routes, chosen by source and target:

* forward   -- same branch and era, later stage: the sound laws (sequencer);
* backward  -- same branch and era, earlier stage: candidates from learnt
               correspondences, each verified by running the laws forward;
               directly between the two stages and through the primitive form;
* sideways  -- other branch, same era (a cognate): back to the primitive form
               in one branch, forward in the other;
* across    -- other era (Tolkien's conceptions): Eldamo's own links between
               the pages first (combine, deprecated), then the form unchanged if
               the target language allows it, then re-etymologization (Strack's
               method for Neo-Eldarin): back to the primitive form, over to the
               other conception's primitive, forward by its laws. Such forms are
               marked as neologisms.

Every variant carries its route, the rules applied and what supports it:
an attested form of Eldamo, an Eldamo link, a verified reconstruction.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from . import backform as BF
from .compound import origins
from .interpreter import comparable, is_vowel, join, phonemes
from .orthography import to_phonetic
from .sequencer import Sequencer, _replays

LIMIT = 8
ROOT_BONUS = 2.0
EQUIV = [set('kgxɣhq'), set('tdθðþ'), set('pbɸβfv'), set('mṃ'), set('nŋñṇ'), set('l'), set('r'), set('sz'), set('w'),
         set('jy')]


# --------------------------------------------------------------------------
# normalized derivations: the form at the end of every stage

def normalize(data: dict, seq: Sequencer) -> list:
    """For each replayable derivation whose replay reaches the attested form:
    {'derivation', 'word', 'era', 'forms': {stage: form}}. Stage 0 is the start
    (Eldamo's primitive form); later stages are the forms after the last rule
    of that stage in the reproducing replay."""
    out = []
    langs = seq.langs
    for d, variants in _replays(data, seq):
        target = comparable(d['steps'][-1]['after'])
        hit = next((v for v in variants if comparable(v['form']) == target), None)
        if hit is None:
            continue
        codes = [s['lang'] for s in d['steps']]
        era = langs[codes[0]]['era']
        first, last = langs[codes[0]]['stage'], langs[codes[-1]]['stage']
        forms = {max(first - 1, 0): d['start']}
        current = d['start']
        by_stage = {}
        for rid, _before, after in hit['trace']:
            if after is not None:
                current = after
                by_stage[seq.by_id[rid].stage] = current
        cur = d['start']
        for s in range(first, last + 1):
            cur = by_stage.get(s, cur)
            if s > 0:
                forms[s] = cur
        forms[last] = d['steps'][-1]['after']
        out.append({'derivation': d['id'], 'word': d['word'], 'era': era, 'forms': forms,
                    'main': hit is variants[0]})
    return out


# --------------------------------------------------------------------------
# helpers

def _skeleton(root_form: str) -> list:
    """Consonant classes of a root: MBAR -> [m, b, r] as equivalence classes."""
    f = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰√()\-]', '', root_form).lower()
    f = f.replace('kh', 'x').replace('th', 'θ').replace('ph', 'f').replace('gw', 'g').replace('kw', 'k')
    out = []
    for ch in f:
        cls = next((i for i, c in enumerate(EQUIV) if ch in c), None)
        if cls is not None:
            out.append(cls)
    return out


def _classes(form: str) -> list:
    out = []
    for p in phonemes(comparable(form)):
        if is_vowel(p):
            continue
        b = p[0]
        cls = next((i for i, c in enumerate(EQUIV) if b in c), None)
        if cls is not None:
            out.append(cls)
    return out


def root_match(form: str, roots: list) -> bool:
    """The consonants of a root appear in order in the form (by sound class)."""
    cs = _classes(form)
    for r in roots:
        sk = _skeleton(r)
        if not sk:
            continue
        it = iter(cs)
        if all(any(c == k for c in it) for k in sk):
            return True
    return False


class Phonotactics:
    """Word-final consonants and consonant clusters of a language's words."""

    def __init__(self, forms: list):
        self.finals, self.clusters, self.initials = Counter(), Counter(), Counter()
        for f in forms:
            ph = phonemes(comparable(f))
            if not ph:
                continue
            if not is_vowel(ph[-1]):
                self.finals[ph[-1]] += 1
            run, start = [], True
            for p in ph + ['#']:
                if p != '#' and not is_vowel(p):
                    run.append(p)
                    continue
                if len(run) > 1:
                    (self.initials if start else self.clusters)[''.join(run)] += 1
                start = start and not run and p == '#'
                start = False
                run = []

    def problems(self, form: str, min_count: int = 2) -> list:
        ph = phonemes(comparable(form))
        out = []
        if ph and not is_vowel(ph[-1]) and self.finals[ph[-1]] < min_count:
            out.append(f'конечный {ph[-1]}')
        run, first = [], True
        for p in ph + ['#']:
            if p != '#' and not is_vowel(p):
                run.append(p)
                continue
            if len(run) > 1:
                c = ''.join(run)
                seen = self.initials[c] if first else self.clusters[c] + self.initials[c]
                if seen < min_count and not (not first and p == '#' and self.clusters[c] + self.finals[run[-1]] >= min_count):
                    out.append(f'сочетание {c}')
            first = False
            run = []
        return out


# --------------------------------------------------------------------------
# context

class Context:
    """Everything reconstruction needs for both branches."""

    def __init__(self, branches: dict):
        self.data = branches
        self.seq = {b: Sequencer(d) for b, d in branches.items()}
        self.lexicon = {b: {e['id']: e for e in d['lexicon']} for b, d in branches.items()}
        self.normal = {b: normalize(d, self.seq[b]) for b, d in branches.items()}
        self._tables = {}
        self._phonotactics = {}
        self.reverse_links = defaultdict(list)    # target id -> [(source id, tag)]
        for b, lex in self.lexicon.items():
            for e in lex.values():
                for tag, ls in e.get('links', {}).items():
                    for x in ls:
                        self.reverse_links[x['id']].append((e['id'], tag))

    # -- languages ---------------------------------------------------------
    def langs(self, branch: str) -> dict:
        return self.seq[branch].langs

    def code(self, branch: str, era: str, stage: int) -> str | None:
        return next((l['code'] for l in self.langs(branch).values() if l['era'] == era and l['stage'] == stage), None)

    def last_stage(self, branch: str, era: str) -> int:
        return max(l['stage'] for l in self.langs(branch).values() if l['era'] == era)

    def entry(self, wid: str):
        for b, lex in self.lexicon.items():
            if wid in lex:
                return b, lex[wid]
        return None, None

    # -- learnt tables -----------------------------------------------------
    def table(self, branch: str, era: str, src: int, dst: int, exclude=frozenset()) -> dict:
        """Correspondences 'form at stage dst <- form at stage src' from the
        normalized derivations (dst < src)."""
        key = (branch, era, src, dst, exclude)
        if key not in self._tables:
            pairs = [(n['forms'][dst], n['forms'][src]) for n in self.normal[branch]
                     if n['era'] == era and src in n['forms'] and dst in n['forms']
                     and n['derivation'] not in exclude]
            self._tables[key] = BF.learn_pairs(pairs)
        return self._tables[key]

    def phonotactics(self, branch: str, code: str) -> Phonotactics:
        if (branch, code) not in self._phonotactics:
            fam = branch
            forms = [to_phonetic(e['form'], fam).strip('-') for e in self.lexicon[branch].values()
                     if e['lang'] == code and not e.get('neo') and ' ' not in e['form']]
            self._phonotactics[(branch, code)] = Phonotactics(forms)
        return self._phonotactics[(branch, code)]

    # -- routes ------------------------------------------------------------
    def forward(self, branch: str, era: str, form: str, src: int, dst: int) -> list:
        """[(form, trace)] main reading first."""
        seq = self.seq[branch]
        rules = seq.sequence(era, src + 1 if src > 0 else 0, dst)
        return [(v['form'], v['trace']) for v in seq.run(form, rules)]

    def backward(self, branch: str, era: str, form: str, src: int, dst: int, roots=(), exclude=frozenset(),
                 limit: int = LIMIT) -> list:
        """[{'form', 'p', 'trace', 'root', 'via'}]: forms at stage dst that give `form`
        at stage src; directly and, for dst > 0, through the primitive form."""
        seq = self.seq[branch]
        out = {}

        def add(f, p, trace, via):
            k = comparable(f)
            rec = {'form': f, 'p': p, 'trace': trace, 'via': via, 'root': bool(roots) and root_match(f, roots)}
            if k not in out or out[k]['p'] < p:
                out[k] = rec

        first = dst + 1 if dst > 0 else 0
        found = BF.backform(seq, self.table(branch, era, src, dst, exclude), form, era, src, limit=limit,
                            first_stage=first, beam=BF.BEAM)
        for f in found:
            add(f['primitive'], math.exp(f['logp']) * (1.0 if f['main'] else 0.5), f['trace'], 'direct')
        if dst > 0:
            prims = BF.backform(seq, self.table(branch, era, src, 0, exclude), form, era, src, limit=4)
            for f in prims:
                for k, (g, trace) in enumerate(self.forward(branch, era, f['primitive'], 0, dst)[:2]):
                    add(g, math.exp(f['logp']) * (1.0 if f['main'] else 0.5) * (1.0 if k == 0 else 0.5), trace,
                        'primitive ' + f['primitive'])
        ranked = sorted(out.values(), key=lambda r: -(r['p'] * (ROOT_BONUS if r['root'] else 1.0)))
        return ranked[:limit]


# --------------------------------------------------------------------------
# the entry point

def _stage_form(ctx: Context, branch: str, entry: dict, era: str, stage: int) -> list:
    """Attested forms of a word at a stage of its own branch and era: its own
    form at its language's stage, its derivation forms, its primitive forms."""
    code = ctx.code(branch, era, stage)
    out = []
    if code and entry['lang'] == code:
        out.append(to_phonetic(entry['form'], branch).strip('-'))
    if stage == 0:
        out += origins(entry, era)
    elif code:
        out += list(entry.get('stages', {}).get(code, ()))
    return list(dict.fromkeys(f for f in out if f))


def _roots(entry: dict | None) -> list:
    return [r['form'] for r in (entry or {}).get('roots', ())]


def reconstruct(ctx: Context, src: tuple, dst: tuple, form: str | None = None, word: str | None = None,
                limit: int = LIMIT, use_links: bool = True, exclude=frozenset()) -> list:
    """Variants of the form at dst = (branch, era, stage), from the form at src.

    Either `word` (an Eldamo page id) or `form` (phonetic, or Tolkien's spelling
    at the latest stage) gives the source. Returns
    [{'form', 'score', 'route', 'marks', 'steps'}], most probable first."""
    sb, se, ss = src
    db, de, ds = dst
    entry = None
    if word:
        _, entry = ctx.entry(word)
    if form is None:
        if entry is None:
            return []
        forms = _stage_form(ctx, sb, entry, se, ss)
        if not forms and entry['lang'] == ctx.code(sb, se, ss):
            forms = [to_phonetic(entry['form'], sb)]
        if not forms:
            return []
        form = forms[0]
    elif ss == ctx.last_stage(sb, se):
        form = to_phonetic(form, sb).strip('-')
    roots = _roots(entry)
    results = {}

    def add(f, score, route, marks, steps):
        k = comparable(f)
        rec = {'form': f.replace('+', ''), 'score': score, 'route': route, 'marks': marks, 'steps': steps}
        if k not in results or results[k]['score'] < score:
            results[k] = rec

    # attested in Eldamo: the word's own forms at the target period
    if entry is not None and (db, de) == (sb, se):
        for f in _stage_form(ctx, db, entry, de, ds):
            add(f, 10.0, 'засвидетельствовано', ['attested'], [])

    if (db, de) == (sb, se):
        _within(ctx, add, sb, se, form, ss, ds, roots, exclude)
    elif de == se:
        _sideways(ctx, add, src, dst, form, entry, roots, exclude)
    else:
        _across(ctx, add, src, dst, form, entry, roots, exclude, use_links)

    ranked = sorted(results.values(), key=lambda r: -r['score'])
    total = sum(r['score'] for r in ranked) or 1.0
    for r in ranked:
        r['score'] = round(r['score'] / total, 3)
    return ranked[:limit]


def _within(ctx, add, branch, era, form, ss, ds, roots, exclude, base_score=1.0, route_prefix='', marks=()):
    if ds == ss:
        add(form, base_score, route_prefix + 'та же стадия', list(marks), [])
    elif ds > ss:
        for k, (f, trace) in enumerate(ctx.forward(branch, era, form, ss, ds)[:4]):
            add(f, base_score * (1.0 if k == 0 else 0.5 / k), route_prefix + 'вперёд по законам',
                list(marks) + (['main'] if k == 0 else []), trace)
    else:
        found = ctx.backward(branch, era, form, ss, ds, roots, exclude)
        top = max((r['p'] for r in found), default=1.0) or 1.0
        for r in found:
            p = base_score * 0.9 * (r['p'] / top) * (ROOT_BONUS if r['root'] else 1.0)
            add(r['form'], p, route_prefix + 'назад: ' + ('напрямую' if r['via'] == 'direct' else 'через праформу'),
                list(marks) + ['reconstructed'] + (['root'] if r['root'] else []), r['trace'])


def _sideways(ctx, add, src, dst, form, entry, roots, exclude):
    sb, era, ss = src
    db, _, ds = dst
    prims = []
    if entry is not None:
        prims = [(f, 1.0, ['primitive-attested']) for f in origins(entry, era)]
    if not prims:
        if ss == 0:
            prims = [(form, 1.0, [])]
        else:
            found = ctx.backward(sb, era, form, ss, 0, roots, exclude)
            top = max((r['p'] for r in found), default=1.0) or 1.0
            prims = [(r['form'], (r['p'] / top) * (ROOT_BONUS if r['root'] else 1.0), ['reconstructed'])
                     for r in found[:5]]
    for prim, w, marks in prims:
        _within(ctx, add, db, era, prim, 0, ds, (), exclude, base_score=w,
                route_prefix=f'через праформу {prim}: ', marks=marks + ['cognate'])


def _across(ctx, add, src, dst, form, entry, roots, exclude, use_links):
    sb, se, ss = src
    db, de, ds = dst
    dst_code = ctx.code(db, de, ds)
    # (a) Eldamo's links between conceptions
    if use_links and entry is not None:
        linked = []
        for tag, ls in entry.get('links', {}).items():
            if tag in ('combine', 'deprecated', 'see'):
                linked += [(x['id'], tag) for x in ls]
        linked += ctx.reverse_links.get(entry['id'], [])
        for wid, tag in linked:
            b2, e2 = ctx.entry(wid)
            if e2 is None or b2 != db:
                continue
            l2 = ctx.langs(db).get(e2['lang'])
            if l2 is None or l2['era'] != de:
                continue
            f2 = to_phonetic(e2['form'], db).strip('-')
            if l2['stage'] == ds:
                add(f2, 5.0, f'связь Eldamo ({tag}): {e2["form"]}', ['link'], [])
            else:
                _within(ctx, add, db, de, f2, l2['stage'], ds, _roots(e2), exclude, base_score=4.0,
                        route_prefix=f'связь Eldamo ({tag}) {e2["form"]}, затем ', marks=['link'])
    # (b) unchanged, when the target language allows the form
    if ss == ctx.last_stage(sb, se) and ds == ctx.last_stage(db, de) and sb == db and dst_code:
        problems = ctx.phonotactics(db, dst_code).problems(form)
        add(form, 1.0 if not problems else 0.15, 'без изменений' + (f" (нетипично для языка: {', '.join(problems)})" if problems else ''),
            ['unchanged'] + (['phonotactics'] if problems else []), [])
    # (c) re-etymologization: primitive of the source conception -> laws of the target one
    prims = []
    if entry is not None:
        prims = [(f, 1.0) for f in origins(entry, se)]
    if not prims:
        if ss == 0:
            prims = [(form, 1.0)]
        else:
            found = ctx.backward(sb, se, form, ss, 0, roots, exclude)
            top = max((r['p'] for r in found), default=1.0) or 1.0
            prims = [(r['form'], (r['p'] / top) * (ROOT_BONUS if r['root'] else 1.0)) for r in found[:4]]
    for prim, w in prims:
        _within(ctx, add, db, de, prim, 0, ds, (), exclude, base_score=0.6 * w,
                route_prefix=f'переэтимологизация через праформу {prim}: ', marks=['neologism'])


# --------------------------------------------------------------------------
# evaluation on Eldamo (reports/reconstruction.md)

def evaluate(ctx: Context, sample: int = 80) -> dict:
    import random
    rnd = random.Random(11)
    out = {}
    for b in ctx.data:
        res = {}
        # A: backward from the last stage of an era to each earlier stage
        for era in ('late', 'middle', 'early'):
            last = ctx.last_stage(b, era)
            norm = [n for n in ctx.normal[b] if n['era'] == era and last in n['forms']]
            held = norm[1::2]
            exclude = frozenset(n['derivation'] for n in held)
            for t in range(last):
                cases = [n for n in held if t in n['forms']]
                cases = rnd.sample(cases, min(sample, len(cases)))
                st = Counter()
                for n in cases:
                    vs = reconstruct(ctx, (b, era, last), (b, era, t), form=n['forms'][last], exclude=exclude)
                    want = comparable(n['forms'][t])
                    got = [comparable(v['form']) for v in vs]
                    st['cases'] += 1
                    st['found'] += bool(got)
                    st['first'] += bool(got) and got[0] == want
                    st['any'] += want in got
                res[f'{era}: {last} -> {t}'] = dict(st)
        out[b] = res
    # B: cognates with the same primitive form, Q <-> S (late)
    starts = defaultdict(dict)
    for b in ctx.data:
        last = ctx.last_stage(b, 'late')
        for n in ctx.normal[b]:
            if n['era'] == 'late' and 0 in n['forms'] and last in n['forms']:
                starts[comparable(n['forms'][0])][b] = n['forms'][last]
    pairs = [(v['quenya'], v['sindarin']) for v in starts.values() if 'quenya' in v and 'sindarin' in v]
    for (sb, db), idx in ((('quenya', 'sindarin'), (0, 1)), (('sindarin', 'quenya'), (1, 0))):
        st = Counter()
        for p in rnd.sample(pairs, min(sample, len(pairs))):
            src_form, want = p[idx[0]], comparable(p[idx[1]])
            vs = reconstruct(ctx, (sb, 'late', ctx.last_stage(sb, 'late')), (db, 'late', ctx.last_stage(db, 'late')),
                             form=src_form)
            got = [comparable(v['form']) for v in vs]
            st['cases'] += 1
            st['first'] += bool(got) and got[0] == want
            st['any'] += want in got
        st['pairs'] = len(pairs)
        out[f'cognates {sb} -> {db}'] = dict(st)
    # C: conceptions, without using the link being tested
    for b, src_code, dst_code in (('quenya', 'mq', 'q'), ('sindarin', 'n', 's'), ('quenya', 'eq', 'q'),
                                  ('sindarin', 'g', 's')):
        lex = ctx.lexicon[b]
        langs = ctx.langs(b)
        pairs = []
        for e in lex.values():
            if e['lang'] != src_code or e.get('neo'):
                continue
            for tag in ('combine', 'deprecated'):
                for x in e.get('links', {}).get(tag, ()):
                    t = lex.get(x['id'])
                    if t is not None and t['lang'] == dst_code:
                        pairs.append((e['id'], t['id']))
        pairs = list(dict.fromkeys(pairs))
        st = Counter()
        sl, dl = langs[src_code], langs[dst_code]
        for a, t in rnd.sample(pairs, min(sample, len(pairs))):
            want = comparable(to_phonetic(lex[t]['form'], b).strip('-'))
            vs = reconstruct(ctx, (b, sl['era'], sl['stage']), (b, dl['era'], dl['stage']), word=a, use_links=False)
            got = [comparable(v['form']) for v in vs]
            st['cases'] += 1
            st['identity'] += comparable(to_phonetic(lex[a]['form'], b).strip('-')) == want
            st['first'] += bool(got) and got[0] == want
            st['any'] += want in got
        st['pairs'] = len(pairs)
        out[f'conceptions {src_code} -> {dst_code}'] = dict(st)
    return out
