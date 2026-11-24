# Адаптация функций для Canvas

Все функции, которые работали с SVG элементами, нужно переделать для Canvas. Вот все необходимые корректировки:

---

## 1. Фильтрация узлов и связей

### Заменить `applyBasicFilter`:

```javascript
/**
 * Применение базовых фильтров (не chains/unique_chains)
 */
function applyBasicFilter(mode) {
    const config = FilterModes[mode];
    if (!config) return;
    
    const allRelationsSelected = selectedRelations.size === Object.keys(relationTypesObj).length;
    
    // Фильтруем связи по правилам режима
    const validLinks = links.filter(config.linkFilter);
    
    // Собираем видимые узлы из валидных связей
    const visibleNodes = new Set();
    validLinks.forEach(l => {
        visibleNodes.add(l.source.id || l.source);
        visibleNodes.add(l.target.id || l.target);
    });
    
    // Применяем видимость к узлам через свойство _visible
    nodes.forEach(node => {
        node._visible = visibleNodes.has(node.id);
    });
    
    // Применяем видимость к связям через свойство _visible
    links.forEach(link => {
        const sourceVisible = visibleNodes.has(link.source.id || link.source);
        const targetVisible = visibleNodes.has(link.target.id || link.target);
        link._visible = config.linkFilter(link) && sourceVisible && targetVisible;
    });
    
    render();
}
```

### Заменить `applyChainVisibility`:

```javascript
/**
 * Применение видимости для найденных цепочек
 */
function applyChainVisibility(chainNodes, chainLinks) {
    nodes.forEach(node => {
        node._visible = chainNodes.has(node.id);
    });
    
    links.forEach(link => {
        link._visible = chainLinks.has(link);
    });
    
    render();
}
```

### Заменить `cleanupInvisibleSelections`:

```javascript
/**
 * Очистка выделений невидимых узлов
 */
function cleanupInvisibleSelections() {
    const visibleNodeIds = new Set();
    nodes.forEach(node => {
        if (node._visible !== false) {
            visibleNodeIds.add(node.id);
        }
    });
    
    selectedNodes.forEach(node => {
        if (!visibleNodeIds.has(node.id)) {
            selectedNodes.delete(node);
        }
    });

    if (selectedNodes.size === 0) {
        resetHighlight();
    } else {
        highlightConnected(Array.from(selectedNodes));
    }
}
```

---

## 2. Обновить функции отрисовки для учета _visible

### Обновить `drawLinks()` - добавить проверку видимости в начало:

```javascript
function drawLinks() {
    const drawDetails = LOD.shouldDrawEdgeDetails();
    const currentLOD = LOD.getCurrentLevel();
    const isMaxDetail = !lodEnabled || currentLOD === 'ultra';
    
    links.forEach(link => {
        // ДОБАВИТЬ: Проверка видимости
        if (link._visible === false) {
            return; // Пропускаем невидимые связи
        }
        
        const source = link.source;
        const target = link.target;
        
        // ... остальной код без изменений
```

### Обновить `drawNodes()` - добавить проверку видимости в начало:

```javascript
function drawNodes() {
    const currentLOD = LOD.getCurrentLevel();
    const isMaxDetail = !lodEnabled || currentLOD === 'ultra';
    
    const drawLabels = lodEnabled ? LOD.shouldDrawLabels() : true;
    const drawGlow = lodEnabled ? LOD.shouldDrawGlow() : true;
    const nodeRadius = lodEnabled ? LOD.getNodeRadius() : 18;
    const fontSize = lodEnabled ? LOD.getFontSize() : 10;
    
    nodes.forEach(node => {
        // ДОБАВИТЬ: Проверка видимости
        if (node._visible === false) {
            return; // Пропускаем невидимые узлы
        }
        
        // Viewport culling
        if (!isInViewport(node.x, node.y, nodeRadius * 2)) {
            return;
        }
        
        // ... остальной код без изменений
```

---

## 3. Режим одинаковой толщины связей

### Добавить глобальную переменную:

```javascript
let uniformLinkWidth = false;
```

### Заменить `toggleUniformLinkWidth`:

```javascript
// Переключение режима одинаковой толщины связей
function toggleUniformLinkWidth() {
    uniformLinkWidth = document.getElementById('uniformLinkWidth').checked;
    render();
}
```

### Обновить `drawLinks()` - учитывать uniformLinkWidth:

В функции `drawLinks()`, в блоке определения `lineWidth`, добавить проверку:

```javascript
// После определения lineWidth, но перед ctx.strokeStyle:

// Применяем режим одинаковой толщины, если включен
if (uniformLinkWidth) {
    lineWidth = 2; // Фиксированная толщина
}

ctx.strokeStyle = color;
ctx.lineWidth = lineWidth / transform.k;
```

