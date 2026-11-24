# Стратегии A / B / C предотвращения runt'ов — спецификация имплементации

**Файл:** `relatio_aidani_codex_patched.html`
**Цель:** избежать роста абзаца на 1 строку из-за переноса последнего слова (или его слогового хвоста), применяя три каскадные техники — от превентивной до радикальной.

---

## 0. Резюме и логика каскада

| Стратегия | Когда применяется | Что делает | Эффект |
|---|---|---|---|
| **A** | превентивно, в фазе 0 (для всех абзацев основного текста) | запрещает `<wbr>` внутри последнего слова абзаца | устраняет worst-case runt'ы — однослоговые фрагменты |
| **B** | в фазе 0.5, для абзацев с обнаруженным runt'ом | сжимает пробелы предпоследней строки через занижение `--w` у `.ws` | runt-слово помещается на предпоследнюю строку; никаких видимых выступов |
| **C** | в фазе 0.5, при отказе B | разрешает runt-слову выступать за правую границу через negative `margin-right` на самом span'е | палеографически аутентичный «свисающий» хвост в зону outer-padding |

Логически это **каскад**: A применяется безусловно ко всем; для абзацев, где после A всё ещё образуется runt, в фазе 0.5 сначала пробуется B (невидимая), и только при её отказе — C (видимое выступание). Если все три отказали, runt сохраняется.

**Точечность стратегии C:** отрицательный `margin-right` задаётся на самом `<span class="runt-hang">`, не на `<p>`. Inline-margin влияет на outer-edge только этого конкретного inline-box'а; wrap-decisions других inline-box'ов в абзаце не затрагиваются. Эффект на runt-строку — точечный.

**Шрифтонезависимость:** все три стратегии работают через DOM-API (`getClientRects`, `getComputedStyle`, `getBoundingClientRect`), измеряющие физические пиксели независимо от шрифта. Калибровочные константы (например, лимит выступа в C) выбираются **адаптивно** в зависимости от шрифта runt-строки — см. Часть VI.

---

# Часть I — Стратегия A: превентивный запрет `<wbr>` в последнем слове

## A.1. Идея

Шейпер `walkWbrOnly` и `walkWrapLongWords` вставляют `<wbr>` между слогами длинных латинских слов (`praedicaverunt → prae·di·ca·ve·runt`). В большинстве случаев это полезно — даёт браузеру точки переноса. Но **в последнем слове абзаца** перенос всегда приводит к runt'у: либо целое слово на новой строке (большое слово, его ширина не помещается на предпоследнюю), либо слоговой хвост на новой строке (3–5 букв висят в одиночестве).

Стратегия A не предотвращает первое (целое слово на новой строке), но устраняет второе. Если `<wbr>`-точек внутри последнего слова нет, браузер вынужден переносить либо всё слово целиком, либо ничего. Слоговой одиночка-хвост невозможен.

## A.2. CSS

Никакого. Эффект достигается отсутствием `<wbr>` в DOM-узлах.

## A.3. JS — функция `markLastWords`

Вставляется в `<script>` рядом с `walkWrapLongWords` (~строка 8650, перед `preprocessSourceTemplate`):

```js
// ═══════════════════════════════════════════════════════════════
// Стратегия A: помечает последнее слово каждого основного абзаца
// классом lastword-no-wbr, чтобы walkWbrOnly / walkWrapLongWords /
// walkJitter пропускали его при расстановке <wbr>.
//
// Эффект: даже если слово не помещается на предпоследнюю строку и
// будет перенесено, оно перенесётся ЦЕЛИКОМ — не слоговым обрубком
// типа «runt» после «praedicave-». Это устраняет наиболее уродливые
// runt'ы за счёт нулевых усилий, без всякого layout-измерения.
//
// Применяется ДО walkWbrOnly / walkWrapLongWords / walkJitter в
// preprocessSourceTemplate. Маргиналии исключены — там runt'ы
// частые по природе узкой колонки, эстетически приемлемы.
//
// ВАЖНО: должна идти ДО markNoTorn (патч KELLS-NOTORN). См. Часть VII.
// ═══════════════════════════════════════════════════════════════

// Минимальная длина слова, для которой имеет смысл его защищать.
// Слово в 1–2 буквы и без <wbr> не получит — оно атомарно от
// рождения.
const LASTWORD_MIN_LEN = 4;

function isLastwordRelevant(block) {
  if (block.tagName !== 'P') return false;
  if (block.classList.contains('marginalia')) return false;
  if (block.classList.contains('rubric')) return false;
  return true;
}

function markLastWords(root) {
  const blocks = root.querySelectorAll('p');
  let marked = 0;

  for (let bi = 0; bi < blocks.length; bi++) {
    const block = blocks[bi];
    if (!isLastwordRelevant(block)) continue;

    // Найти последний значащий text-node с буквами.
    const allTextNodes = [];
    const walker = document.createTreeWalker(
      block, NodeFilter.SHOW_TEXT, null, false
    );
    let n;
    while ((n = walker.nextNode())) allTextNodes.push(n);

    let lastSig = -1;
    for (let i = allTextNodes.length - 1; i >= 0; i--) {
      if (/[A-Za-zÀ-ÿĀ-ſ]/.test(allTextNodes[i].nodeValue || '')) {
        lastSig = i;
        break;
      }
    }
    if (lastSig < 0) continue;

    const tn = allTextNodes[lastSig];
    const v = tn.nodeValue;
    // Последняя последовательность букв (без хвостовой пунктуации).
    const m = v.match(/([A-Za-zÀ-ÿĀ-ſ]+)([^A-Za-zÀ-ÿĀ-ſ]*)$/);
    if (!m) continue;
    const word = m[1];
    if (word.length < LASTWORD_MIN_LEN) continue;

    const wordStart = v.length - m[0].length;
    const wordEnd = wordStart + word.length;

    // Обернуть слово в span. Хвостовая пунктуация (m[2]) остаётся
    // снаружи — она не нужна внутри обёртки, и её наружное положение
    // упрощает дальнейшую логику стратегии C.
    const before = v.slice(0, wordStart);
    const after = v.slice(wordEnd);

    const parent = tn.parentNode;
    if (!parent) continue;

    const span = document.createElement('span');
    span.className = 'lastword-no-wbr';
    span.textContent = word;

    if (before.length > 0) {
      parent.insertBefore(document.createTextNode(before), tn);
    }
    parent.insertBefore(span, tn);
    if (after.length > 0) {
      parent.insertBefore(document.createTextNode(after), tn);
    }
    parent.removeChild(tn);

    marked++;
  }

  if (window.console) {
    console.log('[lastword-no-wbr] marked=' + marked);
  }
}
```

## A.4. Интеграция с walk-функциями

Добавить `lastword-no-wbr` в skip-листы трёх функций — `walkJitter` (~строка 7714), `walkWbrOnly` (~строка 8480), `walkWrapLongWords` (~строка 8650). В каждой из них уже есть проверка classList — добавить одну строку:

```js
if (el.classList && (
    el.classList.contains('liga-protect') ||
    el.classList.contains('lastword-no-wbr') ||   // ← НОВОЕ
    ...
)) return;
```

## A.5. Точка вызова

