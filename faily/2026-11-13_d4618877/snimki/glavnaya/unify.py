"""Единое оформление схем, таблиц и формул во всех редакциях.

Содержание каждой редакции (слова переводчика, его обозначения: →, &, И/Л) не меняется —
меняется только способ набора, чтобы одно и то же место «Трактата» выглядело во всех
редакциях одинаково:
  • таблицы истинности 4.31, 4.442, 5.101 — таблицами (в 2005 г. 4.31 был моноширинным блоком,
    5.101 — строками);
  • рисунки 5.5423 (куб) и 6.36111 (прямая) — общими схемами SVG во всех редакциях;
  • выключные формулы 6.02 и 6.241 — TeX, как в 1961 г.; индексы 5.15/5.151 ($W_r$, $\\text{И}_r$),
    «+c» в 5.02 ($+_c$), ½ в 5.152;
  • остатки вёрстки (обрывки строк в моноширинных блоках) — убраны.
Вызывается из build_all.py после fixes.py; каждое правило проверяет, что сработало.
"""
import re
from fixes import tt431


def _sub(t, old, new, num, ed, count=1):
    if isinstance(old, str):
        if t.count(old) != count:
            raise SystemExit(f"unify: {ed} {num}: «{old[:50]}» найдено {t.count(old)} раз")
        return t.replace(old, new)
    t2, n = old.subn(new if callable(new) else (lambda m: new), t)
    if n != count:
        raise SystemExit(f"unify: {ed} {num}: /{old.pattern[:50]}/ найдено {n} раз")
    return t2


R = lambda rx: re.compile(rx, re.S)
TAB = "| | | | |\n|:-|:-|:-|:-|\n"
FORM_OK = re.compile(r"^[\s()\[\]pqrs,.;:|∼~&→⊃∨≡×\-или*]*$")


def table5101_2005(t):
    """Строки «(ИИИИ) (p, q) слова (формула).» → таблица в четыре столбца, как у других."""
    head, rest = t.split("\n\n", 1)
    lines, tail = [], []
    for para in rest.split("\n\n"):
        m = re.match(r"\(([ИЛ]{4})\) \(\*p, q\*\)\s*(.*)$", para)
        if not m:
            tail.append(para); continue
        tv, body = " ".join(m.group(1)), m.group(2).strip()
        body = re.sub(r"\*\.\*$", ".", body)
        words, form = body, ""
        for i in [k for k, c in enumerate(body) if c == "("]:
            if FORM_OK.match(body[i:]) and i > 0:
                words, form = body[:i].strip(), body[i:].strip()
                break
        clean = lambda s: re.sub(r"\*", "", s).replace("|", "\\|").strip()
        form = clean(form).rstrip(".")
        lines.append(f"| ({tv}) | (p, q) | {clean(words)} | {form} |")
    return head + "\n\n" + TAB + "\n".join(lines) + "\n\n" + "\n\n".join(tail)


def tex(s):
    return s


T602_05 = ("И так мы приходим к числам. Я определяю\n\n"
           "$$x = \\Omega^{0\\prime}x \\quad \\text{Def.}\\quad\\text{и}$$\n\n"
           "$$\\Omega^{\\prime}\\Omega^{n\\prime}x = \\Omega^{n+1\\prime}x \\quad \\text{Def.}$$\n\n"
           "Поэтому, следуя данным знаковым правилам, мы ряд *x*, Ω’*x*, Ω’Ω’*x*, Ω’Ω’Ω’*x*, ... запишем так:\n\n"
           "$$\\Omega^{0\\prime}x,\\ \\Omega^{0+1\\prime}x,\\ \\Omega^{0+1+1\\prime}x,\\ \\Omega^{0+1+1+1\\prime}x,\\ \\ldots$$\n\n"
           "Стало быть, вместо «[*x*, *x*, Ω’, *x*]» пишем\n\n"
           "$$[\\Omega^{0\\prime}x,\\ \\Omega^{n\\prime}x,\\ \\Omega^{n+1\\prime}x]$$\n\n"
           "И даем определения:\n\n0 + 1 = 1 Def.,\n\n0 + 1 + 1 = 2 Def.,\n\n0 + 1 + 1 + 1 = 3 Def.,\n\n(и т. д.).")
T602_23 = ("Вот так мы приходим к числам. Я даю следующие определения:\n\n"
           "$$x = \\Omega^{0\\prime}x \\quad \\text{Def.}\\quad\\text{и}$$\n\n"
           "$$\\Omega^{\\prime}\\Omega^{\\nu\\prime}x = \\Omega^{\\nu+1\\prime}x \\quad \\text{Def.}$$\n\n"
           "Итак, в соответствии с этими правилами сочетаний знаков мы записываем последовательность\n\n"
           "*x*, Ω′*x*, Ω′Ω′*x*, Ω′Ω′Ω′*x*, ...\n\nв виде\n\n"
           "$$\\Omega^{0\\prime}x,\\ \\Omega^{0+1\\prime}x,\\ \\Omega^{0+1+1\\prime}x,\\ \\Omega^{0+1+1+1\\prime}x,\\ \\ldots$$\n\n"
           "Поэтому вместо [*x*, ξ, Ω’ξ] я пишу\n\n"
           "$$[\\Omega^{0\\prime}x,\\ \\Omega^{\\nu\\prime}x,\\ \\Omega^{\\nu+1\\prime}x]$$\n\n"
           "И даю следующие определения:\n\n0 + 1 = 1 Def.,\n\n0 + 1 + 1 = 2 Def.,\n\n0 + 1 + 1 + 1 = 3 Def.\n\n(и т. д.).")
