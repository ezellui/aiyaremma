"""Переводы из DjVu → work/editions/*.md (простой текстовый формат, edition_text.py).

  djvu_texts.json (parse_2017.py, parse_1994.py → djvu_props) → склейка абзацев, разорванных
  страницей → автоправка формул (NORM) → решения decisions_new.py → сноски переводчиков (2017)
  и комментарий Козловой (1994) → editions/<id>.md.

    python3 make_editions.py
"""
import json, re
import edition_text
import decisions_new as dn
import kozlova

canon = json.load(open("canon.json"))
TX = json.load(open("djvu_texts.json"))

META = {
    "ru1958": dict(lang="ru", year=1958, short="Добронравов–Лахути",
                   title="Логико-философский трактат / Пер. с нем. И. С. Добронравова и Д. Г. Лахути (1958; ред. 2008)",
                   cite="Витгенштейн Л. Логико-философский трактат / Пер. И. С. Добронравова, Д. Г. Лахути. "
                        "М.: Канон+, 2017. С. {p}",
                   note="Первый русский перевод (1958), в редакции 2008 г. Текст — из двуязычного издания 2017 г. "
                        "(текстовый слой DjVu, разметка по номерам положений, вычитка формул по листам "
                        "out/proof_new). Сноски переводчиков — примечания."),
    "en1974": dict(lang="en", year=1961, short="Pears–McGuinness",
                   title="Tractatus Logico-Philosophicus, transl. D. F. Pears and B. F. McGuinness (1961; rev. 1974)",
                   cite="Wittgenstein L. Tractatus Logico-Philosophicus / Transl. D. F. Pears, B. F. McGuinness. "
                        "Moscow: Kanon+, 2017. P. {p}",
                   note="Второй английский перевод (1961, исправленное издание 1974). Текст — из издания 2017 г. "
                        "(текстовый слой DjVu, вычитка формул по листам out/proof_new)."),
    "ru1994": dict(lang="ru", year=1994, short="Козлова–Асеев",
                   title="Логико-философский трактат / Пер. с нем. М. С. Козловой и Ю. А. Асеева (1994)",
                   cite="Витгенштейн Л. Философские работы. Ч. I. М.: Гнозис, 1994. С. {p}",
                   note="Перевод М. С. Козловой и Ю. А. Асеева из «Философских работ» (1994). Текстовый слой DjVu, "
                        "вычитка формул по листам out/proof_new. Комментарии — примечания М. С. Козловой к "
                        "«Трактату» (с. 579–599 издания), разнесённые по положениям."),
}
# страница DjVu → страница книги
PAGE = {"ru1958": lambda p: p, "en1974": lambda p: p, "ru1994": lambda p: p - 22}

END = re.compile(r"[.:!?)»\"”’…]\s*$")


def join_breaks(t):
    """Абзац, разорванный страницей/колонтитулом: склеить, если предыдущий не кончается фразой."""
    paras = t.split("\n\n")
    out = []
    for p in paras:
        if out and not out[-1].startswith(("|", "$$", "![")) and not p.startswith(("|", "$$", "![")):
            prev = out[-1]
            if prev.endswith("-") and re.match(r"[a-zа-яё]", p):
                out[-1] = prev[:-1] + p
                continue
            if not END.search(prev) and re.match(r"[a-zа-яё(«\"“]", p):
                out[-1] = prev + " " + p
                continue
        out.append(p)
    return "\n\n".join(out)


VARS = "pqrsxyzabcuPQR"

NORM_COMMON = [
    (r"/\?", "p"), (r"\bjc\b", "x"), (r"(?<=[(\[\"“«‘'])jc", "x"), (r"jc(?=[)\],.\"”»’])", "x"),
    (r"\\\s?3x", "(∃x"), (r"\((3|Э|З)\s?(?=[xyφф])", "(∃"), (r"Эф", "∃φ"), (r"ф", "φ"), (r"\\\|/", "ψ"),
    (r"(?<=N\()\s*[§£ξ]\s*\)", "ξ̄)"), (r"(?<=N’\()\s*[§£ξ]\s*\)", "ξ̄)"), (r"[§£]", "ξ"),
    (r"\((ξ)\)", "(ξ̄)"),
    (r"\bfi[ce]\b", "fx"), (r"(?<=[\"“«])fic", "fx"),
    (r"(?<=[a-zA-Z)])\s?v\s?(?=[~a-zA-Z(])", " ∨ "),
    (r"\s?(?:z>|=>|zd|z\))\s?", " ⊃ "),
    (r"(?<=\s)-(?=[pq]\b)", "~"), (r"\"-/", "\"~"), (r"«-(?=[pq]\b)", "«~"),
    (r"Q'", "Ω’"), (r"\bQ(?=[0-9v]')", "Ω"),
]
NORM = {
    "en": NORM_COMMON + [(r"\"([^\"\n]{1,60})\"", r"“\1”"), (r"(?<=\w)'(?=\w)", "’")],
    "ru": NORM_COMMON + [
        # латинские переменные, прочитанные кириллицей, в формульном окружении
        (r"(?<=[«(\[ ~|.,])р(?=[»)\], .|:;]|$)", "p"), (r"(?<=[«(\[~|])я(?=[»)\],.|])", "q"),
        (r"(?<=[«(\[ ~|.,])х(?=[»)\], .|:;])", "x"), (r"(?<=\()х(?=,)", "x"),
        (r"(?<=[«(\[ ~|])ρ(?=[»)\], .|])", "p"), (r"(?<=[«(\[ ~|])ς?τ(?=[»)\], .|])", "q"),
        (r"(?<=[«(\[ ~|])Ρ(?=[»)\], .|])", "P"), (r"(?<=[«(\[ ~|])χ(?=[»)\], .|])", "x"),
        (r"<<", "«"), (r">>", "»"),
    ],
}


