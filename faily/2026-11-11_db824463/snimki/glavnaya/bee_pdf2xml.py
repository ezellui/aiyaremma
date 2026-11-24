#!/usr/bin/env python3
"""
bee_pdf2xml.py — printouts of Wittgenstein's Nachlass, The Bergen Electronic Edition (Folio Bound VIEWS 3.1a
under Wine, printed with "Hidden Text" on to CUPS-PDF) -> one XML file per Nachlass item.

  python3 bee_pdf2xml.py --fonts DIR --symbol symbol.ttf --out OUT  c0001.pdf c0002.pdf ...

The PDFs are taken as one continuous stream, in the order given (chunks of one printing run).

What the printout carries and how it is read (normalized transcription):
  * TrueType subsets keep the glyph indices of the original fonts: glyph id -> glyph name of the
    CD font (PLANOUP.TTF …) -> Unicode. No ToUnicode is needed.
  * Type 3 fonts are bitmap glyphs made by the Wine printer driver. Their codes are mostly the
    character codes; glyphs that need a decision are listed in glyphs3.json (md5 of the CharProc).
  * colour: #0000a1 text, #00003b last of undecided alternatives, #f83633 editorial (BEE legend);
    black Arial is the running head of the printout.
  * hidden fields (printed small, red Arial 7pt): "<item> <page>" at the left margin opens a record
    (in the Nachlass a remark), a date closes it; red Arial 10.8 after a name is the person index,
    red monospace before notation is the notation descriptor.
  * "Item N Page P  N\\NNN.jpg" (red Arial bold 10.8) is a page of the original, with its facsimile.
  * undecided alternatives: red "[" alt … red "|" alt red "]".
"""
import argparse, collections, hashlib, io, json, os, re, sys, unicodedata
import xml.etree.ElementTree as ET
import pymupdf
from fontTools.ttLib import TTFont
from fontTools.agl import toUnicode

# ---------------------------------------------------------------- fonts
ORIG = {
    'PlantinOUP': 'PLANOUP.TTF', 'PlantinOUP-Bold': 'PLANBOUP.TTF', 'PlantinOUP-Italic': 'PLANIOUP.TTF',
    'PlantinOUP-BoldItalic': 'PLANZOUP.TTF', 'ArialOUP': 'ARIOUP.TTF', 'ArialOUP-Bold': 'ARIBOUP.TTF',
    'ArialOUP-Italic': 'ARITOUP.TTF', 'ArialOUP-BoldItalic': 'ARIBIOUP.TTF',
    'Waboup1': 'WABOUP.TTF', 'Wablast1': 'WABLAST.TTF', 'Wabmath1': 'WABMATH.TTF',
}
# private glyphs of the OUP/WAB fonts (identified on a contact sheet)
PRIVATE = {'p119': 'ƿ', 'p87': 'Ƿ', 'p89': 'Ȝ', 'p121': 'ȝ', 'p84': 'Þ', 'p116': 'þ', 'p98': 'ꝥ',
           'p71': 'Ƌ', 'p103': 'ƌ', 'p112': '⸮'}
C_TEXT, C_ALT, C_RED, C_BLACK = '0000a1', '00003b', 'f83633', '000000'


def color_hex(c):
    if not c:
        return '000000'
    if len(c) == 1:
        c = (c[0],) * 3
    return '%02x%02x%02x' % tuple(int(round(v * 255)) for v in c[:3])