В `preprocessSourceTemplate` (~строка 8800), после `applyAbbreviations` / `decorateTituli` / `addAbbrTranslateSources`, **до** обработки маргиналий, **до** `markNoTorn` (если патч KELLS-NOTORN применён) и до walk-функций:

```js
  applyAbbreviations(root);
  decorateTituli(root);
  addAbbrTranslateSources(root);

  // Стратегия A: пометить последнее слово каждого абзаца, чтобы
  // walkWrapLongWords не вставил <wbr> внутри.
  // ВАЖНО: ДО markNoTorn — иначе markNoTorn расщепит финальное
  // слово на text-node + <span class="no-torn">t.</span>, и
  // markLastWords найдёт «t» как последнее слово (1 буква, пропустит
  // через LASTWORD_MIN_LEN). См. Часть VII.
  markLastWords(root);

  // (Патч KELLS-NOTORN, если применён) — теперь видит lastword-no-wbr
  // как готовую обёртку и пропускает её через skip-лист.
  // try { markNoTorn(root); } ...

  // ... далее splitMarginaliaForTranslate, walkWbrOnly, walkJitter,
  // walkWrapLongWords — все они учитывают новый класс через skip-листы.
```

## A.6. Edge cases стратегии A

- **Короткие абзацы (одно слово).** Слово оборачивается, но толку нет — там и так нет переноса. Безвредно.
- **Параграф заканчивается формулой** типа `Amen.` — `Amen` < `LASTWORD_MIN_LEN` (4 буквы), не оборачивается. Это намеренно: для коротких слов и так нет `<wbr>`.
- **Параграф заканчивается составной обёрткой**, например на `<em class="uncial-passage">`. TreeWalker дойдёт до text-node-а внутри `<em>`, оборачивание сработает — span появится **внутри** `<em>`. Это безопасно: style унаследуется через каскад (`lastword-no-wbr` стилей не имеет, только маркерный класс), uncial-шрифтовый контекст в `<em>` не нарушается. Стратегия C, если запустится для этого абзаца, оборачивает только последнее слово (тоже внутри `<em>`) — без охвата всего `<em>` (см. C.4, Uncial-passage runt).
- **Параграф с `<abbr>` на конце**, например `Amen` — никаких `<wbr>` в `<abbr>` и так нет, ничего не оборачивается дополнительно. Безвредно.
- **Параграф, у которого последнее значащее — это abbreviation** типа `<abbr>DNI</abbr>` без хвостовой текстовой пунктуации. TreeWalker пропустит abbr (не text-node), последний text-node может оказаться на 1–2 уровня выше. Если в нём есть слово ≥ `LASTWORD_MIN_LEN` — оборачивается оно. Это семантически не «последнее слово абзаца», но для целей стратегии A безразлично — мы защищаем от runt'а слово, которое физически может попасть на отдельную строку, и любое длинное слово в хвосте абзаца — кандидат.

---

# Часть II — Стратегия B: сжатие пробелов предпоследней строки

## B.1. Идея

Когда абзац всё-таки получил runt (даже после стратегии A) и runt маленький — обычно достаточно сжать несколько пробелов на предпоследней строке, чтобы runt-слово влезло. `.ws` спаны имеют `padding-right: calc(var(--w) * var(--space-amp))`. Если переписать `--w` у спанов предпоследней строки в сторону минимума, padding обнулится, ширина строки уменьшится, runt-слово получит шанс поместиться.

В отличие от стратегии C, это **полностью невидимое** изменение — пробелы и так дрожат от 0 до `--space-amp`, занижение `--w` до минимальных значений не выходит за пределы естественной вариативности.

## B.2. CSS

Никакого. Изменения в DOM — переписывание inline-style `--w` на существующих `.ws` спанах.

## B.3. JS — функции `analyzeRunt`, `compressPenultimateLine`

Вставляется в `<script>` рядом с другими runt-функциями (~строка 6190, после `paginate`). В этом блоке также живут общие утилиты `analyzeRunt` и `countVisualLines`, используемые и стратегией C.

