P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt}, нашёл {n}: {old[:90]!r}'
    src = src.replace(old, new, cnt)

# ── A. drawFolioInto: вынести подгонку прямоугольника в fitRect ────────────
rep("""  function drawFolioInto(pg, f, imgRef, area) {
    if (!f || !imgRef) return;
    const folioAspect = f.width / f.height;
    const areaAspect = area.w / area.h;
    let drawW, drawH;
    if (folioAspect > areaAspect) {
      drawW = area.w; drawH = area.w / folioAspect;
    } else {
      drawH = area.h; drawW = area.h * folioAspect;
    }
    const drawX = area.x + (area.w - drawW) / 2;
    const drawY = area.y + (area.h - drawH) / 2;
    const sx = drawW / f.width;""",
"""  // PATCH PRINT-BLEED: подгонка фолио в область с сохранением пропорций,
  // вынесена из drawFolioInto — тем же прямоугольником пользуется
  // drawFolioBleed, иначе вылет уехал бы относительно самого фолио.
  function fitRect(f, area) {
    const folioAspect = f.width / f.height;
    const areaAspect  = area.w / area.h;
    let w, h;
    if (folioAspect > areaAspect) { w = area.w; h = area.w / folioAspect; }
    else                          { h = area.h; w = area.h * folioAspect; }
    return { x: area.x + (area.w - w) / 2, y: area.y + (area.h - h) / 2, w, h };
  }

  function drawFolioInto(pg, f, imgRef, area) {
    if (!f || !imgRef) return;
    const _r = fitRect(f, area);
    const drawW = _r.w, drawH = _r.h, drawX = _r.x, drawY = _r.y;
    const sx = drawW / f.width;""")

# ── B. блок bleed / crop-marks: полная замена ──────────────────────────────
old_bleed_start = """  const bleedPt = (cfg.pageSize !== 'a4') ? cfg.bleed * PT_PER_MM : 0;
  const cropMarksEnabled = cfg.cropMarks && bleedPt >= 3 * PT_PER_MM;"""
new_bleed_start = """  const bleedPt = (cfg.pageSize !== 'a4') ? cfg.bleed * PT_PER_MM : 0;
  const cropMarksEnabled = cfg.cropMarks && bleedPt >= 3 * PT_PER_MM;
  // PATCH FOLD-MARKS: метки фальцовки осмысленны только там, где лист
  // складывается пополам (quires, booklet). По умолчанию идут вместе с
  // метками реза и требуют такого же вылета — их негде рисовать без него.
  const foldMarksEnabled =
    (cfg.foldMarks !== null ? cfg.foldMarks : cropMarksEnabled) &&
    bleedPt >= 3 * PT_PER_MM &&
    (cfg.pageSize === 'quires' || cfg.pageSize === 'booklet');

  // PATCH NATURAL-SIZE: сколько PDF-пунктов приходится на один CSS-пиксель
  // фолио. 1 = прежнее поведение (620 px → 620 pt → 218.7 мм).
  // Все фолио кодекса одного размера (жёсткие --folio-w/--folio-h в :root),
  // поэтому масштаб считается один раз по первому и применяется ко всем:
  // разъезжающиеся между собой листы в физической книге невозможны.
  const folioScale = (() => {
    if (cfg.printFolioWidth === null && cfg.printFolioHeight === null) return 1;
    if (!folios.length) return 1;
    const fW = folios[0].width, fH = folios[0].height;
    const wPt = cfg.printFolioWidth  !== null ? cfg.printFolioWidth  * PT_PER_MM : null;
    const hPt = cfg.printFolioHeight !== null ? cfg.printFolioHeight * PT_PER_MM : null;
    if (wPt !== null && hPt !== null) return Math.min(wPt / fW, hPt / fH);
    return wPt !== null ? wPt / fW : hPt / fH;
  })();"""
rep(old_bleed_start, new_bleed_start)

