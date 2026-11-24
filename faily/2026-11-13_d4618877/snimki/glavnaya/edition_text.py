"""Простой текстовый формат редакции «Трактата» — чтобы добавлять новые переводы.

Файл .md в UTF-8:

    ---
    id: en1922pm              # латиницей, без пробелов: язык + год + метка
    lang: en                  # ru | de | en | …
    year: 1961
    title: Tractatus Logico-Philosophicus, transl. D. F. Pears and B. F. McGuinness (1961)
    short: Pears–McGuinness   # подпись колонки в читалке
    cite: Wittgenstein L. Tractatus … London, 1961, p. {p}
    note: откуда текст, что в нём особенного (одна строка или несколько с отступом)
    ---
    @page 7                   # необязательно: страница издания для следующих положений
    1 The world is everything that is the case.
    1.1 The world is the totality of facts, not of things.

    Второй абзац того же положения — после пустой строки.
    > Комментарий переводчика к положению 1.1 (строки с «> »).
    1.11 …

    [^1]: текст примечания; в тексте — ссылка [^1]

Положение начинается строкой с номером («1.1», «1.1.», «1.1 —»); всё до следующего номера —
его текст (Markdown: *курсив*, $формула$, таблицы, ![](fig:имя)). Номера проверяются по
канону 526 положений: незнакомые — ошибка, отсутствующие перечисляются.
"""
import json, re

NUM = re.compile(r"^\s*([1-7](?:\.\d+)?)\.?\s*(?:[—–-]\s*)?(?=\S)")
NOTE = re.compile(r"^\[\^([^\]]+)\]:\s?(.*)$")


def parse(text, canon):
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        key = None
        for ln in m.group(1).split("\n"):
            if re.match(r"^\s+\S", ln) and key:
                meta[key] += " " + ln.strip()
                continue
            mm = re.match(r"^(\w+):\s*(.*?)\s*(?:#.*)?$", ln)
            if mm:
                key = mm.group(1)
                meta[key] = mm.group(2)
        body = text[m.end():]
    for k in ("id", "lang", "title", "short"):
        if not meta.get(k):
            raise ValueError(f"в заголовке нет поля {k}")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", meta["id"]):
        raise ValueError("id — латиница в нижнем регистре, цифры, _")
    canon_set = set(canon)
    texts, pages, comments, notes = {}, {}, [], {}
    cur, page, buf, cbuf, note_key = None, None, [], [], None
    errors = []

    def flush():
        if cur is None:
            return
        t = "\n".join(buf).strip()
        t = re.sub(r"\n{3,}", "\n\n", t)
        texts[cur] = t
        if cbuf:
            comments.append({"covers": [cur], "text": re.sub(r"\n{3,}", "\n\n", "\n".join(cbuf).strip())})

    for ln in body.split("\n"):
        if note_key is not None and ln.strip() and not NUM.match(ln) and not NOTE.match(ln):
            notes[note_key] += "\n" + ln.strip()
            continue
        mm = NOTE.match(ln)
        if mm:
            note_key = mm.group(1)
            notes[note_key] = mm.group(2)
            continue
        if ln.startswith("@page"):
            page = int(ln.split()[1])
            continue
        mm = NUM.match(ln)
        if mm and (mm.group(1) in canon_set or "." in mm.group(1) or len(ln) > 3):
            n = mm.group(1)
            if n not in canon_set:
                errors.append(f"неизвестный номер {n}: {ln[:60]}")
            else:
                flush()
                if n in texts:
                    errors.append(f"повтор номера {n}")
                cur, buf, cbuf = n, [ln[mm.end():]], []
                if page:
                    pages[n] = page
                note_key = None
                continue
        if cur is None:
            continue
        if ln.startswith(">"):
            cbuf.append(ln[1:].lstrip())
        else:
            buf.append(ln)
    flush()
    meta.setdefault("year", "")
    meta.setdefault("cite", meta["title"] + ", {p}")
    meta.setdefault("note", "")
    missing = [n for n in canon if n not in texts]
    return {"meta": meta, "texts": texts, "pages": pages, "comments": comments, "notes": notes,
            "missing": missing, "errors": errors}


def export(ed_id, meta, texts, pages, comments, notes, canon):
    """Редакция из данных читалки -> текстовый формат (шаблон для новых переводов)."""
    out = ["---"] + [f"{k}: {str(meta.get(k, '')).replace(chr(10), ' ')}" for k in
                     ("id", "lang", "year", "title", "short", "cite", "note")] + ["---", ""]
    by_last = {}
    for c in comments:
        by_last.setdefault(c["covers"][-1], []).append(c)
    page = None
    for n in canon:
        if n not in texts:
            continue
        if pages.get(n) and pages[n] != page:
            page = pages[n]
            out.append(f"@page {page}")
        out.append(f"{n} {texts[n]}")
        for c in by_last.get(n, []):
            head = f"[к {c['covers'][0]}–{c['covers'][-1]}] " if len(c["covers"]) > 1 else ""
            out += ["> " + ln if ln else ">" for ln in (head + c["text"]).split("\n")]
        out.append("")
    if notes:
        out.append("")
        for k, v in notes.items():
            out.append(f"[^{k}]: " + v.replace("\n\n", "\n    "))
    return "\n".join(out) + "\n"
