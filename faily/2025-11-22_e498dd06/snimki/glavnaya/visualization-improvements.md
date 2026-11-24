# УЛУЧШЕНИЯ ВИЗУАЛИЗАЦИИ МЕТРИК РАЗМЕРОМ УЗЛОВ

## 📋 Обзор проблем и решений

### Проблема 1: Малая дисперсия метрик делает визуализацию неинформативной
**Решение:** Адаптивное масштабирование с усилением контраста при малой дисперсии

### Проблема 2: Позиция текста не восстанавливается при сбросе визуализации
**Решение:** Сохранение и восстановление исходных значений dy

### Проблема 3: Плохой UX - окно не закрывается, кнопка не меняется
**Решение:** Автоматическое закрытие окна, динамический текст кнопки, кнопка сброса в легенде

---

## 🔧 ИСПРАВЛЕНИЕ 1: Адаптивное масштабирование с учетом дисперсии

### Найти функцию visualizeMetricBySize (строка ~4935)

Найдите код масштабирования радиусов (строки ~4951-4958):

```javascript
// СТАРЫЙ КОД (найти и заменить)
// Масштабируем радиусы от 8 до 40
const minRadius = 8;
const maxRadius = 40;

const scaleRadius = (value) => {
    if (maxValue === minValue) return 18;
    return minRadius + (value - minValue) / (maxValue - minValue) * (maxRadius - minRadius);
};
```

### ЗАМЕНИТЬ на улучшенную версию:

```javascript
// ============================================
// УЛУЧШЕННОЕ МАСШТАБИРОВАНИЕ с учетом дисперсии
// ============================================

// Вычисляем статистику для определения дисперсии
const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
const stdDev = Math.sqrt(variance);
const coefficientOfVariation = stdDev / mean; // Коэффициент вариации

console.log(`📊 Статистика метрики "${metricName}":`, {
    min: minValue.toFixed(4),
    max: maxValue.toFixed(4),
    mean: mean.toFixed(4),
    stdDev: stdDev.toFixed(4),
    cv: coefficientOfVariation.toFixed(4)
});

// Масштабируем радиусы от 8 до 40
const minRadius = 8;
const maxRadius = 40;

// Функция масштабирования с адаптацией к дисперсии
const scaleRadius = (value) => {
    if (maxValue === minValue) return 18;
    
    // Нормализуем значение в диапазон [0, 1]
    const normalized = (value - minValue) / (maxValue - minValue);
    
    // Выбираем стратегию масштабирования в зависимости от коэффициента вариации
    let scaled;
    
    if (coefficientOfVariation < 0.2) {
        // МАЛАЯ ДИСПЕРСИЯ: используем степенное усиление контраста
        // Усиливаем различия между значениями
        const power = 2.5; // Увеличиваем контраст
        scaled = Math.pow(normalized, 1 / power); // Обратная степень для усиления малых различий
        
        console.log(`🔍 Малая дисперсия (CV=${coefficientOfVariation.toFixed(3)}), применяем степенное усиление`);
    } else if (coefficientOfVariation > 1.5) {
        // БОЛЬШАЯ ДИСПЕРСИЯ: используем логарифмическое сжатие
        // Сжимаем большие различия для лучшей читаемости
        const logBase = 10;
        scaled = Math.log(1 + normalized * (logBase - 1)) / Math.log(logBase);
        
        console.log(`📉 Большая дисперсия (CV=${coefficientOfVariation.toFixed(3)}), применяем логарифмическое сжатие`);
    } else {
        // СРЕДНЯЯ ДИСПЕРСИЯ: используем слегка усиленное линейное масштабирование
        const power = 1.5;
        scaled = Math.pow(normalized, 1 / power);
        
        console.log(`📊 Средняя дисперсия (CV=${coefficientOfVariation.toFixed(3)}), применяем умеренное усиление`);
    }
    
    return minRadius + scaled * (maxRadius - minRadius);
};
```

**Что изменилось:**
- ✅ Вычисляется коэффициент вариации (CV) для определения степени разброса данных
- ✅ При CV < 0.2 (малая дисперсия) применяется степенное усиление контраста
- ✅ При CV > 1.5 (большая дисперсия) применяется логарифмическое сжатие
- ✅ При средней дисперсии применяется умеренное усиление
- ✅ Логирование статистики для отладки

---

## 🔧 ИСПРАВЛЕНИЕ 2: Сохранение и восстановление позиции текста

### Часть 2.1: Обновить хранилище исходных данных

Найдите объявление переменных (строка ~4809):

```javascript
// СТАРЫЙ КОД
let isVisualizingBySize = false;
let currentVisualizedMetric = null;
let originalRadii = new Map();
```

