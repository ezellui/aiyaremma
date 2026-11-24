"""hwphxml.py — the HWPh XML database (md2xml.py) as the bridge programs read it.

    import hwphxml
    db = hwphxml.open('hwph-data.xml')
    db.articles[aid].lemma …            # every article, by number (in the order of the numbers)
    db.html(aid), db.plain(aid, 'b')    # the body as HTML; plain text of body / notes ('n') / literature ('l')
    db.persons[pid].key …               # cited persons;  db.cites: (aid, pid, n_body, n_notes, n_lit)
    db.register, db.xrefs               # register of vol. 13, cross-references of the articles

The database is a large file; what the programs ask for again and again (the tables and where each
article's texts stand in the file) is read once and kept in a cache file next to it
(<database>.bridge.pickle, made anew when the database changes). An article's texts are then read
from their place in the file, as a table row would be read.
Python 3.8+, standard library only.
"""
import collections, mmap, os, pickle, re
from xml.etree import ElementTree as ET
from xml.sax.saxutils import unescape

CACHE_VERSION = 1

Article = collections.namedtuple('Article', 'id lemma lemma_fold band kind col_from col_to pdf_from pdf_to n_notes n_chars authors')
Person = collections.namedtuple('Person', 'id key name name_fold n_articles n_body n_notes n_lit n_ed editor variants role')
Register = collections.namedtuple('Register', 'id term term_fold target qualifier band col kind dst')


def _int(v):
    return int(v) if v not in (None, '') else None


