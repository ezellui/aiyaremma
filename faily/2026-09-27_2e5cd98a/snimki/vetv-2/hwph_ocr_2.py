#!/usr/bin/env python3
"""
hwph_ocr.py — puts the two paragraphs that the PDF sets as pictures back into the Markdown volumes.

    python hwph_ocr.py <folder with Bd*.md and img/> [--tesseract PATH] [--tessdata DIR] [--dry-run]

Tesseract reads the running text well but not the notation (Fraktur letters, indices, quantifiers).
glyph_map.json therefore carries, for each such picture, the regions of the picture (in pixels) that
hold notation, with the notation written out as TeX/Unicode. Words that Tesseract finds inside a
region are dropped and the region's notation is put in their place; everything else is Tesseract's.

Python 3.8+, stdlib only. A second run changes nothing: a picture already replaced is gone from the text.
"""
import argparse, csv, glob, io, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _st in (sys.stdout, sys.stderr):
    try:
        _st.reconfigure(errors='replace')
    except Exception:
        pass


def tesseract_words(tesseract, png, lang, tessdata, psm):
    """-> list of lines, each a list of words {text, x0, y0, x1, y1}"""
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, 'ocr')
        cmd = [tesseract, png, base, '-l', lang, '--psm', str(psm), '-c', 'tessedit_create_tsv=1']
        if tessdata:
            cmd[1:1] = ['--tessdata-dir', tessdata]
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if run.returncode or not os.path.exists(base + '.tsv'):
            raise RuntimeError(run.stderr.decode('utf-8', 'replace').strip() or 'tesseract lieferte nichts')
        text = open(base + '.tsv', encoding='utf-8').read()
    lines, order = {}, []
    for r in csv.DictReader(io.StringIO(text), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('level') != '5' or not (r.get('text') or '').strip():
            continue
        key = (int(r['block_num']), int(r['par_num']), int(r['line_num']))
        if key not in lines:
            lines[key] = []
            order.append(key)
        x0, y0 = int(r['left']), int(r['top'])
        lines[key].append(dict(text=r['text'], x0=x0, y0=y0, x1=x0 + int(r['width']), y1=y0 + int(r['height'])))
    return [lines[k] for k in order]


def inside(w, box):
    cx, cy = (w['x0'] + w['x1']) / 2, (w['y0'] + w['y1']) / 2
    return box[0] <= cx <= box[2] and box[1] <= cy <= box[3]


def assemble(lines, regions):
    """lines of words + notation regions -> Markdown paragraphs"""
    used = set()
    out_lines = []                     # (left x, text, is_display)
    for words in lines:
        parts, display = [], None
        for w in words:
            hit = next((i for i, r in enumerate(regions) if inside(w, r['box'])), None)
            if hit is None:
                parts.append(w['text'])
            elif hit not in used:
                used.add(hit)
                if regions[hit].get('display'):
                    display = regions[hit]['text']
                else:
                    parts.append(regions[hit]['text'])
        if display is not None:
            out_lines.append((words[0]['x0'], display, True))
        if parts:
            out_lines.append((words[0]['x0'], ' '.join(parts), False))
    missing = [r['text'] for i, r in enumerate(regions) if i not in used]
    if not out_lines:
        return [], missing
    left = min(x for x, _, d in out_lines if not d) if any(not d for _, _, d in out_lines) else 0
    paras, cur = [], ''
    for x, text, disp in out_lines:
        if disp:
            if cur:
                paras.append(cur)
                cur = ''
            paras.append('$$' + text + '$$')
            continue
        if cur and x > left + 25:          # indented first line: a new paragraph
            paras.append(cur)
            cur = ''
        if cur.endswith('-') and text[:1].islower():
            cur = cur[:-1] + text
        elif cur:
            cur += ' ' + text
        else:
            cur = text
    if cur:
        paras.append(cur)
    # angle quotes read as < >
    paras = [re.sub(r'(?<=\w)>', '›', re.sub(r'<(?=\w)', '‹', p)) if not p.startswith('$$') else p for p in paras]
    return paras, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder', help='Ordner mit Bd*.md und img/')
    ap.add_argument('--glyphs', default=os.path.join(HERE, 'glyph_map.json'))
    ap.add_argument('--tesseract', default=shutil.which('tesseract') or r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    ap.add_argument('--tessdata', help='Ordner mit deu.traineddata, falls nicht im Standardort')
    ap.add_argument('--lang', default='deu')
    ap.add_argument('--psm', type=int, default=6)
    ap.add_argument('--dry-run', action='store_true', help='nur erkennen und zeigen, nichts schreiben')
    a = ap.parse_args()

    glyphs = json.load(open(a.glyphs, encoding='utf-8'))
    targets = {h: g for h, g in glyphs.items() if g.get('ocr')}
    if not targets:
        sys.exit('в glyph_map.json нет картинок с пометкой "ocr"')
    if not os.path.exists(a.tesseract):
        sys.exit('не найден tesseract: %s (укажите --tesseract)' % a.tesseract)

    texts = {}
    for h, g in targets.items():
        png = os.path.join(a.folder, 'img', h + '.png')
        if not os.path.exists(png):
            print('нет файла картинки %s — перегоните PDF конвертером' % png, file=sys.stderr)
            continue
        paras, missing = assemble(tesseract_words(a.tesseract, png, a.lang, a.tessdata, a.psm), g.get('ocr_regions', []))
        texts[h] = paras
        print('%s: абзацев %d, формульных участков %d, не нашли слов в %d' % (h[:8], len(paras), len(g.get('ocr_regions', [])), len(missing)))
        for t in missing:
            print('   участок без слов (формула потеряна, проверьте вручную):', t[:70], file=sys.stderr)

    changed = 0
    for md in sorted(glob.glob(os.path.join(a.folder, 'Bd*.md'))):
        src = open(md, encoding='utf-8').read()
        new = src
        for h, paras in texts.items():
            link = '![](img/%s.png)' % h
            if link in new:
                new = new.replace(link, '<!-- OCR: img/%s.png -->\n\n' % h + '\n\n'.join(paras))
                changed += 1
        if new != src and not a.dry_run:
            open(md, 'w', encoding='utf-8').write(new)
    if a.dry_run:
        for h, paras in texts.items():
            print('\n--- %s\n%s' % (h, '\n\n'.join(paras)))
    print('заменено картинок: %d%s' % (changed, ' (пробный прогон, ничего не записано)' if a.dry_run else ''))


if __name__ == '__main__':
    main()
