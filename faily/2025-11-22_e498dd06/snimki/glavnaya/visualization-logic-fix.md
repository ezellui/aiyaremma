# ИСПРАВЛЕНИЕ: Логика работы кнопок визуализации

## 🔍 Анализ проблем

### Проблема 1: Кнопка сброса появляется не вовремя
**Причина:** Функция `updateVisualizationControlSection()` не вызывается при включении визуализации, только при сбросе

### Проблема 2: Название метрики не отображается
**Причина:** Неполный словарь имен метрик в функции `updateVisualizationControlSection()`

### Проблема 3: Текст кнопки в окне статистики не меняется
**Причина:** Функция `updateVisualizationButtonText()` работает, но нужно убедиться, что она вызывается правильно

---

## 🔧 ИСПРАВЛЕНИЕ 1: Правильный порядок вызовов

### Исправить функцию visualizeMetricBySize

Найдите конец функции `visualizeMetricBySize()` (строка ~5016):

```javascript
// СТАРЫЙ КОД
isVisualizingBySize = true;
currentVisualizedMetric = metricName;

updateVisualizationButtonText(metricName);

console.log(`✅ Визуализация метрики "${metricName}" размером узлов активирована`);
```

**ЗАМЕНИТЬ на:**

```javascript
isVisualizingBySize = true;
currentVisualizedMetric = metricName;

// Обновляем кнопку в окне статистики
updateVisualizationButtonText(metricName);

// Обновляем секцию в легенде
updateVisualizationControlSection();

console.log(`✅ Визуализация метрики "${metricName}" размером узлов активирована`);
```

---

## 🔧 ИСПРАВЛЕНИЕ 2: Исправить функцию resetNodeSizes

Найдите функцию `resetNodeSizes()` (строка ~5020):

```javascript
// СТАРЫЙ КОД
function resetNodeSizes() {
    if (!isVisualizingBySize) return;
    
    const metricToUpdate = currentVisualizedMetric; // СОХРАНИТЬ ДО СБРОСА
    
    isVisualizingBySize = false;
    currentVisualizedMetric = null;
    
    // ... код восстановления ...
    
    // Обновить кнопку
    if (metricToUpdate) {
        updateVisualizationButtonText(metricToUpdate);
    }
    
    console.log('✅ Оригинальные размеры узлов восстановлены');
}
```

**ЗАМЕНИТЬ на:**

```javascript
function resetNodeSizes() {
    if (!isVisualizingBySize) return;
    
    const metricToUpdate = currentVisualizedMetric; // СОХРАНИТЬ ДО СБРОСА
    
    isVisualizingBySize = false;
    currentVisualizedMetric = null;
    
    // Восстановить радиусы
    node.selectAll("circle")
        .transition()
        .duration(500)
        .attr("r", d => originalRadii.get(d.id) || 18);
    
    // Восстановить позицию текста (используем сохраненные значения)
    node.selectAll("text")
        .transition()
        .duration(500)
        .attr("dy", d => {
            const originalDy = originalTextDy.get(d.id) || -25;
            return originalDy;
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
    
    // ВАЖНО: Обновить интерфейс ПОСЛЕ сброса флагов
    if (metricToUpdate) {
        updateVisualizationButtonText(metricToUpdate);
    }
    
    // Скрыть секцию в легенде
    updateVisualizationControlSection();
    
    console.log('✅ Оригинальные размеры узлов восстановлены');
}
```

---

## 🔧 ИСПРАВЛЕНИЕ 3: Расширить словарь имен метрик

Найдите функцию `updateVisualizationControlSection()`:

```javascript
// СТАРЫЙ КОД
const metricNames = {
    'pagerank': 'PageRank',
    'betweenness': 'Betweenness',
    'closeness': 'Closeness',
    'eigenvector': 'Eigenvector',
    'degree': 'Степень связности',
    'weighted-clustering': 'Взвешенная кластеризация',
    'local-cohesion': 'Локальная когезия',
    'rich-club': 'Rich-Club'
};
```

