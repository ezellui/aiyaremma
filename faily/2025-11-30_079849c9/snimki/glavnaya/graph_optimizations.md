# Оптимизации для графа философских концепций

## Критические проблемы производительности

### 1. **SVG плохо масштабируется** (самая большая проблема)
- **Текущее состояние**: 500+ узлов × тысячи связей = десятки тысяч DOM-элементов
- **Проблема**: Браузер пересчитывает layout для каждого изменения
- **Решение**: Переход на Canvas или WebGL

### 2. **Tick-обработчик обновляет все элементы**
```javascript
// ТЕКУЩИЙ КОД - ПЛОХО:
simulation.on("tick", () => {
    link.attr("d", d => { /* обновляет ВСЕ связи */ });
    node.attr("transform", d => { /* обновляет ВСЕ узлы */ });
});
```

### 3. **Слишком много тиков симуляции**
- Текущее: 300 тиков для стабилизации
- С большим графом нужно больше, что замедляет загрузку

---

## РЕШЕНИЯ (от простых к сложным)

## 🟢 Быстрые улучшения (применить сразу)

### A. Ограничить частоту обновлений
```javascript
// Вместо каждого тика - только каждые 30ms
let lastUpdate = 0;
simulation.on("tick", () => {
    const now = performance.now();
    if (now - lastUpdate < 30) return; // Уменьшаем FPS
    lastUpdate = now;
    
    // обновления...
});
```

### B. Упростить расчет путей связей
```javascript
// ТЕКУЩИЙ - сложный изогнутый путь:
.attr("d", d => {
    const dx = d.target.x - d.source.x;
    const dy = d.target.y - d.source.y;
    const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
    return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
});

// ОПТИМИЗИРОВАННЫЙ - прямые линии:
.attr("x1", d => d.source.x)
.attr("y1", d => d.source.y)
.attr("x2", d => d.target.x)
.attr("y2", d => d.target.y);
```

### C. Уменьшить количество сил в симуляции
```javascript
let simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(120)) // уменьшить
    .force("charge", d3.forceManyBody().strength(-200)) // уменьшить силу
    .force("center", d3.forceCenter(width / 2, height / 2))
    // .force("collision", d3.forceCollide().radius(45)) // УБРАТЬ - дорого!
    .alphaDecay(0.05) // УВЕЛИЧИТЬ для быстрой стабилизации
    .velocityDecay(0.6); // Добавить затухание скорости
```

### D. Pre-compute позиции (кэширование)
```javascript
// Вычислить расположение один раз, сохранить в JSON
function saveLayout() {
    const layout = nodes.map(n => ({ id: n.id, x: n.x, y: n.y }));
    localStorage.setItem('graph-layout', JSON.stringify(layout));
}

// При загрузке - использовать сохраненные позиции
function loadLayout() {
    const saved = JSON.parse(localStorage.getItem('graph-layout'));
    if (saved) {
        nodes.forEach(n => {
            const pos = saved.find(s => s.id === n.id);
            if (pos) { n.x = pos.x; n.y = pos.y; }
        });
        simulation.alpha(0); // Не запускать симуляцию!
    }
}
```

---

## 🟡 Средняя сложность (большой эффект)

### E. Виртуализация - рендерить только видимое
```javascript
// Отслеживать viewport при zoom/pan
let viewportBounds = { minX: 0, maxX: width, minY: 0, maxY: height };

zoom.on("zoom", (event) => {
    const transform = event.transform;
    g.attr("transform", transform);
    
    // Обновить границы видимой области
    viewportBounds = {
        minX: -transform.x / transform.k,
        maxX: (width - transform.x) / transform.k,
        minY: -transform.y / transform.k,
        maxY: (height - transform.y) / transform.k
    };
    
    updateVisibility();
});

function updateVisibility() {
    // Скрывать узлы вне видимости
    node.style("display", d => {
        if (d.x < viewportBounds.minX || d.x > viewportBounds.maxX ||
            d.y < viewportBounds.minY || d.y > viewportBounds.maxY) {
            return "none";
        }
        return "block";
    });
    
    // Скрывать связи с невидимыми узлами
    link.style("display", d => {
        const sourceVisible = d.source.x >= viewportBounds.minX && 
                             d.source.x <= viewportBounds.maxX;
        const targetVisible = d.target.x >= viewportBounds.minX && 
                             d.target.x <= viewportBounds.maxX;
        return (sourceVisible || targetVisible) ? "block" : "none";
    });
}
```

### F. Уровни детализации (LOD)
```javascript
// При отдалении - упрощать отображение
zoom.on("zoom", (event) => {
    const scale = event.transform.k;
    
    if (scale < 0.5) {
        // Дальний зум - только точки
        node.select("text").style("display", "none");
        node.select("circle").attr("r", 3);
        link.style("stroke-width", 1);
    } else if (scale < 1) {
        // Средний зум
        node.select("text").style("display", "none");
        node.select("circle").attr("r", 8);
        link.style("stroke-width", 2);
    } else {
        // Ближний зум - все детали
        node.select("text").style("display", "block");
        node.select("circle").attr("r", 18);
        link.style("stroke-width", d => d.weight || 2);
    }
});
```

