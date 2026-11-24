#!/usr/bin/env python3
"""
md2xml.py — the Markdown volumes of the HWPh (Bd01.md … Bd13.md, Bd*s.md, extras.json, img/) as one
XML database, from which the XQuery files of xq/ make the reader.

    python md2xml.py <folder with the BdNN.md> [-o hwph-data.xml]

Python 3.8+, standard library only. Needs lib/ next to it: hwph_common.py and hwph_cite.py (folding,
cited persons), persons_fix.json (hand decisions on persons), img_svg/ (vector versions of pictures).

What the database holds (everything the reader shows or searches, nothing derived from it):
  <articles>      every article: lemma, volume, columns, pages, authors, table of contents, the body
                  as XHTML, the plain text of body / notes / literature, where each column begins
  <xrefs>         cross-references of the articles          <register>  the register volume (vol. 13)
  <persons>       cited persons, <cites> who is cited where  <mentions>  concepts discussed in passing
  <sgroups>       subject groups of vol. 13                  <abbrevs>   lists of abbreviations
  <article-list>  the article list of the printed edition, matched with the articles
  <fold>, <nonword>, <rawsep>   how a character is folded for search and where a word ends (the
                  XQuery side splits words exactly as Python's \\w+ does)
The word index is not in it: xq/global.xq and xq/positions.xq compute it from the plain texts.
"""
import argparse, collections, glob, html, json, math, os, re, sys, time, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, 'lib')
sys.path.insert(0, LIB)
from hwph_common import fold, fold_char, greek_fix  # noqa: E402
import hwph_cite  # noqa: E402

for _st in (sys.stdout, sys.stderr):
    try:
        _st.reconfigure(errors='replace')
    except Exception:
        pass


def log(*a):
    print(*a, file=sys.stderr)


FM_RE = re.compile(r'^---\n(lemma: .*?)\n---\n', re.M | re.S)
NOTE_DEF_RE = re.compile(r'^\[\^(\d+)\]:\s?(.*)$')
REF_RE = re.compile(r'\[\^(\d+)\]')
SEC_RE = re.compile(r'^(?:\*\*)?((?:[IVX]{1,5}|[A-H]|\d{1,2}|[a-h])\.(?:\s?\d{1,2}\.)?)\s')
# a line-end hyphen that survived conversion (page or column break): 'Unbe- grenzte'
DEHYPH_RE = re.compile(r'(?<=[a-zäöüß])(\w)-[ \n]((?!(?:und|oder|bzw|sowie|u|wie|als|noch|statt|resp|bis|zu|or|and|et|ou|e|y|und/oder)\b)[a-zäöüß])')

# internal cross-references: the printed arrow is \u0001 in the text layer
XREF_BEFORE = re.compile(r'\u0001(?:\{p(\d{7})\})?\s*‹([^›]{1,120})›')
XREF_SD = re.compile(r'(‹[^›]{1,120}›|\*[^*]{1,80}\*|\w[\w\-]*)\s*\u0001(?:\{p(\d{7})\})?\s*\(s\.\s?d\.\)')
XREF_BARE = re.compile(r'\u0001\{p(\d{7})\}')      # an epub arrow whose target text is not in the usual form
XPAGE_RE = re.compile(r'(?<=\u0001)\{p\d{7}\}')
# one quoted target that names several articles, each with its own arrow:
# '→ ‹Gestalt-P., → Gestalttheorie›' — two references, not one whose text holds an arrow
XREF_MULTI = re.compile('\u0001(\\{p\\d{7}\\})?\\s*‹([^›\u0001]{1,120}(?:\u0001(?:\\{p\\d{7}\\})?[^›\u0001]{1,120})+)›')
EPUB_PAGE_OFFSET = 86      # page N of the epub (Digitale Bibliothek) is page N + 86 of the PDF


# ---------------------------------------------------------------- reading the volumes
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
        if meta.get('quelle') != 'epub':         # epub text is clean: no text-layer repair
            body = greek_fix(body)
            body = DEHYPH_RE.sub(r'\1\2', body)
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
    lemma = re.sub(r'(?<=\w)\((?=\w{4})', ' (', lemma)   # 'empirische(cultural' but not 'Weltreligion(en)'
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
        # a literature block ends where the next section of a many-part article begins: a section
        # number (I., 2., 1.4., a)), bold, an italic section heading or the first paragraph that calls a
        # note. A literature entry looks like none of these, even when it starts «I. M. BOCHEŃSKI:» or
        # «V. BROCHARD:» (initials, not section numbers) or points at a note («R. E. PALMER s. Anm. [3]»,
        # written [^3] by the PDF text layer), so a paragraph that opens like an entry stays literature.
        entry = re.match(r"^(?:[A-ZÄÖÜ][A-Za-zäöü]?\.(?:-[A-ZÄÖÜ]\.)?\s?)+(?:(?:v\.|von|van|de|du|la|le|del|da)\s)*[A-ZÄÖÜ][A-ZÄÖÜŃŁŠČ'’\-]{2,}"
                         r"[^:]{0,80}?(?::|\ss\.\sAnm\.|,?\sa\.\s?a?\.?\s?O\.)", p)
        if in_lit and not entry and (
                re.match(r'^(?:\*\*)?(?:[IVX]{1,5}\.|\d{1,2}(?:\.\d{1,2})*\.|[a-h]\))\s', p)
                or p.startswith('**')
                or re.search(r'\[\^\d+\]', re.sub(r'(?:Anm\.|a\.\s?a?\.?\s?O\.)[\s–\-]*\[\^\d+\]', '', p))
                # (the PDF text layer may split the italics at a line break: «*… und* *Seinsdenken.*»)
                or re.match(r'^(?:[A-H]\.\s)?\*[^*:]{2,160}\.\*\s–\s', re.sub(r'\*\s+\*', ' ', p))
                and not re.match(r'^\*?(?:Ergänzende|Einzeldarstellung|Gesamtdarstellung|Bibliographi|Textausgab|Quellen|Literatur|Sammelb|Zeitschrift)', p)):
            in_lit = False
        out.append(('lit' if in_lit else 'p', p))
    return out, notes


def runs_of(nums):
    """Series index for each note number: every numbered section restarts its notes at 1.
    A stray out-of-order number (text-layer noise) does not open a new series. A [1] right after a
    [1] does: a section with a single note is followed by the next section's [1] (‹Dialektik› I.3/I.4)."""
    run, top, res = 0, 0, []
    for n in nums:
        if n == 1 and top >= 1:
            run += 1
            top = 0
        top = max(top, n)
        res.append(run)
    return res


# ---------------------------------------------------------------- pictures
MATH_RE = re.compile(r'(?<!\\)\$([^$\n]+?)\$')     # '$a$$b$' are two formulas side by side
PIC_RE = re.compile(r'!\[\]\(img/([0-9a-f]{32})\.png\)')
SVG_DIR = [None]          # set by convert(): the source img folder, where hash.svg may lie next to hash.png


def svg_for(h):
    """Inline SVG for picture h if a vector version exists: it takes the page colour, stays sharp, and
    its words are real text. None -> the PNG stays."""
    cands = ([os.path.join(SVG_DIR[0], h + '.svg')] if SVG_DIR[0] else []) + [os.path.join(LIB, 'img_svg', h + '.svg')]
    path = next((c for c in cands if os.path.exists(c)), None)
    if path is None:
        return None
    svg = open(path, encoding='utf-8').read()
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    w = int(m.group(1)) if m else 0
    svg = re.sub(r'\s(?:width|height)="\d+"', '', svg, count=2)
    return svg, w


def svg_words(h):
    got = svg_for(h)
    if not got:
        return ''
    return ' '.join(html.unescape(t) for t in re.findall(r'<text[^>]*>([^<]*)</text>', got[0]))


def svg_open(svg, attrs):
    """the opening <svg with our attributes first; an attribute the file sets itself is not repeated
    (a second role= makes the element invalid; the browser kept the first one, ours)"""
    tag = re.match(r'<svg\b[^>]*>', svg).group(0)
    own = set(re.findall(r'\s([\w:-]+)=', tag))
    keep = [(k, v) for k, v in attrs if k not in own] + [(k, v) for k, v in attrs if k in own and k != 'role']
    head = '<svg ' + ''.join('%s="%s" ' % kv for kv in keep)
    if 'role' in own:
        tag2 = re.sub(r'\srole="[^"]*"', '', tag, count=1)
        svg = tag2 + svg[len(tag):]
        head = '<svg ' + ''.join('%s="%s" ' % kv for kv in attrs)
    return svg.replace('<svg ', head, 1)


