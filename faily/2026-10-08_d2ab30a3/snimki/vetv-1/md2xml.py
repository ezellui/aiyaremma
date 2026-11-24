#!/usr/bin/env python3
"""
md2xml.py — HWPh Markdown volumes -> one XML database (prototype of the Eldamo-style pipeline).

    python md2xml.py HWPh_epub -o hwph-data.xml --reader path/to/hwph_reader

Prototype note: the Markdown parser is the existing one (hwph_build.build), run unchanged; only its
output sink is swapped — the rows it produces are kept in memory and written as XML instead of a
SQLite file. In a real port the parser would emit these elements directly.

Not written: the word index (tables terms, doclen). The XQuery side computes it from <plain>.
Article bodies are stored as XHTML subtrees; the few bodies that are not well-formed XML (defects of
the current HTML output) are stored as text in <html-raw> and counted in the report.
"""
import argparse, json, os, re, sqlite3, sys, time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

# characters XML 1.0 does not allow
BAD_XML = re.compile('[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]')


class KeepOpen:
    """A sqlite3 connection whose close() does nothing, so the parser's rows stay in memory."""
    def __init__(self, con):
        self._con = con

    def close(self):
        pass

    def __getattr__(self, name):
        return getattr(self._con, name)


def run_parser(reader, src):
    sys.path.insert(0, reader)
    import hwph_build
    con = sqlite3.connect(':memory:')
    real_connect = hwph_build.sqlite3.connect
    hwph_build.sqlite3.connect = lambda _path: KeepOpen(con)
    try:
        hwph_build.build(src, ':memory:')
    except FileNotFoundError:
        pass                                    # the final size report of a file that was never written
    finally:
        hwph_build.sqlite3.connect = real_connect
    return con


def attrs(pairs):
    out = []
    for k, v in pairs:
        if v is None:
            continue
        out.append(' %s=%s' % (k, quoteattr(clean(str(v)))))
    return ''.join(out)


BAD = [0]


def clean(s):
    if BAD_XML.search(s):
        BAD[0] += 1
        s = BAD_XML.sub('�', s)
    return s