```js
// ═══════════════════════════════════════════════════════════════
// ОБЩАЯ УТИЛИТА: analyzeRunt(p)
//
// Возвращает данные о runt'е или null. Используется обеими страте-
// гиями фазы 0.5 (B и C), а также preventRunts (как gate-условие).
//
// runt = объект { lineCount, lastLineWidth, penultLineWidth,
//                 lastLineY, penultLineY }.
//
// Критерии runt-кандидата (всё одновременно):
//   - lineCount >= 2 (одно-строчный абзац не runt по определению);
//   - lastLineWidth < RUNT_MAX_LINE_WIDTH_PX (~60 px) ИЛИ
//     lastLineWidth / penultLineWidth < RUNT_MAX_LINE_FRACTION (0.25).
//
// p должен быть уже в DOM (в measurer'е) при вызове, иначе
// getClientRects() вернёт пустой массив. Также можно вернуть null
// рано через флаг no-runt-hang на p — этот класс зарезервирован
// как явный opt-out из любого runt-prevention для конкретного абзаца.
// ═══════════════════════════════════════════════════════════════

const RUNT_MAX_LINE_WIDTH_PX = 60;
const RUNT_MAX_LINE_FRACTION = 0.25;

function analyzeRunt(p) {
  if (!p.isConnected) return null;
  if (p.classList && p.classList.contains('no-runt-hang')) return null;

  const range = document.createRange();
  range.selectNodeContents(p);
  const rawRects = range.getClientRects();

  // Фильтруем нулевые и группируем по Y (несколько rect'ов могут
  // лежать на одной визуальной строке, если параграф содержит
  // inline-элементы разной высоты — например, .ws спан рядом с
  // буквенным фрагментом).
  const byLine = [];
  for (let i = 0; i < rawRects.length; i++) {
    const r = rawRects[i];
    if (r.width === 0 || r.height === 0) continue;
    // Ищем существующую строку с близким Y (допуск ±3 px).
    let line = null;
    for (let j = 0; j < byLine.length; j++) {
      if (Math.abs(byLine[j].top - r.top) < 3) {
        line = byLine[j];
        break;
      }
    }
    if (line) {
      line.left = Math.min(line.left, r.left);
      line.right = Math.max(line.right, r.right);
      line.width = line.right - line.left;
    } else {
      byLine.push({
        top: r.top,
        left: r.left,
        right: r.right,
        width: r.width
      });
    }
  }

  if (byLine.length < 2) return null;

  // Сортируем по top (на всякий случай — обычно rects идут в порядке
  // отрисовки сверху вниз, но не гарантировано).
  byLine.sort(function(a, b) { return a.top - b.top; });

  const last = byLine[byLine.length - 1];
  const penult = byLine[byLine.length - 2];

  const isRunt =
    last.width < RUNT_MAX_LINE_WIDTH_PX ||
    (last.width / penult.width) < RUNT_MAX_LINE_FRACTION;

  if (!isRunt) return null;

  return {
    lineCount: byLine.length,
    lastLineWidth: last.width,
    penultLineWidth: penult.width,
    lastLineY: last.top,
    penultLineY: penult.top,
  };
}

// ═══════════════════════════════════════════════════════════════
// Стратегия B: занижает --w у .ws спанов предпоследней строки
// runt-абзаца, чтобы runt-слово вернулось на предпоследнюю строку.
//
// Если runt узкий (1–3 буквы), достаточно компенсации 0.5–1.5em
// суммарно по строке. При --space-amp-base 0.20em это 3–8 пробелов
// с занижением --w на 0.5 — естественная вариативность джиттера.
//
// Применяется ВНУТРИ preventRunts, до попытки стратегии C.
// При отказе восстанавливает исходные --w (сохраняемые в data-w0).
// ═══════════════════════════════════════════════════════════════

// Насколько занижать --w. 0 = полное сжатие до минимума, 1 = без
// изменений. 0.3 — мягкая компрессия (сохраняем 30% от исходного).
const COMPRESS_W_RETENTION = 0.3;

// Минимальное число .ws на предпоследней строке, чтобы пробовать
// сжатие. Меньше — экономия слишком мала.
const COMPRESS_MIN_WS = 3;

function compressPenultimateLine(p, runt, measurerContent) {
  // Инициализация общего лога фазы 0.5.
  if (!window.__runtPreventionLog) window.__runtPreventionLog = [];

  const logEntry = {
    strategy: 'B',
    pPreview: (p.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60),
    lineCount: runt.lineCount,
    lastLineWidth: Math.round(runt.lastLineWidth),
    penultLineWidth: Math.round(runt.penultLineWidth),
    widthFraction: +(runt.lastLineWidth / runt.penultLineWidth).toFixed(3),
  };

  // p должен быть в measurerContent (или элементе с layout'ом).
  // Найдём все .ws на предпоследней строке.
  const allWs = p.querySelectorAll('.ws');
  if (allWs.length < COMPRESS_MIN_WS) {
    logEntry.result = 'refused';
    logEntry.reason = 'too_few_ws_in_paragraph';
    logEntry.wsTotalInP = allWs.length;
    window.__runtPreventionLog.push(logEntry);
    return false;
  }

  const targetY = runt.penultLineY;
  const candidates = [];
  for (let i = 0; i < allWs.length; i++) {
    const ws = allWs[i];
    const rect = ws.getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) continue;
    if (Math.abs(rect.top - targetY) < 3) {
      candidates.push(ws);
    }
  }

  logEntry.wsCandidates = candidates.length;

  if (candidates.length < COMPRESS_MIN_WS) {
    logEntry.result = 'refused';
    logEntry.reason = 'too_few_ws_on_penult_line';
    window.__runtPreventionLog.push(logEntry);
    return false;
  }

  // Сохранить исходные --w (для отката) и переписать.
  for (let i = 0; i < candidates.length; i++) {
    const ws = candidates[i];
    // data-w0 — сохранённое исходное значение.
    if (!ws.dataset.w0) {
      ws.dataset.w0 = ws.style.getPropertyValue('--w') || '0.5';
    }
    const w0 = parseFloat(ws.dataset.w0);
    const w1 = w0 * COMPRESS_W_RETENTION;
    ws.style.setProperty('--w', w1.toFixed(3));
  }

  // Перемерим — runt исчез?
  const lineCountAfter = countVisualLines(p);
  logEntry.newLineCount = lineCountAfter;

  if (lineCountAfter < runt.lineCount) {
    logEntry.result = 'success';
    window.__runtPreventionLog.push(logEntry);
    return true;
  }

  // Откат: восстанавливаем исходные --w.
  for (let i = 0; i < candidates.length; i++) {
    const ws = candidates[i];
    if (ws.dataset.w0) {
      ws.style.setProperty('--w', ws.dataset.w0);
      delete ws.dataset.w0;
    }
  }
  logEntry.result = 'refused';
  logEntry.reason = 'no_improvement';
  window.__runtPreventionLog.push(logEntry);
  return false;
}

// Считает визуальное число строк в p. Вынесено в утилиту, потому
// что используется и B, и C.
function countVisualLines(p) {
  const range = document.createRange();
  range.selectNodeContents(p);
  const rects = range.getClientRects();
  const lines = [];
  for (let i = 0; i < rects.length; i++) {
    const r = rects[i];
    if (r.width === 0 || r.height === 0) continue;
    let found = false;
    for (let j = 0; j < lines.length; j++) {
      if (Math.abs(lines[j] - r.top) < 3) { found = true; break; }
    }
    if (!found) lines.push(r.top);
  }
  return lines.length;
}
```

## B.4. Edge cases стратегии B

- **Меньше `COMPRESS_MIN_WS` пробелов на предпоследней строке** — отказ. Случается, например, в абзацах с длинными слитными словами и редкими пробелами.
- **Исходные `--w` уже близки к 0** (мало приниженных значений) — сжатие даст мало эффекта. Функция всё равно попробует, перемерит, и если не помогло — откатит.
- **Предпоследняя строка целиком внутри `<em class="uncial-passage">`.** Uncial-пассажи пропускаются walkWbrOnly / walkWrapLongWords (они в skip-листах) и **не получают `.ws` спанов** — там собственная типографика с фиксированным `word-spacing: 3.85px` в абсолютных пикселях. Если предпоследняя строка лежит полностью в uncial-passage, `compressPenultimateLine` найдёт ноль `.ws` кандидатов на ней и вернёт `false`. Runt уйдёт в C. Это известное ограничение, обусловленное архитектурой uncial-типографики; лечить B-стратегией бессмысленно — у `word-spacing` в px нет CSS-переменной, через которую можно занизить значение. Смешанные строки (часть Kells + часть uncial) обрабатываются нормально — B сжимает только `.ws` Kells-части, чего обычно достаточно.
- **Идемпотентность.** `data-w0` сохраняется на спане при первой компрессии. При повторном вызове `compressPenultimateLine` увидит сохранённое значение и не перепишет его заново. При откате `data-w0` удаляется. Безопасно для повторных вызовов в пределах одной сессии.
- **Resize.** При resize фаза 0.5 не перезапускается. Сохранённые `--w` остаются в их сжатом состоянии. Это нормально — абзац всё так же не должен породить runt в новом размере, если он не породил в исходном (resize меняет только маргиналии, не основную ширину).

---

# Часть III — Стратегия C: runt-hang (точечная и шрифт-адаптивная)

## C.1. Особенности

1. **Точечный margin.** `margin-right: -X` задаётся на самом `<span class="runt-hang">`, не на `<p>`. Inline-margin влияет только на outer-edge **этого** inline-box; line-break decisions других inline-box'ов в абзаце не затрагиваются. Только runt-строка получает дополнительную ширину для wrap-decision.
2. **Шрифт-адаптивный лимит.** Максимальный выступ выбирается на основании шрифта runt-строки через `getComputedStyle()`. Для Uncialis (буквы 12.6 px при font-size 0.86em) — 65 px; для Kells (8.7 px) — 50 px; для Remedius — 50 px; для Beda — 45 px. Это позволяет лечить runt'ы из 4–5 крупных uncial-букв, не теряя сдержанности на Kells-абзацах.
3. **Расширенная обёртка.** Span `runt-hang` всегда охватывает range **от начала runt-слова до конца блока** (включая хвостовую пунктуацию). Это страховка от того, что точка/запятая после runt-слова окажется снаружи span'а и negative margin её визуально втянет внутрь.
4. **Uncial-passage compatibility.** Если последнее слово лежит внутри `<em class="uncial-passage">`, runt-hang span создаётся **только вокруг этого слова** (внутри `<em>`), а не вокруг всего `<em>`. Шрифт-контекст (Uncialis) наследуется через каскад, и `white-space: nowrap` действует только на одно слово — не на весь uncial-фрагмент. Это критично: попытка охватить весь `<em>` атомарно ломает абзацы, целиком состоящие из uncial-passage, превращая их в одну непереносимую строку.

