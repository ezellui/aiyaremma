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

**Что меняется относительно предыдущей версии спеки** (где была только C): отрицательный `margin-right` переведён с `<p>` на сам `<span class="runt-hang">`. Это **точечный** эффект: только runt-строка получает дополнительную ширину для wrap-decision, остальные строки абзаца не затронуты. См. часть III.

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

В `preprocessSourceTemplate` (~строка 8800), после `applyAbbreviations` / `decorateTituli`, **до** обработки маргиналий и до walkWrapLongWords:

```js
  applyAbbreviations(root);
  decorateTituli(root);
  addAbbrTranslateSources(root);

  // Стратегия A: пометить последнее слово каждого абзаца, чтобы
  // walkWrapLongWords не вставил <wbr> внутри. Делается ДО
  // walkWrapLongWords, чтобы skip-лист сработал на готовых обёртках.
  markLastWords(root);

  // ... далее splitMarginaliaForTranslate, walkWbrOnly, walkJitter,
  // walkWrapLongWords — все они учитывают новый класс через skip-листы.
```

## A.6. Edge cases стратегии A

- **Короткие абзацы (одно слово).** Слово оборачивается, но толку нет — там и так нет переноса. Безвредно.
- **Параграф заканчивается формулой** типа `Amen.` — `Amen` < `LASTWORD_MIN_LEN` (4 буквы), не оборачивается. Это намеренно: для коротких слов и так нет `<wbr>`.
- **Параграф заканчивается составной обёрткой**, например на `<em class="uncial-passage">`. TreeWalker дойдёт до text-node-а внутри `<em>`, оборачивание сработает — span появится внутри `<em>`. Это безопасно: stilе унаследуется через каскад, лигатуры внутри одной буквенной последовательности не страдают (внутри обёртки полное слово).
- **Параграф с `<abbr>` на конце**, например `Amen` — никаких `<wbr>` в `<abbr>` и так нет, ничего не оборачивается дополнительно. Безвредно.

---

# Часть II — Стратегия B: сжатие пробелов предпоследней строки

## B.1. Идея

Когда абзац всё-таки получил runt (даже после стратегии A) и runt маленький — обычно достаточно сжать несколько пробелов на предпоследней строке, чтобы runt-слово влезло. `.ws` спаны имеют `padding-right: calc(var(--w) * var(--space-amp))`. Если переписать `--w` у спанов предпоследней строки в сторону минимума, padding обнулится, ширина строки уменьшится, runt-слово получит шанс поместиться.

В отличие от стратегии C, это **полностью невидимое** изменение — пробелы и так дрожат от 0 до `--space-amp`, занижение `--w` до минимальных значений не выходит за пределы естественной вариативности.

## B.2. CSS

Никакого. Изменения в DOM — переписывание inline-style `--w` на существующих `.ws` спанах.

## B.3. JS — функция `compressPenultimateLine`

Вставляется в `<script>` рядом с другими runt-функциями (~строка 6190, после `paginate`):

