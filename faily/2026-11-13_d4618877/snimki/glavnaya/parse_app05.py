"""Аппарат издания 2005 г.: «Литература» к комментарию В. Руднева (стр. книги 222–228).
→ app_ru2005.json

    python3 parse_app05.py "<PDF 2005>" app_ru2005.json
Остальные работы сборника (Коричневая и Голубая книги, лекции, биография) — не «Трактат»,
в читалку не берутся.
"""
import json, re, sys
import pymupdf
from pdfline import page_lines, render_spans
from dehyph import Dehyph

PDF, OUT = sys.argv[1:3]
doc = pymupdf.open(PDF)
dh = Dehyph()
norm = json.load(open("norm_tlp_ru_2005_rudnev.json"))
for t in list(norm["props"].values()) + [c["text"] for c in norm.get("comments", [])]:
    for ln in t.split("\n"):
        dh.learn(ln)

entries, abbrev, section = [], [], "list"
for pno in range(221, 228):
    ls = [l for l in page_lines(doc, pno) if l.text.strip()]
    ls = [l for l in ls if not re.fullmatch(r"\d{3}", l.text.strip())]
    if not ls:
        continue
    margin = min(l.x0 for l in ls if l.size > 10.2)
    for l in ls:
        t = l.text.strip()
        if t == "ЛИТЕРАТУРА":
            continue
        if t == "Принятые сокращения":
            section = "abbr"; continue
        r = render_spans(l.spans).replace("�", "-")
        r = re.sub(r"\*([.,;:])\*", r"\1", r).strip()
        if section == "abbr" and not r.startswith("*"):
            abbrev.append(r); continue
        section = "list"
        if l.x0 > margin + 6 and entries:
            entries[-1].append(r)
        else:
            entries.append([r])
items = [re.sub(r"\*\s*\*", " ", dh.join(e)).replace("  ", " ") for e in entries]
json.dump({"abbrev": abbrev, "items": items}, open(OUT, "w"), ensure_ascii=False, indent=1)
print("сокращений:", len(abbrev), "; работ:", len(items))
for x in items[:4] + items[-4:]:
    print("  ", x)
