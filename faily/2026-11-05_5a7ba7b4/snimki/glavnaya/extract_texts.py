"""Extract every English text of the Tengwa ABC book into translatable units.
usage: extract_texts.py BOOK.pdf texts.json layout.json
texts.json  : what the translator edits ({"units": [{"id","kind","where","en","ru"}]})
layout.json : geometry per unit id (do not edit)
"""
import sys, json, re
import pymupdf as fz

src, out_texts, out_layout = sys.argv[1:4]
doc = fz.open(src)

ACC = 'AccanthisADFStd-'
QUENYA_FONTS = ('AlcarinTengwar-Regular',)
PAGE_NUM_RE = re.compile(r'^\d+$')

def style_of(font):
    if font.startswith(ACC):
        s = font[len(ACC):]
        return {'BoldItal': 'BoldItalic'}.get(s, s)
    return None

def page_lines(page):
    out = []
    for b in page.get_text('dict', flags=fz.TEXT_PRESERVE_WHITESPACE)['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            sp = [s for s in l['spans'] if s['text'].strip() or s['text'] == ' ']
            sp = [s for s in sp if s['text'] != '']
            if any(s['text'].strip() for s in sp):
                out.append(sp)
    return out

def ltext(spans):
    return ''.join(s['text'] for s in spans)

def markup(spans):
    """spans -> text with *italic* / **bold** markup (Accanthis styles only)"""
    out = ''
    for s in spans:
        st = style_of(s['font'])
        t = s['text']
        if st in ('Italic', 'BoldItalic', 'Bold') and t.strip():
            lead = t[:len(t) - len(t.lstrip())]; trail = t[len(t.rstrip()):]
            core = t.strip()
            mark = {'Italic': '*', 'Bold': '**', 'BoldItalic': '***'}[st]
            out += lead + mark + core + mark + trail
        else:
            out += t
    return out

def join_lines(texts):
    res = ''
    for t in texts:
        t = t.rstrip()
        if not res:
            res = t; continue
        if res.endswith('\xad'):
            res = res[:-1] + t.lstrip()
        elif res.endswith('-') and not res.endswith(' -'):
            res = res + t.lstrip()
        else:
            res = res + ' ' + t.lstrip()
    return res.replace('****', '').replace('** **', ' ').replace('* *', ' ')

def lgeom(spans, page):
    return dict(x0=round(min(s['bbox'][0] for s in spans), 2), x1=round(max(s['bbox'][2] for s in spans), 2),
                base=round(spans[0]['origin'][1], 2), size=round(spans[0]['size'], 2))

units = []; layout = {}
def add(uid, kind, where, en, geom):
    units.append(dict(id=uid, kind=kind, where=where, en=en, ru=([] if isinstance(en, list) else '')))
    layout[uid] = geom

# chapter pages: title in Bold 18.2 centred, next page = Quenya page
title_pages = {}
for i, p in enumerate(doc):
    for sp in page_lines(p):
        if sp[0]['font'] == ACC + 'Bold' and abs(sp[0]['size'] - 18.2) < 0.2:
            title_pages[i] = ltext(sp).strip()
chapter_a = {i for i, t in title_pages.items() if (i + 1) < len(doc) and any(
    s['font'] in QUENYA_FONTS for sp in page_lines(doc[i + 1]) for s in sp)}
chapter_b = {i + 1 for i in chapter_a}

header_pages = []
for i, page in enumerate(doc):
    pno = i + 1
    W = page.rect.width
    L = page_lines(page)
    where = 'стр. %d (в книге %s)' % (pno, next((ltext(sp) for sp in L if PAGE_NUM_RE.match(ltext(sp).strip()) and sp[0]['origin'][1] > 500), '—'))
    rest = []
    for sp in L:
        t = ltext(sp).strip()
        if sp[0]['font'] == 'LiberationSerif-Italic' and t == '—Tengwa ABC—':
            header_pages.append(pno); continue
        if PAGE_NUM_RE.match(t) and sp[0]['origin'][1] > 500:
            continue
        if all(s['font'] in QUENYA_FONTS for s in sp):
            continue
        if i in chapter_b and all(style_of(s['font']) == 'Italic' and abs(s['size'] - 14) < .2 for s in sp if s['text'].strip()):
            continue      # romanised Quenya
        rest.append(sp)
    if not rest:
        continue
    if i in chapter_a or i in chapter_b:
        # title / gloss / poem lines (A) or literal translation (B)
        title = [sp for sp in rest if sp[0]['font'] == ACC + 'Bold' and abs(sp[0]['size'] - 18.2) < .2]
        gloss = [sp for sp in rest if any(abs(s['size'] - 16) < .2 and style_of(s['font']) == 'Regular' for s in sp)]
        body = [sp for sp in rest if sp not in title and sp not in gloss]
        tag = 'p%03d' % pno
        if title:
            add(tag + '-title', 'lines', where + ': название тенгвы', [ltext(title[0]).strip()],
                dict(page=pno, align='center', style='Bold', lines=[lgeom(title[0], page)]))
        if gloss:
            sp = gloss[0]
            main = [s for s in sp if style_of(s['font']) == 'Regular']
            add(tag + '-gloss', 'gloss', where + ': значение (скобки сохраняются)', ltext(main).strip(),
                dict(page=pno, style='Regular', line=lgeom(sp, page), main=lgeom(main, page),
                     sides=[dict(text=s['text'], font=s['font'], x=round(s['origin'][0], 2), x1=round(s['bbox'][2], 2),
                                 base=round(s['origin'][1], 2)) for s in sp if s not in main]))
        if body:
            kind = 'стих' if i in chapter_a else 'подстрочник'
            add(tag + ('-poem' if i in chapter_a else '-literal'), 'lines', where + ': ' + kind,
                [ltext(sp).strip() for sp in body],
                dict(page=pno, align='center', style=style_of(body[0][0]['font']) or 'Regular',
                     lines=[lgeom(sp, page) for sp in body]))
        continue

    # ---- non-chapter pages ----
    tag = 'p%03d' % pno
    # table of contents
    if any(re.search(r'\.{4,}\s*\d+$', ltext(sp)) for sp in rest):
        n = 0
        for sp in rest:
            t = ltext(sp).strip()
            m = re.match(r'^(.*?)\.{2,}\s*(\d+)$', t)
            if m:
                n += 1
                add('%s-toc%02d' % (tag, n), 'toc', where + ': оглавление', m.group(1),
                    dict(page=pno, style=style_of(sp[0]['font']) or 'Regular', font=sp[0]['font'],
                         num=m.group(2), **lgeom(sp, page)))
            else:
                add('%s-h%02d' % (tag, n), 'lines', where + ': заголовок', [t],
                    dict(page=pno, align='left', style=style_of(sp[0]['font']) or 'Regular', lines=[lgeom(sp, page)]))
        continue
    # foreign-font display lines (title pages): one unit per line
    if all(not style_of(s['font']) for sp in rest for s in sp if s['font'] != 'LiberationSerif'):
        for n, sp in enumerate(rest, 1):
            g = lgeom(sp, page)
            c = (g['x0'] + g['x1']) / 2
            add('%s-d%02d' % (tag, n), 'lines', where + ': титульная надпись (шрифт %s)' % sp[0]['font'], [ltext(sp).strip()],
                dict(page=pno, align='center' if abs(c - W / 2) < 4 else 'left', font=sp[0]['font'], lines=[g]))
        continue
    # prose page: group into blocks (headings, paragraphs, list items)
    items = []
    for sp in rest:
        bullets = [s for s in sp if s['font'] == 'OpenSymbol']
        text_sp = [s for s in sp if s['font'] != 'OpenSymbol']
        g = lgeom(text_sp, page)
        st = style_of(max(text_sp, key=lambda s: len(s['text']))['font'])
        items.append(dict(sp=text_sp, bullets=bullets, g=g, st=st))
    blocks = []
    for it in items:
        g = it['g']
        heading = it['st'] == 'Bold' and g['size'] >= 15.9
        centred = abs((g['x0'] + g['x1']) / 2 - W / 2) < 3 and g['x0'] > 80
        prev = blocks[-1] if blocks else None
        if (prev and not heading and not prev['heading'] and not it['bullets'] and not prev['centred'] and not centred
                and abs(prev['lines'][-1]['g']['x0'] - g['x0']) < 1 and abs(prev['lines'][-1]['g']['size'] - g['size']) < .1
                and 0 < g['base'] - prev['lines'][-1]['g']['base'] < g['size'] * 1.5):
            prev['lines'].append(it)
        else:
            blocks.append(dict(lines=[it], heading=heading, centred=centred))
    for n, b in enumerate(blocks, 1):
        first = b['lines'][0]
        geom = dict(page=pno, x0=first['g']['x0'], size=first['g']['size'], style=first['st'] or 'Regular',
                    bases=[ln['g']['base'] for ln in b['lines']], x1s=[ln['g']['x1'] for ln in b['lines']],
                    bullets=[dict(x=round(s['origin'][0], 2), base=round(s['origin'][1], 2), text=s['text']) for s in first['bullets']],
                    links=[])
        for ln in b['lines']:
            for lk in page.get_links():
                r = fz.Rect(lk['from'])
                lb = fz.Rect(ln['g']['x0'], ln['g']['base'] - ln['g']['size'] * .7, ln['g']['x1'], ln['g']['base'])
                if lk.get('uri') and r.intersects(lb):
                    txt = page.get_textbox(r).strip()
                    geom['links'].append(dict(uri=lk['uri'], text=txt))
        if b['heading']:
            add('%s-h%02d' % (tag, n), 'lines', where + ': заголовок', [ltext(first['sp']).strip()],
                dict(geom, align='left', lines=[first['g']], flow=True))
        elif b['centred'] or (len(b['lines']) == 1 and first['g']['x0'] > 120):
            add('%s-c%02d' % (tag, n), 'lines', where + ': отдельная строка', [markup(ln['sp']).strip() for ln in b['lines']],
                dict(geom, align='center' if b['centred'] else 'right', lines=[ln['g'] for ln in b['lines']], flow=True))
        else:
            add('%s-a%02d' % (tag, n), 'para', where + (': пункт списка' if first['bullets'] else ': абзац'),
                join_lines([markup(ln['sp']) for ln in b['lines']]), dict(geom, flow=True))

# the running header: one unit for all pages
units.insert(0, dict(id='header', kind='lines', where='колонтитул на %d страницах' % len(header_pages),
                     en=['—Tengwa ABC—'], ru=[]))
layout['header'] = dict(pages=header_pages, font='LiberationSerif-Italic', align='center')

json.dump(dict(note='Заполняйте только поля ru. Пустое ru = оставить английский текст. '
                    'В абзацах (kind=para) разметка: *курсив*, **полужирный**; переносы строк ставит скрипт. '
                    'В kind=lines каждая строка массива ru = строка на странице. '
                    'В kind=gloss — только слово, скобки остаются из книги. В kind=toc — только название главы.',
               units=units), open(out_texts, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(layout, open(out_layout, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(units), 'units', Counter(u['kind'] for u in units))
