#!/usr/bin/env python3
"""
hwph_build.py — builds hwph.sqlite from the Markdown volumes made by hwph2md.py
(--by-volume: Bd01.md … Bd13.md, Bd1s.md, Bd13s.md, index.csv).

    python hwph_build.py <folder with BdNN.md> [-o hwph.sqlite]

Python 3.8+, standard library only.
"""
import argparse, glob, html, json, os, re, sqlite3, sys, time, unicodedata, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hwph_common import fold, fts_engine  # noqa: E402

FM_RE = re.compile(r'^---\n(lemma: .*?)\n---\n', re.M | re.S)
NOTE_DEF_RE = re.compile(r'^\[\^(\d+)\]:\s?(.*)$')
REF_RE = re.compile(r'\[\^(\d+)\]')
SEC_RE = re.compile(r'^(?:\*\*)?((?:[IVX]{1,5}|[A-H]|\d{1,2}|[a-h])\.(?:\s?\d{1,2}\.)?)\s')
XREF_RE = re.compile(r'(Art(?:ikel)?\.?\s*)‹([^›]{2,90})›')

# ---------------------------------------------------------------- parsing
def parse_front(fm):
    meta = {}
    for line in fm.split('\n'):
        k, _, v = line.partition(':')
        v = v.strip()
        if k == 'autoren':
            try:
                meta[k] = [a.strip() for a in json.loads(v) if a.strip()]
            except ValueError:
                meta[k] = re.findall(r'"([^"]+)"', v)
        else:
            meta[k] = v.strip('"')
    def rng(s):
        nums = [int(x) for x in re.findall(r'\d+', s or '')]
        return (nums[0], nums[-1]) if nums else (0, 0)
    meta['col_from'], meta['col_to'] = rng(meta.get('spalten'))
    meta['pdf_from'], meta['pdf_to'] = rng(meta.get('pdf_seiten'))
    return meta

def read_volume(path):
    text = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    parts = FM_RE.split(text)
    # parts: [pre, fm1, body1, fm2, body2, ...]
    for i in range(1, len(parts) - 1, 2):
        meta = parse_front(parts[i])
        body = parts[i + 1]
        body = re.sub(r'^\s*# [^\n]*\n', '', body, count=1)
        yield meta, body.strip('\n')

def squash(s):
    return re.sub(r'[\s,]+', '', s).lower()

def repair_lemma(lemma, body):
    """Lemma broken at a line end ('… Ge-') or glued ('A,B(c-'): take it from the run-in start of the text."""
    lemma = lemma.replace(' (Fortsetzung)', '')
    m = re.match(r'^(?:\*\*)?(.{1,160}?)(?:\*\*)?\s\.\s', body)
    if lemma.endswith('-') and m:
        cand = m.group(1).replace('**', '').strip()
        if squash(cand).startswith(squash(lemma[:-1])[:12]):
            lemma = cand
        else:
            lemma = lemma[:-1] + cand
    lemma = re.sub(r',(?=\S)', ', ', lemma)
    lemma = re.sub(r'(?<=\w)\((?=\w)', ' (', lemma)
    return re.sub(r'\s+', ' ', lemma).strip()

def split_article(body):
    """-> body paragraphs (with lit blocks marked), note definitions [(n, text)]"""
    paras = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    notes, main = [], []
    in_notes = False
    for p in paras:
        if p == '## Anmerkungen':
            in_notes = True
            continue
        if in_notes:
            for line in p.split('\n'):
                m = NOTE_DEF_RE.match(line.strip())
                if m:
                    notes.append([int(m.group(1)), m.group(2)])
                elif notes and line.strip():
                    notes[-1][1] += ' ' + line.strip()
            continue
        main.append(p)
    # mark literature blocks: after '## Literaturhinweise' until a new numbered section begins
    out, in_lit = [], False
    for p in main:
        if p.startswith('## Literaturhinweise'):
            in_lit = True
            out.append(('h', 'Literaturhinweise'))
            continue
        if p.startswith('## '):
            in_lit = False
            out.append(('h', p[3:].strip()))
            continue
        if in_lit and (SEC_RE.match(p) or p.startswith('**')):
            in_lit = False
        out.append(('lit' if in_lit else 'p', p))
    return out, notes

def runs_of(nums):
    """Assign run index to a sequence of footnote numbers (numbering restarts per article part)."""
    run, prev, res = 0, 0, []
    for n in nums:
        if prev and (n == 1 and prev > 1 or n < prev - 3):
            run += 1
        res.append(run)
        prev = max(prev, n) if n >= prev - 3 else n
    return res

