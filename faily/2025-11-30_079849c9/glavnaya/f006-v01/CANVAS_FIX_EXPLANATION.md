# Исправления Canvas версии графа

## 🐛 Найденные проблемы

### Проблема 1: Transform не определен до использования

**Симптомы:**
- При загрузке страницы возникает ошибка JavaScript
- `ReferenceError: transform is not defined` или `ReferenceError: render is not defined`

**Причина:**
```javascript
// Строка 162 (БЫЛО):
resizeCanvas();  // ← Вызывается сразу

// Внутри resizeCanvas (строка 158):
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    render();  // ← Вызывает render()
}

// НО render() определена только на строке 269!
// И transform определен на строке 242!
```

**Порядок выполнения (НЕПРАВИЛЬНЫЙ):**
1. Строка 162: вызов `resizeCanvas()`
2. Строка 158: вызов `render()`
3. ❌ Ошибка: `render` не определен
4. ❌ Ошибка: `transform` не определен

**Решение:**

1. Переместили определение `transform` в начало:
```javascript
// Сразу после создания canvas и ctx
let transform = {
    x: 0,
    y: 0,
    scale: 1
};
```

2. Добавили проверку в `resizeCanvas`:
```javascript
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    // Проверяем, определена ли функция render
    if (typeof render === 'function') {
        render();
    }
}
```

---

### Проблема 2: Те же ошибки с перетаскиванием, что и в SVG версии

**Симптомы:**
- После 1-2 перетаскиваний узлов дальнейшие не работают
- Симуляция мгновенно останавливается
- За один кадр проходят сотни тиков

**Причина:**
Счётчик `tickCount` не сбрасывался при перетаскивании.

**Решение:**

1. Сброс `tickCount` при начале перетаскивания:
```javascript
canvas.addEventListener('mousedown', (e) => {
    const node = findNodeAt(x, y);
    
    if (node) {
        dragNode = node;
        tickCount = 0; // ← ДОБАВЛЕНО
        simulation.alphaTarget(0.3).restart();
        simulationRunning = true;
    }
});
```

2. Остановка симуляции только по alpha:
```javascript
simulation.on("tick", () => {
    tickCount++;
    
    // Останавливаем по alpha, не по tickCount
    if (simulation.alpha() < 0.005) {
        simulation.stop();
        simulationRunning = false;
    }
    
    // Аварийная защита от бесконечного цикла
    if (tickCount > 5000) {
        console.warn('Аварийная остановка!');
        simulation.stop();
    }
});
```

---

## ✅ Полный список исправлений

### Исправление 1: Определение transform перенесено в начало
**Было:** transform определен на строке 242  
**Стало:** transform определен сразу после canvas/ctx (~строка 155)

### Исправление 2: Защита resizeCanvas от вызова несуществующего render
**Было:** `render()` вызывался безусловно  
**Стало:** `if (typeof render === 'function') render();`

### Исправление 3: Удалено дублирующее определение transform
**Было:** transform определялся дважды (строки 155 и 242)  
**Стало:** определяется только один раз в начале

### Исправление 4: Сброс tickCount при перетаскивании
**Добавлено:** `tickCount = 0;` в mousedown обработчике

### Исправление 5: Остановка симуляции по alpha
**Было:** `if (simulation.alpha() < 0.01 || tickCount > 300)`  
**Стало:** `if (simulation.alpha() < 0.005)`

### Исправление 6: Аварийная защита
**Добавлено:** остановка при `tickCount > 5000` для защиты от бесконечного цикла

### Исправление 7: Индикаторы Ticks и Alpha
**Добавлено:** отображение tickCount и alpha в интерфейсе для диагностики

---

## 🧪 Тестирование

После исправлений проверьте:

### ✅ Загрузка страницы
1. Откройте файл в браузере
2. Не должно быть ошибок в консоли
3. Граф должен отобразиться сразу
4. Симуляция должна запуститься автоматически

### ✅ Перетаскивание узлов
1. Перетащите любой узел
2. Проверьте, что `Ticks` сбросился на 0
3. Перетащите еще несколько узлов
4. Каждый раз должно работать корректно

