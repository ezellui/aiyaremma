"""Нормализация четырёх текстов и сборка фрактальной раскладки для каждого."""
import json, re, os
import tlp_tree
from render_tree import render, tree_json

W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(W, "..", "out")
os.makedirs(OUT, exist_ok=True)

canon = json.load(open(f"{W}/canon.json"))
assert len(canon) == 526


def fix(props, edits, tag):
    """Точечные правки: (номер, было, стало) или (номер, None, новый текст целиком)."""
    for num, old, new in edits:
        if old is None:
            props[num] = new
        elif old in props.get(num, ""):
            props[num] = props[num].replace(old, new)
        else:
            print(f"[{tag}] правка не применилась: {num}: {old[:40]!r}")


def tidy(t):
    t = t.replace("</sup><sup>", "")
    t = re.sub(r"[ \t]+\n", "\n", t)
    return t


def overbar(t):
    # «⎯ξ», «⎯*x*» (2005) -> ξ̄, *x̄*
    return re.sub(r"⎯\s*(\*?)([^\s*])(\*?)", lambda m: m.group(1) + m.group(2) + "̄" + m.group(3), t)


SCHEME = "*[здесь в оригинале — графическая схема; в текстовом слое её нет]*"

# ---------------------------------------------------------------- 2023
d = json.load(open(f"{W}/ru2023.json"))
p23 = {k: tidy(v) for k, v in d["props"].items()}
fix(p23, [
    ("4.013", "��[диез]", "♯ [диез]"), ("4.013", "��[бемоль]", "♭ [бемоль]"),
    ("4.442", "«�»", "«⊢»"),
    ("6.01", "η�", "η̄"), ("6.01", "*N*(̄ξ)", "*N*(ξ̄)"),
    ("4.27", None, "Для всякой позиции имеется $K_n = \\sum_{\\nu=0}^{n}\\binom{n}{\\nu}$ "
                   "возможностей существования и несуществования.\n\n"
                   "Любая комбинация этих позиций может существовать, тогда как прочие существовать не будут."),
    ("4.42", None, "Для *n* числа элементарных высказываний имеется $\\sum_{x=0}^{K_n}\\binom{K_n}{x} = L_n$ "
                   "способов, какими высказывание может соотноситься или не соотноситься с возможностями истинности."),
    ("6.1203", "например: и использую", "например:\n\n" + SCHEME + "\n\nи использую"),
    ("6.1203", "следующим образом:\n\nВ итоге", "следующим образом:\n\n" + SCHEME + "\n\nВ итоге"),
    ("6.1203", "а форма «ξ × η» такова:\n\nПоэтому", "а форма «ξ × η» такова:\n\n" + SCHEME + "\n\nПоэтому"),
    ("6.1203", "будет выглядеть так:\n\nЕсли", "будет выглядеть так:\n\n" + SCHEME + "\n\nЕсли"),
], "2023")
pn = d["page_notes"]
fn23 = dict(d["endnotes"])
for pg, notes in pn.items():
    fn23[f"p{pg}"] = re.sub(r"^\[\^\*\]\s*", "", notes[0])
for k in fn23:
    fn23[k] = re.sub(r"^\[\^\*\]\s*", "", fn23[k])
front23 = d["front"]
src23 = {
    "title": "Логико-философский трактат — пер. К. Королева (2023)",
    "note": ("Людвиг Витгенштейн. Логико-философский трактат. Перевод с немецкого, латинского и английского "
             "Кирилла Королева. М.: КоЛибри, Азбука-Аттикус, 2023. Раскладка «логическим деревом» — как в самом "
             "издании: сначала положения 1–7; затем для каждого узла — его повтор (жирным) и ветвь непосредственных "
             "комментариев; ветви идут вглубь по порядку номеров. Повторы порождены по правилу автоматически, "
             "текст каждого положения взят из его вхождения в ветвь родителя. Сноски [^N] — примечания переводчика "
             "(в книге — в конце текста), [^pNN] — подстрочные примечания со стр. NN."),
    "front": {"dedication": front23["dedication"], "motto": front23["motto"],
              "preface_title": "Предисловие[^3]", "preface": front23["preface"]},
    "props": p23, "footnotes": fn23,
}

