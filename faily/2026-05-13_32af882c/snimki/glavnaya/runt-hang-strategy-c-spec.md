# Стратегия C: runt-hang за правое поле — спецификация имплементации

**Файл:** `relatio_aidani_codex_patched.html`
**Цель:** избежать роста абзаца на 1 строку из-за переноса последнего слова (или его слогового хвоста), позволив этому слову слегка выступить за правую границу `folio-content` в палеографически аутентичной манере.
**Сложность:** ~200 строк JS, ~25 строк CSS, два небольших правки в `run()`.

---

## 0. Краткое описание

Между фазой 0 (`preprocessSourceTemplate`) и фазой 1 (`paginate`) добавляется новая фаза **0.5 — `preventRunts`**. Она:

1. Создаёт временный измеритель (использует тот же `measurer`, что и пагинатор).
2. Для каждого `<p>` в template'е проверяет, образуется ли *runt* — последняя строка, занимающая менее ~25% от ширины колонки или менее ~60 px абсолютно.
3. Если runt найден — находит последнее значащее «слово» (с учётом обёрток `.word-wbr`, `.liga-protect` и хвостовой пунктуации), оборачивает его в `<span class="runt-hang">` и навешивает `<p>` класс `has-runt-hang` с CSS-переменной `--runt-hang-x`, равной требуемому выступу в пикселях.
4. **Проверяет**, помог ли фикс (перемеряет): если число строк не уменьшилось — откатывает обёртку и класс.
5. Помечает родительский `.folio-content` классом `has-runt-hang-inside` уже после рендера (в `renderBook`), чтобы локально снять `overflow: hidden` для этих фолио.

В итоге пагинация в фазе 1 видит уже сжатые абзацы; страница помещает их без переноса вниз; визуально хвост слова торчит на 8–25 px в зону `--folio-pad-outer`.

---

## 1. Принцип работы (зачем `margin-right: -Xpx` на `<p>` работает)

CSS-механика, на которой держится фикс:

```css
p.has-runt-hang {
  margin-right: calc(0px - var(--runt-hang-x, 0px));
  overflow: visible;
}
```

Отрицательный `margin-right` на блочном элементе **расширяет его эффективную content-width** на величину `X`. Браузер при выборе точек переноса видит line-box на `X` пикселей шире, и слово, которое раньше не вмещалось — теперь вмещается на предпоследнюю строку. Последняя «runt»-строка исчезает.

Поскольку у `<p>` стоит `text-align: left` (ragged-right), визуально это видно только на той строке, которой действительно не хватало места — все остальные строки заканчиваются раньше и выступа не дают. То есть в большинстве абзацев никакого «торчания» не происходит — оно проявляется ровно в том месте, где раньше был перенос.

Если у `.folio-content` стоит `overflow: hidden`, выступ всё-таки срежется. Поэтому фикс комплексный — он включает локальное снятие `overflow` для соответствующих фолио (вторая часть CSS-патча).

---

## 2. Архитектурное место

Цепочка фаз в `run()`:

```
preprocessSourceTemplate()         ← walkJitter, walkWbrOnly, applyAbbreviations etc.
const measurer = createMeasurer()
const blocks = [...]
preventRunts(blocks, measurerContent)   ← НОВАЯ ФАЗА 0.5
const pages = paginate(blocks, measurerContent, lineHeight)
renderBook(pages)
markFoliosWithRuntHang()           ← НОВЫЙ ВЫЗОВ
addInitialGround / addInkArtifacts ...
positionMarginalia()
```

Порядок важен. `preventRunts` **должен** идти после `preprocessSourceTemplate` (нужны уже расставленные `.ws` спаны и `.word-wbr` обёртки) и **до** `paginate` (чтобы пагинация увидела изменённый layout).

`markFoliosWithRuntHang` идёт после `renderBook` — на этом этапе появляется реальный DOM `.folio` / `.folio-content`, в который надо поставить флаг.

---

## 3. CSS-патч

### 3.1. Куда вставлять

В блоке `<style>` после секции `/* ВЫКЛЮЧАТЕЛЬ ПРОБЕЛЬНОГО ДЖИТТЕРА */` (примерно после строки 1521, перед началом секции с буквенным джиттером). Логически это продолжение темы «коррекций пробельного джиттера».

### 3.2. Код

