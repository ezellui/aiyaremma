"""Ручные решения о тексте: формулы, таблицы, схемы, битые глифы (аналог glyph_map.json в HWPh).

Каждое решение: (редакция, номер, было, стало).  Если «было» = None — положение заменяется целиком.
Все формулы 1961 г. сверены с вырезками скана (14.11.2026), 2023/2005 — с вырезками PDF.
Виды записи: строчная формула $…$, выключная $$…$$, таблица Markdown, схема ![](fig:имя).
`python3 fixes.py` выгружает решения в fixes.json (для просмотра и для читалки).
"""
import json

SCHEME = "*[здесь в оригинале — графическая схема; в текстовом слое её нет]*"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(":-:" for _ in head) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def tt431(T, F):
    t3 = table(["p", "q", "r"], [[a, b, c] for a, b, c in
               [(T, T, T), (F, T, T), (T, F, T), (T, T, F), (F, F, T), (F, T, F), (T, F, F), (F, F, F)]])
    t2 = table(["p", "q"], [[a, b] for a, b in [(T, T), (F, T), (T, F), (F, F)]])
    t1 = table(["p"], [[T], [F]])
    return t3 + "\n\n" + t2 + "\n\n" + t1


def tt4442(T, F):
    return table(["p", "q", " "], [[T, T, T], [F, T, T], [T, F, " "], [F, F, T]])


# 5.101: (ряд истинности, слова, формула)
ROWS_DE = [
    ("WWWW", "Tautologie (Wenn p, so p; und wenn q, so q.)", "(p ⊃ p . q ⊃ q)"),
    ("FWWW", "in Worten: Nicht beides p und q.", "(~(p . q))"),
    ("WFWW", "„ „ Wenn q, so p.", "(q ⊃ p)"),
    ("WWFW", "„ „ Wenn p, so q.", "(p ⊃ q)"),
    ("WWWF", "„ „ p oder q.", "(p ∨ q)"),
    ("FFWW", "„ „ Nicht q.", "(~q)"),
    ("FWFW", "„ „ Nicht p.", "(~p)"),
    ("FWWF", "„ „ p, oder q, aber nicht beide.", "(p . ~q : ∨ : q . ~p)"),
    ("WFFW", "„ „ Wenn p, so q; und wenn q, so p.", "(p ≡ q)"),
    ("WFWF", "„ „ p", ""),
    ("WWFF", "„ „ q", ""),
    ("FFFW", "„ „ Weder p noch q.", "(~p . ~q) oder (p | q)"),
    ("FFWF", "„ „ p und nicht q.", "(p . ~q)"),
    ("FWFF", "„ „ q und nicht p.", "(q . ~p)"),
    ("WFFF", "„ „ q und p.", "(q . p)"),
    ("FFFF", "Kontradiktion (p und nicht p; und q und nicht q.)", "(p . ~p . q . ~q)"),
]
ROWS_EN = [
    ("TTTT", "Tautology (if p then p, and if q then q)", "[p ⊃ p . q ⊃ q]"),
    ("FTTT", "in words: Not both p and q.", "[~(p . q)]"),
    ("TFTT", "„ „ If q then p.", "[q ⊃ p]"),
    ("TTFT", "„ „ If p then q.", "[p ⊃ q]"),
    ("TTTF", "„ „ p or q.", "[p ∨ q]"),
    ("FFTT", "„ „ Not q.", "[~q]"),
    ("FTFT", "„ „ Not p.", "[~p]"),
    ("FTTF", "„ „ p or q, but not both.", "[p . ~q : ∨ : q . ~p]"),
    ("TFFT", "„ „ If p, then q; and if q, then p.", "[p ≡ q]"),
    ("TFTF", "„ „ p", ""),
    ("TTFF", "„ „ q", ""),
    ("FFFT", "„ „ Neither p nor q.", "[~p . ~q or p | q]"),
    ("FFTF", "„ „ p and not q.", "[p . ~q]"),
    ("FTFF", "„ „ q and not p.", "[q . ~p]"),
    ("TFFF", "„ „ p and q.", "[p . q]"),
    ("FFFF", "Contradiction (p and not p; and q and not q.)", "[p . ~p . q . ~q]"),
]