# paintBleed → paintBleedFlat(p) + носитель + боксы + stretch-вылет
old_tail_start = src.index("  // Заливает 4 bleed-полосы вокруг trim-rect")
old_tail_end = src.index("""  // -------------------------------------------------------------------------
  // Развёртка folio по PDF-страницам — четыре режима""")
old_tail = src[old_tail_start:old_tail_end]
assert 'function addPageWithBleed' in old_tail and 'function paintCropMarks' in old_tail

new_tail = """  // Заливает 4 полосы вылета вокруг trim-rect сплошным цветом пергамента
  // (--bleed-fill=flat). Прежнее поведение; годится, когда край фолио ровный,
  // но на постаренном крае даёт видимый стык — тогда лучше stretch.
  function paintBleedFlat(p) {
    if (bleedPt <= 0) return;
    const { pg, offsetX: ox, offsetY: oy, trimW, trimH } = p;
    pg.drawRectangle({ x: ox - bleedPt, y: oy - bleedPt, width: trimW + 2 * bleedPt, height: bleedPt, color: PARCH_COLOR });
    pg.drawRectangle({ x: ox - bleedPt, y: oy + trimH,   width: trimW + 2 * bleedPt, height: bleedPt, color: PARCH_COLOR });
    pg.drawRectangle({ x: ox - bleedPt, y: oy, width: bleedPt, height: trimH, color: PARCH_COLOR });
    pg.drawRectangle({ x: ox + trimW,   y: oy, width: bleedPt, height: trimH, color: PARCH_COLOR });
  }

  // PATCH BLEED-FILL: разрешение режима заливки. touching — упирается ли
  // изображение фолио в линию реза на этой стороне листа. Если нет
  // (a4/a3-лист, поля booklet), растягивать нечего и заливать нечем:
  // между фолио и краем листа лежит белое поле, и вылет там — тоже белый.
  function resolveBleedFill(touching) {
    if (cfg.bleedFill === 'auto') return touching ? 'stretch' : 'none';
    return cfg.bleedFill;
  }

  // ─── Клип через сырые операторы content stream ───────────────────────────
  // pdf-lib не умеет обрезать по прямоугольнику, но page.getContentStream()
  // доступен (тем же приёмом сделаны OCG-обёртки, см. drawImageWithOCG).
  // Аргументы операторов передаются строками: PDFOperator сериализует
  // строку как есть, а число попыталось бы вызвать .copyBytesInto().
  const _n = (v) => v.toFixed(4);
  function clipBegin(pg, x, y, w, h) {
    const cs = pg.getContentStream();
    cs.push(PDFOperator.of('q'));
    cs.push(PDFOperator.of('re', [_n(x), _n(y), _n(w), _n(h)]));
    cs.push(PDFOperator.of('W'));
    cs.push(PDFOperator.of('n'));
  }
  function clipEnd(pg) {
    pg.getContentStream().push(PDFOperator.of('Q'));
  }

  // Рисует изображение фолио в прямоугольник БЕЗ текстового слоя и без
  // OCG-обёрток — только пиксели/вектор. Используется для полос вылета.
  function paintFolioArtPlain(pg, imgRef, r) {
    const o = { x: r.x, y: r.y, width: r.w, height: r.h };
    if (cfg.mode === 'multilayer') {
      for (const ref of imgRef.rasterRefs) pg.drawImage(ref, o);
      if (imgRef.vectorRef) pg.drawPage(imgRef.vectorRef, o);
      return;
    }
    if (cfg.mode === 'vector') { pg.drawPage(imgRef, o); return; }
    pg.drawImage(imgRef, o);
  }

  // Во сколько раз растягивается краевой ряд. При 200 в полосу вылета
  // попадает bleed/(200·ширина фолио) ≈ полпикселя исходного растра —
  // то есть ровно «последний ряд пикселей, вытянутый наружу».
  const BLEED_STRETCH = 200;

  // PATCH BLEED-STRETCH: настоящий вылет. Для каждой стороны, где фолио
  // упирается в линию реза, изображение рисуется ещё раз — огромным и
  // обрезанным по полосе вылета так, что в неё попадает только краевой
  // ряд пикселей. Углы — растяжение по обеим осям сразу.
  // edges: { left, right, top, bottom } — какие стороны листа обрезные.
  // У бифолия в quires это три стороны на каждое фолио: сгиб в середине
  // листа не режется, и вылета там быть не должно.
  //
  // Оговорка для mode=multilayer с --ocg-layers: в полосе вылета слои
  // рисуются без OCG-обёрток, поэтому выключенный в ридере слой останется
  // видимым за линией реза. На печати это не проявляется (там уже отрезано).
  function drawFolioBleed(pg, f, imgRef, area, edges) {
    if (!f || !imgRef || bleedPt <= 0) return;
    if (resolveBleedFill(true) !== 'stretch') return;
    const R = fitRect(f, area);
    const b = bleedPt, M = BLEED_STRETCH;
    const W = R.w * M, H = R.h * M;
    const strip = (cx, cy, cw, ch, ix, iy, iw, ih) => {
      clipBegin(pg, cx, cy, cw, ch);
      paintFolioArtPlain(pg, imgRef, { x: ix, y: iy, w: iw, h: ih });
      clipEnd(pg);
    };
    // Координата, при которой правый/верхний край изображения выходит
    // ровно на внешнюю границу вылета (левый/нижний — просто R.x−b / R.y−b).
    const xRight = R.x + R.w + b - W;
    const yTop   = R.y + R.h + b - H;
    if (edges.right)  strip(R.x + R.w, R.y, b, R.h, xRight, R.y, W, R.h);
    if (edges.left)   strip(R.x - b,   R.y, b, R.h, R.x - b, R.y, W, R.h);
    if (edges.top)    strip(R.x, R.y + R.h, R.w, b, R.x, yTop,    R.w, H);
    if (edges.bottom) strip(R.x, R.y - b,   R.w, b, R.x, R.y - b, R.w, H);
    if (edges.right && edges.top)    strip(R.x + R.w, R.y + R.h, b, b, xRight,  yTop,    W, H);
    if (edges.right && edges.bottom) strip(R.x + R.w, R.y - b,   b, b, xRight,  R.y - b, W, H);
    if (edges.left  && edges.top)    strip(R.x - b,   R.y + R.h, b, b, R.x - b, yTop,    W, H);
    if (edges.left  && edges.bottom) strip(R.x - b,   R.y - b,   b, b, R.x - b, R.y - b, W, H);
  }

  // Рисует 8 меток реза в углах trim-rect. Метки начинаются на 2 мм от
  // угла (внутрь полосы вылета) и идут наружу на длину bleed − 2 мм.
  function paintCropMarks(p) {
    if (!cropMarksEnabled) return;
    const { pg, offsetX: xL, offsetY: yB, trimW, trimH } = p;
    const offset = 2 * PT_PER_MM;     // зазор от угла до начала метки
    const length = bleedPt - offset;  // длина метки
    const thickness = 0.25;           // толщина линии в pt
    const xR = xL + trimW;
    const yT = yB + trimH;

    const drawLine = (x1, y1, x2, y2) => {
      pg.drawLine({
        start: { x: x1, y: y1 },
        end:   { x: x2, y: y2 },
        thickness,
        color: MARK_COLOR,
      });
    };

    // Bottom-left corner: горизонтальная (метка уходит влево от xL) +
    // вертикальная (метка уходит вниз от yB).
    drawLine(xL - offset, yB, xL - offset - length, yB);
    drawLine(xL, yB - offset, xL, yB - offset - length);
    // Bottom-right: горизонтальная вправо + вертикальная вниз.
    drawLine(xR + offset, yB, xR + offset + length, yB);
    drawLine(xR, yB - offset, xR, yB - offset - length);
    // Top-left: горизонтальная влево + вертикальная вверх.
    drawLine(xL - offset, yT, xL - offset - length, yT);
    drawLine(xL, yT + offset, xL, yT + offset + length);
    // Top-right: горизонтальная вправо + вертикальная вверх.
    drawLine(xR + offset, yT, xR + offset + length, yT);
    drawLine(xR, yT + offset, xR, yT + offset + length);
  }

  // PATCH FOLD-MARKS: две метки фальцовки по центру листа — сверху и снизу,
  // в полосе вылета. Штрих вдвое короче метки реза, чтобы наборщик не принял
  // его за линию отреза: по этой линии лист не режут, а складывают.
  function paintFoldMarks(p) {
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
  }

  // PATCH CARRIER: размер листа-носителя под контентную страницу
  // fullW × fullH (trim + вылеты). Ориентация выбирается по пропорциям.
  let _carrierWarned = false;
  function resolveCarrier(fullW, fullH) {
    if (cfg.carrier === 'none') return { w: fullW, h: fullH, padX: 0, padY: 0 };
    const shortSide = cfg.carrier === 'a3' ? A3_W : A4_W;
    const longSide  = cfg.carrier === 'a3' ? A3_H : A4_H;
    const cw = fullW >= fullH ? longSide  : shortSide;
    const ch = fullW >= fullH ? shortSide : longSide;
    if (fullW > cw + 0.5 || fullH > ch + 0.5) {
      if (!_carrierWarned) {
        console.log(`  ⚠ --carrier=${cfg.carrier}: лист ${(fullW / PT_PER_MM).toFixed(1)}×${(fullH / PT_PER_MM).toFixed(1)} мм ` +
          `не помещается на носитель ${(cw / PT_PER_MM).toFixed(0)}×${(ch / PT_PER_MM).toFixed(0)} мм — носитель отключён`);
        _carrierWarned = true;
      }
      return { w: fullW, h: fullH, padX: 0, padY: 0 };
    }
    return { w: cw, h: ch, padX: (cw - fullW) / 2, padY: (ch - fullH) / 2 };
  }

  // Хелпер «всё-в-одном»: добавляет PDF-страницу под обрезной формат
  // trimW × trimH, с полосами вылета по периметру и (при --carrier)
  // добитую до формата бумаги. Возвращает страницу и offset, на который
  // надо сдвинуть ВСЕ внутренние координаты (фолио, текстовый слой и т.д.).
  // При bleed=0 и carrier=none поведение идентично pdf.addPage([trimW, trimH]).
  //
  // touching — упирается ли изображение фолио в линию реза (нужно для
  // --bleed-fill=auto; см. resolveBleedFill).
  function addPageWithBleed(trimW, trimH, touching = true) {
    const fullW = trimW + 2 * bleedPt;
    const fullH = trimH + 2 * bleedPt;
    const car = resolveCarrier(fullW, fullH);
    const pg = pdf.addPage([car.w, car.h]);
    const offsetX = car.padX + bleedPt;
    const offsetY = car.padY + bleedPt;
    const p = { pg, offsetX, offsetY, trimW, trimH };
    // PATCH TRIMBOX: препресс-воркфлоу читает обрезной формат из боксов,
    // а не из нарисованных меток. TrimBox — что останется после реза,
    // BleedBox — trim плюс вылеты, MediaBox — физический лист.
    if (bleedPt > 0 || car.padX > 0 || car.padY > 0) {
      pdf.context; // (контекст документа используется ниже для литералов)
      pg.node.set(PDFName.of('TrimBox'), pdf.context.obj([
        offsetX, offsetY, offsetX + trimW, offsetY + trimH,
      ]));
      pg.node.set(PDFName.of('BleedBox'), pdf.context.obj([
        car.padX, car.padY, car.padX + fullW, car.padY + fullH,
      ]));
    }
    if (bleedPt > 0 && resolveBleedFill(touching) === 'flat') paintBleedFlat(p);
    return p;
  }

"""
src = src[:old_tail_start] + new_tail + src[old_tail_end:]

open(P, 'w', encoding='utf-8').write(src)
print('patch2 ok')
