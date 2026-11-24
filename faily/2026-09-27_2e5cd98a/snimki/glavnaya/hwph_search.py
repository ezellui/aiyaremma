"""
hwph_search.py — the search of the reader: query language, index lookup, ranking, snippets.

The same algorithm is written twice: here for hwph_serve.py and in static_api.js for the static
reader. Both read one index built by hwph_build.py (table terms: every folded word with its
postings), so they give the same answers; tools/parity checks that they do.

Query language (German operator words as on the HWPh CD-ROM are accepted too):
    Seele Leib            both words in one article (AND is implied; AND / UND may be written)
    "anima mundi"         exact phrase (any punctuation between the words)
    transzendent*         * any letters, anywhere in the word: *prin?ip*
    br?der                ? exactly one letter;  ^# a digit, ^$ a letter
    Hegel OR Schelling    either (ODER, |); OR binds closer than AND
    Seele -Leib           without (NOT, NICHT)
    (Proklos OR Neuplatonis*) Hegel      brackets
    Proklos NEAR Hegel    both within 20 words of each other (NEAR/5, NAHE/5)
Options: case-sensitive (only the written capitals), spelling-tolerant (Prinzip ~ Princip,
Cultur ~ Kultur, Theil ~ Teil, seyn ~ sein).
"""
import math, re

from hwph_common import fold

COLS = ['lemma', 'body', 'notes', 'lit', 'authors']
WEIGHTS = (10.0, 1.0, 0.35, 0.5, 2.0)
K1, B = 1.2, 0.75
NEAR_DEFAULT = 20
MAX_EXPAND = 300          # words one pattern may stand for
MAX_VERIFY = 1500         # articles whose text is read to check a phrase, NEAR or capitals (static reader)
WORD = re.compile(r'\w+')


class QueryError(Exception):
    pass


# ---------------------------------------------------------------- spelling-tolerant key
def skey(term):
    """One key for historical and variant spellings of a folded word: ph/f, th/t, c/z/k, y/i,
    ae/a, doubled letters. Prinzip = Princip, Kultur = Cultur, Teil = Theil, sein = seyn."""
    t = term.replace('ph', 'f').replace('th', 't').replace('rh', 'r').replace('dt', 't')
    t = t.replace('ae', 'a').replace('oe', 'o').replace('ue', 'u').replace('ck', 'k').replace('tz', 'z')
    t = t.replace('ch', '\x00')
    t = re.sub('c(?=[eiy])', 'z', t).replace('c', 'k')
    t = t.replace('\x00', 'ch').replace('y', 'i')
    return re.sub(r'(.)\1+', r'\1', t)


# ---------------------------------------------------------------- parsing
TOKEN_RE = re.compile(r'\s*(?:(\()|(\))|(-?)"([^"]*)"|(\S+?)(?=[\s()"]|$))')
OPS = {'OR': 'or', 'ODER': 'or', '|': 'or', 'AND': 'and', 'UND': 'and', 'NOT': 'not', 'NICHT': 'not'}
NEAR_RE = re.compile(r'(?:NEAR|NAHE)(?:/(\d+))?$')