def t5101(rows):
    return table(["", "", "", ""], [[f"({' '.join(r)})", "(p, q)", w, f] for r, w, f in rows]).replace(
        "|  |  |  |  |\n|:-:|:-:|:-:|:-:|\n", "| | | | |\n|:-|:-|:-|:-|\n")


F6 = "[p̄, ξ̄, N(ξ̄)]"
F601 = "[ξ̄, N(ξ̄)]’(η̄) (= [η̄, ξ̄, N(ξ̄)])"
F6241 = ("$$(\\Omega^{\\nu})^{\\mu\\prime}x = \\Omega^{\\nu\\times\\mu\\prime}x \\quad \\text{Def.}$$\n\n"
         "$$\\Omega^{2\\times2\\prime}x = (\\Omega^{2})^{2\\prime}x = (\\Omega^{2})^{1+1\\prime}x = "
         "\\Omega^{2\\prime}\\Omega^{2\\prime}x = \\Omega^{1+1\\prime}\\Omega^{1+1\\prime}x$$\n\n"
         "$$= (\\Omega^{\\prime}\\Omega)^{\\prime}(\\Omega^{\\prime}\\Omega)^{\\prime}x = "
         "\\Omega^{\\prime}\\Omega^{\\prime}\\Omega^{\\prime}\\Omega^{\\prime}x = "
         "\\Omega^{1+1+1+1\\prime}x = \\Omega^{4\\prime}x.$$")
F602 = {
    "def": "$$x = \\Omega^{0\\prime}x \\quad \\text{Def. %s}$$\n\n"
           "$$\\Omega^{\\prime}\\Omega^{\\nu\\prime}x = \\Omega^{\\nu+1\\prime}x \\quad \\text{Def.}$$",
    "series": "x, Ω’x, Ω’Ω’x, Ω’Ω’Ω’x, …",
    "as": "$$\\Omega^{0\\prime}x,\\ \\Omega^{0+1\\prime}x,\\ \\Omega^{0+1+1\\prime}x,\\ \\Omega^{0+1+1+1\\prime}x,\\ \\ldots$$",
    "instead": "„[x, ξ, Ω’ξ]“",
    "new": "$$[\\Omega^{0\\prime}x,\\ \\Omega^{\\nu\\prime}x,\\ \\Omega^{\\nu+1\\prime}x]$$",
    "defs": "0 + 1 = 1 Def.\n\n0 + 1 + 1 = 2 Def.\n\n0 + 1 + 1 + 1 = 3 Def.",
}