def pic_inline(h):
    got = svg_for(h)
    if got:
        return svg_open(got[0], [('class', 'pic'), ('role', 'img')])
    return '<img class="pic" src="img/%s.png" alt=""/>' % h


def pic_figure(h):
    got = svg_for(h)
    if got:
        svg, w = got
        return '<figure class="pic vec">%s</figure>' % svg_open(svg, [('role', 'img'), ('style', 'max-width:%dpx' % max(120, w // 3))])
    return '<figure class="pic"><img src="img/%s.png" alt=""/></figure>' % h


def inline(md):
    # formulas and pictures are set aside before escaping and emphasis: TeX has * and _ of its own
    kept = []

    def keep(html_):
        kept.append(html_)
        return '%d' % (len(kept) - 1)
    md = MATH_RE.sub(lambda m: keep('<span class="m" data-tex="%s">%s</span>' % (html.escape(m.group(1)), html.escape(m.group(1)))), md)
    md = PIC_RE.sub(lambda m: keep(pic_inline(m.group(1))), md)
    s = inline_text(md)
    return re.sub('(\\d+)', lambda m: kept[int(m.group(1))], s)


# ---------------------------------------------------------------- inline marks -> HTML
# ⟦517⟧ — where the text continues on column 517 of the printed edition (hwph2md.py writes it)
COL_RE = re.compile('⟦(\\d+)⟧')
# ^2^1906 (edition), T~i~ (index): pandoc marks, written by epub2md.py. These two serve the plain
# text (unmark), which keeps its old form so that the search index is unchanged.
SUP_RE = re.compile(r'(?<!\[)\^([^\s^\]\[]{1,40})\^')
SUB_RE = re.compile(r'(?<=[^\s~‹(«\[])~([^\s~]{1,40})~')

# The Markdown of the volumes is written from the epub's HTML by epub2md.py: *…*, **…**, ^…^, ~…~
# around an element whose text does not begin or end with a space, nested as the elements were, and
# an asterisk, caret or tilde of the text itself is written as it is. The rules below read it back:
# superscript and subscript are found first (their content has no spaces) and become containers whose
# content is read in turn; emphasis then pairs its asterisks as CommonMark does (a closing run takes
# the nearest opening one), where an asterisk may open if a non-space follows it and close if a
# non-space precedes it; an asterisk that pairs with nothing stays an asterisk. Checked against the
# epub: of 235 431 paragraphs with such marks, the old regular expressions gave 331 wrong (asterisks
# lost, emphasis across the wrong text, 24 not even well-formed), these rules 11 (6 of them only
# whether an asterisk after an italic letter is italic too).
ATOM_LO = 0xF0000                          # pieces already made (column marks, sup, sub) stand as one character
ATOM_RE = re.compile('[\U000F0000-\U000FFFFD]')
SUPSUB = re.compile(r'(\[\^\d+\])|\^([^ \t\n^\[\]]{1,40}?)\^|~([^ \t\n~]{1,40}?)~')
QUOTED = {'‹': '›', '«': '»', '(': ')', '[': ']'}
# asterisks that are signs, not emphasis: the numbers of the Principia Mathematica (*10.02, *22.01)
LITERAL_STAR = re.compile(r'(?:(?<=^)|(?<=[\s«(]))\*(?=\d+\.\d)')
PAGE_FOLLOW = set(' \t,;.:)]–-') | {''}


def _space(c):
    return c == '' or c.isspace()


def _flanking(before, after, prefix):
    """(can open, can close) of a run of asterisks between the characters before and after"""
    can_open, can_close = not _space(after), not _space(before)
    # a page number with an asterisk (109*, 14*;  VII*-): it closes nothing it does not end
    if (before.isdigit() or re.search(r'(?<![A-Za-z])[IVXLC]+$', prefix)) and after in PAGE_FOLLOW:
        can_open = False
    if before in '–—' and after.isdigit():                      # r–*5
        can_close = False
    if before in '([{' and after in ')]},;':                    # (*)  {*, |}
        can_open = can_close = False
    if unicodedata.category(before or ' ') in ('Sm', 'So') and (after.isalpha() or ATOM_RE.match(after or ' ')):
        can_close = False                                       # x*∈*α: after a sign an asterisk opens
    return can_open, can_close


def emphasis(s, atoms):
    """s: text with atom characters -> HTML; emphasis by the delimiter runs of CommonMark (6.2)"""
    toks = []                  # ['t', text] | ['d', count, can_open, can_close, original count] | ['n', tag, children]
    i, n = 0, len(s)
    while i < n:
        if s[i] == '*':
            j = i
            while j < n and s[j] == '*':
                j += 1
            lf, rf = _flanking(s[i - 1] if i > 0 else '', s[j] if j < n else '', s[max(0, i - 8):i])
            toks.append(['d', j - i, lf, rf, j - i])
            i = j
        else:
            j = s.find('*', i)
            j = n if j < 0 else j
            toks.append(['t', s[i:j]])
            i = j
    ci = 0
    while ci < len(toks):
        c = toks[ci]
        if c[0] != 'd' or not c[3]:
            ci += 1
            continue
        found = None
        for oi in range(ci - 1, -1, -1):
            if toks[oi][0] == 'd' and toks[oi][2]:
                found = oi
                break
        if found is None:
            if not c[2]:
                c[:] = ['t', '*' * c[1]]
            ci += 1
            continue
        o = toks[found]
        # ***x***: bold outside, italic inside (as the epub nests them)
        use = 1 if o[1] >= 3 and c[1] >= 3 else (2 if o[1] >= 2 and c[1] >= 2 else 1)
        inner = toks[found + 1:ci]
        for t in inner:                                  # delimiters left between them are text now
            if t[0] == 'd':
                t[:] = ['t', '*' * t[1]]
        node = ['n', 'b' if use == 2 else 'i', inner]
        o[1] -= use
        c[1] -= use
        if c[1] and o[1] == 0 and not c[2]:             # *R**: the closer's further asterisks are text inside
            inner.append(['t', '*' * c[1]])
            c[1] = 0
        if o[1] and c[1] == 0:                          # **p*: the opener's further asterisk is text before
            o[:] = ['t', '*' * o[1]]
        toks[found + 1:ci] = [node]
        ci = found + 2
        if o[0] == 'd' and o[1] == 0:
            del toks[found]
            ci -= 1
        if c[1] == 0:
            del toks[ci]

    def out(ts):
        r = []
        for t in ts:
            if t[0] == 't':
                r.append(t[1])
            elif t[0] == 'd':
                r.append('*' * t[1])
            else:
                r.append('<%s>%s</%s>' % (t[1], out(t[2]), t[1]))
        return ''.join(r)
    return ATOM_RE.sub(lambda m: atoms[ord(m.group(0)) - ATOM_LO], out(toks))


def inline_text(md):
    s = html.escape(md, quote=False)
    atoms = []

    def atom(h):
        atoms.append(h)
        return chr(ATOM_LO + len(atoms) - 1)
    s = COL_RE.sub(lambda m: atom('<span class="col" data-col="%s"></span>' % m.group(1)), s)
    # a small letter written above another (Middle High German u with e above): stacked in the reader,
    # the plain text keeps the Unicode combining letter for search
    s = re.sub('(\\w)ͤ', lambda m: atom('<span class="ovl">' + m.group(1) + '</span>'), s)

    def supsub(m):
        if m.group(1):
            return m.group(1)                   # a note call [^12]
        if m.group(3) is not None and len(m.group(3)) == 1 and not m.group(3).isalnum():
            b, a = m.string[m.start() - 1:m.start()], m.string[m.end():m.end() + 1]
            if b in QUOTED and QUOTED[b] == a:
                return m.group(0)               # ‹~◊~›: a tilde sign quoted with its operand
        tag, inner = ('sup', m.group(2)) if m.group(2) is not None else ('sub', m.group(3))
        return atom('<%s>%s</%s>' % (tag, emphasis(inner, atoms), tag))
    s = SUPSUB.sub(supsub, s)
    s = LITERAL_STAR.sub(lambda m: atom('*'), s)
    return emphasis(s, atoms)


# ---------------------------------------------------------------- plain text (search, places)
def unmark(s):
    s = XPAGE_RE.sub('', s)
    return SUB_RE.sub(r'\1', SUB_RE.sub(r'\1', SUP_RE.sub(r'\1', s)))


def plain(md):
    s = COL_RE.sub(' ', REF_RE.sub('', unmark(md))).replace('\u0001', ' ')
    s = MATH_RE.sub(' ', PIC_RE.sub(' ', s)).replace('$$', ' ')
    s = s.replace('**', '').replace('*', '')
    return re.sub(r'\s+', ' ', s).strip()


COL_SENT = ''


def plain_cols(md):
    """plain(md) and where in it the column marks stood: [(offset, column), …]. The marks become a
    sentinel that survives the other steps and is then taken out again."""
    cols = [int(x) for x in COL_RE.findall(md)]
    if not cols:
        return plain(md), []
    s = COL_RE.sub(' ' + COL_SENT + ' ', REF_RE.sub('', unmark(md))).replace('\u0001', ' ')
    s = MATH_RE.sub(' ', PIC_RE.sub(' ', s)).replace('$$', ' ')
    s = s.replace('**', '').replace('*', '')
    s = re.sub(r'\s+', ' ', s).strip()
    out, marks, i = [], [], 0
    for m in re.finditer(COL_SENT + ' ?', s):
        out.append(s[i:m.start()])
        marks.append(sum(len(x) for x in out))
        i = m.end()
    out.append(s[i:])
    text = ''.join(out).strip()
    lead = len(''.join(out)) - len(''.join(out).lstrip())
    marks = [max(0, min(len(text), m - lead)) for m in marks]
    return text, list(zip(marks, cols))


def join_cols(pieces):
    """' \\n'.join of plain texts, with their column marks moved to offsets in the joined text"""
    text, marks, off = [], [], 0
    for t, ms in pieces:
        marks += [[off + o, c] for o, c in ms]
        text.append(t)
        off += len(t) + 2
    return ' \n'.join(text), marks


def md_table(p):
    rows = [r.strip().strip('|').split('|') for r in p.strip().split('\n')]
    rows = [r for r in rows if not all(re.fullmatch(r'\s*:?-{3,}:?\s*', c) for c in r)]
    head, body = rows[0], rows[1:]

    def cell(tag, c):
        return '<%s>%s</%s>' % (tag, inline(c.strip()), tag)
    out = ['<div class="tbl"><table><thead><tr>' + ''.join(cell('th', c) for c in head) + '</tr></thead><tbody>']
    for r in body:
        out.append('<tr>' + ''.join(cell('td', c) for c in r) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


# ---------------------------------------------------------------- lemma resolution
def lemma_key(s):
    s = fold(s)
    s = re.sub(r'[^\w/;]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


STEM_SUF = ('ungen', 'es', 'en', 'er', 'em', 'e', 'n', 's')


def stem(k):
    for suf in STEM_SUF:
        if k.endswith(suf) and len(k) - len(suf) >= 4:
            return k[:-len(suf)]
    return k


class Resolver:
    def __init__(self, rows):
        self.exact = {}
        self.stems = {}
        for aid, lemma in rows:
            k = lemma_key(lemma)
            self.exact.setdefault(k, aid)
            # "Wahrheit; Wahrheitstheorie" and "Kant, Immanuel" style: first element as a weaker key
            for part in re.split(r'[;,/]', lemma):
                self.exact.setdefault('~' + lemma_key(part), aid)
            first = lemma_key(re.split(r'[;,/(]', lemma)[0])
            self.stems.setdefault(stem(first), aid)

    def find(self, text):
        t = re.sub(r'\s+', ' ', text.replace('*', '')).strip()
        if re.fullmatch(r'\w{1,3}\.(?:\s?\w{1,3}\.)*', t):
            return None                      # abbreviated self-reference ('M.', 'h.M.')
        cands = [t,
                 re.sub(r'\s+[IVX]+\.?(?:\s*[A-Z\d]{1,2}\.?)*(?:\s*\(.*\))?$', '', t),   # section qualifier
                 re.sub(r'\s+\d{1,2}\.$', '', t),
                 re.sub(r'\s*\(.*\)$', '', t)]
        for c in cands:
            k = lemma_key(c)
            if k in self.exact:
                return self.exact[k]
        for c in cands:
            k = '~' + lemma_key(re.split(r'[;,/]', c)[0])
            if k in self.exact:
                return self.exact[k]
        # inflected forms in running text: 'Aggregate' -> 'Aggregat', 'Unbewußten' -> 'Unbewußtes, das'
        k = lemma_key(cands[1])
        if stem(k) in self.stems and len(k) >= 5:
            return self.stems[stem(k)]
        for suf in ('en', 'es', 'er', 'e', 'n', 's'):
            if k.endswith(suf) and len(k) - len(suf) >= 4:
                for kk in (k[:-len(suf)], '~' + k[:-len(suf)]):
                    if kk in self.exact:
                        return self.exact[kk]
        return None


# ---------------------------------------------------------------- register (Bd. 13)
REG_LOC = re.compile(r'(?:\s+(\d)(?=\s+\d))?\s+(1[0-3]|[1-9])\s+(\d{1,4})(f{1,2}\.|[–-]\d{1,4})?(?!\d)')
REG_QUAL = re.compile(r'(?:\s+(?:[IVX]{1,5}|[A-H])(?=\s|$))*(?:\s+\([^)]{1,30}\))?')


def _lemma_index(lemma_list):
    by_first = {}
    for l in sorted(set(lemma_list), key=len, reverse=True):
        by_first.setdefault(l[:3], []).append(l)
    return by_first


def _parse_ref(piece, by_first):
    """'Target [qual] [band col] rest' -> (target, qual, band, col, rest)"""
    piece = piece.lstrip()
    target = None
    for l in by_first.get(piece[:3], []):
        if piece.startswith(l) and (len(piece) == len(l) or not piece[len(l)].isalnum()):
            target = l
            break
    if target is None:
        m = re.match(r'(.{1,80}?)(?=\s+(?:[IVX]{1,5}\s+)?(?:1[0-3]|[1-9])\s+\d|\s+·|\s+s\. auch|$)', piece)
        target = m.group(1).strip() if m else piece[:40].strip()
    rest = piece[len(target):]
    q = REG_QUAL.match(rest)
    qual = q.group(0).strip() if q else ''
    rest = rest[q.end():] if q else rest
    band = col = None
    m = REG_LOC.match(rest)
    if m:
        if m.group(1):
            qual = (qual + ' ' + m.group(1)).strip()
        band, col = m.group(2), m.group(3) + (m.group(4) or '')
        rest = rest[m.end():]
    rest = rest.strip()
    # further column ranges of the same reference: '. 1195–1203', ', 34f.'
    rest = re.sub(r'^(?:[.,;]?\s*(?:(?:1[0-3]|[1-9])\s+)?\d{1,4}(?:f{1,2}\.|[–-]\d{1,4})?\.?(?=\s|$|[.,;]))+', '', rest).strip(' .,;')
    return target, qual, band, col, rest


def parse_register(text, lemma_list):
    """The term register is flattened into one stream: 'term ◊ Target [qual] [band col] · ◊ Target …'.
    What follows a reference decides the owner of the next one:
      '·'        -> same term continues
      's. auch'  -> the following references are 'see also' of the current headword
      nothing    -> the next ◊ is itself a headword entry ('◊ Advaita 1 86f.')
      other text -> that text is the next term.
    Targets are matched against the known lemmas (longest match), which makes the stream splittable."""
    text = re.sub(r'\s+', ' ', text.replace('*', ''))
    by_first = _lemma_index(lemma_list)
    pieces = text.split('\u0001')
    entries = []
    owner = pieces[0].strip(' ·') or None
    mode, next_main = 'ref', owner is None
    for piece in pieces[1:]:
        target, qual, band, col, rest = _parse_ref(piece, by_first)
        if next_main or owner is None:
            owner, mode = target, 'ref'
            entries.append((target, target, qual, band, col, 'main'))
        else:
            entries.append((owner, target, qual, band, col, 'see' if mode == 'see' else 'ref'))
        next_main = False
        if rest == '':
            next_main = True
        elif rest.startswith('·'):
            tail = rest.lstrip('· ').strip()
            if tail:
                owner, mode = tail, 'ref'
        elif rest.startswith('s. auch'):
            mode = 'see'
        else:
            owner, mode = rest.strip(' ·,;'), 'ref'
    return entries


def parse_authors(text, lemma_list):
    """'Register der Verfasser': 'Surname Given ◊ Lemma band col ◊ Lemma band col Next Name ◊ …'"""
    text = re.sub(r'\s+', ' ', text.replace('*', ''))
    by_first = _lemma_index(lemma_list)
    pieces = text.split('\u0001')

    def clean(n):
        return re.sub(r'^(?:[A-ZÄÖÜ] )+(?=[A-ZÄÖÜ][a-zäöüß])', '', n.strip(' ·,;'))
    owner = clean(pieces[0])
    entries = []
    for piece in pieces[1:]:
        target, qual, band, col, rest = _parse_ref(piece, by_first)
        entries.append((owner, target, qual, band, col, 'author'))
        if rest:
            # what stays after a reference may still belong to it — the part of the article and its
            # columns: 'I-II 9 574–580 Menne Albert', '(institut. Formen) 7 846–848'; only the words
            # after the last number are the next author
            tail = re.sub(r'^.*\d(?:\s?ff?\.|\.)?', '', rest) if re.search(r'\d', rest) else rest
            tail = clean(tail)
            if re.match(r'[A-ZÄÖÜ][^\d]*$', tail) and (' ' in tail or tail in ('Red', 'Red.')):
                owner = tail
    return entries


def fix_start_columns(raw, reg):
    """The column an article begins in. On a page of the PDF where a new column of the book begins, the
    running head already names the new one; an article that starts in the last lines of the column
    before got that later number (about one article in four: 'Abfolge' 5 instead of 4). The register
    of vol. 13 gives the true first column of every article: where it is exactly one lower, it wins,
    and the mark of the next column goes right after the opening words, where the register's own
    references show the break to be."""
    def key(t):
        return re.sub(r'[^a-z0-9]', '', fold(t))
    # every column the register gives for the name: besides the article itself ('Denken 2 60–104') the
    # register may point to single places in it ('Fall; Abfall 3 889'), so all of them are kept
    starts = collections.defaultdict(set)
    for term, target, qual, band, col, kind in reg:
        m = re.match(r'(\d+)', col or '')
        if kind == 'main' and m:
            starts[(key(target), band)].add(int(m.group(1)))
    fixed = 0
    for i, (lemma, band, kind, meta, body) in enumerate(raw):
        cols = starts.get((key(lemma), band), ()) if kind == 'article' else ()
        if meta['col_from'] - 1 not in cols:
            continue
        s = meta['col_from'] - 1
        n = meta['col_from']
        meta['col_from'] = s
        head, sep, rest = body.partition('\n\n')
        m = re.search(r'[.;:]\s', head[20:300])
        cut = 20 + m.end() if m else (head.find(' ', 40) + 1 or len(head))
        if '$' in head[:cut]:                       # not inside a formula
            cut = len(head)
        body = head[:cut].rstrip() + ' ⟦%d⟧ ' % n + head[cut:].lstrip() + sep + rest
        raw[i] = (lemma, band, kind, meta, body)
        fixed += 1
    log(f'начальная колонка исправлена по регистру: {fixed} статей')
    return fixed


# ---------------------------------------------------------------- cited persons, concepts
ED_BEFORE = re.compile(r'(?:hg\.|Hg\.|ed\.|éd\.|Ed\.|eds\.|übers\.|Übers\.|trad\.|Ausg\.|bearb\.|Bearb\.)'
                       r'\s*(?:von\s|v\.\s|by\s|par\s)?$')


def person_role(b, n, l, editor):
    """'source' — a thinker the article talks ABOUT (named in the running text, hardly ever in the
    bibliography: Kant, Plotin, Windelband); 'scholar' — a researcher the article cites (notes and
    bibliographies: Gilson, Diels, Pohlenz, Koselleck); 'mixed' — both (Cassirer, Gadamer, Blumenberg).
    Measured on the proportions of the three contexts; editors of editions are scholars."""
    t = b + n + l
    if editor:
        return 'scholar'
    if t < 3:
        return 'source' if b and not l else 'scholar'
    body, lit = b / t, l / t
    if body >= 0.3 and lit < 0.1:
        return 'source'
    if body < 0.15 or lit >= 0.25:
        return 'scholar'
    return 'mixed'


# lemmas that are also everyday words of scholarly prose: counting them says nothing about the topic
MENTION_STOP = set('''Einfluß Begriff Bedeutung Konzept Präsenz Identifikation Frage Problem Beispiel Folge Ausdruck
Aufgabe Bereich Beziehung Entwicklung Funktion Gebrauch Gegensatz Grundlage Grund Hinsicht Interesse Kontext Lehre
Methode Möglichkeit Rolle Sinn Stellung Tendenz Terminus Text Theorie Unterschied Verhältnis Wort Zusammenhang
Zweck Moment Ansatz Aspekt Position Auffassung Anwendung Diskussion Darstellung Behandlung Untersuchung Kritik Erörterung'''.split())


def build_mentions(arts):
    """Concepts an article discusses without an explicit cross-reference: the head of another lemma
    ('Kategorie' of 'Kategorie, Kategorienlehre') occurring in the running text, weighted tf·idf."""
    rows = [(a['id'], a['lemma'], a['plain_b']) for a in arts if a['kind'] == 'article']
    size = {a['id']: a['n_chars'] for a in arts}
    heads = {}
    cands = []
    for aid, lemma, _ in rows:
        parts = [x.strip() for x in re.split(r'[,;/(]', lemma)]
        # every capitalised part names the article ('Leib, Körper' is also 'Körper')
        for k, h in enumerate(parts):
            if h and (k == 0 or (h[0].isupper() and ' ' not in h)):
                cands.append((aid, lemma, h))
    for aid, lemma, h in cands:
        if len(h) < 4 or re.search(r'\d', h) or not h[0].isupper():
            continue
        toks = tuple(h.split())
        if len(toks) > 3:
            continue
        if h in MENTION_STOP:
            continue
        # one head, several lemmas ('Körper, starrer', 'Körperschema'): the lemma that IS the head,
        # otherwise the largest article — the general treatment of the word
        cur = heads.get(toks)
        if cur is None or (cur[1] != h and (lemma == h or size[aid] > size[cur[0]])):
            heads[toks] = (aid, lemma)
    by_first = collections.defaultdict(list)
    for toks, (aid, _) in heads.items():
        by_first[toks[0]].append((toks, aid))
    SUF = ('', 'n', 'en', 's', 'es', 'e', 'er', 'ern')
    tfs = {}
    df = collections.Counter()
    for aid, lemma, pb in rows:
        words = re.findall(r"[A-Za-zÄÖÜäöüßÀ-ÿ\-]+", pb)
        c = collections.Counter()
        for i, w in enumerate(words):
            if not w[:1].isupper():
                continue
            for suf in SUF:
                base = w[:-len(suf)] if suf and w.endswith(suf) else (w if not suf else None)
                if not base or base not in by_first:
                    continue
                for toks, dst in by_first[base]:
                    if len(toks) == 1 or tuple(words[i + 1:i + len(toks)]) == toks[1:]:
                        if dst != aid:
                            c[dst] += 1
                break
        tfs[aid] = c
        for d in c:
            df[d] += 1
    n = len(rows)
    out = []
    for aid, c in tfs.items():
        scored = [(d, tf, tf * math.log(n / df[d])) for d, tf in c.items() if tf >= 2 and df[d] < 0.25 * n]
        scored.sort(key=lambda x: -x[2])
        out += [(aid, d, tf, round(sc, 3)) for d, tf, sc in scored[:20]]
    return out


def load_persons_fix(arts, path=os.path.join(LIB, 'persons_fix.json')):
    """Hand decisions on persons the rules cannot tell apart or together (see persons_fix.json):
    merge — key -> key it belongs to; split — key + articles (lemmas) -> another key, with a name;
    keep — keys that are a person of their own and must not fold into a longer variant."""
    if not os.path.exists(path):
        return {}, {}, {}, {}
    fx = json.load(open(path, encoding='utf-8'))
    merge = {m['key']: m['into'] for m in fx.get('merge', [])}
    by_lemma = {}
    for a in arts:
        if a['kind'] == 'article':
            by_lemma[a['lemma']] = a['id']          # a later article of the same name wins
    split, names = {}, {}
    for sp in fx.get('split', []):
        for a in sp['articles']:
            aid = a if isinstance(a, int) else by_lemma.get(a)
            if aid is None:
                log('persons_fix.json: нет статьи', a)
                continue
            split[(sp['key'], aid)] = sp['to']
        if sp.get('name'):
            names[sp['to']] = sp['name']
    keep = {}
    for kp in fx.get('keep', []):
        keep[kp['key']] = kp
        if kp.get('name'):
            names[kp['key']] = kp['name']
    return merge, split, names, keep


def build_persons(arts, mentions):
    """-> persons [dict], cites [(aid, pid, n_body, n_notes, n_lit)]"""
    raws = collections.Counter(m[2] for m in mentions)
    fix_merge, fix_split, fix_names, fix_keep = load_persons_fix(arts)
    norm = hwph_cite.Normalizer(raws, keep=fix_keep)
    fix_used = set()
    key_of = {raw: norm.key(raw) for raw in raws}
    # a bare surname is read as the person of that name the article named last before it, with initials
    # or with a full multi-word name (OTTO after R. OTTO, after OTTO VON FREISING); an editor in a
    # reference ('hg. I. H. FICHTE') is not such a mention. Text, notes and bibliography are read in
    # this order. Before any such mention the bare name goes to the person who owns it ('1.2. FICHTE
    # verwendet' is J. G. Fichte, though I. H. FICHTE follows).
    resolved = {}
    order = {'b': 0, 'n': 1, 'l': 2}
    by_art = collections.defaultdict(list)
    for i, m in enumerate(mentions):
        by_art[m[0]].append(i)
    for aid, idx in by_art.items():
        idx.sort(key=lambda i: (order[mentions[i][1]], mentions[i][4]))
        last = {}
        for i in idx:
            _, ctx, raw, ed, pos = mentions[i]
            k0 = key_of[raw]
            if not k0:
                continue
            ini, core = norm.parts(raw)
            c = norm.core_map.get(core, core)
            if ini or ' ' in c:
                k = k0
                if not ed:
                    kc = k0.split('|')[0]
                    last[kc] = k0
                    if ' ' in kc:
                        last['#' + kc.split(' ')[0]] = k0
            else:
                prev = last.get(c) or last.get('#' + c)
                k = norm.key_in(raw, collections.Counter({prev: 1}) if prev else collections.Counter())
            resolved[i] = k
    per = collections.defaultdict(collections.Counter)          # key -> counters
    variants = collections.defaultdict(collections.Counter)
    cites = collections.defaultdict(collections.Counter)        # (aid, key) -> counters
    for i, (aid, ctx, raw, ed, pos) in enumerate(mentions):
        k = resolved.get(i)
        if not k:
            continue
        if k in fix_merge:
            fix_used.add(k)
            k = fix_merge[k]
        if (k, aid) in fix_split:
            fix_used.add((k, aid))
            k = fix_split[(k, aid)]
        per[k][ctx] += 1
        per[k]['ed'] += ed
        variants[k][raw] += 1
        cites[(aid, k)][ctx] += 1
    ids = {}
    persons = []
    for i, k in enumerate(sorted(per, key=lambda k: -sum(per[k][c] for c in 'bnl'))):
        c = per[k]
        total = c['b'] + c['n'] + c['l']
        # editors of editions (GLOCKNER, GERHARDT, COLLI): named after 'hg.' or never in the running text
        editor = int(c['ed'] > 0.4 * total or (total >= 30 and c['b'] < 0.03 * total))
        ids[k] = i + 1
        name = fix_names.get(k) or norm.display.get(k, k.split('|')[0])
        persons.append(dict(id=i + 1, key=k, name=name, name_fold=fold(name), n_articles=0, n_body=c['b'],
                            n_notes=c['n'], n_lit=c['l'], n_ed=c['ed'], editor=editor,
                            variants=[v for v, _ in variants[k].most_common(8)],
                            role=person_role(c['b'], c['n'], c['l'], editor)))
    fix_used |= set(fix_keep) & set(per)
    for k in (sorted(set(fix_merge) - fix_used, key=str) + sorted(set(fix_split) - fix_used, key=str)
              + sorted(set(fix_keep) - fix_used)):
        log('persons_fix.json: не встретилось', k)
    cite_rows = [(aid, ids[k], c['b'], c['n'], c['l']) for (aid, k), c in cites.items()]
    n_art = collections.Counter(r[1] for r in cite_rows)
    for p in persons:
        p['n_articles'] = n_art[p['id']]
    return persons, cite_rows


# how the reader finds a person in an article's text (a JavaScript regular expression, flags 'gu')
JS_SYNTAX = set('.*+?^${}()|[]/\\')


def _js_escape(t):
    return ''.join('\\' + c if c in JS_SYNTAX else c for c in t)


def person_pattern(p):
    """small caps (KANT, KANTS), the normal form used after the first mention (Kant, Kants) and, for
    multi-word names, the surname alone (Thomas von Aquin … Aquin)"""
    forms = {p['key'].split('|')[0]}
    for v in p['variants']:
        core = hwph_cite.split_name(v)[1]
        if hwph_cite.valid_core(core):
            forms.add(core)
    more = set()
    for f in forms:
        t = hwph_cite.title(f)
        more.add(t)
        last = t.split(' ')[-1]
        if ' ' in t and len(last) >= 4 and last[0].isupper():
            more.add(last)
    forms |= more
    forms = sorted({f for f in forms if f}, key=lambda f: (-len(f), f))
    alt = '|'.join('\\s+'.join(_js_escape(w) for w in f.split()) for f in forms)
    return r'(?<![\p{L}\p{N}])(?:' + alt + r")(?:s|S|'|’)?(?![\p{L}\p{N}])"


# ---------------------------------------------------------------- vol. 13: subject groups; extras
def build_sgroups(texts, resolver):
    """'Register der Sachgruppen' (vol. 13): '*Ästhetik und Kunsttheorie* ◊ Abstraktion VI ◊ Abwesenheit …'
    -> 47 subject groups and the articles (or article parts) listed under each"""
    groups = []
    text = re.sub(r'[ \t]+', ' ', ' '.join(texts))
    for m in re.finditer(r'\*([^*\n\u0001]{3,90})\*\s*((?:\u0001[^\u0001*]*)+)', text):
        g = dict(id=len(groups) + 1, name=m.group(1).strip(), items=[])
        groups.append(g)
        for pos, label in enumerate(x.strip(' ·\n') for x in m.group(2).split('\u0001')[1:]):
            label = re.sub(r'\s+', ' ', label).strip()
            if not label:
                continue
            aid = None
            # 'Ausdruck I-II', 'Kanon 1–4', 'Mass I 1–5', 'Schuld II 3; IV': the article without the part
            for cand in (label, re.sub(r'(?:\s+(?:[IVX]+(?:\s?[-–]\s?[IVX]+)?|[A-Z]|\d+(?:\s?[.–-]\s?\d+)*|[a-z]))+\s*(?:\(.*\))?$', '', label.split(';')[0] if re.search(r'\s[IVX]+\b.*;', label) else label),
                         re.sub(r'\s+(?:[IVX]+|\d+)\b.*$', '', label), label.split(';')[0],
                         label.replace('ss', 'ß'), label.split(';')[0].replace('ss', 'ß'), label.replace('; ', ' und ')):   # the register writes ss for ß
                aid = resolver.find(cand) if cand else None
                if aid is not None:
                    break
            g['items'].append((aid, label, pos))
    return groups


def build_extras(src, arts, resolver):
    """extras.json of hwph2md.py: the lists of abbreviations and signs (PDF pp. 199–218) and the article
    list the PDF opens with (pp. 1–85), which is compared here with the articles found in the text"""
    path = os.path.join(src, 'extras.json')
    if not os.path.exists(path):
        log('extras.json не найден: списков сокращений и знаков не будет (перегоните PDF новым hwph2md.py)')
        return {}, [], None, []
    ex = json.load(open(path, encoding='utf-8'))
    abbrevs = [(si, sec['title'], i, it['a'], it['text'])
               for si, sec in enumerate(ex.get('abbreviations', [])) for i, it in enumerate(sec['items'])]
    symbols = ex.get('symbols', [])
    # the article list: find each entry among our articles (same volume, column within one of ours, or
    # the name); what stays unmatched on either side is reported
    rows_a = [(a['id'], a['lemma'], a['band'], a['col_from'], a['col_to']) for a in arts if a['kind'] == 'article']
    by_band = collections.defaultdict(list)
    for a in rows_a:
        by_band[a[2]].append(a)

    def squash_(t):
        return re.sub(r'[^a-z0-9]', '', fold(t))
    matched, rows = set(), []
    for i, e in enumerate(ex.get('article_index', [])):
        aid = None
        cands = [a for a in by_band.get(e['band'], []) if a[3] - 1 <= e['col'] <= a[4] + 1]
        key = squash_(e['lemma'])

        def common(a):
            k2 = squash_(a[1])
            n = 0
            while n < min(len(key), len(k2)) and key[n] == k2[n]:
                n += 1
            return n
        # the candidate whose name agrees longest (two articles may share a column: 'Abstraktionsgrade',
        # 'Abstraktionsklasse'); at least the first five letters
        best = max(cands, key=lambda a: (common(a), a[0] not in matched, -abs(a[3] - e['col'])), default=None)
        if best is not None and common(best) >= 5:
            aid = best[0]
        if aid is None:
            aid = resolver.find(e['lemma'])
        if aid is not None:
            matched.add(aid)
        rows.append((i, e['lemma'], e['zh'], e['band'], e['col'], e['page'], aid))
    missing = [r for r in rows if r[6] is None]
    not_listed = [a for a in rows_a if a[0] not in matched]
    log('список статей PDF: %d записей, не найдено среди статей %d, статей вне списка %d'
        % (len(rows), len(missing), len(not_listed)))
    stats = dict(abbreviations=sum(len(x['items']) for x in ex.get('abbreviations', [])), article_list=len(rows),
                 article_list_unmatched=len(missing), articles_not_in_list=len(not_listed))
    return stats, abbrevs, symbols, rows


# ---------------------------------------------------------------- the articles
def convert(src):
    t0 = time.time()
    SVG_DIR[0] = os.path.join(src, 'img') if os.path.isdir(os.path.join(src, 'img')) else None
    files = sorted(glob.glob(os.path.join(src, 'Bd*.md')))
    if not files:
        sys.exit('В папке нет файлов Bd*.md: ' + src)

    # pass 1: read everything
    raw, register_text, sgroup_text = [], [], []
    for f in files:
        for meta, body in read_volume(f):
            band = meta.get('band', '')
            if band == '13' and body.count('\u0001') * 1000 < len(body):
                # prose among the register pages (the foreword and introduction of vol. 13, whose running
                # heads say "13" instead of "13*"): front matter, not register — a register page has
                # some 30 references per 1000 characters
                band = meta['band'] = '13*'
                if meta['lemma'].endswith('(Fortsetzung)'):
                    meta['lemma'] = 'Vorbemerkung und Einführung [zu Band 13]'
            sg_head = re.search('\n\nRegister der Sachgruppen(?: ⟦\\d+⟧)?\n\n', body) if band == '13*' else None
            if sg_head:
                # after the introduction of vol. 13 come the subject-group register and the first
                # columns of the reference register (a priori … abyssus): they are registers, not prose
                intro, rest = body[:sg_head.start()], body[sg_head.end():]
                sg, _, refs = rest.partition('Register der Verweise')
                sgroup_text.append(COL_RE.sub(' ', sg))
                if refs:
                    refs = re.sub(r'^\s*[A-ZÄÖÜ]\s+', '', COL_RE.sub(' ', refs))     # the letter heading 'A'
                    register_text.append((meta['pdf_to'], refs))
                body = intro
            if band == '13':                       # register volume
                register_text.append((meta['pdf_from'], COL_RE.sub(' ', body)))   # column marks mean nothing in the register stream
                continue
            kind = 'front' if band.endswith('*') else 'article'
            lemma = greek_fix(repair_lemma(meta['lemma'], body))
            raw.append((lemma, band, kind, meta, body))
    raw.sort(key=lambda r: (r[3]['pdf_from']))
    log(f'прочитано статей: {len(raw)} ({time.time() - t0:.0f} с)')

    ids = [(i + 1, r[0]) for i, r in enumerate(raw) if r[2] == 'article']
    resolver = Resolver(ids)
    page_rows = [(r[3]['pdf_from'], r[3]['pdf_to'], i + 1) for i, r in enumerate(raw) if r[2] == 'article']

    def by_page(epub_page, text):
        """the article an epub arrow points into: the page anchor lies inside its PDF pages; where two
        articles share the page, the one the arrow names, else the one that starts there"""
        pg = epub_page + EPUB_PAGE_OFFSET
        cands = [(f, a) for f, t, a in page_rows if f <= pg <= t]
        if not cands:
            return None
        if len(cands) > 1 and text:
            named = resolver.find(text)
            if named in [a for _, a in cands]:
                return named
        return max(cands)[1]

    # pass 2: register (before the articles, so that authors missing in the text can be filled in)
    register_text.sort()
    full = ' '.join(t for _, t in register_text)
    cut = full.find('Register der Verfasser')
    lemma_names = [l for _, l in ids]
    reg = parse_register(full[:cut] if cut > 0 else full, lemma_names)
    if cut > 0:
        reg += parse_authors(full[cut + len('Register der Verfasser'):], lemma_names)
    n_start_fixed = fix_start_columns(raw, reg)
    rows = [(i + 1, r[1], r[3]['col_from'], r[3]['col_to']) for i, r in enumerate(raw) if r[2] == 'article']
    by_band = {}
    for aid, band, c1, c2 in rows:
        by_band.setdefault(band, []).append((c1, c2, aid))

    def by_location(band, col, prefer):
        n = int(re.match(r'\d+', col).group(0))
        cands = [aid for c1, c2, aid in by_band.get(band, []) if c1 <= n <= c2]
        if prefer in cands:
            return prefer
        return cands[-1] if cands else None   # shared column: the later article starts there

    register = []
    for term, target, qual, band, col, kind in reg:
        dst = resolver.find(target)
        if band and col:
            loc = by_location(band, col, dst)
            dst = loc or dst
        term = greek_fix(term)
        register.append(dict(id=len(register) + 1, term=term, term_fold=fold(term), target=target, qualifier=qual,
                             band=band, col=col, kind=kind, dst=dst))

    reg_authors = {}
    for r in register:
        if r['kind'] == 'author' and r['dst'] and r['term'] not in reg_authors.setdefault(r['dst'], []):
            reg_authors[r['dst']].append(r['term'])
    filled = 0

    # pass 3: articles
    xrefs = []
    mentions = []
    arts = []
    for i, (lemma, band, kind, meta, body) in enumerate(raw):
        aid = i + 1
        blocks, notes = split_article(body)
        note_runs = runs_of([n for n, _ in notes])
        # align calls with notes: notes come in numbered series, one per numbered section, and every
        # section restarts its calls at [1]. A [1] after any call of the current series moves to the
        # next series; a call whose number the current series lacks is looked up further on, then back.
        by_series = {}
        for idx, ((n, _), r) in enumerate(zip(notes, note_runs)):
            by_series.setdefault((r, n), idx)
        n_series = (note_runs[-1] + 1) if note_runs else 0
        state = {'cur': 0, 'max': 0}

        def ref_html(m):
            n = int(m.group(1))
            # «vgl. Anm. [1]» in the text points back at a note of the same series and opens none
            back_ref = re.search(r'Anm\.\s*$', m.string[max(0, m.start() - 12):m.start()])
            if n == 1 and state['max'] >= 1 and state['cur'] + 1 < n_series and not back_ref:
                state['cur'] += 1
                state['max'] = 0
            cur = state['cur']
            if (cur, n) in by_series:
                state['max'] = max(state['max'], n)
            else:
                later = [r for r in range(cur + 1, n_series) if (r, n) in by_series]
                earlier = [r for r in range(cur - 1, -1, -1) if (r, n) in by_series]
                if later:
                    cur = later[0]
                elif earlier:
                    cur = earlier[0]
                else:
                    return f'<sup class="fn fn-missing">{n}</sup>'
            return f'<sup class="fn" data-fn="{cur}-{n}">{n}</sup>'

        links = []

        def mark_xrefs(p):
            # a column mark must not stand between the arrow and its target
            p = re.sub('\u0001(\\{p\\d{7}\\})?\\s*(⟦\\d+⟧)\\s*', lambda m: m.group(2) + ' \u0001' + (m.group(1) or '') + ' ', p)
            p = re.sub('(⟦\\d+⟧)\\s*\u0001(\\s*\\(s\\.\\s?d\\.\\))', '\u0001\\2 \\1', p)

            def multi(m):
                # '→ ‹A, → B›': one reference per arrow, each with its own quoted target
                parts = re.split('\u0001(\\{p\\d{7}\\})?', m.group(2))
                out = '\u0001' + (m.group(1) or '') + ' ‹' + parts[0].strip() + '›'
                for k in range(1, len(parts), 2):
                    out += ' \u0001' + (parts[k] or '') + ' ‹' + parts[k + 1].strip() + '›'
                return out
            p = XREF_MULTI.sub(multi, p)

            def before(m):
                links.append((m.group(2), 'before', m.group(1)))
                return '%d' % (len(links) - 1)

            def sd(m):
                links.append((m.group(1), 'sd', m.group(2)))
                return '%d' % (len(links) - 1)

            def bare(m):
                links.append(('', 'bare', m.group(1)))
                return '%d' % (len(links) - 1)
            p = XREF_BEFORE.sub(before, p)
            p = XREF_SD.sub(sd, p)
            p = XREF_BARE.sub(bare, p)
            return p.replace('\u0001', '→')

        def link_html(m):
            raw_t, form, page = links[int(m.group(1))]
            t = raw_t.strip('‹›*')
            dst = None
            if kind == 'article':
                dst = by_page(int(page), t) if page else None
                dst = dst or (resolver.find(t) if t else None)
            if form == 'bare':
                xrefs.append((aid, t, dst))
                return f'<a class="xref" href="#/a/{dst}">→</a>' if dst and dst != aid else '→'
            xrefs.append((aid, t, dst))
            shown = inline(raw_t) if raw_t.startswith('*') else html.escape(raw_t)
            if form == 'before':
                inner = '→ ' + shown
                return f'<a class="xref" href="#/a/{dst}">{inner}</a>' if dst and dst != aid else f'<span class="xref-dead">{inner}</span>'
            inner = shown
            tail = ' <span class="sd">→ (s.d.)</span>'
            return (f'<a class="xref" href="#/a/{dst}">{inner}</a>' if dst and dst != aid else inner) + tail

        parts, toc, body_plain, lit_plain, fig_words, flow_seq = [], [], [], [], [], []
        for k, (kind_, p) in enumerate(blocks):
            if kind_ == 'h':
                parts.append(f'<h3 id="h{k}">{html.escape(p)}</h3>')
                toc.append([f'h{k}', p, 0])
                continue
            if p.startswith('<!-- OCR:'):
                parts.append('<div class="ocr" data-i18n="art.ocr"></div>')   # the words come from i18n.js
                continue
            if p.startswith('<!--'):
                parts.append('<div class="gap">' + html.escape(p.strip('<!- >')) + '</div>')
                continue
            if p.startswith('$$') and p.endswith('$$'):
                tex = p[2:-2].strip()
                parts.append('<div class="md" data-tex="%s">%s</div>' % (html.escape(tex), html.escape(tex)))
                continue
            if PIC_RE.fullmatch(p.strip()):
                hh = PIC_RE.match(p.strip()).group(1)
                parts.append(pic_figure(hh))
                words = svg_words(hh)
                if words:
                    fig_words.append(words)           # the words of a diagram can be searched for
                continue
            if p.startswith('|') and '\n|' in p:
                parts.append(md_table(p))
                continue
            h = inline(mark_xrefs(p))
            h = REF_RE.sub(ref_html, h)
            h = re.sub('(\\d+)', link_html, h)
            cls = ' class="lit"' if kind_ == 'lit' else ''
            m = SEC_RE.match(p) if kind_ == 'p' else None
            if m and re.match(r'(?:[A-ZÄÖÜ]\.\s?)*[A-ZÄÖÜ]{2,}[\s:,]', p[m.end():]):
                m = None                         # 'A. H. ARMSTRONG: …' is a bibliography entry
            if m:
                label = m.group(1)
                lvl = 1 if re.match(r'[IVX]+\.', label) else (2 if re.match(r'[A-H]\.', label) else 3)
                words = plain(p[m.end():])[:70]
                toc.append([f'p{k}', label + ' ' + words, lvl])
                parts.append(f'<p id="p{k}"{cls}>{h}</p>')
            else:
                parts.append(f'<p{cls}>{h}</p>')
            flow_seq.append((kind_ == 'lit', plain_cols(p)))
        if notes:
            # a call lost from the text layer: a section's lone note [1] has no call, and the next
            # section's [1] was taken for it (its [2] then found the next series). Give that [1] to the
            # next series, where its [2], [3] … are; the lone note stays without a call.
            seq = [tuple(map(int, x.split('-'))) for x in re.findall(r'data-fn="(\d+-\d+)"', ''.join(parts))]
            have = set(seq)
            size = {}
            for (n, _), r in zip(notes, note_runs):
                size[r] = size.get(r, 0) + 1
            moved = {(r, 1) for (r, n), nx in zip(seq, seq[1:] + [None])
                     if n == 1 and size.get(r) == 1 and nx == (r + 1, 2) and (r + 1, 1) not in have}
            if moved:
                def move(m):
                    r, n = int(m.group(1)), int(m.group(2))
                    return f'data-fn="{r + 1}-1"' if (r, n) in moved else m.group(0)
                parts = [re.sub(r'data-fn="(\d+)-(\d+)"', move, x) for x in parts]
            parts.append('<h3 id="notes">Anmerkungen</h3><ol class="notes">')
            for (n, t), r in zip(notes, note_runs):
                nt = re.sub('(\\d+)', link_html, inline(mark_xrefs(t)))
                parts.append(f'<li id="fn{r}-{n}" value="{n}">{nt}</li>')
            parts.append('</ol>')
            toc.append(['notes', 'Anmerkungen', 0])
        # text and literature are one flow in the book: every paragraph starts with the column the flow
        # has reached, whichever of the two plain texts it lands in; the notes are a flow of their own
        running = meta['col_from']
        for is_lit, (t_, ms_) in flow_seq:
            (lit_plain if is_lit else body_plain).append((t_, [(0, running)] + ms_))
            running = ms_[-1][1] if ms_ else running
        running, note_pieces = meta['col_from'], []
        for _, t in notes:
            t_, ms_ = plain_cols(t)
            note_pieces.append((t_, [(0, running)] + ms_))
            running = ms_[-1][1] if ms_ else running
        notes_plain, cm_n = join_cols(note_pieces)
        bp, cm_b = join_cols(body_plain)
        lp, cm_l = join_cols(lit_plain)
        authors = meta.get('autoren', [])
        if not authors and kind == 'article' and reg_authors.get(aid):
            authors = reg_authors[aid]
            filled += 1
        # de-duplicate while keeping order (multi-part articles repeat names)
        seen, auth = set(), []
        for a in authors:
            if a not in seen:
                seen.add(a)
                auth.append(a)
        arts.append(dict(id=aid, lemma=lemma, lemma_fold=fold(lemma), band=band, kind=kind,
                         col_from=meta['col_from'], col_to=meta['col_to'], pdf_from=meta['pdf_from'],
                         pdf_to=meta['pdf_to'], authors=auth, n_notes=len(notes),
                         n_chars=len(bp) + len(lp) + len(notes_plain), toc=toc, html='\n'.join(parts),
                         plain_b=' \n'.join([bp] + fig_words), plain_n=notes_plain, plain_l=lp,
                         colmap=(json.dumps(cm_b), json.dumps(cm_n), json.dumps(cm_l))))
        if kind == 'article':
            for ctx, txt in (('b', bp), ('n', notes_plain), ('l', lp)):
                for rname, pos in hwph_cite.raw_mentions(txt, lemma):
                    ed = bool(ED_BEFORE.search(txt[max(0, pos - 24):pos]))
                    mentions.append((aid, ctx, rname, ed, pos))
        if aid % 500 == 0:
            log(f'… {aid}/{len(raw)} {lemma}')
    persons, cites = build_persons(arts, mentions)
    concept_mentions = build_mentions(arts)
    sgroups = build_sgroups(sgroup_text, resolver)
    extras, abbrevs, symbols, article_list = build_extras(src, arts, resolver)

    n_items = sum(len(g['items']) for g in sgroups)
    stats = dict(articles=len(ids), front=len(raw) - len(ids), xrefs=len(xrefs), xrefs_resolved=sum(1 for r in xrefs if r[2]),
                 register=len(register), register_resolved=sum(1 for r in register if r['dst']), authors_filled=filled,
                 persons=len(persons), concept_mentions=len(concept_mentions),
                 **extras, start_columns_fixed=n_start_fixed, subject_groups=len(sgroups), group_items=n_items,
                 group_items_resolved=sum(1 for g in sgroups for it in g['items'] if it[0] is not None),
                 built=time.strftime('%Y-%m-%d %H:%M'))
    return dict(arts=arts, xrefs=xrefs, register=register, persons=persons, cites=cites,
                mentions=concept_mentions, sgroups=sgroups, abbrevs=abbrevs, symbols=symbols,
                article_list=article_list, stats=stats, t_parse=time.time() - t0)


# ---------------------------------------------------------------- XML
BAD_XML = re.compile('[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]')
BAD = []


def clean(s, where):
    if BAD_XML.search(s):
        BAD.append(where)
        s = BAD_XML.sub('�', s)
    return s


def esc(s, where=''):
    return html.escape(clean(s, where), quote=False)


def attrs(pairs, where=''):
    out = []
    for k, v in pairs:
        if v is None:
            continue
        v = repr(v) if isinstance(v, float) else str(v)
        out.append(' %s="%s"' % (k, html.escape(clean(v, where), quote=True).replace('&#x27;', "'")))
    return ''.join(out)


def tree(v):
    """an ordered JSON value as XML: <o><m k="key">…</m></o>, <a>, <s>, <n>, <null/>, <true/>, <false/>"""
    if isinstance(v, dict):
        return '<o>%s</o>' % ''.join('<m%s%s>%s</m>' % (attrs([('k', k)]), ' num="1"' if isinstance(k, int) else '', tree(x))
                                     for k, x in v.items())
    if isinstance(v, list):
        return '<a>%s</a>' % ''.join(tree(x) for x in v)
    if v is None:
        return '<null/>'
    if v is True:
        return '<true/>'
    if v is False:
        return '<false/>'
    if isinstance(v, (int, float)):
        return '<n>%s</n>' % repr(v)
    return '<s>%s</s>' % esc(v)


def write_xml(d, out):
    from xml.etree import ElementTree as ET
    chars = set()
    with open(out, 'w', encoding='utf-8') as f:
        w = f.write
        w('<?xml version="1.0" encoding="UTF-8"?>\n<hwph engine="index">\n')
        # structured values (statistics, the list of signs), kept with their key order
        w('<json name="stats">%s</json>\n' % tree(d['stats']))
        if d['symbols'] is not None:
            w('<json name="symbols">%s</json>\n' % tree(d['symbols']))
        w('<articles>\n')
        for a in d['arts']:
            aid = a['id']
            w('<article%s>\n' % attrs([('id', aid), ('lemma', a['lemma']), ('lemma-fold', a['lemma_fold']), ('band', a['band']),
                                        ('kind', a['kind']), ('col-from', a['col_from']), ('col-to', a['col_to']),
                                        ('pdf-from', a['pdf_from']), ('pdf-to', a['pdf_to']), ('n-notes', a['n_notes']),
                                        ('n-chars', a['n_chars'])], aid))
            w('<authors>%s</authors>\n' % ''.join('<author>%s</author>' % esc(x, aid) for x in a['authors']))
            w('<toc>%s</toc>\n' % ''.join('<entry%s/>' % attrs([('id', e[0]), ('label', e[1]), ('level', e[2])], aid) for e in a['toc']))
            body = '<html>' + clean(a['html'], aid) + '</html>'
            try:
                ET.fromstring(body)
            except ET.ParseError as e:
                sys.exit('статья %d (%s): HTML не является корректным XML: %s' % (aid, a['lemma'], e))
            w(body + '\n')
            for part in 'bnl':
                text = a['plain_' + part]
                chars.update(text)
                w('<plain part="%s">%s</plain>\n' % (part, esc(text, aid)))
            chars.update(a['lemma'])
            chars.update(' '.join(a['authors']))
            w('<colmap%s/>\n' % attrs(zip('bnl', a['colmap'])))
            w('</article>\n')
        w('</articles>\n')

        def table(name, item, rows, cols):
            w('<%s>\n' % name)
            for r in rows:
                w('<%s%s/>\n' % (item, attrs(zip(cols, r))))
            w('</%s>\n' % name)
        table('xrefs', 'x', d['xrefs'], ['src', 'target', 'dst'])
        table('register', 'r', [(r['id'], r['term'], r['term_fold'], r['target'], r['qualifier'], r['band'], r['col'], r['kind'], r['dst'])
                                for r in d['register']],
              ['id', 'term', 'term-fold', 'target', 'qualifier', 'band', 'col', 'kind', 'dst'])
        w('<persons>\n')
        for p in d['persons']:
            w('<p%s/>\n' % attrs([('id', p['id']), ('key', p['key']), ('name', p['name']), ('name-fold', p['name_fold']),
                                   ('n-articles', p['n_articles']), ('n-body', p['n_body']), ('n-notes', p['n_notes']),
                                   ('n-lit', p['n_lit']), ('n-ed', p['n_ed']), ('editor', p['editor']),
                                   ('variants', json.dumps(p['variants'], ensure_ascii=False)), ('role', p['role']),
                                   ('pattern', person_pattern(p))]))
        w('</persons>\n')
        table('cites', 'c', d['cites'], ['aid', 'pid', 'n-body', 'n-notes', 'n-lit'])
        table('mentions', 'm', d['mentions'], ['aid', 'dst', 'tf', 'score'])
        w('<sgroups>\n')
        for g in d['sgroups']:
            w('<group%s>' % attrs([('id', g['id']), ('name', g['name'])]))
            for aid, label, pos in g['items']:
                w('<item%s/>' % attrs([('aid', aid), ('label', label), ('pos', pos)]))
            w('</group>\n')
        w('</sgroups>\n')
        table('abbrevs', 'abbrev', d['abbrevs'], ['sec', 'title', 'pos', 'abbr', 'text'])
        table('article-list', 'e', d['article_list'], ['pos', 'lemma', 'zh', 'band', 'col', 'page', 'aid'])

        # folding table: the search form of every character of the indexed text, as Python computes it
        # (Unicode data of XQuery engines differs in details; the table keeps both sides identical)
        w('<fold>\n')
        for c in sorted(chars):
            fc = fold_char(c)
            if fc != c and not BAD_XML.search(c):
                w('<f%s/>\n' % attrs([('c', c), ('to', fc)]))
        w('</fold>\n')
        # characters of the folded text that do not belong to a word (Python's \w decides), so that
        # the XQuery side splits words exactly as the parser's regular expression does
        folded = set()
        for c in chars:
            folded.update(fold_char(c))
        nonword = ''.join(sorted(c for c in folded if not re.match(r'\w', c) and not BAD_XML.search(c)))
        w('<nonword>%s</nonword>\n' % esc(nonword))
        # characters of the text itself that end a word: their search form is not part of a word. The
        # words of the text, folded one by one, are then exactly the words of the folded text (a mark
        # folded away, U+0364 or ´, does not split what it stands in)
        rawsep = ''.join(sorted(c for c in chars if fold_char(c) and not BAD_XML.search(c)
                                and any(not re.match(r'\w', x) for x in fold_char(c))))
        mixed = [c for c in chars if fold_char(c) and any(re.match(r'\w', x) for x in fold_char(c))
                 and any(not re.match(r'\w', x) for x in fold_char(c))]
        if mixed:
            log('знаки, свёртка которых даёт и букву, и не букву (слова в позиционном указателе могут сдвинуться):', mixed)
        w('<rawsep>%s</rawsep>\n' % esc(rawsep))
        w('</hwph>\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', help='папка с Bd01.md … Bd13.md')
    ap.add_argument('-o', '--out', default='hwph-data.xml')
    a = ap.parse_args()
    t0 = time.time()
    d = convert(os.path.abspath(a.src))
    t1 = time.time()
    write_xml(d, a.out)
    if BAD:
        log('недопустимые в XML управляющие знаки заменены на U+FFFD:', len(BAD), 'мест, статьи', sorted(set(map(str, BAD)))[:20])
    log(json.dumps(d['stats'], ensure_ascii=False))
    log('готово: %s (%.0f МБ; разбор %.0f с, запись %.0f с)' % (a.out, os.path.getsize(a.out) / 1e6, t1 - t0, time.time() - t1))


if __name__ == '__main__':
    main()
