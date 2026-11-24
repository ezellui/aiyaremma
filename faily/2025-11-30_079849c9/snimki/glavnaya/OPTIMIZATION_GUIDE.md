# Пошаговое руководство по оптимизации вашего графа

## 🎯 Цель
Ускорить работу графа с 500+ концепциями и 1000+ связями

---

## ⚡ Этап 1: Быстрые улучшения (30 минут)

### Шаг 1.1: Замените изогнутые пути на прямые линии

**Найдите в вашем коде (примерно строки 729-745):**
```javascript
let link = g.append("g")
    .selectAll("path")
    .data(links)
    .enter()
    .append("path")
    .attr("class", d => { /* ... */ })
    .attr("stroke", d => relationTypesObj[d.type].color)
    .attr("marker-end", d => `url(#arrow-${d.type})`);
```

**Замените на:**
```javascript
let link = g.append("g")
    .selectAll("line")  // ← ИЗМЕНЕНО: path → line
    .data(links)
    .enter()
    .append("line")     // ← ИЗМЕНЕНО: path → line
    .attr("class", d => { /* ... */ })
    .attr("stroke", d => relationTypesObj[d.type].color)
    .attr("marker-end", d => `url(#arrow-${d.type})`);
```

**Найдите в tick-обработчике (примерно строки 682-700):**
```javascript
link.filter(function() { return this.style.display !== "none"; })
    .attr("d", d => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
    });
```

**Замените на:**
```javascript
link.filter(function() { return this.style.display !== "none"; })
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);
```

**Эффект:** Ускорение в 2-3 раза ⚡

---

### Шаг 1.2: Ограничьте частоту обновлений

**Найдите simulation.on("tick") (примерно строки 682-709):**
```javascript
simulation.on("tick", () => {
    const now = Date.now();
    if (now - lastTickUpdate < TICK_UPDATE_INTERVAL) {
        return;
    }
    lastTickUpdate = now;
    
    tickCount++;
    
    // ... остальной код
});
```

**Измените константу:**
```javascript
const TICK_UPDATE_INTERVAL = 16; // было
```
**на:**
```javascript
const TICK_UPDATE_INTERVAL = 30; // стало (~33 FPS вместо 60)
```

**Эффект:** Снижение нагрузки на 40% без заметной потери плавности 📉

---

### Шаг 1.3: Уменьшите силы симуляции

**Найдите (примерно строки 668-673):**
```javascript
let simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(160))
    .force("charge", d3.forceManyBody().strength(-350))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(45))
    .alphaDecay(0.02);
```

**Замените на:**
```javascript
let simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(120)) // ↓ было 160
    .force("charge", d3.forceManyBody().strength(-200))              // ↑ было -350
    .force("center", d3.forceCenter(width / 2, height / 2))
    // .force("collision", d3.forceCollide().radius(45))             // ← УБРАНО!
    .alphaDecay(0.05)                                                // ↑ было 0.02
    .velocityDecay(0.6);                                            // ← ДОБАВЛЕНО
```

**Эффект:** Быстрая стабилизация, снижение вычислений на 30% 🚀

---

### Шаг 1.4: Удалите сложные фильтры CSS

**Найдите в стилях (примерно строки 38-60):**
```css
.node circle {
    stroke-width: 3px;
    filter: drop-shadow(0 0 10px rgba(255,255,255,0.4));  /* ← УДАЛИТЬ */
}

.node.highlighted circle {
    stroke-width: 5px;
    filter: drop-shadow(0 0 20px rgba(255,255,255,0.8));  /* ← УДАЛИТЬ */
}

.node.selected circle {
    stroke-width: 6px;
    stroke: #ffd700 !important;
    filter: drop-shadow(0 0 15px #ffd700);                /* ← УДАЛИТЬ */
}
```

**Замените на:**
```css
.node circle {
    stroke-width: 2px;  /* Упрощено */
}

.node.highlighted circle {
    stroke-width: 4px;
}

.node.selected circle {
    stroke-width: 5px;
    stroke: #ffd700 !important;
}
```

**Эффект:** Меньше нагрузки на GPU, плавнее зум и панорамирование 🎨

---

## 🔄 Этап 2: Виртуализация (1-2 часа)

### Шаг 2.1: Добавьте отслеживание viewport

**Добавьте после создания zoom (примерно после строки 637):**

```javascript
let viewportBounds = {
    minX: -500, 
    maxX: width + 500,
    minY: -500, 
    maxY: height + 500
};

function updateViewportBounds(transform) {
    const margin = 200; // Запас для плавности
    viewportBounds = {
        minX: (-transform.x - margin) / transform.k,
        maxX: (width - transform.x + margin) / transform.k,
        minY: (-transform.y - margin) / transform.k,
        maxY: (height - transform.y + margin) / transform.k
    };
}
```

### Шаг 2.2: Обновляйте границы при зуме

**Найдите zoom.on("zoom") (примерно строка 633):**
```javascript
const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
    });
