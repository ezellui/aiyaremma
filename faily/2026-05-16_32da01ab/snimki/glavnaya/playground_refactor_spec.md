# Playground v2 — спецификация переделки

## 0. Контекст и цели

Файл `illumination_playground.html` — рабочий полигон для подбора параметров фильтра старения иллюстраций (`illumination-aged-*`), который применяется к трём элементам кодекса: front carpet, back carpet, big-initial в дропкапе. В текущей версии playground'а есть два структурных недостатка:

**(A) Один фильтр, три preview.**
В DOM лежит ровно один SVG-фильтр `#illumination-aged`, и он применяется через CSS ко всем трём preview-блокам. То есть на полигоне нельзя проверить, как один и тот же набор параметров расходится по trois инстансам с разными seed'ами — а именно так фильтр существует в финале (front: seeds 52/42/11, back: 71/89/23, initial: 113/67/37). Слайдеров для `coarse-seed` и `fine-seed` тоже нет.

**(B) Мёртвый CSS.**
В блоке стилей лежит копия CSS из основного кодекса целиком — около 3200 строк. Реально playground задействует ~40 классов; остальное — маргиналии, библиотечные штампы, алхимические интерполяции, кодикологические слои, мета-структуры (фолиация, оглавление, plate captions, dedicatory leaf), которых на полигоне нет в принципе.

Цель переделки: исправить оба пункта одним рефакторингом, не трогая ядро SVG-фильтра (оно архитектурно совпадает с финалом 1:1).

---

## 1. Текущая разведка

### 1.1. Что используется в HTML body playground'а

39 классов:

- **Playground UI (9):** `pg-controls`, `pg-dump`, `pg-dump-label`, `pg-layout`, `pg-mode-row`, `pg-preset`, `pg-preset-row`, `pg-preview`, `pg-previews`. (Плюс ещё 6 динамических, которые JS создаёт через DOM: `pg-control`, `pg-control-label`, `pg-value`, `pg-filter-off`, `pg-filter-on-css`, `pg-preset-off`.)
- **Per-preview (3):** `preview-front`, `preview-back`, `preview-initial`.
- **Page structure (9):** `folio`, `folio-content`, `folio-cover`, `folio-cover-front`, `folio-cover-back`, `parchment-bg`, `parch-h1`, `parch-h2`, `parch-h3`.
- **Иллюстрации (4):** `carpet-svg`, `illuminated-initial`, `big-initial`, `dropcap`.
- **Палитра нитей плетёнки (14):** `kk-silver/gold`, `dove-silver/gold`, `frt-silver/gold`, `med-silver/gold`, `node-silver/gold`, `peacock-silver/gold`, `rose-silver/gold`.

Плюс SVG-defs (через `<use href="#...">`): `carpet-frame-outer`, `carpet-frame-inner`, `knot-twist`, `mda`, `mdb`, `luna`, `sol`, `braid-strip`, и т.д. — лежат в первом SVG-блоке в начале body.

### 1.2. Что лежит в CSS, но не используется

Около 135 классов; разнесены по тематическим группам:

| Группа | Примеры классов | Объём |
| --- | --- | --- |
| Маргиналии (рука писца/комментатора) | `.mg-*`, `.mg-coemanus`, `.mg-finanus`, `.mg-aug`, `.mg-cellach`, `.mg-red/left/right/jitter-render/selectable/translate-source/translated` | большой |
| Колофон и поздняя рука | `.colophon`, `.later-hand`, `.later-hand-colophon`, `.nomen-illustre`, `.nomsac`, `.s-abbas`, `.tiro` | средний |
| Библиотечные штампы | `.lib-*`, `.schedel-exlibris`, `.reichenberg`, `.munich`, `.fur-note`, `.ing-note` | большой |
| Probatio pennae | `.prob-*`, `.prob-anon`, `.prob-coemanus`, `.prob-bernardus`, `.prob-flourish`, `.prob-late` | средний |
| Алхимические интерполяции | `.alch`, `.alch-interlinear`, `.alch-mark`, `.alch-quire`, `.alch-quire-edge`, `.alch-quire-outer-edge`, `.alch-rasura`, `.alch-marginal-signum` | большой |
| Кодикологические слои | `.aging-edges-layer`, `.folliculi-layer`, `.ghost-layer`, `.ruling-layer`, `.prick-dots-layer`, `.bounding-lines-layer` | средний |
| Дедикационный лист | `.dedicatory`, `.dedicatory-leaf`, `.dedi-cross`, `.dedi-line` | малый |
| Терминология / titulus | `.titulus-svg`, `.tit`, `.syll`, `.signum`, `.terminus`, `.word-render`, `.word-source`, `.theological`, `.theological-cont` | средний |
| Билингва / translate | `.abbr-translate-source`, `.mg-translate-source`, `.mg-translated`, `.elvish` | малый |
| Структура кодекса | `.flip-book`, `.spread`, `.page-recto`, `.page-verso`, `.gutter`, `.edge-gutter-recto/verso`, `.foliator-note`, `.folio-number`, `.blank-leaf`, `.book-label`, `.book-spine-shadow`, `.book-stack-*` | большой |
| Rasura и эмендации | `.alch-rasura`, `.ink-drip`, `.ink-l` | малый |
| Rubric | `.rubric`, `.rubric-stays`, `.smcaps`, `.t-rubricatus` | малый |
| Catchword/divider/section | `.catchword`, `.divider`, `.section-break-soft`, `.ornament-line` | малый |
| Альт-варианты пергамена | `.parch-f1..f6`, `.parch-h4..h6`, `.parch-alch-f/h` (в playground используются только `parch-h1..h3`) | средний |
| Doc title / dedicatory text | `.doc-title`, `.doc-subtitle`, `.incipit-verso`, `.final-recto`, `.dedi-cross` | малый |
| Jitter / runt / liga | `.jitter-off`, `.letter-jitter-off`, `.mg-jitter-render`, `.has-runt-hang-inside`, `.runt-hang`, `.liga-protect` | средний |
| Прочее | `.bernard`, `.no-aging`, `.no-indent`, `.no-torn`, `.cod`, `.com`, `.gap`, `.h6`, `.leaf`, `.margin-wrap`, `.marginalia`, `.med`, `.terminology` | малый |

«Шум» grep'а (нужно отбросить, это случайные совпадения с inline-SVG data:URL'ами и JS-комментариями): `.toString`, `.intersectsNode`, `.color`, `.height`, `.width`, `.org`, `.google`, `.w3`, `.mjs`, `.s1..s4`, `.dim-1..3`, `.ws`, `.blob`, `.book-stack-` (хвост от обрезанного селектора).

---

## 2. Архитектура полигона трёх фильтров

### 2.1. Варианты UI-модели

**Вариант A — общие параметры + три набора seed'ов.**
Один комплект из 15 слайдеров параметров. Отдельный блок «Seeds» c тремя строками (front / back / initial) и тремя seed'ами в каждой строке (disp / coarse / fine). Три preview-блока показывают разный рисунок шума при одинаковых параметрах.

- **Плюсы:** минимум новых элементов UI; точно соответствует тому, как фильтр сейчас живёт в финале; легко рендерить три фильтра при `updateFilter()`.
- **Минусы:** не позволяет дифференцировать параметры между инстансами. Конкретно — не получится подобрать для initial ослабленный `disp-scale` и более слабые альфы, как предполагает комментарий в финальном фильтре («second-pass патч с дифференцированными scale/alpha»).

**Вариант B — три полностью независимых набора параметров.**
Три полные панели по 15 слайдеров с переключателем активной панели (или таб-интерфейс). Каждый инстанс редактируется автономно.

