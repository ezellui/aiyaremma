P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt}, нашёл {n}: {old[:90]!r}'
    src = src.replace(old, new, cnt)

# ── финальная сводка по печати ────────────────────────────────────────────
rep("""  if (cfg.bleed > 0 && cfg.pageSize !== 'a4') {
    console.log(`  Print: каждая страница расширена на ${cfg.bleed}мм с каждой стороны (bleed-зона цвета пергамента).`);
    if (cfg.cropMarks && cfg.bleed >= 3) {
      console.log('          Crop-marks нарисованы в углах trim-area.');
    }
    console.log('          После типографской обрезки до trim-size получится оригинальный формат.');
  }""",
"""  if (cfg.bleed > 0 && cfg.pageSize !== 'a4') {
    const _fillDesc = {
      stretch: 'краевой ряд пикселей фолио растянут наружу',
      flat:    'сплошная заливка цвета пергамента',
      none:    'пустое поле листа',
    };
    const _fillMode = cfg.bleedFill === 'auto' ? '(auto)' : '';
    console.log(`  Print: каждая страница расширена на ${cfg.bleed}мм с каждой стороны.`);
    console.log(`          Вылет: ${_fillDesc[cfg.bleedFill] || cfg.bleedFill} ${_fillMode}`.trimEnd());
    console.log('          TrimBox / BleedBox проставлены — препресс возьмёт обрезной формат из них.');
    if (cfg.cropMarks && cfg.bleed >= 3) {
      console.log('          Метки реза — в углах trim-area.');
    }
    if ((cfg.foldMarks !== null ? cfg.foldMarks : (cfg.cropMarks && cfg.bleed >= 3)) &&
        cfg.bleed >= 3 && (cfg.pageSize === 'quires' || cfg.pageSize === 'booklet')) {
      console.log('          Метки фальцовки (короткий штрих сверху и снизу по центру) — линия сгиба, не реза.');
    }
    if (cfg.carrier !== 'none') {
      console.log(`          Лист центрирован на носителе ${cfg.carrier.toUpperCase()}: печатать «actual size / 100%», без «fit to page».`);
    }
    console.log('          После обрезки до trim-size получится оригинальный формат.');
  }""")

# ── help: новые ключи ─────────────────────────────────────────────────────
rep("""      --quires-margin-vertical <mm>  верх/низ (a4/a3)                     [= --margin]""",
"""      --quires-margin-vertical <mm>  верх/низ (a4/a3)                     [= --margin]
      --print-folio-width <mm>   физическая ширина ОДНОГО фолио [1 CSS-px → 1 pt]
      --print-folio-height <mm>  физическая высота ОДНОГО фолио [1 CSS-px → 1 pt]
                          «Натуральная величина» страницы кодекса. Работает там,
                          где лист выводится из геометрии фолио, а не из формата
                          бумаги: --page-size=native, --quires-sheet=native,
                          --spread-sheet=native.
                          Без этих ключей масштаб 1 px → 1 pt (72 dpi-эквивалент):
                          фолио 620×820px → 218.7×289.3 мм, бифолий 437×289 мм —
                          это НЕ влезает в A3 и не соответствует замыслу HTML.
                          Задана одна величина — вторая берётся из пропорций
                          фолио (620:820 = 0.7561); заданы обе — вписывание
                          с сохранением пропорций (масштаб = min).
                          Замысел HTML («~165 × 130 мм … pocket gospel-book,
                          Book of Dimma / Mulling» в комментарии к .folio):
                            --print-folio-height=165  →  124.8 × 165.0 мм,
                                                         бифолий 249.5 × 165 мм.
                          Ровно 130 × 165 недостижимо: это иная пропорция, чем
                          620:820, а растягивать фолио для факсимиле нельзя.
                          Если важнее ширина 130 мм: --print-folio-width=130
                          → 130 × 171.9 мм.
      --carrier <none|a4|a3>  лист-носитель [${DEFAULTS.carrier}]
                          PDF-страница добивается до формата бумаги, обрезной
                          лист с вылетами и метками центрируется на нём.
                          Нужно, чтобы драйвер принтера не масштабировал
                          нестандартный размер «под лист»: страница уже A4/A3,
                          печать «actual size» сохраняет натуральную величину.
                          Ориентация носителя выбирается автоматически.
      --bleed-fill <auto|stretch|flat|none>  чем заполнять вылет [${DEFAULTS.bleedFill}]
                          stretch: краевой ряд пикселей фолио растянут наружу —
                                   тон, фактура и постарение края продолжаются
                                   за линию реза, стыка не видно.
                          flat:    сплошная #ccb98c (поведение до этого патча;
                                   на постаренном крае даёт видимый кант).
                          none:    белое поле.
                          auto:    stretch там, где фолио упирается в линию
                                   реза, иначе none.
      --fold-marks / --no-fold-marks
                          метки фальцовки по центру листа (quires, booklet):
                          короткий штрих в вылете сверху и снизу — линия сгиба
                          бифолия, вдвое короче меток реза, чтобы не путать.
                          По умолчанию включены вместе с --crop-marks.""")

open(P, 'w', encoding='utf-8').write(src)
print('patch4 ok')
