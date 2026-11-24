

# ── A. 07 §12 ───────────────────────────────────────────────────────
patch(P07, D58_OLD, D58_NEW, "A1 Д-58 — пять видов")
patch(P07, RULE3_OLD, RULE3_NEW, "A2 правило 3 — строка 12.4 о поле id на место")
patch(P07, RULE3_ORPHAN_OLD, RULE3_ORPHAN_NEW, "A3 правило 3 — пометка 2026-10-14")

rows_md = "".join(
    f"| {n} | {kind} | {text} | {src} | {addr} | открыт |\n"
    for n, kind, addr, text, src in ROWS
)
_t07 = rd(P07)
_d64 = [l for l in _t07.split("\n") if l.startswith("| Д-64 |")]
if len(_d64) == 1:
    patch(P07, _d64[0] + "\n", _d64[0] + "\n" + rows_md, "A4 Д-65…Д-75",
          marker="| Д-65 |")
else:
    failed += 1
    print(f"  fail  A4 Д-65…Д-75: строк Д-64 — {len(_d64)}")

for n in ("1", "2", "3", "4", "6", "7"):
    drop_row(P07, f"| Огр-{n} |", f"A5 снять Огр-{n}")
replace_row(P07, OGR10_OLD_PREFIX, OGR10_NEW, "A6 Огр-10 — только BYO-ключ")

# ── B. 07 §8, §11 ───────────────────────────────────────────────────
patch(P07, PHASE13_ADD_OLD, PHASE13_ADD_NEW, "B1 врезка «Фаза 13» += 13.2",
      marker="**Беседа 13.2 (добавлена 2026-10-14).**")
patch(P07, "### Фаза 14 (добавлена 2026-10-13): довершение локализации\n",
      CONV_132 + "### Фаза 14 (добавлена 2026-10-13): довершение локализации\n",
      "B2 беседа 13.2", marker="### Беседа 13.2: Утечки и лимитер запросов")
patch(P07, "### Типовая беседа L: новый язык интерфейса",
      PHASE15 + "### Типовая беседа L: новый язык интерфейса",
      "B3 Фаза 15", marker="### Фаза 15 (добавлена 2026-10-14)")

_t07 = rd(P07)
_g = [l for l in _t07.split("\n") if l.startswith(GRAPH_OLD_TAIL)]
if len(_g) == 1:
    patch(P07, _g[0] + "\n", _g[0] + "\n" + GRAPH_ADD, "B4 §11 — узлы 13.2, 15.1–15.4",
          marker="13.2 (утечки и лимитер:")
else:
    failed += 1
    print(f"  fail  B4 §11: строк 14.2 — {len(_g)}")
patch(P07, ORDER_OLD, ORDER_NEW, "B5 §11 — порядок Фазы 13")
patch(P07, ORDER14_ANCHOR, ORDER14_NEW + ORDER15, "B6 §11 — порядок Фаз 14 и 15",
      marker=ORDER15)

# ── C. 06, README, NEXT-CONTEXT, 08 ─────────────────────────────────
patch(P06, P06_13_OLD, P06_13_NEW, "C1 06 — Фаза 13 ≈2 сессии")
patch(P06, P06_13_ADD_OLD, P06_13_ADD_NEW, "C2 06 — 13.2",
      marker="**13.2. Утечки и лимитер запросов**")
patch(P06, P06_15_OLD, P06_15_NEW, "C3 06 — Фаза 15",
      marker="### Фаза 15: Снятие ограничений")
patch("README.md", README_13_OLD, README_13_NEW, "C4 README — строка Фазы 13")
patch("README.md", README_15_OLD, README_15_NEW, "C5 README — строка Фазы 15",
      marker="| 15 — снятие ограничений |")
patch("README.md", README_REG_OLD, README_REG_NEW, "C6 README — реестр")
patch("NEXT-CONTEXT.md", NC_HEAD_OLD, NC_HEAD_NEW, "C7 NEXT-CONTEXT — заголовок состояния")
patch("NEXT-CONTEXT.md", NC_PARA_OLD, NC_PARA_NEW, "C8 NEXT-CONTEXT — порядок фаз")
patch(P08, H08_OLD, H08_NEW, "C9 08 Часть III — врезка",
      marker="> **Правки 2026-10-14 (вне бесед — ревизия ограничений")

print(f"\napplied={applied} skip={skipped} fail={failed}")
sys.exit(1 if failed else 0)
