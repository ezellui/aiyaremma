# Анализ и исправление ошибок в коде статистики графа философских концепций

## Обзор проблем

В результате детального анализа кода обнаружены следующие критические ошибки и рассогласования:

---

## 1. КРИТИЧЕСКАЯ ОШИБКА: Несоответствие имени переменной PageRank кэша

### Проблема
В коде используются два разных написания переменной кэша PageRank:
- `pageRankCache` (с заглавной R) - в объявлении и функции расчёта
- `pagerankCache` (со строчной r) - в функциях отображения и визуализации

### Места ошибок
1. **Строка 3978** - функция `generatePageRankContent()`:
```javascript
if (!pagerankCache || pagerankCache.length === 0) {
```

2. **Строка 3984** - функция `generatePageRankContent()`:
```javascript
pagerankCache.slice(0, 30),
```

3. **Строка 4850** - функция `toggleMetricVisualization()`:
```javascript
case 'pagerank':
    metricData = pagerankCache;
    break;
```

### Исправление
Заменить все вхождения `pagerankCache` на `pageRankCache` (с заглавной R):

```javascript
// Строка 3978 - ИСПРАВИТЬ
function generatePageRankContent() {
    if (!pageRankCache || pageRankCache.length === 0) {
        return generateCalculateButton('PageRank', 'pagerank', 
            'Алгоритм PageRank определяет важность узлов на основе количества и качества входящих связей');
    }
    
    return generateMetricResults(
        pageRankCache.slice(0, 30),  // ИСПРАВИТЬ
        '⭐ PageRank',
        'Важность узлов на основе входящих связей',
        'pagerank',
        'value',
        true
    );
}
```

```javascript
// Строка 4850 - ИСПРАВИТЬ
case 'pagerank':
    metricData = pageRankCache;  // ИСПРАВИТЬ
    break;
```

---

## 2. ОШИБКА: Неправильная инициализация данных философов

### Проблема
В функции `initializePhilosophyMetrics()` (строка 3187-3191) создаются философы с произвольными датами рождения вместо использования реальных данных из массива `philosophers`.

### Место ошибки
```javascript
// Строки 3187-3191 - НЕПРАВИЛЬНО
const philosophersData = Array.from(new Set(nodes.map(n => n.concept))).map((concept, idx) => ({
    id: concept,
    name: concept,
    birth: 1800 + idx * 10  // ← Произвольные даты!
}));
```

### Исправление
Использовать реальные данные из массива `philosophers`:

```javascript
// ИСПРАВИТЬ функцию initializePhilosophyMetrics() (начиная со строки 3170)
function initializePhilosophyMetrics() {
    try {
        const conceptsData = nodes.map(n => ({
            id: n.id,
            label: n.label,
            philosopher: n.concept,
            rubrics: n.rubrics || []
        }));
        
        const relationsData = links.map(l => ({
            source: typeof l.source === 'object' ? l.source.id : l.source,
            target: typeof l.target === 'object' ? l.target.id : l.target,
            type: l.type || 'influence',
            weight: l.weight || 1,
            bidirectional: l.bidirectional || false
        }));
        
        // ИСПРАВЛЕНО: используем реальные данные философов
        const philosopherNameMap = {};
        philosophers.forEach(p => {
            philosopherNameMap[p.nameRu] = p;
        });
        
        const uniquePhilosophers = Array.from(new Set(nodes.map(n => n.concept)));
        const philosophersData = uniquePhilosophers.map(concept => {
            const philData = philosopherNameMap[concept];
            return {
                id: concept,
                name: concept,
                birth: philData ? philData.birth : 0,
                death: philData ? philData.death : 0
            };
        });
        
        initializeMetricsData(conceptsData, relationsData, philosophersData);
        
        console.log('✅ Философские метрики инициализированы');
        return true;
    } catch (error) {
        console.error('❌ Ошибка при инициализации метрик:', error);
        return false;
    }
}
```

---

## 3. ОШИБКА: Вызов несуществующей функции switchMetric

### Проблема
В функции `runSingleMetric()` (строка 5148) вызывается функция `switchMetric(metricName)`, которая не определена в коде.

### Место ошибки
```javascript
// Строка 5148
setTimeout(() => {
    hideProgress();
    switchMetric(metricName);  // ← Функция не существует!
}, 500);
```

### Исправление
Удалить вызов несуществующей функции или заменить на корректный вызов:

```javascript
// ИСПРАВИТЬ строки 5145-5149
showProgress('Готово!', 100);
setTimeout(() => {
    hideProgress();
    // Убираем вызов несуществующей функции
    console.log(`✅ Метрика ${metricName} рассчитана`);
}, 500);
```