def lex(q):
    out, pos = [], 0
    q = q.strip()
    while pos < len(q):
        m = TOKEN_RE.match(q, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        if m.group(1):
            out.append(('(',))
        elif m.group(2):
            out.append((')',))
        elif m.group(4) is not None:
            if m.group(3):
                out.append(('not',))
            out.append(('phrase', m.group(4)))
        else:
            w = m.group(5)
            if w in OPS:
                out.append((OPS[w],))
            elif NEAR_RE.match(w):
                out.append(('near', int(NEAR_RE.match(w).group(1) or NEAR_DEFAULT)))
            elif len(w) > 1 and w[0] == '-':
                out.append(('not',))
                out.append(('word', w[1:]))
            else:
                out.append(('word', w))
    return out


def word_pattern(w):
    """A written word -> (folded pattern parts, original). Parts: literal text and wildcards."""
    parts, i = [], 0
    while i < len(w):
        c = w[i]
        if c == '*':
            parts.append(('any',))
        elif c == '?':
            parts.append(('one',))
        elif c == '^' and i + 1 < len(w):
            n = w[i + 1]
            i += 1
            parts.append(('digit',) if n == '#' else ('letter',) if n == '$' else ('lit', fold(n)))
        else:
            parts.append(('lit', c))
        i += 1
    return parts


def word_tokens(text):
    """Split a written word or phrase into folded words, keeping wildcards inside words."""
    out = []
    for raw in re.findall(r'[\w*?^#$]+', text):
        f = ''.join(p[1] if p[0] == 'lit' else '' for p in word_pattern(raw))
        if not WORD.search(fold(f)) and not any(p[0] != 'lit' for p in word_pattern(raw)):
            continue
        out.append(raw)
    return out


def parse(q):
    """Query -> tree: ('or', [..]) ('and', [..]) ('not', x) ('near', n, [leaves]) ('term', raw) ('phrase', [raw..])"""
    toks = lex(q)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def leaf():
        t = peek()
        if t is None:
            return None
        if t[0] == '(':
            take()
            e = expr_and()
            if peek() and peek()[0] == ')':
                take()
            return e
        if t[0] == 'phrase':
            take()
            ws = word_tokens(t[1])
            if not ws:
                return None
            return ('term', ws[0]) if len(ws) == 1 else ('phrase', ws)
        if t[0] == 'word':
            take()
            ws = word_tokens(t[1])
            if not ws:
                return None
            return ('term', ws[0]) if len(ws) == 1 else ('phrase', ws)
        return None

    def unary():
        t = peek()
        if t and t[0] == 'not':
            take()
            x = near()
            return ('not', x) if x else None
        return near()

    def near():
        x = leaf()
        items, dist = [x], None
        while peek() and peek()[0] == 'near':
            dist = take()[1] if dist is None else min(dist, take()[1])
            y = leaf()
            if y is not None:
                items.append(y)
        items = [i for i in items if i is not None]
        if dist is None or len(items) < 2:
            return items[0] if items else None
        if any(i[0] not in ('term', 'phrase') for i in items):
            raise QueryError('NEAR')
        return ('near', dist, items)

    def expr_or():
        x = unary()
        items = [x]
        while peek() and peek()[0] == 'or':
            take()
            items.append(unary())
        items = [i for i in items if i is not None]
        if not items:
            return None
        return items[0] if len(items) == 1 else ('or', items)

    def expr_and():
        items = []
        while peek() and peek()[0] != ')':
            if peek()[0] == 'and':
                take()
                continue
            if peek()[0] == 'or':          # a stray OR at the start of a group
                take()
                continue
            x = expr_or()
            if x is None:
                if peek() and peek()[0] not in (')',):
                    take()
                continue
            items.append(x)
        if not items:
            return None
        return items[0] if len(items) == 1 else ('and', items)

    tree = expr_and()
    while peek():                            # unbalanced ')' — read on
        take()
        more = expr_and()
        if more is not None:
            tree = ('and', [tree, more]) if tree is not None else more
    return tree


def leaves(tree, neg=False):
    """(leaf, negated) pairs in reading order"""
    if tree is None:
        return []
    k = tree[0]
    if k in ('term', 'phrase', 'near'):
        return [(tree, neg)]
    if k == 'not':
        return leaves(tree[1], True)
    out = []
    for c in tree[1]:
        out += leaves(c, neg)
    return out


# ---------------------------------------------------------------- patterns -> words of the index
def pattern_regex(raw, case=False):
    """Regex (Python and JavaScript alike) for one written word with wildcards."""
    out = []
    for p in word_pattern(raw):
        if p[0] == 'lit':
            ch = p[1] if case else fold(p[1])
            out.append(re.escape(ch) if ch else '')
        elif p[0] == 'any':
            out.append(r'\w*')
        elif p[0] == 'one':
            out.append(r'\w')
        elif p[0] == 'digit':
            out.append(r'\d')
        else:
            out.append(r'[^\W\d_]')
    return ''.join(out)


def js_escape_regex(s):
    """Python's re.escape leaves a few characters escaped that JavaScript's u-flag rejects."""
    return re.sub(r'\\([^\w\\.*+?^${}()|\[\]/-])', r'\1', s)


def kind_of(raw):
    ps = word_pattern(raw)
    wild = [i for i, p in enumerate(ps) if p[0] != 'lit']
    if not wild:
        return 'plain'
    if wild == [len(ps) - 1] and ps[-1][0] == 'any':
        return 'prefix'
    return 'wild'


class Index:
    """Access to the index; hwph_serve.py and the parity tools give one over the database."""
    def __init__(self, con):
        self.con = con
        self.cache = {}
        n, lens = 0, {}
        for aid, l0, l1, l2, l3, l4 in con.execute('SELECT aid, l0, l1, l2, l3, l4 FROM doclen'):
            lens[aid] = (l0, l1, l2, l3, l4)
            n += 1
        self.lengths = lens
        self.n = n
        self.avgdl = sum(sum(v) for v in lens.values()) / max(1, n)

    def postings(self, term):
        if term in self.cache:
            return self.cache[term]
        r = self.con.execute('SELECT post FROM terms WHERE term=?', (term,)).fetchone()
        d = decode(r[0]) if r else {}
        if len(self.cache) > 5000:
            self.cache.clear()
        self.cache[term] = d
        return d

    def expand(self, raw, tolerant):
        """Words of the index a written word stands for (most frequent first), and whether the
        list was cut."""
        f = fold(raw)
        k = kind_of(raw)
        if k == 'plain' and not tolerant:
            return [f], False
        rx = re.compile(pattern_regex(raw) + r'\Z')
        lit = re.match(r'\w*', ''.join(p[1] if p[0] == 'lit' else '\x00' for p in word_pattern(raw)))
        head = fold(lit.group(0)) if lit else ''
        if tolerant:
            if k == 'plain':
                rows = self.con.execute('SELECT term, docs FROM terms WHERE skey=?', (skey(f),)).fetchall()
            else:
                # a pattern and tolerance: the pattern over the tolerant keys of the words
                krx = re.compile(pattern_regex(skey_pattern(raw)) + r'\Z')
                rows = [(t, d) for t, d, s in self.con.execute('SELECT term, docs, skey FROM terms') if krx.match(s)]
        elif head:
            rows = [(t, d) for t, d in self.con.execute(
                'SELECT term, docs FROM terms WHERE term >= ? AND term < ?', (head, head + '\uffff')) if rx.match(t)]
        else:
            rows = [(t, d) for t, d in self.con.execute('SELECT term, docs FROM terms') if rx.match(t)]
        rows.sort(key=lambda x: (-x[1], x[0]))
        return [t for t, _ in rows[:MAX_EXPAND]], len(rows) > MAX_EXPAND

    def texts(self, aid):
        """the five columns of an article as the index saw them"""
        raise NotImplementedError


def skey_pattern(raw):
    """a pattern with its literal runs put through skey (wildcards stay)"""
    out, run = '', ''
    for p in word_pattern(raw):
        if p[0] == 'lit':
            run += fold(p[1])
        else:
            out += skey(run) if run else ''
            run = ''
            out += {'any': '*', 'one': '?', 'digit': '^#', 'letter': '^$'}[p[0]]
    return out + (skey(run) if run else '')


def decode(s):
    out, prev = {}, 0
    for e in s.split(' '):
        a, c = e.split(':')
        prev += int(a, 36)
        cnt = [0, 0, 0, 0, 0]
        for i, x in enumerate(c.split(',')):
            cnt[i] = int(x, 36)
        out[prev] = cnt
    return out


def encode(docs):
    parts, prev = [], 0
    for aid in sorted(docs):
        c = list(docs[aid])
        while c and c[-1] == 0:
            c.pop()
        parts.append(b36(aid - prev) + ':' + ','.join(b36(x) for x in c))
        prev = aid
    return ' '.join(parts)


def b36(n):
    s, n = '', int(n)
    while True:
        n, r = divmod(n, 36)
        s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
        if not n:
            return s


# ---------------------------------------------------------------- evaluation
SEP = r'[^\w]+'


def leaf_regex(leaf, words_of, case):
    """Regex over (folded, or with case the original) text for one leaf: each word is its
    expansions (or its pattern)."""
    def word_rx(raw):
        if case:
            return pattern_regex(raw, case=True)
        ws = words_of(raw)
        if ws is None:                     # prefix: the pattern itself
            return pattern_regex(raw)
        return '(?:' + '|'.join(re.escape(w) for w in sorted(ws, key=len, reverse=True)) + ')' if ws else '(?!)'
    if leaf[0] == 'term':
        body = word_rx(leaf[1])
    else:
        body = SEP.join(word_rx(w) for w in leaf[1])
    return r'(?<!\w)' + body + r'(?!\w)'


class Search:
    def __init__(self, index, texts, tolerant=False, case=False, column=None, verify_all=True):
        self.ix, self.texts = index, texts
        self.tolerant, self.case, self.col = tolerant, case, column
        self.verify_all = verify_all
        self.expanded = {}
        self.cut = False
        self.approx = None

    # the index words a written word stands for; None = a prefix, looked up as a range
    def words_of(self, raw):
        if raw in self.expanded:
            return self.expanded[raw]
        if kind_of(raw) == 'prefix' and not self.tolerant:
            self.expanded[raw] = None
            return None
        ws, cut = self.ix.expand(raw, self.tolerant)
        self.cut = self.cut or cut
        self.expanded[raw] = ws
        return ws

    def word_docs(self, raw):
        ws = self.words_of(raw)
        if ws is None:
            head = fold(raw[:-1])
            ws = [t for (t,) in self.ix.con.execute(
                'SELECT term FROM terms WHERE term >= ? AND term < ?', (head, head + '\uffff'))]
        out = {}
        for w in ws:
            for aid, c in self.ix.postings(w).items():
                e = out.get(aid)
                if e is None:
                    out[aid] = list(c)
                else:
                    for i in range(5):
                        e[i] += c[i]
        return out

    def restrict(self, docs):
        if self.col is None:
            return docs
        out = {}
        for a, c in docs.items():
            if c[self.col]:
                z = [0, 0, 0, 0, 0]
                z[self.col] = c[self.col]
                out[a] = z
        return out

    def count_in_texts(self, rx, aid, near=None):
        t = self.texts(aid)
        cols = [t['lemma'], t['b'], t['n'], t['l'], t['au']]
        out = []
        for i, x in enumerate(cols):
            if self.col is not None and i != self.col:
                out.append(0)
                continue
            s = x if self.case else fold(x or '')
            out.append(near(s) if near else len(rx.findall(s or '')))
        return out

    def leaf_docs(self, leaf):
        """articles of one leaf with per-column counts"""
        if leaf[0] == 'term':
            docs = self.word_docs(leaf[1])
            if not self.case:
                return self.restrict(docs)
            cand = docs
            rx = re.compile(leaf_regex(leaf, self.words_of, True))
            return self.check(cand, lambda a: self.count_in_texts(rx, a))
        if leaf[0] == 'phrase':
            lists = [self.word_docs(w) for w in leaf[1]]
            cand = intersect(lists)
            rx = re.compile(leaf_regex(leaf, self.words_of, self.case))
            return self.check(cand, lambda a: self.count_in_texts(rx, a))
        # near: every item somewhere, then the windows in the text
        items = leaf[2]
        lists = []
        for it in items:
            if it[0] == 'term':
                lists.append(self.word_docs(it[1]))
            else:
                lists.append(intersect([self.word_docs(w) for w in it[1]]))
        cand = intersect(lists)
        rxs = [re.compile(leaf_regex(it, self.words_of, self.case)) for it in items]
        dist = leaf[1]
        return self.check(cand, lambda a: self.count_in_texts(None, a, near=lambda s: near_count(s, rxs, dist)))

    def check(self, cand, counter):
        keys = sorted(cand)
        if not self.verify_all and len(keys) > MAX_VERIFY:
            keys.sort(key=lambda a: (-sum(cand[a]), a))
            self.approx = dict(checked=MAX_VERIFY, of=len(keys))
            keys = sorted(keys[:MAX_VERIFY])
        out = {}
        for a in keys:
            c = counter(a)
            if any(c):
                out[a] = c
        return out

    def run(self, tree):
        self.leaf_results = []
        pos = self.eval(tree)
        return pos

    def eval(self, node):
        k = node[0]
        if k in ('term', 'phrase', 'near'):
            d = self.leaf_docs(node)
            self.leaf_results.append((node, d))
            return set(d)
        if k == 'or':
            s = set()
            for c in node[1]:
                if c[0] == 'not':
                    continue
                s |= self.eval(c)
            return s
        if k == 'and':
            pos, negs = None, []
            for c in node[1]:
                if c[0] == 'not':
                    negs.append(c[1])
                    continue
                r = self.eval(c)
                pos = r if pos is None else pos & r
            if pos is None:
                return set()
            for n in negs:
                pos -= self.eval_neg(n)
            return pos
        if k == 'not':
            return set()
        return set()

    def eval_neg(self, node):
        saved = self.leaf_results
        self.leaf_results = []
        r = self.eval(node)
        self.leaf_results = saved
        return r

    def score(self, aid):
        L = self.ix.lengths.get(aid, (0, 0, 0, 0, 0))
        D = sum(L)
        s = 0.0
        for leaf, docs in self.leaf_results:
            c = docs.get(aid)
            if not c:
                continue
            n_hit = len(docs)
            idf = math.log((self.ix.n - n_hit + 0.5) / (n_hit + 0.5))
            if idf <= 0:
                idf = 1e-6
            f = sum(WEIGHTS[i] * c[i] for i in range(5))
            s += idf * (f * (K1 + 1)) / (f + K1 * (1 - B + B * D / self.ix.avgdl))
        return s

    def highlight(self, tree):
        """one regex for snippets and marks: every positive leaf (NEAR: its items)"""
        parts = []
        for leaf, neg in leaves(tree):
            if neg:
                continue
            for it in (leaf[2] if leaf[0] == 'near' else [leaf]):
                parts.append(leaf_regex(it, self.words_of, self.case).replace(SEP, r'[^\w]{1,4}'))
        return '|'.join(parts) if parts else None


def intersect(lists):
    if not lists:
        return {}
    lists = sorted(lists, key=len)
    out = {}
    for a, c in lists[0].items():
        cc, ok = list(c), True
        for other in lists[1:]:
            e = other.get(a)
            if e is None:
                ok = False
                break
            cc = [min(x, y) for x, y in zip(cc, e)]
        if ok:
            out[a] = cc
    return out


def near_count(text, rxs, dist):
    """How many NEAR matches: every item within `dist` words of each other (in words between the
    end of the first and the start of the last)."""
    if not text:
        return 0
    # word positions: index of the word each character starts
    starts = [m.start() for m in WORD.finditer(text)]
    import bisect
    spans = []
    for rx in rxs:
        occ = []
        for m in rx.finditer(text):
            a = bisect.bisect_left(starts, m.start())
            b = bisect.bisect_right(starts, m.end() - 1) - 1
            occ.append((a, max(a, b)))
        if not occ:
            return 0
        spans.append(occ)
    n = 0
    for (a0, b0) in spans[0]:
        ok = True
        lo, hi = a0, b0
        for occ in spans[1:]:
            best = None
            for (a, b) in occ:
                l2, h2 = min(lo, a), max(hi, b)
                # words between the first end and the last start
                gap = max(a, lo) - min(b, hi) - 1
                if gap <= dist and (best is None or h2 - l2 < best[1] - best[0]):
                    best = (l2, h2)
            if best is None:
                ok = False
                break
            lo, hi = best
        if ok:
            n += 1
    return n