**ЗАМЕНИТЬ на:**

```javascript
// Переменные для визуализации метрик
let isVisualizingBySize = false;
let currentVisualizedMetric = null;
let originalRadii = new Map();
let originalTextDy = new Map(); // ДОБАВЛЕНО: сохранение исходных dy текста
```

### Часть 2.2: Обновить функцию saveOriginalRadii

Найдите функцию `saveOriginalRadii()` (строка ~4814):

```javascript
// СТАРЫЙ КОД
function saveOriginalRadii() {
    if (originalRadii.size === 0) {
        node.selectAll("circle").each(function(d) {
            originalRadii.set(d.id, d3.select(this).attr("r") || 18);
        });
    }
}
```

**ЗАМЕНИТЬ на:**

```javascript
// Сохранить оригинальные радиусы узлов и позиции текста
function saveOriginalRadii() {
    if (originalRadii.size === 0) {
        // Сохраняем радиусы кругов
        node.selectAll("circle").each(function(d) {
            const radius = parseFloat(d3.select(this).attr("r")) || 18;
            originalRadii.set(d.id, radius);
        });
        
        // Сохраняем позиции текста (dy)
        node.selectAll("text").each(function(d) {
            const dy = parseFloat(d3.select(this).attr("dy")) || -25;
            originalTextDy.set(d.id, dy);
        });
        
        console.log(`💾 Сохранены исходные параметры для ${originalRadii.size} узлов`);
    }
}
```

### Часть 2.3: Обновить функцию resetNodeSizes

Найдите функцию `resetNodeSizes()` (строка ~5020):

Найдите секцию восстановления позиции текста (строки ~5032-5039):

```javascript
// СТАРЫЙ КОД
// Восстановить позицию текста
node.selectAll("text")
    .transition()
    .duration(500)
    .attr("dy", d => {
        const radius = originalRadii.get(d.id) || 18;
        return -(radius + 7);
    });
```

**ЗАМЕНИТЬ на:**

```javascript
// Восстановить позицию текста (используем сохраненные значения)
node.selectAll("text")
    .transition()
    .duration(500)
    .attr("dy", d => {
        const originalDy = originalTextDy.get(d.id) || -25;
        return originalDy;
    });
```

---

## 🔧 ИСПРАВЛЕНИЕ 3: Улучшение UX визуализации

### Часть 3.1: Автоматическое закрытие модального окна

Найдите функцию `toggleMetricVisualization()` (строка ~4823):

В начале функции, после проверки на сброс, **ДОБАВИТЬ**:

```javascript
function toggleMetricVisualization(metricKey) {
    if (isVisualizingBySize && currentVisualizedMetric === metricKey) {
        // Если уже визуализируем эту метрику - сбрасываем
        resetNodeSizes();
        return;
    }
    
    // ============================================
    // ДОБАВЛЕНО: Закрываем модальное окно перед визуализацией
    // ============================================
    if (isStatsModalOpen) {
        closeStatsModal();
        console.log('🔽 Модальное окно закрыто для визуализации');
    }
    
    // Получаем данные метрики
    let metricData = null;
    // ... остальной код
```

### Часть 3.2: Динамический текст кнопки визуализации

Найдите функцию `generateMetricResults()` (строка ~3827), в которой генерируется кнопка визуализации.

Найдите эту секцию (около строки 3835-3839):

```javascript
// СТАРЫЙ КОД
<div class="stats-content-actions">
    <button class="stats-action-btn secondary" onclick="toggleMetricVisualization('${metricKey}')">
        <span>📏</span>
        <span>Визуализировать размером</span>
    </button>
</div>
```

**ЗАМЕНИТЬ на:**

```javascript
<div class="stats-content-actions">
    <button class="stats-action-btn secondary" 
            id="visualize-btn-${metricKey}"
            onclick="toggleMetricVisualization('${metricKey}')">
        <span id="visualize-icon-${metricKey}">📏</span>
        <span id="visualize-text-${metricKey}">Визуализировать размером</span>
    </button>
</div>
```

Также в блоке с результатами (около строки 3857):

```javascript
// СТАРЫЙ КОД (найти и заменить аналогично)
<div class="stats-content-actions">
    <button class="stats-action-btn secondary" onclick="toggleMetricVisualization('${metricKey}')">
        <span>📏</span>
        <span>Визуализировать размером</span>
    </button>
</div>
```

**ЗАМЕНИТЬ на:**

```javascript
<div class="stats-content-actions">
    <button class="stats-action-btn secondary" 
            id="visualize-btn-${metricKey}"
            onclick="toggleMetricVisualization('${metricKey}')">
        <span id="visualize-icon-${metricKey}">📏</span>
        <span id="visualize-text-${metricKey}">Визуализировать размером</span>
    </button>
</div>
```

