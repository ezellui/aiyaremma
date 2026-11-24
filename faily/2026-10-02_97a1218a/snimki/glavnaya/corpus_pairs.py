"""Co-mentions of two philosophers across the WHOLE HWPh corpus (SPEC §9.2).

The bridge looks for evidence of a relation only in the articles matched to its two concepts.
This tool takes every article where both philosophers are cited (`cites`), finds windows of up
to W sentences naming both (school adjectives «platonisch», «Kantianer» count as naming), and
ranks them by words fitting the relation type (read_brief.KW) plus German words of both concepts
(guesses from concepts_hwph.json): a window that names both philosophers AND both ideas is what
a relation needs.

    python corpus_pairs.py --hwph … --philosphaira … --out … rel_… rel_…
    python corpus_pairs.py … --group h1_not_supported [--skip 0 --top 20]
    python corpus_pairs.py … --group same_article [--skip 0 --top 20]
        [--n 3] [--W 3] [--maxart 80] [--clip 650] [--nclip 160] [--dclip 400] [--need-concept]
"""
import argparse, json, os, re, sqlite3, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from read_evidence import parse_article, name_patterns
from read_brief import KW, TYPES, sentences
from concept_brief import stems

SUF = r'(?:eer|eisch|isch|ische[nmrs]?|sch|ianer|ianismus|ismus|iker|isten?)'
NOADJ = {'zeno_stoic', 'marcus_aurelius', 'sextus', 'al_farabi', 'socrates'}