class HwphXml:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        st = os.stat(self.path)
        sig = (CACHE_VERSION, st.st_size, st.st_mtime_ns)
        cache = self.path + '.bridge.pickle'
        data = None
        if os.path.exists(cache):
            try:
                with open(cache, 'rb') as f:
                    data = pickle.load(f)
                if data.get('sig') != sig:
                    data = None
            except Exception:
                data = None
        if data is None:
            data = self._read()
            data['sig'] = sig
            try:
                with open(cache, 'wb') as f:
                    pickle.dump(data, f, protocol=4)
            except OSError:
                pass
        self.articles = data['articles']         # aid -> Article, in the order of the numbers
        self._spans = data['spans']              # aid -> (html_from, html_to, raw?, b, n, l spans)
        self.persons = data['persons']           # pid -> Person, in the order of the numbers
        self.cites = data['cites']               # [(aid, pid, n_body, n_notes, n_lit)] in the order of the file
        self.register = data['register']         # [Register] by id
        self.xrefs = data['xrefs']               # [(src, target, dst)]
        self._f = None
        self._by_pid = None

    # ------------------------------------------------------------------ reading the file once
    def _read(self):
        articles, spans = {}, {}
        with open(self.path, 'rb') as fh:
            mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
            end_arts = mm.find(b'</articles>')
            pos = mm.find(b'<articles>')
            while True:
                a0 = mm.find(b'<article ', pos, end_arts)
                if a0 < 0:
                    break
                t1 = mm.find(b'>\n', a0) + 1
                at = ET.fromstring(mm[a0:t1] + b'</article>').attrib
                au0 = mm.find(b'<authors>', t1)
                au1 = mm.find(b'</authors>', au0) + len(b'</authors>')
                authors = [x.text or '' for x in ET.fromstring(mm[au0:au1])]
                h0 = mm.find(b'<html', au1)
                raw = mm[h0:h0 + 10] == b'<html-raw>'
                open_t = b'<html-raw>' if raw else b'<html>'
                close_t = b'</html-raw>' if raw else b'</html>'
                h1 = mm.find(close_t + b'\n<plain part="b">', h0)
                b0 = h1 + len(close_t) + len(b'\n<plain part="b">')
                b1 = mm.find(b'</plain>\n<plain part="n">', b0)
                n0 = b1 + len(b'</plain>\n<plain part="n">')
                n1 = mm.find(b'</plain>\n<plain part="l">', n0)
                l0 = n1 + len(b'</plain>\n<plain part="l">')
                l1 = mm.find(b'</plain>\n', l0)
                aid = int(at['id'])
                articles[aid] = Article(aid, at.get('lemma', ''), at.get('lemma-fold', ''), at.get('band', ''), at.get('kind', ''),
                                        _int(at.get('col-from')), _int(at.get('col-to')), _int(at.get('pdf-from')),
                                        _int(at.get('pdf-to')), _int(at.get('n-notes')), _int(at.get('n-chars')), authors)
                spans[aid] = (h0 + len(open_t), h1, raw, (b0, b1), (n0, n1), (l0, l1))
                pos = mm.find(b'</article>\n', l1)
            tail_end = mm.rfind(b'</hwph>')
            tail = ET.fromstring(b'<t>' + mm[end_arts + len(b'</articles>'):tail_end] + b'</t>')
            mm.close()
        persons = {}
        for p in tail.find('persons'):
            import json
            pid = int(p.get('id'))
            persons[pid] = Person(pid, p.get('key'), p.get('name'), p.get('name-fold'), _int(p.get('n-articles')),
                                  _int(p.get('n-body')), _int(p.get('n-notes')), _int(p.get('n-lit')), _int(p.get('n-ed')),
                                  _int(p.get('editor')), json.loads(p.get('variants') or '[]'), p.get('role'))
        cites = [(int(c.get('aid')), int(c.get('pid')), int(c.get('n-body')), int(c.get('n-notes')), int(c.get('n-lit')))
                 for c in tail.find('cites')]
        register = [Register(int(r.get('id')), r.get('term'), r.get('term-fold'), r.get('target'), r.get('qualifier'),
                             r.get('band'), r.get('col'), r.get('kind'), _int(r.get('dst'))) for r in tail.find('register')]
        xrefs = [(int(x.get('src')), x.get('target'), _int(x.get('dst'))) for x in tail.find('xrefs')]
        return dict(articles=dict(sorted(articles.items())), spans=spans, persons=dict(sorted(persons.items())),
                    cites=cites, register=register, xrefs=xrefs)

    # ------------------------------------------------------------------ an article's texts
    def _bytes(self, span):
        if self._f is None:
            self._f = open(self.path, 'rb')
        self._f.seek(span[0])
        return self._f.read(span[1] - span[0]).decode('utf-8')

    def html(self, aid):
        """the article as the reader shows it (the XHTML of the database, character for character)"""
        h0, h1, raw, *_ = self._spans[aid]
        s = self._bytes((h0, h1))
        return unescape(s) if raw else s

    def plain(self, aid, part='b'):
        """plain text: 'b' body (with the words of its diagrams), 'n' notes, 'l' literature"""
        return unescape(self._bytes(self._spans[aid][{'b': 3, 'n': 4, 'l': 5}[part]]))

    # ------------------------------------------------------------------ what the programs ask
    def article_rows(self, *fields, kind=None):
        """tuples of the given fields of every article, in the order of the numbers"""
        return [tuple(getattr(a, f) for f in fields) for a in self.articles.values() if kind is None or a.kind == kind]

    def cites_of(self, pids):
        """the citation rows of these persons, in the order of the file"""
        if self._by_pid is None:
            self._by_pid = collections.defaultdict(list)
            for r in self.cites:
                self._by_pid[r[1]].append(r)
        return sorted((r for p in set(pids) for r in self._by_pid.get(p, ())), key=self.cites_order)

    def cites_order(self, row, _pos={}):
        if not _pos:
            _pos.update((id(r), i) for i, r in enumerate(self.cites))
        return _pos[id(row)]

    def register_dsts(self, term, like=False):
        """[(article, count)] of the register entries (not authors) whose folded term is term (or, with
        like, matches it as an SQL LIKE pattern), by article number"""
        test = like_matcher(term) if like else (lambda s: s == term)
        c = collections.Counter(r.dst for r in self.register if r.dst is not None and r.kind != 'author' and test(r.term_fold or ''))
        return sorted(c.items())


def like_matcher(pattern):
    """SQL LIKE: % any run, _ one character, ASCII letters without regard to case"""
    rx = ''.join('.*' if ch == '%' else '.' if ch == '_' else re.escape(ch) for ch in pattern)
    cre = re.compile(rx, re.S)

    def low(s):
        return ''.join(ch.lower() if 'A' <= ch <= 'Z' else ch for ch in s)
    cre = re.compile(''.join('.*' if ch == '%' else '.' if ch == '_' else re.escape(low(ch)) for ch in pattern), re.S)
    return lambda s: cre.fullmatch(low(s)) is not None


_OPEN = {}


def open(path):
    """the database at path (read once per program)"""
    path = os.path.abspath(path)
    if path not in _OPEN:
        _OPEN[path] = HwphXml(path)
    return _OPEN[path]