```

**Замените на:**
```javascript
const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
        updateViewportBounds(event.transform);  // ← ДОБАВЛЕНО
        updateVisibility();                      // ← ДОБАВЛЕНО
    });
```

### Шаг 2.3: Добавьте функцию скрытия невидимых элементов

**Добавьте новую функцию:**

```javascript
function updateVisibility() {
    // Скрываем узлы вне viewport
    node.style("display", d => {
        if (d.x < viewportBounds.minX || d.x > viewportBounds.maxX ||
            d.y < viewportBounds.minY || d.y > viewportBounds.maxY) {
            return "none";
        }
        return "block";
    });

    // Скрываем связи, если оба конца невидимы
    link.style("display", d => {
        const sourceVisible = 
            d.source.x >= viewportBounds.minX && d.source.x <= viewportBounds.maxX &&
            d.source.y >= viewportBounds.minY && d.source.y <= viewportBounds.maxY;
        const targetVisible = 
            d.target.x >= viewportBounds.minX && d.target.x <= viewportBounds.maxX &&
            d.target.y >= viewportBounds.minY && d.target.y <= viewportBounds.maxY;
        
        return (sourceVisible || targetVisible) ? "block" : "none";
    });
}
```

**Эффект:** При зуме отрисовываются только видимые элементы! 🔍

---

## 💾 Этап 3: Кэширование позиций (15 минут)

**Добавьте две новые функции:**

```javascript
function saveLayout() {
    const layout = nodes.map(n => ({ 
        id: n.id, 
        x: n.x, 
        y: n.y 
    }));
    localStorage.setItem('philosophy-graph-layout', JSON.stringify(layout));
    console.log('Позиции сохранены!');
}

function loadLayout() {
    const saved = localStorage.getItem('philosophy-graph-layout');
    if (!saved) return false;

    const layout = JSON.parse(saved);
    let loaded = 0;
    
    nodes.forEach(n => {
        const pos = layout.find(s => s.id === n.id);
        if (pos) {
            n.x = pos.x;
            n.y = pos.y;
            n.fx = pos.x;
            n.fy = pos.y;
            loaded++;
        }
    });

    if (loaded > 0) {
        simulation.alpha(0); // НЕ запускать симуляцию!
        console.log(`Загружено ${loaded} позиций`);
        
        // Обновить визуализацию
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        node.attr("transform", d => `translate(${d.x},${d.y})`);
        
        return true;
    }
    return false;
}
```

**Вызовите при загрузке страницы (в конце скрипта):**

```javascript
// После всей инициализации, перед запуском симуляции
if (!loadLayout()) {
    // Если не загрузили - запускаем симуляцию
    simulation.alpha(1).restart();
} else {
    // Если загрузили - симуляция уже остановлена
    console.log('Граф загружен из кэша - симуляция не нужна!');
}

// Сохранять позиции после остановки симуляции
simulation.on("end", () => {
    saveLayout(); // ← АВТОСОХРАНЕНИЕ
    console.log("Симуляция завершена, позиции сохранены");
});
```

**Эффект:** Мгновенная загрузка при повторном посещении! ⚡

---

## 📊 Этап 4: Уровни детализации LOD (30 минут)

**Добавьте функцию:**

```javascript
function updateLOD(scale) {
    if (scale < 0.5) {
        // Дальний зум - минимум деталей
        node.select("text").style("display", "none");
        node.select("circle").attr("r", 3);
        link.style("stroke-width", 1).style("opacity", 0.2);
    } else if (scale < 1.2) {
        // Средний зум
        node.select("text").style("display", "none");
        node.select("circle").attr("r", 10);
        link.style("stroke-width", 2).style("opacity", 0.4);
    } else {
        // Ближний зум - все детали
        node.select("text").style("display", "block");
        node.select("circle").attr("r", 18);
        link.style("stroke-width", d => d.weight || 2).style("opacity", 0.6);
    }
}
```

**Вызывайте в zoom обработчике:**

```javascript
const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
        updateViewportBounds(event.transform);
        updateVisibility();
        updateLOD(event.transform.k);  // ← ДОБАВЛЕНО
    });
