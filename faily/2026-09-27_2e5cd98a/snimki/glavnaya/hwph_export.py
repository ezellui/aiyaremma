#!/usr/bin/env python3
"""
hwph_export.py — the reader as a folder of files that opens with a double click on index.html,
no server, no Python on the reading machine.

    python hwph_export.py [--db hwph.sqlite] [--out hwph_static]

Browsers do not let a page opened from disk (file://) read other files with fetch(); they do let
it load scripts. So every piece of data is written as a small script that hands its content to the
page: data/<key>.js contains  HWPH.put("<key>", {...}).

What is written:
  data/meta.js          lemma list, bands, statistics, per-article lengths for ranking
  data/a/<id>.js        one article: its HTML and everything the right-hand column shows
  data/t/<id>.js        plain text of an article (text, notes, literature, authors): snippets, phrases
  data/s/<xx>.js        search index, one file per first two letters of a word
  data/r/<xx>.js        register of vol. 13, one file per first two letters of a term
  data/graph.js         cross-references, citations, discussed concepts: graphs, persons, co-citation
  data/persons.js       all cited persons (names, counts, roles)
  data/pat/<n>.js       how each person is written in the text (for marking places), 500 per file
  index.html, static_api.js, katex/, img/

Python 3.8+, stdlib only. The reader's own files (hwph_ui.html, hwph_serve.py, hwph_common.py,
hwph_cite.py) must lie next to this script.
"""
import argparse, json, math, os, re, shutil, sqlite3, sys, time, zlib
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hwph_serve as S                      # noqa: E402  (the same answers the server gives)
from hwph_common import fold                # noqa: E402

for _st in (sys.stdout, sys.stderr):
    try:
        _st.reconfigure(errors='replace')
    except Exception:
        pass

TOKEN = re.compile(r'\w+')

def js(key, data):
    return 'HWPH.put(%s,%s);\n' % (json.dumps(key), json.dumps(data, ensure_ascii=False, separators=(',', ':')))

def shard_name(term):
    """file name for the first two letters of a folded word: hex code points, safe on any disk"""
    return '-'.join('%x' % ord(c) for c in term[:2])

def b36(n):
    s, n = '', int(n)
    while True:
        n, r = divmod(n, 36)
        s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
        if not n:
            return s

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)