---

## 4. ОШИБКА: Проблемная проверка metricsObj в toggleMetricVisualization

### Проблема
В функции `toggleMetricVisualization()` (строка 4917) есть проверка `if (funcName && metricsObj)`, но `metricsObj` нигде не определён, и комментарий выше (строка 4915) говорит, что он не нужен.

### Место ошибки
```javascript
// Строки 4915-4920
const funcName = metricFunctions[metricKey];
// Теперь все функции глобальные, не нужен metricsObj

if (funcName && metricsObj) {  // ← metricsObj не определён!
    metricData = nodes.map(n => ({
        node: n,
        value: window[funcName](n.id).total || window[funcName](n.id).weighted || 0
```

### Исправление
Убрать проверку `metricsObj`:

```javascript
// ИСПРАВИТЬ строки 4914-4925
const funcName = metricFunctions[metricKey];

if (funcName) {  // ИСПРАВЛЕНО: убрана проверка metricsObj
    metricData = nodes.map(n => {
        const result = window[funcName](n.id);
        const value = result.total !== undefined ? result.total : 
                     result.weighted !== undefined ? result.weighted : 0;
        return {
            node: n,
            value: value
        };
    });
    break;
}
```

---

## 5. ПОТЕНЦИАЛЬНАЯ ПРОБЛЕМА: Отсутствие обработки ошибок при визуализации

### Проблема
В функции `visualizeMetricBySize()` (около строки 4930) нет проверки на наличие данных перед визуализацией.

### Рекомендация по улучшению
Добавить проверку данных в начале функции `visualizeMetricBySize()`:

```javascript
// Добавить в начало функции visualizeMetricBySize (найти по поиску)
function visualizeMetricBySize(metricName, metricData) {
    // ДОБАВИТЬ проверку данных
    if (!metricData || metricData.length === 0) {
        console.warn(`⚠️ Нет данных для визуализации метрики ${metricName}`);
        return;
    }
    
    // Остальной код функции...
```

---

## 6. ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ: Кэширование философских метрик

### Проблема
Философские метрики (problem-generation, critical-power и т.д.) пересчитываются каждый раз заново, хотя для них объявлены переменные кэша.

### Текущий код
```javascript
// Строка 2396
let problemGenerationIndexCache = null;
// Но функция problemGenerationIndex (строка 2398) не использует этот кэш
```

### Рекомендация
Реализовать кэширование для всех философских метрик. Пример для `problemGenerationIndex`:

```javascript
// УЛУЧШИТЬ функцию problemGenerationIndex (около строки 2398)
function problemGenerationIndex(conceptId) {
    // Используем кэш если есть
    if (problemGenerationIndexCache && problemGenerationIndexCache.has(conceptId)) {
        return problemGenerationIndexCache.get(conceptId);
    }

    const incoming = _incomingLinks.get(conceptId) || [];

    const critiques = incoming.filter(r => r.type === 'critique').length;
    const oppositions = incoming.filter(r => r.type === 'oppose').length;
    const contradictions = incoming.filter(r => r.type === 'internal_contradiction').length;

    const weightedCriticism = incoming.reduce((sum, r) => {
        const typeWeight = {
            'critique': 2,
            'oppose': 3,
            'internal_contradiction': 4
        }[r.type] || 0;
        return sum + typeWeight * (r.weight || 1);
    }, 0);

    const result = {
        raw: critiques + oppositions + contradictions,
        weighted: weightedCriticism,
        critiques,
        oppositions,
        contradictions
    };
    
    // Сохраняем в кэш
    if (!problemGenerationIndexCache) {
        problemGenerationIndexCache = new Map();
    }
    problemGenerationIndexCache.set(conceptId, result);
    
    return result;
}
```

Аналогичные улучшения нужно применить ко всем остальным философским метрикам.

---

## 7. ПРОВЕРКА: Согласованность HTML-разметки модального окна

### Проблема
Нужно убедиться, что в HTML-разметке модального окна (строки 839-1063) правильно объявлены все элементы.

### Проверка элементов
В коде должны присутствовать следующие элементы с правильными ID:

```html
<!-- Эти элементы ДОЛЖНЫ быть в HTML (около строк 839-1063) -->
<div id="statsModal" class="...">
    <div class="stats-modal-content">
        <div class="stats-modal-header">
            <!-- Переключатели параметров -->
            <div class="stats-parameter-toggle">
                <input type="checkbox" id="statsUseWeightsToggle" 
                       onchange="handleStatsParameterChange()">
                <label for="statsUseWeightsToggle">Учитывать веса</label>
            </div>
            <div class="stats-parameter-toggle">
                <input type="checkbox" id="statsRespectDirectionToggle" 
                       onchange="handleStatsParameterChange()">
                <label for="statsRespectDirectionToggle">Учитывать направленность</label>
            </div>
            <!-- Кнопка закрытия -->
            <button class="stats-close-btn" onclick="closeStatsModal()">×</button>
        </div>
        <div class="stats-modal-body">
            <!-- Навигация и контент -->
            <div class="stats-content-area" id="statsContentArea">
                <!-- Динамический контент -->
            </div>
        </div>
    </div>
</div>

<!-- Индикатор прогресса -->
<div id="analysisProgress" class="stats-progress-indicator" style="display: none;">
    <div class="stats-progress-text" id="progressLabel">Расчёт...</div>
    <div class="stats-progress-bar">
        <div class="stats-progress-fill" id="progressBar" style="width: 0%;"></div>
    </div>
    <div class="stats-progress-text" id="progressPercent">0%</div>
</div>
```

### Исправление (если элементов нет)
Если каких-то элементов не хватает в HTML, нужно их добавить. Проверьте наличие:
1. `<div id="statsModal">` - основной контейнер модального окна
2. `<input id="statsUseWeightsToggle">` - переключатель весов
3. `<input id="statsRespectDirectionToggle">` - переключатель направленности
4. `<div id="statsContentArea">` - область контента
5. `<div id="analysisProgress">` - индикатор прогресса
6. `<div id="progressBar">` - полоса прогресса
7. `<div id="progressLabel">` - метка прогресса
8. `<div id="progressPercent">` - процент прогресса

---

## Итоговый чек-лист исправлений

### Критические (обязательные)
- [ ] ✅ **Исправить** `pagerankCache` → `pageRankCache` (3 места: строки 3978, 3984, 4850)
- [ ] ✅ **Исправить** функцию `initializePhilosophyMetrics()` для использования реальных дат философов (строка 3187-3191)
- [ ] ✅ **Удалить** вызов несуществующей функции `switchMetric()` (строка 5148)
- [ ] ✅ **Исправить** проверку `metricsObj` в функции `toggleMetricVisualization()` (строка 4917)

### Рекомендуемые (улучшения)
- [ ] ⚠️ Добавить проверку данных в функцию `visualizeMetricBySize()`
- [ ] ⚠️ Реализовать кэширование для всех философских метрик
- [ ] ⚠️ Проверить наличие всех необходимых HTML-элементов

---

## Дополнительные рекомендации

### 1. Единообразие названий переменных
Рекомендуется использовать camelCase с заглавной буквой для всех кэш-переменных:
- `pageRankCache` ✓
- `betweennessCache` ✓
- `closenessCache` ✓
- `eigenvectorCache` ✓
- `weightedClusteringCache` ✓
- `localCohesionCache` ✓
- `richClubCache` ✓

### 2. Обработка ошибок
Добавить try-catch блоки во все функции расчёта метрик для перехвата и логирования ошибок.

### 3. Валидация данных
Добавить валидацию входных данных в начале критических функций.

---

## Проверка работоспособности после исправлений

После внесения исправлений необходимо проверить:

1. **Открытие модального окна статистики**
   - Кнопка "Открыть панель статистики" работает
   - Переключатели параметров отображаются и работают

2. **Расчёт базовых метрик**
   - PageRank рассчитывается и отображается
   - Betweenness рассчитывается и отображается
   - Closeness рассчитывается и отображается
   - Eigenvector рассчитывается и отображается

3. **Расчёт новых метрик**
   - Weighted Clustering рассчитывается и отображается
   - Local Cohesion рассчитывается и отображается
   - Rich-Club рассчитывается и отображается

4. **Визуализация метрик размером узлов**
   - Кнопка "Визуализировать размером" работает для всех метрик
   - Размеры узлов меняются согласно значениям метрики
   - Сброс размеров работает корректно

5. **Философские метрики**
   - Все философские метрики рассчитываются с правильными датами философов
   - Результаты отображаются в таблицах

---

## Заключение

Основные проблемы связаны с:
1. Несоответствием имён переменных (критическая ошибка)
2. Неправильной инициализацией данных философов
3. Вызовом несуществующих функций
4. Отсутствием проверок на существование объектов

После внесения всех исправлений код должен работать корректно, и все метрики будут рассчитываться и отображаться правильно.