```css
  /* ═══════════════════════════════════════════════════════════════
     RUNT-HANG — выступание последнего слова абзаца за правое поле.

     Палеографически аутентичный приём: в инсулярных кодексах писец
     регулярно позволял последнему слову строки слегка торчать за
     bounding line, если этим избегался перенос по слогам и образо-
     вание короткой «сиротской» последней строки.

     Применяется через JS-фазу preventRunts (см. секцию скриптов):
       - <p> с runt-кандидатом получает класс has-runt-hang и
         CSS-переменную --runt-hang-x (в пикселях, положительная);
       - последнее значащее слово оборачивается в .runt-hang;
       - .folio-content фолио получает класс has-runt-hang-inside,
         локально снимающий overflow:hidden.

     Слово выступает в зону --folio-pad-outer (= 82 px), что заведомо
     больше типичного выступа (8-25 px). Глобальный overflow:hidden
     у .folio остаётся — сама страница ничего лишнего не показывает.

     Если хвостовое слово реально не помещается с выступом <= 30 px
     (HARD_MAX_HANG_PX в JS), фикс не применяется — runt остаётся как
     есть.                                                          */
  p.has-runt-hang {
    /* Расширяем content-box параграфа влево: layout получает
       дополнительные --runt-hang-x пикселей. На строках, не дости-
       гающих правого края, эффект незаметен; на проблемной — слово
       помещается без переноса. */
    margin-right: calc(0px - var(--runt-hang-x, 0px));
    /* Подстраховка: внутри <p> overflow:visible (это значение по
       умолчанию, но явно). */
    overflow: visible;
  }

  /* Само хвостовое слово. Класс служит маркером для:
       - тестов / DevTools (легко найти все защищённые runt'ы);
       - блокировки <wbr>-разрезов внутри слова (white-space:nowrap).
     Визуально стиль не несёт — выступание создаётся через margin
     родительского <p>. */
  .runt-hang {
    white-space: nowrap;
  }

  /* Локальное снятие overflow:hidden у .folio-content. Применяется
     только к фолио, на которых JS обнаружил хотя бы один runt-hang.
     Глобально overflow остаётся на .folio (и на .folio-content
     остальных фолио) — чтобы dropcap'ы, иллюминированные инициалы
     и прочие decorations не «утекали» за пределы страницы. */
  .folio-content.has-runt-hang-inside {
    overflow: visible;
  }
```

### 3.3. Совместимость

- `calc(0px - var(...))` — стандартный синтаксис, работает везде.
- `margin-right: -Xpx` на `<p>` — стандартное поведение CSS 2.1, кросс-браузерно.
- Класс `has-runt-hang-inside` ставится JS-ом, `:has()` не используется (сознательно, для совместимости со старыми Safari).

---

## 4. JS-патч: новые функции

### 4.1. Куда вставлять

Все четыре функции (`findLastWordTarget`, `analyzeRunt`, `applyRuntHang`, `preventRunts`) добавляются в `<script>` **между** определением `paginate` (заканчивается около строки 6190) и определением `makeFolio` (начинается там же ниже). Логически они — соседи пагинатора, оперируют через тот же measurer.

Функция `markFoliosWithRuntHang` ставится сразу после `renderBook` (~строка 6580; точное место см. в секции 5).

### 4.2. Утилита 1 — поиск runt-target

