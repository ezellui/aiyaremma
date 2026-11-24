"""Подозрительные участки скана 1961 г. → regions61.json (сырьё для контактных листов).

В отличие от HWPh (решение на уникальную картинку-глиф) здесь решение принимается на участок
скана: одно-три слова строки или всё положение с формулами. Участок получает:
  key   — устойчивый ключ «ed:num:w:<ocr-слова>» или «ed:num:formula»;
  box   — страница и прямоугольник в пикселях pgm (1813×2900);
  ocr   — что прочёл tesseract; cur — что сейчас стоит в нашем тексте (после всех правок);
  why   — признаки: conf (уверенность tesseract < 60 и слова нет в словаре),
          wit (tesseract и слой IA расходятся), junk (не-буквенный мусор в слове),
          formula (положение с логическими знаками — сверяется целиком).

    python3 regions61.py ../ocr lp1961.json regions61.json
"""
import json, os, re, sys, difflib, unicodedata
from spellchecker import SpellChecker

OCR, LP, OUT = sys.argv[1:4]
W = os.path.dirname(os.path.abspath(__file__))
lp = json.load(open(LP))
wit = json.load(open(f"{W}/witness61.json"))
canon = json.load(open(f"{W}/canon.json"))
WORD = re.compile(r"[^\W_]+(?:[-’'][^\W_]+)*")
FORMULA = re.compile(r"[~⊃∨≡ξηΩ]|\(p|p\)|\bp\s*\.|\bq\b|\$")
NORM = {"de": "tlp_de_1961", "en": "tlp_en_1961_ogden"}
ED = {"de": "de1961", "en": "en1961"}