def norm(lang, t):
    for a, b in NORM[lang]:
        t = re.sub(a, b, t)
    return t


def italic_vars(t):
    """Русский текст: одиночные латинские буквы-переменные — курсивом, как в других изданиях."""
    def f(m):
        return "*" + m.group(0) + "*"
    parts = re.split(r"(\$[^$]*\$|!\[\]\([^)]*\)|^\|.*$)", t, flags=re.M)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<![\w*\\])[a-zA-Z]{1,3}(?![\w*’'])(?![^(]*\]\()", lambda m: m.group(0) if m.group(0) in
                          ("Def", "I", "II", "III", "N", "Gen", "et", "al", "ed", "Ibid") else f(m), parts[i])
    return "".join(parts)


def build(ed):
    meta = META[ed]
    texts = {n: join_breaks(TX[ed]["texts"][n]) for n in canon if n in TX[ed]["texts"]}
    texts = {n: norm(meta["lang"], t) for n, t in texts.items()}
    bad = dn.apply(ed, texts)
    if meta["lang"] == "ru":
        texts = {n: (t if n in dn.WHOLE.get(ed, {}) else italic_vars(t)) for n, t in texts.items()}
    pages = {n: PAGE[ed](p) for n, p in TX[ed]["pages"].items()}
    notes, comments = {}, []
    if ed in ("ru1958", "en1974"):
        notes = footnotes(ed, texts)
    if ed == "ru1994":
        comments = kozlova.comments(canon)
    md = edition_text.export(ed, dict(meta, id=ed), texts, pages, comments, notes, canon)
    open(f"editions/{ed}.md", "w", encoding="utf-8").write(md)
    chk = edition_text.parse(md, canon)
    print(ed, "положений", len(chk["texts"]), "нет", chk["missing"], "решений не легло", bad,
          "сносок", len(notes), "комментариев", len(comments))


# --- сноски переводчиков в издании 2017 ---
RAW17 = json.load(open("raw2017.json"))


def footnotes(ed, texts):
    """Сноски страницы (raw2017 notes) → [^k] у слова с цифрой-маркером в тексте положения."""
    want_ru = ed == "ru1958"
    notes = {}
    k = 0
    for grp in RAW17["notes"]:
        lines = grp["lines"]
        # сноски ru — кириллица; en — латиница (на нечётных страницах только английские)
        body = [l for l in lines if bool(re.search(r"[а-яё]", l, re.I)) == want_ru]
        if not body:
            continue
        if grp["page"] % 2 == (0 if want_ru else 1) or not want_ru:
            pass
        txt = " ".join(body)
        txt = re.sub(r"(\w)-\s+(\w)", r"\1\2", txt)
        items = re.split(r"(?:^|\s)(?=[1-9*]\s+[А-ЯA-Z«])", txt)
        for it in items:
            it = it.strip()
            m = re.match(r"^([1-9*])\s+(.*)$", it, re.S)
            if not m:
                continue
            k += 1
            key = f"{ed[:2]}{k}"
            notes[key] = m.group(2).strip()
            place(texts, grp["page"], m.group(1), key, ed)
    return notes


def place(texts, page, mark, key, ed):
    """Поставить ссылку [^key] в положение на этой странице: после слова с маркером «слово1» / «»1»."""
    nums = [n for n, p in TX[ed]["pages"].items() if p == page]
    rx = re.compile(r"(?<=[^\s\d.,(])" + re.escape(mark) + r"(?=[\s,.;:)]|$)")
    for n in nums:
        t = texts.get(n, "")
        m = rx.search(t)
        if m:
            texts[n] = t[:m.start()] + f"[^{key}]" + t[m.end():]
            return
    if nums:                                   # маркер не распознан — к последнему положению страницы
        n = sorted(nums, key=canon.index)[-1]
        texts[n] = texts[n] + f"[^{key}]"


if __name__ == "__main__":
    for ed in META:
        build(ed)
