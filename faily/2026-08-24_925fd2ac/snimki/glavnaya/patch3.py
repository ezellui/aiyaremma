P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt}, нашёл {n}: {old[:90]!r}'
    src = src.replace(old, new, cnt)

# мусорная строка из patch2
rep("      pdf.context; // (контекст документа используется ниже для литералов)\n", "")

# ── QUIRES: геометрия native с физическим масштабом ───────────────────────
rep("""    let pageW, pageH, leftSlot, rightSlot;
    if (cfg.quiresSheet === 'native') {
      pageW = 2 * fW;
      pageH = fH;
      leftSlot  = { x: 0,   y: 0, w: fW, h: fH };
      rightSlot = { x: fW,  y: 0, w: fW, h: fH };
    } else {""",
"""    let pageW, pageH, leftSlot, rightSlot;
    const sheetIsNativeQuires = cfg.quiresSheet === 'native';
    if (sheetIsNativeQuires) {
      // PATCH NATURAL-SIZE: folioScale = pt на один CSS-px (1 = как раньше).
      // Лист-бифолий = два фолио впритык, сгиб ровно по центру.
      const pW = fW * folioScale;
      const pH = fH * folioScale;
      pageW = 2 * pW;
      pageH = pH;
      leftSlot  = { x: 0,   y: 0, w: pW, h: pH };
      rightSlot = { x: pW,  y: 0, w: pW, h: pH };
    } else {""")

# ── QUIRES: цикл отрисовки ────────────────────────────────────────────────
rep("""    for (const ip of impositionPages) {
      const p = addPageWithBleed(pageW, pageH);
      if (ip.left && ip.left.f) {
        drawFolioInto(p.pg, ip.left.f, ip.left.ref,
          { x: p.offsetX + leftSlot.x, y: p.offsetY + leftSlot.y, w: leftSlot.w, h: leftSlot.h });
      }
      if (ip.right && ip.right.f) {
        drawFolioInto(p.pg, ip.right.f, ip.right.ref,
          { x: p.offsetX + rightSlot.x, y: p.offsetY + rightSlot.y, w: rightSlot.w, h: rightSlot.h });
      }
      paintCropMarks(p.pg, pageW, pageH);
    }""",
"""    for (const ip of impositionPages) {
      const p = addPageWithBleed(pageW, pageH, sheetIsNativeQuires);
      const leftArea  = { x: p.offsetX + leftSlot.x,  y: p.offsetY + leftSlot.y,  w: leftSlot.w,  h: leftSlot.h };
      const rightArea = { x: p.offsetX + rightSlot.x, y: p.offsetY + rightSlot.y, w: rightSlot.w, h: rightSlot.h };
      // PATCH BLEED-STRETCH: вылет по трём обрезным сторонам каждого фолио.
      // Четвёртая — сгиб в центре листа: там режущего края нет.
      if (sheetIsNativeQuires) {
        if (ip.left && ip.left.f) {
          drawFolioBleed(p.pg, ip.left.f, ip.left.ref, leftArea,
            { left: true, top: true, bottom: true });
        }
        if (ip.right && ip.right.f) {
          drawFolioBleed(p.pg, ip.right.f, ip.right.ref, rightArea,
            { right: true, top: true, bottom: true });
        }
        // Пустая половина бифолия (одиночные обложки в separate-режиме):
        // её вылет по верху и низу тянуть неоткуда — половина белая целиком.
      }
      if (ip.left && ip.left.f)  drawFolioInto(p.pg, ip.left.f,  ip.left.ref,  leftArea);
      if (ip.right && ip.right.f) drawFolioInto(p.pg, ip.right.f, ip.right.ref, rightArea);
      paintCropMarks(p);
      paintFoldMarks(p);
    }""")