P6241 = ("$$\\Omega^{2\\times2\\prime}x = (\\Omega^{2})^{2\\prime}x = (\\Omega^{2})^{1+1\\prime}x = \\Omega^{2\\prime}\\Omega^{2\\prime}x"
         " = \\Omega^{1+1\\prime}\\Omega^{1+1\\prime}x$$\n\n"
         "$$= (\\Omega^{\\prime}\\Omega)^{\\prime}(\\Omega^{\\prime}\\Omega)^{\\prime}x = \\Omega^{\\prime}\\Omega^{\\prime}\\Omega^{\\prime}\\Omega^{\\prime}x"
         " = \\Omega^{1+1+1+1\\prime}x = \\Omega^{4\\prime}x.$$")
T6241_05 = ("Вот что гласит доказательство Пропозиции 2 × 2 = 4:\n\n"
            "$$(\\Omega^{n})^{m\\prime}x = \\Omega^{n\\times m\\prime}x \\quad \\text{Def.}$$\n\n" + P6241)
T6241_23 = ("Доказательство высказывания 2 × 2 = 4 выглядит следующим образом:\n\n"
            "$$(\\Omega^{\\nu})^{\\mu\\prime}x = \\Omega^{\\nu\\times\\mu\\prime}x \\quad \\text{Def.}$$\n\n" + P6241)

RULES = {
    "ru2005": [
        ("4.013", "употребле-\n\n```\nния    и   в нотах).\n```", "употребления ♯ и ♭ в нотах)."),
        ("4.31", R(r"\n\n```\n\s*p\s+q\s+r\s+p\s+q\s+r.*?```"), "\n\n" + tt431("И", "Л")),
        ("5.101", table5101_2005, None),
        ("5.02", "«+*с*» «*с*»", "«$+_c$» «*c*»"),
        ("5.02", "вместо «+*с*»", "вместо «$+_c$»"),
        ("5.15", "*Иr*", "$\\text{И}_r$"), ("5.15", "*Иr s*", "$\\text{И}_{rs}$"),
        ("5.15", "*Иrs* : *Иr*", "$\\text{И}_{rs} : \\text{И}_r$"),
        ("5.151", "*Иr*", "$\\text{И}_r$"), ("5.151", "*Иrs* —", "$\\text{И}_{rs}$ —"),
        ("5.151", "*Иrs* : *И r* .", "$\\text{И}_{rs} : \\text{И}_r$."),
        ("5.152", "*Ѕ*", "½"),
        ("5.5423", R(r"фигуру\n\n```.*?```\n\n\*b\*\n\n\*b\*\n\n\*a\*\n\n\*a\* можно"), "фигуру\n\n![](fig:5.5423)\n\nможно"),
        ("6.02", R(r"\A.*\Z"), T602_05),
        ("6.241", R(r"\A.*\Z"), T6241_05),
        ("6.36111", R(r"\n\n```\n\s*a\s+b\n```\n\n"), "\n\n![](fig:6.36111)\n\n"),
    ],
    "ru2023": [
        ("4.26", R(r"истин-\n\n```\nны, а какие ложны\.\s*n\n```"), "истинны, а какие ложны."),
        ("5.101", " ν ", " ∨ ", 2),
        ("5.02", "«+*c*»", "«$+_c$»", 2),
        ("5.15", "И*rs* : И*r*", "$\\text{И}_{rs} : \\text{И}_r$"),
        ("5.15", "И*rs*", "$\\text{И}_{rs}$"), ("5.15", "И*r*", "$\\text{И}_r$"),
        ("5.151", "И*rs* : И*r*", "$\\text{И}_{rs} : \\text{И}_r$"),
        ("5.151", "И*rs*", "$\\text{И}_{rs}$"), ("5.151", "И*r*", "$\\text{И}_r$"),
        ("5.152", "<sup>1</sup>/2", "½"),
        ("5.5423", "восприятия фигуры ниже как куба", "восприятия фигуры ниже\n\n![](fig:5.5423)\n\nкак куба"),
        ("6.02", R(r"\A.*\Z"), T602_23),
        ("6.241", R(r"\A.*\Z"), T6241_23),
        ("6.36111", R(r"\n\n```\n[^`]*a × ×\s+b °\n```\n\n"), "\n\n![](fig:6.36111)\n\n"),
    ],
}


def apply(props, ed):
    for rule in RULES.get(ed, []):
        num, old = rule[0], rule[1]
        if callable(old) and not isinstance(old, re.Pattern):
            props[num] = old(props[num]); continue
        new = rule[2]
        cnt = rule[3] if len(rule) > 3 else 1
        props[num] = _sub(props[num], old, new, num, ed, cnt)
    return props
