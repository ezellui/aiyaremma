"""Решения по участкам контактных листов 1961 г. (аналог glyph_map из HWPh, но на участок).

Каждая запись: (издание, положение, было, стало, вид). «Было» должно встречаться в тексте
положения ровно один раз (после fixes.py); иначе build_all.py сообщит об ошибке.
Вид решения — как в HWPh:
  text  — обычная правка слова/склейки/распознавания;
  sym   — формула, записанная юникодом (⊃ ∨ ~ ∃ ≡ ξ Ω …) в строке текста;
  tex   — формула TeX внутри $…$ (когда юникода мало: индексы, черта над буквой, дроби);
  texd  — выключная формула $$…$$;
  emph  — разрядка/курсив оригинала → *…*.
Решения принимались по вырезкам скана (out/proof/regions/), сверка — по изданиям 2023 и 2005 гг.

    python3 decisions61.py      # проверка: все «было» находятся ровно один раз
"""

DE, EN = "de1961", "en1961"

D = [
    # --- немецкий текст: слова ---
    (DE, "2.01231", "ÜUmeinen", "Um einen", "text"),
    (DE, "2.0141", "ın", "in", "text"),
    (DE, "3.1432", "dass ain der Beziehung R zu b steht‘‘", "dass a in der Beziehung R zu b steht“", "text"),
    (DE, "3.1432", "zu ‚‚b“ steht", "zu ‚b‘ steht", "text"),
    (DE, "3.261", "welchesallein", "welches allein", "text"),
    (DE, "3.312", "konstantundalles", "konstant und alles", "text"),
    (DE, "3.331", "Iheory", "Theory", "text"),
    (DE, "3.34", "derHervorbringung", "der Hervorbringung", "text"),
    (DE, "3.342", "etwaswillkürlich", "etwas willkürlich", "text"),
    (DE, "3.343", "ineineandere", "in eine andere", "text"),
    (DE, "4.013", "der#und bin der", "der ♯ und ♭ in der", "sym"),
    (DE, "4.0141", "entnchmen", "entnehmen", "text"),
    (DE, "4.0141", "indieSprache derGrammop", "in die Sprache der Grammop", "text"),
    (DE, "4.016", "Hieroglyphenschrift,welche", "Hieroglyphenschrift, welche", "text"),
    (DE, "4.022", "Undersagt", "Und er sagt", "text"),
    (DE, "4.023", "DerSatzistdie BeschreibungeinesSachverhaltes", "Der Satz ist die Beschreibung eines Sachverhaltes", "text"),
    (DE, "4.461", "Weahrheitsbedingungen", "Wahrheitsbedingungen", "text"),
    (DE, "4.52", "dassesdie", "dass es die", "text"),
    (DE, "5.01", "Weahrheitsargumente", "Wahrheitsargumente", "text"),
    (DE, "5.23", "ausihmden", "aus ihm den", "text"),
    (DE, "5.2522", "Formenreihea,", "Formenreihe a,", "text"),
    (DE, "5.2522", "Kiammerausdruckes", "Klammerausdruckes", "text"),
    (DE, "5.41", "Weahrheitsfunktionen", "Wahrheitsfunktionen", "text"),
    (DE, "5.62", "ist,daszeigtsich", "ist, das zeigt sich", "text"),
    (DE, "5.62", "Sprache(der Sprache,;dieallein", "Sprache (der Sprache, die allein", "text"),
    (DE, "5.631", "gibtesnicht", "gibt es nicht", "text"),
    (DE, "6.022", "Formaller", "Form aller", "text"),
    (DE, "6.124", "ZElementarsätze", "Elementarsätze", "text"),
    (DE, "6.231", "„I+I+I+I“", "„1 + 1 + 1 + 1“", "sym"),
    (DE, "6.231", "„(I+I)+(I+1)“", "„(1 + 1) + (1 + 1)“", "sym"),
    (DE, "6.3211", "hatjaauch", "hat ja auch", "text"),
    (DE, "6.37", "gibtesnicht", "gibt es nicht", "text"),
    (DE, "6.371", "Weltanschauungliegt", "Weltanschauung liegt", "text"),
    (DE, "6.375", "esnureine", "es nur eine", "text"),
    (DE, "6.43", "Weltändern", "Welt ändern", "text"),
    (DE, "6.4312", "Zeitliegtausserhalb", "Zeit liegt ausserhalb", "text"),
    (DE, "6.51", "nich t", "nicht", "text"),
    (DE, "6.522", "zeig tsich", "zeigt sich", "text"),
]


def check(props_by_ed):
    bad = []
    for ed, num, old, new, kind in D:
        n = props_by_ed[ed][num].count(old)
        if n != 1:
            bad.append((ed, num, old, n))
    return bad


def apply(props, ed):
    for e, num, old, new, kind in D:
        if e != ed:
            continue
        t = props[num]
        if t.count(old) != 1:
            raise SystemExit(f"decisions61: {ed} {num}: «{old}» встречается {t.count(old)} раз")
        props[num] = t.replace(old, new)
    return props


if __name__ == "__main__":
    import json, os
    W = os.path.dirname(os.path.abspath(__file__))
    pe = {DE: json.load(open(f"{W}/norm_tlp_de_1961.json"))["props"],
          EN: json.load(open(f"{W}/norm_tlp_en_1961_ogden.json"))["props"]}
    b = check(pe)
    print(len(D), "решений;", "все на месте" if not b else b)
