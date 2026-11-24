"""Примечания М. С. Козловой к «Логико-философскому трактату» (Философские работы, 1994, с. 579–599 DjVu)
→ комментарии к положениям: [{"covers": [номера], "text": …}].

Статья начинается строкой «[Стр. N] номер[—номер] текст…»; номера идут по порядку канона,
а предыдущая строка кончается фразой. Ссылка без номера («Стр. 5 Десятичные числа…») — к сноске
автора при положении 1.
"""
import re
import djvu_lines as dl
import djvu_props as dp

DJ = "../tlp1/tlp1994.djvu"
HEAD = re.compile(r"^(?:Стр\.\s*\d+\s+)?([1-7](?:\.\d+)?)\.?(?:\s*[—–-]\s*([1-7](?:\.\d+)?))?\s+(?=\S)")


def lines():
    out = []
    for p in range(579, 600):
        L = sorted(dl.lines(DJ, p), key=lambda z: z.y0)
        for l in L[1:]:
            t = l.text.strip()
            if re.fullmatch(r"\d{3}", t):
                continue
            if "«Философские исследования»" in t:
                return out
            out.append(t)
    return out


def comments(canon):
    order = {n: i for i, n in enumerate(canon)}
    entries, cur, last = [], None, -1
    prev = ""
    for t in lines():
        t2 = re.sub(r"^(Стр\.\s*\d+\s+)", r"\1", t.translate(dp.TR) if False else t)
        m = HEAD.match(t2)
        ok = False
        if m and m.group(1) in order and re.search(r"[.»)!?:*>]\s*$", prev or "."):
            a = order[m.group(1)]
            b = order.get(m.group(2), a) if m.group(2) else a
            if a >= last and a - last <= 120 and b >= a:
                ok = True
        if t.startswith("Стр.") and not ok and not m:
            # «Стр. 5 Десятичные числа…» — комментарий к сноске автора при 1
            cur = {"covers": ["1"], "lines": [re.sub(r"^Стр\.\s*\d+\s+", "", t)]}
            entries.append(cur)
        elif ok:
            covers = canon[a:b + 1]
            last = a
            body = t2[m.end():]
            head = m.group(0).strip()
            head = re.sub(r"^Стр\.\s*\d+\s+", "", head)
            cur = {"covers": covers, "lines": [body], "head": head}
            entries.append(cur)
        elif cur:
            cur["lines"].append(t)
        prev = t
    out = []
    dh = dp.Dehyph()
    for e in entries:
        for ln in e["lines"]:
            dh.learn(ln)
    for e in entries:
        txt = dh.join(e["lines"])
        txt = re.sub(r"\s+", " ", txt).strip()
        txt = txt.replace("<", "«").replace(">", "»").replace("4мир»", "«мир»")
        out.append({"covers": e["covers"], "text": txt})
    return out


if __name__ == "__main__":
    import json
    canon = json.load(open("canon.json"))
    C = comments(canon)
    print(len(C), "статей; покрыто положений:", len({n for c in C for n in c["covers"]}))
    for c in C[:6] + C[-3:]:
        print(c["covers"][0], "…", c["covers"][-1], "|", c["text"][:120])
