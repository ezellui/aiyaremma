import io, sys, re
P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt} вхождений, нашёл {n}: {old[:80]!r}'
    src = src.replace(old, new, cnt)

# ── 1. DEFAULTS ────────────────────────────────────────────────────────────
rep("""  quiresMarginVertical: null,
  pages: null,            // null = все""",
"""  quiresMarginVertical: null,
  // PATCH NATURAL-SIZE: физический размер ОДНОГО фолио в миллиметрах.
  // Действует там, где лист выводится из геометрии фолио, а не из формата
  // бумаги: --page-size=native, --quires-sheet=native, --spread-sheet=native.
  //   обе null — прежнее поведение: 1 CSS-px → 1 pt
  //              (620×820 px → 218.7×289.3 мм, лист-бифолий 437×289 мм);
  //   задана одна — вторая берётся из пропорций фолио (620:820 = 0.7561);
  //   заданы обе — вписывание с сохранением пропорций (масштаб = min).
  // Замысел HTML (комментарий к .folio: «~165 × 130 мм … pocket gospel-book,
  // Book of Dimma / Mulling») даётся ключом --print-folio-height=165 →
  // фолио 124.8 × 165.0 мм. Ровно 130 × 165 недостижимо: это другая
  // пропорция, чем 620:820, а растягивать фолио для факсимиле нельзя.
  printFolioWidth:  null,
  printFolioHeight: null,
  // PATCH CARRIER: лист-носитель. PDF-страница расширяется до формата бумаги,
  // обрезной лист вместе с вылетами и метками центрируется на нём. Нужно,
  // чтобы драйвер принтера не масштабировал нестандартный размер «под лист»:
  // страница уже A4/A3, «натуральная величина» переживает печать.
  //   none (default) — страница ровно trim + bleed;
  //   a4 / a3        — ориентация выбирается автоматически по пропорциям
  //                    листа; если лист не влезает — предупреждение и none.
  carrier: 'none',
  // PATCH BLEED-FILL: чем заполнять полосы вылета.
  //   auto (default) — stretch там, где фолио упирается в линию реза,
  //                    иначе ничего (белое поле листа);
  //   stretch        — растянуть краевой ряд пикселей фолио наружу.
  //                    Настоящий вылет: тон, фактура и постарение края
  //                    продолжаются за линию реза, стыка не видно;
  //   flat           — сплошная заливка #ccb98c (поведение до этого патча);
  //   none           — оставить белым.
  bleedFill: 'auto',
  // PATCH FOLD-MARKS: метки фальцовки по центру листа — там, где бифолий
  // складывается пополам. Рисуются в полосе вылета сверху и снизу, штрихом
  // вдвое короче меток реза, чтобы не путать их с линией отреза.
  //   null = авто: включены вместе с --crop-marks в quires и booklet.
  foldMarks: null,
  pages: null,            // null = все""")

# ── 2. bool-флаги в парсере ────────────────────────────────────────────────
rep("""      } else if (key === 'hide-scrollbars' || key === 'no-hide-scrollbars') {
        val = key === 'hide-scrollbars';
        key = 'hide-scrollbars';
        i++;""",
"""      } else if (key === 'hide-scrollbars' || key === 'no-hide-scrollbars') {
        val = key === 'hide-scrollbars';
        key = 'hide-scrollbars';
        i++;
      // PATCH PRINT-FLAGS: crop-marks и fold-marks — тоже bool-флаги.
      // До этого патча голый --crop-marks съедал следующий аргумент, если
      // тот не начинался с дефиса, и приходилось писать --crop-marks=1.
      } else if (key === 'crop-marks' || key === 'no-crop-marks') {
        val = key === 'crop-marks';
        key = 'crop-marks';
        i++;
      } else if (key === 'fold-marks' || key === 'no-fold-marks') {
        val = key === 'fold-marks';
        key = 'fold-marks';
        i++;""")

