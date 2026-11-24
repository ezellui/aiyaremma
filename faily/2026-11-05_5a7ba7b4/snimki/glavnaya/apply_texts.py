"""Put translated texts (texts.json, field ru) into the Tengwa ABC PDF.
Only units with a non-empty ru are touched; everything else stays byte-for-byte.
usage: apply_texts.py BOOK.pdf texts.json layout.json fonts.json OUT.pdf
fonts.json maps style/font names to font files, e.g.
  {"Regular": ".../AccanthisADFStdCyr-Regular.otf", ..., "LiberationSerif-Italic": "...", "Cantarell-Thin": "..."}
"""
import sys, json, re, os
import pymupdf as fz
import pikepdf, pyphen

src, texts_fn, layout_fn, fonts_fn, dst = sys.argv[1:6]
units = json.load(open(texts_fn, encoding='utf-8'))['units']
lay = json.load(open(layout_fn, encoding='utf-8'))
fontfiles = json.load(open(fonts_fn, encoding='utf-8'))
hy = pyphen.Pyphen(lang='ru_RU')
doc = fz.open(src)

warnings = []
def warn(uid, msg):
    warnings.append('%s: %s' % (uid, msg))

_fonts = {}
def font(key):
    if key not in _fonts:
        if key not in fontfiles or not os.path.exists(fontfiles[key]):
            return None
        _fonts[key] = fz.Font(fontfile=fontfiles[key])
    return _fonts[key]

def fkey(style, fontname=None):
    if fontname and not fontname.startswith('AccanthisADFStd-'):
        return fontname
    return style or 'Regular'

COMBINE = {'Regular': {'*': 'Italic', '**': 'Bold', '***': 'BoldItalic'},
           'Bold': {'*': 'BoldItalic', '**': 'Regular', '***': 'Italic'},
           'Italic': {'*': 'Regular', '**': 'BoldItalic', '***': 'Bold'},
           'BoldItalic': {'*': 'Bold', '**': 'Italic', '***': 'Regular'}}

def runs_of(text, base):
    """'a *b* **c**' -> [(text, fontkey)]; markup only for Accanthis styles"""
    if base not in COMBINE:
        return [(text, base)]
    out = []
    for part in re.split(r'(\*{1,3}[^*]+?\*{1,3})', text):
        if not part:
            continue
        m = re.fullmatch(r'(\*{1,3})([^*]+?)\1', part)
        if m:
            out.append((m.group(2), COMBINE[base][m.group(1)]))
        else:
            out.append((part, base))
    return out

def width(runs, size):
    return sum(font(k).text_length(t, fontsize=size) for t, k in runs)

def words_of(runs):
    """split runs into words (lists of runs) at spaces"""
    words = [[]]
    for t, k in runs:
        parts = re.split(r'( )', t)
        for p in parts:
            if p == ' ':
                words.append([])
            elif p:
                words[-1].append((p, k))
    return [w for w in words if w]

def hyphen_splits(word):
    """possible (head_runs, tail_runs) splits of a word (list of runs)"""
    text = ''.join(t for t, _ in word)
    if '://' in text or '@' in text or len(text) < 5:
        return []
    pos = [p for p in hy.positions(text)]
    res = []
    for p in sorted(pos, reverse=True):
        head, tail, acc = [], [], 0
        for t, k in word:
            if acc + len(t) <= p:
                head.append((t, k))
            elif acc >= p:
                tail.append((t, k))
            else:
                head.append((t[:p - acc], k)); tail.append((t[p - acc:], k))
            acc += len(t)
        head = head[:-1] + [(head[-1][0] + '-', head[-1][1])]
        res.append((head, tail))
    return res

def wrap(runs, size, maxw):
    """greedy line breaking with Russian hyphenation; returns list of run-lists"""
    lines, cur = [], []
    def joined(a, b):
        return a + ([(' ', b[0][1])] if a else []) + b
    for w in words_of(runs):
        trial = joined(cur, w)
        if width(trial, size) <= maxw or not cur:
            if not cur and width(w, size) > maxw:
                warn('-', 'слово шире строки: ' + ''.join(t for t, _ in w))
            cur = trial
            continue
        placed = False
        for head, tail in hyphen_splits(w):
            if width(joined(cur, head), size) <= maxw:
                lines.append(joined(cur, head)); cur = tail; placed = True
                break
        if not placed:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- planning
