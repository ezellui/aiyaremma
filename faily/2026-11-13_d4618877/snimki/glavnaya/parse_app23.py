"""Аппарат издания 2023 г. (К. Королев): статья, «О составе сборника», текстологическое
замечание, «Логическое дерево „Трактата“» со схемой. → app_ru2023.json

    python3 parse_app23.py "<PDF 2023>" app_ru2023.json figs/src
Подстраничные сноски «*», «**»… получают метки вида [^s7-2] (раздел, страница PDF, номер на странице).
Схема логического дерева (векторная, стр. PDF 34) сохраняется как figs/src/ru2023-logtree.svg.
"""
import json, re, sys
import pymupdf
from pdfline import page_lines, render_spans
from dehyph import Dehyph

PDF, OUT, FIGSRC = sys.argv[1:4]
doc = pymupdf.open(PDF)
dh = Dehyph()
STAR = re.compile(r"((?:\[\^\*\])+)")

# (id, заглавие, страницы PDF с 0, начало, конец)
SECTIONS = [
    ("article", "К. Королев. Людвиг «великий и ужасный» и его «Трактат»", range(5, 25), "Людвиг «великий", None),
    ("composition", "О составе сборника", range(25, 27), "О составе сборника", None),
    ("textology", "Текстологическое замечание о принципах перевода", range(29, 32), "Текстологическое замечание", "Логическое дерево"),
    ("logtree", "Логическое дерево «Трактата»", range(32, 34), "Логическое дерево", None),
]


def section(sid, pages, start, stop):
    paras, notes, started, cur_note = [], {}, False, None
    for pno in pages:
        ls = [l for l in page_lines(doc, pno) if l.text.strip()]
        ls = [l for l in ls if not (abs(l.size - 9.0) < 0.3 and (l.y0 < 55 or l.y0 > 525))]   # колонтитулы
        body = [l for l in ls if l.size > 9.5]
        small = [l for l in ls if l.size <= 9.5]
        if not body and not small:
            continue
        margin = min((l.x0 for l in body), default=40)
        k = 0
        first = True
        for l in body:
            t = l.text.strip()
            if not started:
                if start in t:
                    started = True
                continue
            if stop and stop in t:
                return paras, notes
            if l.size > 10.4 or "FreeSet" in l.spans[0]["font"]:   # подзаголовок/хвост заглавия
                if not paras:
                    continue
            r = render_spans(l.spans)
            if re.fullmatch(r"(?:\[\^\*\]\s*){3}", r.strip()):
                paras.append(["⁂"]); first = False
                continue

            def lab(m):
                nonlocal k
                k += 1
                return f"[^{sid[0]}{pno + 1}-{m.group(1).count('*')}]"
            r = STAR.sub(lab, r)
            if not paras or (l.x0 > margin + 3) or paras[-1] == ["⁂"]:
                paras.append([r])
            else:
                paras[-1].append(r)
            first = False
        if not started:
            continue
        for l in small:
            r = render_spans(l.spans)
            m = re.match(r"\s*((?:\[\^\*\])+)\s*", r)
            if m:
                cur_note = f"{sid[0]}{pno + 1}-{m.group(1).count('*')}"
                notes[cur_note] = [r[m.end():]]
            elif cur_note:
                notes[cur_note].append(r)
    return paras, notes


out = []
for sid, title, pages, start, stop in SECTIONS:
    paras, notes = section(sid, pages, start, stop)
    text = "\n\n".join(dh.join(p) for p in paras)
    if sid == "logtree":
        text += "\n\n![](fig:logtree)"
    out.append({"id": sid, "title": title, "text": text,
                "notes": {k: dh.join(v) for k, v in notes.items()},
                "pages": [pages[0] + 1, pages[-1] + 1]})
    print(sid, len(paras), "абзацев,", len(notes), "сносок,", len(text), "зн.")

# схема логического дерева: вектор, обрезанный по рисунку
pg = doc[33]
r = pymupdf.Rect()
for d in pg.get_drawings():
    r |= d["rect"]
for b in pg.get_text("dict")["blocks"]:
    r |= pymupdf.Rect(b["bbox"])
pg.set_cropbox(r + (-4, -4, 4, 4))
svg = pg.get_svg_image(text_as_path=True)
open(f"{FIGSRC}/ru2023-logtree.svg", "w").write(svg)
print("схема дерева:", round(r.width), "×", round(r.height), "pt,", len(svg) // 1024, "КБ")
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