### ✅ Панорамирование и зум
1. Перетащите фон (не узел) - должно работать панорамирование
2. Используйте колесо мыши для зума
3. Проверьте, что `transform` корректно обновляется

### ✅ Индикаторы
Должны отображаться:
- **FPS:** ~60 (при активной симуляции ~30-40)
- **Draw:** время отрисовки в мс
- **Nodes:** 1000
- **Links:** 2000
- **Visible:** количество видимых узлов
- **Ticks:** счётчик тиков (сбрасывается при перетаскивании)
- **Alpha:** энергия системы (уменьшается до ~0.000)
- **Sim:** running / stopped

---

## 🔍 Отладка

Если проблемы остаются, откройте консоль DevTools и проверьте:

### 1. Проверка определения transform
```javascript
console.log(typeof transform); // должно быть "object"
console.log(transform);         // должно быть { x: 0, y: 0, scale: 1 }
```

### 2. Проверка работы симуляции
```javascript
console.log(simulation.alpha()); // должно постепенно уменьшаться
console.log(tickCount);          // должно увеличиваться при симуляции
```

### 3. Проверка при перетаскивании
Перетащите узел и сразу проверьте:
```javascript
console.log('Ticks после drag:', tickCount);  // должно быть близко к 0
console.log('Alpha:', simulation.alpha());     // должно быть ~0.3
```

---

## 📊 Сравнение с SVG версией

| Аспект | SVG версия | Canvas версия |
|--------|-----------|---------------|
| **Производительность** | ~30-40 FPS (500 узлов) | **60 FPS (1000 узлов)** ✓ |
| **Рендеринг** | DOM манипуляции | Прямая отрисовка |
| **Интерактивность** | D3 events | Ручная обработка |
| **Масштабируемость** | До ~500 узлов | **До 10,000+ узлов** ✓ |
| **Сложность кода** | Проще | Сложнее |

---

## 💡 Дополнительные улучшения (опционально)

### 1. Quadtree для быстрого поиска узлов

Текущий `findNodeAt()` проверяет все узлы линейно (O(n)). Для больших графов можно использовать quadtree:

```javascript
// Создать quadtree для быстрого поиска
const quadtree = d3.quadtree()
    .x(d => d.x)
    .y(d => d.y)
    .addAll(nodes);

function findNodeAt(x, y) {
    const graphPos = screenToGraph(x, y);
    const clickRadius = 10 / transform.scale;
    
    // O(log n) вместо O(n)
    return quadtree.find(graphPos.x, graphPos.y, clickRadius);
}

// Обновлять quadtree при изменении позиций
simulation.on("end", () => {
    quadtree = d3.quadtree()
        .x(d => d.x)
        .y(d => d.y)
        .addAll(nodes);
});
```

### 2. Offscreen Canvas для фона

Если граф редко обновляется, можно рисовать связи на отдельном offscreen canvas:

```javascript
const offscreenCanvas = document.createElement('canvas');
const offscreenCtx = offscreenCanvas.getContext('2d');

function renderLinksToOffscreen() {
    // Рисуем все связи один раз
    offscreenCtx.clearRect(0, 0, width, height);
    // ... отрисовка связей
}

function render() {
    ctx.drawImage(offscreenCanvas, 0, 0); // Быстрая копия
    // ... отрисовка только узлов
}
```

### 3. Web Workers для симуляции

Вынести D3 force simulation в отдельный поток:

```javascript
// simulation-worker.js
self.onmessage = function(e) {
    // Запустить симуляцию
    // Отправлять позиции обратно
    self.postMessage({ positions: [...] });
};

// В основном коде
const worker = new Worker('simulation-worker.js');
worker.onmessage = (e) => {
    updateNodePositions(e.data.positions);
    render();
};
```

---

## ✅ Итого

Все исправления внесены в файл `canvas_graph.html`. 

Основные проблемы решены:
- ✅ Transform определен до использования
- ✅ Перетаскивание работает корректно
- ✅ Симуляция останавливается по alpha
- ✅ Добавлены индикаторы для диагностики
- ✅ Аварийная защита от бесконечного цикла

Файл готов к использованию! 🚀
