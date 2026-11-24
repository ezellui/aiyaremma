/* ═══════════════════════════════════════════════════════════════════
   PLAYGROUND LIVE-UPDATE (v2 — три независимых фильтра)

   Структура:
   - CONTROLS:  метаданные master-слайдеров (15 параметров)
   - INSTANCES: ['front', 'back', 'initial'] — три инстанса фильтра
   - SEEDS:     9 number-input'ов (3 инстанса × 3 типа шума)
   - OVERRIDES: для каждого инстанса — 15 чекбоксов + 15 слайдеров,
                включающих per-instance дельту по любому параметру

   Resolve-семантика:
     value(instance, paramId) =
       override[instance][paramId] if override checkbox checked
       else master[paramId]

   updateFilter() обновляет все 3 фильтра в одном цикле.
   ═══════════════════════════════════════════════════════════════════ */

const CONTROLS = [
  // [id, label, group, min, max, step, defaultValue, decimals]
  ["disp-scale",    "Displacement scale (амплитуда)",       "1. Гуляние линий",         0.0,  3.0,   0.05,  0.85,  2],
  ["disp-freq",     "Disp baseFrequency (частота)",         "1. Гуляние линий",         0.02, 2.0,   0.005, 0.230, 3],
  ["disp-octaves",  "Disp numOctaves",                      "1. Гуляние линий",         1,    5,     1,     3,     0],
  ["coarse-freq",   "Coarse baseFrequency (размер пятен)",  "2. Крупные пятна",         0.005,0.3,   0.005, 0.030, 3],
  ["coarse-alpha",  "Coarse alpha (затемнение)",            "2. Крупные пятна",         0.0,  1.0,   0.02,  0.500, 3],
  ["coarse-offset", "Coarse alpha offset (контрастность)",  "2. Крупные пятна",         -0.3, 0.3,   0.01,  -0.070, 3],
  ["coarse-r",      "Coarse tint R",                        "2. Крупные пятна",         0.0,  0.3,   0.005, 0.080, 3],
  ["coarse-g",      "Coarse tint G",                        "2. Крупные пятна",         0.0,  0.3,   0.005, 0.040, 3],
  ["coarse-b",      "Coarse tint B",                        "2. Крупные пятна",         0.0,  0.3,   0.005, 0.000, 3],
  ["fine-freq",     "Fine baseFrequency (размер зерна)",    "3. Мелкая зернистость",    0.3,  3.0,   0.05,  2.000, 3],
  ["fine-alpha",    "Fine alpha (сила зернистости)",        "3. Мелкая зернистость",    0.0,  1.0,   0.02,  0.460, 3],
  ["fine-r",        "Fine tint R",                          "3. Мелкая зернистость",    0.0,  0.3,   0.005, 0.060, 3],
  ["fine-g",        "Fine tint G",                          "3. Мелкая зернистость",    0.0,  0.3,   0.005, 0.030, 3],
  ["fine-b",        "Fine tint B",                          "3. Мелкая зернистость",    0.0,  0.3,   0.005, 0.000, 3],
];

const INSTANCES = ['front', 'back', 'initial'];
const INSTANCE_LABELS = { front: 'Front carpet', back: 'Back carpet', initial: 'Initial' };

const SEED_DEFAULTS = {
  front:   { disp: 52,  coarse: 42, fine: 11 },
  back:    { disp: 71,  coarse: 89, fine: 23 },
  initial: { disp: 113, coarse: 67, fine: 37 },
};

