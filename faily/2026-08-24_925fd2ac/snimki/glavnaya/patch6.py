P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt}, нашёл {n}: {old[:90]!r}'
    src = src.replace(old, new, cnt)

# ── DEFAULTS ──────────────────────────────────────────────────────────────
rep("""  folioEdge: 'auto',
  pages: null,            // null = все""",
"""  folioEdge: 'auto',
  // PATCH SPINE: ширина корешка в миллиметрах — вставка ПОСЕРЕДИНЕ
  // обложечного листа при --quires-cover-mode=wrapper.
  // Обёрточный бифолий огибает весь книжный блок, и на огибание уходит
  // бумага: если сложить его ровно пополам, обе крышки окажутся уже
  // внутренних страниц на половину толщины блока каждая. Поэтому лист
  // расширяется на quiresSpine, а половины разъезжаются от центра —
  // каждая остаётся в натуральную величину, между ними встаёт полоса
  // корешка. Внутренних тетрадей это не касается: они складываются
  // вокруг пустоты (внутренний бифолий) или вокруг вложенных листов
  // (это уже не корешок, а выползание, см. --quires-creep).
  // Полоса заполняется растяжением внутренних краёв обеих крышек, так
  // что корешок выглядит продолжением пергамента, а не белой вставкой.
  // Метки фальцовки при spine > 0 рисуются ДВЕ — по краям полосы: это
  // линии биговки, по ним лист сгибается, а не режется.
  // Толщина блока = число сложенных листов × 2 × толщину бумаги; для
  // восьми внутренних бифолиев это 16 толщин (80 г/м² ≈ 1.6 мм,
  // 160 г/м² ≈ 3.2 мм). Надёжнее сложить блок и померить штангенциркулем.
  quiresSpine: 0,
  pages: null,            // null = все""")

# ── парсер ────────────────────────────────────────────────────────────────
rep("""      case 'folio-edge':                cfg.folioEdge = String(val).toLowerCase(); break;""",
"""      case 'folio-edge':                cfg.folioEdge = String(val).toLowerCase(); break;
      case 'quires-spine':              cfg.quiresSpine = parseFloat(val); break;""")

# ── валидация ─────────────────────────────────────────────────────────────
rep("""  if (!['auto', 'square', 'as-is'].includes(cfg.folioEdge)) {
    throw new Error(`--folio-edge должен быть auto, square или as-is, не "${cfg.folioEdge}"`);
  }""",
"""  if (!['auto', 'square', 'as-is'].includes(cfg.folioEdge)) {
    throw new Error(`--folio-edge должен быть auto, square или as-is, не "${cfg.folioEdge}"`);
  }
  if (!(cfg.quiresSpine >= 0 && cfg.quiresSpine <= 50)) {
    throw new Error(`--quires-spine должен быть в [0..50] мм, не "${cfg.quiresSpine}"`);
  }
  if (cfg.quiresSpine > 0) {
    if (cfg.pageSize !== 'quires') {
      console.log(`  ⚠ --quires-spine игнорируется при page-size=${cfg.pageSize}: корешок вставляется только в обложечный лист quires-раскладки`);
    } else if (cfg.quiresCoverMode !== 'wrapper') {
      console.log(`  ⚠ --quires-spine игнорируется при --quires-cover-mode=separate: в этом стиле обложки — отдельные листы, они ничего не огибают и корешок им не нужен`);
    } else if (cfg.quiresSheet !== 'native') {
      console.log(`  ⚠ --quires-spine игнорируется при --quires-sheet=${cfg.quiresSheet}: там фолио вписаны в лист бумаги, а ширина половин задана полями`);
    }
  }""")