**ЗАМЕНИТЬ на ПОЛНЫЙ словарь:**

```javascript
const metricNames = {
    // Базовые метрики
    'overview': 'Общий обзор',
    'degree': 'Степень связности',
    'pagerank': 'PageRank',
    'betweenness': 'Betweenness Centrality',
    'closeness': 'Closeness Centrality',
    'eigenvector': 'Eigenvector Centrality',
    'weighted-clustering': 'Взвешенная кластеризация',
    'local-cohesion': 'Локальная когезия',
    'rich-club': 'Rich-Club коэффициент',
    
    // Философские метрики
    'problem-generation': 'Индекс проблемности',
    'critical-power': 'Критическая сила',
    'revolutionary': 'Индекс революционности',
    'paradigm-shift': 'Парадигмальный сдвиг',
    'influence': 'Индекс влияния',
    'foundational': 'Индекс основополагания',
    'synthetic': 'Индекс синтетичности',
    'dialogical': 'Индекс диалогичности',
    'coherence': 'Внутренняя когерентность',
    'tension': 'Индекс напряжения',
    
    // Продвинутые метрики
    'transformation': 'Индекс трансформации',
    'fertility': 'Концептуальная плодовитость',
    'complexity': 'Концептуальная сложность',
    'continuity': 'Индекс преемственности',
    'temporal-influence': 'Временное влияние'
};
```

---

## 🔧 ИСПРАВЛЕНИЕ 4: Улучшить функцию updateVisualizationButtonText

Найдите функцию `updateVisualizationButtonText()`:

```javascript
// СТАРЫЙ КОД
function updateVisualizationButtonText(metricKey) {
    const iconElement = document.getElementById(`visualize-icon-${metricKey}`);
    const textElement = document.getElementById(`visualize-text-${metricKey}`);
    
    if (!iconElement || !textElement) return;
    
    if (isVisualizingBySize && currentVisualizedMetric === metricKey) {
        // Визуализация активна
        iconElement.textContent = '🔄';
        textElement.textContent = 'Сбросить визуализацию';
    } else {
        // Визуализация неактивна
        iconElement.textContent = '📏';
        textElement.textContent = 'Визуализировать размером';
    }
}
```

**ЗАМЕНИТЬ на улучшенную версию с логированием:**

```javascript
// Обновить текст кнопки визуализации
function updateVisualizationButtonText(metricKey) {
    const iconElement = document.getElementById(`visualize-icon-${metricKey}`);
    const textElement = document.getElementById(`visualize-text-${metricKey}`);
    
    if (!iconElement || !textElement) {
        console.warn(`⚠️ Элементы кнопки для метрики "${metricKey}" не найдены`);
        return;
    }
    
    if (isVisualizingBySize && currentVisualizedMetric === metricKey) {
        // Визуализация активна для ЭТОЙ метрики
        iconElement.textContent = '🔄';
        textElement.textContent = 'Сбросить визуализацию';
        console.log(`🔄 Кнопка метрики "${metricKey}" → "Сбросить"`);
    } else {
        // Визуализация неактивна ИЛИ активна для другой метрики
        iconElement.textContent = '📏';
        textElement.textContent = 'Визуализировать размером';
        console.log(`📏 Кнопка метрики "${metricKey}" → "Визуализировать"`);
    }
}
```

---

## 🔧 ИСПРАВЛЕНИЕ 5: Улучшить функцию updateVisualizationControlSection

Найдите функцию `updateVisualizationControlSection()`:

```javascript
// СТАРЫЙ КОД
function updateVisualizationControlSection() {
    const section = document.getElementById('visualizationControlSection');
    const metricLabel = document.getElementById('currentVisualizationMetric');
    
    if (!section) return; // Если секции нет в HTML
    
    if (isVisualizingBySize && currentVisualizedMetric) {
        section.style.display = 'block';
        if (metricLabel) {
            const metricNames = { /* ... */ };
            metricLabel.textContent = metricNames[currentVisualizedMetric] || currentVisualizedMetric;
        }
    } else {
        section.style.display = 'none';
    }
}
```