## C.2. CSS

```css
  /* ═══════════════════════════════════════════════════════════════
     RUNT-HANG — выступание последнего слова абзаца за правое поле.

     Палеографически аутентичный приём: в инсулярных кодексах писец
     регулярно позволял последнему слову строки слегка торчать за
     bounding line, если этим избегался перенос по слогам и образо-
     вание короткой «сиротской» последней строки.

     ТОЧЕЧНОСТЬ: отрицательный margin-right задаётся на самом
     <span class="runt-hang"> (а не на родительском <p>). Inline-
     margin влияет только на outer-edge этого конкретного span'а
     при line-break-decision. Остальные строки <p> не затрагиваются.
     Возможные коллизии с маргиналиями см. в Edge cases.            */
  .runt-hang {
    white-space: nowrap;
    /* Отрицательный margin-right: эффективная outer-width span'а
       при wrap-decision равна (content-width − runt-hang-x). Браузер
       решает, что после span'а нужно меньше горизонтального места,
       и runt-слово оказывается на предпоследней строке. Визуально
       сам span рисуется в полную width своего content; «лишние»
       --runt-hang-x пикселей выступают за правый край line-box. */
    margin-right: calc(0px - var(--runt-hang-x, 0px));
  }

  /* Локальное снятие overflow:hidden у .folio-content для фолио,
     на которых есть хотя бы один runt-hang. Без этого выступающий
     хвост обрезается. Глобальный overflow:hidden на .folio
     остаётся — выступ заведомо меньше padding-outer 82px, поэтому
     за пределы фолио ничего не уходит. */
  .folio-content.has-runt-hang-inside {
    overflow: visible;
  }
```

## C.3. JS — функция `applyRuntHang` и связанные

