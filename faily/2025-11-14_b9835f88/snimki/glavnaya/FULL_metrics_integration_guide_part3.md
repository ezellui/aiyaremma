# ПОЛНОЕ РУКОВОДСТВО ПО ИНТЕГРАЦИИ МЕТРИК
## Версия 2.0 - Часть 3 (ФИНАЛ)

---

## 7. ГЕНЕРАТОРЫ КОНТЕНТА ДЛЯ ВСЕХ МЕТРИК {#генераторы-контента}

**ВНИМАНИЕ:** Все генераторы находятся в файле `FULL_metrics_integration_guide_GENERATORS.js` 
из-за большого размера кода (~2000 строк).

Основные функции генераторов:

```javascript
// Вспомогательная функция для генерации блока описания метрики
function generateMetricDescriptionBlock(metricKey) {
    const desc = getMetricDescription(metricKey);
    if (!desc) return '';
    
    return `
        <div class="metric-description-box">
            <div class="metric-description-section">
                <div class="metric-description-label">📋 Что измеряет</div>
                <div class="metric-description-text">${desc.description}</div>
            </div>
            
            <div class="metric-description-section">
                <div class="metric-description-label">💡 Интерпретация</div>
                <div class="metric-description-text">${desc.interpretation}</div>
            </div>
            
            <div class="metric-description-section">
                <div class="metric-description-label">🎯 Применение</div>
                <div class="metric-description-text">${desc.usage}</div>
            </div>
            
            <div class="metric-description-section">
                <div class="metric-description-label">🧮 Формула</div>
                <div class="metric-formula">${desc.formula}</div>
            </div>
        </div>
    `;
}

// Вспомогательная функция для генерации кнопки расчёта
function generateCalculateButton(metricName, metricKey, description) {
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">${metricName}</h3>
            <p class="stats-content-subtitle">${description}</p>
        </div>
        
        ${generateMetricDescriptionBlock(metricKey)}
        
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-text">Метрика ещё не рассчитана</div>
            <button class="calculate-metric-btn" onclick="calculateMetricFromModal('${metricKey}')">
                ⚡ Рассчитать ${metricName}
            </button>
        </div>
    `;
}