ops = {}           # page index -> dict(redact=[rects], place=[(x, base, runs, size)], shifts=[], links=[])
def P(i):
    return ops.setdefault(i, dict(redact=[], place=[], shifts=[], links=[]))

def band(x0, x1, base, size):
    return fz.Rect(x0 - 0.3, base - size * 0.62, x1 + 0.3, base + size * 0.12)

def place_line(pg, runs, size, base, align, x0, x1):
    w = width(runs, size)
    x = x0 if align == 'left' else (x1 - w if align == 'right' else (x0 + x1) / 2 - w / 2)
    P(pg)['place'].append((x, base, runs, size))
    return x, w

def ru_of(u):
    r = u.get('ru')
    if isinstance(r, list):
        r = [x for x in r if x is not None]
        return r if any(str(x).strip() for x in r) else None
    return r if (r and r.strip()) else None

flow_pages = {}
for u in units:
    uid = u['id']; ru = ru_of(u); g = lay.get(uid)
    if ru is None or g is None:
        continue
    if uid == 'header':
        k = fkey(None, g['font'])
        if not font(k):
            warn(uid, 'нет файла шрифта ' + k); continue
        for p in g['pages']:
            page = doc[p - 1]
            for b in page.get_text('dict')['blocks']:
                for l in b.get('lines', []):
                    for s in l['spans']:
                        if s['text'].strip() == u['en'][0]:
                            P(p - 1)['redact'].append(fz.Rect(s['bbox']))
                            place_line(p - 1, [(ru[0], k)], s['size'], s['origin'][1], 'center', s['bbox'][0], s['bbox'][2])
        continue
    pg = g['page'] - 1
    if g.get('flow'):
        flow_pages.setdefault(pg, []).append(u)
        continue
    if u['kind'] == 'gloss':
        k = fkey(g['style'])
        m = g['main']
        P(pg)['redact'].append(band(m['x0'], m['x1'], m['base'], m['size']))
        text = '(' + ru + ')' if g.get('paren') else ru
        runs = [(text, k)]
        wmain = width(runs, m['size'])
        sides = g['sides']
        line = g['line']
        # original advances of side spans
        before = [s for s in sides if s['x'] < m['x0']]
        after = [s for s in sides if s['x'] >= m['x0']]
        wb = sum(m['x0'] - s['x'] for s in before[-1:]) if before else 0
        wa = sum(s['x1'] - s['x'] for s in after)
        total = wb + wmain + wa
        x = (line['x0'] + line['x1']) / 2 - total / 2
        for s in before:
            P(pg)['shifts'].append((s['x'], s['base'], x, s['base'])); x += wb
        P(pg)['place'].append((x, m['base'], runs, m['size'])); x += wmain
        for s in after:
            P(pg)['shifts'].append((s['x'], s['base'], x, s['base'])); x += s['x1'] - s['x']
        continue
    if u['kind'] == 'toc':
        k = fkey(g['style'], g.get('font'))
        if not font(k):
            warn(uid, 'нет файла шрифта ' + k); continue
        P(pg)['redact'].append(band(g['x0'], g['x1'], g['base'], g['size']))
        name = [(ru, k)]
        num = [(g['num'], k)]
        wn = width(name, g['size']); wnum = width(num, g['size'])
        dotw = font(k).text_length('.', fontsize=g['size'])
        free = g['x1'] - g['x0'] - wn - wnum
        if free < dotw * 2:
            warn(uid, 'название не помещается в строку оглавления (не хватает %.1f pt)' % (dotw * 2 - free))
        ndots = max(1, int((free - 1) / dotw))
        place_line(pg, name, g['size'], g['base'], 'left', g['x0'], g['x1'])
        P(pg)['place'].append((g['x1'] - wnum - ndots * dotw, g['base'], [('.' * ndots, k)], g['size']))
        P(pg)['place'].append((g['x1'] - wnum, g['base'], num, g['size']))
        continue
    # kind lines (non-flow)
    k = fkey(g.get('style'), g.get('font'))
    if not font(k):
        warn(uid, 'нет файла шрифта для «%s» — пропущено' % k); continue
    L = g['lines']
    for l in L:
        P(pg)['redact'].append(band(l['x0'], l['x1'], l['base'], l['size']))
    size = L[0]['size']
    lead = (L[1]['base'] - L[0]['base']) if len(L) > 1 else size * 1.37
    page_w = doc[pg].rect.width
    maxw = g.get('maxw') or (page_w - 2 * 50)
    prefix = g.get('prefix', '')
    texts = ru if isinstance(ru, list) else [ru]
    if g.get('paren'):
        texts = ['(' + ' '.join(texts) + ')']
    out_lines = []
    for t in texts:
        for wl in wrap(runs_of(prefix + t, k), size, maxw):
            out_lines.append(wl)
    if len(out_lines) > len(L) and not g.get('maxw'):
        warn(uid, 'строк стало %d вместо %d — лишние продолжены вниз с тем же интерлиньяжем' % (len(out_lines), len(L)))
    for i, runs in enumerate(out_lines):
        ref = L[min(i, len(L) - 1)]
        base = ref['base'] if i < len(L) else L[-1]['base'] + lead * (i - len(L) + 1)
        if g['align'] == 'center':
            cx = (ref['x0'] + ref['x1']) / 2
            place_line(pg, runs, size, base, 'center', cx, cx)
        else:
            place_line(pg, runs, size, base, g['align'], ref['x0'], ref['x1'])
    if g.get('links'):
        P(pg)['links'].append((g['links'], out_lines, L))