class Fonts:
    def __init__(self, fontdir, symbol, glyphs3):
        self.order = {}
        for base, fn in ORIG.items():
            p = os.path.join(fontdir, fn)
            if os.path.exists(p):
                self.order[base] = TTFont(p).getGlyphOrder()
        if symbol and os.path.exists(symbol):
            self.order['Symbol'] = TTFont(symbol).getGlyphOrder()
        self.g3 = glyphs3            # md5 -> char
        self.unknown = collections.Counter()
        self.t3cache = {}            # (doc id, xref) -> {code: md5}

    def t3_hashes(self, doc, xref):
        key = (id(doc), xref)
        if key not in self.t3cache:
            m = {}
            try:
                enc = doc.xref_get_key(xref, 'Encoding/Differences')
                procs = doc.xref_get_key(xref, 'CharProcs')
                names = re.findall(r'(\d+)|/(\S+?)(?=[\s/\]])', enc[1].strip('[]') + ' ')
                code = 0; byname = {}
                for num, nm in names:
                    if num:
                        code = int(num)
                    else:
                        byname[nm] = code; code += 1
                for nm, ref in re.findall(r'/(\S+?)\s+(\d+)\s+0\s+R', procs[1]):
                    if nm in byname:
                        m[byname[nm]] = hashlib.md5(doc.xref_stream(int(ref))).hexdigest()
            except Exception:
                pass
            self.t3cache[key] = m
        return self.t3cache[key]

    def char(self, doc, font, ucs, gid):
        """-> (text, family) ; family: 'mono' for the Type 3 / Courier notation font"""
        if font.startswith('Type3'):
            m = re.search(r'\((\d+) 0 R\)', font)
            h = self.t3_hashes(doc, int(m.group(1))).get(gid) if m else None
            if h and h in self.g3:
                return self.g3[h], 'mono'
            if 32 <= gid < 127:
                return chr(gid), 'mono'
            self.unknown[(h, gid)] += 1
            return '�', 'text'
        base = font.split('+')[-1]
        order = self.order.get(base)
        if order is None:
            fam = 'mono' if base.startswith('Courier') else 'text'
            return (chr(ucs) if ucs else '�'), fam
        name = order[gid] if gid < len(order) else ''
        u = PRIVATE.get(name) or toUnicode(name) or ''
        if not u:
            self.unknown[(base, name)] += 1
            u = '�'
        return u, 'text'


# ---------------------------------------------------------------- page analysis
class Ch:
    __slots__ = ('t', 'x0', 'x1', 'y', 'top', 'size', 'font', 'col', 'bold', 'ital', 'mono', 'ul', 'st', 'sup')


def page_chars(doc, page, fonts):
    out = []
    for s in page.get_texttrace():
        if s['type'] == 3 or s.get('opacity', 1) == 0:     # invisible text
            continue
        font = s['font']; col = color_hex(s['color'])
        base = font.split('+')[-1]
        bold = 'Bold' in base; ital = 'Italic' in base
        for ucs, gid, origin, bbox in s['chars']:
            t, fam = fonts.char(doc, font, ucs, gid)
            c = Ch()
            c.t = t; c.x0, c.x1 = bbox[0], bbox[2]; c.y = origin[1]
            if fam == 'mono' and s['size'] < 2:              # Type 3: size is a unit scale; use the advance
                c.size = max(6.0, (bbox[2] - bbox[0]) / 0.6)
            else:
                c.size = s['size']
            c.top = c.y - c.size * 0.75
            c.font = 'Type3' if font.startswith('Type3') else base
            c.col = col; c.bold = bold; c.ital = ital; c.mono = fam == 'mono'
            c.ul = c.st = c.sup = False
            out.append(c)
    return out


def rules(page):
    """thin horizontal strokes/rects that are not white: underlines, strike-throughs, header rules"""
    segs = []
    for d in page.get_drawings():
        col = d.get('fill') or d.get('color')
        if col and all(v > 0.95 for v in col[:3]):
            continue
        for it in d['items']:
            if it[0] == 're':
                r = it[1]
                if r.height < 1.2 and r.width > 1.5:
                    segs.append((r.x0, r.x1, (r.y0 + r.y1) / 2))
            elif it[0] == 'l':
                p, q = it[1], it[2]
                if abs(p.y - q.y) < 0.5 and abs(p.x - q.x) > 1.5:
                    segs.append((min(p.x, q.x), max(p.x, q.x), p.y))
    return segs


def mark_rules(chars, segs):
    for c in chars:
        mx = (c.x0 + c.x1) / 2
        for x0, x1, y in segs:
            if x0 - 0.3 <= mx <= x1 + 0.3:
                d = y - c.y
                if -0.5 <= d <= 3.0:
                    c.ul = True
                elif -0.65 * c.size <= d <= -0.15 * c.size:
                    c.st = True