# ---------------------------------------------------------------- 2005
d = json.load(open(f"{W}/ru2005.json"))
p05 = {k: overbar(tidy(v)) for k, v in d["props"].items()}
fix(p05, [
    ("4.27", None, "Относительно существования и несуществования *n* Положений Вещей существует "
                   "$K_n = \\sum_{\\nu=0}^{n}\\binom{n}{\\nu}$ возможностей.\n\n"
                   "Могут существовать все эти комбинации Положений Вещей, других не существует."),
    ("4.42", None, "Относительно согласования и несогласования Пропозиции с возможностями истинности у "
                   "Элементарной Пропозиции имеется $\\sum_{k=0}^{k_n}\\binom{k_n}{k} = L_n$ возможностей."),
    ("4.442", "Так, например,*p* *q*\n\n```\n", "Так, например,\n\n```\n                                   p            q\n"),
], "2005")
com05 = [{"after": c["after"], "text": overbar(tidy(c["text"]))} for c in d["comments"]]
src05 = {
    "title": "Логико-философский трактат — пер. и комментарий В. Руднева (2005)",
    "note": ("Людвиг Витгенштейн. Tractatus logico-philosophicus (с параллельными комментариями В. Руднева) // "
             "Витгенштейн Л. Избранные работы. М.: Территория будущего, 2005 (Университетская библиотека "
             "Александра Погорельского). Положения переложены в «логическое дерево» по образцу издания 2023 г.; "
             "комментарий Руднева стоит цитатой сразу после положения (если он относится к нескольким положениям "
             "подряд — после последнего из них, с пометкой «к a–b»). В издании нет положений 2.182, 3.142, 4.062, "
             "4.063, 4.43, 4.431, 5.1363, 5.5303; 2.06 напечатано не на месте (среди 2.03x), опечатки нумерации "
             "«2.1» (вместо 2.01), «3.18» (вместо 3.318) исправлены."),
    "front": {**d["front"], "preface_title": "Предисловие"},
    "comment_label": "Комментарий В. Руднева",
    "missing_label": "в издании 2005 г. отсутствует",
    "props": p05, "comments": com05,
}

# ---------------------------------------------------------------- 1961
d = json.load(open(f"{W}/lp1961.json"))
srcs61 = {}
for lang in ("de", "en"):
    p = {k: tidy(v) for k, v in d[lang]["props"].items()}
    fns = {}
    if lang == "de":
        p["1"] = p["1"].rstrip("*") + "[^1]"
        fns["1"] = re.sub(r"^\*\s*", "", d[lang]["notes"][0][1])
        title = "Logisch-philosophische Abhandlung — deutscher Text (Ausgabe 1961)"
        note = ("Ludwig Wittgenstein. Tractatus Logico-Philosophicus. London: Routledge & Kegan Paul, 1961 "
                "(International Library of Psychology, Philosophy and Scientific Method; deutscher Text mit "
                "englischer Übersetzung von C. K. Ogden). Text aus dem Scan neu erkannt (tesseract), "
                "Nummern nach der kanonischen Liste wiederhergestellt; Sperrsatz und Kursiv gehen bei der "
                "Erkennung verloren, Formeln und Tabellen sind nur teilweise lesbar. "
                "Anordnung als «logischer Baum» nach dem Muster der russischen Ausgabe 2023.")
        front = {"dedication": "*Dem Andenken meines Freundes David H. Pinsent gewidmet*"
                 if False else "*DEDICATED TO THE MEMORY OF MY FRIEND DAVID H. PINSENT*",
                 "motto": "Motto: … und alles, was man weiss, nicht bloss rauschen und brausen gehört hat, "
                          "lässt sich in drei Worten sagen.\n*Kürnberger*",
                 "preface_title": "Vorwort", "preface": d[lang]["front_raw"]}
        miss = "fehlt"
    else:
        p["1"] = p["1"].rstrip("*") + "[^1]"
        p["6.32"] = p["6.32"].rstrip("*") + "[^2]"
        fns["1"] = re.sub(r"^\*\s*", "", d[lang]["notes"][0][1])
        fns["2"] = re.sub(r"^\*\s*", "", d[lang]["notes"][1][1])
        title = "Tractatus Logico-Philosophicus — English translation by C. K. Ogden (1961 impression)"
        note = ("Ludwig Wittgenstein. Tractatus Logico-Philosophicus. With an introduction by Bertrand Russell. "
                "London: Routledge & Kegan Paul, 1961 (Ogden–Ramsey translation of 1922). Text re-OCRed from the "
                "scan (tesseract), proposition numbers restored against the canonical list; italics are lost and "
                "formulas/tables are only partly legible. Arranged as a «logical tree» after the Russian "
                "edition of 2023.")
        front = {"dedication": "*DEDICATED TO THE MEMORY OF MY FRIEND DAVID H. PINSENT*",
                 "motto": "Motto: … und alles, was man weiss, nicht bloss rauschen und brausen gehört hat, "
                          "lässt sich in drei Worten sagen.\n*Kürnberger*",
                 "preface_title": "Preface", "preface": d[lang]["front_raw"]}
        miss = "missing"
    srcs61[lang] = {"title": title, "note": note, "front": front, "props": p, "footnotes": fns,
                    "missing_label": miss, "notes_title": "Anmerkungen" if lang == "de" else "Notes"}

ALL = {
    "tlp_ru_2023_korolev": src23,
    "tlp_ru_2005_rudnev": src05,
    "tlp_de_1961": srcs61["de"],
    "tlp_en_1961_ogden": srcs61["en"],
}
for name, src in ALL.items():
    have = set(src["props"])
    print(name, "положений:", len(have & set(canon)), "нет:", sorted(set(canon) - have, key=tlp_tree.key),
          "лишних:", sorted(have - set(canon)))
    md = render(src, canon)
    open(f"{OUT}/{name}.md", "w").write(md)
    json.dump(tree_json(src, canon), open(f"{OUT}/{name}.json", "w"), ensure_ascii=False, indent=1)
    json.dump(src, open(f"{W}/norm_{name}.json", "w"), ensure_ascii=False, indent=1)