# ---- flowing pages (prose): units follow each other keeping the original gaps
BOTTOM = 470.0
for pg, us in flow_pages.items():
    page = doc[pg]
    allu = [u for u in units if lay.get(u['id'], {}).get('page') == pg + 1 and lay[u['id']].get('flow')]
    def first_last(g):
        if 'bases' in g and g.get('bases'):
            return g['bases'][0], g['bases'][-1]
        return g['lines'][0]['base'], g['lines'][-1]['base']
    prev_orig_last = None; cur_last = None
    for u in allu:
        g = lay[u['id']]; ru = ru_of(u)
        f0, fl = first_last(g)
        start = f0 if prev_orig_last is None else cur_last + (f0 - prev_orig_last)
        if ru is None:
            if cur_last is not None and abs(start - f0) > 0.5:
                warn(u['id'], 'не переведён, а соседи сдвинулись — может наложиться (сдвиг %.1f pt)' % (start - f0))
            prev_orig_last, cur_last = fl, fl
            continue
        k = fkey(g.get('style'))
        size = g['size']
        if u['kind'] == 'para':
            lead = (g['bases'][1] - g['bases'][0]) if len(g['bases']) > 1 else size * 1.367
            x0 = g['x0']
            x1 = 316.2 if x0 < 60 else 316.2
            for b, x1o in zip(g['bases'], g['x1s']):
                P(pg)['redact'].append(band(g['x0'], x1o, b, size))
            wl = wrap(runs_of(ru, k), size, x1 - x0)
            for i, runs in enumerate(wl):
                place_line(pg, runs, size, start + i * lead, 'left', x0, x1)
            for bl in g.get('bullets', []):
                P(pg)['shifts'].append((bl['x'], bl['base'], bl['x'], start))
            last = start + (len(wl) - 1) * lead
            if g.get('links'):
                P(pg)['links'].append((g['links'], wl, [dict(x0=x0, base=start + i * lead, size=size) for i in range(len(wl))]))
        else:
            L = g['lines']
            lead = (L[1]['base'] - L[0]['base']) if len(L) > 1 else size * 1.37
            for l in L:
                P(pg)['redact'].append(band(l['x0'], l['x1'], l['base'], l['size']))
            texts = ru if isinstance(ru, list) else [ru]
            outl = [r for t in texts for r in wrap(runs_of(t, k), size, 316.2 - L[0]['x0'] if g['align'] == 'left' else 264)]
            for i, runs in enumerate(outl):
                ref = L[min(i, len(L) - 1)]
                if g['align'] == 'center':
                    cx = (ref['x0'] + ref['x1']) / 2
                    place_line(pg, runs, size, start + i * lead, 'center', cx, cx)
                else:
                    place_line(pg, runs, size, start + i * lead, g['align'], ref['x0'], ref['x1'])
            last = start + (len(outl) - 1) * lead
        if last > BOTTOM:
            warn(u['id'], 'текст ушёл ниже поля набора на %.1f pt (стр. %d)' % (last - BOTTOM, pg + 1))
        prev_orig_last, cur_last = fl, last