def export(db_path, out):
    t0 = time.time()
    S.DB_PATH = os.path.abspath(db_path)
    con = S.db()
    meta_kv = dict(con.execute('SELECT key, value FROM meta'))
    S.ENGINE = meta_kv.get('engine', 'fts5')
    S.INFO = dict(engine='static', stats=json.loads(meta_kv.get('stats', '{}')))
    if os.path.isdir(out):
        shutil.rmtree(out)
    data = os.path.join(out, 'data')
    os.makedirs(data)

    rows = con.execute('SELECT id, lemma, band, col_from, kind, col_to, authors FROM articles ORDER BY lemma_fold').fetchall()
    ids = [r[0] for r in rows]

    # ---- per-article: HTML with its column, plain text, and the search postings
    postings = defaultdict(dict)                       # term -> {aid: [lemma, body, notes, lit, authors]}
    lengths = {}
    for k, (aid, lemma, band, c1, kind, c2, authors) in enumerate(rows):
        art = S.api_article({}, aid)
        write(os.path.join(data, 'a', '%d.js' % aid), js('a/%d' % aid, art))
        pb, pn, pl = con.execute('SELECT plain_body, plain_notes, plain_lit FROM articles WHERE id=?', (aid,)).fetchone()
        texts = dict(b=S.unz(pb), n=S.unz(pn), l=S.unz(pl), au=' '.join(json.loads(authors)))
        write(os.path.join(data, 't', '%d.js' % aid), js('t/%d' % aid, texts))
        cols = [lemma, texts['b'], texts['n'], texts['l'], texts['au']]
        lens = []
        for ci, text in enumerate(cols):
            toks = TOKEN.findall(fold(text))
            lens.append(len(toks))
            for t, c in Counter(toks).items():
                e = postings[t].get(aid)
                if e is None:
                    e = postings[t][aid] = [0, 0, 0, 0, 0]
                e[ci] = c
        lengths[aid] = lens
        if k % 500 == 0:
            print('… статьи %d/%d' % (k, len(rows)), file=sys.stderr)

    # ---- search index: term -> "delta-id:counts delta-id:counts …" (base 36, trailing zeros dropped)
    shards = defaultdict(dict)
    for term, docs in postings.items():
        parts, prev = [], 0
        for aid in sorted(docs):
            c = docs[aid]
            while c and c[-1] == 0:
                c = c[:-1]
            parts.append(b36(aid - prev) + ':' + ','.join(b36(x) for x in c))
            prev = aid
        shards[shard_name(term)][term] = ' '.join(parts)
    for name, terms in shards.items():
        write(os.path.join(data, 's', name + '.js'), js('s/' + name, terms))
    n_docs = len(rows)
    avg = [sum(l[i] for l in lengths.values()) / max(1, n_docs) for i in range(5)]
    print('индекс: слов %d, файлов %d' % (len(postings), len(shards)), file=sys.stderr)
    del postings

    # ---- register
    reg = defaultdict(list)
    for term, target, qual, band, col, kind, dst, lemma, tf in con.execute(
            "SELECT r.term, r.target, r.qualifier, r.band, r.col, r.kind, r.dst, a.lemma, r.term_fold FROM register r "
            "LEFT JOIN articles a ON a.id=r.dst ORDER BY r.id"):
        reg[shard_name(tf) if tf else '_'].append([term, target, qual, band, col, kind, dst, lemma, tf])
    for name, lst in reg.items():
        write(os.path.join(data, 'r', name + '.js'), js('r/' + name, lst))

    # ---- graph data: everything graphs, persons and co-citation are computed from
    xrefs = [list(r) for r in con.execute(
        'SELECT src, dst, count(*) FROM xrefs WHERE dst IS NOT NULL GROUP BY src, dst')]
    cites = [list(r) for r in con.execute('SELECT aid, pid, n_body, n_notes, n_lit FROM cites ORDER BY aid')]
    mentions = [list(r) for r in con.execute('SELECT aid, dst, tf, score FROM mentions')]
    write(os.path.join(data, 'graph.js'), js('graph', dict(xrefs=xrefs, cites=cites, mentions=mentions)))
    persons = [list(r) for r in con.execute(
        'SELECT id, name, name_fold, n_articles, n_body, n_notes, n_lit, editor, role FROM persons ORDER BY n_articles DESC')]
    write(os.path.join(data, 'persons.js'), js('persons', persons))

    # ---- how each person is written (marking places in an article), with the spellings
    pats = defaultdict(dict)
    for pid, variants in con.execute('SELECT id, variants FROM persons'):
        try:
            src = S.person_pattern(con, pid)
        except Exception:
            src = None
        pats[pid // 500][pid] = [src, json.loads(variants)]
    for b, d in pats.items():
        write(os.path.join(data, 'pat', '%d.js' % b), js('pat/%d' % b, d))

    # ---- meta
    meta = dict(info=S.INFO, lemmas=[[r[0], r[1], r[2], r[3], r[4], r[5]] for r in rows],
                n_docs=n_docs, avg=avg, lengths=lengths, shards=sorted(shards), reg_shards=sorted(reg),
                weights=S.WEIGHTS, built=time.strftime('%Y-%m-%d %H:%M'))
    write(os.path.join(data, 'meta.js'), js('meta', meta))

    # ---- the page
    ui = open(os.path.join(HERE, 'hwph_ui.html'), encoding='utf-8').read()
    ui = ui.replace('<script>\n"use strict";', '<script src="static_api.js"></script>\n<script>\n"use strict";', 1)
    if 'static_api.js' not in ui:
        sys.exit('hwph_ui.html: не нашлось места для static_api.js')
    write(os.path.join(out, 'index.html'), ui)
    shutil.copyfile(os.path.join(HERE, 'static_api.js'), os.path.join(out, 'static_api.js'))
    if os.path.isdir(os.path.join(HERE, 'katex')):
        shutil.copytree(os.path.join(HERE, 'katex'), os.path.join(out, 'katex'))
    img = os.path.join(os.path.dirname(S.DB_PATH), 'img')
    if os.path.isdir(img):
        os.makedirs(os.path.join(out, 'img'))
        for f in os.listdir(img):
            if f.endswith('.png'):
                shutil.copyfile(os.path.join(img, f), os.path.join(out, 'img', f))
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
    nfiles = sum(len(fs) for _, _, fs in os.walk(out))
    print('готово: %s — %d файлов, %.0f МБ, %.0f с' % (out, nfiles, size / 1e6, time.time() - t0), file=sys.stderr)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=os.path.join(HERE, 'hwph.sqlite'))
    ap.add_argument('--out', default=os.path.join(HERE, 'hwph_static'))
    a = ap.parse_args()
    if not os.path.exists(a.db):
        sys.exit('Нет базы %s' % a.db)
    export(a.db, a.out)
