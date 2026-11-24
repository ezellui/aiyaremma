"""Единый набор схем трактата в SVG: один чертёж на схему, подписи — по языку редакции.

Чертежи 5.6331 и 6.1203 a–d во всех изданиях одни и те же (это схемы самого Витгенштейна);
различаются только подписи: W/F (нем.), T/F (англ.), И/Л (рус.), «Auge/Eye/Глаз».
Геометрия берётся из векторных рисунков издания 2005 г. (там они набраны путями PDF,
а подписи — текстом), подписи ставятся заново из таблицы LABELS. Схема «~ξ» (6.1203tilde)
и рисунки 1961 г. 5.5423 и 6.36111 нарисованы вручную.

    python3 figsvg.py "<PDF 2005>" figs/src      # шаблоны figs/src/<name>.svg с метками {T} {F} {EYE} {Q1} {Q2}
    python3 figsvg.py --render figs/src figs     # редакции: figs/<ed>-<name>.svg
"""
import os, re, sys

LABELS = {
    "de1961": {"T": "W", "F": "F", "EYE": "Auge", "Q1": "„", "Q2": "“", "font": "italic"},
    "en1961": {"T": "T", "F": "F", "EYE": "Eye", "Q1": "“", "Q2": "”", "font": "italic"},
    "ru2005": {"T": "И", "F": "Л", "EYE": "Глаз", "Q1": "«", "Q2": "»", "font": "italic"},
    "ru2023": {"T": "И", "F": "Л", "EYE": "Глаз", "Q1": "«", "Q2": "»", "font": "italic"},
}
# какие схемы есть в какой редакции (5.5423 и 6.36111 — только в 1961: в переводах их нет)
HAS = {"5.6331": "*", "6.1203a": "*", "6.1203b": "*", "6.1203c": "*", "6.1203d": "*",
       "6.1203tilde": "*", "5.5423": "de1961 en1961", "6.36111": "de1961 en1961"}
PX = 110 / 72          # пункт PDF → css-пиксель (размер как в книге при 110 px на дюйм)
FONT = "Georgia,'Times New Roman',serif"