# ---------------------------------------------------------------- execution
for pg, o in sorted(ops.items()):
    page = doc[pg]
    for r in o['redact']:
        page.add_redact_annot(r)
    if o['redact']:
        page.apply_redactions(images=fz.PDF_REDACT_IMAGE_NONE, graphics=fz.PDF_REDACT_LINE_ART_NONE,
                              text=fz.PDF_REDACT_TEXT_REMOVE)
    used = {}
    for x, base, runs, size in o['place']:
        for t, k in runs:
            if k not in used:
                fn = 'f%d' % (len(used) + 1)
                page.insert_font(fontname=fn, fontbuffer=font(k).buffer)
                used[k] = fn
            page.insert_text((x, base), t, fontname=used[k], fontsize=size, color=(0, 0, 0))
            x += font(k).text_length(t, fontsize=size)
    # links: move rects onto the new position of the link text
    if o['links']:
        cur_links = page.get_links()
        for links, wl, L in o['links']:
            for lk in links:
                found = None
                for i, runs in enumerate(wl):
                    line = ''.join(t for t, _ in runs)
                    j = line.find(lk['text'])
                    if j >= 0:
                        x = [p for p in o['place'] if abs(p[1] - (L[i]['base'] if i < len(L) else 0)) < 0.01]
                        found = (i, j, line)
                        break
                for cl in cur_links:
                    if cl.get('uri') == lk['uri']:
                        if found:
                            i, j, line = found
                            entry = [p for p in o['place'] if ''.join(t for t, _ in p[2]) == line]
                            if entry:
                                x, base, runs, size = entry[0]
                                pre = width_prefix = 0
                                acc = ''
                                for t, k in runs:
                                    if len(acc) + len(t) <= j:
                                        pre += font(k).text_length(t, fontsize=size); acc += t
                                    else:
                                        pre += font(k).text_length(t[:j - len(acc)], fontsize=size); kk = k; break
                                w = font(runs[0][1]).text_length(lk['text'], fontsize=size)
                                cl['from'] = fz.Rect(x + pre, base - size * 0.8, x + pre + w, base + size * 0.25)
                                page.update_link(cl)
                        else:
                            page.delete_link(cl)
                            warn('link', 'ссылка %s удалена: её текста нет в переводе' % lk['uri'])

doc.subset_fonts()
tmp = dst + '.tmp.pdf'
doc.save(tmp, garbage=3, deflate=True)

# move side/bullet text objects (kept in their original embedded fonts)
pdf = pikepdf.open(tmp)
moved = 0; want = sum(len(o['shifts']) for o in ops.values())
for pg, o in ops.items():
    if not o['shifts']:
        continue
    page = pdf.pages[pg]
    H = float(page.mediabox[3])
    cs = pikepdf.parse_content_stream(page)
    changed = False
    for ox, ob, nx, nb in o['shifts']:
        for i, (operands, op) in enumerate(cs):
            if str(op) in ('Td', 'TD') and abs(float(operands[0]) - ox) < 0.2 and abs(float(operands[1]) - (H - ob)) < 0.2:
                cs[i] = pikepdf.ContentStreamInstruction([pikepdf.Object.parse(b'%.3f' % nx), pikepdf.Object.parse(b'%.3f' % (H - nb))], op)
                changed = True; moved += 1
                break
    if changed:
        page.Contents = pdf.make_stream(pikepdf.unparse_content_stream(cs))
pdf.save(dst)
os.remove(tmp)

n = sum(1 for u in units if ru_of(u) is not None)
print('подставлено единиц: %d; перемещено служебных знаков: %d из %d' % (n, moved, want))
for w in warnings:
    print('  ! ' + w)