```js
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
  // p должен быть в measurerContent (или элементе с layout'ом).
  // Найдём все .ws на предпоследней строке.
  const allWs = p.querySelectorAll('.ws');
  if (allWs.length < COMPRESS_MIN_WS) return false;

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

  if (candidates.length < COMPRESS_MIN_WS) return false;

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

  if (lineCountAfter < runt.lineCount) {
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
- **Идемпотентность.** `data-w0` сохраняется на спане при первой компрессии. При повторном вызове compressPenultimateLine увидит сохранённое значение и не перепишет его заново. При откате `data-w0` удаляется. Безопасно для повторных вызовов в пределах одной сессии.
- **Resize.** При resize фаза 0.5 не перезапускается (см. в общем разделе про идемпотентность). Сохранённые `--w` остаются в их сжатом состоянии. Это нормально — абзац всё так же не должен породить runt в новом размере, если он не породил в исходном (resize меняет только маргиналии, не основную ширину).

---

# Часть III — Стратегия C: runt-hang (точечная — исправленная версия)

## C.1. Что было исправлено

В предыдущей итерации этой спеки `margin-right: -X` применялся к `<p class="has-runt-hang">`. Это работало для visual эффекта (только runt-строка выступала из-за `text-align: left`), но влияло на line-break decision **во всех строках абзаца** — другая строка, до этого заканчивавшаяся почти у правого края, могла бы прихватить лишнее слово, породив новый runt.

**Точечное решение**: перенос отрицательного `margin-right` с `<p>` на сам `<span class="runt-hang">`. Inline-margin влияет только на outer-edge **этого** inline-box'а; wrap-decisions других inline-box'ов в абзаце не затрагиваются. Это даёт ровно то поведение, которое нужно: эффект только на runt-строке.

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

## C.3. JS — функция `applyRuntHang` (исправленная)

Главное отличие от предыдущей версии: обёртка `<span class="runt-hang">` **всегда охватывает всё содержимое от начала runt-слова до конца блока** (включая хвостовую пунктуацию). Это гарантирует, что после runt-hang в `<p>` ничего нет — и negative `margin-right` ни на что не «налезает» визуально.

```js
// ═══════════════════════════════════════════════════════════════
// Стратегия C: оборачивает runt-target в <span class="runt-hang">
// и задаёт ему --runt-hang-x для negative margin-right.
//
// ВАЖНО: обёртка всегда расширяется ДО КОНЦА блока, чтобы:
//   (а) margin-right на span'е не сдвигал visible-контент после
//       runt'а влево (его попросту нет — точка/пунктуация уже в
//       обёртке);
//   (б) visual выступ был непрерывным, без артефактов «висящей»
//       точки за пределами обёртки.
//
// Возвращает true при успехе, false при отказе.
// ═══════════════════════════════════════════════════════════════

const HARD_MAX_HANG_PX = 45;   // повышено с 30 до 45 на основании
                                // ширины букв Kells: ~8.7 px/буква,
                                // 4-буквенный хвост = ~35 px.
const HANG_SAFETY_PX = 4;