const PRESETS = {
  off: null,  // спецзначение: отключить filter совсем
  current: {  // production-точка (значения из финального dump'а в кодексе)
    "disp-scale": 0.85, "disp-freq": 0.230, "disp-octaves": 3,
    "coarse-freq": 0.030, "coarse-alpha": 0.500, "coarse-offset": -0.070,
    "coarse-r": 0.080, "coarse-g": 0.040, "coarse-b": 0.000,
    "fine-freq": 2.000, "fine-alpha": 0.460,
    "fine-r": 0.060, "fine-g": 0.030, "fine-b": 0.000,
  },
  v4: {
    "disp-scale": 1.0, "disp-freq": 0.5, "disp-octaves": 2,
    "coarse-freq": 0.06, "coarse-alpha": 0.55, "coarse-offset": -0.05,
    "coarse-r": 0.08, "coarse-g": 0.04, "coarse-b": 0.00,
    "fine-freq": 1.4, "fine-alpha": 0.40,
    "fine-r": 0.06, "fine-g": 0.03, "fine-b": 0.00,
  },
  v5: {
    "disp-scale": 0.6, "disp-freq": 0.5, "disp-octaves": 2,
    "coarse-freq": 0.06, "coarse-alpha": 0.38, "coarse-offset": -0.03,
    "coarse-r": 0.08, "coarse-g": 0.04, "coarse-b": 0.00,
    "fine-freq": 1.4, "fine-alpha": 0.28,
    "fine-r": 0.06, "fine-g": 0.03, "fine-b": 0.00,
  },
  strong: {
    "disp-scale": 1.4, "disp-freq": 0.6, "disp-octaves": 2,
    "coarse-freq": 0.04, "coarse-alpha": 0.75, "coarse-offset": -0.10,
    "coarse-r": 0.09, "coarse-g": 0.045, "coarse-b": 0.00,
    "fine-freq": 1.6, "fine-alpha": 0.55,
    "fine-r": 0.06, "fine-g": 0.03, "fine-b": 0.00,
  },
  hand: {
    "disp-scale": 1.8, "disp-freq": 0.30, "disp-octaves": 2,
    "coarse-freq": 0.10, "coarse-alpha": 0.35, "coarse-offset": 0,
    "coarse-r": 0.07, "coarse-g": 0.04, "coarse-b": 0.00,
    "fine-freq": 1.4, "fine-alpha": 0.25,
    "fine-r": 0.06, "fine-g": 0.03, "fine-b": 0.00,
  },
  aged: {
    "disp-scale": 0.9, "disp-freq": 0.5, "disp-octaves": 2,
    "coarse-freq": 0.025, "coarse-alpha": 0.65, "coarse-offset": -0.15,
    "coarse-r": 0.10, "coarse-g": 0.05, "coarse-b": 0.00,
    "fine-freq": 1.2, "fine-alpha": 0.35,
    "fine-r": 0.06, "fine-g": 0.03, "fine-b": 0.00,
  },
};

/* ─── 1. Рендер master-слайдеров (как раньше) ───────────────────────── */
const list = document.getElementById('pg-control-list');
const groups = {};
CONTROLS.forEach(([id, label, group, min, max, step, def, fmt]) => {
  if (!groups[group]) {
    const h = document.createElement('h3');
    h.textContent = group;
    list.appendChild(h);
    groups[group] = true;
  }
  const row = document.createElement('div');
  row.className = 'pg-control';
  row.innerHTML = `
    <div class="pg-control-label">
      <span>${label}</span>
      <span class="pg-value" id="val-${id}"></span>
    </div>
    <input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${def}"/>
  `;
  list.appendChild(row);
});

/* ─── 2. Рендер UI для overrides ────────────────────────────────────── */
const overridesContainer = document.getElementById('pg-overrides-container');
INSTANCES.forEach(instance => {
  const block = document.createElement('div');
  block.className = 'pg-override-block';
  block.dataset.instance = instance;

  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'pg-override-toggle';
  toggle.innerHTML = `
    <span><span class="pg-override-arrow">▸</span> ${INSTANCE_LABELS[instance]} overrides</span>
    <span class="pg-override-active-count" id="ovr-count-${instance}"></span>
  `;
  toggle.addEventListener('click', () => {
    block.classList.toggle('pg-override-open');
  });

  const body = document.createElement('div');
  body.className = 'pg-override-body';

  CONTROLS.forEach(([id, label, group, min, max, step, def, decimals]) => {
    const row = document.createElement('div');
    row.className = 'pg-override-row';
    row.dataset.paramId = id;
    row.innerHTML = `
      <input type="checkbox" class="pg-override-check" id="ovr-chk-${instance}-${id}"/>
      <label class="pg-override-label" for="ovr-chk-${instance}-${id}" title="${label}">${id}</label>
      <input type="range" id="ovr-${instance}-${id}" min="${min}" max="${max}" step="${step}" value="${def}" disabled/>
      <div class="pg-override-value" id="ovr-val-${instance}-${id}">—</div>
    `;
    body.appendChild(row);
  });

  block.appendChild(toggle);
  block.appendChild(body);
  overridesContainer.appendChild(block);
});

/* ─── 3. Resolve-семантика ──────────────────────────────────────────── */
function read(id) {
  return parseFloat(document.getElementById(id).value);
}

function resolve(instance, paramId) {
  const chk = document.getElementById(`ovr-chk-${instance}-${paramId}`);
  if (chk && chk.checked) {
    return parseFloat(document.getElementById(`ovr-${instance}-${paramId}`).value);
  }
  return read(paramId);
}

