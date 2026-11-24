#!/usr/bin/env python3
"""
hwph_ocr.py — recognises the paragraphs that the PDF sets as pictures and puts the text into the
Markdown volumes in place of the picture link.

    python hwph_ocr.py <folder with Bd*.md and img/> [--tesseract PATH] [--lang deu] [--dry-run]

Which pictures are text is written in glyph_map.json ("ocr": true). Needs Tesseract with the German
model (deu.traineddata). Python 3.8+, stdlib only. Running it again changes nothing: a picture that
has been replaced is no longer in the text.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

for _st in (sys.stdout, sys.stderr):
    try:
        _st.reconfigure(errors='replace')
    except Exception:
        pass


def ocr(tesseract, png, lang, tessdata=None):
    cmd = [tesseract, png, 'stdout', '-l', lang, '--psm', '6']
    if tessdata:
        cmd[1:1] = ['--tessdata-dir', tessdata]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out.returncode:
        raise RuntimeError(out.stderr.decode('utf-8', 'replace').strip())
    return out.stdout.decode('utf-8', 'replace')


def to_paragraphs(raw):
    """lines -> paragraphs: join broken words, keep a blank line or an indented start as a break"""
    paras, cur = [], ''
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            if cur:
                paras.append(cur)
                cur = ''
            continue
        if cur.endswith('-') and s[:1].islower():
            cur = cur[:-1] + s
        elif cur:
            cur += ' ' + s
        else:
            cur = s
    if cur:
        paras.append(cur)
    return [re.sub(r'\s+', ' ', p) for p in paras]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder', help='Ordner mit Bd*.md und img/')
    ap.add_argument('--glyphs', default=os.path.join(HERE, 'glyph_map.json'))
    ap.add_argument('--tesseract', default=shutil.which('tesseract') or r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    ap.add_argument('--tessdata', help='Ordner mit deu.traineddata, falls nicht im Standardort')
    ap.add_argument('--lang', default='deu')
    ap.add_argument('--dry-run', action='store_true', help='nur erkennen und zeigen, nichts schreiben')
    a = ap.parse_args()

    glyphs = json.load(open(a.glyphs, encoding='utf-8'))
    targets = [h for h, g in glyphs.items() if g.get('ocr')]
    if not targets:
        sys.exit('в glyph_map.json нет картинок с пометкой "ocr"')
    if not os.path.exists(a.tesseract):
        sys.exit('не найден tesseract: %s (укажите --tesseract)' % a.tesseract)

    texts = {}
    for h in targets:
        png = os.path.join(a.folder, 'img', h + '.png')
        if not os.path.exists(png):
            print('нет файла картинки %s — перегоните PDF конвертером' % png, file=sys.stderr)
            continue
        texts[h] = to_paragraphs(ocr(a.tesseract, png, a.lang, a.tessdata))
        print('%s: распознано абзацев %d, знаков %d' % (h[:8], len(texts[h]), sum(map(len, texts[h]))))

    changed = 0
    for md in sorted(glob.glob(os.path.join(a.folder, 'Bd*.md'))):
        src = open(md, encoding='utf-8').read()
        new = src
        for h, paras in texts.items():
            link = '![](img/%s.png)' % h
            if link in new:
                body = '<!-- OCR: img/%s.png -->\n\n' % h + '\n\n'.join(paras)
                new = new.replace(link, body)
                changed += 1
        if new != src and not a.dry_run:
            open(md, 'w', encoding='utf-8').write(new)
    if a.dry_run:
        for h, paras in texts.items():
            print('\n--- %s\n%s' % (h, '\n\n'.join(paras)))
    print('заменено картинок: %d%s' % (changed, ' (пробный прогон, ничего не записано)' if a.dry_run else ''))


if __name__ == '__main__':
    main()
