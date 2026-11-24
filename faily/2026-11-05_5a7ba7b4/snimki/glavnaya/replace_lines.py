"""Replace whole text lines in the Tengwa ABC PDF, keeping everything else byte-for-byte.
Each replacement: page number (1-based), exact old line text, new text.
The new line keeps the old baseline, size and style, and is centred on the old
line's centre (or kept at the old left edge with align='left').
usage: replace_lines.py IN.pdf OUT.pdf MAP.json FONTDIR
MAP.json: [{"page": 18, "old": "A sturdy ...", "new": "...", "align": "center"}, ...]
"""
import sys, json, os
import pymupdf as fz

src, dst, mapfn, fontdir = sys.argv[1:5]
repl = json.load(open(mapfn, encoding='utf-8'))
doc = fz.open(src)

STYLE = {'AccanthisADFStd-Regular': 'Regular', 'AccanthisADFStd-Italic': 'Italic',
         'AccanthisADFStd-Bold': 'Bold', 'AccanthisADFStd-BoldItal': 'BoldItalic',
         'AccanthisADFStd-BoldItalic': 'BoldItalic'}
fonts = {s: fz.Font(fontfile=os.path.join(fontdir, f'AccanthisCyr-{s}.otf')) for s in set(STYLE.values())}

# embedded Alcarin subset (for the parentheses around the gloss)
alcarin = None
for x in range(1, doc.xref_length()):
    pass

def page_lines(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            spans = [s for s in l['spans'] if s['text'].strip()]
            if spans:
                out.append(spans)
    return out

by_page = {}
for r in repl:
    by_page.setdefault(r['page'], []).append(r)

missing = []
for pno, items in sorted(by_page.items()):
    page = doc[pno - 1]
    lines = page_lines(page)
    todo = []
    for r in items:
        hit = None
        for spans in lines:
            text = ''.join(s['text'] for s in spans).strip()
            if text == r['old'].strip():
                hit = spans
                break
        if hit is None:
            missing.append((pno, r['old']))
            continue
        main = max(hit, key=lambda s: len(s['text']))
        style = STYLE.get(main['font'])
        if style is None:
            missing.append((pno, r['old'] + '  [font ' + main['font'] + ']'))
            continue
        x0 = min(s['bbox'][0] for s in hit); x1 = max(s['bbox'][2] for s in hit)
        y0 = min(s['bbox'][1] for s in hit); y1 = max(s['bbox'][3] for s in hit)
        todo.append(dict(r=r, rect=fz.Rect(x0, y0, x1, y1), base=main['origin'][1],
                         size=main['size'], style=style, color=main['color'], x0=x0, x1=x1))
    for t in todo:
        page.add_redact_annot(t['rect'] + (-0.5, 0.5, 0.5, -0.5))
    page.apply_redactions(images=fz.PDF_REDACT_IMAGE_NONE, graphics=fz.PDF_REDACT_LINE_ART_NONE,
                          text=fz.PDF_REDACT_TEXT_REMOVE)
    for t in todo:
        f = fonts[t['style']]
        fname = 'acyr' + t['style']
        page.insert_font(fontname=fname, fontbuffer=f.buffer)
        new = t['r']['new']
        w = f.text_length(new, fontsize=t['size'])
        align = t['r'].get('align', 'center')
        if align == 'left':
            x = t['x0']
        elif align == 'right':
            x = t['x1'] - w
        else:
            x = (t['x0'] + t['x1']) / 2 - w / 2
        c = t['color']
        page.insert_text((x, t['base']), new, fontname=fname, fontsize=t['size'],
                         color=((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255))

doc.subset_fonts()
doc.save(dst, garbage=3, deflate=True)
print('replaced', sum(len(v) for v in by_page.values()) - len(missing), 'missing', len(missing))
for m in missing:
    print('  MISSING p%d: %s' % m)
