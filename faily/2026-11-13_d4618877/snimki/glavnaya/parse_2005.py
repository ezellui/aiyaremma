"""Извлечение «Трактата» из издания 2005 г. (пер. и комментарий В. Руднева,
«Избранные работы», Территория будущего).

Положения набраны жирным с номером в начале строки, параллельный комментарий —
обычным шрифтом сразу после положения (или после группы положений).
Дефис в шрифтах издания — управляющие символы \\x07/\\x1d, в курсиве — «'».
"""
import json, re, sys
import pymupdf
from pdfline import page_lines, render_spans, is_tabular, render_pre
from dehyph import Dehyph
import tlp_tree

PDF, OUT = sys.argv[1], sys.argv[2]
doc = pymupdf.open(PDF)
FIRST, LAST = 18, 221            # страницы PDF (= страницы книги) с положениями
NUMSTART = re.compile(r"^\s*([1-7](?:\.\d+)?)\s+(?=\S)")
dh = Dehyph()


def fix_spans(spans):
    out = []
    for s in spans:
        s = dict(s)
        t = s["text"].replace("\x07", "-").replace("\x1d", "-")
        if "Italic" in s["font"] or "A-Bold" in s["font"]:
            t = t.replace("'", "-")
        s["text"] = t
        out.append(s)
    return out


items = []   # последовательность: ("prop", num, paras) | ("comm", paras)
pre_title = []


def cur_paras(kind):
    return items[-1][-1]


def add(kind_line, text, new_para):
    paras = items[-1][-1]
    if kind_line == "pre":
        if paras and paras[-1]["kind"] == "pre":
            paras[-1]["lines"].append(text)
        else:
            paras.append({"kind": "pre", "lines": [text]})
        return
    if new_para or not paras or paras[-1]["kind"] == "pre":
        paras.append({"kind": "txt", "lines": [text]})
    else:
        paras[-1]["lines"].append(text)


for pno in range(FIRST - 1, LAST):
    ls = [l for l in page_lines(doc, pno) if l.text.strip()]
    ls = [l for l in ls if not (l.y0 < 50 and l.size < 8.6) and not (l.y0 > 595 and re.fullmatch(r"\s*\d+\s*", l.text))]
    for l in ls:
        l.spans = fix_spans(l.spans)
    main = [l for l in ls if l.size >= 9.4]
    margin = min((l.x0 for l in main), default=60)
    indent = margin + 14.2
    for l in ls:
        bold = l.bold()
        txt = l.text
        m = NUMSTART.match(txt)
        at_indent = abs(l.x0 - indent) < 2.5
        if bold and m and at_indent:
            r = render_spans(l.spans)
            r = re.sub(r"^\s*\**\s*[1-7](?:\.\d+)?\s+\**", "", r)
            items.append(["prop", m.group(1), l.page, []])
            add("txt", r, True)
            continue
        if not items:
            continue
        kind = "prop" if bold else "comm"
        if items[-1][0] != kind:
            if kind == "prop":
                # жирная строка без номера после комментария — не положение
                kind = "comm"
            else:
                items.append(["comm", None, l.page, []])
        if is_tabular(l, small=0):
            add("pre", render_pre(l, margin), False)
        else:
            add("txt", render_spans(l.spans), l.x0 > margin + 3)

for it in items:
    for p in it[-1]:
        if p["kind"] == "txt":
            for ln in p["lines"]:
                dh.learn(ln)

props, comments, order = {}, [], []
run = []
for kind, num, page, paras in items:
    text = "\n\n".join(dh.join_para(p) for p in paras)
    if kind == "prop":
        if num in props:
            print("ПОВТОР номера", num, "стр.", page)
        props[num] = text
        order.append(num)
        run.append(num)
    else:
        comments.append({"after": run[:] if run else [order[-1]], "page": page, "text": text})
        run = []

nums = sorted(props, key=tlp_tree.key)
print("положений:", len(props), "комментариев:", len(comments))
bad = [a for a, b in zip(order, order[1:]) if tlp_tree.key(a) >= tlp_tree.key(b)]
print("нарушений порядка:", bad[:20])
json.dump({"source": "2005", "props": props, "order": order, "comments": comments},
          open(OUT, "w"), ensure_ascii=False, indent=1)
