"""Нумерация «Трактата» и древовидная («фрактальная») раскладка, как в переводе 2023 г.

Правило родителя (Витгенштейн, примечание к 1): у n.m1, n.m2 ... родитель n.m.
Технически: отбросить последнюю цифру дробной части, затем хвостовые нули;
пустая дробная часть -> целое (раздел). Так 2.0121 -> 2.012, 2.01 -> 2, 3.001 -> 3,
6.1203 -> 6.12.  Дети одного родителя делятся на группы по числу отброшенных нулей:
у 3 это {3.001}, {3.01..3.05}, {3.1..3.5}; каждая группа — отдельная «ветвь».

Раскладка (сверена с изданием 2023 построчно):
  блок корня: 1..7;
  для каждого раздела k, у которого есть дети: заголовок раздела, затем
  для каждой группы детей узла N: [повтор N (кроме первой группы сразу под
  заголовком раздела), члены группы], затем рекурсивно поддеревья членов группы
  с детьми, по порядку; затем следующая группа.
"""
from decimal import Decimal
import re

NUM_RE = re.compile(r"^[1-7](\.\d+)?$")


def key(n):
    return Decimal(n)


def parent(n):
    if "." not in n:
        return None
    i, d = n.split(".")
    d2 = d[:-1].rstrip("0")
    return f"{i}.{d2}" if d2 else i


def group_id(n):
    """Число нулей, отброшенных при подъёме к родителю (ключ группы)."""
    i, d = n.split(".")
    return len(d[:-1]) - len(d[:-1].rstrip("0"))


def build(nums):
    nums = sorted(set(nums), key=key)
    kids = {}
    for n in nums:
        p = parent(n)
        if p is not None:
            kids.setdefault(p, []).append(n)
    groups = {}
    for p, ch in kids.items():
        g = {}
        for c in ch:
            g.setdefault(group_id(c), []).append(c)
        groups[p] = [g[k] for k in sorted(g, reverse=True)]  # больше нулей — раньше
    return nums, groups


def layout(nums):
    """Последовательность событий раскладки.

    ('root', [1..7])                 — блок корня
    ('section', k)                   — заголовок раздела k
    ('block', N, members, repeat)    — ветвь: N и его группа детей;
                                       repeat=False, если N уже стоит заголовком раздела
    """
    nums, groups = build(nums)
    roots = [n for n in nums if parent(n) is None]
    ev = [("root", roots)]

    def walk(n, first_under_section):
        for gi, g in enumerate(groups.get(n, [])):
            ev.append(("block", n, g, not (first_under_section and gi == 0)))
            for m in g:
                if m in groups:
                    walk(m, False)

    for r in roots:
        if r in groups:
            ev.append(("section", r))
            walk(r, True)
    return ev


def expected_sequence(nums):
    """Порядок появления номеров в издании 2023: (номер, роль)."""
    seq = []
    for e in layout(nums):
        if e[0] == "root":
            seq += [(n, "member") for n in e[1]]
        elif e[0] == "section":
            seq.append((e[1], "section"))
        else:
            _, n, g, rep = e
            if rep:
                seq.append((n, "head"))
            seq += [(m, "member") for m in g]
    return seq