function applyRuntHang(p, runt, measurerContent) {
  const xPx = Math.round(runt.lastLineWidth + HANG_SAFETY_PX);
  if (xPx > HARD_MAX_HANG_PX) return false;

  // Найти DOM-range от начала runt-слова до конца <p>.
  const tail = findRuntTailRange(p);
  if (!tail) return false;

  // Обернуть range в <span class="runt-hang">.
  const span = document.createElement('span');
  span.className = 'runt-hang';
  span.style.setProperty('--runt-hang-x', xPx + 'px');

  try {
    // Range.surroundContents работает только если range не пересекает
    // границ узлов наполовину. Если пересекает — fallback на extract
    // + append.
    tail.range.surroundContents(span);
  } catch (e) {
    // Fallback: extract → wrap → reinsert.
    const fragment = tail.range.extractContents();
    span.appendChild(fragment);
    tail.range.insertNode(span);
  }

  // Перемерим (p всё ещё в measurer'е).
  const newLineCount = countVisualLines(p);

  if (newLineCount >= runt.lineCount) {
    // Откат: развернуть span.
    unwrapElement(span);
    return false;
  }

  return true;
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

  // Если text-node — единственный значащий ребёнок прозрачной
  // обёртки (.word-wbr / .liga-protect), стартуем РАНЬШЕ — от
  // начала самой обёртки, чтобы runt-hang охватывал обёртку
  // целиком (нужно для случая <span class="word-wbr"><span
  // class="word-source">...</span><span class="word-render">...
  // </span></span>: оба внутренних подспана пройдут в обёртку
  // как один атом).
  let startNode = tn;
  let startOff = startOffset;
  let parent = tn.parentNode;
  if (parent && parent.classList) {
    if (parent.classList.contains('word-render') ||
        parent.classList.contains('word-source')) {
      // Поднимаемся до .word-wbr
      const wordWbr = parent.parentNode;
      if (wordWbr && wordWbr.classList &&
          wordWbr.classList.contains('word-wbr')) {
        // Стартуем перед всем .word-wbr
        startNode = wordWbr.parentNode;
        startOff = Array.prototype.indexOf.call(
          wordWbr.parentNode.childNodes, wordWbr);
      }
    } else if (parent.classList.contains('lastword-no-wbr')) {
      // Стартуем перед обёрткой стратегии A.
      startNode = parent.parentNode;
      startOff = Array.prototype.indexOf.call(
        parent.parentNode.childNodes, parent);
    }
  }

  // Конец range = после последнего ребёнка p.
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

## C.4. Что изменилось в `applyRuntHang` концептуально

| Версия | Где `margin-right: -X` | Где `--runt-hang-x` | Что в `<p>` после применения |
|---|---|---|---|
| **Старая** | на `<p class="has-runt-hang">` | в style `<p>` | `<p>...<span class="runt-hang">word</span>.</p>` (точка снаружи span'а) |
| **Новая** | на `<span class="runt-hang">` | в style span'а | `<p>...<span class="runt-hang">word.</span></p>` (точка внутри span'а; ничего после) |

В новой версии span runt-hang всегда последний в `<p>`. Negative margin ни на что после не давит, ничего за span'ом не сдвигается влево.

## C.5. Edge cases стратегии C

Большая часть совпадает с предыдущей версией, дополнительно:

- **Содержимое после runt-слова не помещается в span целиком.** Может случиться, если в `<p>` есть необычная структура — например, иллюминированный ornament-line после слова. Тогда `range.surroundContents` бросит ошибку (range cross-boundary). Fallback через `extractContents` + `insertNode` справится с большинством случаев, но decoratives внутри лучше обходить — в `findRuntTailRange` стоит проверить, нет ли блочных элементов между runt-словом и концом `<p>`, и в случае их обнаружения вернуть `null`.
- **Translate-режим.** Когда runt-hang обёртка лежит вокруг `.word-wbr` (двойного source/render), `findRuntTailRange` поднимается до самого `.word-wbr` через ветку `word-render`/`word-source`, и span охватывает оба внутренних слоя. В translate-режиме `.word-render` скрыт, виден `.word-source` — но и для него `margin-right: -X` работает (margin наследуется на тот же span). Поведение симметрично, выступание корректное.
- **Коллизия с маргиналией в outer-padding.** Эта же проблема, что и раньше — выступ может зайти на территорию маргиналии. Не лечится в рамках этой спеки (нужна post-render validation после `positionMarginalia`).

---

# Часть IV — Композиция: как стратегии работают вместе

## IV.1. Изменения в `preventRunts`

Объединённая функция фазы 0.5 теперь применяет B и C каскадно для каждого `<p>` с runt'ом:

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
  preprocessSourceTemplate();   // существующее, изнутри теперь
                                // вызывает markLastWords (см. ниже)

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

Внутри `preprocessSourceTemplate` (стр. ~8800) вставка `markLastWords` встаёт сразу после `applyAbbreviations` / `decorateTituli` / `addAbbrTranslateSources`:

```js
function preprocessSourceTemplate() {
  // ... шаги 1, 1.5 (br → пробел, trim в маргиналиях)

  applyAbbreviations(root);
  decorateTituli(root);
  addAbbrTranslateSources(root);

  // Стратегия A: пометить последнее слово каждого основного <p>.
  // ДОЛЖНО быть здесь — до splitMarginaliaForTranslate / walkWbrOnly /
  // walkJitter / walkWrapLongWords. Эти три воспользуются skip-листом
  // через .lastword-no-wbr.
  markLastWords(root);

  // ... шаги 4, 5, 6 (split, wbr, jitter, wrapLongWords)
}
```

## IV.3. Логика взаимодействия

| Сценарий | A применилась? | B попробовалась? | C попробовалась? | Итог |
|---|---|---|---|---|
| Длинный абзац без runt'а | да (бесплатно) | нет (нет runt'а) | нет | абзац без `<wbr>` в последнем слове, runt и не возник |
| Абзац с runt'ом из целого слова, runt узкий | да | да, успех | нет | пробелы сжаты, слово вернулось — невидимо |
| Абзац с runt'ом, узким, но сжатие не помогло | да | пробовалась, отказ | да, успех | runt-слово выступает за край |
| Абзац с runt'ом из крупного слова (> 45 px) | да | возможен отказ B | отказ C (HARD_MAX) | runt сохраняется как есть |
| Параграф `.theological` | да* | нет | нет | runt сохраняется (политика «не трогать») |