---

## 4. Статистика фильтров

### Заменить `updateFilterStats`:

```javascript
// Обновление статистики фильтров
function updateFilterStats() {
    let visibleNodesCount = 0;
    let visibleLinksCount = 0;
    
    nodes.forEach(node => {
        if (node._visible !== false) visibleNodesCount++;
    });
    
    links.forEach(link => {
        if (link._visible !== false) visibleLinksCount++;
    });
    
    const totalNodes = nodes.length;
    const totalLinks = links.length;
    
    document.getElementById('filterStats').textContent = 
        `Показано: ${visibleNodesCount}/${totalNodes} концепций, ${visibleLinksCount}/${totalLinks} связей`;
}
```

---

## 5. Навигация и zoom

### Заменить `selectSearchResult`:

```javascript
function selectSearchResult(nodeId, context) {
    const nodeData = nodes.find(n => n.id === nodeId);
    if (!nodeData) return;
    
    if (context === 'legend') {
        // Выделяем узел и центрируем
        selectedNodes.clear();
        selectedNodes.add(nodeData);
        highlightConnected([nodeData]);
        
        // Анимированный переход к узлу
        animatePanAndZoom(nodeData.x, nodeData.y, 1.5, 750);
        
        clearLegendSearch();
        
    } else if (context === 'modal') {
        // Переходим к детальной информации об узле
        showDetailModal(nodeData);
        clearModalSearch();
    }
}

// Вспомогательная функция для плавного перехода
function animatePanAndZoom(targetX, targetY, targetScale, duration) {
    const startTransform = { ...transform };
    const startTime = Date.now();
    
    // Вычисляем конечную трансформацию
    const endTransform = {
        x: width / 2 - targetX * targetScale,
        y: height / 2 - targetY * targetScale,
        k: targetScale
    };
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const t = Math.min(elapsed / duration, 1);
        
        // Ease-in-out функция
        const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        
        // Интерполяция трансформации
        transform.x = startTransform.x + (endTransform.x - startTransform.x) * eased;
        transform.y = startTransform.y + (endTransform.y - startTransform.y) * eased;
        transform.k = startTransform.k + (endTransform.k - startTransform.k) * eased;
        
        render();
        
        if (t < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    animate();
}
```

---

## 6. Управление симуляцией

### Заменить `resetSimulation`:

```javascript
function resetSimulation() {
    nodes.forEach(n => {
        n.fx = null;
        n.fy = null;
    });
    resetHighlight();
    simulation.alpha(1).restart();
}
```

### Заменить `centerGraph`:

```javascript
function centerGraph() {
    animatePanAndZoom(width / 2, height / 2, 1, 750);
    simulation.force("center", d3.forceCenter(width / 2, height / 2));
    simulation.alpha(0.3).restart();
}
```

### Заменить `freezeSimulation`:

```javascript
function freezeSimulation() {
    if (simulation) {
        simulation.stop();
        // console.log("Симуляция заморожена");
    }
}
```

### Заменить `unfreezeSimulation`:

```javascript
function unfreezeSimulation() {
    if (simulation) {
        // Возобновляем симуляцию с небольшой энергией
        simulation.alpha(0.3).restart();
        // console.log("Симуляция разморожена");
    }
}
```

---

## 7. Группировка узлов

### Оставить расчет позиций как есть, но обновить `toggleGrouping`:

```javascript
function toggleGrouping() {
    isGrouped = !isGrouped;
    const btn = document.getElementById('groupBtn');
    
    resetHighlight();
    
    if (isGrouped) {
        btn.classList.add('active');
        btn.textContent = '📦 Разгруппировать';
        
        // Добавляем силы группировки
        simulation
            .force("x", d3.forceX(d => groupPositions[d.concept].x).strength(0.3))
            .force("y", d3.forceY(d => groupPositions[d.concept].y).strength(0.3))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("collision", d3.forceCollide().radius(40));
    } else {
        btn.classList.remove('active');
        btn.textContent = '📦 Группировать';
        
        // Убираем силы группировки
        simulation
            .force("x", null)
            .force("y", null)
            .force("charge", d3.forceManyBody().strength(-350))
            .force("collision", d3.forceCollide().radius(45))
            .force("center", d3.forceCenter(width / 2, height / 2));
    }
    simulation.alpha(0.5).restart();
}
```

---

## 8. Resize обработчик

### Заменить `window.addEventListener('resize')`:

```javascript
window.addEventListener('resize', () => {
    // Canvas resize уже обрабатывается функцией resizeCanvas()
    // Нужно только обновить позиции групп и центр симуляции
    
    const newWidth = window.innerWidth;
    const newHeight = window.innerHeight;
    
    // Пересчитываем позиции групп
    const newSpacingX = newWidth / (cols + 1);
    const newSpacingY = newHeight / (rows + 1);
    philosopherNames.forEach((phil, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        groupPositions[phil] = {
            x: newSpacingX * (col + 1),
            y: newSpacingY * (row + 1)
        };
    });
    
    if (isGrouped) {
        simulation
            .force("x", d3.forceX(d => groupPositions[d.concept].x).strength(0.3))
            .force("y", d3.forceY(d => groupPositions[d.concept].y).strength(0.3));
    } else {
        simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
    }
    
    simulation.alpha(0.3).restart();
});
```

---

## 9. Переход к узлу из модального окна

### Заменить `gotoNodeFromModal`:

```javascript
// Функция перехода к узлу из модального окна
function gotoNodeFromModal(nodeId) {
    closeDetailModal();
    
    setTimeout(() => {
        const nodeData = nodes.find(n => n.id === nodeId);
        if (nodeData) {
            // Выделяем узел
            selectedNodes.clear();
            selectedNodes.add(nodeData);
            highlightConnected([nodeData]);
            
            // Центрируем на узле с анимацией
            animatePanAndZoom(nodeData.x, nodeData.y, 1.5, 750);
        }
    }, 100);
}
```

---

## 10. Обновление данных графа

### Заменить `updateGraphData`:

```javascript
// Обновление графа без полной перезагрузки
function updateGraphData() {
    // Пересоздаем массив links из connections
    links = connections.map(conn => ({
        source: conn.from,
        target: conn.to,
        type: conn.type,
        weight: conn.weight || 2,
        bidirectional: conn.bidirectional || false,
        description: conn.description
    }));
    
    // Инициализируем состояния для новых связей
    links.forEach(link => {
        if (link._dimmed === undefined) link._dimmed = false;
        if (link._highlighted === undefined) link._highlighted = false;
        if (link._selected === undefined) link._selected = false;
        if (link._hovered === undefined) link._hovered = false;
        if (link._visible === undefined) link._visible = true;
    });
    
    // Перезапускаем симуляцию с новыми данными
    simulation.nodes(nodes);
    simulation.force("link").links(links);
    
    // Перерисовываем
    render();
    
    // Перезапускаем симуляцию
    simulation.alpha(0.3).restart();
}
```

### УДАЛИТЬ `updateGraphVisualization`:

Эта функция больше не нужна, так как Canvas не требует создания/обновления DOM элементов. Все обновления происходят через `render()`.

---

## 11. Обработчики кликов на пустом месте

Эти обработчики уже реализованы в новом Canvas коде в обработчике `canvas.addEventListener('click')`. Можно удалить эти строки:

```javascript
// УДАЛИТЬ ЭТИ ОБРАБОТЧИКИ:
d3.select('#graph').on('click', function(event) {
    if (event.shiftKey && event.target.tagName === 'svg') {
        openEditConceptModal();
    }
});

svg.on('click.clearSelection', function(event) {
    if (!event.shiftKey && event.target.tagName === 'svg') {
        editMode.pendingConceptSelection = [];
        node.classed('selected', false);
    }
});
```

Они уже обрабатываются в Canvas коде.

---

## 12. Обновить findNodeAt и findLinkAt для учета видимости

### Добавить проверки видимости:

```javascript
function findNodeAt(x, y) {
    const radius = LOD.getNodeRadius();
    for (let node of nodes) {
        // Пропускаем невидимые узлы
        if (node._visible === false) continue;
        
        const dx = node.x - x;
        const dy = node.y - y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist <= radius) {
            return node;
        }
    }
    return null;
}

function findLinkAt(x, y) {
    const threshold = Math.max(10, 15 / transform.k);
    let closestLink = null;
    let minDistance = threshold;
    
    for (let link of links) {
        // Пропускаем невидимые связи
        if (link._visible === false) continue;
        
        // ... остальной код без изменений
    }
    
    return closestLink;
}
```

---

## Резюме изменений

### Что изменилось:
1. ✅ Фильтрация теперь через свойство `_visible` вместо `display: none`
2. ✅ Все функции zoom/pan используют анимацию через `animatePanAndZoom`
3. ✅ Статистика и подсчеты используют прямой перебор массивов
4. ✅ Удалена функция `updateGraphVisualization` (не нужна для Canvas)
5. ✅ Режим одинаковой толщины через переменную `uniformLinkWidth`
6. ✅ Обработчики событий уже в Canvas коде
7. ✅ Функции работы с симуляцией упрощены (нет tickCount)

### Ключевые добавления:
- Функция `animatePanAndZoom()` для плавных переходов
- Проверки `_visible` в `drawNodes()` и `drawLinks()`
- Проверки `_visible` в `findNodeAt()` и `findLinkAt()`

Все функции теперь полностью адаптированы для Canvas!