def lines_of(chars):
    chars = sorted(chars, key=lambda c: (c.y, c.x0))
    lines = []
    for c in chars:
        if lines and abs(c.y - lines[-1]['y']) <= 0.4 * max(c.size, 10):
            lines[-1]['ch'].append(c)
        else:
            lines.append({'y': c.y, 'ch': [c]})
    for l in lines:
        l['ch'].sort(key=lambda c: c.x0)
        sizes = sorted(c.size for c in l['ch'] if not c.mono)
        base = collections.Counter(round(c.y, 1) for c in l['ch']).most_common(1)[0][0]
        l['y'] = base
        for c in l['ch']:
            if c.y < base - 2.0 and c.size < max(sizes or [c.size]) - 1:
                c.sup = True
        l['x0'] = l['ch'][0].x0; l['x1'] = l['ch'][-1].x1
    return lines


def images_of(page, outdir, gmap):
    res = []
    for info in page.get_image_info(xrefs=True):
        w, h = info['width'], info['height']
        if (w, h) == (18, 16):                     # the D / I / P buttons
            continue
        bb = pymupdf.Rect(info['bbox'])
        if bb.width < 2 or bb.height < 2:
            continue
        key = hashlib.md5(page.parent.extract_image(info['xref'])['image']).hexdigest() if info['xref'] else \
            hashlib.md5(repr((w, h, info.get('digest'))).encode()).hexdigest()
        fn = key[:16] + '.png'
        p = os.path.join(outdir, 'img', fn)
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            zoom = max(1.0, w / bb.width)
            page.get_pixmap(clip=bb, matrix=pymupdf.Matrix(zoom, zoom)).save(p)
        res.append({'y': bb.y1 - 2, 'x0': bb.x0, 'img': fn, 'key': key, 'w': w, 'h': h,
                    'map': gmap.get(key)})
    return res


# ---------------------------------------------------------------- stream -> events
def style(c):
    return (c.col, c.bold, c.ital, c.mono, c.ul, c.st, c.sup, c.font.startswith('Arial'), round(c.size))


def runs(line):
    out = []
    prev = None
    for c in line['ch']:
        t = c.t
        if prev is not None:
            gap = c.x0 - prev.x1
            if gap > 0.22 * min(c.size, prev.size) and not t.isspace() and not out[-1][1].endswith(' '):
                t = ' ' + t
        k = style(c)
        if out and out[-1][0] == k and not (t.startswith(' ') and k[7]):
            out[-1][1] += t; out[-1][2] = c.x1
        else:
            out.append([k, t, c.x1, c.x0])
        prev = c
    return out


PAGE_RE = re.compile(r'Item\s+(\S+)\s+Page\s+(.+?)(?:\s+(\S+\\\S+\.\w+))?\s*$')
REC_RE = re.compile(r'^\s*(\d{3}[a-z0-9]*)\s+(.+?)\s*$')
HEAD_RE = re.compile(r'^Item\s+(\d{3}\S*)\s+(.*)$')


