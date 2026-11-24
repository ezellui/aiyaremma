#!/usr/bin/env python3
"""Ревизия ограничений 07 §12 (2026-10-14, вне бесед; решения пользователя):
беседа 13.2 «Утечки и лимитер запросов» и Фаза 15 «Снятие ограничений».
Идёт ПОСЛЕ patch-docs-phase13-14.py; оба — в одном коммите.

Вопрос пользователя: какие ограничения устранимы без коренной переделки
архитектуры. Ответ принят: все, кроме Огр-5, Огр-11 и трёх закреплённых
решений (Огр-8, Огр-9, Огр-12); у Огр-10 остаётся половина о BYO-ключе.
Для Огр-2 и Огр-7 — «как надёжнее» (отвязка только поверх узла дерева
файла; тарифы в БД редакциями).
  A  07 §12 — Д-65…Д-75 с адресатами (13.2 — Д-65, Д-66, Д-67; 15.1 —
     Д-68, Д-69, Д-70; 15.2 — Д-71; 15.3 — Д-72, Д-73; 15.4 — Д-74,
     Д-75); строки Огр-1…Огр-4, Огр-6, Огр-7 сняты, Огр-10 сужен;
     правило 3 — пометка и возврат строки 12.4 о поле `id` на место;
     Д-58 — «пять видов».
  B  07 §8 — врезка «Фаза 13» += 13.2, беседа 13.2 перед Фазой 14;
     Фаза 15 (15.1–15.4) перед шаблоном L; §11 — узлы и порядок.
  C  06 §2, README, NEXT-CONTEXT, 08 Часть III.
Идемпотентен (new-in-text проверяется ПЕРВЫМ). Запуск из корня репо:
    python3 scripts/patches/patch-docs-phase13-2-15.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
P07 = "docs/07-conversation-protocol.md"
P08 = "docs/08-history.md"
P06 = "docs/06-dev-strategy.md"
applied = skipped = failed = 0


def rd(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def wr(rel, text):
    (ROOT / rel).write_text(text, encoding="utf-8")


def patch(rel, old, new, label, marker=None):
    global applied, skipped, failed
    text = rd(rel)
    if (marker or new) in text:
        skipped += 1
        print(f"  skip  {label}")
        return
    if text.count(old) != 1:
        failed += 1
        print(f"  fail  {label}: исходный фрагмент встречается {text.count(old)} раз")
        return
    wr(rel, text.replace(old, new))
    applied += 1
    print(f"  ok    {label}")


def drop_row(rel, prefix, label):
    """Снять строку таблицы, начинающуюся с prefix (нет строки — skip)."""
    global applied, skipped, failed
    lines = rd(rel).split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if not hits:
        skipped += 1
        print(f"  skip  {label}")
        return
    if len(hits) != 1:
        failed += 1
        print(f"  fail  {label}: строк {len(hits)}")
        return
    del lines[hits[0]]
    wr(rel, "\n".join(lines))
    applied += 1
    print(f"  ok    {label}")


def replace_row(rel, prefix, new, label):
    global applied, skipped, failed
    text = rd(rel)
    if new in text:
        skipped += 1
        print(f"  skip  {label}")
        return
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hits) != 1:
        failed += 1
        print(f"  fail  {label}: строк {len(hits)}")
        return
    lines[hits[0]] = new
    wr(rel, "\n".join(lines))
    applied += 1
    print(f"  ok    {label}")
