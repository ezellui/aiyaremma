"""Аппарат издания 1961 г. (Routledge, Ogden): заметка издателя, введение Б. Рассела, указатель.
→ app_1961.json

    # растр и OCR (один раз):  страницы PDF 5, 7–23 — целиком; 191–207 — по столбцам
    python3 parse_app61.py ../ocr_app app_1961.json

Введение: абзацы по отступу первой строки (TSV tesseract), перенос слов склеивается.
Указатель: два столбца; строка с наименьшим отступом — заглавное слово, следующий отступ —
подрубрика, ещё больший — продолжение строки. Номера положений приводятся к канону
(старинные цифры: I → 1, o → 0, дефис → точка) и проверяются по нему.
"""
import json, os, re, sys
from collections import defaultdict

SRC, OUT = sys.argv[1:3]
W = os.path.dirname(os.path.abspath(__file__))
canon = set(json.load(open(f"{W}/canon.json")))


def lines(path):
    """[(x, y, h, text)] — строки TSV в порядке чтения."""
    L = defaultdict(list)
    for ln in open(path, encoding="utf-8").read().splitlines()[1:]:
        f = ln.split("\t")
        if len(f) >= 12 and f[0] == "5" and f[11].strip():
            L[(int(f[2]), int(f[3]), int(f[4]))].append((int(f[6]), int(f[7]), int(f[8]), int(f[9]), f[11]))
    out = []
    for k, ws in L.items():
        ws.sort()
        out.append((ws[0][0], min(w[1] for w in ws), max(w[3] for w in ws), " ".join(w[4] for w in ws)))
    out.sort(key=lambda t: t[1])
    return out


def join_lines(ls):
    s = ""
    for t in ls:
        if s.endswith("-") and t[:1].islower():
            s = s[:-1] + t
        else:
            s = (s + " " + t) if s else t
    return re.sub(r"\s+", " ", s).strip()


def prose(pages, head):
    paras, cur = [], []
    for p in pages:
        ls = [l for l in lines(f"{SRC}/pg-{p:03d}.tsv") if 150 < l[1] < 2700]
        ls = [l for l in ls if l[3].strip() not in (head,) and not re.fullmatch(r"[\dIlqo]{1,3}", l[3].strip())]
        if not ls:
            continue
        margin = sorted(l[0] for l in ls)[len(ls) // 4]
        for x, y, h, t in ls:
            if x > margin + 25 and cur:
                paras.append(cur); cur = []
            cur.append(t)
    if cur:
        paras.append(cur)
    return [join_lines(p) for p in paras]


NUM = re.compile(r"(?<![\w.])([1-7Iil])(?:\s?[.\-·]\s?([\dIlOoSsz ]{1,7}?))?(?=[\s,;)]|$)")


def fix_num(a, b):
    tr = str.maketrans({"I": "1", "l": "1", "i": "1", "O": "0", "o": "0", "S": "5", "s": "5", "z": "2"})
    n = a.translate(tr) + ("." + b.replace(" ", "").translate(tr) if b else "")
    return n


def index(pages):
    entries, bad = [], []
    for p in pages:
        for col in "ab":
            ls = [l for l in lines(f"{SRC}/ix-{p:03d}-{col}.tsv") if 170 < l[1] < 2700]
            ls = [l for l in ls if l[3].strip() not in ("INDEX", "IN]", "IN")]
            if not ls:
                continue
            xs = sorted(l[0] for l in ls)
            base = xs[0]
            for x, y, h, t in ls:
                t = t.strip()
                if re.fullmatch(r"[\dIl]{3}", t):
                    continue
                lvl = 0 if x < base + 20 else 1 if x < base + 60 else 2
                if lvl == 2 and entries:
                    tgt = entries[-1]["subs"] if entries[-1]["subs"] else None
                    if tgt is not None:
                        tgt[-1] = join_lines([tgt[-1], t])
                    else:
                        entries[-1]["head"] = join_lines([entries[-1]["head"], t])
                elif lvl == 1 and entries:
                    entries[-1]["subs"].append(t)
                else:
                    if entries and entries[-1]["head"].endswith(("-", ",")) and not entries[-1]["subs"]:
                        entries[-1]["head"] = join_lines([entries[-1]["head"], t])
                    else:
                        entries.append({"head": t, "subs": [], "page": p})

    def norm(s):
        def rep(m):
            n = fix_num(m.group(1), m.group(2))
            if n in canon:
                return n
            bad.append((s, m.group(0)))
            return m.group(0)
        s = re.sub(r"\(\s*([iIl1-9](?:\s*,\s*[iIl1-9])*)\s*\)", lambda m: "(" + m.group(1).replace("I", "1").replace("i", "1").replace("l", "1") + ")", s)
        return NUM.sub(rep, s)
    for e in entries:
        e["head"] = norm(e["head"])
        e["subs"] = [norm(s) for s in e["subs"]]
    return entries, bad


out = {}
out["note"] = prose([5], "NOTE")
out["intro"] = prose(range(7, 24), "INTRODUCTION")
ix, bad = index(range(191, 208))
out["index"] = ix
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
print("заметка:", len(out["note"]), "абз.; введение:", len(out["intro"]), "абз.; указатель:", len(ix), "статей,",
      sum(len(e["subs"]) for e in ix), "подрубрик; номеров вне канона:", len(bad))
for b in bad[:40]:
    print("  ", b)