def events(pdfs, fonts, outdir, gmap, log):
    """yield ('item', n, title) ('page', item, page, facs) ('rec', item, page) ('date', s)
       ('line', x0, x1, y, runs, size) ('img', dict) ('gap',)"""
    textleft = None
    for path in pdfs:
        doc = pymupdf.open(path)
        log['pdfs'] += 1
        for page in doc:
            log['pages'] += 1
            chars = page_chars(doc, page, fonts)
            # running head: black Arial (title, copyright, "Page: N Query:")
            chars = [c for c in chars if not (c.col == C_BLACK and c.font.startswith('Arial'))]
            mark_rules(chars, rules(page))
            items = [('l', l) for l in lines_of(chars)] + [('i', im) for im in images_of(page, outdir, gmap)]
            items.sort(key=lambda t: t[1]['y'])
            body_x = [l['x0'] for k, l in items if k == 'l' and l['ch'][0].col in (C_TEXT, C_ALT)
                      and not l['ch'][0].font.startswith('Arial')]
            if body_x:
                xs = collections.Counter(round(x) for x in body_x).most_common(1)[0][0]
                textleft = xs if textleft is None else min(textleft, xs) if abs(xs - textleft) < 40 else xs
            yield ('newpage',)
            for k, obj in items:
                if k == 'i':
                    yield ('img', obj); continue
                rs = runs(obj)
                rest = []
                for st, t, x1, x0 in rs:
                    col, bold, ital, mono, ul, stk, sup, arial, size = st
                    s = t.strip()
                    if not s:
                        rest.append((st, t, x0)); continue
                    if col == C_RED and arial and size >= 10 and bold and PAGE_RE.search(s):
                        m = PAGE_RE.search(s)
                        yield ('page', m.group(1), m.group(2).strip(), m.group(3)); continue
                    if col == C_RED and arial and size <= 8:
                        m = REC_RE.match(s)
                        if m and textleft and x0 < textleft - 15:
                            yield ('rec', m.group(1), m.group(2)); continue
                        yield ('date', s); continue
                    if col == C_TEXT and arial and size >= 13:
                        m = HEAD_RE.match(s)
                        if m:
                            yield ('item', m.group(1), m.group(2).strip()); continue
                    rest.append((st, t, x0))
                if any(t.strip() for _, t, _ in rest):
                    x0 = next(x for st, t, x in rest if t.strip())
                    yield ('line', x0, obj['x1'], obj['y'], rest, max(c.size for c in obj['ch']), textleft)


# ---------------------------------------------------------------- events -> XML
NOSPACE_AFTER_HYPHEN = re.compile(r'^[A-ZÄÖÜ]')
SPACE_AFTER_HYPHEN = re.compile(r'^(und|oder|bzw|sowie|u\.|wie|als|noch|statt|bis|zu|or|and)\b')


class Builder:
    """inline stream -> element tree, with alternatives, persons and notation"""
    def __init__(self, parent):
        self.root = parent
        self.stack = [parent]
        self.app = None          # current <app> while inside red [ … ]
        self.pending_notation = None

    def cur(self):
        return self.stack[-1]

    def text(self, s, attrs=None):
        el = self.cur()
        if attrs:
            el = ET.SubElement(el, attrs[0], attrs[1]) if attrs[0] else el
            el.text = (el.text or '') + s
            return
        if len(el):
            el[-1].tail = (el[-1].tail or '') + s
        else:
            el.text = (el.text or '') + s

    def wrap(self, s, st):
        col, bold, ital, mono, ul, stk, sup, arial, size = st
        el_parent = self.cur()
        chain = []
        if col == C_RED and not mono:
            chain.append(('ed', {}))
        if col == C_ALT and self.app is None:
            chain.append(('hi', {'rend': 'alt'}))
        if bold:
            chain.append(('hi', {'rend': 'b'}))
        if ital:
            chain.append(('hi', {'rend': 'i'}))
        if ul:
            chain.append(('hi', {'rend': 'u'}))
        if stk:
            chain.append(('del', {}))
        if sup:
            chain.append(('hi', {'rend': 'sup'}))
        if not chain:
            self.text(s); return
        # merge with the previous sibling when it has the same chain
        el = el_parent
        for i, (tag, a) in enumerate(chain):
            last = el[-1] if len(el) and not (el[-1].tail or '').strip() and el[-1].tag == tag and el[-1].attrib == a else None
            if last is not None and (last.tail or '') == '':
                el = last
                # descend to the deepest last child of the same chain
                continue
            el = ET.SubElement(el, tag, a)
        if len(el):
            el[-1].tail = (el[-1].tail or '') + s
        else:
            el.text = (el.text or '') + s

    def put(self, st, t):
        col, bold, ital, mono, ul, stk, sup, arial, size = st
        s = t
        core = s.strip()
        # person index (hidden field): red Arial ~10.8 after the name
        if col == C_RED and arial and 9 <= size <= 12 and core:
            ET.SubElement(self.cur(), 'person', {'key': core}).tail = ' ' if s.endswith(' ') else ''
            return
        # notation: red monospace = descriptor, other monospace = the notation itself
        if mono:
            if col == C_RED:
                self.pending_notation = ((self.pending_notation + ' ') if self.pending_notation else '') + core
                return
            el = self.cur()
            last = el[-1] if len(el) else None
            if last is not None and last.tag == 'formula' and not (last.tail or '').strip() and self.pending_notation is None:
                last.text += (last.tail or '') + s; last.tail = ''
            else:
                if s.startswith(' '):
                    self.text(' '); s = s[1:]
                a = {'notation': self.pending_notation} if self.pending_notation else {}
                f = ET.SubElement(el, 'formula', a); f.text = s.rstrip()
                f.tail = ' ' if s.endswith(' ') else ''
                self.pending_notation = None
            return
        # undecided alternatives
        if col == C_RED and not arial:
            i = 0
            while i < len(s):
                ch = s[i]
                if ch == '[' and self.app is None:
                    self.app = ET.SubElement(self.cur(), 'app'); r = ET.SubElement(self.app, 'rdg')
                    self.stack.append(r); i += 1; continue
                if ch == '|' and self.app is not None:
                    self.stack.pop(); r = ET.SubElement(self.app, 'rdg'); self.stack.append(r); i += 1; continue
                if ch == ']' and self.app is not None:
                    self.stack.pop()
                    rdgs = self.app.findall('rdg')
                    if len(rdgs) >= 2:
                        rdgs[-1].tag = 'lem'
                    else:                                  # a plain editorial bracket after all
                        r = rdgs[0]; self.app.tag = 'ed'; self.app.remove(r)
                        self.app.text = '[' + (r.text or ''); [self.app.append(x) for x in list(r)]
                        self.text(']')
                    self.app = None; i += 1; continue
                j = i
                while j < len(s) and s[j] not in '[|]':
                    j += 1
                self.wrap(s[i:j], st); i = j
            return
        self.wrap(s, st)


