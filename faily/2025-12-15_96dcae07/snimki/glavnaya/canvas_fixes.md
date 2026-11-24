# Исправления для Canvas графа философии

## Исправление 1: Точная визуализация согласно исходным стилям

### Заменить функцию `drawLinks()` на:

```javascript
function drawLinks() {
    const drawDetails = LOD.shouldDrawEdgeDetails();
    const currentLOD = LOD.getCurrentLevel();
    
    links.forEach(link => {
        const source = link.source;
        const target = link.target;
        
        // Viewport culling
        if (!isInViewport(source.x, source.y) && !isInViewport(target.x, target.y)) {
            return;
        }
        
        const isDimmed = link._dimmed || false;
        const isHighlighted = link._highlighted || false;
        const isSelected = link._selected || false;
        const isHovered = link._hovered || false;
        
        // Определяем визуальные параметры согласно исходным CSS стилям
        let opacity = 0.4; // базовая opacity из .link
        if (isDimmed) opacity = 0.1; // из .link.dimmed
        if (isHighlighted) opacity = 1.0; // из .link.highlighted
        if (isHovered) opacity = 0.9; // из .link:hover
        
        // Определяем толщину линии
        let lineWidth;
        if (lodEnabled) {
            lineWidth = LOD.getEdgeWidth(link.weight);
        } else {
            // Базовая толщина согласно weight (из CSS)
            if (link.weight === 1) lineWidth = 2; // .link.weight-weak
            else if (link.weight === 2) lineWidth = 3; // .link.weight-medium
            else if (link.weight === 3) lineWidth = 5; // .link.weight-strong
            else lineWidth = 2;
        }
        
        // При hover значительно увеличиваем
        if (isHovered) {
            if (link.weight === 1) lineWidth = 8; // .link.weight-weak:hover
            else if (link.weight === 2) lineWidth = 10; // .link.weight-medium:hover
            else if (link.weight === 3) lineWidth = 12; // .link.weight-strong:hover
            else lineWidth = 10;
        }
        
        if (isSelected) {
            lineWidth = 5; // .link.selected
        }
        
        const color = relationTypesObj[link.type].color;
        
        // Рисуем связь
        ctx.save();
        ctx.globalAlpha = opacity;
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth / transform.k; // Масштабируем толщину
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Пунктирная линия для двунаправленных связей
        if (link.bidirectional) {
            ctx.setLineDash([5 / transform.k, 5 / transform.k]);
        }
        
        // Рисуем кривую Безье (как в исходном SVG)
        ctx.beginPath();
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.5; // Как в исходном коде
        
        // Параметры дуги для квадратичной кривой
        const angle = Math.atan2(dy, dx);
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        
        // Контрольная точка для дуги
        const controlX = midX - Math.sin(angle) * dr * 0.15;
        const controlY = midY + Math.cos(angle) * dr * 0.15;
        
        ctx.moveTo(source.x, source.y);
        ctx.quadraticCurveTo(controlX, controlY, target.x, target.y);
        ctx.stroke();
        
        ctx.setLineDash([]);
        
        // Фильтр свечения для highlighted связей
        if (isHighlighted || isSelected) {
            ctx.shadowBlur = 5 / transform.k;
            ctx.shadowColor = color;
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
        
        // Рисуем стрелку на конце (если детализация позволяет)
        if ((lodEnabled && drawDetails) || !lodEnabled) {
            drawArrow(target.x, target.y, controlX, controlY, color, lineWidth / transform.k);
        }
        
        ctx.restore();
    });
}

function drawArrow(toX, toY, fromX, fromY, color, lineWidth) {
    const angle = Math.atan2(toY - fromY, toX - fromX);
    const arrowSize = Math.max(6, lineWidth * 1.5);
    
    ctx.save();
    ctx.fillStyle = color;
    ctx.translate(toX, toY);
    ctx.rotate(angle);
    
    // Отступаем от центра узла (26 как в исходном refX)
    ctx.translate(-26 / transform.k, 0);
    
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-arrowSize / transform.k, -arrowSize / (2 * transform.k));
    ctx.lineTo(-arrowSize / transform.k, arrowSize / (2 * transform.k));
    ctx.closePath();
    ctx.fill();
    
    ctx.restore();
}
```

### Заменить функцию `drawNodes()` на:

```javascript
function drawNodes() {
    const drawLabels = lodEnabled ? LOD.shouldDrawLabels() : true;
    const drawGlow = lodEnabled ? LOD.shouldDrawGlow() : true;
    const nodeRadius = lodEnabled ? LOD.getNodeRadius() : 18;
    const fontSize = lodEnabled ? LOD.getFontSize() : 10;
    
    nodes.forEach(node => {
        // Viewport culling
        if (!isInViewport(node.x, node.y, nodeRadius * 2)) {
            return;
        }
        
        const isDimmed = node._dimmed || false;
        const isHighlighted = node._highlighted || false;
        const isSelected = node._selected || false;
        const isHovered = node._hovered || false;
        
        // Определяем opacity согласно исходным CSS
        let opacity = 1.0;
        if (isDimmed) opacity = 0.2; // из .node.dimmed
        
        const color = philosopherConcepts[node.concept].color;
        
        ctx.save();
        ctx.globalAlpha = opacity;
        
        // Свечение для выделенных узлов (filter: drop-shadow)
        if ((isHighlighted || isSelected) && drawGlow) {
            // .node.highlighted circle и .node.selected circle
            const shadowBlur = isSelected ? 15 : 20;
            ctx.shadowBlur = shadowBlur / transform.k;
            ctx.shadowColor = isSelected ? '#ffd700' : 'rgba(255,255,255,0.8)';
        }
        
        // Дополнительное свечение при hover
        if (isHovered) {
            ctx.shadowBlur = 10 / transform.k;
            ctx.shadowColor = 'rgba(255,255,255,0.4)';
        }
        
        // Основной круг узла
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, nodeRadius / transform.k, 0, Math.PI * 2);
        ctx.fill();
        
        // Обводка
        if (isSelected) {
            ctx.strokeStyle = '#ffd700'; // .node.selected circle
            ctx.lineWidth = 6 / transform.k;
        } else if (isHighlighted) {
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 5 / transform.k; // .node.highlighted circle
        } else {
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 3 / transform.k; // .node circle
        }
        ctx.stroke();
        
        ctx.shadowBlur = 0;
        ctx.shadowColor = 'transparent';
        
        // Текст (метка узла)
        if (drawLabels && fontSize > 0) {
            ctx.fillStyle = '#fff';
            ctx.font = `600 ${fontSize / transform.k}px 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            
            // Тень для текста (text-shadow: 0 0 4px black)
            ctx.shadowColor = 'black';
            ctx.shadowBlur = 4 / transform.k;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
            
            ctx.fillText(node.label, node.x, node.y - (nodeRadius / transform.k) - (7 / transform.k));
            
            ctx.shadowBlur = 0;
        }
        
        ctx.restore();
    });
}
```

---

## Исправление 2: Галочка для включения/выключения LOD

### Добавить в HTML после `<canvas>` (строка 227):

```html
<div id="container">
    <canvas id="graph"></canvas>
    <div class="tooltip" id="tooltip"></div>
    
    <!-- Контроллер LOD -->
    <div id="lod-control" style="position: absolute; top: 20px; right: 20px; 
                                   background: rgba(0,0,0,0.8); padding: 12px 18px; 
                                   border-radius: 8px; color: white; font-size: 13px;
                                   border: 1px solid rgba(255,255,255,0.2);
                                   z-index: 1000;">
        <label style="cursor: pointer; display: flex; align-items: center; gap: 8px;">
            <input type="checkbox" id="lod-toggle" checked style="cursor: pointer; width: 16px; height: 16px;">
            <span>Переменная детализация</span>
        </label>
    </div>
</div>
```

### Добавить в JavaScript (после объявления переменной transform):

```javascript
// ============================================
// КОНТРОЛЬ LOD
// ============================================

let lodEnabled = true;