# ── геометрия: отдельный расчёт для обложечного листа ─────────────────────
rep("""      leftSlot  = { x: mO,         y: mV, w: cellW, h: cellH };
      rightSlot = { x: halfW + mG, y: mV, w: cellW, h: cellH };
    }
""",
"""      leftSlot  = { x: mO,         y: mV, w: cellW, h: cellH };
      rightSlot = { x: halfW + mG, y: mV, w: cellW, h: cellH };
    }

    // PATCH SPINE: геометрия обложечного листа. При spine > 0 в wrapper-режиме
    // на native-листе лист шире внутренних ровно на корешок, а половины
    // раздвинуты от центра: каждая крышка остаётся в натуральную величину.
    const spinePt = (cfg.pageSize === 'quires' && cfg.quiresCoverMode === 'wrapper' &&
                     sheetIsNativeQuires) ? cfg.quiresSpine * PT_PER_MM : 0;
    const coverPageW  = pageW + spinePt;
    const coverLeftSlot  = leftSlot;
    const coverRightSlot = spinePt > 0
      ? { ...rightSlot, x: rightSlot.x + spinePt }
      : rightSlot;
""")

# ── рендер ────────────────────────────────────────────────────────────────
rep("""    for (const ip of impositionPages) {
      const p = addPageWithBleed(pageW, pageH, sheetIsNativeQuires);
      const leftArea  = { x: p.offsetX + leftSlot.x,  y: p.offsetY + leftSlot.y,  w: leftSlot.w,  h: leftSlot.h };
      const rightArea = { x: p.offsetX + rightSlot.x, y: p.offsetY + rightSlot.y, w: rightSlot.w, h: rightSlot.h };""",
"""    for (const ip of impositionPages) {
      // PATCH SPINE: обложечный лист шире внутренних на корешок.
      const isCoverSheet = spinePt > 0 && ip.kind && ip.kind.startsWith('cover-wrapper');
      const sheetW = isCoverSheet ? coverPageW : pageW;
      const lSlot  = isCoverSheet ? coverLeftSlot  : leftSlot;
      const rSlot  = isCoverSheet ? coverRightSlot : rightSlot;
      const p = addPageWithBleed(sheetW, pageH, sheetIsNativeQuires);
      const leftArea  = { x: p.offsetX + lSlot.x,  y: p.offsetY + lSlot.y,  w: lSlot.w,  h: lSlot.h };
      const rightArea = { x: p.offsetX + rSlot.x, y: p.offsetY + rSlot.y, w: rSlot.w, h: rSlot.h };""")

rep("""        // Пустая половина бифолия (одиночные обложки в separate-режиме):
        // её вылет по верху и низу тянуть неоткуда — половина белая целиком.
      }""",
"""        // PATCH SPINE: полоса корешка заполняется теми же средствами, что и
        // вылет, — растяжением внутренних краёв обеих крышек навстречу друг
        // другу, по половине полосы на каждую. Пергамент продолжается через
        // корешок без стыка.
        if (isCoverSheet) {
          const half = spinePt / 2;
          if (ip.left && ip.left.f) {
            drawFolioBleed(p.pg, ip.left.f, ip.left.ref, leftArea, { right: true }, half);
          }
          if (ip.right && ip.right.f) {
            drawFolioBleed(p.pg, ip.right.f, ip.right.ref, rightArea, { left: true }, half);
          }
        }
        // Пустая половина бифолия (одиночные обложки в separate-режиме):
        // её вылет по верху и низу тянуть неоткуда — половина белая целиком.
      }""")

rep("""      paintCropMarks(p);
      paintFoldMarks(p);
    }

    const coverLabel""",
"""      paintCropMarks(p);
      paintFoldMarks(p, isCoverSheet ? spinePt : 0);
    }

    const coverLabel""")

# ── drawFolioBleed: необязательная ширина полосы ──────────────────────────
rep("""  function drawFolioBleed(pg, f, imgRef, area, edges) {
    if (!f || !imgRef || bleedPt <= 0) return;
    if (resolveBleedFill(true) !== 'stretch') return;
    const R = fitRect(f, area);
    const b = bleedPt, M = BLEED_STRETCH;""",
"""  // widthOverride — ширина полосы, если она не равна вылету (полоса корешка
  // в обложечном листе, см. PATCH SPINE).
  function drawFolioBleed(pg, f, imgRef, area, edges, widthOverride = null) {
    if (!f || !imgRef) return;
    const b = widthOverride !== null ? widthOverride : bleedPt;
    if (b <= 0) return;
    if (resolveBleedFill(true) !== 'stretch') return;
    const R = fitRect(f, area);
    const M = BLEED_STRETCH;""")

