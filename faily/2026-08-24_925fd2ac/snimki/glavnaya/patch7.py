P = 'codex-to-pdf.mjs'
src = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    n = src.count(old)
    assert n == cnt, f'ожидал {cnt}, нашёл {n}: {old[:90]!r}'
    src = src.replace(old, new, cnt)

# ── DEFAULTS ──────────────────────────────────────────────────────────────
rep("""  quiresSpine: 0,
  pages: null,            // null = все""",
"""  quiresSpine: 0,
  // PATCH QUIRES-ONLY: какую часть quires-раскладки выводить.
  //   all (default) — весь кодекс;
  //   cover         — только обложечный лист (в wrapper-режиме это один
  //                   бифолий, две стороны; в separate — четыре страницы
  //                   передней и задней обложки);
  //   inner         — только тетради, без обложек.
  // Важно: это НЕ --pages. Ключ --pages отфильтровывает массив folios, а
  // imposition индексирует его по номеру листа — при quires это молча
  // ломает раскладку. Здесь же фильтруются готовые imposition-страницы,
  // а съёмка ограничивается теми фолио, которые на них попали: работа с
  // обложкой перестаёт стоить полного прогона кодекса.
  quiresOnly: 'all',
  pages: null,            // null = все""")

# ── парсер ────────────────────────────────────────────────────────────────
rep("""      case 'quires-spine':              cfg.quiresSpine = parseFloat(val); break;""",
"""      case 'quires-spine':              cfg.quiresSpine = parseFloat(val); break;
      case 'quires-only':               cfg.quiresOnly = String(val).toLowerCase(); break;""")

# ── валидация ─────────────────────────────────────────────────────────────
rep("""  if (!(cfg.quiresSpine >= 0 && cfg.quiresSpine <= 50)) {""",
"""  if (!['all', 'cover', 'inner'].includes(cfg.quiresOnly)) {
    throw new Error(`--quires-only должен быть all, cover или inner, не "${cfg.quiresOnly}"`);
  }
  if (cfg.quiresOnly !== 'all' && cfg.pageSize !== 'quires') {
    console.log(`  ⚠ --quires-only игнорируется при page-size=${cfg.pageSize}`);
  }
  if (cfg.quiresOnly !== 'all' && cfg.pages) {
    throw new Error('--quires-only и --pages несовместимы: --pages ломает индексацию листов в quires-раскладке');
  }
  if (!(cfg.quiresSpine >= 0 && cfg.quiresSpine <= 50)) {""")

# ── ограничение съёмки ────────────────────────────────────────────────────
# Набор нужных фолио вычисляется из структуры тетрадей ДО цикла съёмки.
rep("""  const images = [];
  let totalBytes = 0;
  const imgExt = cfg.format === 'jpeg' ? 'jpg' : 'png';""",
"""  // PATCH QUIRES-ONLY: какие фолио вообще нужно снимать. Обложечный лист
  // в wrapper-режиме держит первый и последний лист кодекса, то есть четыре
  // фолио: recto/verso листа 1 и листа N. В separate-режиме — те же четыре,
  // просто разложенные по четырём страницам. Остальное при --quires-only=cover
  // не снимается вовсе, и прогон из получаса превращается в минуту.
  const neededFolioIdx = (() => {
    if (cfg.pageSize !== 'quires' || cfg.quiresOnly === 'all') return null;
    const total = folios.length;
    const coverIdx = new Set([0, 1, total - 2, total - 1].filter(i => i >= 0 && i < total));
    if (cfg.quiresOnly === 'cover') return coverIdx;
    const inner = new Set();
    for (let i = 0; i < total; i++) if (!coverIdx.has(i)) inner.add(i);
    return inner;
  })();
  if (neededFolioIdx) {
    console.log(`  [quires-only=${cfg.quiresOnly}] снимаю ${neededFolioIdx.size} из ${folios.length} folio`);
  }

  const images = [];
  let totalBytes = 0;
  const imgExt = cfg.format === 'jpeg' ? 'jpg' : 'png';""")

rep("""  for (let i = 0; i < folios.length; i++) {
    const f = folios[i];
    const t0 = Date.now();

    let buf;""",
"""  for (let i = 0; i < folios.length; i++) {
    const f = folios[i];
    // PATCH QUIRES-ONLY: пропущенные фолио занимают своё место в массиве
    // как null — нумерация листов не должна поехать.
    if (neededFolioIdx && !neededFolioIdx.has(i)) { images.push(null); continue; }
    const t0 = Date.now();

    let buf;""")

# ── embed: пропускаем null ────────────────────────────────────────────────
rep("""    for (let i = 0; i < folios.length; i++) {
      const ml = images[i];
      const rasterRefs = [];""",
"""    for (let i = 0; i < folios.length; i++) {
      const ml = images[i];
      if (!ml) { imgRefs.push(null); continue; }
      const rasterRefs = [];""")

rep("""    for (let i = 0; i < folios.length; i++) {
      const [embedded] = await pdf.embedPdf(images[i], [0]);
      imgRefs.push(embedded);
    }""",
"""    for (let i = 0; i < folios.length; i++) {
      if (!images[i]) { imgRefs.push(null); continue; }
      const [embedded] = await pdf.embedPdf(images[i], [0]);
      imgRefs.push(embedded);
    }""")

rep("""    for (let i = 0; i < folios.length; i++) {
      imgRefs.push(cfg.format === 'png'
        ? await pdf.embedPng(images[i])
        : await pdf.embedJpg(images[i]));
    }""",
"""    for (let i = 0; i < folios.length; i++) {
      if (!images[i]) { imgRefs.push(null); continue; }
      imgRefs.push(cfg.format === 'png'
        ? await pdf.embedPng(images[i])
        : await pdf.embedJpg(images[i]));
    }""")

# ── фильтрация imposition-страниц ─────────────────────────────────────────
rep("""    for (const ip of impositionPages) {
      // PATCH SPINE: обложечный лист шире внутренних на корешок.""",
"""    // PATCH QUIRES-ONLY: оставляем только нужные imposition-страницы.
    const wantPages = cfg.quiresOnly === 'all' ? impositionPages
      : impositionPages.filter(ip => {
          const isCover = !!(ip.kind && ip.kind.startsWith('cover'));
          return cfg.quiresOnly === 'cover' ? isCover : !isCover;
        });
    if (cfg.quiresOnly !== 'all') {
      console.log(`  [quires-only=${cfg.quiresOnly}] ${wantPages.length} из ${impositionPages.length} PDF-страниц`);
    }

    for (const ip of wantPages) {
      // PATCH SPINE: обложечный лист шире внутренних на корешок.""")

# ── help ──────────────────────────────────────────────────────────────────
rep("""      --quires-spine <mm>""",
"""      --quires-only <all|cover|inner>  что выводить [${DEFAULTS.quiresOnly}]
                          cover  — только обложечный лист (в wrapper-режиме
                                   один бифолий, две стороны);
                          inner  — только тетради;
                          Съёмка ограничивается нужными фолио, поэтому
                          работа с обложкой перестаёт стоить полного прогона.
                          Это НЕ --pages: тот фильтрует массив folios и молча
                          ломает индексацию листов в quires-раскладке
                          (совместное использование запрещено).
      --quires-spine <mm>""")

open(P, 'w', encoding='utf-8').write(src)
print('patch7 ok')