// Обработчик галочки LOD
document.getElementById('lod-toggle').addEventListener('change', (e) => {
    lodEnabled = e.target.checked;
    render();
});
```

---

## Исправление 3: Курсор-указатель при наведении на узлы/связи

### Обновить функцию `updateHoverState`:

```javascript
function updateHoverState(x, y) {
    const newHoveredNode = findNodeAt(x, y);
    const newHoveredLink = !newHoveredNode ? findLinkAt(x, y) : null;
    
    let needsRender = false;
    
    // Обновление hover для узлов
    if (newHoveredNode !== hoveredNode) {
        if (hoveredNode) {
            hoveredNode._hovered = false;
        }
        hoveredNode = newHoveredNode;
        if (hoveredNode) {
            hoveredNode._hovered = true;
        }
        needsRender = true;
    }
    
    // Обновление hover для связей
    if (newHoveredLink !== hoveredLink) {
        if (hoveredLink) {
            hoveredLink._hovered = false;
        }
        hoveredLink = newHoveredLink;
        if (hoveredLink) {
            hoveredLink._hovered = true;
        }
        needsRender = true;
    }
    
    // Обновление курсора
    if (hoveredNode || hoveredLink) {
        canvas.style.cursor = 'pointer';
    } else if (isDragging) {
        canvas.style.cursor = 'grabbing';
    } else {
        canvas.style.cursor = 'grab';
    }
    
    // Обновление tooltip
    if (hoveredNode) {
        showNodeTooltip(hoveredNode);
    } else if (hoveredLink) {
        showLinkTooltip(hoveredLink);
    } else {
        hideTooltip();
    }
    
    if (needsRender) {
        render();
    }
}
```

---

## Исправление 4: Точное определение клика на связях

### Заменить функцию `findLinkAt`:

```javascript
function findLinkAt(x, y) {
    const threshold = Math.max(10, 15 / transform.k); // Адаптивный порог
    let closestLink = null;
    let minDistance = threshold;
    
    for (let link of links) {
        const source = link.source;
        const target = link.target;
        
        // Параметры кривой (как в drawLinks)
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
        
        const angle = Math.atan2(dy, dx);
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        
        const controlX = midX - Math.sin(angle) * dr * 0.15;
        const controlY = midY + Math.cos(angle) * dr * 0.15;
        
        // Проверяем расстояние до кривой Безье в нескольких точках
        const numSamples = 20; // Количество точек для проверки
        for (let i = 0; i <= numSamples; i++) {
            const t = i / numSamples;
            
            // Квадратичная кривая Безье: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
            const curveX = (1 - t) * (1 - t) * source.x + 
                          2 * (1 - t) * t * controlX + 
                          t * t * target.x;
            const curveY = (1 - t) * (1 - t) * source.y + 
                          2 * (1 - t) * t * controlY + 
                          t * t * target.y;
            
            const dist = Math.sqrt((curveX - x) ** 2 + (curveY - y) ** 2);
            
            if (dist < minDistance) {
                minDistance = dist;
                closestLink = link;
            }
        }
    }
    
    return closestLink;
}
```

---

## Исправление 5: Drag узлов после остановки симуляции

### Обновить обработчики мыши для canvas:

```javascript
// ============================================
// ОБРАБОТЧИКИ МЫШИ (исправленная версия)
// ============================================

let isDragging = false;
let isDraggingNode = false;
let draggedNode = null;
let dragStart = { x: 0, y: 0 };
let lastTransform = { ...transform };

canvas.addEventListener('mousedown', (e) => {
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    
    // Проверяем, кликнули ли на узел
    const clickedNode = findNodeAt(worldPos.x, worldPos.y);
    
    if (clickedNode && !e.shiftKey) {
        // Начинаем перетаскивание узла
        isDraggingNode = true;
        draggedNode = clickedNode;
        draggedNode.fx = draggedNode.x;
        draggedNode.fy = draggedNode.y;
        
        // Перезапускаем симуляцию только если она не работает
        if (simulation.alpha() < 0.001) {
            // Симуляция остановлена, обновляем вручную
        } else {
            simulation.alphaTarget(0.3).restart();
        }
        
        canvas.style.cursor = 'grabbing';
    } else {
        // Начинаем перетаскивание холста
        isDragging = true;
        dragStart = { x: e.clientX, y: e.clientY };
        lastTransform = { ...transform };
        canvas.style.cursor = 'grabbing';
    }
});

canvas.addEventListener('mousemove', (e) => {
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    
    if (isDraggingNode && draggedNode) {
        // Перетаскивание узла
        draggedNode.fx = worldPos.x;
        draggedNode.fy = worldPos.y;
        draggedNode.x = worldPos.x;
        draggedNode.y = worldPos.y;
        
        // Если симуляция остановлена, просто перерисовываем
        if (simulation.alpha() < 0.001) {
            render();
        }
    } else if (isDragging) {
        // Перетаскивание холста
        const dx = e.clientX - dragStart.x;
        const dy = e.clientY - dragStart.y;
        transform.x = lastTransform.x + dx;
        transform.y = lastTransform.y + dy;
        render();
    } else {
        // Обновление hover состояния
        updateHoverState(worldPos.x, worldPos.y);
    }
});