```js
// ═══════════════════════════════════════════════════════════════
// RUNT-HANG — Стратегия C.
//
// Идея: для абзацев, у которых последняя визуальная строка содержит
// один короткий хвост (целое слово или слог после <wbr>), позволить
// этому хвосту выступить за правое поле, чтобы он вернулся на
// предпоследнюю строку и абзац потерял лишнюю строку.
//
// Реализация — фаза preventRunts перед пагинацией: измеряем каждый
// <p> в measurer'е, обнаруживаем runt, применяем класс has-runt-hang
// + обёртку .runt-hang, перемеряем, при успехе фиксируем.
// ═══════════════════════════════════════════════════════════════

// Пунктуация и whitespace, которые не считаются «значащим словом».
// Соответствует тому, что не должно одиноко висеть на отдельной
// строке (точка после Amen — не runt, а сама точка не таргет).
const RUNT_NON_WORD_RE = /^[\s.,;:!?…—–\-«»""''()[\]{}/\\]+$/;

// Имена тегов, которые НЕ являются «словесными» обёртками и через
// которые мы можем «прозрачно» поднимать выбор runt-target в
// сторону предка (например, <em>, <span class="word-wbr">).
//
// Если конечный target оказывается внутри одной из таких обёрток,
// мы предпочитаем пометить классом runt-hang всю обёртку целиком —
// чтобы стили (nowrap) распространились на её содержимое
// единым атомом.
const RUNT_TRANSPARENT_WRAPPERS = {
  'WORD-WBR': 1,        // <span class="word-wbr">
  'LIGA-PROTECT': 1,    // защита лигатур
};

function isTransparentWrapper(el) {
  if (el.nodeType !== 1) return false;
  if (el.tagName === 'SPAN') {
    if (el.classList.contains('word-wbr')) return true;
    if (el.classList.contains('liga-protect')) return true;
  }
  return false;
}

// Находит «последнее значащее слово» в данном <p> и возвращает
// объект, описывающий, какой элемент/диапазон надо обернуть/пометить
// классом runt-hang.
//
// Стратегия поиска:
//   1. DFS по дереву <p> справа-налево.
//   2. Пропускаем whitespace-only text-nodes и нод-обёртки без
//      словесного содержимого.
//   3. Дойдя до text-node со словесными символами, определяем
//      span слова в нём (через regex: последняя последовательность
//      не-пробельных не-пунктуационных символов).
//   4. Если text-node — единственный ребёнок «прозрачной» обёртки
//      (.word-wbr), таргетом становится сама обёртка.
//   5. Возвращаем либо { kind: 'element', el }, либо
//      { kind: 'range', node, start, end } — то и другое
//      приёмлемо для applyRuntHang.
//
// Возвращает null, если ничего не найдено (пустой абзац, только
// пунктуация и т.п.).
function findLastWordTarget(p) {
  // Собираем все text-nodes в порядке DFS
  const textNodes = [];
  const walker = document.createTreeWalker(
    p,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );
  let n;
  while ((n = walker.nextNode())) textNodes.push(n);
  if (textNodes.length === 0) return null;

  // Идём с конца, пропускаем whitespace и pure-punctuation
  for (let i = textNodes.length - 1; i >= 0; i--) {
    const tn = textNodes[i];
    const v = tn.nodeValue;
    if (!v) continue;
    if (RUNT_NON_WORD_RE.test(v)) continue;

    // Найдён text-node со словесным содержимым.
    // Найти в нём начало последнего слова (последняя серия
    // словесных символов с конца).
    const m = v.match(/[A-Za-zÀ-ÿĀ-ſ]+[^\s]*$/);
    if (!m) continue;
    const start = v.length - m[0].length;
    const end = v.length;

    // Не выбираем хвостовую пунктуацию как часть слова — она
    // войдёт в обёртку естественным образом, потому что после
    // последнего text-node-а слова в <p> могут быть только
    // whitespace-only / punctuation-only text-nodes, и они уже
    // лежат справа от наших границ. Их в runt-обёртку **не**
    // включаем — пусть остаются вне (если есть).
    //
    // НО: если этот text-node содержит И слово, И пунктуацию
    // (типа "incarnatione."), берём ВСЁ оставшееся до конца
    // text-node-а. Это охватывает пунктуацию, прилипшую к слову.
    // Уже сделано: m[0] жадно тянется до конца через [^\s]*$.

    // Если text-node — единственный значащий ребёнок прозрачной
    // обёртки, лучше пометить саму обёртку. Поднимаемся.
    let target = tn;
    let p1 = tn.parentNode;
    // .word-wbr содержит word-source (visually-hidden) + word-render.
    // Это особый случай: словесная часть лежит в word-render, но
    // структурно надо помечать word-wbr (внешний span).
    if (p1 && p1.classList && p1.classList.contains('word-render')) {
      const grandP = p1.parentNode;
      if (grandP && grandP.classList && grandP.classList.contains('word-wbr')) {
        return { kind: 'element', el: grandP };
      }
    }
    // Если родитель — прозрачная обёртка и в ней нет других text-nodes
    // со словесным содержимым, помечаем обёртку.
    while (p1 && isTransparentWrapper(p1)) {
      if (hasOtherWordTextNodes(p1, tn)) break;
      target = p1;
      p1 = p1.parentNode;
    }

    if (target.nodeType === 1) {
      return { kind: 'element', el: target };
    }
    return { kind: 'range', node: tn, start: start, end: end };
  }

  return null;
}

// Вспомогательная: есть ли в поддереве `el` другие text-nodes,
// помимо `except`, в которых есть словесные символы?
function hasOtherWordTextNodes(el, except) {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
  let n;
  while ((n = walker.nextNode())) {
    if (n === except) continue;
    if (!n.nodeValue) continue;
    if (/[A-Za-zÀ-ÿĀ-ſ]/.test(n.nodeValue)) return true;
  }
  return false;
}
```

