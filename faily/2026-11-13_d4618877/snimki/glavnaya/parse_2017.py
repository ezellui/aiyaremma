"""Издание 2017 г. (Канон+): четыре текста «Трактата» на развороте → props по редакциям.

Чётная страница файла: немецкий | русский (Добронравов–Лахути, 2-е изд. 2008);
нечётная: английский Огдена (1933) | английский Пирса–Макгиннесса (1974).
Текстовый слой DjVu (распознанный) режется по середине страницы на два столбца; колонтитул,
номер страницы и подстрочные примечания (мелкий кегль) отделяются; абзацы — по отступу.

    python3 parse_2017.py ../tlp1/tlp2017.djvu raw2017.json
"""
import json, re, statistics, sys
import djvu_lines as dl

DJ, OUT = sys.argv[1:3]
FIRST, LAST = 36, 219
STREAMS = {0: ("de2017", "ru1958"), 1: ("en1933", "en1974")}
W = {}


def columns(p):
    L = dl.lines(DJ, p)
    if not L:
        return [], [], []
    width = max(w[1] for l in L for w in l.words)
    mid = width / 2 + 40
    ys = sorted(l.y0 for l in L)
    hmed = statistics.median(l.h for l in L)
    cols = ([], [])
    notes = []
    for l in L:
        t = l.text.strip()
        if l is min(L, key=lambda z: z.y0) and re.search(r"Abhandlung|Tractat|трактат", t):
            continue                                   # колонтитул
        if re.fullmatch(r"\d{1,3}", t) and l.y0 > max(ys) - 30:
            continue                                   # номер страницы
        left = [w for w in l.words if (w[0] + w[1]) / 2 < mid]
        right = [w for w in l.words if (w[0] + w[1]) / 2 >= mid]
        for k, part in ((0, left), (1, right)):
            if part:
                ln = dl.Line(part, 0)
                (notes if ln.h < 0.78 * hmed and ln.y0 > ys[len(ys) * 2 // 3] else cols[k]).append(ln)
    return cols[0], cols[1], notes


def paragraphs(lines):
    if not lines:
        return []
    xs = sorted(l.x0 for l in lines)
    margin = xs[len(xs) // 10]
    out = []
    for l in sorted(lines, key=lambda z: z.y0):
        start = l.x0 - margin > 45 or re.match(r"^\s*[1-7I](?:\s?[.,]\s?\d+)*\s?[.,]?\s", l.text)
        if start or not out:
            out.append([l.text])
        else:
            out[-1].append(l.text)
    return out


res = {s: [] for pair in STREAMS.values() for s in pair}
notes = []
for p in range(FIRST, LAST + 1):
    a, b, n = columns(p)
    for k, col in enumerate((a, b)):
        for para in paragraphs(col):
            res[STREAMS[p % 2][k]].append({"page": p, "lines": para})
    if n:
        notes.append({"page": p, "lines": [l.text for l in sorted(n, key=lambda z: z.y0)]})
dl.save_cache(DJ)
json.dump({"streams": res, "notes": notes}, open(OUT, "w"), ensure_ascii=False, indent=0)
for s, v in res.items():
    print(s, "абзацев:", len(v))