*— `markLastWords` не делает дополнительной фильтрации по `.theological`. Можно добавить, если хочется идеологической чистоты, но безвредно.

## IV.4. Что меняется в пагинаторе

Ничего. Пагинатор работает с уже подготовленными блоками (фазы 0 + 0.5). Все runt-prevention изменения зафиксированы в DOM template'а **до** того, как `paginate` начинает измерять блоки.

## IV.5. Производительность

- A — один TreeWalker на абзац, O(n) по числу абзацев. Десятки ms на полный кодекс.
- B/C (через `preventRunts`) — два-три forced reflow на runt-кандидат (один на `analyzeRunt`, один на B-перемер, опционально один на C-перемер). Для абзаца без runt'а — один reflow на `analyzeRunt`, потом сразу выход. На сотне абзацев в кодексе — суммарно сотни ms, не критично, но измеримо.
- `markFoliosWithRuntHang` — один проход по `.folio-content`, O(n_pages). Бесплатно.

---

# Часть V — Сводный diff

| Файл / место | Действие | Размер |
|---|---|---|
| `<style>` после секции jitter (~стр. 1521) | добавить блок `RUNT-HANG` CSS (только два правила: `.runt-hang` и `.folio-content.has-runt-hang-inside`) | ~30 строк |
| `<script>` после `walkWrapLongWords` (~стр. 8650) | добавить `markLastWords`, `isLastwordRelevant`, `LASTWORD_MIN_LEN` | ~60 строк |
| `<script>` после `paginate` (~стр. 6190) | добавить `analyzeRunt`, `applyRuntHang`, `compressPenultimateLine`, `findRuntTailRange`, `unwrapElement`, `countVisualLines`, `preventRunts`, `markFoliosWithRuntHang` | ~250 строк |
| `<script>` `walkJitter` (~стр. 7714) | в classList-проверке добавить `lastword-no-wbr` и `runt-hang` | +2 строки |
| `<script>` `walkWbrOnly` (~стр. 8480) | в classList-проверке добавить `lastword-no-wbr` и `runt-hang` | +2 строки |
| `<script>` `walkWrapLongWords` (~стр. 8650) | в classList-проверке добавить `lastword-no-wbr` и `runt-hang` | +2 строки |
| `<script>` `preprocessSourceTemplate` (~стр. 8800) | вставить `markLastWords(root)` | +2 строки |
| `<script>` `run()` (~стр. 9794) | добавить блок Фазы 0.5 (`preventRunts` + логирование) и `markFoliosWithRuntHang()` после `renderBook` | +15 строк |

**Итого:** ~365 строк добавлений, ~6 строк точечных правок существующего кода. Атомарный коммит, простой откат.

---

# Часть VI — Что вне scope

- **Снижение `--space-amp-base`** с 0.60em до 0.20em — отдельная одно-строчная правка (предыдущая итерация анализа). Должна применяться независимо. Снизит частоту срабатывания B/C в разы.
- **Аналогичная обработка `.marginalia`** — runt'ы в маргиналиях частые и эстетически приемлемы (узкая колонка → ragged endings — норма). Если захочется лечить, стратегия A применима без изменений; B/C — нет (узкая колонка не оставляет места ни для сжатия, ни для выступа).
- **Валидация runt-hang против положений маргиналий** после `positionMarginalia`. Описана в Edge cases C, отдельная фаза.
- **Пересчёт `--runt-hang-x` в em вместо px** — потенциально лучше для масштабирования, но текущая пиксельная схема работает корректно в пределах одного breakpoint'а.
- **Переразметка шрифта Kells для отключения отдельных GSUB-правил** (например, `t.orn` или `et→&`) — отдельная задача, требует fontTools-патчинга woff2.
