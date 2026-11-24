"""Извлечение немецкого текста и английского перевода (Огден/Рамсей, 1922) из
двуязычного издания Routledge & Kegan Paul (1961, скан Internet Archive).

Текстовый слой скана (Courier, OCR Internet Archive) слишком плох: умлауты
потеряны, номера искажены. Поэтому страницы перераспознаны tesseract (300 dpi;
чётные — deu, нечётные — eng), а номера положений восстановлены выравниванием
по каноническому списку из 526 номеров: порядок положений в издании строго
возрастающий, поэтому i-е найденное начало положения = i-й номер канона.
"""
import json, re, sys, glob, statistics, difflib
from dehyph import Dehyph
import tlp_tree

OCR_DIR, CANON, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
canon = json.load(open(CANON))
FIRST, LAST = 30, 189     # страницы с положениями (немецкий — чётные)


def words(page):
    ws = []
    for ln in open(f"{OCR_DIR}/pg-{page:03d}.tsv", encoding="utf-8").read().splitlines()[1:]:
        f = ln.split("\t")
        if len(f) < 12 or f[0] != "5" or not f[11].strip():
            continue
        x, y, w, h = map(int, f[6:10])
        ws.append({"x": x, "y": y, "w": w, "h": h, "t": f[11], "c": float(f[10])})
    return ws


def vlines(ws):
    """Слова -> визуальные строки (по пересечению по вертикали)."""
    ws = sorted(ws, key=lambda w: w["y"] + w["h"] / 2)
    lines = []
    for w in ws:
        cy = w["y"] + w["h"] / 2
        if lines and abs(lines[-1]["cy"] - cy) < 22:
            L = lines[-1]
            L["ws"].append(w)
            L["cy"] = statistics.mean(v["y"] + v["h"] / 2 for v in L["ws"])
        else:
            lines.append({"cy": cy, "ws": [w]})
    for L in lines:
        L["ws"].sort(key=lambda w: w["x"])
        L["x"] = L["ws"][0]["x"]
        L["h"] = statistics.median(w["h"] for w in L["ws"])
        L["text"] = " ".join(w["t"] for w in L["ws"])
    return lines


NUMLIKE = re.compile(r"^[\dIiLlOoSsZz\-—_.,:;'*^|!?tTJjf]{1,9}\*?$")


def looks_num(tok):
    return bool(NUMLIKE.match(tok)) and any(ch.isdigit() or ch in "IilLoO" for ch in tok)


def norm_num(tok):
    t = tok.strip("_—-*:;,'")
    tr = str.maketrans({"I": "1", "i": "1", "l": "1", "L": "1", "O": "0", "o": "0",
                        "S": "5", "s": "5", "Z": "2", "z": "2", "-": ".", ",": ".",
                        "|": "1", "!": "1", "t": "1", "T": "1", "J": "1", "j": "1", "f": "1"})
    return t.translate(tr)