```js
// ═══════════════════════════════════════════════════════════════
// Стратегия C: оборачивает runt-target в <span class="runt-hang">
// и задаёт ему --runt-hang-x для negative margin-right.
//
// Шрифт-адаптивный лимит выступа определяется через getRuntHangLimit:
// на основании computed font-family runt-строки выбирается одно из
// четырёх значений (Kells/Uncialis/Remedius/Beda).
//
// Обёртка всегда расширяется ДО КОНЦА блока, чтобы:
//   (а) margin-right на span'е не сдвигал visible-контент после
//       runt'а влево (его попросту нет — пунктуация уже в обёртке);
//   (б) visual выступ был непрерывным, без артефактов «висящей»
//       точки за пределами обёртки.
//
// Возвращает true при успехе, false при отказе.
// ═══════════════════════════════════════════════════════════════

// Шрифт-адаптивные лимиты выступа (в px). Калибровка:
//   средняя ширина строчной буквы (в em) × font-size (px) × ~5 букв.
// Для font-size 0.86em (= 13.76 px на base 16 px):
//   Kells:    0.635em × 13.76 × ~5 = 44 px → округлили вверх до 50
//   Uncialis: 0.92em  × 13.76 × ~5 = 63 px → округлили вверх до 65
//   Remedius: оценка ~0.70em → ~48 px → 50
//   Beda:     оценка ~0.65em → ~45 px → 45
// Значения выбраны так, чтобы покрывать 5-буквенный runt и при этом
// не уходить далеко за --folio-pad-outer (82 px), оставляя резерв
// для возможных коллизий с маргиналиями.
const RUNT_HANG_LIMIT_KELLS    = 50;
const RUNT_HANG_LIMIT_UNCIALIS = 65;
const RUNT_HANG_LIMIT_REMEDIUS = 50;
const RUNT_HANG_LIMIT_BEDA     = 45;
const RUNT_HANG_LIMIT_DEFAULT  = 50;

const HANG_SAFETY_PX = 4;

function applyRuntHang(p, runt, measurerContent) {
  // Инициализация общего лога фазы 0.5 (доступен через window).
  if (!window.__runtPreventionLog) window.__runtPreventionLog = [];

  const logEntry = {
    strategy: 'C',
    pPreview: (p.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60),
    lineCount: runt.lineCount,
    lastLineWidth: Math.round(runt.lastLineWidth),
    penultLineWidth: Math.round(runt.penultLineWidth),
    widthFraction: +(runt.lastLineWidth / runt.penultLineWidth).toFixed(3),
  };

  // Найти DOM-range от начала runt-слова до конца <p>.
  const tail = findRuntTailRange(p);
  if (!tail) {
    logEntry.result = 'refused';
    logEntry.reason = 'no_tail_target';
    window.__runtPreventionLog.push(logEntry);
    return false;
  }

  // Шрифт-адаптивный лимит.
  const limit = getRuntHangLimit(tail);
  logEntry.font = tail.fontHint;
  logEntry.limit = limit;

  const xPx = Math.round(runt.lastLineWidth + HANG_SAFETY_PX);
  logEntry.xPx = xPx;

  if (xPx > limit) {
    logEntry.result = 'refused';
    logEntry.reason = 'over_limit';
    window.__runtPreventionLog.push(logEntry);
    if (window.console) {
      console.log('[runt-hang] refused: xPx=' + xPx +
                  ' > limit=' + limit +
                  ' (font: ' + tail.fontHint + ')');
    }
    return false;
  }

  // Обернуть range в <span class="runt-hang">.
  const span = document.createElement('span');
  span.className = 'runt-hang';
  span.style.setProperty('--runt-hang-x', xPx + 'px');

  try {
    tail.range.surroundContents(span);
    logEntry.wrapMethod = 'surround';
  } catch (e) {
    // Fallback: extract → wrap → reinsert.
    const fragment = tail.range.extractContents();
    span.appendChild(fragment);
    tail.range.insertNode(span);
    logEntry.wrapMethod = 'extract_fallback';
  }

  // Измеряем фактическую ширину runt-target (того, что попало в span).
  // Это полезно для диагностики: если targetWidth заметно меньше
  // lastLineWidth — значит, на runt-строке было не одно слово, и
  // margin влияет только на финальный фрагмент.
  const spanRects = Array.from(span.getClientRects()).filter(r => r.width > 0);
  if (spanRects.length > 0) {
    let maxW = 0;
    for (const r of spanRects) if (r.width > maxW) maxW = r.width;
    logEntry.targetWidth = Math.round(maxW);
  }

  // Перемерим (p всё ещё в measurer'е).
  const newLineCount = countVisualLines(p);
  logEntry.newLineCount = newLineCount;

  if (newLineCount >= runt.lineCount) {
    // Откат: развернуть span.
    unwrapElement(span);
    logEntry.result = 'refused';
    logEntry.reason = 'no_improvement';
    window.__runtPreventionLog.push(logEntry);
    if (window.console) {
      console.log('[runt-hang] refused: no_improvement' +
                  ' (xPx=' + xPx +
                  ', targetWidth=' + (logEntry.targetWidth || '?') +
                  ', lineCount stayed at ' + newLineCount +
                  ', font: ' + tail.fontHint + ')');
    }
    return false;
  }

  logEntry.result = 'success';
  window.__runtPreventionLog.push(logEntry);
  return true;
}

// ── Шрифт-адаптивный лимит ─────────────────────────────────────
// Возвращает лимит выступа в px на основании computed font-family
// первого text-node-а внутри tail-range. Если шрифт не распознан —
// дефолт. Также записывает tail.fontHint (для логирования).
function getRuntHangLimit(tail) {
  const probeEl = findProbeElementForRange(tail.range);
  if (!probeEl) {
    tail.fontHint = 'none';
    return RUNT_HANG_LIMIT_DEFAULT;
  }

  const cs = getComputedStyle(probeEl);
  const fam = (cs.fontFamily || '').toLowerCase();

  // Сопоставление с известными font-family из CSS.
  if (fam.indexOf('uncialis') !== -1) {
    tail.fontHint = 'uncialis';
    return RUNT_HANG_LIMIT_UNCIALIS;
  }
  if (fam.indexOf('remedius') !== -1) {
    tail.fontHint = 'remedius';
    return RUNT_HANG_LIMIT_REMEDIUS;
  }
  if (fam.indexOf('beda') !== -1) {
    tail.fontHint = 'beda';
    return RUNT_HANG_LIMIT_BEDA;
  }
  if (fam.indexOf('kells') !== -1) {
    tail.fontHint = 'kells';
    return RUNT_HANG_LIMIT_KELLS;
  }
  // Шрифт не распознан — дефолт (равен Kells).
  tail.fontHint = 'unknown:' + fam.slice(0, 40);
  return RUNT_HANG_LIMIT_DEFAULT;
}

// Возвращает первый Element, computed style которого описывает
// шрифт первого text-node-а в range. Если range стартует в Element,
// спускается до первого text-node-а; берёт его parentElement.
function findProbeElementForRange(range) {
  const startNode = range.startContainer;
  // Если range стартует в text-node — его родительский Element.
  if (startNode.nodeType === 3) {
    return startNode.parentElement;
  }
  // Иначе — childNodes[startOffset] либо первый text-node внутри.
  const child = startNode.childNodes[range.startOffset];
  if (child) {
    if (child.nodeType === 3) return child.parentElement;
    if (child.nodeType === 1) {
      // Спускаемся в первый text-node под этим элементом.
      const walker = document.createTreeWalker(
        child, NodeFilter.SHOW_TEXT, null, false);
      const firstText = walker.nextNode();
      if (firstText) return firstText.parentElement;
      return child;
    }
  }
  // Range пустой или нестандартный — fallback на стартовый Element.
  return startNode.nodeType === 1 ? startNode : null;
}

// Находит Range от начала последнего значащего слова в p до конца
// последнего узла p (включая хвостовую пунктуацию и whitespace).
// Возвращает { range } или null.
function findRuntTailRange(p) {
  const allTextNodes = [];
  const walker = document.createTreeWalker(
    p, NodeFilter.SHOW_TEXT, null, false
  );
  let n;
  while ((n = walker.nextNode())) allTextNodes.push(n);
  if (allTextNodes.length === 0) return null;

  // Идём с конца, ищем text-node со словесными символами.
  let lastSig = -1;
  for (let i = allTextNodes.length - 1; i >= 0; i--) {
    if (/[A-Za-zÀ-ÿĀ-ſ]/.test(allTextNodes[i].nodeValue || '')) {
      lastSig = i;
      break;
    }
  }
  if (lastSig < 0) return null;

  const tn = allTextNodes[lastSig];
  const m = tn.nodeValue.match(/[A-Za-zÀ-ÿĀ-ſ]+[^\s]*$/);
  if (!m) return null;
  const startOffset = tn.nodeValue.length - m[0].length;

  let startNode = tn;
  let startOff = startOffset;
  let parent = tn.parentNode;

  // Подъём через прозрачные обёртки. Последовательные ветки —
  // от внутренней структуры наружу:
  //   .word-render/.word-source → .word-wbr
  //   .lastword-no-wbr
  //   .uncial-passage (см. ниже)
  if (parent && parent.classList) {
    if (parent.classList.contains('word-render') ||
        parent.classList.contains('word-source')) {
      const wordWbr = parent.parentNode;
      if (wordWbr && wordWbr.classList &&
          wordWbr.classList.contains('word-wbr')) {
        startNode = wordWbr.parentNode;
        startOff = Array.prototype.indexOf.call(
          wordWbr.parentNode.childNodes, wordWbr);
      }
    } else if (parent.classList.contains('lastword-no-wbr')) {
      startNode = parent.parentNode;
      startOff = Array.prototype.indexOf.call(
        parent.parentNode.childNodes, parent);
    }
  }

  // ВНИМАНИЕ: ветка «подъёма до <em.uncial-passage>» НАМЕРЕННО НЕ
  // реализована. Раньше пытались поднимать range до самого <em>,
  // чтобы «не разрезать шрифт-контекст». Это давало баг: если
  // <em class="uncial-passage"> занимал весь абзац (или большую
  // его часть), runt-hang span охватывал весь <em>, и
  // white-space: nowrap на .runt-hang слепливал все uncial-строки
  // в одну, уезжающую за правое поле. Симптом особенно ярко
  // проявлялся в абзацах рядом с .mg-coemanus (узкая колонка →
  // больше runt'ов в uncial).
  //
  // Правильное поведение: оборачивать ТОЛЬКО последнее слово,
  // даже если оно внутри <em.uncial-passage>. Шрифт-контекст
  // (Uncialis) автоматически наследуется через каскад — runt-hang
  // span, лежащий внутри <em>, рендерится Uncialis'ом. Никакого
  // разрезания шрифта не происходит, потому что в обёртку попадает
  // только хвост уже uncial-форматированного текста.

  const range = document.createRange();
  if (startNode === tn) {
    range.setStart(tn, startOff);
  } else {
    range.setStart(startNode, startOff);
  }
  range.setEnd(p, p.childNodes.length);

  return { range: range };
}

// Разворачивает обёртку: содержимое перемещается на место span,
// span удаляется.
function unwrapElement(el) {
  const parent = el.parentNode;
  if (!parent) return;
  while (el.firstChild) {
    parent.insertBefore(el.firstChild, el);
  }
  parent.removeChild(el);
  parent.normalize();
}

// markFoliosWithRuntHang — без изменений с предыдущей версии.
function markFoliosWithRuntHang() {
  const contents = document.querySelectorAll(
    '#codex-book .folio-content'
  );
  for (let i = 0; i < contents.length; i++) {
    const c = contents[i];
    if (c.querySelector('.runt-hang')) {
      c.classList.add('has-runt-hang-inside');
    }
  }
}
```

## C.4. Edge cases стратегии C

