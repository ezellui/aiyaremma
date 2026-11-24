"""Dossier for the new concepts of list A (N1): for each concept, the sentences of its HWPh article(s)
that name a base philosopher, with column and the notes they call; own philosopher's sentences only
when they contain a German word of one of his existing concepts.
    python dossier.py <scratch> > dossier.txt"""
import json, re, sqlite3, sys, collections
S = sys.argv[1]
B = S + '/build/hwph_reader'
sys.path.insert(0, B); sys.path.insert(0, B + '/bridge')
import hwph_cite
from read_evidence import parse_article, name_patterns
from read_brief import sentences
from concept_de import DE
db = sqlite3.connect(B + '/hwph.sqlite')
pmap = json.load(open(S + '/stage/hwph_all/bridge_out/philosophers_hwph.json', encoding='utf-8'))
pats = name_patterns(db, pmap, hwph_cite)
C = json.load(open(S + '/m1/pat3/app/data/concepts.json', encoding='utf-8'))
by_phil = collections.defaultdict(list)
for c in C: by_phil[c['philosopher']].append(c)
n1 = json.load(open(S + '/stage/hwph_all/hwph_reader/bridge/review/n1/decisions.json', encoding='utf-8'))
A = collections.OrderedDict()
for x in n1:
    if x['verdict'] == 'A' and x['philosopher'] != 'nietzsche' or (x['verdict'] == 'A' and x['concept'] != 'Amor fati'):
        A.setdefault((x['philosopher'], x['concept']), []).append(x['article'])
only = sys.argv[2:]
for (ph, label), arts in A.items():
    if only and ph not in only: continue
    own_words = []
    for c in by_phil[ph]:
        for g in DE.get(c['id'], '').split('|'):
            g = re.split(r'[,;(/]', g)[0].strip()
            if len(g) >= 5: own_words.append((g, c['id']))
    print(f'\n######## {ph}: {label}')
    print('   свои концепции:', '; '.join(f"{c['id']}={c['label']}" for c in by_phil[ph]))
    for aid in arts:
        lemma, band, c0, c1 = db.execute('SELECT lemma, band, col_from, col_to FROM articles WHERE id=?', (aid,)).fetchone()
        paras, notes = parse_article(db, aid)
        named = collections.Counter()
        print(f'  == ‹{lemma}› Bd. {band}, Sp. {c0}–{c1} (id {aid})')
        for p in paras:
            if p['text'].startswith('## '):
                print('   ', p['text'][:120]); continue
            for s in sentences(p['text']):
                who = [q for q, rx in pats.items() if rx.search(s)]
                others = [q for q in who if q != ph]
                ow = [cid for g, cid in own_words if g.lower() in s.lower()] if ph in who else []
                if not others and not ow: continue
                for q in who: named[q] += 1
                fn = re.findall(r'\[(\d+)\]', s)
                nt = ' | '.join(notes[k]['text'][:150] for k in notes if notes[k]['n'] in fn)
                tag = ','.join(others) + (f' (свои: {",".join(sorted(set(ow)))})' if ow else '')
                print(f"   · Sp. {p['c_from']}{'–' + str(p['c_to']) if p['c_to'] != p['c_from'] else ''} [{tag}] {s[:700]}" + (f"\n        ⟶ {nt[:400]}" if nt else ''))
        print('   названы:', dict(named.most_common()))