# ── 3. case-ветки ──────────────────────────────────────────────────────────
rep("""      case 'quires-margin-vertical':    cfg.quiresMarginVertical = parseFloat(val); break;""",
"""      case 'quires-margin-vertical':    cfg.quiresMarginVertical = parseFloat(val); break;
      // PATCH NATURAL-SIZE / CARRIER / BLEED-FILL / FOLD-MARKS
      case 'print-folio-width':         cfg.printFolioWidth  = parseFloat(val); break;
      case 'print-folio-height':        cfg.printFolioHeight = parseFloat(val); break;
      case 'carrier':                   cfg.carrier   = String(val).toLowerCase(); break;
      case 'bleed-fill':                cfg.bleedFill = String(val).toLowerCase(); break;
      case 'fold-marks':                cfg.foldMarks = (val === true || val === 'true' || val === '1'); break;
      case 'no-fold-marks':             cfg.foldMarks = false; break;""")

# ── 4. валидация ───────────────────────────────────────────────────────────
rep("""  if (cfg.quiresMarginVertical !== null && !(cfg.quiresMarginVertical >= 0)) {
    throw new Error(`--quires-margin-vertical должен быть ≥ 0, не "${cfg.quiresMarginVertical}"`);
  }""",
"""  if (cfg.quiresMarginVertical !== null && !(cfg.quiresMarginVertical >= 0)) {
    throw new Error(`--quires-margin-vertical должен быть ≥ 0, не "${cfg.quiresMarginVertical}"`);
  }
  // PATCH NATURAL-SIZE / CARRIER / BLEED-FILL
  if (cfg.printFolioWidth !== null && !(cfg.printFolioWidth > 0 && cfg.printFolioWidth <= 1000)) {
    throw new Error(`--print-folio-width должен быть в (0..1000] мм, не "${cfg.printFolioWidth}"`);
  }
  if (cfg.printFolioHeight !== null && !(cfg.printFolioHeight > 0 && cfg.printFolioHeight <= 1000)) {
    throw new Error(`--print-folio-height должен быть в (0..1000] мм, не "${cfg.printFolioHeight}"`);
  }
  if (!['none', 'a4', 'a3'].includes(cfg.carrier)) {
    throw new Error(`--carrier должен быть none, a4 или a3, не "${cfg.carrier}"`);
  }
  if (!['auto', 'stretch', 'flat', 'none'].includes(cfg.bleedFill)) {
    throw new Error(`--bleed-fill должен быть auto, stretch, flat или none, не "${cfg.bleedFill}"`);
  }
  // --print-folio-* работает только там, где лист выводится из фолио.
  const _naturalSizeApplies =
    (cfg.pageSize === 'native') ||
    (cfg.pageSize === 'quires'  && cfg.quiresSheet === 'native') ||
    (cfg.pageSize === 'spreads' && cfg.spreadSheet === 'native');
  if ((cfg.printFolioWidth !== null || cfg.printFolioHeight !== null) && !_naturalSizeApplies) {
    console.log(`  ⚠ --print-folio-* игнорируется: при page-size=${cfg.pageSize}` +
      (cfg.pageSize === 'quires' ? `/quires-sheet=${cfg.quiresSheet}` : '') +
      (cfg.pageSize === 'spreads' ? `/spread-sheet=${cfg.spreadSheet}` : '') +
      ` размер листа задан форматом бумаги, а фолио вписывается в него aspect-fit'ом`);
  }
  if (cfg.pageSize === 'quires' && cfg.quiresSheet !== 'native' && cfg.bleed > 0) {
    console.log(`  ⚠ --bleed при --quires-sheet=${cfg.quiresSheet}: фолио вписано внутрь листа и не доходит до линии реза,` +
      ` вылет получится пустым полем, а метки реза разметят край ${cfg.quiresSheet.toUpperCase()}, а не бифолий.` +
      ` Для типографской сборки нужен --quires-sheet=native.`);
  }""")

open(P, 'w', encoding='utf-8').write(src)
print('patch1 ok')