- **Содержимое после runt-слова не помещается в span целиком.** Может случиться, если в `<p>` есть необычная структура — например, иллюминированный ornament-line после слова. Тогда `range.surroundContents` бросит ошибку (range cross-boundary). Fallback через `extractContents` + `insertNode` справится с большинством случаев, но decoratives внутри лучше обходить — в `findRuntTailRange` стоит проверить, нет ли блочных элементов между runt-словом и концом `<p>`, и в случае их обнаружения вернуть `null`.
- **Translate-режим.** Когда runt-hang обёртка лежит вокруг `.word-wbr` (двойного source/render), `findRuntTailRange` поднимается до самого `.word-wbr` через ветку `word-render`/`word-source`, и span охватывает оба внутренних слоя. В translate-режиме `.word-render` скрыт, виден `.word-source` — но и для него `margin-right: -X` работает (margin наследуется на тот же span). Поведение симметрично, выступание корректное.
- **Коллизия с маргиналией в outer-padding.** Эта же проблема, что и раньше — выступ может зайти на территорию маргиналии. Не лечится в рамках этой спеки (нужна post-render validation после `positionMarginalia`).
- **Uncial-passage runt.** Если последнее слово лежит внутри `<em class="uncial-passage">`, runt-hang span создаётся вокруг **этого слова** (внутри `<em>`), а **не** вокруг всего `<em>`. Получается:
  ```html
  <p>
    ... обычный текст ...
    <em class="uncial-passage">
      ... uncial text ... 
      <span class="runt-hang">Amen.</span>
    </em>
  </p>
  ```
  Шрифт-контекст внутри runt-hang span'а — Uncialis, потому что span наследует font-family от родительского `<em>`. Никакого разрезания шрифта не происходит. `getRuntHangLimit` опросит computed font-family у span'а (получит `0550 Uncialis`) и применит лимит 65 px.

  **Важно: НЕ поднимать range до `<em>` целиком.** Если runt-hang охватывает весь `<em class="uncial-passage">`, `white-space: nowrap` на span'е заставит все строки uncial-пассажа слиться в одну, уезжающую за правое поле. Это особенно ярко проявляется в абзацах рядом с `.mg-coemanus` маргиналиями, где узкая колонка чаще порождает runt-условия для uncial-фрагментов. См. комментарий в `findRuntTailRange`.
- **Шрифт не распознан.** Если `font-family` runt-строки не содержит ни одного из ключевых имён (`uncialis`/`remedius`/`beda`/`kells`), `getRuntHangLimit` возвращает `RUNT_HANG_LIMIT_DEFAULT` (50 px). В консоль логируется `fontHint: 'unknown:...'` — это сигнал, что либо появился новый шрифт, либо font-family записан в неожиданном виде; стоит обновить mapping. На практике в текущем проекте такого не должно случаться.

---

# Часть IV — Композиция: как стратегии работают вместе

## IV.1. Изменения в `preventRunts`

Объединённая функция фазы 0.5 применяет B и C каскадно для каждого `<p>` с runt'ом:

```js
function preventRunts(blocks, measurerContent) {
  let processed = 0;
  let fixedB = 0;
  let fixedC = 0;
  let refused = 0;

  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    if (block.nodeType !== 1) continue;
    if (block.tagName !== 'P') continue;
    if (block.classList.contains('theological')) continue;
    if (block.classList.contains('dropcap')) continue;
    if (block.classList.contains('no-runt-hang')) continue;

    processed++;

    const parent = block.parentNode;
    const nextSibling = block.nextSibling;

    measurerContent.replaceChildren(block);

    const runt = analyzeRunt(block);
    if (runt) {
      // Попытка B — мягкая компрессия пробелов.
      const okB = compressPenultimateLine(block, runt, measurerContent);
      if (okB) {
        fixedB++;
      } else {
        // Попытка C — runt-hang.
        const okC = applyRuntHang(block, runt, measurerContent);
        if (okC) fixedC++;
        else refused++;
      }
    }

    measurerContent.removeChild(block);
    if (nextSibling) parent.insertBefore(block, nextSibling);
    else parent.appendChild(block);
  }

  measurerContent.replaceChildren();

  return {
    processed: processed,
    fixedB: fixedB,
    fixedC: fixedC,
    refused: refused
  };
}
```

## IV.2. Изменения в `run()`

Полный набор вставок в `run()`:

```js
  // ── Фаза 0 ──
  preprocessSourceTemplate();   // внутри теперь вызывает markLastWords
                                // ДО markNoTorn (см. Часть VII)

  const blocks = [];
  // ... (без изменений)

  const measurer = createMeasurer();
  document.body.appendChild(measurer);
  const measurerContent = measurer.querySelector('.folio-content');
  const lineHeight = measureLineHeight(measurerContent);

  // ── Фаза 0.5: runt prevention (Стратегии B + C) ──
  const tRuntStart = performance.now();
  const runtStats = preventRunts(blocks, measurerContent);
  const tRuntEnd = performance.now();
  if (window.console) {
    console.log(
      '[runt-prevention] processed=' + runtStats.processed +
      ' fixedB=' + runtStats.fixedB +
      ' fixedC=' + runtStats.fixedC +
      ' refused=' + runtStats.refused +
      ' in ' + (tRuntEnd - tRuntStart).toFixed(0) + ' ms'
    );
  }

  // ── Фаза 1: пагинация ──
  const t0 = performance.now();
  const pages = paginate(blocks, measurerContent, lineHeight);
  const t1 = performance.now();
  measurer.remove();

  // ── Фаза 2: построение DOM книги ──
  renderBook(pages);
  markFoliosWithRuntHang();   // ставит has-runt-hang-inside на
                              // .folio-content с runt-обёрткой
  // ... далее без изменений
```

Внутри `preprocessSourceTemplate` (~стр. 8800) вставка `markLastWords` встаёт между `addAbbrTranslateSources` и `markNoTorn`:

```js
function preprocessSourceTemplate() {
  // ... шаги 1, 1.5 (br → пробел, trim в маргиналиях)

  applyAbbreviations(root);
  decorateTituli(root);
  addAbbrTranslateSources(root);

  // Стратегия A.
  // ВАЖНО: ДО markNoTorn — иначе markNoTorn расщепит финальное слово
  // на «префикс» + <span class="no-torn">t.</span>, и markLastWords
  // вместо целого слова найдёт «t» (1 буква, < LASTWORD_MIN_LEN,
  // skipped). См. Часть VII.
  markLastWords(root);

  // ... шаги 4, 5, 6 (split, wbr, jitter, wrapLongWords)
  //     внутри top-цикла теперь идёт markNoTorn (если применён патч
  //     KELLS-NOTORN).
}
```

## IV.3. Логика взаимодействия

| Сценарий | A применилась? | B попробовалась? | C попробовалась? | Итог |
|---|---|---|---|---|
| Длинный абзац без runt'а | да (бесплатно) | нет (нет runt'а) | нет | абзац без `<wbr>` в последнем слове, runt и не возник |
| Абзац с runt'ом из целого слова, runt узкий | да | да, успех | нет | пробелы сжаты, слово вернулось — невидимо |
| Абзац с runt'ом, узким, но сжатие не помогло | да | пробовалась, отказ | да, успех | runt-слово выступает за край |
| Абзац с runt'ом из крупного слова (Kells > 50 px) | да | возможен отказ B | отказ C (превышен лимит) | runt сохраняется как есть |
| Абзац с runt'ом из крупного uncial-слова (> 65 px) | да | отказ B (нет .ws в uncial) | отказ C (превышен лимит) | runt сохраняется как есть |
| Абзац с uncial-passage в конце, runt из 4–5 uncial-букв | да | отказ B (если уперлась в uncial) | да (лимит 65 px) | uncial-фрагмент выступает целиком в outer-padding |
| Параграф `.theological` | да* | нет | нет | runt сохраняется (политика «не трогать») |

