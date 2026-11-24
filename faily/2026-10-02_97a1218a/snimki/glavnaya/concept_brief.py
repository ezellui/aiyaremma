"""Compact reading of HWPh evidence for CONCEPTS (заход C1): for each concept, the best sentences
of its HWPh article(s) in which its philosopher is named, ranked by the concept's German words
(guesses from concept_de.py and the lemma abbreviation the article uses, «N.» for ‹Notwendigkeit›),
with the column, the section the sentence stands in and the notes it calls.

Articles looked at, in order: best and alternatives from concepts_hwph.json; if none of them names
the philosopher near a concept word, the whole corpus (articles where the philosopher is in `cites`,
sentences with a concept word next to his name).

    python concept_brief.py --hwph … --philosphaira … --out … [ids …] [--phil kant] [--status matched]
        [--n 3] [--W 2] [--clip 600] [--nclip 160] [--dclip 2000] [--corpus] [--art lemma-or-id …]
"""
import argparse, json, os, re, sqlite3, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from read_evidence import parse_article, name_patterns
from read_brief import sentences

SEC = re.compile(r'^((?:[IVX]+\.|[A-H]\.|\d+\.|[a-h]\))(?:\s*(?:[A-H]\.|\d+\.|[a-h]\)))*)\s*(.{2,140}?)\s[–-]\s')
DEF = r'Begriff|Terminus|Ausdruck|bezeichnet|versteht|verstanden|definiert|Definition|Lehre|lehrt|Theorie|Bestimmung|bestimmt|meint|heißt|nennt|Grundbegriff|zentral|Prinzip'

def stems(guesses, extra=()):
    out = set()
    for g in guesses.split('|') + list(extra):
        for w in re.split(r"[\s,;/()'’\-]+", g):
            w = w.strip('.').lower()
            if len(w) < 4 or w in ('der', 'die', 'das', 'und', 'des', 'von', 'vom', 'als', 'zur', 'sich'): continue
            out.add(w[:max(4, min(len(w) - 1, 9))])
    return out