### 4.3. Утилита 2 — детектирование runt'а

```js
// Возвращает данные о runt'е или null.
//
// runt = объект { lineCount, lastLineWidth, penultLineWidth,
//                 lastLineY, penultLineY }.
//
// Критерии runt-кандидата (всё одновременно):
//   - lineCount >= 2 (одно-строчный абзац не runt по определению);
//   - lastLineWidth < RUNT_WIDTH_PX (~60 px) ИЛИ
//     lastLineWidth / penultLineWidth < 0.25;
//   - <p> не помечен no-runt-hang (флаг для исключений).
//
// p должен быть уже в DOM (в measurer'е) при вызове, иначе
// getClientRects() вернёт пустой массив.
const RUNT_MAX_LINE_WIDTH_PX = 60;
const RUNT_MAX_LINE_FRACTION = 0.25;

function analyzeRunt(p) {
  if (!p.isConnected) return null;
  if (p.classList && p.classList.contains('no-runt-hang')) return null;

  const range = document.createRange();
  range.selectNodeContents(p);
  const rawRects = range.getClientRects();
  range.detach && range.detach();

  // Фильтруем нулевые и группируем по Y (несколько rect'ов могут
  // лежать на одной визуальной строке, если параграф содержит
  // inline-элементы разной высоты).
  const byLine = [];
  for (let i = 0; i < rawRects.length; i++) {
    const r = rawRects[i];
    if (r.width === 0 || r.height === 0) continue;
    // Ищем существующую строку с близким Y
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

  // Сортируем по top (на всякий случай)
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
```

### 4.4. Утилита 3 — применение и проверка runt-hang