def parse_lang(pages):
    items = []     # [num_ocr, page, paras]
    notes = []     # [(page, text)]
    for pg in pages:
        ls = vlines(words(pg))
        if not ls:
            continue
        # колонтитул сверху, номер страницы снизу
        if ls and re.search(r"ABHANDLUNG|PHILOSOPHICUS|TRACTATUS|LOGISCH", ls[0]["text"]):
            ls = ls[1:]
        while ls and re.fullmatch(r"[\W\d]{1,6}( \w{1,3})?", ls[-1]["text"]) and len(ls[-1]["text"]) < 12:
            ls = ls[:-1]
        body_h = statistics.median(L["h"] for L in ls) if ls else 50
        # подстрочные сноски: мелкий кегль внизу, начиная со «*»
        cut = None
        for i, L in enumerate(ls):
            if i > len(ls) / 2 and L["h"] < body_h * 0.86 and L["text"].lstrip().startswith(("*", "+", "t ", "f ")):
                cut = i
                break
        if cut is not None:
            nt = " ".join(L["text"] for L in ls[cut:])
            notes.append((pg, nt))
            ls = ls[:cut]
        starts = sorted(L["x"] for L in ls)
        # x продолжения строк — самый частый левый край
        cont = statistics.mode([round(x / 15) * 15 for x in starts]) if starts else 300
        for L in ls:
            first = L["ws"][0]
            rest = L["ws"][1:]
            is_num = (first["x"] < cont - 60 and looks_num(first["t"]) and
                      (not rest or rest[0]["x"] - (first["x"] + first["w"]) > 40))
            if is_num:
                txt = " ".join(w["t"] for w in rest)
                items.append([first["t"], pg, [[txt]] if txt else []])
                continue
            if not items:
                continue
            # таблица/схема: широкие разрывы между словами
            gaps = [b["x"] - (a["x"] + a["w"]) for a, b in zip(L["ws"], L["ws"][1:])]
            tab = gaps and max(gaps) > 120 and len(L["text"]) < 70
            paras = items[-1][2]
            if tab:
                col0 = cont
                s = ""
                for w in L["ws"]:
                    c = max(0, (w["x"] - col0) // 21)
                    s = s + (" " * (c - len(s)) if len(s) < c else " ") + w["t"]
                if paras and paras[-1] and paras[-1][0].startswith("\x00PRE"):
                    paras[-1].append(s.rstrip())
                else:
                    paras.append(["\x00PRE", s.rstrip()])
                continue
            new_para = L["x"] > cont + 40
            if new_para or not paras or paras[-1][0].startswith("\x00PRE"):
                paras.append([L["text"]])
            else:
                paras[-1].append(L["text"])
    return items, notes


def assign(items, lang):
    """Сопоставить найденные начала положений каноническим номерам."""
    ocr = [norm_num(it[0]) for it in items]
    print(lang, "найдено начал:", len(items), "канон:", len(canon))
    sm = difflib.SequenceMatcher(a=ocr, b=canon, autojunk=False)
    mapping = {}
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal" or (op == "replace" and a2 - a1 == b2 - b1):
            for i in range(a2 - a1):
                mapping[a1 + i] = canon[b1 + i]
        else:
            print("  ", op, [items[i][0] for i in range(a1, a2)], "->", canon[b1:b2],
                  "стр.", [items[i][1] for i in range(a1, a2)])
            if op == "replace":   # число не совпало: сшиваем по порядку, лишнее — в текст
                for i in range(min(a2 - a1, b2 - b1)):
                    mapping[a1 + i] = canon[b1 + i]
    return mapping


def build(items, mapping, dh):
    props, last = {}, None
    for i, (tok, pg, paras) in enumerate(items):
        if i in mapping:
            last = mapping[i]
            props[last] = paras
        elif last:
            # ложное «начало» — вернуть в текст предыдущего положения
            props[last].append([tok] + (paras[0] if paras else []))
            props[last].extend(paras[1:])
    for k, paras in props.items():
        for p in paras:
            if p and not p[0].startswith("\x00PRE"):
                for ln in p:
                    dh.learn(ln)
    out = {}
    for k, paras in props.items():
        ps = []
        for p in paras:
            if not p:
                continue
            if p[0].startswith("\x00PRE"):
                ps.append("```\n" + "\n".join(p[1:]) + "\n```")
            else:
                ps.append(dh.join(p))
        out[k] = "\n\n".join(ps)
    return out


def front(pages):
    paras = []
    for pg in pages:
        ls = vlines(words(pg))
        if ls and re.search(r"ABHANDLUNG|PHILOSOPHICUS|TRACTATUS|LOGISCH", ls[0]["text"]):
            ls = ls[1:]
        while ls and re.fullmatch(r"[\W\d]{1,6}", ls[-1]["text"]):
            ls = ls[:-1]
        cont = statistics.mode([round(L["x"] / 15) * 15 for L in ls]) if ls else 300
        for L in ls:
            if not paras or L["x"] > cont + 40:
                paras.append([L["text"]])
            else:
                paras[-1].append(L["text"])
    return paras


res = {}
for lang, pages in (("de", range(FIRST, LAST + 1, 2)), ("en", range(FIRST + 1, LAST + 1, 2))):
    items, notes = parse_lang(pages)
    mapping = assign(items, lang)
    dh = Dehyph()
    props = build(items, mapping, dh)
    pf = front([26, 28] if lang == "de" else [27, 29])
    res[lang] = {"props": props, "notes": notes,
                 "front_raw": [dh.join(p) for p in pf]}
    print(lang, "положений:", len(props), "сносок:", notes)
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