canvas.addEventListener('mouseup', (e) => {
    if (isDraggingNode) {
        isDraggingNode = false;
        if (draggedNode) {
            draggedNode.fx = null;
            draggedNode.fy = null;
            
            // Если симуляция работала, останавливаем её
            if (simulation.alpha() > 0.001) {
                simulation.alphaTarget(0);
            }
            
            draggedNode = null;
        }
    }
    
    if (isDragging) {
        isDragging = false;
    }
    
    // Обновляем курсор
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    updateHoverState(worldPos.x, worldPos.y);
});

canvas.addEventListener('mouseleave', () => {
    if (isDraggingNode && draggedNode) {
        draggedNode.fx = null;
        draggedNode.fy = null;
        if (simulation.alpha() > 0.001) {
            simulation.alphaTarget(0);
        }
    }
    
    isDragging = false;
    isDraggingNode = false;
    draggedNode = null;
    canvas.style.cursor = 'grab';
    
    // Скрываем tooltip
    hideTooltip();
    
    // Сбрасываем hover состояния
    if (hoveredNode) {
        hoveredNode._hovered = false;
        hoveredNode = null;
    }
    if (hoveredLink) {
        hoveredLink._hovered = false;
        hoveredLink = null;
    }
    render();
});
```

---

## Дополнительное улучшение: Обновление LOD уровней

Для более плавной детализации можно скорректировать пороги LOD:

```javascript
const LOD = {
    // Уровни детализации в зависимости от масштаба
    MINIMAL: 0.4,   // До этого масштаба - минимальная детализация
    LOW: 0.7,       // До этого - низкая детализация
    MEDIUM: 1.0,    // До этого - средняя детализация
    HIGH: 1.5,      // Выше - высокая детализация
    
    getCurrentLevel() {
        if (!lodEnabled) return 'ultra'; // Всегда максимум если LOD выключен
        
        const k = transform.k;
        if (k < this.MINIMAL) return 'minimal';
        if (k < this.LOW) return 'low';
        if (k < this.MEDIUM) return 'medium';
        if (k < this.HIGH) return 'high';
        return 'ultra';
    },
    
    shouldDrawLabels() {
        if (!lodEnabled) return true;
        return transform.k >= this.LOW;
    },
    
    shouldDrawEdgeDetails() {
        if (!lodEnabled) return true;
        return transform.k >= this.MEDIUM;
    },
    
    shouldDrawGlow() {
        if (!lodEnabled) return true;
        return transform.k >= this.MEDIUM;
    },
    
    getNodeRadius() {
        if (!lodEnabled) return 18;
        
        const k = transform.k;
        if (k < this.MINIMAL) return 8;
        if (k < this.LOW) return 12;
        return 18;
    },
    
    getEdgeWidth(weight) {
        if (!lodEnabled) {
            // Возвращаем базовую толщину по весу
            const baseWidths = {1: 2, 2: 3, 3: 5};
            return baseWidths[weight] || 2;
        }
        
        const k = transform.k;
        const baseWidths = {1: 2, 2: 3, 3: 5};
        const base = baseWidths[weight] || 2;
        
        if (k < this.MINIMAL) return base * 0.5;
        if (k < this.LOW) return base * 0.7;
        return base;
    },
    
    getFontSize() {
        if (!lodEnabled) return 10;
        
        const k = transform.k;
        if (k < this.LOW) return 0;
        if (k < this.MEDIUM) return 8;
        return 10;
    }
};
```

---

## Резюме исправлений

1. ✅ **Точная визуализация** - узлы и связи теперь рисуются с точным соблюдением исходных CSS стилей
2. ✅ **Галочка LOD** - добавлен UI контроль для включения/выключения переменной детализации
3. ✅ **Курсор-указатель** - курсор меняется на `pointer` при наведении на узлы/связи
4. ✅ **Точное определение связей** - улучшен алгоритм определения клика на кривых Безье
5. ✅ **Drag после остановки симуляции** - узлы можно перетаскивать даже после полной остановки симуляции

Все исправления готовы к применению!