```js
// Жёсткие лимиты на выступ. Если требуемое расширение line-box
// превышает HARD_MAX_HANG_PX, фикс не применяется.
const HARD_MAX_HANG_PX = 30;
// Дополнительный запас сверх ширины runt-строки.
const HANG_SAFETY_PX = 4;

// Применяет фикс к p in-place. Возвращает true при успехе
// (runt после фикса исчез), false при отказе или откате.
//
// Параметры:
//   p — целевой <p> (тот же узел, что был в measurer'е).
//   runt — результат analyzeRunt(p) до применения фикса.
//   measurerContent — measurer для повторного измерения.
function applyRuntHang(p, runt, measurerContent) {
  const xPx = Math.round(runt.lastLineWidth + HANG_SAFETY_PX);

  if (xPx > HARD_MAX_HANG_PX) {
    // Слишком большой выступ — отказ.
    return false;
  }

  // Найти runt-target.
  const tgt = findLastWordTarget(p);
  if (!tgt) return false;

  // Применить обёртку/класс.
  let wrappedSpan = null;
  if (tgt.kind === 'element') {
    tgt.el.classList.add('runt-hang');
  } else {
    // kind === 'range' — оборачиваем диапазон в text-node-е.
    const node = tgt.node;
    const before = node.nodeValue.slice(0, tgt.start);
    const middle = node.nodeValue.slice(tgt.start, tgt.end);
    const after = node.nodeValue.slice(tgt.end);

    const span = document.createElement('span');
    span.className = 'runt-hang';
    span.appendChild(document.createTextNode(middle));

    const parent = node.parentNode;
    if (before.length > 0) {
      parent.insertBefore(document.createTextNode(before), node);
    }
    parent.insertBefore(span, node);
    if (after.length > 0) {
      parent.insertBefore(document.createTextNode(after), node);
    }
    parent.removeChild(node);
    wrappedSpan = span;
  }

  p.classList.add('has-runt-hang');
  p.style.setProperty('--runt-hang-x', xPx + 'px');

  // Перемеряем — действительно ли фикс уменьшил число строк?
  // p всё ещё в measurer'е (тот же node).
  const after = analyzeRunt(p);
  // analyzeRunt вернёт null, если runt пропал, ИЛИ если строк
  // теперь меньше двух — оба варианта = успех.
  // Однако возможна ситуация: runt всё ещё есть, но теперь короче.
  // Считаем успехом, если ПОСЛЕ строк меньше, чем БЫЛО.
  const rangeCheck = document.createRange();
  rangeCheck.selectNodeContents(p);
  const newLineCount = countVisualLines(rangeCheck);

  if (newLineCount >= runt.lineCount) {
    // Откат
    p.classList.remove('has-runt-hang');
    p.style.removeProperty('--runt-hang-x');
    if (wrappedSpan) {
      // Развернуть обёртку обратно
      const parent = wrappedSpan.parentNode;
      const textNode = document.createTextNode(wrappedSpan.textContent);
      // Склеить с соседними text-nodes, если есть
      parent.replaceChild(textNode, wrappedSpan);
      // Простая нормализация соседних text-узлов
      parent.normalize();
    } else if (tgt.kind === 'element') {
      tgt.el.classList.remove('runt-hang');
    }
    return false;
  }

  return true;
}

// Вспомогательная: визуальное число строк через тот же byLine-механизм.
function countVisualLines(range) {
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

### 4.5. Главная функция — `preventRunts`

```js
// Обрабатывает все <p> в массиве blocks (в порядке появления в кодексе).
//
// blocks — Array<Element>, как и в paginate; нам интересны только
// блоки type === 'p'. Маргиналии, рубрики и колофоны пропускаем
// (для маргиналий runt-hang отдельная техника, для рубрик и колофонов
// сирот не бывает по природе).
//
// Мутирует blocks in-place: добавляет класс has-runt-hang к нужным
// <p>, оборачивает runt-target'ы в .runt-hang.
//
// Возвращает: { processed, fixed, refused } для диагностики.
function preventRunts(blocks, measurerContent) {
  let processed = 0;
  let fixed = 0;
  let refused = 0;

  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    if (block.nodeType !== 1) continue;
    if (block.tagName !== 'P') continue;

    // Исключения:
    // - theological: сакральные абзацы, неприкосновенны (canSplit=false)
    // - dropcap: первая строка содержит большую буквицу, метрики ширины
    //            не совпадают со средними; ложные срабатывания.
    // - no-runt-hang: явный flag из разметки.
    if (block.classList.contains('theological')) continue;
    if (block.classList.contains('dropcap')) continue;
    if (block.classList.contains('no-runt-hang')) continue;

    processed++;

    // Ставим в measurer.
    // ВАЖНО: блок переезжает из template'а в measurer, не клон.
    // Это критично — нам нужно мутировать ИМЕННО ТОТ узел, который
    // потом пойдёт в paginate. (paginate работает с теми же узлами
    // и клонирует их в свой measurer уже после нашего фикса.)
    //
    // После анализа возвращаем блок обратно в template на исходное
    // место. Для этого помним previousSibling и parent.
    const parent = block.parentNode;
    const nextSibling = block.nextSibling;

    measurerContent.replaceChildren(block);

    const runt = analyzeRunt(block);
    if (runt) {
      const ok = applyRuntHang(block, runt, measurerContent);
      if (ok) fixed++; else refused++;
    }

    // Возвращаем блок в template
    measurerContent.removeChild(block);
    if (nextSibling) {
      parent.insertBefore(block, nextSibling);
    } else {
      parent.appendChild(block);
    }
  }

  // Чистим measurer на всякий случай.
  measurerContent.replaceChildren();

  return { processed: processed, fixed: fixed, refused: refused };
}
```

### 4.6. Утилита 4 — пометка фолио после рендера

```js
// После того как пагинатор уложил блоки по фолио и renderBook
// построил физический DOM, проходим по каждому .folio-content и
// смотрим, есть ли внутри хотя бы один <p> с has-runt-hang. Если
// есть — навешиваем .has-runt-hang-inside, чтобы CSS снял
// overflow:hidden локально.
//
// Эта функция должна вызываться ПОСЛЕ renderBook и ДО
// positionMarginalia (positionMarginalia измеряет геометрию, и
// если overflow:hidden срежет хвост, измерения будут корректны
// только при уже снятом overflow).
function markFoliosWithRuntHang() {
  const contents = document.querySelectorAll('#codex-book .folio-content');
  for (let i = 0; i < contents.length; i++) {
    const c = contents[i];
    if (c.querySelector('p.has-runt-hang')) {
      c.classList.add('has-runt-hang-inside');
    }
  }
}
```

---

## 5. Изменения в `run()`

### 5.1. Существующий код (~строка 9788–9802)

```js
  const measurer = createMeasurer();
  document.body.appendChild(measurer);
  const measurerContent = measurer.querySelector('.folio-content');
  const lineHeight = measureLineHeight(measurerContent);

  const t0 = performance.now();
  const pages = paginate(blocks, measurerContent, lineHeight);
  const t1 = performance.now();

  measurer.remove();

