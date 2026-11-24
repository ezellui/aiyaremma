#!/usr/bin/env python3
"""Prototype: printed BEE (Folio Views -> Wine -> CUPS-PDF) normalized transcription -> HTML.

Usage: folio_pdf2html.py input.pdf fontdir output.html
fontdir: folder with the original OUP/WAB TTF fonts from the CD (PLANOUP.TTF etc.).
"""
import io
import re
import sys
import html
from collections import defaultdict

import pdfplumber
import pikepdf
from fontTools.ttLib import TTFont
from fontTools.agl import toUnicode
from fontTools.t1Lib import T1Font

ORIG = {
    'PlantinOUP': 'PLANOUP.TTF', 'PlantinOUP-Italic': 'PLANIOUP.TTF',
    'PlantinOUP-Bold': 'PLANBOUP.TTF', 'PlantinOUP-BoldItalic': 'PLANZOUP.TTF',
    'ArialOUP': 'ARIOUP.TTF', 'ArialOUP-Bold': 'ARIBOUP.TTF',
    'ArialOUP-Italic': 'ARIIOUP.TTF', 'ArialOUP-BoldItalic': 'ARIBIOUP.TTF',
    'Waboup1': 'WABOUP.TTF', 'Wablast1': 'WABLAST.TTF', 'Wabmath1': 'WABMATH.TTF',
}
# Glyphs with private names in the OUP fonts; filled in after visual identification.
PRIVATE = {'p98': '„', 'p71': '“'}

COLORS = {  # BEE legend, normalized transcription
    (0.0, 0.0, 0.630859): 'txt',      # standard blue
    (0.970703, 0.209961, 0.199951): 'ed',  # red: editorial
    (0.0, 0.0, 0.0): 'alt',          # black: last of undecided alternatives
}


def symbol_table():
    t1 = T1Font('/usr/share/fonts/type1/urw-base35/StandardSymbolsPS.t1')
    t1.parse()
    enc = t1.font['Encoding']
    return {i: (toUnicode(n) or '') for i, n in enumerate(enc) if n != '.notdef'}


def font_tables(pdf_path, fontdir):
    """Map embedded-subset font name -> {pdf byte code: unicode}."""
    pdf = pikepdf.open(pdf_path)
    sym = symbol_table()
    tables = {}
    for page in pdf.pages:
        for _, fo in page.Resources.get('/Font', {}).items():
            bn = str(fo.get('/BaseFont', '')).lstrip('/')
            if not bn or bn in tables:
                continue
            base = bn.split('+')[-1]
            if base == 'Symbol':
                tables[bn] = sym
                continue
            if base not in ORIG or '/FontFile2' not in fo.FontDescriptor:
                continue
            sub = TTFont(io.BytesIO(fo.FontDescriptor.FontFile2.read_bytes()))
            og = TTFont(f'{fontdir}/{ORIG[base]}').getGlyphOrder()
            sg = sub.getGlyphOrder()
            m = {}
            for code, g in sub['cmap'].getcmap(1, 0).cmap.items():
                name = og[sg.index(g)]
                m[code] = PRIVATE.get(name) or toUnicode(name) or f'[?{name}]'
            tables[bn] = m
    return tables


def decode(ch, tables):
    t = tables.get(ch['fontname'])
    if t is None:
        return ch['text']
    try:
        code = ch['text'].encode('cp1252')[0]
    except (UnicodeEncodeError, IndexError):
        return ch['text']
    return t.get(code, ch['text'])


def color_class(ch):
    c = tuple(round(x, 6) for x in (ch.get('non_stroking_color') or ()))
    return COLORS.get(c, 'txt')


def underlines(page):
    out = []
    for r in page.rects + page.lines:
        if r['height'] < 1.5 and r['width'] > 2:
            out.append((r['x0'], r['x1'], r['top']))
    return out


def is_underlined(ch, uls):
    for x0, x1, y in uls:
        if x0 - 0.5 <= ch['x0'] and ch['x1'] <= x1 + 0.5 and 0 <= y - ch['bottom'] + 3 <= 5:
            return True
    return False


def lines_of(page, tables):
    uls = underlines(page)
    rows = defaultdict(list)
    for ch in page.chars:
        rows[round(ch['bottom'])].append(ch)
    for y in sorted(rows):
        chs = sorted(rows[y], key=lambda c: c['x0'])
        spans, prev = [], None
        for ch in chs:
            txt = decode(ch, tables)
            if prev is not None and ch['x0'] - prev['x1'] > ch['size'] * 0.2 and not txt.isspace():
                txt = ' ' + txt
            key = (color_class(ch), is_underlined(ch, uls), 'Italic' in ch['fontname'],
                   ch['fontname'].split('+')[-1].startswith('Arial'))
            if spans and spans[-1][0] == key:
                spans[-1][1].append(txt)
            else:
                spans.append((key, [txt]))
            prev = ch
        yield y, chs[0]['x0'], chs[-1]['x1'], spans


def span_html(spans):
    out = []
    for (cls, ul, it, _), parts in spans:
        s = html.escape(''.join(parts))
        if ul:
            s = f'<u>{s}</u>'
        if it:
            s = f'<i>{s}</i>'
        out.append(s if cls == 'txt' else f'<span class="{cls}">{s}</span>')
    return ''.join(out)


def convert(pdf_path, fontdir, out_path):
    tables = font_tables(pdf_path, fontdir)
    body, para = [], []

    def flush():
        if para:
            body.append('<p>' + ' '.join(para).replace('- ', '-') + '</p>')
            para.clear()

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            last_y = None
            for y, x0, x1, spans in lines_of(page, tables):
                plain = ''.join(''.join(p) for _, p in spans).strip()
                if y < 200 or not plain:  # running header of the printout
                    continue
                m = re.match(r'Item (\S+) Page\s+(\S+.*)$', plain)
                if m:
                    item, pg = m.group(1), m.group(2).strip()
                    body.append(f'<h3 class="pb" id="ms{item}-{pg.replace(" ", "_")}">'
                                f'{item}, {html.escape(pg)}</h3>')
                    last_y = y
                    continue
                if re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{2}\.?', plain) and x0 > 400:
                    flush()
                    body.append(f'<p class="date">{html.escape(plain)}</p>')
                    last_y = y
                    continue
                gap = (y - last_y) if last_y is not None else 0
                indent = x0 > 150 and not para
                if gap > 30 or (x0 > 150 and para):
                    flush()
                para.append(span_html(spans).strip())
                last_y = y
            # page breaks of the printout are not text breaks
    flush()
    doc = f'''<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<title>Ms-101 (Auszug) — BEE, normalisierte Transkription</title>
<style>
body{{max-width:44em;margin:2em auto;font:17px/1.55 Georgia,serif;color:#1a1a6e}}
.ed{{color:#c62828}} .alt{{color:#111}}
.date{{text-align:right;margin:.2em 0;color:#555}}
h3.pb{{font:600 12px/1 system-ui,sans-serif;color:#c62828;margin:1.6em 0 .4em;border-top:1px solid #eee;padding-top:.4em}}
p{{margin:.3em 0}}
</style></head><body>
<p style="font:13px system-ui;color:#777">Prototyp der Konvertierung · Quelle: Wittgenstein's Nachlass, BEE (OUP 2000), Normalized Transcription, Ausdruck</p>
{chr(10).join(body)}
</body></html>'''
    open(out_path, 'w', encoding='utf-8').write(doc)
    return len(body)


if __name__ == '__main__':
    print(convert(*sys.argv[1:4]), 'blocks')