def lemma_abbrev(lemma):
    # HWPh abbreviates the lemma by its initial(s): ‹Notwendigkeit› → N., ‹Form und Materie› → F. und M.
    head = re.split(r'[;,/(]', lemma)[0].strip()
    ini = [w[0] for w in head.split() if w[:1].isupper()]
    return [re.escape(i) + r'\.' for i in ini[:1]]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hwph', required=True); ap.add_argument('--philosphaira', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('ids', nargs='*'); ap.add_argument('--phil'); ap.add_argument('--status')
    ap.add_argument('--n', type=int, default=3); ap.add_argument('--W', type=int, default=2)
    ap.add_argument('--clip', type=int, default=600); ap.add_argument('--nclip', type=int, default=160); ap.add_argument('--dclip', type=int, default=2000)
    ap.add_argument('--corpus', action='store_true', help='always search the whole corpus as well')
    ap.add_argument('--art', nargs='*', default=[], help='look (also) in these articles: lemma or id')
    ap.add_argument('--grep', help='extra regex the sentence must match (overrides concept words ranking)')
    ap.add_argument('--maxart', type=int, default=4)
    a = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(a.hwph))); import hwph_cite
    db = sqlite3.connect(a.hwph); data = os.path.join(a.philosphaira, 'app', 'data')
    C = {c['id']: c for c in json.load(open(data + '/concepts.json', encoding='utf-8'))}
    P = {p['id']: p for p in json.load(open(data + '/philosophers.json', encoding='utf-8'))}
    CM = json.load(open(os.path.join(a.out, 'concepts_hwph.json'), encoding='utf-8'))
    pmap = json.load(open(os.path.join(a.out, 'philosophers_hwph.json'), encoding='utf-8'))
    art = {x[0]: x for x in db.execute('SELECT id, lemma, band, col_from, col_to FROM articles')}
    by_lemma = {x[1]: x[0] for x in art.values()}
    pats = name_patterns(db, pmap, hwph_cite); cache = {}
    ids = a.ids or [k for k, v in CM.items() if (not a.phil or v['philosopher'] == a.phil) and (not a.status or v['status'] == a.status)]

    def article_ids(cm):
        out = []
        for b in [cm.get('best')] + cm.get('alternatives', []):
            if b and b['article'] not in out: out.append(b['article'])
        return out

    def scan(aid, ph, st, abbr, grep):
        if aid not in cache: cache[aid] = parse_article(db, aid)
        paras, notes = cache[aid]
        res, sec, nphil = [], '', 0
        abbr_re = re.compile('(?<![A-Za-zÄÖÜäöüß])(?:' + '|'.join(abbr) + ')') if abbr else None
        for pi, p in enumerate(paras):
            t = p['text']
            if t.startswith('## '): sec = t[3:80]; continue
            m = SEC.match(t)
            if m: sec = (m.group(1) + ' ' + m.group(2))[:90]
            ss = sentences(t)
            for i in range(len(ss)):
                for w in range(1, a.W + 1):
                    if i + w > len(ss): continue
                    chunk = ' '.join(ss[i:i + w])
                    if not pats[ph].search(chunk): continue
                    if w > 1 and (pats[ph].search(' '.join(ss[i:i + w - 1])) or pats[ph].search(' '.join(ss[i + 1:i + w]))):
                        continue
                    if w == 1: nphil += 1
                    low = chunk.lower()
                    if grep:
                        if not re.search(grep, chunk): continue
                        hits = 1
                    else:
                        hits = sum(1 for s in st if s in low) + (len(abbr_re.findall(chunk)) and 1 if abbr_re else 0)
                    score = (3 if w == 1 else 1) + 3 * min(hits, 3) + (2 if pats[ph].search(sec) else 0) + (1 if re.search(DEF, chunk) else 0)
                    if len(chunk) > 1100: score -= 2
                    res.append((score, hits, aid, pi, i, chunk, p, sec))
        return res, nphil

    for cid in ids:
        c, cm = C[cid], CM[cid]; ph = c['philosopher']
        print(f"\n=== {cid}  «{c['label']}» ({P[ph]['nameRu']})  [{cm['status']}]  догадки: {cm['guesses']}")
        print(f"  КРАТ: {c.get('description','')}")
        print(f"  ПОЛН: {c.get('extendedDescription','')[:a.dclip]}")
        if c.get('provenanceStatus'): print(f"  [сейчас {c['provenanceStatus']}: {c.get('provenance','')}]")
        if ph not in pats: print('  (философа нет в HWPh)'); continue
        aids = [by_lemma[x] if x in by_lemma else int(x) for x in a.art] + article_ids(cm)
        aids = list(dict.fromkeys(aids))[:a.maxart + len(a.art)]
        st = stems(cm['guesses'])
        found, summary = [], []
        for aid in aids:
            r, nph = scan(aid, ph, st, lemma_abbrev(art[aid][1]), a.grep)
            found += r; summary.append(f"‹{art[aid][1]}› {art[aid][2]}/{art[aid][3]}–{art[aid][4]} (фраз с ним {nph})")
        print('  СТАТЬИ: ' + '; '.join(summary))
        if a.corpus or not any(f[1] > 0 for f in found):
            pids = pmap[ph]['hwph_persons']
            q = 'SELECT aid, SUM(n_body) s FROM cites WHERE pid IN (%s) GROUP BY aid HAVING s>0 ORDER BY s DESC' % ','.join('?' * len(pids))
            cand = [r[0] for r in db.execute(q, pids) if r[0] not in aids and r[0] in art]
            extra = []
            for aid in cand[:400]:
                pl = db.execute('SELECT plain_body FROM articles WHERE id=?', (aid,)).fetchone()[0]
                import zlib; low = zlib.decompress(pl).decode().lower()
                if a.grep and not re.search(a.grep, zlib.decompress(pl).decode()): continue
                if not a.grep and not any(s in low for s in st): continue
                r, _ = scan(aid, ph, st, [], a.grep)
                extra += [x for x in r if x[1] > 0]
            if extra: print('  + КОРПУС: ' + ', '.join(sorted({f'‹{art[x[2]][1]}›' for x in extra})[:12]))
            found += extra
        found.sort(key=lambda w: (-w[0], -w[1]))
        taken = []
        for w in found:
            if any(t[2] == w[2] and t[3] == w[3] and abs(t[4] - w[4]) <= 1 for t in taken): continue
            taken.append(w)
            if len(taken) >= a.n: break
        if not taken: print('  (фраз с философом нет)')
        for score, hits, aid, pi, si, chunk, p, sec in taken:
            cols = f"{p['c_from']}" + (f"–{p['c_to']}" if p['c_to'] != p['c_from'] else '')
            print(f"  · ‹{art[aid][1]}› Bd. {art[aid][2]}, Sp. {cols} [{score}] §{sec[:60]}: {chunk[:a.clip]}")
            notes = cache[aid][1]; order = list(notes)
            for n in re.findall(r'\[(\d+)\]', chunk):
                f = next((k for k in p['fns'] if notes.get(k, {}).get('n') == n), None)
                if not f: continue
                t = notes[f]['text']
                if re.match(r'(a\.\s?a\.\s?O|a\.O|ebda|ebd\.|ibid|Vgl\. ebda|\d)', t):
                    k = order.index(f); t = t + '  ⟵ ' + ' | '.join(notes[order[j]]['text'][:100] for j in range(max(0, k - 2), k))
                print(f'      [{n}] {t[:a.nclip]}')

if __name__ == '__main__':
    main()