# ── QUIRES: журнал — физические размеры ───────────────────────────────────
rep("""    const sheetDesc = cfg.quiresSheet === 'native'
      ? `${pageW.toFixed(0)}×${pageH.toFixed(0)}pt (= 2 folio side-by-side, native бифолий)`
      : `${cfg.quiresSheet.toUpperCase()} landscape ${pageW.toFixed(0)}×${pageH.toFixed(0)}pt (folio letterboxed)`;
    console.log(`  → ${impositionPages.length} PDF-страниц ${sheetDesc}`);""",
"""    const sheetDesc = cfg.quiresSheet === 'native'
      ? `${pageW.toFixed(0)}×${pageH.toFixed(0)}pt (= 2 folio side-by-side, native бифолий)`
      : `${cfg.quiresSheet.toUpperCase()} landscape ${pageW.toFixed(0)}×${pageH.toFixed(0)}pt (folio letterboxed)`;
    console.log(`  → ${impositionPages.length} PDF-страниц ${sheetDesc}`);
    // PATCH NATURAL-SIZE: физика листа в миллиметрах + эффективное
    // разрешение растра на этом размере (raster-режим).
    if (sheetIsNativeQuires) {
      const mm = (pt) => (pt / PT_PER_MM).toFixed(1);
      console.log(`  натуральная величина: фолио ${mm(pageW / 2)}×${mm(pageH)} мм, ` +
                  `лист-бифолий ${mm(pageW)}×${mm(pageH)} мм` +
                  (folioScale !== 1 ? ` (масштаб ${folioScale.toFixed(4)} pt/px)` : ` (1 px → 1 pt)`));
      if (bleedPt > 0) {
        console.log(`               с вылетами: ${mm(pageW + 2 * bleedPt)}×${mm(pageH + 2 * bleedPt)} мм` +
                    (cfg.carrier !== 'none' ? `, на носителе ${cfg.carrier.toUpperCase()}` : ''));
      }
      if (cfg.mode === 'raster') {
        const dpi = fW * cfg.scale / ((pageW / 2) / 72);
        console.log(`               растр: ${Math.round(dpi)} dpi при --scale=${cfg.scale}` +
                    (dpi < 300 ? ` ⚠ для печати желательно ≥ 300 (нужен --scale≈${(cfg.scale * 300 / dpi).toFixed(2)})` : ''));
      }
    }""")

# ── BOOKLET: фолио не доходит до края листа → touching=false ──────────────
rep("""      let p = addPageWithBleed(sheetW, sheetH);
      const sL = slot(frontL), sR = slot(frontR);
      drawFolioInto(p.pg, sL.f, sL.ref, { x: p.offsetX + mO,         y: p.offsetY + mV, w: cellW, h: cellH });
      drawFolioInto(p.pg, sR.f, sR.ref, { x: p.offsetX + halfW + mG, y: p.offsetY + mV, w: cellW, h: cellH });
      paintCropMarks(p.pg, sheetW, sheetH);

      // Back
      p = addPageWithBleed(sheetW, sheetH);
      const sBL = slot(backL), sBR = slot(backR);
      drawFolioInto(p.pg, sBL.f, sBL.ref, { x: p.offsetX + mO,         y: p.offsetY + mV, w: cellW, h: cellH });
      drawFolioInto(p.pg, sBR.f, sBR.ref, { x: p.offsetX + halfW + mG, y: p.offsetY + mV, w: cellW, h: cellH });
      paintCropMarks(p.pg, sheetW, sheetH);""",
"""      // touching=false: фолио вписано в полу-лист с полями и до линии реза
      // не доходит, поэтому вылет по умолчанию остаётся пустым полем.
      let p = addPageWithBleed(sheetW, sheetH, false);
      const sL = slot(frontL), sR = slot(frontR);
      drawFolioInto(p.pg, sL.f, sL.ref, { x: p.offsetX + mO,         y: p.offsetY + mV, w: cellW, h: cellH });
      drawFolioInto(p.pg, sR.f, sR.ref, { x: p.offsetX + halfW + mG, y: p.offsetY + mV, w: cellW, h: cellH });
      paintCropMarks(p);
      paintFoldMarks(p);

      // Back
      p = addPageWithBleed(sheetW, sheetH, false);
      const sBL = slot(backL), sBR = slot(backR);
      drawFolioInto(p.pg, sBL.f, sBL.ref, { x: p.offsetX + mO,         y: p.offsetY + mV, w: cellW, h: cellH });
      drawFolioInto(p.pg, sBR.f, sBR.ref, { x: p.offsetX + halfW + mG, y: p.offsetY + mV, w: cellW, h: cellH });
      paintCropMarks(p);
      paintFoldMarks(p);""")

# ── SPREADS: native-геометрия с масштабом + вылет ─────────────────────────
rep("""      if (sheetIsNative) {
        // Sheet ровно по folio (+ опциональные явные поля).
        pageW = f.width  + 2 * coverMargin;
        pageH = f.height + 2 * coverMargin;
        area  = { x: coverMargin, y: coverMargin, w: f.width, h: f.height };
      } else {""",
"""      if (sheetIsNative) {
        // Sheet ровно по folio (+ опциональные явные поля).
        // PATCH NATURAL-SIZE: folioScale переводит CSS-px в физические pt.
        pageW = f.width  * folioScale + 2 * coverMargin;
        pageH = f.height * folioScale + 2 * coverMargin;
        area  = { x: coverMargin, y: coverMargin, w: f.width * folioScale, h: f.height * folioScale };
      } else {""")