### G. Отложенная инициализация событий
```javascript
// Не вешать события сразу на все элементы
// Вместо этого - event delegation на родителе

svg.on("mouseover", function(event) {
    const target = event.target;
    if (target.tagName === "circle") {
        // Обработка наведения на узел
        const nodeData = d3.select(target.parentNode).datum();
        showTooltip(nodeData, event);
    }
});
```

---

## 🔴 Радикальные решения (максимальный эффект)

### H. **Canvas вместо SVG** (рекомендуется для 500+ узлов)

Canvas в 10-100 раз быстрее для большого количества элементов!

```javascript
// Использовать d3-force, но рисовать на Canvas
const canvas = document.querySelector('canvas');
const context = canvas.getContext('2d');

simulation.on("tick", () => {
    context.clearRect(0, 0, width, height);
    
    // Рисовать связи
    context.strokeStyle = '#999';
    context.lineWidth = 1;
    links.forEach(d => {
        context.beginPath();
        context.moveTo(d.source.x, d.source.y);
        context.lineTo(d.target.x, d.target.y);
        context.stroke();
    });
    
    // Рисовать узлы
    nodes.forEach(d => {
        context.beginPath();
        context.arc(d.x, d.y, 5, 0, 2 * Math.PI);
        context.fillStyle = d.color;
        context.fill();
    });
});

// Интерактивность через quadtree для быстрого поиска
const quadtree = d3.quadtree()
    .x(d => d.x)
    .y(d => d.y)
    .addAll(nodes);

canvas.addEventListener('click', (event) => {
    const [x, y] = d3.pointer(event);
    const node = quadtree.find(x, y, 20);
    if (node) handleNodeClick(node);
});
```

### I. **WebGL с sigma.js** (для тысяч узлов)

Полная замена D3 на специализированную библиотеку:

```html
<script src="https://cdn.jsdelivr.net/npm/sigma@latest/dist/sigma.min.js"></script>

<script>
const graph = new graphology.Graph();

// Добавить данные
concepts.forEach(c => graph.addNode(c.id, { 
    x: Math.random(), 
    y: Math.random(), 
    label: c.label,
    color: philosopherColors[c.philosopher]
}));

relations.forEach(r => graph.addEdge(r.source, r.target, {
    color: relationColors[r.type]
}));

// Создать визуализацию (рендерит через WebGL)
const renderer = new Sigma(graph, document.getElementById('container'), {
    renderEdgeLabels: false,
    enableEdgeEvents: true
});

// Применить layout алгоритм
import FA2Layout from "graphology-layout-forceatlas2/worker";
const layout = new FA2Layout(graph, { iterations: 300 });
layout.start();
</script>
```

---

## 📊 Сравнение производительности

| Решение | Узлы | Связи | FPS | Сложность |
|---------|------|-------|-----|-----------|
| **Текущий D3+SVG** | 100 | 200 | 60 | - |
| **+ Оптимизации A-D** | 300 | 600 | 40-50 | Низкая |
| **+ Виртуализация E-F** | 500 | 1000 | 30-40 | Средняя |
| **Canvas (H)** | 1000 | 5000 | 50-60 | Высокая |
| **WebGL sigma.js (I)** | 10000+ | 50000+ | 60 | Высокая |

---

## ✅ Рекомендуемый план действий

### Этап 1 (1-2 часа):
1. Применить оптимизации A, B, C
2. Добавить кэширование позиций (D)
3. **Ожидаемый результат**: 2-3x ускорение

### Этап 2 (3-4 часа):
4. Реализовать виртуализацию (E)
5. Добавить LOD (F)
6. **Ожидаемый результат**: работает с 500 узлами при 30+ FPS

### Этап 3 (если всё еще медленно):
7. Переписать на Canvas (H) - большая работа, но огромный эффект

---

## 🔧 Дополнительные трюки

### Отключить симуляцию после стабилизации
```javascript
simulation.on("tick", () => {
    if (simulation.alpha() < 0.01) {
        simulation.stop();
        console.log("Симуляция остановлена");
    }
    // обновления...
});
```

### Группировка связей между одними и теми же узлами
```javascript
// Вместо 10 связей A→B нарисовать одну толстую
const groupedLinks = d3.rollup(
    relations,
    v => ({ count: v.length, types: v.map(r => r.type) }),
    r => `${r.source}-${r.target}`
);
```

### Использовать Web Workers для расчетов
```javascript
// Вынести симуляцию в отдельный поток
const worker = new Worker('simulation-worker.js');
worker.postMessage({ nodes, links });
worker.onmessage = (e) => {
    updatePositions(e.data.positions);
};
```