*— `markLastWords` не делает дополнительной фильтрации по `.theological`. Можно добавить, если хочется идеологической чистоты, но безвредно.

## IV.4. Что меняется в пагинаторе

Ничего. Пагинатор работает с уже подготовленными блоками (фазы 0 + 0.5). Все runt-prevention изменения зафиксированы в DOM template'а **до** того, как `paginate` начинает измерять блоки.

## IV.5. Производительность

- A — один TreeWalker на абзац, O(n) по числу абзацев. Десятки ms на полный кодекс.
- B/C (через `preventRunts`) — два-три forced reflow на runt-кандидат (один на `analyzeRunt`, один на B-перемер, опционально один на C-перемер). Для абзаца без runt'а — один reflow на `analyzeRunt`, потом сразу выход.
- `getRuntHangLimit` добавляет один `getComputedStyle` на каждый успешный runt — это дёшево (computed style кэшируется браузером).
- `markFoliosWithRuntHang` — один проход по `.folio-content`, O(n_pages). Бесплатно.

Итого на сотне абзацев в кодексе — суммарно сотни ms на фазу 0.5, не критично.

---

# Часть V — Сводный diff

| Файл / место | Действие | Размер |
|---|---|---|
| `<style>` после секции jitter (~стр. 1521) | добавить блок `RUNT-HANG` CSS (два правила: `.runt-hang` и `.folio-content.has-runt-hang-inside`) | ~30 строк |
| `<script>` после `walkWrapLongWords` (~стр. 8650) | добавить `markLastWords`, `isLastwordRelevant`, `LASTWORD_MIN_LEN` | ~60 строк |
| `<script>` после `paginate` (~стр. 6190) | добавить `analyzeRunt` + константы `RUNT_MAX_LINE_*`, `applyRuntHang`, `compressPenultimateLine`, `findRuntTailRange`, `findProbeElementForRange`, `getRuntHangLimit`, `unwrapElement`, `countVisualLines`, `preventRunts`, `markFoliosWithRuntHang`, шрифт-адаптивные константы | ~375 строк |
| `<script>` `walkJitter` (~стр. 7714) | в classList-проверке добавить `lastword-no-wbr` и `runt-hang` | +2 строки |
| `<script>` `walkWbrOnly` (~стр. 8480) | в classList-проверке добавить `lastword-no-wbr` и `runt-hang` | +2 строки |
| `<script>` `walkWrapLongWords` (~стр. 8650) | в classList-проверке добавить `lastword-no-wbr` и `runt-hang` | +2 строки |
| `<script>` `preprocessSourceTemplate` (~стр. 8800) | вставить `markLastWords(root)` **до** `markNoTorn` | +2 строки |
| `<script>` `run()` (~стр. 9794) | добавить блок Фазы 0.5 (`preventRunts` + логирование) и `markFoliosWithRuntHang()` после `renderBook` | +15 строк |
| (При патче KELLS-NOTORN) `KELLS_NOTORN_SKIP_DESC_CLASSES` | добавить `lastword-no-wbr` и `runt-hang` | +2 строки |

**Итого:** ~485 строк добавлений, ~8 строк точечных правок существующего кода. Атомарный коммит, простой откат.

---

# Часть VI — Шрифтонезависимость и калибровка

Эта секция описывает, какие части спецификации зависят от шрифта, и куда смотреть при добавлении нового.

## VI.1. Метрики используемых шрифтов

| Шрифт | Контекст использования (CSS-классы) | Mean lc width (weighted) | font-size в `.p` | px на букву |
|---|---|---|---|---|
| **0800 Kells** | основной текст `<p>`, маргиналии Cellach | 0.635em | 0.86em → 13.76 px | **~8.7 px** |
| **0550 Uncialis** | `.uncial-passage`, `.rubric`, `.doc-title`, `.doc-subtitle`, `.illuminated-initial` | 0.92em | 0.86em → 13.76 px | **~12.6 px** |
| **0800 Remedius** | `.mg-coemanus`, `.colophon`, `.later-hand-colophon` | ~0.70em (оценка) | 0.68em → 10.88 px (mg-coemanus), 0.92em → 14.72 px (colophon) | ~7.6 / 10.3 px |
| **0746 Beda** | `.marginalia` (умолчательный) | ~0.65em (оценка) | разный, обычно 0.68em → ~10.88 px | ~7.1 px |

Для Remedius и Beda реальных woff2-файлов в распоряжении не было — оценки даны из общих характеристик инсулярного типа письма. При получении файлов — пересчитать через `fontTools` (см. VI.4).

## VI.2. Шрифтонезависимые части

| Компонент | Почему независим |
|---|---|
| `analyzeRunt` через `getClientRects()` | Меряет физические пиксели DOM. Признак runt — *относительная* метрика (< 25% от полной ширины), не привязана к ширине букв. |
| `compressPenultimateLine` | Работает с `.ws` спанами, существующими в любом шрифтовом контексте, где walkJitter/walkWbrOnly создаёт их (т.е. везде, кроме uncial-passage). Сжатие `--w` — пропорциональное к текущему значению. |
| `applyRuntHang` (CSS) | `margin-right: -X` работает идентично на любом шрифте — это property layout-движка, не шрифтового шейпера. |
| `markLastWords` (`LASTWORD_MIN_LEN = 4`) | Это количество букв, а не пикселей. Работает корректно для любого шрифта. |
| `findRuntTailRange` | Использует DOM-обходчики и `Range`. Шрифт безразличен. |

## VI.3. Шрифтозависимые части

| Компонент | Где зависимость | Как откалибровано |
|---|---|---|
| `RUNT_HANG_LIMIT_*` константы | px-лимит выступа = ширина_буквы × ~5 букв | Kells: 50; Uncialis: 65; Remedius: 50; Beda: 45; default: 50 |
| `getRuntHangLimit` mapping | Сопоставление computed font-family с лимитом | По substring-match: `'uncialis'`, `'remedius'`, `'beda'`, `'kells'` |

## VI.4. Как добавить новый шрифт

Если в проекте появляется новый шрифт (например, `0500 Wearmouth-Jarrow` для гипотетических scriptio continua пассажей):

1. Через `fontTools` извлечь `mean lc width` × `unitsPerEm`. Пример Python:
   ```python
   from fontTools.ttLib import TTFont
   import statistics
   font = TTFont("0500-Wearmouth.woff2")
   hmtx = font["hmtx"]
   cmap = font.getBestCmap()
   freq = {'e':12,'i':10,'a':8,'u':7,'t':7,'s':6,'n':6,'r':6,'o':6,'m':5,
           'l':5,'c':4,'d':4,'p':3,'b':2,'q':2,'g':2,'v':2,'f':2,'h':1,'x':1}
   ws, wt = 0, 0
   for ch, f in freq.items():
       g = cmap.get(ord(ch))
       if g and g in hmtx.metrics:
           ws += hmtx.metrics[g][0] * f
           wt += f
   mean_em = ws / wt / font["head"].unitsPerEm
   print(f"weighted mean lc width: {mean_em:.3f}em")
   ```
2. Рассчитать pixel-лимит: `(mean_lc_em × font_size_em × base_px) × 5`.
3. Добавить константу `RUNT_HANG_LIMIT_WEARMOUTH = NNN;`
4. В `getRuntHangLimit` добавить ветку:
   ```js
   if (fam.indexOf('wearmouth') !== -1) {
     tail.fontHint = 'wearmouth';
     return RUNT_HANG_LIMIT_WEARMOUTH;
   }
   ```