def with_adjectives(pats, pmap):
    for ph, e in pmap.items():
        if ph not in pats or ph in NOADJ: continue
        last = e['hwph_names'][0].split()[-1]
        st = re.sub(r'(as|es|os|us|is|on|e)$', '', last) if len(last) > 5 else last
        if len(st) < 4: continue
        rx = '(?:' + st[0].upper() + '|' + st[0].lower() + ')' + re.escape(st[1:]) + SUF + r'\w*'
        pats[ph] = re.compile('(?:' + pats[ph].pattern + ')|' + rx)
    return pats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hwph', required=True); ap.add_argument('--philosphaira', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('ids', nargs='*'); ap.add_argument('--group', choices=['h1_not_supported', 'same_article'])
    ap.add_argument('--journal', default=os.path.join(HERE, 'review', 'decisions.json'))
    ap.add_argument('--skip', type=int, default=0); ap.add_argument('--top', type=int, default=20)
    ap.add_argument('--n', type=int, default=3); ap.add_argument('--W', type=int, default=3); ap.add_argument('--maxart', type=int, default=80)
    ap.add_argument('--clip', type=int, default=650); ap.add_argument('--nclip', type=int, default=160); ap.add_argument('--dclip', type=int, default=400)
    ap.add_argument('--need-concept', action='store_true', help='show only windows with a word of at least one concept')
    a = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(a.hwph))); import hwph_cite
    db = sqlite3.connect(a.hwph); data = os.path.join(a.philosphaira, 'app', 'data')
    C = {c['id']: c for c in json.load(open(data + '/concepts.json', encoding='utf-8'))}
    P = {p['id']: p for p in json.load(open(data + '/philosophers.json', encoding='utf-8'))}
    R = {r['id']: r for r in json.load(open(data + '/relations.json', encoding='utf-8'))}
    CM = json.load(open(os.path.join(a.out, 'concepts_hwph.json'), encoding='utf-8'))
    pmap = json.load(open(os.path.join(a.out, 'philosophers_hwph.json'), encoding='utf-8'))
    art = {x[0]: x for x in db.execute('SELECT id, lemma, band FROM articles')}
    pats = with_adjectives(name_patterns(db, pmap, hwph_cite), pmap); cache = {}
    ids = list(a.ids)
    if a.group == 'h1_not_supported':
        J = json.load(open(a.journal, encoding='utf-8'))
        ids = [x['id'] for x in J if x['verdict'] == 'not_supported' and 'РЕШЕНО' not in x.get('note', '')]
    elif a.group == 'same_article':
        ev = json.load(open(os.path.join(a.out, 'relations_evidence.json'), encoding='utf-8'))
        ids = sorted(r['id'] for r in ev if r['verdict'] == 'hwph_same_article' and not r.get('provenance_status'))
    if a.group: ids = ids[a.skip:a.skip + a.top]
    lab = lambda c: f'{C[c]["label"]} ({P[C[c]["philosopher"]]["nameRu"]})'
    for rid in ids:
        r = R.get(rid)
        if not r: print(f'\n=== {rid}: нет в данных'); continue
        p1, p2 = C[r['source']]['philosopher'], C[r['target']]['philosopher']
        arrow = '⇄' if r.get('bidirectional') else '→'
        print(f'\n=== {rid}  {lab(r["source"])} —{r["type"]}/{r.get("weight")}{arrow} {lab(r["target"])}')
        print(f'  ОПИС: {r.get("description", "")[:a.dclip]}')
        if p1 not in pats or p2 not in pats or p1 == p2: print('  (философа нет в HWPh или связь внутрисистемная)'); continue
        q = ('SELECT c1.aid, c1.n_body + c2.n_body s FROM cites c1 JOIN cites c2 ON c1.aid = c2.aid '
             'WHERE c1.pid IN (%s) AND c2.pid IN (%s) ORDER BY s DESC')
        ids1, ids2 = pmap[p1]['hwph_persons'], pmap[p2]['hwph_persons']
        rows = db.execute(q % (','.join('?' * len(ids1)), ','.join('?' * len(ids2))), ids1 + ids2).fetchall()
        aids = list(dict.fromkeys(x[0] for x in rows if x[0] in art))[:a.maxart]
        s1 = stems(CM.get(r['source'], {}).get('guesses', ''), [])
        s2 = stems(CM.get(r['target'], {}).get('guesses', ''), [])
        kinds = TYPES.get(r['type'], ('pos', 'neg'))
        ws = []
        for aid in aids:
            if aid not in cache: cache[aid] = parse_article(db, aid)
            paras, notes = cache[aid]
            for pi, p in enumerate(paras):
                if p['text'].startswith('## '): continue
                ss = sentences(p['text'])
                for i in range(len(ss)):
                    for w in range(1, a.W + 1):
                        if i + w > len(ss): continue
                        chunk = ' '.join(ss[i:i + w])
                        if not (pats[p1].search(chunk) and pats[p2].search(chunk)): continue
                        if w > 1 and any(pats[p1].search(t) and pats[p2].search(t) for t in (' '.join(ss[i:i + w - 1]), ' '.join(ss[i + 1:i + w]))): continue
                        low = chunk.lower()
                        h1, h2 = any(x in low for x in s1), any(x in low for x in s2)
                        if a.need_concept and not (h1 or h2): continue
                        score = (3 if w == 1 else 2 if w == 2 else 1) + 3 * h1 + 3 * h2 + sum(4 for k in kinds if re.search(KW[k], chunk))
                        if len(chunk) > 1000: score -= 2
                        ws.append((score, aid, pi, i, chunk, p, re.findall(r'\[(\d+)\]', chunk), h1, h2))
        ws.sort(key=lambda w: -w[0]); taken = []
        for w in ws:
            if any(t[1] == w[1] and t[2] == w[2] and abs(t[3] - w[3]) <= 2 for t in taken): continue
            taken.append(w)
            if len(taken) >= a.n: break
        print(f'  статей с обоими: {len(rows)}, просмотрено {len(aids)}, окон {len(ws)}')
        for score, aid, pi, si, chunk, p, fns, h1, h2 in taken:
            cols = f'{p["c_from"]}' + (f'–{p["c_to"]}' if p['c_to'] != p['c_from'] else '')
            mark = ('И' if h1 else '·') + ('Ц' if h2 else '·')
            print(f'  · ‹{art[aid][1]}› Bd. {art[aid][2]}, Sp. {cols} [{score} {mark}]: {chunk[:a.clip]}')
            notes = cache[aid][1]
            for n in fns:
                f = next((k for k in p['fns'] if notes.get(k, {}).get('n') == n), None)
                if f: print(f'      [{n}] {notes[f]["text"][:a.nclip]}')

if __name__ == '__main__':
    main()