// ── Фаза 1: построение DOM книги ──
  // Все вставки и присвоения классов до первого layout read.
  renderBook(pages);
```

### 5.2. Заменить на

```js
  const measurer = createMeasurer();
  document.body.appendChild(measurer);
  const measurerContent = measurer.querySelector('.folio-content');
  const lineHeight = measureLineHeight(measurerContent);

  // ── Фаза 0.5: runt-prevention (Стратегия C) ──
  // Анализируем каждый <p>, при наличии runt-кандидата оборачиваем
  // последнее слово в .runt-hang и навешиваем <p> класс has-runt-hang.
  // Делается ДО paginate, чтобы пагинатор увидел уже скорректирован-
  // ный layout (меньше строк в фиксированных абзацах => плотнее
  // упаковка страниц).
  const tRuntStart = performance.now();
  const runtStats = preventRunts(blocks, measurerContent);
  const tRuntEnd = performance.now();
  if (window.console) {
    console.log(
      '[runt-hang] processed=' + runtStats.processed +
      ' fixed=' + runtStats.fixed +
      ' refused=' + runtStats.refused +
      ' in ' + (tRuntEnd - tRuntStart).toFixed(0) + ' ms'
    );
  }

  const t0 = performance.now();
  const pages = paginate(blocks, measurerContent, lineHeight);
  const t1 = performance.now();

  measurer.remove();

// ── Фаза 1: построение DOM книги ──
  // Все вставки и присвоения классов до первого layout read.
  renderBook(pages);

  // Пометка фолио с runt-hang (для локального снятия overflow:hidden
  // у их .folio-content; см. CSS-секцию runt-hang).
  markFoliosWithRuntHang();
```

### 5.3. Точка вставки в текстовом виде

Найти строку:

```
  const lineHeight = measureLineHeight(measurerContent);
```

Перед строкой `const t0 = performance.now();` (которая идёт примерно через 2 строки ниже) вставить блок `Фаза 0.5` целиком.

Найти строку:

```
  renderBook(pages);
```

Сразу после неё вставить вызов `markFoliosWithRuntHang();` с предшествующим комментарием.

---

## 6. Идемпотентность при resize

В текущей архитектуре `resize` не запускает `walkJitter`/`paginate` заново — только `positionMarginalia()` (см. строки 9846–9853 в run). Это значит: **runt-hang классы и обёртки, поставленные в фазе 0.5, переживают resize без повторной обработки.**

Однако `--runt-hang-x` задано в пикселях, не в `em`. Если пользователь меняет zoom браузера (Ctrl+/-), все геометрические значения масштабируются согласованно, и пиксельное значение остаётся релевантным. Если же изменяется размер окна (что меняет `--folio-w` на mobile через media query), может возникнуть рассинхрон. Это **известное ограничение** — лечится в будущей версии переходом на `em` единицы и/или сбросом+пересчётом всех runt-hang в обработчике resize.

На текущем этапе делаем **минимально достаточное**: runt-hang работает корректно при первом рендере и при resize в пределах одного breakpoint'а.

---

## 7. Тестовые сценарии

После внедрения фикса нужно проверить:

| Сценарий | Ожидаемое поведение |
|----------|---------------------|
| Абзац с однострочным runt'ом (типа "atque", "vidit.") | `has-runt-hang` появляется, абзац стал на 1 строку короче, хвост виден за правой границей `.folio-content` |
| Абзац с runt'ом, состоящим из слогового хвоста ("runt" после `praedicave-`) | То же; внутри runt'а нет `<wbr>` (заблокирован через `white-space: nowrap` на `.runt-hang`) |
| Абзац, у которого последняя строка занимает >= 25% колонки | `has-runt-hang` НЕ ставится (это уже не runt) |
| Абзац с классом `.theological` | runt-hang не применяется (исключение) |
| Абзац с однострочным содержимым | runt-hang не применяется (lineCount < 2) |
| Абзац, у которого слово runt > 30 px шириной | `applyRuntHang` возвращает false (превышен HARD_MAX_HANG_PX), runt остаётся как есть |
| Hовый абзац после fixed абзаца, который теперь стал короче | `paginate` упаковал страницу плотнее; следующий блок поднялся выше |
| Фолио с маргиналией в внешнем поле + runt-hang в основном тексте на той же высоте | **визуальная коллизия возможна** — см. секцию Edge cases ниже |

### 7.1. Ручная проверка через DevTools

В консоли:

```js
// Сколько абзацев получили фикс
document.querySelectorAll('p.has-runt-hang').length

