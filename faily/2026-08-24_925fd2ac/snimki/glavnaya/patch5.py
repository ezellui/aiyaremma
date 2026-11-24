P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt}, нашёл {n}: {old[:90]!r}'
    src = src.replace(old, new, cnt)

# ── DEFAULTS ──────────────────────────────────────────────────────────────
rep("""  foldMarks: null,
  pages: null,            // null = все""",
"""  foldMarks: null,
  // PATCH FOLIO-EDGE: у .folio в HTML стоит
  //   clip-path: polygon(3px 3px, calc(100% - 3px) 3px, …)
  // — краска обрезана на 3 px внутрь по всему периметру, диагонали внизу
  // дают «сбитые уголки». На экране это незаметно: за фолио лежит тёмный
  // фон разворота. Но захват идёт по border-box, и эти 3 px попадают
  // в вывод как чужая подложка:
  //   • в mode=vector изоляция делает фон прозрачным → 3 px белые.
  //     На бифолии два соседних фолио дают белый шов 6 px (≈1.1 мм)
  //     ровно по линии сгиба;
  //   • в mode=raster в них попадает фон разворота → тёмная рама,
  //     из которой --bleed-fill=stretch тянет наружу не пергамент,
  //     а подложку.
  // Лечение: тот же полигон, сдвинутый к краям — срезанные уголки
  // сохраняются, инсет обнуляется.
  //   auto (default) — square там, где фолио доходит до линии реза
  //                    (page-size = native / quires / spreads);
  //   square         — всегда обнулять инсет;
  //   as-is          — не трогать HTML (поведение до этого патча).
  folioEdge: 'auto',
  pages: null,            // null = все""")

# ── парсер ────────────────────────────────────────────────────────────────
rep("""      case 'no-fold-marks':             cfg.foldMarks = false; break;""",
"""      case 'no-fold-marks':             cfg.foldMarks = false; break;
      case 'folio-edge':                cfg.folioEdge = String(val).toLowerCase(); break;""")

# ── валидация ─────────────────────────────────────────────────────────────
rep("""  if (!['auto', 'stretch', 'flat', 'none'].includes(cfg.bleedFill)) {
    throw new Error(`--bleed-fill должен быть auto, stretch, flat или none, не "${cfg.bleedFill}"`);
  }""",
"""  if (!['auto', 'stretch', 'flat', 'none'].includes(cfg.bleedFill)) {
    throw new Error(`--bleed-fill должен быть auto, stretch, flat или none, не "${cfg.bleedFill}"`);
  }
  if (!['auto', 'square', 'as-is'].includes(cfg.folioEdge)) {
    throw new Error(`--folio-edge должен быть auto, square или as-is, не "${cfg.folioEdge}"`);
  }""")

# ── резолв режима + инжекция ──────────────────────────────────────────────
rep("""  const wantParchOverride = (cfg.parchmentVariant !== 'auto');
  const anyVisualChange = wantAbbrExpansion || wantMgExpansion || wantMgHidden ||
                          wantNoAging || wantFolScale || wantFolDensity || wantParchOverride;""",
"""  const wantParchOverride = (cfg.parchmentVariant !== 'auto');
  // PATCH FOLIO-EDGE: обнулять ли 3-пиксельный инсет clip-path у .folio.
  // auto — только в режимах, где фолио доходит до линии реза листа.
  const wantSquareEdge = (cfg.folioEdge === 'square') ||
    (cfg.folioEdge === 'auto' &&
     ['native', 'quires', 'spreads'].includes(cfg.pageSize));
  const anyVisualChange = wantAbbrExpansion || wantMgExpansion || wantMgHidden ||
                          wantNoAging || wantFolScale || wantFolDensity ||
                          wantParchOverride || wantSquareEdge;""")

rep("""      parchOverride: wantParchOverride ? cfg.parchmentVariant : null,
    };""",
"""      parchOverride: wantParchOverride ? cfg.parchmentVariant : null,
      squareEdge: wantSquareEdge,
    };""")

# правило в инжектируемый stylesheet: ищем начало textContent и добавляем в конец
rep("""      style.id = 'codex-to-pdf-visual-overrides';
      style.textContent = `""",
"""      style.id = 'codex-to-pdf-visual-overrides';
      style.textContent = `
        /* PATCH FOLIO-EDGE (см. cfg.folioEdge): исходный полигон .folio
           обрезает краску на 3 px внутрь по периметру. Здесь тот же контур,
           сдвинутый к краям border-box: срезанные нижние уголки (диагонали
           по 7 px) сохранены, инсет обнулён. Класс вешается на body только
           при squareEdge. */
        body.folio-square-edge .folio {
          clip-path: polygon(
            0 0,
            100% 0,
            100% calc(100% - 4px),
            calc(100% - 7px) 100%,
            7px 100%,
            0 calc(100% - 4px)
          ) !important;
        }
""")

# добавление класса на body
rep("""        ...(wantNoAging  ? ['no-aging'] : []),
      ],""",
"""        ...(wantNoAging  ? ['no-aging'] : []),
        ...(wantSquareEdge ? ['folio-square-edge'] : []),
      ],""")

rep("""    if (wantParchOverride)   summary.push(`parch=${cfg.parchmentVariant}`);""",
"""    if (wantParchOverride)   summary.push(`parch=${cfg.parchmentVariant}`);
    if (wantSquareEdge)      summary.push('folio-edge=square (инсет clip-path обнулён)');""")

# ── help ──────────────────────────────────────────────────────────────────
rep("""      --fold-marks / --no-fold-marks""",
"""      --folio-edge <auto|square|as-is>  край фолио при захвате [${DEFAULTS.folioEdge}]
                          У .folio в HTML clip-path обрезает краску на 3 px
                          внутрь по периметру (диагонали внизу — сбитые уголки).
                          Захват идёт по border-box, поэтому эти 3 px попадают
                          в вывод как чужая подложка: в mode=vector — белыми
                          (на бифолии два соседних фолио дают белый шов ≈1.1 мм
                          ровно по сгибу), в mode=raster — тёмным фоном
                          разворота, из которого --bleed-fill=stretch тянет
                          наружу подложку вместо пергамента.
                          square: тот же контур, сдвинутый к краям — срезанные
                                  уголки на месте, инсет обнулён.
                          auto:   square для page-size native/quires/spreads
                                  (там фолио доходит до линии реза), as-is
                                  для a4/booklet.
                          as-is:  не трогать HTML (поведение до этого патча).
      --fold-marks / --no-fold-marks""")

open(P, 'w', encoding='utf-8').write(src)
print('patch5 ok')
