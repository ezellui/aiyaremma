#!/usr/bin/env python3
"""parity.py — do the server and the static reader give the same answers?

    python tools/parity.py --server http://127.0.0.1:8765/ --static hwph_static/index.html [--quick]

Both must be built from one database. Asks both the same questions (search with the whole query
language and its options, articles, graphs, persons, node expansion, suggestions, register, word
list, highlighting, errors) and compares the answers as JSON. Needs Python's playwright with
Chromium (pip install playwright; python -m playwright install chromium); the reader itself does not.
Exit code 1 when anything differs; answers the static reader marks as approximate (a phrase in more
than 1500 articles) are counted apart.
"""
import argparse, json, os, random, sqlite3, sys, time, urllib.error, urllib.parse, urllib.request

QUERIES = ['Seele', 'Seele Leib', 'Seele -Leib', '"anima mundi"', 'transzendent*', 'ἄπειρον', 'απειρ*', 'aufklarung',
           'Hegel OR Schelling', 'Kant', '"Wille zur Macht"', 'Dialektik -Hegel', 'br?der', '*prin?ip*', 'Solo?je?',
           '?ynismus', 'gr^und*', '(Proklos OR Neuplatonis*) Hegel', 'Proklos NEAR Hegel', 'Proklos NEAR/3 Hegel',
           'Hegel UND (neuplatonis* ODER Pro?l?s)', 'novalis ODER hardenberg', '"das Nichts" NICHT Heidegger', 'Leben',
           'Zeichen*', 'Leere', 'Nous NEAR Logos', '"coincidentia oppositorum"']
VARIANTS = [{}, {'tol': '1'}, {'case': '1'}, {'scope': 'notes'}, {'scope': 'lemma'}, {'band': '5'}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--server', default='http://127.0.0.1:8765/')
    ap.add_argument('--static', default='hwph_static/index.html')
    ap.add_argument('--db', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hwph.sqlite'))
    ap.add_argument('--quick', action='store_true', help='fewer questions')
    ap.add_argument('--browser', help='path to a Chromium executable')
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    def srv(path):
        try:
            return json.load(urllib.request.urlopen(a.server.rstrip('/') + path, timeout=300))
        except urllib.error.HTTPError as e:
            return {'ERR': json.load(e).get('code')}

    db = sqlite3.connect(a.db)
    random.seed(5)
    arts = [r[0] for r in db.execute("SELECT id FROM articles WHERE kind='article'")]
    persons = [r[0] for r in db.execute('SELECT id FROM persons WHERE editor=0 ORDER BY n_articles DESC LIMIT 15')]
    A = random.sample(arts, 6 if a.quick else 20)
    P = persons[:5] if a.quick else persons
    queries = QUERIES[:8] if a.quick else QUERIES

    paths = []
    for q in queries:
        for v in VARIANTS:
            paths.append(('search', '/api/search?' + urllib.parse.urlencode(dict(q=q, limit=10, **v))))
        paths.append(('highlight', '/api/highlight?' + urllib.parse.urlencode(dict(q=q))))
        paths.append(('words', '/api/words?' + urllib.parse.urlencode(dict(q=q, tol='1'))))
    for aid in A:
        paths += [('article', '/api/article/%d' % aid), ('graph', '/api/graph/a/%d?depth=2&scholars=1' % aid),
                  ('expand', '/api/expand?node=a%d&what=persons&scholars=1&limit=80' % aid),
                  ('expand', '/api/expand?node=a%d&what=concepts&limit=80' % aid), ('pattern', '/api/pattern?concept=%d' % aid)]
    for pid in P:
        paths += [('person', '/api/person/%d' % pid), ('graph', '/api/graph/p/%d?n=24' % pid),
                  ('expand', '/api/expand?node=p%d&what=articles&limit=80' % pid), ('pattern', '/api/pattern?pid=%d' % pid)]
    for q in ['seel', 'kant', 'ἄπειρ', 'anima', 'Ze', 'spinoz']:
        paths += [('suggest', '/api/suggest?q=' + urllib.parse.quote(q)), ('register', '/api/register?q=' + urllib.parse.quote(q))]
    paths += [('persons', '/api/persons?role=thinkers&limit=300'), ('lemmas', '/api/lemmas'),
              ('error', '/api/article/99999999'), ('error', '/api/expand?node=x1&what=persons'), ('error', '/api/pattern')]

    res, diffs, approx = {}, [], 0
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=a.browser) if a.browser else p.chromium.launch()
        pg = b.new_page()
        pg.set_default_timeout(600000)
        pg.goto('file://' + os.path.abspath(a.static))
        pg.wait_for_timeout(1500)
        for kind, path in paths:
            x = srv(path)
            y = pg.evaluate('p => window.HWPH_API(p).then(r => r, e => ({ERR: e.code || ("JS " + e.message)}))', path)
            if 'ERR' in x or 'ERR' in y:
                same = x.get('ERR') == y.get('ERR') and x.get('ERR') is not None
            else:
                same = json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)
            if not same and kind == 'search' and y.get('approx'):
                approx += 1
                continue
            r = res.setdefault(kind, [0, 0])
            r[0] += 1
            r[1] += same
            if not same:
                diffs.append((kind, path))
        b.close()
    for k, (n, ok) in sorted(res.items()):
        print('%-10s %d/%d' % (k, ok, n))
    if approx:
        print('approximate in the static reader (phrase in more than 1500 articles): %d' % approx)
    for d in diffs[:30]:
        print('DIFF', *d)
    print('%.0f s' % (time.time() - t0))
    sys.exit(1 if diffs else 0)


if __name__ == '__main__':
    main()