def fold(s):
    s = unicodedata.normalize("NFD", s.replace("ß", "ss"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def page_words(pg):
    out = []
    p = f"{OCR}/pg-{pg:03d}.tsv"
    if not os.path.exists(p):
        return out
    for ln in open(p, encoding="utf-8").read().splitlines()[1:]:
        f = ln.split("\t")
        if len(f) >= 12 and f[0] == "5" and f[11].strip():
            out.append({"line": (int(f[2]), int(f[3]), int(f[4])), "x": int(f[6]), "y": int(f[7]),
                        "w": int(f[8]), "h": int(f[9]), "conf": float(f[10]), "t": f[11]})
    return out


def owner_words(lang):
    """Слова OCR, разложенные по положениям (по координатам начала положений)."""
    starts = sorted((p, y, n) for n, (p, y) in lp[lang]["loc"].items())
    byp = {}
    pages = sorted({p for p, _, _ in starts})
    pages = list(range(pages[0], pages[-1] + 3, 2))
    cur = None
    for pg in pages:
        here = [(y, n) for p, y, n in starts if p == pg]
        for wd in sorted(page_words(pg), key=lambda w: (w["y"] // 25, w["x"])):
            if wd["y"] < 200 or wd["y"] > 2700:      # колонтитулы и номер страницы
                continue
            o = cur
            for y, n in here:
                if wd["y"] + wd["h"] / 2 >= y - 15:
                    o = n
            if o is None:
                continue
            wd["page"] = pg
            byp.setdefault(o, []).append(wd)
        if here:
            cur = max(here)[1]
    return byp


def tokens(text):
    clean = re.sub(r"```.*?```|\$[^$]*\$|!\[\]\([^)]*\)|\[\^[^\]]*\]", lambda m: " " * len(m.group()), text, flags=re.S)
    return [(m.start(), m.end(), m.group()) for m in WORD.finditer(clean)]


def main():
    res = []
    for lang in ("de", "en"):
        sp = SpellChecker(language=lang)
        props = json.load(open(f"{W}/norm_{NORM[lang]}.json"))["props"]
        freq = {}
        for t in props.values():
            for _, _, w in tokens(t):
                freq[fold(w)] = freq.get(fold(w), 0) + 1

        def known(w):
            f = fold(w)
            parts = re.split(r"[-’']", f)
            return all(p in sp or freq.get(p, 0) >= 3 or len(p) <= 1 or p.isdigit() for p in parts)

        byp = owner_words(lang)
        for num in canon:
            text = props[num]
            ws = byp.get(num, [])
            toks = tokens(text)
            # выравнивание слов OCR и слов нашего текста
            ow = []
            for i, wd in enumerate(ws):
                for m in WORD.finditer(wd["t"]):
                    ow.append((i, m.group()))
            sm = difflib.SequenceMatcher(None, [fold(w) for _, w in ow], [fold(t[2]) for t in toks], autojunk=False)
            o2t = {}
            for tag, a1, a2, b1, b2 in sm.get_opcodes():
                for k in range(a1, a2):
                    if tag == "equal":
                        o2t[k] = (b1 + k - a1, b1 + k - a1)
                    elif b2 > b1:
                        j = b1 + min(k - a1, b2 - b1 - 1)
                        o2t[k] = (j, j) if tag == "replace" and (a2 - a1) == (b2 - b1) else (b1, b2 - 1)
            bad = set(wit[lang]["bad_by_page"].get(str(lp[lang]["loc"][num][0]), [])) | \
                  set(wit[lang]["bad_by_page"].get(str(lp[lang]["loc"][num][0] + 2), []))
            flagged = []
            for k, (i, w) in enumerate(ow):
                wd = ws[i]
                why = []
                if k in o2t:
                    a, b = o2t[k]
                    cur = text[toks[a][0]:toks[b][1]]
                else:
                    cur = None
                if re.search(r"[^\w\s.,;:!?„“”‚‘’'»«()\-–—]", wd["t"]) and not FORMULA.search(text):
                    why.append("junk")
                if wd["conf"] < 60 and (cur is None or not all(known(x) for x in WORD.findall(cur))):
                    why.append("conf")
                if fold(w) in bad and (cur is None or not known(cur)):
                    why.append("wit")
                if cur is None and wd["conf"] < 80:
                    why.append("lost")
                if why:
                    flagged.append((k, i, why))
            # склеить соседние слова одной строки
            groups = []
            for k, i, why in flagged:
                if groups and k - groups[-1]["k2"] <= 2 and ws[i]["line"] == ws[groups[-1]["i2"]]["line"]:
                    g = groups[-1]; g["k2"] = k; g["i2"] = i; g["why"] |= set(why)
                else:
                    groups.append({"k1": k, "k2": k, "i1": i, "i2": i, "why": set(why)})
            for g in groups:
                w1, w2 = ws[g["i1"]], ws[g["i2"]]
                line = [wd for wd in ws if wd["line"] == w1["line"] and wd["page"] == w1["page"]]
                x1 = min(wd["x"] for wd in line); x2 = max(wd["x"] + wd["w"] for wd in line)
                y1 = min(wd["y"] for wd in line); y2 = max(wd["y"] + wd["h"] for wd in line)
                spans = [o2t[k] for k in range(g["k1"], g["k2"] + 1) if k in o2t]
                if spans:
                    a = max(0, min(s[0] for s in spans) - 1); b = min(len(toks) - 1, max(s[1] for s in spans) + 1)
                    ctx = text[toks[a][0]:toks[b][1]]
                    a0 = min(s[0] for s in spans); b0 = max(s[1] for s in spans)
                    cur = text[toks[a0][0]:toks[b0][1]]
                else:
                    ctx = cur = ""
                ocr = " ".join(ws[i]["t"] for i in range(g["i1"], g["i2"] + 1))
                res.append({"key": f"{ED[lang]}:{num}:w:{ocr}", "ed": ED[lang], "lang": lang, "num": num,
                            "kind": "word", "page": w1["page"],
                            "box": [max(0, x1 - 10), max(0, y1 - 12), x2 + 10, y2 + 12],
                            "hl": [w1["x"] - 4, w2["x"] + w2["w"] + 4],
                            "ocr": ocr, "cur": cur, "ctx": ctx,
                            "conf": round(min(ws[i]["conf"] for i in range(g["i1"], g["i2"] + 1))),
                            "why": sorted(g["why"])})
            if FORMULA.search(text):
                res.append({"key": f"{ED[lang]}:{num}:formula", "ed": ED[lang], "lang": lang, "num": num,
                            "kind": "formula", "page": lp[lang]["loc"][num][0], "cur": text, "why": ["formula"]})
    json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=0)
    from collections import Counter
    for lang in ("de", "en"):
        rr = [r for r in res if r["lang"] == lang]
        c = Counter(w for r in rr for w in r["why"])
        print(lang, "участков:", len(rr), dict(c))


main()