# рамки рисунков в PDF 2005 г.: (страница с 1, прямоугольник в пунктах)
BOXES = {"5.6331": (183, (60, 495, 400, 598)), "6.1203a": (189, (60, 314, 400, 404)),
         "6.1203b": (189, (60, 453, 400, 561)), "6.1203c": (190, (72, 194, 413, 303)),
         "6.1203d": (190, (73, 331, 413, 465))}


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def extract(pdf, out):
    import pymupdf
    doc = pymupdf.open(pdf)
    os.makedirs(out, exist_ok=True)
    for name, (pno, box) in BOXES.items():
        pg = doc[pno - 1]
        R = pymupdf.Rect(box)
        paths, xs, ys = [], [], []
        for d in pg.get_drawings():
            r = d["rect"]
            if not R.contains(r) and not R.intersects(r):
                continue
            if len(d["items"]) == 1 and r.width > 300:          # фон рамки
                continue
            seg = []
            for it in d["items"]:
                k = it[0]
                if k == "l":
                    seg.append(("M", it[1])); seg.append(("L", it[2]))
                elif k == "c":
                    seg.append(("M", it[1])); seg.append(("C", it[2], it[3], it[4]))
                elif k == "re":
                    q = it[1]; seg += [("M", q.tl), ("L", q.tr), ("L", q.br), ("L", q.bl), ("Z",)]
                elif k == "qu":
                    q = it[1]; seg += [("M", q.ul), ("L", q.ur), ("L", q.lr), ("L", q.ll), ("Z",)]
            paths.append((d, seg))
            xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
        texts = []
        for b in pg.get_text("rawdict", clip=R)["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    word = "".join(c["c"] for c in s["chars"])
                    if "Глаз" in word:
                        c0 = s["chars"][0]
                        dash = [c for c in s["chars"] if c["c"] == "—"][0]
                        texts.append((dash["origin"][0] - 1.5, c0["origin"][1], "{EYE}", "end", s["size"]))
                        texts.append((dash["origin"][0], dash["origin"][1], "—", "start", s["size"]))
                        xs.append(c0["bbox"][0] - 12)
                        continue
                    for c in s["chars"]:
                        ch = c["c"]
                        if not ch.strip():
                            continue
                        ch = {"И": "{T}", "Л": "{F}"}.get(ch, ch)
                        texts.append((c["origin"][0], c["origin"][1], ch, "start", s["size"]))
                        xs += [c["bbox"][0], c["bbox"][2]]; ys += [c["bbox"][1], c["bbox"][3]]
        x0, y0, x1, y1 = min(xs) - 3, min(ys) - 3, max(xs) + 3, max(ys) + 3
        P = lambda p: f"{f(p.x - x0)} {f(p.y - y0)}"
        body = []
        for d, seg in paths:
            dd = " ".join(t[0] + (" " + " ".join(P(p) for p in t[1:]) if len(t) > 1 else "") for t in seg)
            fill = "#000" if d.get("fill") is not None and d["type"] in ("f", "fs") else "none"
            stroke = "#000" if d["type"] in ("s", "fs") else "none"
            sw = f' stroke-width="{f(d.get("width") or 0.5)}"' if stroke != "none" else ""
            body.append(f'<path d="{dd}" fill="{fill}" stroke="{stroke}"{sw}/>')
        for x, y, ch, anchor, size in texts:
            # подписи-буквы И/Л в 2005 г. — курсив; символы ξ η — прямые
            st = ' font-style="{font}"' if ch in ("{T}", "{F}", "{EYE}", "p", "q", "r") else ""
            an = ' text-anchor="end"' if anchor == "end" else ""
            body.append(f'<text x="{f(x - x0)}" y="{f(y - y0)}" font-size="{f(size)}"{st}{an}>{ch}</text>')
        w, h = x1 - x0, y1 - y0
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{round(w * PX)}" height="{round(h * PX)}" '
               f'viewBox="0 0 {f(w)} {f(h)}" font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>\n")
        open(f"{out}/{name}.svg", "w").write(svg)
        print(name, round(w), "×", round(h), "pt,", len(paths), "путей,", len(texts), "подписей")
    # «~ξ» в записи 6.1203: T над, «TξF» посередине, F под, со штрихами
    tilde = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{round(62 * PX)}" height="{round(52 * PX)}" viewBox="0 0 62 52" font-family="{FONT}">
<g stroke="#000" stroke-width="0.6"><line x1="17" y1="11" x2="25" y2="19"/><line x1="40" y1="33" x2="47" y2="41"/></g>
<g font-size="10"><text x="11" y="10" font-style="{{font}}">{{T}}</text>
<text x="2" y="30">{{Q1}}<tspan font-style="{{font}}">{{T}}</tspan> ξ <tspan font-style="{{font}}">{{F}}</tspan>{{Q2}}</text>
<text x="46" y="50" font-style="{{font}}">{{F}}</text></g>
</svg>
'''
    open(f"{out}/6.1203tilde.svg", "w").write(tilde)


def render(src, out):
    n = 0
    for f_ in sorted(os.listdir(src)):
        if not f_.endswith(".svg"):
            continue
        name = f_[:-4]
        tpl = open(f"{src}/{f_}").read()
        for ed, lab in LABELS.items():
            if HAS.get(name, "*") != "*" and ed not in HAS[name].split():
                continue
            s = re.sub(r"\{(\w+)\}", lambda m: lab.get(m.group(1), m.group(0)), tpl)
            open(f"{out}/{ed}-{name}.svg", "w").write(s)
            n += 1
    print(n, "файлов SVG в", out)


if __name__ == "__main__":
    if sys.argv[1] == "--render":
        render(sys.argv[2], sys.argv[3])
    else:
        extract(sys.argv[1], sys.argv[2])
