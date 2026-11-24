#!/usr/bin/env python3
"""
hwph_serve.py — local reader for hwph.sqlite (built by hwph_build.py).

    python hwph_serve.py [--db hwph.sqlite] [--port 8765] [--no-browser]

Opens http://127.0.0.1:8765/ ; listens on localhost only. Python 3.8+, stdlib only.
"""
import argparse, json, os, re, sqlite3, struct, sys, threading, webbrowser, zlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hwph_common import fold, parse_query, fts_expr, highlight_regex, snippets, count_hits  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(HERE, 'hwph_ui.html')
COLUMNS = ['lemma', 'body', 'notes', 'lit', 'authors']
WEIGHTS = [10.0, 1.0, 0.35, 0.5, 2.0]

_local = threading.local()
DB_PATH = 'hwph.sqlite'
ENGINE = 'fts5'
INFO = {}

def unz(b):
    return zlib.decompress(b).decode('utf-8') if b else ''

def rank_fts4(mi):
    # matchinfo 'pcx': p phrases, c columns, then 3*p*c ints (hits this row, hits all rows, rows with hit)
    ints = struct.unpack('@%dI' % (len(mi) // 4), mi)
    p, c = ints[0], ints[1]
    score = 0.0
    for i in range(p):
        for j in range(c):
            base = 2 + 3 * (i * c + j)
            hits, docs = ints[base], ints[base + 2]
            if hits:
                score += WEIGHTS[j] * hits / (1.0 + docs ** 0.5)
    return score

def db():
    con = getattr(_local, 'con', None)
    if con is None:
        con = sqlite3.connect('file:%s?mode=ro' % DB_PATH.replace('\\', '/'), uri=True, check_same_thread=False)
        con.create_function('rank4', 1, rank_fts4)
        _local.con = con
    return con

# ---------------------------------------------------------------- API
def api_info(_):
    return INFO

LEMMAS_CACHE = {}

def api_lemmas(_):
    if 'v' not in LEMMAS_CACHE:
        rows = db().execute("SELECT id, lemma, band, col_from, kind FROM articles ORDER BY lemma_fold").fetchall()
        LEMMAS_CACHE['v'] = rows
    return LEMMAS_CACHE['v']

def article_brief(con, aid):
    r = con.execute('SELECT id, lemma, band, col_from FROM articles WHERE id=?', (aid,)).fetchone()
    return dict(id=r[0], lemma=r[1], band=r[2], col=r[3]) if r else None

def api_article(qs, aid):
    con = db()
    r = con.execute('SELECT id, lemma, band, kind, col_from, col_to, pdf_from, pdf_to, authors, n_notes, '
                    'n_chars, toc, html FROM articles WHERE id=?', (aid,)).fetchone()
    if not r:
        raise KeyError(aid)
    out = dict(id=r[0], lemma=r[1], band=r[2], kind=r[3], col_from=r[4], col_to=r[5], pdf_from=r[6],
               pdf_to=r[7], authors=json.loads(r[8]), n_notes=r[9], n_chars=r[10], toc=json.loads(r[11]),
               html=unz(r[12]))
    # neighbours in printed order
    p = con.execute('SELECT id FROM articles WHERE pdf_from < (SELECT pdf_from FROM articles WHERE id=?) '
                    'ORDER BY pdf_from DESC LIMIT 1', (aid,)).fetchone()
    n = con.execute('SELECT id FROM articles WHERE pdf_from > (SELECT pdf_from FROM articles WHERE id=?) '
                    'ORDER BY pdf_from LIMIT 1', (aid,)).fetchone()
    out['prev'] = article_brief(con, p[0]) if p else None
    out['next'] = article_brief(con, n[0]) if n else None
    out['backlinks'] = [dict(id=a, lemma=l, n=c) for a, l, c in con.execute(
        'SELECT a.id, a.lemma, count(*) FROM xrefs x JOIN articles a ON a.id=x.src '
        'WHERE x.dst=? AND x.src<>? GROUP BY a.id ORDER BY a.lemma_fold', (aid, aid))]
    out['outlinks'] = [dict(id=a, lemma=l, n=c) for a, l, c in con.execute(
        'SELECT a.id, a.lemma, count(*) FROM xrefs x JOIN articles a ON a.id=x.dst '
        'WHERE x.src=? AND x.dst<>? GROUP BY a.id ORDER BY a.lemma_fold', (aid, aid))]
    out['register'] = [dict(term=t, qualifier=q, band=b, col=c) for t, q, b, c in con.execute(
        "SELECT term, max(qualifier), max(band), max(col) FROM register WHERE dst=? AND kind='ref' "
        "GROUP BY term_fold ORDER BY term_fold LIMIT 400", (aid,))]
    out['see_also'] = [dict(id=d, lemma=l) for d, l in con.execute(
        "SELECT DISTINCT r.dst, a.lemma FROM register r JOIN articles a ON a.id=r.dst "
        "WHERE r.kind='see' AND r.term_fold=? AND r.dst IS NOT NULL", (fold(r[1]),))]
    return out

def api_search(qs):
    q = (qs.get('q') or [''])[0].strip()
    scope = (qs.get('scope') or ['all'])[0]
    band = (qs.get('band') or [''])[0]
    offset = int((qs.get('offset') or ['0'])[0])
    limit = min(int((qs.get('limit') or ['20'])[0]), 100)
    items = parse_query(q)
    column = scope if scope in COLUMNS else None
    expr = fts_expr(items, ENGINE, column)
    res = dict(q=q, total=0, items=[], register=[])
    if not expr:
        return res
    con = db()
    where = 'fts MATCH ?'
    args = [expr]
    extra = ''
    if band:
        extra = ' AND a.band=?'
        args.append(band)
    if ENGINE == 'fts5':
        order = 'bm25(fts, %s)' % ', '.join(str(w) for w in WEIGHTS)
        sql = ('SELECT a.id, a.lemma, a.band, a.col_from, a.col_to, a.authors, a.plain_body, a.plain_notes, '
               'a.plain_lit FROM fts JOIN articles a ON a.id=fts.rowid WHERE %s%s ORDER BY %s LIMIT ? OFFSET ?'
               % (where, extra, order))
    else:
        sql = ('SELECT a.id, a.lemma, a.band, a.col_from, a.col_to, a.authors, a.plain_body, a.plain_notes, '
               "a.plain_lit FROM (SELECT rowid AS rid, rank4(matchinfo(fts, 'pcx')) AS score FROM fts WHERE %s) f "
               'JOIN articles a ON a.id=f.rid WHERE 1%s ORDER BY f.score DESC LIMIT ? OFFSET ?' % (where, extra))
    try:
        rows = con.execute(sql, args + [limit, offset]).fetchall()
        total = con.execute('SELECT count(*) FROM fts JOIN articles a ON a.id=fts.rowid WHERE %s%s' % (where, extra),
                            args).fetchone()[0]
    except sqlite3.OperationalError as e:
        raise ValueError('Suchausdruck: %s' % e)
    rx = highlight_regex(items)
    for aid, lemma, bnd, c1, c2, authors, pb, pn, pl in rows:
        texts = dict(body=unz(pb), notes=unz(pn), lit=unz(pl))
        hits = {k: count_hits(v, rx) for k, v in texts.items()}
        snips = []
        order = [column] if column in texts else ['body', 'notes', 'lit']
        for k in order:
            for s in snippets(texts[k], rx, maxn=2 - len(snips)):
                snips.append(dict(where=k, html=s))
            if len(snips) >= 2:
                break
        res['items'].append(dict(id=aid, lemma=lemma, band=bnd, col_from=c1, col_to=c2,
                                 authors=json.loads(authors), hits=hits, snippets=snips))
    res['total'] = total
    if offset == 0 and scope in ('all', 'register') and items and len(items) == 1 and not items[0]['neg']:
        res['register'] = register_lookup(' '.join(items[0]['tokens']), 40, prefix=items[0]['prefix'])
    return res

def register_lookup(term, limit, prefix=True):
    f = fold(term).strip()
    if not f:
        return []
    con = db()
    rows = con.execute(
        "SELECT r.term, r.target, r.qualifier, r.band, r.col, r.kind, r.dst, a.lemma FROM register r "
        "LEFT JOIN articles a ON a.id=r.dst WHERE r.term_fold LIKE ? AND r.kind<>'see' "
        "ORDER BY length(r.term_fold), r.term_fold, r.id LIMIT ?",
        ((f + '%') if prefix else f, limit)).fetchall()
    if not rows and not prefix:
        return register_lookup(term, limit, True)
    return [dict(term=t, target=tg, qualifier=q, band=b, col=c, kind=k, id=d, lemma=l)
            for t, tg, q, b, c, k, d, l in rows]

def api_register(qs):
    q = (qs.get('q') or [''])[0]
    return register_lookup(q, 300)

# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, code, body, ctype='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        try:
            if u.path in ('/', '/index.html'):
                with open(UI, 'rb') as fh:
                    return self.send(200, fh.read(), 'text/html; charset=utf-8')
            if u.path == '/api/info':
                return self.send(200, api_info(qs))
            if u.path == '/api/lemmas':
                return self.send(200, api_lemmas(qs))
            m = re.fullmatch(r'/api/article/(\d+)', u.path)
            if m:
                return self.send(200, api_article(qs, int(m.group(1))))
            if u.path == '/api/search':
                return self.send(200, api_search(qs))
            if u.path == '/api/register':
                return self.send(200, api_register(qs))
            self.send(404, {'error': 'not found'})
        except KeyError:
            self.send(404, {'error': 'Artikel nicht gefunden'})
        except ValueError as e:
            self.send(400, {'error': str(e)})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:  # keep the server alive
            import traceback
            traceback.print_exc()
            self.send(500, {'error': repr(e)})

def main():
    global DB_PATH, ENGINE, INFO
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=os.path.join(HERE, 'hwph.sqlite'))
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--no-browser', action='store_true')
    a = ap.parse_args()
    DB_PATH = os.path.abspath(a.db)
    if not os.path.exists(DB_PATH):
        sys.exit('Datenbank fehlt: %s  (zuerst: python hwph_build.py <Ordner>)' % DB_PATH)
    con = db()
    meta = dict(con.execute('SELECT key, value FROM meta'))
    ENGINE = meta.get('engine', 'fts5')
    INFO = dict(engine=ENGINE, stats=json.loads(meta.get('stats', '{}')))
    try:
        con.execute("SELECT count(*) FROM fts WHERE fts MATCH 'a'").fetchone()
    except sqlite3.OperationalError as e:
        sys.exit('Diese Python-SQLite kann den Index nicht lesen (%s). Datenbank mit diesem Python neu bauen.' % e)
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    url = 'http://127.0.0.1:%d/' % a.port
    print('HWPh-Leser läuft: %s  (Strg+C beendet)' % url)
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