# ---------------------------------------------------------------- markdown -> html
def inline(md):
    s = html.escape(md, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = s.replace('*', '')
    return s

def plain(md):
    s = REF_RE.sub('', md)
    s = s.replace('**', '').replace('*', '')
    return re.sub(r'\s+', ' ', s).strip()

# ---------------------------------------------------------------- lemma resolution
def lemma_key(s):
    s = fold(s)
    s = re.sub(r'[^\w/;]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

class Resolver:
    def __init__(self, rows):
        self.exact = {}
        for aid, lemma in rows:
            k = lemma_key(lemma)
            self.exact.setdefault(k, aid)
            # "Wahrheit; Wahrheitstheorie" and "Kant, Immanuel" style: first element as a weaker key
            for part in re.split(r'[;,/]', lemma):
                self.exact.setdefault('~' + lemma_key(part), aid)

    def find(self, text):
        t = re.sub(r'\s+', ' ', text.replace('*', '')).strip()
        if re.fullmatch(r'\w{1,3}\.(?:\s?\w{1,3}\.)*', t):
            return None                      # abbreviated self-reference ('M.', 'h.M.')
        cands = [t,
                 re.sub(r'\s+[IVX]+(?:\s+[A-Z\d])*(?:\s*\(.*\))?$', '', t),   # section qualifier
                 re.sub(r'\s*\(.*\)$', '', t)]
        for c in cands:
            k = lemma_key(c)
            if k in self.exact:
                return self.exact[k]
        for c in cands:
            k = '~' + lemma_key(re.split(r'[;,/]', c)[0])
            if k in self.exact:
                return self.exact[k]
        return None

# ---------------------------------------------------------------- register (Bd. 13)
REG_LOC = re.compile(r'\s+((?:1[0-3]|[1-9]))\s+(\d{1,4})(f{1,2}\.|[–-]\d{1,4})?')
REG_QUAL = re.compile(r'(?:\s+(?:[IVX]{1,5}|[A-H]|\d)(?=\s|$))*(?:\s+\([^)]{1,30}\))?')

def parse_register(text, resolver, lemma_list):
    """Register lines look like: 'term ◊ Target [qualifier] [band col] · ◊ Target … s. auch ◊ *Rel*  next-term ◊ …'
    Targets are matched against the known lemma list (longest match), which is what makes the flattened text splittable."""
    text = text.replace('*', '')
    text = re.sub(r'\s+', ' ', text)
    keys = sorted({l for l in lemma_list}, key=len, reverse=True)
    by_first = {}
    for l in keys:
        by_first.setdefault(l[:3], []).append(l)
    pieces = text.split('\u0001')
    entries, term, pending_term, seealso_of = [], None, pieces[0].strip(), None
    for piece in pieces[1:]:
        piece = piece.lstrip()
        target = None
        for l in by_first.get(piece[:3], []):
            if piece.startswith(l) and (len(piece) == len(l) or not piece[len(l)].isalnum()):
                target = l
                break
        if target is None:
            # unknown target: take up to a location or a separator
            m = re.match(r'(.{1,80}?)(?=\s+(?:1[0-3]|[1-9])\s+\d|\s+·|\s+s\. auch|$)', piece)
            target = m.group(1).strip() if m else piece[:40]
        rest = piece[len(target):]
        q = REG_QUAL.match(rest)
        qual = q.group(0).strip() if q else ''
        rest = rest[q.end():] if q else rest
        band = col = None
        m = REG_LOC.match(rest)
        if m:
            band, col = m.group(1), m.group(2) + (m.group(3) or '')
            rest = rest[m.end():]
        rest = rest.strip()
        if pending_term is not None:
            term = pending_term.strip(' ·,;') or term
            seealso_of = None
        kind = 'see' if seealso_of else ('main' if not term else 'ref')
        if term or seealso_of:
            entries.append((seealso_of or term, target, qual, band, col, kind))
        else:
            seealso_of = None
        # what follows decides who owns the next target
        if rest.startswith('·') or rest == '':
            pending_term = None
        elif rest.startswith('s. auch'):
            seealso_of = target
            pending_term = None
            tail = rest[len('s. auch'):].strip(' ·')
            if tail:
                pending_term = tail
        else:
            pending_term = rest
            seealso_of = None
        if pending_term is not None and pending_term.strip(' ·,;') == '':
            # lemma entries: '◊ Advaita 1 86f. s. auch …' — the term is the lemma itself
            pending_term = None
        if not term and not seealso_of and pending_term is None:
            term = target
    return entries

# ---------------------------------------------------------------- build
SCHEMA = '''
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE articles(
  id INTEGER PRIMARY KEY, lemma TEXT, lemma_fold TEXT, band TEXT, kind TEXT,
  col_from INT, col_to INT, pdf_from INT, pdf_to INT, authors TEXT,
  n_notes INT, n_chars INT, toc TEXT,
  html BLOB, plain_body BLOB, plain_notes BLOB, plain_lit BLOB);
CREATE INDEX articles_fold ON articles(lemma_fold);
CREATE INDEX articles_loc ON articles(band, col_from);
CREATE TABLE xrefs(src INT, target TEXT, dst INT);
CREATE INDEX xrefs_src ON xrefs(src);
CREATE INDEX xrefs_dst ON xrefs(dst);
CREATE TABLE register(id INTEGER PRIMARY KEY, term TEXT, term_fold TEXT, target TEXT, qualifier TEXT,
  band TEXT, col TEXT, kind TEXT, dst INT);
CREATE INDEX register_fold ON register(term_fold);
CREATE INDEX register_dst ON register(dst);
'''

def z(s):
    return zlib.compress(s.encode('utf-8'), 6)

def build(src, out):
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(src, 'Bd*.md')))
    if not files:
        sys.exit('keine Bd*.md in ' + src)
    engine = fts_engine()
    if os.path.exists(out):
        os.remove(out)
    db = sqlite3.connect(out)
    db.executescript(SCHEMA)
    if engine == 'fts5':
        db.execute("CREATE VIRTUAL TABLE fts USING fts5(lemma, body, notes, lit, authors, "
                   "content='', tokenize='unicode61 remove_diacritics 0')")
    else:
        db.execute('CREATE VIRTUAL TABLE fts USING fts4(lemma, body, notes, lit, authors, '
                   'content="", tokenize=unicode61 "remove_diacritics=0")')
    db.execute("INSERT INTO meta VALUES('engine', ?)", (engine,))

    # pass 1: read everything
    raw, register_text = [], []
    for f in files:
        for meta, body in read_volume(f):
            band = meta.get('band', '')
            if band == '13':                       # register volume
                register_text.append((meta['pdf_from'], body))
                continue
            kind = 'front' if band.endswith('*') else 'article'
            lemma = repair_lemma(meta['lemma'], body)
            raw.append((lemma, band, kind, meta, body))
    raw.sort(key=lambda r: (r[3]['pdf_from']))
    print(f'{len(raw)} Artikel gelesen ({time.time() - t0:.0f}s)', file=sys.stderr)

    ids = [(i + 1, r[0]) for i, r in enumerate(raw) if r[2] == 'article']
    resolver = Resolver(ids)

    # pass 2: articles
    xref_rows = []
    for i, (lemma, band, kind, meta, body) in enumerate(raw):
        aid = i + 1
        blocks, notes = split_article(body)
        note_runs = runs_of([n for n, _ in notes])
        note_key = {}
        for (n, _), r in zip(notes, note_runs):
            note_key.setdefault((r, n), None)
        ref_nums = [int(x) for kind_, p in blocks if kind_ != 'h' for x in REF_RE.findall(p)]
        ref_runs = iter(runs_of(ref_nums))

        def ref_html(m):
            n = int(m.group(1))
            r = next(ref_runs, 0)
            if (r, n) not in note_key:
                r = next((rr for (rr, nn) in note_key if nn == n), r)
            return f'<sup class="fn" data-fn="{r}-{n}">{n}</sup>'

        def xref_html(m):
            target = m.group(2)
            dst = resolver.find(re.sub(r'<[^>]+>', '', target)) if kind == 'article' else None
            xref_rows.append((aid, re.sub(r'<[^>]+>', '', target), dst))
            if dst and dst != aid:
                return f'{m.group(1)}‹<a class="xref" href="#/a/{dst}">{target}</a>›'
            return m.group(0)

        parts, toc, body_plain, lit_plain = [], [], [], []
        for k, (kind_, p) in enumerate(blocks):
            if kind_ == 'h':
                parts.append(f'<h3 id="h{k}">{html.escape(p)}</h3>')
                toc.append([f'h{k}', p, 0])
                continue
            if p.startswith('<!--'):
                parts.append('<div class="gap">' + html.escape(p.strip('<!- >')) + '</div>')
                continue
            h = inline(p)
            h = REF_RE.sub(ref_html, h)
            h = XREF_RE.sub(xref_html, h)
            cls = ' class="lit"' if kind_ == 'lit' else ''
            m = SEC_RE.match(p) if kind_ == 'p' else None
            if m:
                label = m.group(1)
                lvl = 1 if re.match(r'[IVX]+\.', label) else (2 if re.match(r'[A-H]\.', label) else 3)
                words = plain(p[m.end():])[:70]
                toc.append([f'p{k}', label + ' ' + words, lvl])
                parts.append(f'<p id="p{k}"{cls}>{h}</p>')
            else:
                parts.append(f'<p{cls}>{h}</p>')
            (lit_plain if kind_ == 'lit' else body_plain).append(plain(p))
        if notes:
            parts.append('<h3 id="notes">Anmerkungen</h3><ol class="notes">')
            for (n, t), r in zip(notes, note_runs):
                parts.append(f'<li id="fn{r}-{n}" value="{n}">{inline(t)}</li>')
            parts.append('</ol>')
            toc.append(['notes', 'Anmerkungen', 0])
        notes_plain = ' \n'.join(plain(t) for _, t in notes)
        bp, lp = ' \n'.join(body_plain), ' \n'.join(lit_plain)
        authors = meta.get('autoren', [])
        # de-duplicate while keeping order (multi-part articles repeat names)
        seen, auth = set(), []
        for a in authors:
            if a not in seen:
                seen.add(a)
                auth.append(a)
        db.execute('INSERT INTO articles VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
            aid, lemma, fold(lemma), band, kind, meta['col_from'], meta['col_to'],
            meta['pdf_from'], meta['pdf_to'], json.dumps(auth, ensure_ascii=False),
            len(notes), len(bp) + len(lp) + len(notes_plain), json.dumps(toc, ensure_ascii=False),
            z('\n'.join(parts)), z(bp), z(notes_plain), z(lp)))
        db.execute('INSERT INTO fts(rowid, lemma, body, notes, lit, authors) VALUES(?,?,?,?,?,?)',
                   (aid, fold(lemma), fold(bp), fold(notes_plain), fold(lp), fold(' '.join(auth))))
        if aid % 500 == 0:
            print(f'… {aid}/{len(raw)} {lemma}', file=sys.stderr)
    db.executemany('INSERT INTO xrefs VALUES(?,?,?)', xref_rows)

    # pass 3: register
    register_text.sort()
    reg = parse_register(' '.join(t for _, t in register_text), resolver, [l for _, l in ids])
    loc_index = {}
    for aid, lemma in ids:
        pass
    rows = db.execute("SELECT id, band, col_from, col_to FROM articles WHERE kind='article'").fetchall()
    by_band = {}
    for aid, band, c1, c2 in rows:
        by_band.setdefault(band, []).append((c1, c2, aid))

    def by_location(band, col):
        n = int(re.match(r'\d+', col).group(0))
        for c1, c2, aid in by_band.get(band, []):
            if c1 <= n <= c2:
                return aid
        return None

    reg_rows = []
    for term, target, qual, band, col, kind in reg:
        dst = resolver.find(target)
        if band and col:
            loc = by_location(band, col)
            dst = loc or dst
        reg_rows.append((term, fold(term), target, qual, band, col, kind, dst))
    db.executemany('INSERT INTO register(term, term_fold, target, qualifier, band, col, kind, dst) '
                   'VALUES(?,?,?,?,?,?,?,?)', reg_rows)

    n_x = len(xref_rows)
    n_xr = sum(1 for r in xref_rows if r[2])
    n_r = len(reg_rows)
    n_rr = sum(1 for r in reg_rows if r[-1])
    stats = dict(articles=len(ids), front=len(raw) - len(ids), xrefs=n_x, xrefs_resolved=n_xr,
                 register=n_r, register_resolved=n_rr, built=time.strftime('%Y-%m-%d %H:%M'))
    db.execute("INSERT INTO meta VALUES('stats', ?)", (json.dumps(stats),))
    db.commit()
    if engine == 'fts5':
        db.execute("INSERT INTO fts(fts) VALUES('optimize')")
    else:
        db.execute("INSERT INTO fts(fts) VALUES('optimize')")
    db.commit()
    db.execute('VACUUM')
    db.close()
    print(json.dumps(stats, ensure_ascii=False), file=sys.stderr)
    print(f'fertig: {out} ({os.path.getsize(out) / 1e6:.0f} MB, {time.time() - t0:.0f}s, {engine})', file=sys.stderr)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src', help='Ordner mit Bd01.md … Bd13.md')
    ap.add_argument('-o', '--out', default='hwph.sqlite')
    a = ap.parse_args()
    build(a.src, a.out)