FIXES = [
    # ------------------------------------------------------------ 2023 (Королев)
    ("ru2023", "4.013", "��[диез]", "♯ [диез]"),
    ("ru2023", "4.013", "��[бемоль]", "♭ [бемоль]"),
    ("ru2023", "4.442", "«�»", "«⊢»"),
    ("ru2023", "6.01", "η�", "η̄"),
    ("ru2023", "6.01", "*N*(̄ξ)", "*N*(ξ̄)"),
    ("ru2023", "4.27", None, "Для всякой позиции имеется $K_n = \\sum_{\\nu=0}^{n}\\binom{n}{\\nu}$ "
                             "возможностей существования и несуществования.\n\n"
                             "Любая комбинация этих позиций может существовать, тогда как прочие существовать не будут."),
    ("ru2023", "4.42", None, "Для *n* числа элементарных высказываний имеется $\\sum_{x=0}^{K_n}\\binom{K_n}{x} = L_n$ "
                             "способов, какими высказывание может соотноситься или не соотноситься с возможностями истинности."),
    ("ru2023", "6.1203", "например: и использую", "например:\n\n![](fig:6.1203a)\n\nи использую"),
    ("ru2023", "6.1203", "следующим образом:\n\nВ итоге", "следующим образом:\n\n![](fig:6.1203b)\n\nВ итоге"),
    ("ru2023", "6.1203", "а форма «ξ × η» такова:\n\nПоэтому", "а форма «ξ × η» такова:\n\n![](fig:6.1203c)\n\nПоэтому"),
    ("ru2023", "6.1203", "будет выглядеть так:\n\nЕсли", "будет выглядеть так:\n\n![](fig:6.1203d)\n\nЕсли"),
    # ------------------------------------------------------------ 2005 (Руднев)
    ("ru2005", "4.27", None, "Относительно существования и несуществования *n* Положений Вещей существует "
                             "$K_n = \\sum_{\\nu=0}^{n}\\binom{n}{\\nu}$ возможностей.\n\n"
                             "Могут существовать все эти комбинации Положений Вещей, других не существует."),
    ("ru2005", "4.42", None, "Относительно согласования и несогласования Пропозиции с возможностями истинности у "
                             "Элементарной Пропозиции имеется $\\sum_{k=0}^{k_n}\\binom{k_n}{k} = L_n$ возможностей."),
    # ------------------------------------------------------------ 1961, немецкий
    ("de1961", "4.27", "gibt es K,= >> () Möglichkeiten.",
     "gibt es $K_n = \\sum_{\\nu=0}^{n}\\binom{n}{\\nu}$ Möglichkeiten."),
    ("de1961", "4.42", "gibt es Ku > (== L, Möglichkeiten.",
     "gibt es $\\sum_{\\kappa=0}^{K_n}\\binom{K_n}{\\kappa} = L_n$ Möglichkeiten."),
    ("de1961", "4.31", "Die Reihen der „‚W“", "Die Reihen der „W“"),
    ("de1961", "4.31", "Wahrheitsmöglichkeiten):", "Wahrheitsmöglichkeiten):\n\n" + tt431("W", "F")),
    ("de1961", "4.442", "Es ist z. B.:\n\nein Satzzeichen.", "Es ist z. B.:\n\n" + tt4442("W", "F") + "\n\nein Satzzeichen."),
    ("de1961", "4.442", "„Urteilstrich“ „-“", "„Urteilstrich“ „⊢“"),
    ("de1961", "4.442", "„-“ gehört", "„⊢“ gehört"),
    ("de1961", "4.442", "„(WW-W) (p,gqg)“ oder deutlicher „(WWFW) (P,q)“",
     "„(WW–W) (p, q)“ oder deutlicher „(WWFW) (p, q)“"),
    ("de1961", "5.101", None, "Die Wahrheitsfunktionen jeder Anzahl von Elementarsätzen lassen sich in einem Schema "
                              "folgender Art hinschreiben:\n\n" + t5101(ROWS_DE) +
                              "\n\nDiejenigen Wahrheitsmöglichkeiten seiner Wahrheitsargumente, welche den Satz "
                              "bewahrheiten, will ich seine Wahrheitsgründe nennen."),
    ("de1961", "5.502", None, "Ich schreibe also statt „(-----W)(ξ, ....)“ „N(ξ̄)“.\n\n"
                              "N(ξ̄) ist die Negation sämtlicher Werte der Satzvariablen ξ."),
    ("de1961", "5.51", None, "Hat ξ nur einen Wert, so ist N(ξ̄) = ~p (nicht p), hat es zwei Werte, "
                             "so ist N(ξ̄) = ~p . ~q (weder p noch q)."),
    ("de1961", "6", None, f"Die allgemeine Form der Wahrheitsfunktion ist: {F6}.\n\nDies ist die allgemeine Form des Satzes."),
    ("de1961", "6.001", "Operation N’ (£)", "Operation N’(ξ̄)"),
    ("de1961", "6.01", None, f"Die allgemeine Form der Operation Ω’(η̄) ist also: {F601}.\n\n"
                             "Das ist die allgemeinste Form des Überganges von einem Satz zum anderen."),
    ("de1961", "6.02", None, "Und so kommen wir zu den Zahlen: Ich definiere\n\n" + F602["def"] % "und" +
                             "\n\nNach diesen Zeichenregeln schreiben wir also die Reihe " + F602["series"] +
                             "\n\nso:\n\n" + F602["as"] + "\n\nAlso schreibe ich statt " + F602["instead"] + ":\n\n"
                             + F602["new"] + "\n\nUnd definiere:\n\n" + F602["defs"] + "\n\n(u. s. f.)"),
    ("de1961", "6.03", None, "Die allgemeine Form der ganzen Zahl ist: [0, ξ, ξ + 1]."),
    ("de1961", "6.241", None, "So lautet der Beweis des Satzes 2 × 2 = 4:\n\n" + F6241),
    # ------------------------------------------------------------ 1961, английский (Огден)
    ("en1961", "4.27", None, "With regard to the existence of n atomic facts there are "
                             "$K_n = \\sum_{\\nu=0}^{n}\\binom{n}{\\nu}$ possibilities.\n\n"
                             "It is possible for all combinations of atomic facts to exist, and the others not to exist."),
    ("en1961", "4.42", None, "With regard to the agreement and disagreement of a proposition with the "
                             "truth-possibilities of n elementary propositions there are "
                             "$\\sum_{\\kappa=0}^{K_n}\\binom{K_n}{\\kappa} = L_n$ possibilities."),
    ("en1961", "4.31", None, "The truth-possibilities can be presented by schemata of the following kind "
                             "(“T” means “true”, “F” “false”. The rows of T’s and F’s under the row of the "
                             "elementary propositions mean their truth-possibilities in an easily intelligible "
                             "symbolism).\n\n" + tt431("T", "F")),
    ("en1961", "4.442", "Thus e.g.\n\nis a propositional sign.", "Thus e.g.\n\n" + tt4442("T", "F") + "\n\nis a propositional sign."),
    ("en1961", "4.442", "assertion sign “|-”", "assertion sign “⊢”"),
    ("en1961", "4.442", "‘‘|_” belongs", "“⊢” belongs"),
    ("en1961", "4.442", "‘“(T T—T) (f,g)”, or more plainly: ‘(TT FT) (A:9)”",
     "“(TT–T) (p, q)”, or more plainly: “(TTFT) (p, q)”"),
    ("en1961", "5.101", None, "The truth-functions of every number of elementary propositions can be written in a "
                              "schema of the following kind:\n\n" + t5101(ROWS_EN) +
                              "\n\nThose truth-possibilities of its truth-arguments, which verify the proposition, "
                              "I shall call its truth-grounds."),
    ("en1961", "5.502", None, "Therefore I write instead of “(-----T)(ξ, ....)”, “N(ξ̄)”.\n\n"
                              "N(ξ̄) is the negation of all the values of the propositional variable ξ."),
    ("en1961", "5.51", None, "If ξ has only one value, then N(ξ̄) = ~p (not p), if it has two values then "
                             "N(ξ̄) = ~p . ~q (neither p nor q)."),
    ("en1961", "6", None, f"The general form of truth-function is: {F6}.\n\nThis is the general form of proposition."),
    ("en1961", "6.001", "operation WV’ (£)", "operation N’(ξ̄)"),
    ("en1961", "6.01", None, f"The general form of the operation Ω’(η̄) is therefore: {F601}.\n\n"
                             "This is the most general form of transition from one proposition to another."),
    ("en1961", "6.02", None, "And thus we come to numbers: I define\n\n" + F602["def"] % "and" +
                             "\n\nAccording, then, to these symbolic rules we write the series " + F602["series"] +
                             "\n\nas:\n\n" + F602["as"] + "\n\nTherefore I write in place of “[x, ξ, Ω’ξ]”,\n\n"
                             + F602["new"] + "\n\nAnd I define:\n\n" + F602["defs"] + "\n\nand so on."),
    ("en1961", "6.03", None, "The general form of the cardinal number is: [0, ξ, ξ + 1]."),
    ("en1961", "6.241", None, "Thus the proof of the proposition 2 × 2 = 4 runs:\n\n" + F6241),
]


def apply(props, ed, log=print):
    n = 0
    for e, num, old, new in FIXES:
        if e != ed:
            continue
        if old is None:
            props[num] = new
            n += 1
        elif old in props.get(num, ""):
            props[num] = props[num].replace(old, new)
            n += 1
        else:
            log(f"[{ed}] правка не применилась: {num}: {old[:50]!r}")
    return n


if __name__ == "__main__":
    json.dump([{"edition": e, "num": n, "old": o, "new": w} for e, n, o, w in FIXES],
              open("fixes.json", "w"), ensure_ascii=False, indent=1)
    print(len(FIXES), "решений")