### Часть 3.3: Функция обновления текста кнопки

**ДОБАВИТЬ** новую функцию после `toggleMetricVisualization()` (около строки 4930):

```javascript
// Обновить текст кнопки визуализации
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

### Часть 3.4: Вызов обновления кнопки в visualizeMetricBySize

В конце функции `visualizeMetricBySize()` (около строки 5016) **ДОБАВИТЬ**:

```javascript
isVisualizingBySize = true;
currentVisualizedMetric = metricName;

// ДОБАВИТЬ:
updateVisualizationButtonText(metricName);

console.log(`✅ Визуализация метрики "${metricName}" размером узлов активирована`);
```

### Часть 3.5: Вызов обновления кнопки в resetNodeSizes

В конце функции `resetNodeSizes()` (около строки 5054) **ДОБАВИТЬ**:

```javascript
isVisualizingBySize = false;
currentVisualizedMetric = null;

// Восстановить радиусы
// ... код ...

// ДОБАВИТЬ в конце, перед console.log:
const oldMetric = currentVisualizedMetric;
if (oldMetric) {
    updateVisualizationButtonText(oldMetric);
}

console.log('✅ Оригинальные размеры узлов восстановлены');
```

**ВАЖНО:** Нужно сохранить `currentVisualizedMetric` ДО того, как установить его в `null`:

```javascript
// Правильная последовательность
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

### Часть 3.6: Добавить кнопку сброса в легенду (опционально)

Можно добавить отдельную кнопку сброса в легенде, которая будет видна всегда.

В HTML-разметке легенды (это нужно искать в основном HTML, не в stats.html фрагменте), добавить:

```html
<!-- В легенде, после других кнопок управления -->
<div class="legend-section" id="visualizationControlSection" style="display: none;">
    <h4>🎨 Визуализация метрик</h4>
    <div style="background: rgba(108, 92, 231, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
        <div style="color: #fff; font-size: 12px; margin-bottom: 8px;">
            Активна: <strong id="currentVisualizationMetric">-</strong>
        </div>
        <button class="legend-button" onclick="resetNodeSizes()" style="width: 100%;">
            🔄 Сбросить визуализацию
        </button>
    </div>
</div>
```

И добавить функцию для показа/скрытия этой секции:

```javascript
// Показать/скрыть секцию управления визуализацией в легенде
function updateVisualizationControlSection() {
    const section = document.getElementById('visualizationControlSection');
    const metricLabel = document.getElementById('currentVisualizationMetric');
    
    if (!section) return; // Если секции нет в HTML
    
    if (isVisualizingBySize && currentVisualizedMetric) {
        section.style.display = 'block';
        if (metricLabel) {
            // Получаем читаемое имя метрики
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
            metricLabel.textContent = metricNames[currentVisualizedMetric] || currentVisualizedMetric;
        }
    } else {
        section.style.display = 'none';
    }
}
```

Вызывать эту функцию в `visualizeMetricBySize()` и `resetNodeSizes()`.

---

## 📊 Сводная таблица изменений

| Файл/Место | Что делать | Сложность |
|------------|-----------|-----------|
| `visualizeMetricBySize()` ~4951 | Заменить масштабирование | Средняя |
| Переменные ~4809 | Добавить `originalTextDy` | Легко |
| `saveOriginalRadii()` ~4814 | Добавить сохранение dy | Легко |
| `resetNodeSizes()` ~5032 | Использовать сохраненные dy | Легко |
| `toggleMetricVisualization()` ~4823 | Добавить закрытие окна | Легко |
| `generateMetricResults()` ~3835 | Добавить id к кнопкам | Средняя |
| Новая функция | Добавить `updateVisualizationButtonText()` | Легко |
| `visualizeMetricBySize()` ~5016 | Вызов обновления кнопки | Легко |
| `resetNodeSizes()` ~5054 | Вызов обновления кнопки | Легко |

---

## ✅ Проверка после применения

### Проверка 1: Улучшенное масштабирование
- [ ] Откройте консоль браузера
- [ ] Визуализируйте разные метрики
- [ ] Проверьте логи: должны появляться сообщения о типе дисперсии
- [ ] Метрики с малой дисперсией теперь визуально различимы

### Проверка 2: Восстановление позиции текста
- [ ] Включите визуализацию любой метрики
- [ ] Обратите внимание на позиции подписей узлов
- [ ] Сбросьте визуализацию
- [ ] Подписи должны вернуться точно на исходные позиции