- **Плюсы:** максимальная гибкость, дифференцированные параметры под каждый инстанс.
- **Минусы:** избыточно сложный UI; требует постоянно переключаться между табами, чтобы синхронизировать общие настройки; в типичной задаче (общий тон старения для всего кодекса) — излишне.

**Вариант C — master + per-instance overrides.**
Один master-комплект из 15 слайдеров. Под ним три блока «overrides» (front/back/initial), каждый блок свёрнут по умолчанию. В блоке override каждый параметр имеет чекбокс «отличать от master»; когда чекбокс снят — наследует master, когда поставлен — открывает локальный слайдер с собственным значением. Плюс три seed'а на инстанс.

- **Плюсы:** покрывает оба сценария — общий тон правится в одном месте, при необходимости отдифференцировать (например, ослабить initial) включается override без перенастройки остального.
- **Минусы:** требует чуть больше JS-логики (resolve семантики override / inherit).

### 2.2. Рекомендация

Вариант C. Семантика «общий тон + локальные дельты» точно описывает реальное использование: в 95% случаев Нянконян будет двигать общие параметры (как в финале сейчас — все три фильтра идентичны кроме seed'ов), а нужны overrides только если возникает second-pass задача типа «ослабить эффект на маленьком 100×100 viewBox у инициала».

Альтернатива (если хочется быстрее): начать с Варианта A, при появлении нужды в дельтах добавить блок overrides отдельным шагом — структурно совместимо.

В дальнейшем спецификация описывает **Вариант C**. Если выберешь A, можно вычеркнуть пункты 2.3.3 и 2.6.2.

### 2.3. Layout панели

Структура `pg-controls`:

```
[ Filter mode toggle: off / on-css ]            (как сейчас)
[ Firefox-diag: disp-type radio ]                (как сейчас)
[ Firefox-diag: cif radio ]                      (как сейчас)
[ Presets: off | current | v4 | v5 | ... ]       (расширенный)

──────  MASTER PARAMS  ──────
[ Группа 1: Гуляние линий — 4 слайдера ]
[ Группа 2: Крупные пятна — 6 слайдеров ]
[ Группа 3: Мелкая зернистость — 5 слайдеров ]

──────  SEEDS (per-instance)  ──────
                disp    coarse    fine
  Front:        [ 52 ]   [ 42 ]   [ 11 ]
  Back:         [ 71 ]   [ 89 ]   [ 23 ]
  Initial:      [ 113]   [ 67 ]   [ 37 ]
  [ Reseed all (random) ]

──────  OVERRIDES  ──────
  ▸ Front overrides           (свёрнут по умолчанию)
  ▸ Back overrides            (свёрнут)
  ▸ Initial overrides         (свёрнут)
```

Каждый блок overrides при раскрытии показывает 15 строк вида:
`[☐] disp-scale         [slider, disabled]    inherit (0.85)`
Когда чекбокс ставится — слайдер активируется и инстанс перестаёт наследовать master по этому параметру.

### 2.4. Изменения в SVG-defs

Вместо одного `#illumination-aged` — три фильтра:

```xml
<filter id="illumination-aged-front"   ...> ... </filter>
<filter id="illumination-aged-back"    ...> ... </filter>
<filter id="illumination-aged-initial" ...> ... </filter>
```

ID элементов внутри каждого фильтра нужно дополнить суффиксом инстанса:
`disp-turb-front`, `disp-map-front`, `coarse-turb-front`, `coarse-mat-front`, `fine-turb-front`, `fine-mat-front` — и аналогично для `-back` / `-initial`.

### 2.5. Изменения в CSS (`.pg-preview`)

Сейчас (строки 3483–3486):
```css
body.pg-filter-on-css .pg-preview .carpet-svg,
body.pg-filter-on-css .pg-preview .illuminated-initial svg,
body.pg-filter-on-css .pg-preview .big-initial svg {
  filter: url(#illumination-aged);
}
```

Становится:
```css
body.pg-filter-on-css .preview-front .carpet-svg {
  filter: url(#illumination-aged-front);
}
body.pg-filter-on-css .preview-back .carpet-svg {
  filter: url(#illumination-aged-back);
}
body.pg-filter-on-css .preview-initial .illuminated-initial svg,
body.pg-filter-on-css .preview-initial .big-initial svg {
  filter: url(#illumination-aged-initial);
}
```

### 2.6. Изменения в JS

**2.6.1. Расширение `CONTROLS` (вне зависимости от варианта).**
Добавить параметры `coarse-seed`, `fine-seed` (range `0..200`). Расширить `disp-seed` до `0..200` (сейчас `0..100`, не дотягивается до seed=113 у initial).

Обновить дефолты всех 15 параметров на актуальные значения из финального dump'а:
```
disp-scale: 0.85    disp-freq: 0.230   disp-octaves: 3
coarse-freq: 0.030  coarse-alpha: 0.500  coarse-offset: -0.070
coarse-r: 0.080  coarse-g: 0.040  coarse-b: 0.000
fine-freq: 2.000  fine-alpha: 0.460
fine-r: 0.060  fine-g: 0.030  fine-b: 0.000
```

**2.6.2. Новая структура состояния (для Варианта C).**
```js
const state = {
  master: { /* 15 параметров */ },
  seeds: {
    front:   { disp: 52,  coarse: 42, fine: 11 },
    back:    { disp: 71,  coarse: 89, fine: 23 },
    initial: { disp: 113, coarse: 67, fine: 37 },
  },
  overrides: {
    front:   { /* субсет параметров; ключи только для активных override'ов */ },
    back:    {},
    initial: {},
  },
};

function resolve(instance, paramName) {
  return state.overrides[instance][paramName] ?? state.master[paramName];
}
```

`updateFilter()` теперь обновляет три фильтра в цикле:
```js
for (const instance of ['front', 'back', 'initial']) {
  applyToFilter(`illumination-aged-${instance}`, instance);
}
```

**2.6.3. Firefox-fix re-attach.**
Текущий `parent.removeChild(filterEl); parent.appendChild(filterEl);` (4716–4718) теперь делается для всех трёх фильтров.

**2.6.4. Пресеты.**
Существующие `v4 / v5 / strong / hand / aged` — это master-only пресеты (без seed'ов и без overrides). Добавить `current` с финальными значениями. Семантика применения: пресет переписывает только master, seeds и overrides не трогает (либо опциональная очистка overrides — обсуждаемо).

### 2.7. Формат dump'а

Сейчас dump показывает один `<filter id="illumination-aged">` блок. Новый dump показывает три блока, сразу готовых к копипасту в `relatio_aidani_codex-late.html` рядом с существующими SVG-фильтрами:

```xml
<!-- FRONT carpet -->
<filter id="illumination-aged-front" ...> ... </filter>

<!-- BACK carpet -->
<filter id="illumination-aged-back" ...> ... </filter>

<!-- INITIAL -->
<filter id="illumination-aged-initial" ...> ... </filter>
```

Кнопка «Copy dump» в UI — копирует все три фильтра разом.

---

## 3. CSS-аудит

### 3.1. Методология

Аудит делается в три прохода:
1. **Класс-инвентарь:** уже сделан в разделе 1 (39 used vs 180 declared).
2. **Сегментный анализ:** проверка каждой комментарной секции CSS на принадлежность к нужным группам — какие комментарии-разделители помечают блоки, которые можно удалять целиком.
3. **Ручная проверка серых зон:** некоторые селекторы оперируют тип-селекторами или ID и не отлавливаются классовым анализом (`@font-face`, `:root` переменные, `body { ... }`, `em.uncial-passage { ... }`).

### 3.2. Что точно нужно

| Блок | Зачем | Объём |
| --- | --- | --- |
| `@font-face` для каролингских/инсулярных шрифтов | дропкап + надписи на carpet'е | ~10 правил |
| `:root` CSS-переменные | пергаментные тона, цвета пигментов, тени | большой |
| `body`, `html` базовые стили | фон страницы playground'а | малый |
| `.folio`, `.parch-h1..h3`, `.parchment-bg` | подложка под preview | средний |
| `.folio-cover`, `.folio-cover-front/back` | контейнер carpet'а | малый |
| `.folio-content` | контейнер для preview-initial с текстом | малый |
| `.carpet-svg` | сам carpet | малый |
| `.illuminated-initial`, `.big-initial`, `.dropcap` | инициал на странице | средний |
| Палитра нитей плетёнки: `.kk-*`, `.dove-*`, `.frt-*`, `.med-*`, `.node-*`, `.peacock-*`, `.rose-*` | покраска жил в SVG carpet'а | средний |
| `.pg-*` блок (3256–3494) | playground UI | большой |
| SVG defs `<svg width=0 ...>` в начале body | `<use>` цели: `carpet-frame-outer/inner`, `knot-twist`, `mda`, `mdb`, `luna`, `sol`, `braid-strip` | большой |

### 3.3. Что точно удаляем

В порядке секций CSS (по строкам разделителей из разведки):

| Секция | Строки (примерно) | Что в ней |
| --- | --- | --- |
| Маргиналии Коемана | ~958–977 | `.mg-coemanus` и связанные |
| Маргиналия Финана | ~978–1012 | `.mg-finanus` |
| Поздняя рука в колофоне | ~1013–1050 | `.later-hand`, `.later-hand-colophon` |
| Фолиация и foliator-note на алхимических листах | ~1118–1132 | `.foliator-note`, `.folio-number` (если только не нужна для preview-initial — проверить) |
| Hair/flesh варианты пергамена (вне нужных) | ~2212–2544 кроме `.parch-h1..h3` | `.parch-h4..h6`, `.parch-f1..f6` (используются ли `h2/h3` — нужно сверить, возможно достаточно одного варианта) |
| Седьмой пергамен hair/flesh | ~2666–2707 | специфический пергамен для одного passage |
| Шов/guard у фальца | ~2708–2814 | `.alch-quire-edge`, `.alch-quire-outer-edge` |
| Inline-rasura | ~2815–2863 | `.alch-rasura` |
| Interlinear alchemica | ~2864–2891 | `.alch-interlinear*` |
| Alch-mark | ~2892–3113 | `.alch-mark`, `.alch-marginal-signum`, `.alch` |
| Кодикологические штампы (общий заголовок и все 6) | ~3114–3255 | `.m-FUR/Ing/Aug`, `.schedel-exlibris`, `Clm`, `.reichenberg`, и все их потомки |

Плюс из не-помеченных декоративными комментариями участков (нужно отлавливать по селекторам):
- `.dedicatory*`, `.dedi-*`
- `.flip-book`, `.spread`, `.page-recto`, `.page-verso`, `.gutter`, `.edge-gutter-*`
- `.doc-title`, `.doc-subtitle`, `.incipit-verso`, `.final-recto`
- `.aging-edges-layer`, `.folliculi-layer`, `.ghost-layer`, `.ruling-layer`, `.prick-dots-layer`, `.bounding-lines-layer`
- `.titulus-svg`, `.tit`, `.syll`, `.signum`, `.terminus`, `.word-render`, `.word-source`, `.theological*`
- `.rubric*`, `.smcaps`, `.t-rubricatus`
- `.catchword`, `.divider`, `.section-break-soft`, `.ornament-line`
- `.colophon`, `.nomen-illustre`, `.nomsac`, `.s-abbas`, `.tiro`, `.bernard`
- `.jitter-off`, `.letter-jitter-off`, `.mg-jitter-render`, `.has-runt-hang-inside`, `.runt-hang`, `.liga-protect`
- `.prob-*`
- `.lib-*`, `.book-label`, `.book-spine-shadow`, `.book-stack-*`, `.fur-note`, `.ing-note`, `.munich`
- `.blank-leaf`, `.leaf`, `.margin-wrap`, `.marginalia`, `.med`
- `.elvish`, `.abbr-translate-source`, `.mg-translate-source`, `.mg-translated`
- `.no-aging`, `.no-indent`, `.no-torn`
- `.ink-drip`, `.ink-l`
- любые `@media print { ... }` блоки (если есть)

### 3.4. Серые зоны (нужна проверка)

- **`em.uncial-passage`** и связанные — используется ли уж в надписях на carpet'е? Нужно посмотреть, нет ли в SVG-defs или внутри preview-блоков элементов `<em class="uncial-passage">`. (Беглый скан говорит, что нет — но проверить.)
- **Переменные `:root`** — некоторые могут касаться только основного кодекса (например, переменные для книжной обложки, для алхимического пергамена, для штампов). Их можно вычистить, но это аккуратная работа: переменная, объявленная в `:root`, выглядит безобидно, но если она единственный источник какого-то значения для нужного класса — поломаем.
- **`@font-face`-декларации** — нужно сверить со шрифтами, реально упомянутыми в `font-family` у используемых классов. В playground'е используется `0550 Uncialis`, `0800 Remedius`, `Uncial Antiqua`, возможно ещё пара — остальные `@font-face` (для греческого, готического, scriptio continua etc.) можно убрать.
- **`@keyframes`** — если playground'у нужны какие-то анимации (мерцание шума? нет?), нужно решить. Скорее всего удаляем все.
- **`parch-h2`, `parch-h3`** — `parch-h1` точно используется во front, но `h2` (preview-initial) и `h3` — нужно проверить, действительно ли требуются три разных, или достаточно одного для всего playground'а.

---

## 4. Поэтапный план имплементации

Предлагаю разбить на 3 коммита:

**Шаг 1 — мёртвый CSS (без архитектурных изменений).**
Удалить все секции из 3.3 + чистка серых зон из 3.4. Visual smoke test: открыть playground, убедиться что три preview-блока выглядят так же, как до чистки. Ожидаемое сокращение файла: -2500…3000 строк CSS (~50–60% всего файла).

**Шаг 2 — три фильтра в DOM + per-instance seeds.**
Расширить `CONTROLS` (новые `coarse-seed` и `fine-seed`, диапазон `disp-seed` до 0..200), обновить дефолты до финальных. Размножить фильтр в SVG-defs на три. Обновить CSS привязки к preview-блокам. Обновить `updateFilter()` для трёх инстансов. Добавить блок "Seeds" в UI. Обновить формат dump'а.

На этом шаге останавливаемся, если Вариант A — это уже всё.

**Шаг 3 — overrides (только для Варианта C).**
Добавить структуру `state.overrides`, функцию `resolve()`. Сгенерировать UI трёх свернутых блоков overrides. Подключить чекбоксы → активацию слайдеров. Обновить пресет-логику (чтобы пресет очищал overrides, или нет — обсуждаемо).

---

## 5. Открытые вопросы для решения до старта

1. **Какой UI-вариант — A, B или C?** Моя рекомендация — C; от ответа зависит, нужен ли Шаг 3.
2. **Хочешь ли ты «Reseed all (random)» кнопку?** Удобно для быстрой генерации новых seed-сетов при экспериментах.
3. **При применении пресета — очищать overrides или сохранять?** Я бы предлагал очищать (по принципу «пресет = чистая точка»), но это нестандартное поведение.
4. **Глубина CSS-чистки на Шаге 1: только классы или включая `:root`-переменные и `@font-face`?** Первое безопасно и даёт ~80% эффекта; второе требует ручной проверки каждой переменной.
5. **Что делать с `parch-h2/h3`?** Может, нормализовать на один пергаменный пресет для всего playground'а (так визуально однороднее) — или оставить три разных листа как сейчас, чтобы preview ближе к реальному кодексу?

После твоего фидбэка по этим пяти пунктам я могу приступать к имплементации Шага 1.
