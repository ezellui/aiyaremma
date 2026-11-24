"""Второй «свидетель» для вычитки 1961 г.: OCR-слой Internet Archive в самом PDF.

Оба распознавания одной страницы (tesseract и слой IA) выравниваются по свёрнутым словам
(регистр, диакритика, ß→ss убраны — у IA нет умлаутов). Дальше:
  * подозрительное слово: tesseract и IA прочли его по-разному, и в словаре его нет;
  * поправка: замена «слово на слово», где слово tesseract не из словаря, а слово IA —
    словарное (по-немецки — только если IA-слово есть в словаре как есть, без умлаутов).
Результат: witness61.json — {lang: {"suspect": {num: [слова]}, "fixes": {tess_word: ia_word}}}.
Поправки применяет build_all.py (функция apply_witness), подозрительные идут в листы вычитки.

    python3 witness61.py "<PDF 1961>" ../ocr lp1961.json witness61.json
"""
import json, re, sys, difflib, unicodedata
import pymupdf
from spellchecker import SpellChecker

PDF, OCR, LP, OUT = sys.argv[1:5]
doc = pymupdf.open(PDF)
lp = json.load(open(LP))
WORD = re.compile(r"[^\W_]+")


def fold(s):
    s = unicodedata.normalize("NFD", s.replace("ß", "ss"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def tess_words(pg):
    out = []
    for ln in open(f"{OCR}/pg-{pg:03d}.tsv", encoding="utf-8").read().splitlines()[1:]:
        f = ln.split("\t")
        if len(f) >= 12 and f[0] == "5" and f[11].strip():
            out += WORD.findall(f[11])
    return out


def ia_words(pg):
    return WORD.findall(doc[pg - 1].get_text())


res = {}
for lang, pages in (("de", range(30, 190, 2)), ("en", range(31, 190, 2))):
    sp = SpellChecker(language=lang)
    known_f = {fold(w) for w in sp.word_frequency.dictionary}
    bad_by_page, fixes, votes = {}, {}, {}
    for pg in pages:
        a, b = tess_words(pg), ia_words(pg)
        fa, fb = [fold(w) for w in a], [fold(w) for w in b]
        sm = difflib.SequenceMatcher(a=fa, b=fb, autojunk=False)
        bad = set()
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == "equal":
                continue
            for w in fa[a1:a2]:
                if len(w) > 1 and not w.isdigit() and w not in known_f:
                    bad.add(w)
            if op == "replace" and a2 - a1 == b2 - b1:
                for t, i in zip(a[a1:a2], b[b1:b2]):
                    ft, fi = fold(t), fold(i)
                    if len(t) < 3 or ft in known_f or not i.isalpha():
                        continue
                    ok = (i.lower() in sp) if lang == "de" else (fi in known_f)
                    if ok and difflib.SequenceMatcher(a=ft, b=fi).ratio() >= 0.6:
                        votes.setdefault(t, {}).setdefault(i, 0)
                        votes[t][i] += 1
        bad_by_page[pg] = bad
    for t, cand in votes.items():
        i = max(cand, key=cand.get)
        if t[:1].isupper() and not i[:1].isupper():
            i = i[:1].upper() + i[1:]
        fixes[t] = i
    res[lang] = {"bad_by_page": {str(k): sorted(v) for k, v in bad_by_page.items()}, "fixes": fixes}
    print(lang, "поправок по второму OCR:", len(fixes))
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