def tidy(el):
    """collapse whitespace and strip <p> edges; drop empty inline elements"""
    for e in el.iter():
        if e.text:
            e.text = re.sub(r'[ \t\n]+', ' ', e.text)
        if e.tail:
            e.tail = re.sub(r'[ \t\n]+', ' ', e.tail)
    for p in el.iter('p'):
        if p.text:
            p.text = p.text.lstrip()
        last = p[-1] if len(p) else None
        if last is not None and last.tail:
            last.tail = last.tail.rstrip()
        elif last is None and p.text:
            p.text = p.text.rstrip()


def join_text(prev_tail, nxt):
    """separator between two wrapped lines"""
    if prev_tail.endswith('-') and not prev_tail.endswith(' -'):
        if SPACE_AFTER_HYPHEN.match(nxt):
            return ' '
        return ''
    return ' '


def convert(pdfs, fonts, outdir, gmap):
    log = collections.Counter()
    items = {}
    order = []
    item = rec = p = b = None
    last_line = None
    cur_page = None
    cur_item_n = None

    def new_item(n, title=''):
        nonlocal item, rec, p, b, last_line
        if n in items:
            item = items[n]
        else:
            item = ET.Element('item', {'n': n})
            if title:
                item.set('title', title)
            items[n] = item; order.append(n)
        rec = p = b = None; last_line = None

    def new_rec(n, page):
        nonlocal rec, p, b, last_line
        if item is None or item.get('n') != n:
            new_item(n)
        rec = ET.SubElement(item, 'rec', {'page': page}); p = b = None; last_line = None
        log['records'] += 1

    def new_p(rend=None):
        nonlocal p, b
        if rec is None:
            new_rec(cur_item_n or 'front', cur_page or '')
        p = ET.SubElement(rec, 'p', {'rend': rend} if rend else {}); b = Builder(p)

    for ev in events(pdfs, fonts, outdir, gmap, log):
        kind = ev[0]
        if kind == 'newpage':
            continue
        if kind == 'item':
            cur_item_n = ev[1]; new_item(ev[1], ev[2]); log['items'] += 1; continue
        if kind == 'page':
            n, pg, facs = ev[1], ev[2], ev[3]
            cur_page = pg
            if item is None or item.get('n') != n:
                new_item(n)
            target = rec if rec is not None else item
            a = {'n': pg}
            if facs:
                a['facs'] = facs.replace('\\', '/')
            if p is not None:
                ET.SubElement(b.cur(), 'pb', a).tail = ''
            else:
                ET.SubElement(target, 'pb', a)
            log['pb'] += 1; continue
        if kind == 'rec':
            cur_item_n = ev[1]; new_rec(ev[1], ev[2]); continue
        if kind == 'date':
            if rec is not None:
                d = rec.get('date', '')
                rec.set('date', (d + ' ' + ev[1]).strip())
            continue
        if kind == 'img':
            im = ev[1]
            if p is None:
                new_p()
            m = im['map']
            if m and m.get('kind') == 'sym':
                b.text(m['value'])
            elif m and m.get('kind') in ('tex', 'texd'):
                f = ET.SubElement(b.cur(), 'formula', {'tex': m['value']}); f.tail = ''
            else:
                f = ET.SubElement(b.cur(), 'figure', {'src': 'img/' + im['img'], 'w': str(im['w']), 'h': str(im['h'])}); f.tail = ''
            log['img'] += 1; continue
        if kind == 'line':
            x0, x1, y, rs, size, tl = ev[1:]
            tl = tl or x0
            label = None
            if rs and rs[0][2] < tl - 10 and len(rs) > 1:      # remark number in the margin: "43)", "6·53"
                label = rs[0][1].strip(); rs = rs[1:]
            indent = x0 > tl + 6
            right = x0 > tl + 200 and x1 - x0 < 120
            gap = (y - last_line['y']) if last_line and y > last_line['y'] else 0
            newpar = (p is None or label is not None or indent or right or (last_line and last_line['right'])
                      or gap > 1.9 * size)
            if newpar:
                new_p('right' if right else None)
                if label:
                    ET.SubElement(p, 'num').text = label
                    p[-1].tail = ' '
            else:
                tail = ''.join(t for _, t, _ in [(r[0], r[1], r[2]) for r in last_line['runs']])[-3:]
                first = rs[0][1].lstrip() if rs else ''
                b.text(join_text(tail.rstrip(), first))
            for st, t, _ in rs:
                b.put(st, t)
            last_line = {'y': y, 'runs': rs, 'right': right}
            log['lines'] += 1
    for it in items.values():
        tidy(it)
    return items, order, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdfs', nargs='+')
    ap.add_argument('--fonts', required=True)
    ap.add_argument('--symbol')
    ap.add_argument('--out', required=True)
    ap.add_argument('--glyphs3', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glyphs3.json'))
    ap.add_argument('--glyph-map', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glyph_map.json'))
    ap.add_argument('--version', default='norm')
    a = ap.parse_args()
    g3 = json.load(open(a.glyphs3)) if os.path.exists(a.glyphs3) else {}
    gmap = json.load(open(a.glyph_map)) if os.path.exists(a.glyph_map) else {}
    fonts = Fonts(a.fonts, a.symbol, {k: v['char'] for k, v in g3.items() if v.get('char')})
    os.makedirs(a.out, exist_ok=True)
    items, order, log = convert(a.pdfs, fonts, a.out, gmap)
    for n in order:
        el = items[n]
        el.set('version', a.version)
        ET.indent(el, space=' ')
        safe = re.sub(r'[^\w.-]', '_', n)
        ET.ElementTree(el).write(os.path.join(a.out, f'{safe}.{a.version}.xml'), encoding='utf-8', xml_declaration=True)
    rep = {'log': dict(log), 'items': order,
           'unknown_glyphs': {f'{k[0]}|{k[1]}': v for k, v in fonts.unknown.most_common()}}
    json.dump(rep, open(os.path.join(a.out, f'report.{a.version}.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rep['log']), 'unknown glyphs:', len(fonts.unknown))


if __name__ == '__main__':
    main()