// Распределение по ширине выступа
Array.from(document.querySelectorAll('p.has-runt-hang')).map(p =>
  p.style.getPropertyValue('--runt-hang-x')
)

// Визуально подсветить — временно
document.styleSheets[0].insertRule(
  'p.has-runt-hang { outline: 1px dashed crimson; } ' +
  '.runt-hang { background: rgba(255,200,200,0.4); }',
  document.styleSheets[0].cssRules.length
);
```

---

## 8. Edge cases и риски

### 8.1. Маргиналии в внешнем поле

`--folio-pad-outer: 82px` — это поле, где живут маргиналии. Если runt-hang выступает в это поле и одна из маргиналий находится на той же Y-координате, **они будут перекрываться визуально**.

**Текущее решение в этой спеке**: коллизия не детектируется. Выступ ≤ 30 px, маргиналии обычно начинаются дальше от текстового блока (отдельная колонка). Реальная коллизия редка; если возникнет — добавить в `applyRuntHang` проверку Y-координаты против absolute-позиций маргиналий после `positionMarginalia`.

**Если хочется решить сразу** (вне scope, но указать): в `applyRuntHang` после успешного применения проверить через `getBoundingClientRect()` пересечение с маргиналиями на той же странице. Поскольку в фазе 0.5 страницы ещё не построены, эту проверку правильнее делать post-render — отдельной фазой `validateRuntHangsAgainstMarginalia` между `positionMarginalia` и финализацией. Если пересечение — снять класс.

### 8.2. `dropcap` параграфы

У dropcap-параграфов первая буква в 2-3 раза больше шрифта; первая строка геометрически зажата (более узкая визуально). `getClientRects()` возвращает для них странную геометрию. Поэтому **в спеке dropcap-параграфы исключены** через явный classList-check в preventRunts. Если оставить их в обработке, возможны ложные срабатывания на первой строке (которая воспринимается как «короткая последняя» из-за обтекания вокруг буквицы).

### 8.3. Параграфы с `.uncial-passage` внутри

Если внутри `<p>` есть `<em class="uncial-passage">` с другим шрифтом — рендеринг строк может дать нестандартную геометрию (разная высота rect'ов). `analyzeRunt` группирует rect'ы по Y с допуском ±3px — это покрывает 90% случаев. Если шрифт uncial-passage значительно крупнее (font-size > 1.15em основного), возможны ложные срабатывания. Симптом — нестабильные `lineCount`. Лечится увеличением допуска группировки до ±5–8 px (поменять константу `3` в `analyzeRunt` и `countVisualLines`).

### 8.4. Откат при отказе

`applyRuntHang` делает откат через `parent.normalize()` после удаления обёртки. Это сливает соседние text-nodes. Большинство потомков `<p>` — text-nodes, span'ы, `<wbr>`. `normalize()` НЕ затрагивает структуру span'ов и не мерджит их. **Безопасно.**

Однако: если runt-target был элементом (`tgt.kind === 'element'`), мы лишь снимаем класс, обёртку не разворачиваем. Это **полностью идемпотентный** случай.

### 8.5. Translate-режим (`body.mg-translated`)

В режиме перевода `.word-source` показывается, `.word-render` скрывается. Структура `.word-wbr` остаётся, и класс `runt-hang` на ней тоже работает (он применяет `white-space: nowrap`, которое всё равно никого не интересует, потому что `.word-source` короткий и без `<wbr>`).

**Проблема**: ширина слова в режиме перевода может быть другой, и `--runt-hang-x`, вычисленная для render-режима, окажется некорректной. На практике перевод обычно лишь чуть короче или такой же по ширине → выступ будет либо тот же, либо чуть меньше требуемого (что **безопасно** — просто фикс не сработает идеально, абзац может вернуться к runt'у, но без негативных последствий).

**Что в спеке не делается**: пересчёт `--runt-hang-x` при переключении в translate-режим. Это можно добавить через MutationObserver на `body.classList` + повторный проход `preventRunts`. Вне scope текущей итерации.

### 8.6. Catchword'ы

`attachCatchwords` ставит catchword (call-перенос) в правом нижнем углу `.folio-content`. Если в runt-hang выступ попадает в зону catchword'а — они визуально пересекутся.

На практике catchword внизу страницы, а runt-hang — на последней строке абзаца, которая обычно не на самом нижнем краю фолио (пагинация старается заполнять страницу). Конфликт маловероятен. Если возникнет — диагностируется визуально, лечится исключением последнего абзаца на странице из preventRunts.

---

## 9. Rollback

Полностью откатить фикс — три действия:

1. Удалить весь блок CSS (секция 3.2).
2. Удалить четыре функции JS (секции 4.2–4.6) и функцию `markFoliosWithRuntHang`.
3. В `run()` удалить блок «Фаза 0.5» и вызов `markFoliosWithRuntHang()`.

Никаких дополнительных мутаций DOM в `preprocessSourceTemplate` или `paginate` не делается, так что rollback изолирован.

Частичный rollback — например, оставить детектирование, но не применять (для сбора статистики):

```js
// В preventRunts, в месте where applyRuntHang вызывается:
// if (runt) { const ok = applyRuntHang(...); ... }
// Заменить на:
if (runt) {
  console.log('[runt-hang] would fix:', block.textContent.slice(0, 60), runt);
  refused++;
}
```

---

## 10. Известные ограничения

- **Только основной текст.** Маргиналии не обрабатываются — там runt'ы частые и эстетически нормальные (узкая колонка). Для маргиналий рекомендуется отдельная стратегия A (запрет `<wbr>` в последнем слове), как обсуждалось в предыдущем анализе.
- **Жёсткий пиксельный лимит выступа.** 30 px — компромисс. Длинные слова (типа `incarnatione`) шириной > 30 px при ширине runt-строки > 26 px не лечатся. На шрифте Kells это слова в ~7+ букв.
- **Не учитывает positionMarginalia.** Если маргиналия физически перекрывается с выступом, визуально это видно. Описано в 8.1.
- **Не пересчитывается в translate-режиме.** Описано в 8.5.
- **Не пересчитывается при изменении breakpoint.** Описано в секции 6.

---

## 11. Что вне scope этой спеки

- Стратегия A (запрет `<wbr>` в последнем слове абзаца) — отдельная техника, может сочетаться, но не зависит от C.
- Стратегия B (сжатие соседних `.ws` для уменьшения wrap-pressure) — отдельная техника.
- Уменьшение `--space-amp-base` с 0.60em до 0.20em (предыдущая итерация анализа) — отдельная правка, должна делаться независимо.
- Аналогичная обработка `.marginalia` — описано в общих чертах в предыдущем ответе, отдельной спекой.
- Validation outside layout — runt-hang против маргиналий — описано в 8.1, отдельная фаза.

---

## 12. Сводный diff (только места правок)

| Файл / место | Действие | Размер |
|--------------|----------|--------|
| `<style>` после строки ~1521 | Добавить секцию `RUNT-HANG` CSS | ~25 строк |
| `<script>` после функции `paginate` (~строка 6190) | Добавить пять функций: `findLastWordTarget`, `hasOtherWordTextNodes`, `analyzeRunt`, `applyRuntHang`, `countVisualLines`, `preventRunts`, `markFoliosWithRuntHang` | ~210 строк |
| `<script>`, функция `run()` (~строка 9794) | Вставить фазу 0.5 после `measureLineHeight` | ~10 строк |
| `<script>`, функция `run()` (~строка 9803) | Вставить вызов `markFoliosWithRuntHang()` после `renderBook(pages)` | ~3 строки |

**Итого:** ~248 строк добавлений, 0 строк изменений существующего кода. Чистое расширение функциональности без правки существующих систем — идеально для атомарного коммита и быстрого rollback.