5. Проверить логи в консоли — после первого рендера убедиться, что `[runt-hang]` сообщения с `fontHint: 'unknown:...'` исчезли.

## VI.5. Поведение при отсутствии шрифта в mapping

`getRuntHangLimit` возвращает `RUNT_HANG_LIMIT_DEFAULT = 50` и записывает `tail.fontHint = 'unknown:<font-family>'`. В консоли при отказе через `> limit` выводится этот hint — это даёт сигнал, что нужно добавить новую ветку. Стратегия C продолжит работать, просто с консервативным лимитом — это безопасный fallback.

---

# Часть VII — Совместимость с патчем KELLS-NOTORN

Пользовательский патч `KELLS-NOTORN` (отдельная задача, применён к коду) обёртывает все `t.` и `t:` в `<span class="no-torn">` с CSS `font-feature-settings: "liga" off, "dlig" on`, затем после рендера снимает класс с финальных `t.` в каждом `<p>` через `clearNoTornAtEnds`. Это даёт декоративный `t.orn` только в конце абзаца.

Спецификация совместима с этим патчем при условии трёх правок:

## VII.1. Порядок фаз

`markLastWords` **должна** идти ДО `markNoTorn` в `preprocessSourceTemplate`. Если порядок обратный, `markNoTorn` сначала расщепит финальное слово абзаца:

```
"praedicaverunt." → "praedicaverun" + <span class="no-torn">t.</span>
```

а `markLastWords` затем найдёт через TreeWalker последний text-node с буквами — это `"t."` внутри `no-torn`-обёртки. Regex `[A-Za-zÀ-ÿĀ-ſ]+$` извлечёт `"t"` — 1 букву, что меньше `LASTWORD_MIN_LEN = 4`. Слово будет пропущено, и стратегия A не сработает для этого абзаца. `walkWrapLongWords` зайдёт в text-node `"praedicaverun"` и наставит `<wbr>` между слогами — что и было исходной проблемой.

При правильном порядке (`markLastWords` → `markNoTorn`) `markLastWords` видит исходный целостный text-node `"...praedicaverunt."` и оборачивает `praedicaverunt` в `lastword-no-wbr`. Затем `markNoTorn` обходит дерево; если `lastword-no-wbr` есть в его skip-листе (см. VII.2), он не заходит внутрь, и `t.` в финальном слове остаётся без `no-torn` обёртки — там лигатура `t.orn` потенциально сработает.

## VII.2. Skip-листы

В `KELLS_NOTORN_SKIP_DESC_CLASSES` (объект, определённый в патче KELLS-NOTORN) добавить два класса:

```js
const KELLS_NOTORN_SKIP_DESC_CLASSES = {
  // ... существующие классы из патча ...
  'lastword-no-wbr': 1,    // ← НОВОЕ: стратегия A
  'runt-hang': 1,          // ← НОВОЕ: стратегия C
};
```

**Зачем `lastword-no-wbr`:** чтобы `markNoTorn` не заходил внутрь и не расщеплял финальное слово. После `clearNoTornAtEnds` финальный `t.` в этом абзаце остаётся неприкосновенным для шейпера — `t.orn` срабатывает на нём (декоративный завиток виден).

**Зачем `runt-hang`:** на момент создания runt-hang (фаза 0.5) `markNoTorn` уже отработал. Прямого эффекта добавление в skip нет. Но если в будущей итерации `markNoTorn` будет повторно вызываться при resize или ином пересчёте — skip-лист защитит от дублирования обёрток внутри runt-hang. Это дёшево и предусмотрительно.

## VII.3. Поведение `clearNoTornAtEnds` с обёртками A и C

Функция `isLastContentLeaf(sp, p)` поднимается через всех parent'ов от `sp` до `<p>`, проверяя `nextSibling` на каждом уровне. Это **корректно работает** с любой вложенностью обёрток:

```html
<p>
  ...
  <span class="runt-hang">
    <span class="lastword-no-wbr">
      praedicaverun<span class="no-torn">t.</span>
    </span>
  </span>
</p>
```

Если этот `<span class="no-torn">` — последний content leaf в `<p>` (все siblings вверх до `<p>` пусты или whitespace), `isLastContentLeaf` возвращает `true`, класс снимается. `t.orn` активируется.

Если за этим `no-torn` есть ещё что-то значащее в `<p>` (например, иллюминированный ornament-line после абзаца, что бывает редко), `isLastContentLeaf` вернёт `false`, класс останется. `t.orn` не сработает. Это корректно — мы хотели декоративный завиток ТОЛЬКО на абсолютном финале абзаца.

## VII.4. Walk-функции и `no-torn`

Не обязательно, но **рекомендуется** добавить `no-torn` в skip-листы walk-функций (`walkWbrOnly`, `walkWrapLongWords`, `walkJitter`) — наряду с `lastword-no-wbr` и `runt-hang`. Технически text-node `"t."` слишком короткий для walk-обработки (вряд ли длинное слово), но это страховка от любых edge cases:

```js
if (el.classList && (
    el.classList.contains('liga-protect') ||
    el.classList.contains('lastword-no-wbr') ||
    el.classList.contains('runt-hang') ||
    el.classList.contains('no-torn') ||         // ← рекомендуется
    ...
)) return;
```

## VII.5. Замечание про `--ws-p-target`

В патче KELLS-NOTORN также изменён `--ws-p-target: 0.12em → 0.18em` (это смежное, но не тематически связанное изменение). Эффект на runt-prevention: средний межсловный gap расширяется с 0.12em до 0.18em, что **слегка увеличивает** вероятность runt'ов (больше места уходит на пробелы). Это не ломает работу A/B/C, но повышает частоту срабатывания B и C. Если планируется снизить `--space-amp-base` (см. Часть VIII), стоит делать это совместно — тогда mean = 0.18em сохраняется, но дисперсия уменьшается.

---

# Часть VIII — Что вне scope

- **Снижение `--space-amp-base`** с 0.60em до 0.20em — отдельная одно-строчная правка (предыдущая итерация анализа). Снизит частоту срабатывания B/C в разы при сохранении нынешнего `--ws-p-target = 0.18em`.
- **Аналогичная обработка `.marginalia`** — runt'ы в маргиналиях частые и эстетически приемлемы (узкая колонка → ragged endings — норма). Если захочется лечить, стратегия A применима без изменений; B/C — нет (узкая колонка не оставляет места ни для сжатия, ни для выступа).
- **Валидация runt-hang против положений маргиналий** после `positionMarginalia`. Описана в Edge cases C, отдельная фаза.
- **Пересчёт `--runt-hang-x` в em вместо px** — потенциально лучше для масштабирования, но текущая пиксельная схема работает корректно в пределах одного breakpoint'а.
- **Точные метрики Remedius и Beda** через `fontTools`. Сейчас лимиты для этих шрифтов взяты по оценке. При получении woff2-файлов — пересчитать.
- **Переразметка шрифта Kells для отключения отдельных GSUB-правил** (например, `t.orn` навсегда) — отдельная задача, требует fontTools-патчинга woff2. Альтернатива пользовательскому патчу KELLS-NOTORN, но более радикальная.
