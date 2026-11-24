"""Статьи и предисловия из DjVu (издания 2017 и 1994) → editions/<id>.app.json, editions/<id>.front.json.

  ru1958: «От составителей», введение Б. Рассела (рус.), статья переводчиков о русских изданиях 1958 и 2008 гг.;
  en1974: «From the compilers», статья переводчиков (англ.);
  ru1994: «Философские искания Л. Витгенштейна» (М. С. Козлова).
  Предисловие автора, посвящение и эпиграф — для всех трёх.

Абзац — по отступу первой строки; подстрочные сноски — хвост страницы мелким кеглем; знак сноски
в тексте — цифра, приклеенная к слову («языке1»).

    python3 parse_app17.py
"""
import json, re, statistics
import djvu_lines as dl
import djvu_props as dp

D17, D94 = "../tlp1/tlp2017.djvu", "../tlp1/tlp1994.djvu"


def page_lines(djvu, p, col=None):
    L = sorted(dl.lines(djvu, p), key=lambda z: z.y0)
    if col is not None:
        import parse_2017_cols as pc
        L = pc.column(djvu, p, col)
    L = [l for l in L if not re.fullmatch(r"\[?\d{1,3}\]?", l.text.strip())]
    return L


def split_page(L):
    """(текст, сноски): сноски — хвост строк заметно меньшего кегля."""
    if not L:
        return [], []
    med = statistics.median(l.h for l in L)
    k = len(L)
    while k > 0 and L[k - 1].h < 0.86 * med:
        k -= 1
    if k < len(L) and len(L) - k >= 1 and k > 0 and L[k].y0 - L[k - 1].y1 > 40:
        return L[:k], L[k:]
    return L, []


def paragraphs(L, indent=60):
    if not L:
        return []
    xs = sorted(l.x0 for l in L)
    margin = xs[len(xs) // 5]
    out = []
    for l in L:
        if not out or l.x0 - margin > indent:
            out.append([l.text])
        else:
            out[-1].append(l.text)
    return out


def article(djvu, pages, skip_head=(), col=None, title_lines=0):
    body, notes = [], []
    first = True
    for p in pages:
        L = page_lines(djvu, p, col)
        while L and any(re.search(h, L[0].text) for h in skip_head):
            L = L[1:]
        if first:
            L = L[title_lines:]
        b, n = split_page(L)
        paras = paragraphs(b)
        if paras and not first and body and not (b and b[0].x0 - sorted(x.x0 for x in b)[len(b) // 5] > 60):
            body[-1] += paras.pop(0)                 # абзац продолжается с прошлой страницы
        body += paras
        for para in paragraphs(n, 40):
            if re.match(r"^\s*(\d{1,2}|\*)\s", para[0]) or not notes:
                notes.append(para)
            else:
                notes[-1] += para
        first = False
    dh = dp.Dehyph()
    for para in body + notes:
        for ln in para:
            dh.learn(ln)
    text = [re.sub(r"\s+", " ", dh.join(p)).strip() for p in body]
    nts = {}
    for i, p in enumerate(notes, 1):
        t = re.sub(r"\s+", " ", dh.join(p)).strip()
        t = re.sub(r"^(\d{1,2}|\*)\s+", "", t)
        nts[str(i)] = t
    # знаки сносок в тексте: цифра, приклеенная к слову или кавычке, по порядку
    k = 1
    for i, t in enumerate(text):
        def mark(m):
            nonlocal k
            if m.group(2) == str(k) and str(k) in nts:
                k += 1
                return m.group(1) + f"[^{k - 1}]"
            return m.group(0)
        text[i] = re.sub(r"([^\s\d.,(\-–—])(\d{1,2})(?=[\s,.;:)»\"”]|$)", mark, t)
    return {"text": "\n\n".join(text), "notes": nts}


if __name__ == "__main__":
    import sys
    a = article(D17, range(271, 283), skip_head=[r"русские издания 1958 и 2008", r"^\d+$"], title_lines=3)
    print(a["text"][:1500]); print(list(a["notes"].items())[:3])