function readSeed(instance, seedType) {
  return parseInt(document.getElementById(`seed-${instance}-${seedType}`).value, 10) || 0;
}

function fmt(id, v) {
  const meta = CONTROLS.find(c => c[0] === id);
  const decimals = meta[7];
  return Number(v).toFixed(decimals);
}

function buildColorMatrix(r, g, b, alpha, offset = 0) {
  return `0 0 0 0 ${r.toFixed(3)}
` +
         `        0 0 0 0 ${g.toFixed(3)}
` +
         `        0 0 0 0 ${b.toFixed(3)}
` +
         `        0 0 0 ${alpha.toFixed(3)} ${offset.toFixed(3)}`;
}

/* ─── 4. Обновление трёх фильтров ───────────────────────────────────── */
function applyToFilter(instance) {
  const filterEl = document.getElementById(`illumination-aged-${instance}`);

  // color-interpolation-filters (Firefox-diag)
  const cif = document.querySelector('input[name="pg-cif"]:checked');
  const cifVal = cif ? cif.value : 'auto';
  filterEl.setAttribute('color-interpolation-filters', cifVal);

  // Тип турбулентности для disp (Firefox-diag)
  const dispType = document.querySelector('input[name="pg-disp-type"]:checked');
  const typeVal = dispType ? dispType.value : 'turbulence';

  // Блок 1: displacement
  const dispTurb = document.getElementById(`disp-turb-${instance}`);
  dispTurb.setAttribute('type', typeVal);
  dispTurb.setAttribute('baseFrequency', resolve(instance, 'disp-freq').toFixed(3));
  dispTurb.setAttribute('numOctaves', resolve(instance, 'disp-octaves'));
  dispTurb.setAttribute('seed', readSeed(instance, 'disp'));

  const dispMap = document.getElementById(`disp-map-${instance}`);
  dispMap.setAttribute('scale', resolve(instance, 'disp-scale').toFixed(2));

  // Блок 2: coarse
  const coarseTurb = document.getElementById(`coarse-turb-${instance}`);
  coarseTurb.setAttribute('baseFrequency', resolve(instance, 'coarse-freq').toFixed(3));
  coarseTurb.setAttribute('seed', readSeed(instance, 'coarse'));

  const coarseMat = document.getElementById(`coarse-mat-${instance}`);
  coarseMat.setAttribute('values', buildColorMatrix(
    resolve(instance, 'coarse-r'),
    resolve(instance, 'coarse-g'),
    resolve(instance, 'coarse-b'),
    resolve(instance, 'coarse-alpha'),
    resolve(instance, 'coarse-offset'),
  ));

  // Блок 3: fine
  const fineTurb = document.getElementById(`fine-turb-${instance}`);
  fineTurb.setAttribute('baseFrequency', resolve(instance, 'fine-freq').toFixed(3));
  fineTurb.setAttribute('seed', readSeed(instance, 'fine'));

  const fineMat = document.getElementById(`fine-mat-${instance}`);
  fineMat.setAttribute('values', buildColorMatrix(
    resolve(instance, 'fine-r'),
    resolve(instance, 'fine-g'),
    resolve(instance, 'fine-b'),
    resolve(instance, 'fine-alpha'),
    0,
  ));

  // Firefox fix: принудительная инвалидация
  const parent = filterEl.parentNode;
  parent.removeChild(filterEl);
  parent.appendChild(filterEl);
}

function refreshOverrideValueDisplays() {
  INSTANCES.forEach(instance => {
    let activeCount = 0;
    CONTROLS.forEach(([id]) => {
      const chk = document.getElementById(`ovr-chk-${instance}-${id}`);
      const slider = document.getElementById(`ovr-${instance}-${id}`);
      const valDisplay = document.getElementById(`ovr-val-${instance}-${id}`);
      const row = slider.closest('.pg-override-row');

      if (chk.checked) {
        activeCount += 1;
        slider.disabled = false;
        row.classList.add('pg-override-active');
        valDisplay.textContent = fmt(id, parseFloat(slider.value));
      } else {
        slider.disabled = true;
        row.classList.remove('pg-override-active');
        valDisplay.innerHTML = `<span class="pg-override-inherit-hint">inherit (${fmt(id, read(id))})</span>`;
      }
    });
    const counter = document.getElementById(`ovr-count-${instance}`);
    counter.textContent = activeCount > 0 ? `${activeCount} active` : '';
  });
}

