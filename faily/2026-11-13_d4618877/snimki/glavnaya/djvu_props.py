"""Поток абзацев распознанного издания → положения по каноническому списку номеров.

split(paras, canon) → (props{num: [абзац…]}, pages{num: page}, junk[абзацы до первого номера])
Номер в начале абзаца распознан с ошибками («6Л202», «2.023 », «1 .», «I.1»): кандидат
приводится к цифрам и принимается, только если он есть в каноне и идёт после предыдущего
не дальше чем на 40 номеров. Пропущенные номера ищутся вторым проходом: абзац без номера,
который начинается с «похожего» на ожидаемый номер текста, — тоже начало положения.
"""
import re
from dehyph import Dehyph

TR = str.maketrans({"I": "1", "l": "1", "i": "1", "|": "1", "Л": "1", "О": "0", "O": "0", "o": "0", "о": "0",
                    "З": "3", "б": "6", "S": "5", "s": "5", "B": "8", "Б": "6", "z": "2", ",": "."})
HEAD = re.compile(r"^\s*([1-7IlЛ|][0-9IlЛ|OОoоЗбSsBz.,\s]{0,10}?)(?:\.|,)?\s+(?=\S)")


def number(text):
    m = HEAD.match(text)
    if not m:
        return None, 0
    raw = m.group(1)
    n = re.sub(r"\s+", "", raw.translate(TR)).rstrip(".")
    n = re.sub(r"\.{2,}", ".", n)
    if not re.fullmatch(r"[1-7](\.\d+)?", n):
        return None, 0
    return n, m.end()


def split(paras, canon):
    order = {n: i for i, n in enumerate(canon)}
    props, pages, junk = {}, {}, []
    cur, last = None, -1
    for p in paras:
        text = " ".join(p["lines"]).strip()
        n, cut = number(text)
        if n in order and 0 < order[n] - last <= 40 and n not in props:
            cur, last = n, order[n]
            props[n] = [p["lines"][:]]
            props[n][0][0] = props[n][0][0].strip()[cut - (len(text) - len(text.lstrip())):] \
                if False else re.sub(r"^\s*" + re.escape(text[:cut].strip()) + r"\s*", "", props[n][0][0].strip(), count=1)
            pages[n] = p["page"]
        elif cur is None:
            junk.append(text)
        else:
            props[cur].append(p["lines"])
    return props, pages, junk


def render(props, extra_learn=()):
    """Абзацы положений → текст Markdown (склейка переносов по словарю самого текста)."""
    dh = Dehyph()
    for v in props.values():
        for para in v:
            for ln in para:
                dh.learn(ln.strip())
    for t in extra_learn:
        dh.learn(t)
    return {n: "\n\n".join(dh.join([l for l in para if l.strip()]) for para in v if any(l.strip() for l in para))
            for n, v in props.items()}
