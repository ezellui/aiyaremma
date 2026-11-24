"""Извлечение «Трактата» из издания 2023 г. (пер. К. Королева, КоЛибри).

В PDF: стр. 40 — корневой блок 1–7; стр. 41–146 — дерево; дальше «ПРИМЕЧАНИЯ».
Повторы узлов (заголовки ветвей) набраны жирным, члены ветвей — обычным.
Канонический текст положения берётся из его вхождения членом ветви (оно ровно одно);
сноски, стоящие только в жирных повторах, переносятся в канонический текст.
"""
import json, re, sys
import pymupdf
from pdfline import page_lines, render_spans
from dehyph import Dehyph
import tlp_tree

PDF = sys.argv[1]
OUT = sys.argv[2]
doc = pymupdf.open(PDF)

NUMLINE = re.compile(r"^\s*([1-7](?:\.\d+)?)\.\s*")
SECTION = re.compile(r"^\s*([1-7])\.\s*$")

entries = []      # {num, role, paras:[[line,...],...], page}
page_notes = {}   # page -> [text]
dh = Dehyph()


def body_lines(pno):
    ls = [l for l in page_lines(doc, pno) if l.text.strip()]
    ls = [l for l in ls if not (abs(l.size - 9.0) < 0.3 and (l.y0 < 55 or l.y0 > 525))]
    # подстраничные сноски: от первой строки мелкого кегля, начинающейся со «*»
    notes, body, in_note = [], [], False
    for l in ls:
        if not in_note and l.size < 9 and l.text.lstrip().startswith("*") and l.y0 > 250:
            in_note = True
        (notes if in_note else body).append(l)
    return body, notes


stop = False
for pno in range(39, 160):
    body, notes = body_lines(pno)
    if notes:
        nt = []
        for l in notes:
            t = render_spans(l.spans)
            if t.lstrip().startswith("*") or not nt:
                nt.append([t])
            else:
                nt[-1].append(t)
        page_notes[pno + 1] = nt
    main = [l for l in body if abs(l.size - 10.1) < 0.5]
    margin = min((l.x0 for l in main), default=40)
    indent = margin + 14.1
    i = 0
    while i < len(body):
        l = body[i]
        txt = l.text
        if txt.strip() == "ПРИМЕЧАНИЯ":
            stop = True
            break
        m_sec = SECTION.match(txt)
        if m_sec and l.bold() and l.x0 > indent + 40:
            head = []
            j = i + 1
            while j < len(body) and body[j].bold() and body[j].x0 > indent + 5:
                head.append(render_spans(body[j].spans))
                j += 1
            entries.append({"num": m_sec.group(1), "role": "section",
                            "paras": [head], "page": l.page})
            i = j
            continue
        m = NUMLINE.match(txt)
        if m and abs(l.x0 - indent) < 3 and not (pno == 39 and False):
            role = "head" if l.bold() else "member"
            r = render_spans(l.spans)
            r = re.sub(r"^\s*\**\s*[1-7](?:\.\d+)?\.\s*\**\s*", "", r)
            if l.bold():
                r = r.replace("*", "")  # курсив в повторе нам не нужен
            entries.append({"num": m.group(1), "role": role, "paras": [[r]], "page": l.page})
        elif pno == 39 and m and abs(l.x0 - margin) < 3:
            # корневой блок 1–7 набран без абзацного отступа
            entries.append({"num": m.group(1), "role": "member",
                            "paras": [[re.sub(r"^\s*[1-7]\.\s*", "", render_spans(l.spans))]],
                            "page": l.page})
        else:
            if not entries:
                i += 1
                continue
            r = render_spans(l.spans)
            e = entries[-1]
            new_para = (l.x0 > margin + 3) and not (pno == 39)
            if pno == 39 and l.x0 > margin + 3 and e["paras"][-1] and \
                    e["paras"][-1][-1].rstrip().endswith((".", ")")):
                new_para = True
            if new_para:
                e["paras"].append([r])
            else:
                e["paras"][-1].append(r)
        i += 1
    if stop:
        break

for e in entries:
    for p in e["paras"]:
        for ln in p:
            dh.learn(ln)

for e in entries:
    e["text"] = "\n\n".join(dh.join(p) for p in e["paras"] if p)

# --- сверка порядка с алгоритмом дерева
members = [e["num"] for e in entries if e["role"] == "member"]
nums = sorted(set(members), key=tlp_tree.key)
exp = tlp_tree.expected_sequence(nums)
got = [(e["num"], e["role"]) for e in entries]
ok = exp == got
print("положений-членов:", len(members), "уникальных:", len(nums))
print("порядок совпадает с алгоритмом:", ok)
if not ok:
    for k, (a, b) in enumerate(zip(exp, got)):
        if a != b:
            print("расхождение на", k, a, b, got[k - 3:k + 3])
            break
    print(len(exp), len(got))

# --- сноски: перенести номера сносок из повторов в каноническое вхождение
FN = re.compile(r"\[\^(\d+|\*+)\]")
canon = {}
for e in entries:
    if e["role"] == "member":
        canon[e["num"]] = e["text"]
moved = 0
for e in entries:
    if e["role"] in ("head", "section"):
        for m in FN.finditer(e["text"]):
            tag = m.group(0)
            c = canon.get(e["num"])
            if c is None or tag in c:
                continue
            before = FN.sub("", e["text"][: m.start()])
            ctx = re.sub(r"\W+", " ", before).split()[-3:]
            pos = None
            if ctx:
                pat = r"\W+".join(map(re.escape, ctx))
                mm = list(re.finditer(pat, FN.sub(lambda x: "\x00" * len(x.group(0)), c)))
                if mm:
                    pos = mm[0].end()
                    while pos < len(c) and c[pos] in ".,;:»)!?":
                        pos += 0
                        break
            if pos is None:
                pos = len(c)
            canon[e["num"]] = c[:pos] + tag + c[pos:]
            moved += 1
print("сносок перенесено из повторов:", moved)

json.dump({"source": "2023", "props": canon, "page_notes": page_notes,
           "entries": [{k: e[k] for k in ("num", "role", "page", "text")} for e in entries]},
          open(OUT, "w"), ensure_ascii=False, indent=1)