### Проверка 3: Улучшенный UX
- [ ] Нажмите кнопку "Визуализировать размером"
- [ ] Модальное окно должно автоматически закрыться
- [ ] Визуализация должна быть видна на графе
- [ ] Откройте окно статистики снова
- [ ] Текст кнопки изменился на "Сбросить визуализацию" с иконкой 🔄
- [ ] Нажмите кнопку - визуализация сбросится, текст вернется к "Визуализировать размером" 📏

---

## 🎯 Примеры поведения по метрикам

### Метрики с малой дисперсией (CV < 0.2)
**Примеры:** Closeness Centrality, некоторые философские метрики

**До исправления:**
- Все узлы почти одинакового размера
- Невозможно различить различия

**После исправления:**
- Степенное усиление контраста (power = 2.5)
- Даже малые различия становятся визуально заметными
- Логирование: `🔍 Малая дисперсия (CV=0.15), применяем степенное усиление`

### Метрики со средней дисперсией (0.2 <= CV <= 1.5)
**Примеры:** PageRank, Degree

**Поведение:**
- Умеренное усиление (power = 1.5)
- Естественное распределение размеров
- Логирование: `📊 Средняя дисперсия (CV=0.8), применяем умеренное усиление`

### Метрики с большой дисперсией (CV > 1.5)
**Примеры:** Betweenness, некоторые философские метрики

**До исправления:**
- Несколько огромных узлов
- Множество крошечных узлов
- Плохая читаемость

**После исправления:**
- Логарифмическое сжатие
- Большие узлы немного уменьшаются
- Малые узлы становятся более заметными
- Логирование: `📉 Большая дисперсия (CV=2.3), применяем логарифмическое сжатие`

---

## 💡 Дополнительные рекомендации

### Настройка параметров масштабирования

Если вам нужно настроить пороги или силу преобразований, измените эти значения:

```javascript
// В функции scaleRadius внутри visualizeMetricBySize

// Пороги коэффициента вариации
const LOW_CV_THRESHOLD = 0.2;   // Порог малой дисперсии
const HIGH_CV_THRESHOLD = 1.5;  // Порог большой дисперсии

// Сила преобразований
const LOW_CV_POWER = 2.5;       // Усиление при малой дисперсии (больше = сильнее)
const MID_CV_POWER = 1.5;       // Усиление при средней дисперсии
const HIGH_CV_LOG_BASE = 10;    // База логарифма при большой дисперсии

if (coefficientOfVariation < LOW_CV_THRESHOLD) {
    scaled = Math.pow(normalized, 1 / LOW_CV_POWER);
} else if (coefficientOfVariation > HIGH_CV_THRESHOLD) {
    scaled = Math.log(1 + normalized * (HIGH_CV_LOG_BASE - 1)) / Math.log(HIGH_CV_LOG_BASE);
} else {
    scaled = Math.pow(normalized, 1 / MID_CV_POWER);
}
```

### Альтернативные стратегии масштабирования

Можно использовать другие функции преобразования:

```javascript
// Сигмоидальное преобразование (S-образная кривая)
const sigmoid = (x) => 1 / (1 + Math.exp(-10 * (x - 0.5)));
scaled = sigmoid(normalized);

// Кубический корень (мягче чем квадратный)
scaled = Math.pow(normalized, 1/3);

// Арктангенс (очень мягкое сжатие экстремумов)
scaled = Math.atan(normalized * Math.PI) / (Math.PI / 2);
```

---

## 🚀 Результат после всех улучшений

✅ **Визуализация информативна** для любых метрик, независимо от дисперсии
✅ **Позиция текста корректно восстанавливается** при сбросе
✅ **Удобный UX**: окно закрывается, кнопка меняется динамически
✅ **Профессиональный вид**: плавные анимации и понятные индикаторы
✅ **Отладка упрощена**: логирование статистики метрик в консоль

---

## 📝 Порядок применения

1. ✅ Исправление 1: Адаптивное масштабирование (~10 строк замены)
2. ✅ Исправление 2.1: Добавить `originalTextDy` (1 строка)
3. ✅ Исправление 2.2: Обновить `saveOriginalRadii()` (~10 строк)
4. ✅ Исправление 2.3: Обновить восстановление текста в `resetNodeSizes()` (~5 строк)
5. ✅ Исправление 3.1: Закрытие окна (~5 строк)
6. ✅ Исправление 3.2: Добавить id к кнопкам (~6 строк в двух местах)
7. ✅ Исправление 3.3: Новая функция `updateVisualizationButtonText()` (~15 строк)
8. ✅ Исправление 3.4-3.5: Вызовы обновления кнопки (по 1-2 строки)
9. ⚠️ Опционально: Кнопка в легенде

**Общее время:** ~20-30 минут

Удачи с улучшением визуализации! 🎨