```

**Эффект:** При отдалении упрощается отрисовка 🎨

---

## 🎛️ Опциональные улучшения

### Добавьте индикатор производительности

**HTML (добавьте в body):**
```html
<div style="position: absolute; top: 10px; right: 10px; 
            background: rgba(0,0,0,0.8); color: #0f0; 
            padding: 10px; border-radius: 5px; 
            font-family: monospace; font-size: 12px;">
    FPS: <span id="fps">60</span><br>
    Nodes: <span id="node-count">0</span><br>
    Visible: <span id="visible-count">0</span>
</div>
```

**JavaScript:**
```javascript
let frameCount = 0;
let lastFpsUpdate = performance.now();

function updatePerformance() {
    frameCount++;
    const now = performance.now();
    
    if (now - lastFpsUpdate >= 1000) {
        const fps = Math.round(frameCount * 1000 / (now - lastFpsUpdate));
        document.getElementById('fps').textContent = fps;
        document.getElementById('node-count').textContent = nodes.length;
        
        const visible = node.filter(function() { 
            return this.style.display !== "none"; 
        }).size();
        document.getElementById('visible-count').textContent = visible;
        
        frameCount = 0;
        lastFpsUpdate = now;
    }
}

// Вызывайте в tick-обработчике
simulation.on("tick", () => {
    // ... ваш код
    updatePerformance();  // ← ДОБАВИТЬ В КОНЕЦ
});
```

---

## 📈 Ожидаемые результаты

| Этап | Время | Ускорение | Сложность |
|------|-------|-----------|-----------|
| Этап 1 (все шаги) | 30 мин | 2-3x | ⭐ Легко |
| Этап 2 (виртуализация) | 1-2 часа | 3-5x | ⭐⭐ Средне |
| Этап 3 (кэширование) | 15 мин | Мгновенная загрузка | ⭐ Легко |
| Этап 4 (LOD) | 30 мин | 1.5-2x | ⭐⭐ Средне |
| **ИТОГО** | **2.5-3 часа** | **5-10x** | - |

---

## 🚨 Если всё ещё медленно...

### Вариант A: Переход на Canvas
- Используйте файл `canvas_graph.html` как шаблон
- В 10-100 раз быстрее для больших графов
- Сложность реализации: высокая (1-2 дня работы)
- Результат: 60 FPS даже с 10000+ узлами

### Вариант B: Использование sigma.js
```html
<script src="https://cdn.jsdelivr.net/npm/sigma@latest/dist/sigma.min.js"></script>
<script src="https://unpkg.com/graphology@latest/dist/graphology.min.js"></script>
```

Специализированная библиотека для больших графов с WebGL-рендерингом.

---

## ✅ Чек-лист применения

- [ ] Шаг 1.1: path → line для связей
- [ ] Шаг 1.2: Увеличен TICK_INTERVAL до 30ms
- [ ] Шаг 1.3: Убрана collision force, увеличен alphaDecay
- [ ] Шаг 1.4: Удалены CSS filter (drop-shadow)
- [ ] Шаг 2.1-2.3: Виртуализация viewport
- [ ] Шаг 3: Кэширование позиций
- [ ] Шаг 4: LOD (уровни детализации)
- [ ] Опционально: Индикатор производительности

---

## 💡 Советы по отладке

1. **Откройте DevTools → Performance**
   - Запишите профиль во время работы графа
   - Найдите самые медленные функции

2. **Проверьте FPS**
   - Добавьте индикатор производительности
   - Цель: стабильные 30+ FPS

3. **Считайте видимые элементы**
   - При зуме должно быть < 30% от общего числа

4. **Тестируйте постепенно**
   - Применяйте оптимизации по одной
   - Измеряйте результат после каждой

---

Удачи с оптимизацией! 🚀