**ЗАМЕНИТЬ на улучшенную версию:**

```javascript
// Показать/скрыть секцию управления визуализацией в легенде
function updateVisualizationControlSection() {
    const section = document.getElementById('visualizationControlSection');
    const metricLabel = document.getElementById('currentVisualizationMetric');
    
    if (!section) {
        console.warn('⚠️ Секция visualizationControlSection не найдена в HTML');
        return;
    }
    
    if (isVisualizingBySize && currentVisualizedMetric) {
        // Визуализация активна - показываем секцию
        section.style.display = 'block';
        
        if (metricLabel) {
            // ПОЛНЫЙ словарь имен метрик
            const metricNames = {
                // Базовые метрики
                'overview': 'Общий обзор',
                'degree': 'Степень связности',
                'pagerank': 'PageRank',
                'betweenness': 'Betweenness Centrality',
                'closeness': 'Closeness Centrality',
                'eigenvector': 'Eigenvector Centrality',
                'weighted-clustering': 'Взвешенная кластеризация',
                'local-cohesion': 'Локальная когезия',
                'rich-club': 'Rich-Club коэффициент',
                
                // Философские метрики
                'problem-generation': 'Индекс проблемности',
                'critical-power': 'Критическая сила',
                'revolutionary': 'Индекс революционности',
                'paradigm-shift': 'Парадигмальный сдвиг',
                'influence': 'Индекс влияния',
                'foundational': 'Индекс основополагания',
                'synthetic': 'Индекс синтетичности',
                'dialogical': 'Индекс диалогичности',
                'coherence': 'Внутренняя когерентность',
                'tension': 'Индекс напряжения',
                
                // Продвинутые метрики
                'transformation': 'Индекс трансформации',
                'fertility': 'Концептуальная плодовитость',
                'complexity': 'Концептуальная сложность',
                'continuity': 'Индекс преемственности',
                'temporal-influence': 'Временное влияние'
            };
            
            const metricName = metricNames[currentVisualizedMetric] || currentVisualizedMetric;
            metricLabel.textContent = metricName;
            
            console.log(`✅ Секция легенды показана: "${metricName}"`);
        }
    } else {
        // Визуализация неактивна - скрываем секцию
        section.style.display = 'none';
        console.log(`🔽 Секция легенды скрыта`);
    }
}
```

---

## 🔧 ИСПРАВЛЕНИЕ 6: Убедиться в правильности HTML кнопки в легенде

Проверьте, что в HTML легенды есть такая секция:

```html
<!-- В легенде, после других секций -->
<div class="legend-section" id="visualizationControlSection" style="display: none;">
    <h4>🎨 Визуализация метрик</h4>
    <div style="background: rgba(108, 92, 231, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
        <div style="color: #fff; font-size: 12px; margin-bottom: 8px;">
            Активна: <strong id="currentVisualizationMetric">-</strong>
        </div>
        <button class="legend-button" onclick="resetNodeSizes()" style="width: 100%; background: linear-gradient(135deg, #e74c3c, #c0392b); border: none; padding: 10px; border-radius: 8px; color: white; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
            🔄 Сбросить визуализацию
        </button>
    </div>
</div>
```

**ВАЖНО:** Убедитесь, что:
1. `id="visualizationControlSection"` - правильный ID
2. `id="currentVisualizationMetric"` - правильный ID для текста метрики
3. `style="display: none;"` - изначально скрыта
4. `onclick="resetNodeSizes()"` - правильный обработчик

---

## 🔧 ИСПРАВЛЕНИЕ 7: Обновление всех кнопок при переключении метрик

Добавьте функцию для обновления ВСЕХ кнопок визуализации:

```javascript
// Обновить все кнопки визуализации
function updateAllVisualizationButtons() {
    // Список всех возможных метрик
    const allMetrics = [
        'degree', 'pagerank', 'betweenness', 'closeness', 'eigenvector',
        'weighted-clustering', 'local-cohesion', 'rich-club',
        'problem-generation', 'critical-power', 'revolutionary', 'paradigm-shift',
        'influence', 'foundational', 'synthetic', 'dialogical', 'coherence', 'tension',
        'transformation', 'fertility', 'complexity', 'continuity', 'temporal-influence'
    ];
    
    allMetrics.forEach(metric => {
        updateVisualizationButtonText(metric);
    });
    
    console.log('🔄 Все кнопки визуализации обновлены');
}
```

И вызывайте её в конце `visualizeMetricBySize()` и `resetNodeSizes()`:

```javascript
// В конце visualizeMetricBySize()
isVisualizingBySize = true;
currentVisualizedMetric = metricName;

// Обновляем все кнопки
updateAllVisualizationButtons();

// Обновляем секцию в легенде
updateVisualizationControlSection();

console.log(`✅ Визуализация метрики "${metricName}" размером узлов активирована`);
```

```javascript
// В конце resetNodeSizes()
if (metricToUpdate) {
    // Обновляем все кнопки
    updateAllVisualizationButtons();
}

// Скрыть секцию в легенде
updateVisualizationControlSection();

console.log('✅ Оригинальные размеры узлов восстановлены');
```

---

## 📋 Проверка логики работы

### Сценарий 1: Включение визуализации

1. Пользователь нажимает "Визуализировать размером" для метрики A
2. `toggleMetricVisualization('A')` вызывается
3. `visualizeMetricBySize(data, 'A')` выполняется:
   - `isVisualizingBySize = true`
   - `currentVisualizedMetric = 'A'`
   - `updateAllVisualizationButtons()` → все кнопки обновляются, кнопка A становится "Сбросить"
   - `updateVisualizationControlSection()` → секция в легенде **ПОКАЗЫВАЕТСЯ** с текстом метрики A
4. Модальное окно закрывается (если было открыто)

**Ожидаемый результат:**
- ✅ Визуализация активна
- ✅ Кнопка метрики A: "🔄 Сбросить визуализацию"
- ✅ Кнопка в легенде ВИДНА с текстом "PageRank" (или другое имя)
- ✅ Окно статистики закрыто

### Сценарий 2: Сброс визуализации

1. Пользователь нажимает "Сбросить визуализацию" (или кнопку в легенде)
2. `toggleMetricVisualization('A')` вызывается
3. Проверка: `isVisualizingBySize && currentVisualizedMetric === 'A'` → true
4. `resetNodeSizes()` выполняется:
   - Сохраняется `metricToUpdate = 'A'`
   - `isVisualizingBySize = false`
   - `currentVisualizedMetric = null`
   - Восстанавливаются размеры и позиции
   - `updateAllVisualizationButtons()` → все кнопки становятся "Визуализировать"
   - `updateVisualizationControlSection()` → секция в легенде **СКРЫВАЕТСЯ**

**Ожидаемый результат:**
- ✅ Визуализация отключена
- ✅ Все кнопки: "📏 Визуализировать размером"
- ✅ Кнопка в легенде СКРЫТА

### Сценарий 3: Переключение метрик

1. Визуализация метрики A активна
2. Пользователь открывает окно статистики и нажимает "Визуализировать" для метрики B
3. `toggleMetricVisualization('B')` вызывается
4. Проверка: `isVisualizingBySize && currentVisualizedMetric === 'B'` → false (currentVisualizedMetric === 'A')
5. Визуализация метрики B применяется:
   - `currentVisualizedMetric = 'B'`
   - Кнопка A становится "Визуализировать"
   - Кнопка B становится "Сбросить"
   - Секция в легенде обновляется на метрику B

---

## ✅ Финальная проверка

После применения всех исправлений:

### Тест 1: Первое включение
- [ ] Открыть окно статистики
- [ ] Нажать "Визуализировать размером" для любой метрики
- [ ] Окно должно закрыться
- [ ] Визуализация должна появиться
- [ ] В легенде должна ПОЯВИТЬСЯ кнопка с названием метрики
- [ ] При открытии окна статистики кнопка должна быть "🔄 Сбросить визуализацию"

### Тест 2: Сброс через окно статистики
- [ ] При активной визуализации открыть окно
- [ ] Нажать кнопку "Сбросить визуализацию"
- [ ] Визуализация должна сброситься
- [ ] Кнопка в легенде должна ИСЧЕЗНУТЬ
- [ ] Кнопка в окне должна стать "📏 Визуализировать размером"

### Тест 3: Сброс через легенду
- [ ] При активной визуализации (окно закрыто)
- [ ] Нажать кнопку "Сбросить визуализацию" в легенде
- [ ] Визуализация должна сброситься
- [ ] Кнопка в легенде должна ИСЧЕЗНУТЬ

### Тест 4: Переключение метрик
- [ ] Включить визуализацию метрики A
- [ ] Открыть окно, включить визуализацию метрики B
- [ ] Кнопка A должна стать "Визуализировать"
- [ ] Кнопка B должна стать "Сбросить"
- [ ] Кнопка в легенде должна показывать метрику B

---

## 🐛 Отладка через консоль

После применения исправлений, в консоли браузера вы должны видеть:

```
// При включении визуализации
📊 Статистика метрики "pagerank": ...
🔍 Малая дисперсия (CV=0.15), применяем степенное усиление
📏 Кнопка метрики "pagerank" → "Сбросить"
🔄 Все кнопки визуализации обновлены
✅ Секция легенды показана: "PageRank"
✅ Визуализация метрики "pagerank" размером узлов активирована

// При сбросе
📏 Кнопка метрики "pagerank" → "Визуализировать"
🔄 Все кнопки визуализации обновлены
🔽 Секция легенды скрыта
✅ Оригинальные размеры узлов восстановлены
```

Если какие-то сообщения не появляются или появляются не в том порядке - это указывает на проблему в коде.

---

## 📝 Краткая сводка изменений

| Что | Где | Зачем |
|-----|-----|-------|
| Добавить вызов `updateVisualizationControlSection()` | В конце `visualizeMetricBySize()` | Показать кнопку в легенде |
| Добавить вызов `updateVisualizationControlSection()` | В конце `resetNodeSizes()` | Скрыть кнопку в легенде |
| Расширить словарь метрик | В `updateVisualizationControlSection()` | Показывать все имена метрик |
| Добавить логирование | В `updateVisualizationButtonText()` | Отладка |
| Улучшить `updateVisualizationControlSection()` | Весь код функции | Логирование + полный словарь |
| Добавить `updateAllVisualizationButtons()` | Новая функция | Обновление всех кнопок сразу |
| Вызывать `updateAllVisualizationButtons()` | В обеих функциях | Синхронизация состояния |

---

## 🎯 Ожидаемое поведение после исправлений

1. **Первое нажатие "Визуализировать":**
   - Окно закрывается ✅
   - Визуализация включается ✅
   - Кнопка в легенде ПОЯВЛЯЕТСЯ с названием метрики ✅
   - Кнопка в окне становится "Сбросить" ✅

2. **Повторное нажатие (на ту же кнопку):**
   - Визуализация СБРАСЫВАЕТСЯ ✅
   - Кнопка в легенде ИСЧЕЗАЕТ ✅
   - Кнопка в окне становится "Визуализировать" ✅

3. **Нажатие кнопки в легенде:**
   - Визуализация СБРАСЫВАЕТСЯ ✅
   - Кнопка в легенде ИСЧЕЗАЕТ ✅
   - Кнопки в окне становятся "Визуализировать" ✅

Всё должно работать логично и предсказуемо! 🚀
