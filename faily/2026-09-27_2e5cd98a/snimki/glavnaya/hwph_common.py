"""Shared by hwph_build.py and hwph_serve.py (Python 3.8+, stdlib only)."""
import html, re, sqlite3, unicodedata
from functools import lru_cache

# spacing accents left over from the PDF's decomposed Greek
_DROP = set('´′`˜¨᾿῾῀΄΅')

@lru_cache(maxsize=None)
def fold_char(c):
    if c in _DROP:
        return ''
    if c == 'ß':
        return 'ss'
    d = unicodedata.normalize('NFD', c)
    d = ''.join(x for x in d if not unicodedata.combining(x))
    d = d.lower()
    return d.replace('ς', 'σ').replace('ı', 'i')

_table = {}

def fold(s):
    """Search form: no diacritics (German, Greek, Latin transliterations), lower case, ß->ss, ς->σ."""
    if not s:
        return ''
    missing = {ord(c) for c in set(s)} - _table.keys()
    for o in missing:
        _table[o] = fold_char(chr(o))
    return s.translate(_table)

def fold_map(s):
    """Folded string plus, for each folded char, the index of its source char."""
    out, idx = [], []
    for i, c in enumerate(s):
        f = fold_char(c)
        out.append(f)
        idx.extend([i] * len(f))
    return ''.join(out), idx

def fts_engine():
    db = sqlite3.connect(':memory:')
    try:
        db.execute("CREATE VIRTUAL TABLE t USING fts5(x, tokenize='unicode61 remove_diacritics 0')")
        return 'fts5'
    except sqlite3.OperationalError:
        db.execute('CREATE VIRTUAL TABLE t USING fts4(x, tokenize=unicode61 "remove_diacritics=0")')
        return 'fts4'
    finally:
        db.close()

# ---------------------------------------------------------------- query
TOKEN_RE = re.compile(r'\w+', re.U)

def parse_query(q):
    """User syntax: words (AND), "exact phrase", prefix*, OR between items, -word to exclude.
    Returns list of items {tokens, prefix, neg, or_before}."""
    items, or_next = [], False
    for m in re.finditer(r'(-?)"([^"]+)"(\*?)|(\S+)', q):
        if m.group(4) is not None:
            w = m.group(4)
            if w == 'OR' or w == '|':
                or_next = True
                continue
            neg = w.startswith('-') and len(w) > 1
            if neg:
                w = w[1:]
            prefix = w.endswith('*')
            toks = TOKEN_RE.findall(fold(w))
        else:
            neg, prefix = bool(m.group(1)), bool(m.group(3))
            toks = TOKEN_RE.findall(fold(m.group(2)))
        if not toks:
            continue
        items.append(dict(tokens=toks, prefix=prefix, neg=neg, or_before=or_next and bool(items)))
        or_next = False
    return items

def fts_expr(items, engine, column=None):
    pos = [it for it in items if not it['neg']]
    neg = [it for it in items if it['neg']]
    if not pos:
        return None
    def term(it):
        p = '"' + ' '.join(it['tokens']) + '"'
        if it['prefix']:
            p = p + '*' if engine == 'fts5' else '"' + ' '.join(it['tokens']) + '*"'
        if column and engine == 'fts4':
            p = column + ':' + p
        return p
    if engine == 'fts5':
        expr = ''
        for it in pos:
            expr += (' OR ' if it['or_before'] else (' AND ' if expr else '')) + term(it)
        if neg:
            expr = '(' + expr + ') NOT (' + ' OR '.join(term(it) for it in neg) + ')'
        if column:
            expr = '{' + column + '} : (' + expr + ')'
        return expr
    # fts4 standard syntax: implicit AND, OR binds tighter, -term excludes
    expr = ''
    for it in pos:
        expr += (' OR ' if it['or_before'] else ' ') + term(it)
    for it in neg:
        expr += ' -' + term(it)
    return expr.strip()

def item_regex(it):
    toks = [re.escape(t) for t in it['tokens']]
    if it['prefix']:
        toks[-1] += r'\w*'
    return r'(?<!\w)' + r'\W{1,4}'.join(toks) + r'(?!\w)'

def highlight_regex(items):
    pats = [item_regex(it) for it in items if not it['neg']]
    return re.compile('|'.join(pats)) if pats else None

def snippets(text, rx, width=110, maxn=2):
    """Best windows around hits, returned as html with <mark>."""
    if not text or rx is None:
        return []
    folded, idx = fold_map(text)
    hits = [(m.start(), m.end()) for m in rx.finditer(folded)]
    if not hits:
        return []
    # greedy: take densest windows
    chosen = []
    for s, e in hits:
        if any(abs(s - c) < width * 2 for c, _ in chosen):
            continue
        chosen.append((s, e))
        if len(chosen) >= maxn:
            break
    out = []
    for s, _ in chosen:
        a = max(0, s - width)
        b = min(len(folded), s + width)
        oa = idx[a] if a < len(idx) else 0
        ob = idx[b - 1] + 1 if b - 1 < len(idx) else len(text)
        # extend to word boundaries
        while oa > 0 and not text[oa - 1].isspace() and s - a < width + 20:
            oa -= 1
            a -= 1
        piece_hits = [(idx[hs], idx[he - 1] + 1) for hs, he in hits if idx[hs] >= oa and idx[he - 1] < ob]
        buf, pos = [], oa
        for hs, he in piece_hits:
            buf.append(html.escape(text[pos:hs]))
            buf.append('<mark>' + html.escape(text[hs:he]) + '</mark>')
            pos = he
        buf.append(html.escape(text[pos:ob]))
        out.append(('… ' if oa > 0 else '') + ''.join(buf).strip() + (' …' if ob < len(text) else ''))
    return out

def count_hits(text, rx):
    if not text or rx is None:
        return 0
    return sum(1 for _ in rx.finditer(fold(text)))