function updateFilter() {
  // Снимаем pg-filter-off при любом изменении (пользователь хочет видеть результат)
  document.body.classList.remove('pg-filter-off');

  // Обновляем все 3 фильтра
  INSTANCES.forEach(applyToFilter);

  // Master-value labels
  CONTROLS.forEach(([id]) => {
    document.getElementById('val-' + id).textContent = fmt(id, read(id));
  });

  // Override-value labels (и активные счётчики)
  refreshOverrideValueDisplays();

  dumpFilter();
}

/* ─── 5. Dump (три блока) ───────────────────────────────────────────── */
function buildFilterXml(instance) {
  const dispType = document.querySelector('input[name="pg-disp-type"]:checked');
  const typeVal = dispType ? dispType.value : 'turbulence';
  const cif = document.querySelector('input[name="pg-cif"]:checked');
  const cifVal = cif ? cif.value : 'auto';

  const dispFreq    = resolve(instance, 'disp-freq').toFixed(3);
  const dispOct     = resolve(instance, 'disp-octaves');
  const dispScale   = resolve(instance, 'disp-scale').toFixed(2);
  const coarseFreq  = resolve(instance, 'coarse-freq').toFixed(3);
  const fineFreq    = resolve(instance, 'fine-freq').toFixed(3);
  const dispSeed    = readSeed(instance, 'disp');
  const coarseSeed  = readSeed(instance, 'coarse');
  const fineSeed    = readSeed(instance, 'fine');

  const coarseMat = buildColorMatrix(
    resolve(instance, 'coarse-r'), resolve(instance, 'coarse-g'), resolve(instance, 'coarse-b'),
    resolve(instance, 'coarse-alpha'), resolve(instance, 'coarse-offset'),
  );
  const fineMat = buildColorMatrix(
    resolve(instance, 'fine-r'), resolve(instance, 'fine-g'), resolve(instance, 'fine-b'),
    resolve(instance, 'fine-alpha'), 0,
  );

  return `<filter id="illumination-aged-${instance}" x="-3%" y="-3%" width="106%" height="106%"
        color-interpolation-filters="${cifVal}">
  <feTurbulence type="${typeVal}" baseFrequency="${dispFreq}"
                numOctaves="${dispOct}" seed="${dispSeed}" result="dispNoise"/>
  <feDisplacementMap in="SourceGraphic" in2="dispNoise"
                     xChannelSelector="R" yChannelSelector="G"
                     scale="${dispScale}" result="displaced"/>

  <feTurbulence type="fractalNoise" baseFrequency="${coarseFreq}"
                numOctaves="3" seed="${coarseSeed}" stitchTiles="stitch" result="coarseNoise"/>
  <feColorMatrix in="coarseNoise" type="matrix"
    values="${coarseMat}" result="coarseTinted"/>
  <feComposite in="coarseTinted" in2="displaced" operator="in" result="coarseOnInk"/>

  <feTurbulence type="fractalNoise" baseFrequency="${fineFreq}"
                numOctaves="2" seed="${fineSeed}" stitchTiles="stitch" result="fineNoise"/>
  <feColorMatrix in="fineNoise" type="matrix"
    values="${fineMat}" result="fineTinted"/>
  <feComposite in="fineTinted" in2="displaced" operator="in" result="fineOnInk"/>

  <feMerge>
    <feMergeNode in="displaced"/>
    <feMergeNode in="coarseOnInk"/>
    <feMergeNode in="fineOnInk"/>
  </feMerge>
</filter>`;
}

function dumpFilter() {
  const blocks = INSTANCES.map(inst => {
    const label = inst === 'front'   ? 'FRONT carpet'
               : inst === 'back'    ? 'BACK carpet'
                                    : 'INITIAL';
    return `<!-- ${label} -->\n${buildFilterXml(inst)}`;
  });
  document.getElementById('pg-dump-out').textContent = blocks.join('\n\n');
}

/* ─── 6. Пресеты ────────────────────────────────────────────────────── */
function clearAllOverrides() {
  INSTANCES.forEach(instance => {
    CONTROLS.forEach(([id]) => {
      const chk = document.getElementById(`ovr-chk-${instance}-${id}`);
      if (chk.checked) chk.checked = false;
      // Также сбрасываем slider'ы overrides в значение master'а
      const slider = document.getElementById(`ovr-${instance}-${id}`);
      const masterVal = document.getElementById(id).value;
      slider.value = masterVal;
    });
  });
}