# ── paintFoldMarks: две линии биговки при корешке ─────────────────────────
rep("""  function paintFoldMarks(p) {
    if (!foldMarksEnabled) return;
    const { pg, offsetX: ox, offsetY: oy, trimW, trimH } = p;
    const offset = 2 * PT_PER_MM;
    const length = Math.max((bleedPt - offset) / 2, 1);
    const xMid = ox + trimW / 2;
    pg.drawLine({
      start: { x: xMid, y: oy + trimH + offset },
      end:   { x: xMid, y: oy + trimH + offset + length },
      thickness: 0.25, color: MARK_COLOR,
    });
    pg.drawLine({
      start: { x: xMid, y: oy - offset },
      end:   { x: xMid, y: oy - offset - length },
      thickness: 0.25, color: MARK_COLOR,
    });
  }""",
"""  // spineWidth > 0 (обложечный лист с корешком) — вместо одной линии сгиба
  // рисуются ДВЕ линии биговки по краям полосы корешка.
  function paintFoldMarks(p, spineWidth = 0) {
    if (!foldMarksEnabled) return;
    const { pg, offsetX: ox, offsetY: oy, trimW, trimH } = p;
    const offset = 2 * PT_PER_MM;
    const length = Math.max((bleedPt - offset) / 2, 1);
    const xMid = ox + trimW / 2;
    const xs = spineWidth > 0
      ? [xMid - spineWidth / 2, xMid + spineWidth / 2]
      : [xMid];
    for (const x of xs) {
      pg.drawLine({
        start: { x, y: oy + trimH + offset },
        end:   { x, y: oy + trimH + offset + length },
        thickness: 0.25, color: MARK_COLOR,
      });
      pg.drawLine({
        start: { x, y: oy - offset },
        end:   { x, y: oy - offset - length },
        thickness: 0.25, color: MARK_COLOR,
      });
    }
  }""")

# ── журнал ────────────────────────────────────────────────────────────────
rep("""      if (bleedPt > 0) {
        console.log(`               с вылетами: ${mm(pageW + 2 * bleedPt)}×${mm(pageH + 2 * bleedPt)} мм` +""",
"""      if (spinePt > 0) {
        console.log(`               обложечный лист шире на корешок: ${mm(coverPageW)}×${mm(pageH)} мм ` +
                    `(две крышки по ${mm(pageW / 2)} мм + корешок ${cfg.quiresSpine} мм)`);
      }
      if (bleedPt > 0) {
        console.log(`               с вылетами: ${mm(pageW + 2 * bleedPt)}×${mm(pageH + 2 * bleedPt)} мм` +""")

# ── help ──────────────────────────────────────────────────────────────────
rep("""      --folio-edge <auto|square|as-is>""",
"""      --quires-spine <mm>  ширина корешка в обложечном листе [${DEFAULTS.quiresSpine}]
                          Только для --quires-cover-mode=wrapper на
                          --quires-sheet=native. Обёрточный бифолий огибает
                          весь книжный блок, и на огибание уходит бумага:
                          сложенный ровно пополам, он даёт крышки уже
                          внутренних страниц на половину толщины блока каждая.
                          С этим ключом обложечный лист становится шире
                          внутренних ровно на корешок, половины раздвигаются
                          от центра, каждая крышка остаётся в натуральную
                          величину. Полоса корешка заполняется растяжением
                          внутренних краёв обеих крышек; меток фальцовки
                          становится две — по краям полосы (линии биговки).
                          Толщина блока = число сложенных листов × 2 × толщину
                          бумаги: для восьми внутренних бифолиев это 16 толщин,
                          то есть ≈1.6 мм на 80 г/м² и ≈3.2 мм на 160 г/м².
                          Надёжнее сложить блок и померить штангенциркулем.
      --folio-edge <auto|square|as-is>""")

open(P, 'w', encoding='utf-8').write(src)
print('patch6 ok')
