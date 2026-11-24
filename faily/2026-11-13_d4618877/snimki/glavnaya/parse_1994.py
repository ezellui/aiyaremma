"""Издание 1994 г. (Гнозис; пер. М. С. Козловой и Ю. А. Асеева): «Трактат» по-немецки и по-русски
на соседних страницах (файл стр. 23–164), примечания и комментарии Козловой (стр. 579–599).

    python3 parse_1994.py ../tlp1/tlp1994.djvu raw1994.json
Страница — один столбец: номер положения висит слева (x≈190), текст — с x≈540;
абзац внутри положения — красная строка. Язык страницы — по колонтитулу.
"""
import json, re, sys
import djvu_lines as dl

DJ, OUT = sys.argv[1:3]
FIRST, LAST = 27, 164


def page_paras(p):
    L = sorted(dl.lines(DJ, p), key=lambda z: z.y0)
    if not L:
        return None, []
    head = L[0].text
    lang = "de" if re.search(r"[A-Z]{5}", head) else "ru"
    L = L[1:]
    if L and re.fullmatch(r"\[?\d{1,3}\]?", L[-1].text.strip()):
        L = L[:-1]
    body = [l for l in L if l.x0 > 400]
    margin = sorted(l.x0 for l in body)[len(body) // 5] if body else 540
    paras = []
    for l in L:
        start = l.x0 < 400 or l.x0 - margin > 40
        if start or not paras:
            paras.append({"page": p, "lines": [l.text]})
        else:
            paras[-1]["lines"].append(l.text)
    return lang, paras


streams = {"de1994": [], "ru1994": []}
for p in range(FIRST, LAST + 1):
    lang, paras = page_paras(p)
    if lang:
        streams[lang + "1994"].extend(paras)


# примечания и комментарии Козловой: «Стр. N 2.0121 текст …» — по номерам положений
comm = []
for p in range(579, 600):
    L = sorted(dl.lines(DJ, p), key=lambda z: z.y0)
    for l in L[1:]:
        t = l.text.strip()
        if re.fullmatch(r"\d{3}", t) or "«Философские исследования»" in t:
            if "«Философские исследования»" in t:
                break
            continue
        comm.append({"page": p, "x": l.x0, "text": t})
dl.save_cache(DJ)
json.dump({"streams": streams, "comm_lines": comm}, open(OUT, "w"), ensure_ascii=False, indent=0)
for s, v in streams.items():
    print(s, "абзацев:", len(v))
print("строк комментария:", len(comm))