function applyPreset(name) {
  if (name === 'off') {
    document.body.classList.add('pg-filter-off');
    return;
  }
  document.body.classList.remove('pg-filter-off');
  const p = PRESETS[name];
  if (!p) return;

  // Применяем мастер-параметры
  Object.entries(p).forEach(([id, v]) => {
    const el = document.getElementById(id);
    if (el) el.value = v;
  });

  // Очищаем все overrides (по утверждённому решению)
  clearAllOverrides();

  updateFilter();
}

/* ─── 7. Reseed all (random) ────────────────────────────────────────── */
function randomSeed() {
  return Math.floor(Math.random() * 201);  // 0..200 inclusive
}

function reseedAll() {
  INSTANCES.forEach(instance => {
    ['disp', 'coarse', 'fine'].forEach(seedType => {
      const el = document.getElementById(`seed-${instance}-${seedType}`);
      el.value = randomSeed();
    });
  });
  updateFilter();
}

/* ─── 8. Привязка событий ───────────────────────────────────────────── */

// Мастер-слайдеры
CONTROLS.forEach(([id]) => {
  document.getElementById(id).addEventListener('input', updateFilter);
});

// Override checkboxes и slider'ы
INSTANCES.forEach(instance => {
  CONTROLS.forEach(([id]) => {
    document.getElementById(`ovr-chk-${instance}-${id}`).addEventListener('change', updateFilter);
    document.getElementById(`ovr-${instance}-${id}`).addEventListener('input', updateFilter);
  });
});

// Seeds inputs
INSTANCES.forEach(instance => {
  ['disp', 'coarse', 'fine'].forEach(seedType => {
    document.getElementById(`seed-${instance}-${seedType}`).addEventListener('input', updateFilter);
  });
});

// Reseed button
document.getElementById('pg-reseed-all').addEventListener('click', reseedAll);

// Кнопки пресетов
document.querySelectorAll('.pg-preset').forEach(btn => {
  btn.addEventListener('click', () => applyPreset(btn.dataset.preset));
});

// Firefox-diag radio (тип турбулентности + cif)
document.querySelectorAll('input[name="pg-disp-type"], input[name="pg-cif"]').forEach(radio => {
  radio.addEventListener('change', updateFilter);
});

/* ═══════════════════════════════════════════════════════════════════
   FILTER APPLICATION MODE — три разных способа подключить фильтр.
   Каждый preview-блок привязан к своему фильтру (-front / -back /
   -initial); функция определяет инстанс по родителю SVG-элемента.
   ═══════════════════════════════════════════════════════════════════ */
function getInstanceForSvg(svgEl) {
  if (svgEl.closest('.preview-front'))   return 'front';
  if (svgEl.closest('.preview-back'))    return 'back';
  if (svgEl.closest('.preview-initial')) return 'initial';
  return null;
}

function setFilterMode(mode) {
  const SVGNS = 'http://www.w3.org/2000/svg';
  const targets = document.querySelectorAll(
    '.carpet-svg, .illuminated-initial > svg, .big-initial > svg'
  );

  // Очищаем все три способа применения
  document.body.classList.remove('pg-filter-on-css');
  targets.forEach(svg => {
    svg.removeAttribute('filter');
    const wrapG = svg.querySelector(':scope > g[data-pg-wrap="1"]');
    if (wrapG) {
      while (wrapG.firstChild) svg.appendChild(wrapG.firstChild);
      wrapG.remove();
    }
  });

  if (mode === 'css') {
    document.body.classList.add('pg-filter-on-css');
  } else if (mode === 'svg') {
    targets.forEach(svg => {
      const instance = getInstanceForSvg(svg);
      if (!instance) return;
      const g = document.createElementNS(SVGNS, 'g');
      g.setAttribute('filter', `url(#illumination-aged-${instance})`);
      g.setAttribute('data-pg-wrap', '1');
      while (svg.firstChild) g.appendChild(svg.firstChild);
      svg.appendChild(g);
    });
  } else if (mode === 'root') {
    targets.forEach(svg => {
      const instance = getInstanceForSvg(svg);
      if (!instance) return;
      svg.setAttribute('filter', `url(#illumination-aged-${instance})`);
    });
  }
}

// Включаем SVG-g режим по умолчанию (Firefox-safe + Chrome compatible)
setFilterMode('svg');

document.querySelectorAll('input[name="pg-mode"]').forEach(radio => {
  radio.addEventListener('change', e => {
    if (e.target.checked) setFilterMode(e.target.value);
  });
});

// Маркируем кнопку off специальным стилем
document.querySelector('.pg-preset[data-preset="off"]').classList.add('pg-preset-off');

updateFilter();
