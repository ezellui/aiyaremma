"""Run a word form through the sound changes of a branch in chronological order.

Rule order is (language stage, Eldamo @order). Rules without @order are all
primitive (✶, ᴹ✶); their position is inferred from the attested derivations:
the orders of the ordered rules applied just before and after them.

A rule is applied with all its sub-formulas at once (a sound law); the rule's
unchanged sub-formulas (mb > mb) protect their sites. Rules named as optional
or irregular ("often", "sometimes", "usually", ...) branch: the form with and
the form without the change are both kept. The number of variants is capped.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from . import interpreter
from .interpreter import Unsupported, comparable

OPTIONAL = re.compile(r'\b(often|sometimes|usually|occasionally|generally|sporadically|may|might)\b', re.I)
MAX_VARIANTS = 24


@dataclass
class CompiledRule:
    id: str
    name: str
    lang: str
    stage: int
    era: str
    order: float
    optional: bool
    rule: object | None             # interpreter.Rule of the changing sub-formulas
    protect: object | None          # interpreter.Rule of the unchanged ones
    unsupported: list = field(default_factory=list)


def _compile(rule: dict, pairs: dict, langs: dict, order: float) -> CompiledRule:
    changing, unchanged, bad = [], [], []
    for pid in rule['pairs']:
        p = pairs[pid]
        if not p.get('in_branch', True):
            continue
        try:
            compiled = interpreter.compile_rule(p['from'] or '', p['to'])
        except Unsupported as exc:
            bad.append(f"{p['from']} > {p['to']}: {exc}")
            continue
        (unchanged if p['kind'] == 'identity' else changing).append(compiled)
    L = langs[rule['lang']]
    return CompiledRule(
        id=rule['id'], name=rule['name'], lang=rule['lang'], stage=L['stage'], era=L['era'], order=order,
        optional=bool(OPTIONAL.search(rule['name'])),
        rule=interpreter.combine(changing) if changing else None,
        protect=interpreter.combine(unchanged) if unchanged else None,
        unsupported=bad)


def infer_orders(rules: list, pairs: dict, derivations: list) -> dict:
    """Position for rules without @order, from their neighbours in derivations."""
    known = {r['id']: r['order'] for r in rules if r['order'] is not None}
    lang_of = {r['id']: r['lang'] for r in rules}
    low, high = defaultdict(list), defaultdict(list)
    for d in derivations:
        seq = [pairs[s['pair']]['rule'] for s in d['steps'] if s['pair'] in pairs]
        for i, rid in enumerate(seq):
            if rid in known:
                continue
            before = [known[x] for x in seq[:i] if x in known and lang_of[x] == lang_of[rid]]
            after = [known[x] for x in seq[i + 1:] if x in known and lang_of[x] == lang_of[rid]]
            if before:
                low[rid].append(max(before))
            if after:
                high[rid].append(min(after))
    out = {}
    for r in rules:
        if r['order'] is not None:
            continue
        lo = max(low[r['id']]) if low[r['id']] else None
        hi = min(high[r['id']]) if high[r['id']] else None
        if lo is not None and hi is not None and lo < hi:
            out[r['id']] = (lo + hi) / 2
        elif lo is not None:
            out[r['id']] = lo + 0.5
        elif hi is not None:
            out[r['id']] = hi - 0.5
        else:
            out[r['id']] = None   # never attested next to an ordered rule
    return out


class Sequencer:
    def __init__(self, data: dict):
        self.langs = {l['code']: l for l in data['meta']['languages']}
        pairs = {p['id']: p for p in data['pairs']}
        inferred = infer_orders(data['rules'], pairs, data['derivations'])
        self.rules = []
        self.unplaced = []
        for r in data['rules']:
            order = r['order'] if r['order'] is not None else inferred.get(r['id'])
            if order is None:
                self.unplaced.append(r['id'])
                order = 1e9   # end of its stage
            self.rules.append(_compile(r, pairs, self.langs, order))
        self.rules.sort(key=lambda c: (c.era, c.stage, c.order, c.id))
        self.by_id = {c.id: c for c in self.rules}

    def sequence(self, era: str, first_stage: int, last_stage: int, after_order: float | None = None):
        """Rules of one era from first_stage to last_stage, optionally only those
        after a given order within the first stage."""
        out = []
        for c in self.rules:
            if c.era != era or not (first_stage <= c.stage <= last_stage):
                continue
            if after_order is not None and c.stage == first_stage and c.order <= after_order:
                continue
            out.append(c)
        return out

    def run(self, form: str, rules: list, branch_optional: bool = True) -> list:
        """Apply rules in order. Returns variants: [{'form', 'trace'}], the first
        being the main reading (optional rules applied)."""
        variants = [{'form': form, 'trace': []}]
        for c in rules:
            if c.rule is None:
                continue
            nxt = []
            for v in variants:
                try:
                    res = interpreter.apply_rule(c.rule, v['form'], protect=c.protect)
                except Unsupported:
                    nxt.append(v)
                    continue
                outs = sorted(res['all_sites'])
                if not outs:
                    nxt.append(v)
                    continue
                for o in outs:
                    nxt.append({'form': o, 'trace': v['trace'] + [(c.id, v['form'], o)]})
                if c.optional and branch_optional:
                    nxt.append({'form': v['form'], 'trace': v['trace'] + [(c.id, v['form'], None)]})
            seen, variants = set(), []
            for v in nxt:
                key = comparable(v['form'])
                if key not in seen:
                    seen.add(key)
                    variants.append(v)
            variants = variants[:MAX_VARIANTS]
        return variants


def backtest(data: dict, seq: Sequencer | None = None) -> dict:
    """Replay every attested derivation of the branch from its start form."""
    seq = seq or Sequencer(data)
    langs = seq.langs
    results = []
    for d in data['derivations']:
        if d['deleted'] or not d['steps']:
            continue
        codes = [s['lang'] for s in d['steps']]
        if any(c not in langs for c in codes):
            continue
        era = langs[codes[0]]['era']
        if any(langs[c]['era'] != era for c in codes):
            continue
        first, last = langs[codes[0]]['stage'], langs[codes[-1]]['stage']
        rules = seq.sequence(era, first, last)
        variants = seq.run(d['start'], rules)
        target = comparable(d['steps'][-1]['after'])
        forms = [comparable(v['form']) for v in variants]
        main = forms[0] == target
        anyv = target in forms
        diverge = None
        if not main:
            # first attested intermediate form the main reading never passes through
            passed = {comparable(d['start'])} | {comparable(t[2]) for t in variants[0]['trace'] if t[2]}
            for s in d['steps']:
                if comparable(s['after']) not in passed:
                    diverge = {'pair': s['pair'], 'expected': s['after']}
                    break
        results.append({'derivation': d['id'], 'word': d['word_form'], 'start': d['start'],
                        'target': d['steps'][-1]['after'], 'main': variants[0]['form'],
                        'variants': len(variants), 'ok_main': main, 'ok_any': anyv, 'diverge': diverge,
                        'steps': len(d['steps'])})
    n = len(results)
    return {
        'derivations': n,
        'main': sum(r['ok_main'] for r in results),
        'any': sum(r['ok_any'] for r in results),
        'results': results,
        'unplaced_rules': seq.unplaced,
    }