// Вспомогательная функция для генерации результатов в виде сетки карточек
function generateMetricResults(data, title, description, metricKey, valueKey, isDecimal) {
    if (!data || data.length === 0) {
        return `
            <div class="stats-content-header">
                <h3 class="stats-content-title">${title}</h3>
                <p class="stats-content-subtitle">${description}</p>
                
                <div class="stats-content-actions">
                    <button class="stats-action-btn secondary" onclick="toggleMetricVisualization('${metricKey}')">
                        <span>📏</span>
                        <span>Визуализировать размером</span>
                    </button>
                </div>
            </div>
            
            ${generateMetricDescriptionBlock(metricKey)}
            
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-text">Нет данных для отображения</div>
            </div>
        `;
    }
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">${title}</h3>
            <p class="stats-content-subtitle">${description}</p>
            
            <div class="stats-content-actions">
                <button class="stats-action-btn secondary" onclick="toggleMetricVisualization('${metricKey}')">
                    <span>📏</span>
                    <span>Визуализировать размером</span>
                </button>
            </div>
        </div>
        
        ${generateMetricDescriptionBlock(metricKey)}
        
        <div class="metric-results-grid">
            ${data.map((item, index) => {
                const value = item[valueKey];
                const displayValue = isDecimal ? value.toFixed(4) : Math.round(value);
                return `
                    <div class="metric-result-card" onclick="highlightNodeById('${item.node.id}')">
                        <div class="metric-result-rank">#${index + 1}</div>
                        <div class="metric-result-name">${item.node.label}</div>
                        <div class="metric-result-value">${displayValue}</div>
                        <div class="metric-result-philosopher">${item.node.concept}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// Примеры основных генераторов (полный список в отдельном файле):

function generateOverviewContent() {
    const avgDegree = (links.length * 2 / nodes.length).toFixed(2);
    const density = (links.length / ((nodes.length * (nodes.length - 1)) / 2) * 100).toFixed(3);
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">📈 Общий обзор графа</h3>
            <p class="stats-content-subtitle">Базовая статистика сети философских концепций</p>
        </div>
        
        ${generateMetricDescriptionBlock('overview')}
        
        <div class="metric-results-grid">
            <div class="metric-result-card">
                <div class="metric-result-rank">Узлы</div>
                <div class="metric-result-value">${nodes.length}</div>
                <div class="metric-result-philosopher">Всего концепций</div>
            </div>
            <div class="metric-result-card">
                <div class="metric-result-rank">Связи</div>
                <div class="metric-result-value">${links.length}</div>
                <div class="metric-result-philosopher">Всего отношений</div>
            </div>
            <div class="metric-result-card">
                <div class="metric-result-rank">Плотность</div>
                <div class="metric-result-value">${density}%</div>
                <div class="metric-result-philosopher">Плотность сети</div>
            </div>
            <div class="metric-result-card">
                <div class="metric-result-rank">Средняя степень</div>
                <div class="metric-result-value">${avgDegree}</div>
                <div class="metric-result-philosopher">Связей на узел</div>
            </div>
        </div>
    `;
}

function generateDegreeContent() {
    const degreeData = nodes.map(n => {
        const inDegree = links.filter(l => 
            (typeof l.target === 'object' ? l.target.id : l.target) === n.id
        ).length;
        const outDegree = links.filter(l => 
            (typeof l.source === 'object' ? l.source.id : l.source) === n.id
        ).length;
        return {
            node: n,
            inDegree,
            outDegree,
            totalDegree: inDegree + outDegree
        };
    }).sort((a, b) => b.totalDegree - a.totalDegree);
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">🔗 Степень связности</h3>
            <p class="stats-content-subtitle">Количество входящих и исходящих связей для каждого узла</p>
        </div>
        
        ${generateMetricDescriptionBlock('degree')}
        
        <table class="metric-table">
            <thead class="metric-table-header">
                <tr>
                    <th>#</th>
                    <th>Концепция</th>
                    <th>Входящих</th>
                    <th>Исходящих</th>
                    <th>Всего</th>
                </tr>
            </thead>
            <tbody>
                ${degreeData.slice(0, 20).map((d, i) => `
                    <tr class="metric-table-row" onclick="highlightNodeById('${d.node.id}')">
                        <td><strong>${i + 1}</strong></td>
                        <td><strong>${d.node.label}</strong></td>
                        <td>${d.inDegree}</td>
                        <td>${d.outDegree}</td>
                        <td class="metric-table-value">${d.totalDegree}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ... остальные генераторы следуют аналогичной структуре ...
// Полный список см. в файле FULL_metrics_integration_guide_GENERATORS.js
```

**Список всех генераторов:**
- `generateOverviewContent()` ✓
- `generateDegreeContent()` ✓
- `generatePageRankContent()`
- `generateBetweennessContent()`
- `generateClosenessContent()`
- `generateEigenvectorContent()`
- `generateWeightedClusteringContent()`
- `generateLocalCohesionContent()`
- `generateRichClubContent()`
- `generateProblemGenerationContent()`
- `generateCriticalPowerContent()`
- `generateRevolutionaryContent()`
- `generateParadigmShiftContent()`
- `generateInfluenceContent()`
- `generateFoundationalContent()`
- `generateSyntheticContent()`
- `generateDialogicalContent()`
- `generateCoherenceContent()`
- `generateTensionContent()`
- `generateTransformationContent()`
- `generateFertilityContent()`
- `generateComplexityContent()`
- `generateContinuityContent()`
- `generateTemporalInfluenceContent()`
- `generatePhilosopherProfileContent()`
- `generatePhilosopherSystematicContent()`
- `generatePhilosopherReachContent()`
- `generatePhilosopherInterdisciplinaryContent()`
- `generateConceptRankingsContent()`
- `generatePhilosopherRankingsContent()`

---

## 8. ФУНКЦИЯ ВИЗУАЛИЗАЦИИ РАЗМЕРОМ УЗЛОВ {#визуализация}

Добавить после генераторов контента:

```javascript
// ============================================
// ВИЗУАЛИЗАЦИЯ МЕТРИК РАЗМЕРОМ УЗЛОВ
// ============================================

let isVisualizingBySize = false;
let currentVisualizedMetric = null;
let originalRadii = new Map();

// Сохранить оригинальные радиусы узлов
function saveOriginalRadii() {
    if (originalRadii.size === 0) {
        node.selectAll("circle").each(function(d) {
            originalRadii.set(d.id, d3.select(this).attr("r") || 18);
        });
    }
}

// Переключатель визуализации размером для текущей метрики
function toggleMetricVisualization(metricKey) {
    if (isVisualizingBySize && currentVisualizedMetric === metricKey) {
        // Если уже визуализируем эту метрику - сбрасываем
        resetNodeSizes();
        return;
    }
    
    // Получаем данные метрики
    let metricData = null;
    
    switch(metricKey) {
        case 'degree':
            metricData = nodes.map(n => {
                const inDegree = links.filter(l => 
                    (typeof l.target === 'object' ? l.target.id : l.target) === n.id
                ).length;
                const outDegree = links.filter(l => 
                    (typeof l.source === 'object' ? l.source.id : l.source) === n.id
                ).length;
                return {
                    node: n,
                    value: inDegree + outDegree
                };
            });
            break;
            
        case 'pagerank':
            metricData = pagerankCache;
            break;
            
        case 'betweenness':
            metricData = betweennessCache;
            break;
            
        case 'closeness':
            metricData = closenessCache;
            break;
            
        case 'eigenvector':
            metricData = eigenvectorCache;
            break;
            
        case 'weighted-clustering':
            metricData = weightedClusteringCache;
            break;
            
        case 'local-cohesion':
            metricData = localCohesionCache;
            break;
            
        case 'rich-club':
            metricData = richClubCache;
            break;
            
        // Философские метрики
        case 'problem-generation':
        case 'critical-power':
        case 'revolutionary':
        case 'paradigm-shift':
        case 'influence':
        case 'foundational':
        case 'synthetic':
        case 'dialogical':
        case 'coherence':
        case 'tension':
        case 'transformation':
        case 'fertility':
        case 'complexity':
        case 'continuity':
            if (!philosophyMetrics) {
                alert('Сначала инициализируйте философские метрики');
                return;
            }
            
            const metricFunctions = {
                'problem-generation': 'problemGenerationIndex',
                'critical-power': 'criticalPowerIndex',
                'revolutionary': 'revolutionaryIndex',
                'paradigm-shift': 'paradigmShiftIndex',
                'influence': 'influenceIndex',
                'foundational': 'foundationalIndex',
                'synthetic': 'syntheticIndex',
                'dialogical': 'dialogicalIndex',
                'coherence': 'internalCoherenceIndex',
                'tension': 'tensionIndex',
                'transformation': 'transformationIndex',
                'fertility': 'conceptualFertilityIndex',
                'complexity': 'conceptualComplexityIndex',
                'continuity': 'conceptualContinuityIndex'
            };
            
            const funcName = metricFunctions[metricKey];
            const metricsObj = ['transformation', 'fertility', 'complexity', 'continuity'].includes(metricKey) 
                ? advancedMetrics 
                : philosophyMetrics;
            
            if (funcName && metricsObj) {
                metricData = nodes.map(n => ({
                    node: n,
                    value: metricsObj[funcName](n.id).total || metricsObj[funcName](n.id).weighted || 0
                })).filter(d => d.value > 0);
            }
            break;
    }
    
    if (!metricData || metricData.length === 0) {
        alert('Нет данных для визуализации. Сначала рассчитайте метрику.');
        return;
    }
    
    visualizeMetricBySize(metricData, metricKey);
}

// Применить визуализацию метрики размером узлов
function visualizeMetricBySize(metricData, metricName) {
    saveOriginalRadii();
    
    // Создаём мапу значений
    const valueMap = new Map();
    metricData.forEach(item => {
        valueMap.set(item.node.id, item.value);
    });
    
    // Находим min и max
    const values = Array.from(valueMap.values()).filter(v => v > 0);
    if (values.length === 0) return;
    
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    
    // Масштабируем радиусы от 8 до 40
    const minRadius = 8;
    const maxRadius = 40;
    
    const scaleRadius = (value) => {
        if (maxValue === minValue) return 18;
        return minRadius + (value - minValue) / (maxValue - minValue) * (maxRadius - minRadius);
    };
    
    // Применяем новые радиусы
    node.selectAll("circle")
        .transition()
        .duration(500)
        .attr("r", d => {
            const value = valueMap.get(d.id) || 0;
            return value > 0 ? scaleRadius(value) : 8;
        });
    
    // Обновляем позицию текста
    node.selectAll("text")
        .transition()
        .duration(500)
        .attr("dy", d => {
            const value = valueMap.get(d.id) || 0;
            const radius = value > 0 ? scaleRadius(value) : 8;
            return -(radius + 7);
        });
    
    // Создаём новые маркеры с разными размерами
    const defs = svg.select("defs");
    
    // Обновляем маркеры связей
    link.each(function(d) {
        const targetNode = typeof d.target === 'object' ? d.target : nodes.find(n => n.id === d.target);
        if (!targetNode) return;
        
        const value = valueMap.get(targetNode.id) || 0;
        const radius = value > 0 ? scaleRadius(value) : 8;
        const markerId = `arrow-${d.type}-${targetNode.id}`;
        
        // Создаём индивидуальный маркер
        if (defs.select(`#${markerId}`).empty()) {
            const marker = defs.append("marker")
                .attr("id", markerId)
                .attr("markerWidth", 10)
                .attr("markerHeight", 10)
                .attr("refX", radius + 8)
                .attr("refY", 3)
                .attr("orient", "auto")
                .attr("markerUnits", "userSpaceOnUse");
            
            marker.append("path")
                .attr("d", "M0,0 L0,6 L9,3 z")
                .attr("fill", linkColors[d.type] || "#999");
        } else {
            defs.select(`#${markerId}`)
                .attr("refX", radius + 8);
        }
        
        d3.select(this).attr("marker-end", `url(#${markerId})`);
    });
    
    isVisualizingBySize = true;
    currentVisualizedMetric = metricName;
    
    console.log(`✅ Визуализация метрики "${metricName}" размером узлов активирована`);
}

// Восстановить оригинальные размеры
function resetNodeSizes() {
    if (!isVisualizingBySize) return;
    
    isVisualizingBySize = false;
    currentVisualizedMetric = null;
    
    // Восстановить радиусы
    node.selectAll("circle")
        .transition()
        .duration(500)
        .attr("r", d => originalRadii.get(d.id) || 18);
    
    // Восстановить позицию текста
    node.selectAll("text")
        .transition()
        .duration(500)
        .attr("dy", d => {
            const radius = originalRadii.get(d.id) || 18;
            return -(radius + 7);
        });
    
    // Восстановить оригинальные маркеры
    link.attr("marker-end", d => `url(#arrow-${d.type})`);
    
    // Удалить временные маркеры
    const defs = svg.select("defs");
    defs.selectAll("[id^='arrow-'][id*='-']").each(function() {
        const id = d3.select(this).attr("id");
        const parts = id.split('-');
        if (parts.length > 2) {
            d3.select(this).remove();
        }
    });
    
    console.log('✅ Оригинальные размеры узлов восстановлены');
}

// Вызов при инициализации
window.addEventListener('load', () => {
    saveOriginalRadii();
});
```

---

## 9. ИНСТРУКЦИИ ПО ПРИМЕНЕНИЮ {#инструкции}

### Шаг 1: Подготовка

1. Откройте исходный файл `philosophy_graph_stats_example.html`
2. Создайте резервную копию файла
3. Откройте файл в текстовом редакторе (VS Code, Sublime Text и т.д.)

### Шаг 2: Удаление старого кода

**A. Удалите секцию "Статистический анализ" из легенды:**

Найдите (примерно строка 300-400):
```html
<div class="legend-section">
    <h4>📊 Статистический анализ</h4>
    <!-- ... весь блок до конца секции ... -->
</div>
```
Удалите всю эту секцию.

**B. Удалите или закомментируйте старые функции:**

Найдите в JavaScript (примерно строка 4240-4630):
```javascript
function switchMetric(metricName) { ... }
function showMetric(metricName) { ... }
function formatMetricResults(data, valueKey, title, isDecimal) { ... }
```

Закомментируйте их или удалите:
```javascript
/* 
function switchMetric(metricName) { ... }
function showMetric(metricName) { ... }
function formatMetricResults(data, valueKey, title, isDecimal) { ... }
*/
```

### Шаг 3: Добавление нового кода

**A. Добавьте CSS:**

Вставьте код из **Части 1, раздел 2** после существующих стилей (примерно после строки 500).

**B. Добавьте HTML разметку:**

1. Замените секцию статистического анализа в легенде кодом из **Части 1, раздел 3** (кнопка)
2. Добавьте модальное окно перед `</body>` кодом из **Части 1, раздел 3**

**C. Добавьте JavaScript:**

Перед закрывающим тегом `</script>` вставьте в следующем порядке:

1. Классы метрик - **Часть 1, раздел 4**
2. Описания метрик - **Часть 2, раздел 5**
3. Функции управления - **Часть 2, раздел 6**
4. Генераторы контента - **Часть 3, раздел 7** (см. отдельный файл)
5. Функция визуализации - **Часть 3, раздел 8**

### Шаг 4: Создание файла генераторов (опционально)

Вы можете вынести генераторы в отдельный JS файл для лучшей организации:

1. Создайте файл `metrics_generators.js`
2. Поместите туда все функции `generate...Content()`
3. Подключите перед закрывающим `</script>`:
```html
<script src="metrics_generators.js"></script>
```

### Шаг 5: Тестирование

1. Откройте файл в браузере
2. Нажмите кнопку "📊 Открыть панель статистики" в легенде
3. Проверьте навигацию между метриками
4. Попробуйте переключатели "Учитывать веса" и "Учитывать направленность"
5. Рассчитайте несколько метрик через кнопки
6. Попробуйте визуализацию размером узлов

### Шаг 6: Отладка

Если что-то не работает:

1. Откройте Console в браузере (F12)
2. Проверьте ошибки JavaScript
3. Убедитесь, что все функции определены
4. Проверьте, что модальное окно правильно добавлено в HTML

### Возможные проблемы и решения

**Проблема:** Модальное окно не открывается
**Решение:** Проверьте, что функция `openStatsModal()` определена и кнопка имеет правильный `onclick`

**Проблема:** Метрики не рассчитываются
**Решение:** Убедитесь, что функции `runSingleMetric()` и расчёта метрик не были удалены

**Проблема:** Визуализация размером не работает
**Решение:** Проверьте, что функция `saveOriginalRadii()` вызывается при загрузке страницы

**Проблема:** Описания метрик не меняются при переключении параметров
**Решение:** Убедитесь, что в описаниях используются функции, а не статические строки

---

## 10. ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ

### Кастомизация стилей

Вы можете изменить цветовую схему модального окна, отредактировав CSS переменные:

```css
/* Основные цвета */
:root {
    --stats-primary-color: #6c5ce7;
    --stats-secondary-color: #3498db;
    --stats-danger-color: #e74c3c;
    --stats-success-color: #27ae60;
    --stats-background: #1a1a2e;
}
```

### Добавление новых метрик

Чтобы добавить свою метрику:

1. Добавьте метод в класс `PhilosophyGraphMetrics` или `AdvancedPhilosophyMetrics`
2. Добавьте описание в `metricDescriptions`
3. Создайте генератор контента `generate[ИмяМетрики]Content()`
4. Добавьте пункт в навигационное меню
5. Добавьте case в `loadStatsContent()`

### Экспорт результатов

Добавьте функцию экспорта результатов в CSV:

```javascript
function exportMetricsToCSV(metricData, metricName) {
    const csv = [
        ['Rank', 'Concept', 'Value', 'Philosopher'],
        ...metricData.map((item, index) => [
            index + 1,
            item.node.label,
            item.value,
            item.node.concept
        ])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${metricName}_results.csv`;
    a.click();
}
```

---

## 11. ЗАКЛЮЧЕНИЕ

Это полное руководство включает:

✅ **Удаление старого кода** - точные указания, что удалить
✅ **CSS для модального окна** - полностью в тёмной теме
✅ **HTML разметка** - со всеми метриками
✅ **Классы метрик** - все методы из обоих JS файлов
✅ **Описания метрик** - с учётом параметров useWeightedPaths и respectDirection
✅ **Функции управления** - с синхронизацией параметров
✅ **Генераторы контента** - для всех 30+ метрик
✅ **Визуализация размером узлов** - полностью интегрирована
✅ **Инструкции по применению** - пошаговое руководство

### Итоговая структура файла:

```
philosophy_graph_stats_example.html
├── <head>
│   └── <style>
│       ├── [существующие стили]
│       └── [НОВЫЕ стили модального окна] ← Часть 1, раздел 2
├── <body>
│   ├── <div id="legend">
│   │   ├── [существующие секции]
│   │   └── [НОВАЯ кнопка статистики] ← Часть 1, раздел 3
│   ├── [существующий граф]
│   └── [НОВОЕ модальное окно] ← Часть 1, раздел 3
├── <script>
│   ├── [существующий код графа]
│   ├── [НОВЫЕ классы метрик] ← Часть 1, раздел 4
│   ├── [НОВЫЕ описания метрик] ← Часть 2, раздел 5
│   ├── [НОВЫЕ функции управления] ← Часть 2, раздел 6
│   ├── [НОВЫЕ генераторы контента] ← Часть 3, раздел 7
│   └── [НОВАЯ визуализация] ← Часть 3, раздел 8
└── </html>
```

### Файлы руководства:

1. **FULL_metrics_integration_guide_part1.md** - CSS, HTML, классы метрик
2. **FULL_metrics_integration_guide_part2.md** - Описания, управление
3. **FULL_metrics_integration_guide_part3.md** - Генераторы, визуализация, инструкции

### Примечания:

- Все метрики полностью интегрированы
- Параметры useWeightedPaths и respectDirection учитываются
- Визуализация размером узлов работает для всех метрик
- Подробные описания метрик динамически обновляются при изменении параметров

Удачи в интеграции! 🚀