rep("""      const p = addPageWithBleed(pageW, pageH);
      drawFolioInto(p.pg, f, imgRef,
        { x: p.offsetX + area.x, y: p.offsetY + area.y, w: area.w, h: area.h });
      paintCropMarks(p.pg, pageW, pageH);
      nCovers++;""",
"""      const touching = sheetIsNative && coverMargin === 0;
      const p = addPageWithBleed(pageW, pageH, touching);
      const rect = { x: p.offsetX + area.x, y: p.offsetY + area.y, w: area.w, h: area.h };
      if (touching) {
        drawFolioBleed(p.pg, f, imgRef, rect, { left: true, right: true, top: true, bottom: true });
      }
      drawFolioInto(p.pg, f, imgRef, rect);
      paintCropMarks(p);
      nCovers++;""")

rep("""      if (sheetIsNative) {
        const lW = fL.width;
        const lH = fL.height;
        // Если правый слот пуст, удваиваем ширину относительно left folio —
        // спред-страница остаётся spread-sized, но правая половина пустая.
        const rW = fR ? fR.width  : lW;
        const rH = fR ? fR.height : lH;""",
"""      if (sheetIsNative) {
        // PATCH NATURAL-SIZE: folioScale переводит CSS-px в физические pt.
        const lW = fL.width  * folioScale;
        const lH = fL.height * folioScale;
        // Если правый слот пуст, удваиваем ширину относительно left folio —
        // спред-страница остаётся spread-sized, но правая половина пустая.
        const rW = fR ? fR.width  * folioScale : lW;
        const rH = fR ? fR.height * folioScale : lH;""")

rep("""      const p = addPageWithBleed(pageW, pageH);
      drawFolioInto(p.pg, fL, refL,
        { x: p.offsetX + leftRect.x, y: p.offsetY + leftRect.y, w: leftRect.w, h: leftRect.h });
      if (fR) {
        drawFolioInto(p.pg, fR, refR,
          { x: p.offsetX + rightRect.x, y: p.offsetY + rightRect.y, w: rightRect.w, h: rightRect.h });
      } else {
        trailingBlank = true;
      }
      paintCropMarks(p.pg, pageW, pageH);
      nSpreads++;""",
"""      const touching = sheetIsNative && sMO === 0 && sMV === 0;
      const p = addPageWithBleed(pageW, pageH, touching);
      const lRect = { x: p.offsetX + leftRect.x,  y: p.offsetY + leftRect.y,  w: leftRect.w,  h: leftRect.h };
      const rRect = { x: p.offsetX + rightRect.x, y: p.offsetY + rightRect.y, w: rightRect.w, h: rightRect.h };
      if (touching) {
        drawFolioBleed(p.pg, fL, refL, lRect, { left: true, top: true, bottom: true });
        if (fR) drawFolioBleed(p.pg, fR, refR, rRect, { right: true, top: true, bottom: true });
      }
      drawFolioInto(p.pg, fL, refL, lRect);
      if (fR) {
        drawFolioInto(p.pg, fR, refR, rRect);
      } else {
        trailingBlank = true;
      }
      paintCropMarks(p);
      nSpreads++;""")

# ── NATIVE / A4: одиночная folio на страницу ──────────────────────────────
rep("""      } else {
        pageW = f.width; pageH = f.height;
        area = { x: 0, y: 0, w: f.width, h: f.height };
      }""",
"""      } else {
        // PATCH NATURAL-SIZE: folioScale переводит CSS-px в физические pt.
        pageW = f.width * folioScale; pageH = f.height * folioScale;
        area = { x: 0, y: 0, w: pageW, h: pageH };
      }""")

rep("""      const p = addPageWithBleed(pageW, pageH);
      drawFolioInto(p.pg, f, imgRefs[i],
        { x: p.offsetX + area.x, y: p.offsetY + area.y, w: area.w, h: area.h });
      paintCropMarks(p.pg, pageW, pageH);
    }""",
"""      const touching = cfg.pageSize !== 'a4';
      const p = addPageWithBleed(pageW, pageH, touching);
      const rect = { x: p.offsetX + area.x, y: p.offsetY + area.y, w: area.w, h: area.h };
      if (touching) {
        drawFolioBleed(p.pg, f, imgRefs[i], rect, { left: true, right: true, top: true, bottom: true });
      }
      drawFolioInto(p.pg, f, imgRefs[i], rect);
      paintCropMarks(p);
    }""")

open(P, 'w', encoding='utf-8').write(src)
print('patch3 ok')