def num(v):
    """REAL columns: repr keeps the exact double, as json.dumps writes it"""
    return repr(v) if isinstance(v, float) else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('-o', '--out', default='hwph-data.xml')
    ap.add_argument('--reader', required=True)
    a = ap.parse_args()
    t0 = time.time()
    con = run_parser(os.path.abspath(a.reader), os.path.abspath(a.src))
    from hwph_serve import unz            # the parser's compression of text columns
    from hwph_common import fold_char
    t1 = time.time()
    raw_bodies = []
    chars = set()
    with open(a.out, 'w', encoding='utf-8') as out:
        w = out.write
        meta = dict(con.execute('SELECT key, value FROM meta'))
        w('<?xml version="1.0" encoding="UTF-8"?>\n<hwph%s>\n' % attrs(sorted(meta.items())))

        w('<articles>\n')
        cm = {r[0]: r[1:] for r in con.execute('SELECT aid, b, n, l FROM colmap')}
        for row in con.execute('SELECT id, lemma, lemma_fold, band, kind, col_from, col_to, pdf_from, pdf_to, '
                               'authors, n_notes, n_chars, toc, html, plain_body, plain_notes, plain_lit '
                               'FROM articles ORDER BY id'):
            (aid, lemma, lfold, band, kind, c1, c2, p1, p2, authors, nn, nc, toc, h, pb, pn, pl) = row
            w('<article%s>\n' % attrs([('id', aid), ('lemma', lemma), ('lemma-fold', lfold), ('band', band),
                                        ('kind', kind), ('col-from', c1), ('col-to', c2), ('pdf-from', p1),
                                        ('pdf-to', p2), ('n-notes', nn), ('n-chars', nc)]))
            w('<authors>%s</authors>\n' % ''.join('<author>%s</author>' % escape(clean(x)) for x in json.loads(authors)))
            w('<toc>%s</toc>\n' % ''.join('<entry%s/>' % attrs([('id', e[0]), ('label', e[1]), ('level', e[2])])
                                          for e in json.loads(toc)))
            body = unz(h)
            try:
                if BAD_XML.search(body):
                    raise ET.ParseError('control character')
                ET.fromstring('<html>' + body + '</html>')
                w('<html>' + body + '</html>\n')
            except ET.ParseError:
                raw_bodies.append(aid)
                w('<html-raw>%s</html-raw>\n' % escape(clean(body)))
            for part, t in (('b', pb), ('n', pn), ('l', pl)):
                text = unz(t)
                chars.update(text)
                w('<plain part="%s">%s</plain>\n' % (part, escape(clean(text))))
            chars.update(lemma)
            chars.update(' '.join(json.loads(authors)))
            b, n, l = cm.get(aid, (None, None, None))
            w('<colmap%s/>\n' % attrs([('b', b), ('n', n), ('l', l)]))
            w('</article>\n')
        w('</articles>\n')

        def table(name, item, sql, cols):
            w('<%s>\n' % name)
            for r in con.execute(sql):
                w('<%s%s/>\n' % (item, attrs((c, num(v)) for c, v in zip(cols, r))))
            w('</%s>\n' % name)

        table('xrefs', 'x', 'SELECT src, target, dst FROM xrefs ORDER BY rowid', ['src', 'target', 'dst'])
        table('register', 'r', 'SELECT id, term, term_fold, target, qualifier, band, col, kind, dst FROM register ORDER BY id',
              ['id', 'term', 'term-fold', 'target', 'qualifier', 'band', 'col', 'kind', 'dst'])
        table('persons', 'p', 'SELECT id, key, name, name_fold, n_articles, n_body, n_notes, n_lit, n_ed, editor, variants, role '
              'FROM persons ORDER BY id',
              ['id', 'key', 'name', 'name-fold', 'n-articles', 'n-body', 'n-notes', 'n-lit', 'n-ed', 'editor', 'variants', 'role'])
        table('cites', 'c', 'SELECT aid, pid, n_body, n_notes, n_lit FROM cites ORDER BY rowid',
              ['aid', 'pid', 'n-body', 'n-notes', 'n-lit'])
        table('mentions', 'm', 'SELECT aid, dst, tf, score FROM mentions ORDER BY rowid', ['aid', 'dst', 'tf', 'score'])
        w('<sgroups>\n')
        for gid, name in con.execute('SELECT id, name FROM sgroups ORDER BY id'):
            w('<group%s>' % attrs([('id', gid), ('name', name)]))
            for aid, label, pos in con.execute('SELECT aid, label, pos FROM sgroup_items WHERE gid=? ORDER BY rowid', (gid,)):
                w('<item%s/>' % attrs([('aid', aid), ('label', label), ('pos', pos)]))
            w('</group>\n')
        w('</sgroups>\n')
        table('abbrevs', 'abbrev', 'SELECT sec, title, pos, abbr, text FROM abbrevs ORDER BY rowid',
              ['sec', 'title', 'pos', 'abbr', 'text'])
        table('article-list', 'e', 'SELECT pos, lemma, zh, band, col, page, aid FROM aindex ORDER BY rowid',
              ['pos', 'lemma', 'zh', 'band', 'col', 'page', 'aid'])

        # folding table: the search form of every character of the indexed text, as Python computes it
        # (Unicode data of XQuery engines differs in details; the table keeps both sides identical)
        w('<fold>\n')
        for c in sorted(chars):
            f = fold_char(c)
            if f != c and not BAD_XML.search(c):
                w('<f%s/>\n' % attrs([('c', c), ('to', f)]))
        w('</fold>\n')
        # characters of the folded text that do not belong to a word (Python's \w decides), so that
        # the XQuery side splits words exactly as the parser's regular expression does
        folded = set()
        for c in chars:
            folded.update(fold_char(c))
        nonword = ''.join(sorted(c for c in folded if not re.match(r'\w', c) and not BAD_XML.search(c)))
        w('<nonword>%s</nonword>\n' % escape(nonword))
        w('</hwph>\n')
    print(json.dumps(dict(parse_s=round(t1 - t0), write_s=round(time.time() - t1),
                          size_mb=round(os.path.getsize(a.out) / 1e6, 1), raw_bodies=raw_bodies,
                          replaced_control_chars=BAD[0]), ensure_ascii=False), file=sys.stderr)


if __name__ == '__main__':
    main()
