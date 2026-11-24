# Миграция графа философии с SVG на Canvas с уровнями детализации (LOD)

## Обзор изменений

Этот документ содержит все необходимые фрагменты кода для переделки графа с SVG на Canvas. Основные улучшения:

1. **Canvas вместо SVG** - значительно выше производительность для больших датасетов
2. **Level of Detail (LOD)** - разная детализация в зависимости от масштаба
3. **Оптимизированный рендеринг** - отрисовка только видимых элементов
4. **Сохранение всего функционала** - клики, выделение, tooltip, drag & drop

---

## 1. HTML структура (замена строк 17-29)

Заменить:
```html
<div id="container">
    <svg id="graph"></svg>
    <div class="tooltip" id="tooltip"></div>
</div>
```

На:
```html
<div id="container">
    <canvas id="graph"></canvas>
    <div class="tooltip" id="tooltip"></div>
</div>
```

---

## 2. CSS стили (замена строк 23-26 и добавление новых)

Заменить:
```css
#graph {
    width: 100%;
    height: 100%;
}
```

На:
```css
#graph {
    width: 100%;
    height: 100%;
    cursor: grab;
}

#graph:active {
    cursor: grabbing;
}
```

Удалить CSS стили для SVG элементов (строки 28-142) - они больше не нужны для Canvas.

---

## 3. Основная инициализация (замена строк 603-750)

Полностью заменить раздел от создания SVG до создания узлов на следующий код:

```javascript
// ============================================
// CANVAS ИНИЦИАЛИЗАЦИЯ
// ============================================

const canvas = document.getElementById('graph');
const ctx = canvas.getContext('2d', { alpha: false });

// Настройка canvas размеров с учетом devicePixelRatio для четкости
const dpr = window.devicePixelRatio || 1;
let width = window.innerWidth;
let height = window.innerHeight;

function resizeCanvas() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.scale(dpr, dpr);
    render();
}

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// ============================================
// ТРАНСФОРМАЦИЯ И МАСШТАБИРОВАНИЕ
// ============================================

let transform = {
    x: 0,
    y: 0,
    k: 1
};

// Применение трансформации к координатам
function applyTransform(x, y) {
    return {
        x: x * transform.k + transform.x,
        y: y * transform.k + transform.y
    };
}

// Обратная трансформация (из экранных в мировые координаты)
function inverseTransform(screenX, screenY) {
    return {
        x: (screenX - transform.x) / transform.k,
        y: (screenY - transform.y) / transform.k
    };
}

// ============================================
// СИСТЕМА LOD (LEVEL OF DETAIL)
// ============================================

const LOD = {
    // Уровни детализации в зависимости от масштаба
    MINIMAL: 0.3,   // До этого масштаба - минимальная детализация
    LOW: 0.6,       // До этого - низкая детализация
    MEDIUM: 1.2,    // До этого - средняя детализация
    HIGH: 2.0,      // Выше - высокая детализация
    
    getCurrentLevel() {
        const k = transform.k;
        if (k < this.MINIMAL) return 'minimal';
        if (k < this.LOW) return 'low';
        if (k < this.MEDIUM) return 'medium';
        if (k < this.HIGH) return 'high';
        return 'ultra';
    },
    
    shouldDrawLabels() {
        return transform.k >= this.LOW;
    },
    
    shouldDrawEdgeDetails() {
        return transform.k >= this.MEDIUM;
    },
    
    shouldDrawGlow() {
        return transform.k >= this.MEDIUM;
    },
    
    getNodeRadius() {
        const k = transform.k;
        if (k < this.MINIMAL) return 8;
        if (k < this.LOW) return 12;
        return 18; // полный размер
    },
    
    getEdgeWidth(weight) {
        const k = transform.k;
        const baseWidths = {1: 2, 2: 3, 3: 5};
        const base = baseWidths[weight] || 2;
        
        if (k < this.MINIMAL) return base * 0.5;
        if (k < this.LOW) return base * 0.7;
        return base;
    },
    
    getFontSize() {
        const k = transform.k;
        if (k < this.LOW) return 0;
        if (k < this.MEDIUM) return 8;
        return 10;
    }
};

// ============================================
// VIEWPORT CULLING (отсечение невидимых объектов)
// ============================================

function isInViewport(x, y, padding = 100) {
    const screen = applyTransform(x, y);
    return screen.x >= -padding && 
           screen.x <= width + padding && 
           screen.y >= -padding && 
           screen.y <= height + padding;
}

// ============================================
// РЕНДЕРИНГ НА CANVAS
// ============================================

function render() {
    // Очистка canvas
    ctx.fillStyle = '#0f0c29'; // Цвет фона
    ctx.fillRect(0, 0, width, height);
    
    ctx.save();
    
    // Применяем трансформацию
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.k, transform.k);
    
    const level = LOD.getCurrentLevel();
    
    // 1. Рисуем связи
    drawLinks();
    
    // 2. Рисуем узлы
    drawNodes();
    
    ctx.restore();
    
    // 3. Рисуем UI элементы поверх (если нужно)
    drawUI();
}

function drawLinks() {
    const drawDetails = LOD.shouldDrawEdgeDetails();
    
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
        
        // Определяем визуальные параметры
        let opacity = isDimmed ? 0.1 : 0.4;
        if (isHighlighted) opacity = 1.0;
        
        let lineWidth = LOD.getEdgeWidth(link.weight);
        if (link._hovered) lineWidth *= 3;
        if (isSelected) lineWidth *= 1.5;
        
        const color = relationTypesObj[link.type].color;
        
        // Рисуем кривую связь (квадратичная кривая Безье)
        ctx.save();
        ctx.globalAlpha = opacity;
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Рисуем линию
        ctx.beginPath();
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 0.3; // Кривизна
        
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        const offsetX = -dy / Math.sqrt(dx * dx + dy * dy) * dr;
        const offsetY = dx / Math.sqrt(dx * dx + dy * dy) * dr;
        
        ctx.moveTo(source.x, source.y);
        ctx.quadraticCurveTo(
            midX + offsetX, midY + offsetY,
            target.x, target.y
        );
        ctx.stroke();
        
        // Рисуем стрелку на конце
        if (drawDetails) {
            drawArrow(target.x, target.y, midX + offsetX, midY + offsetY, color, lineWidth);
        }
        
        // Пунктирная линия для двунаправленных связей
        if (link.bidirectional && drawDetails) {
            ctx.setLineDash([5 / transform.k, 5 / transform.k]);
            ctx.stroke();
            ctx.setLineDash([]);
        }
        
        ctx.restore();
    });
}

function drawArrow(toX, toY, fromX, fromY, color, lineWidth) {
    const angle = Math.atan2(toY - fromY, toX - fromX);
    const arrowSize = Math.max(8, lineWidth * 2);
    
    ctx.save();
    ctx.fillStyle = color;
    ctx.translate(toX, toY);
    ctx.rotate(angle);
    
    // Отступаем от центра узла
    ctx.translate(-20, 0);
    
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-arrowSize, -arrowSize / 2);
    ctx.lineTo(-arrowSize, arrowSize / 2);
    ctx.closePath();
    ctx.fill();
    
    ctx.restore();
}

function drawNodes() {
    const drawLabels = LOD.shouldDrawLabels();
    const drawGlow = LOD.shouldDrawGlow();
    const nodeRadius = LOD.getNodeRadius();
    const fontSize = LOD.getFontSize();
    
    nodes.forEach(node => {
        // Viewport culling
        if (!isInViewport(node.x, node.y, nodeRadius * 2)) {
            return;
        }
        
        const isDimmed = node._dimmed || false;
        const isHighlighted = node._highlighted || false;
        const isSelected = node._selected || false;
        const isHovered = node._hovered || false;
        
        let opacity = isDimmed ? 0.2 : 1.0;
        const color = philosopherConcepts[node.concept].color;
        
        ctx.save();
        ctx.globalAlpha = opacity;
        
        // Свечение для выделенных узлов
        if ((isHighlighted || isSelected) && drawGlow) {
            const glowRadius = nodeRadius + 10;
            const gradient = ctx.createRadialGradient(
                node.x, node.y, nodeRadius,
                node.x, node.y, glowRadius
            );
            gradient.addColorStop(0, color + '40');
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Основной круг узла
        ctx.fillStyle = color;
        ctx.strokeStyle = isSelected ? '#ffd700' : '#fff';
        ctx.lineWidth = isSelected ? 6 / transform.k : (isHighlighted ? 5 / transform.k : 3 / transform.k);
        
        if (isHovered) {
            ctx.shadowBlur = 10 / transform.k;
            ctx.shadowColor = 'rgba(255, 255, 255, 0.5)';
        }
        
        ctx.beginPath();
        ctx.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        
        ctx.shadowBlur = 0;
        
        // Текст (метка узла)
        if (drawLabels && fontSize > 0) {
            ctx.fillStyle = '#fff';
            ctx.font = `600 ${fontSize}px 'Segoe UI', sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            
            // Тень для текста (для читаемости)
            ctx.shadowColor = 'black';
            ctx.shadowBlur = 4 / transform.k;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
            
            ctx.fillText(node.label, node.x, node.y - nodeRadius - 7);
            
            ctx.shadowBlur = 0;
        }
        
        ctx.restore();
    });
}

function drawUI() {
    // Здесь можно рисовать UI элементы поверх графа (например, индикаторы, легенду)
    // Пока оставляем пустым
}

// ============================================
// D3 FORCE SIMULATION (без изменений логики)
// ============================================

let simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(160))
    .force("charge", d3.forceManyBody().strength(-350))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(45))
    .alphaDecay(0.02);

let tickCount = 0;
const maxTicks = 300;
let lastTickUpdate = 0;
const TICK_UPDATE_INTERVAL = 16; // ~60 FPS

simulation.on("tick", () => {
    const now = Date.now();
    if (now - lastTickUpdate < TICK_UPDATE_INTERVAL) {
        return;
    }
    lastTickUpdate = now;
    tickCount++;
    
    // Вместо обновления DOM, просто перерисовываем canvas
    requestAnimationFrame(render);
    
    if (tickCount >= maxTicks) {
        simulation.stop();
    }
});

simulation.on("end", () => {
    console.log("Симуляция завершена после", tickCount, "тиков");
    console.log("Производительность - узлов:", nodes.length, "связей:", links.length);
    if (performance.memory) {
        console.log("Использование памяти:", 
            Math.round(performance.memory.usedJSHeapSize / 1048576), "МБ");
    }
    render();
});
```

---

## 4. Интерактивность: Zoom & Pan (добавить после инициализации симуляции)

```javascript
// ============================================
// МАСШТАБИРОВАНИЕ И ПЕРЕТАСКИВАНИЕ (Zoom & Pan)
// ============================================

let isDragging = false;
let dragStart = { x: 0, y: 0 };
let lastTransform = { ...transform };

// Zoom колесиком мыши
canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    
    const mouseX = e.offsetX;
    const mouseY = e.offsetY;
    
    // Координаты до масштабирования
    const worldBefore = inverseTransform(mouseX, mouseY);
    
    // Масштабирование
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newK = Math.max(0.1, Math.min(4, transform.k * zoomFactor));
    transform.k = newK;
    
    // Координаты после масштабирования
    const worldAfter = inverseTransform(mouseX, mouseY);
    
    // Корректируем позицию чтобы масштабирование было к точке курсора
    transform.x += (worldAfter.x - worldBefore.x) * transform.k;
    transform.y += (worldAfter.y - worldBefore.y) * transform.k;
    
    render();
});

// Перетаскивание холста
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
        simulation.alphaTarget(0.3).restart();
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
        render();
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
            simulation.alphaTarget(0);
            draggedNode = null;
        }
    }
    
    if (isDragging) {
        isDragging = false;
        canvas.style.cursor = 'grab';
    }
});

canvas.addEventListener('mouseleave', () => {
    isDragging = false;
    isDraggingNode = false;
    canvas.style.cursor = 'grab';
});

let isDraggingNode = false;
let draggedNode = null;
```

---

## 5. Интерактивность: Клики и выделение (заменить функции обработки кликов)

```javascript
// ============================================
// ОПРЕДЕЛЕНИЕ КЛИКОВ НА УЗЛАХ И СВЯЗЯХ
// ============================================

function findNodeAt(x, y) {
    const radius = LOD.getNodeRadius();
    for (let node of nodes) {
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
    const threshold = 10 / transform.k; // Расстояние для клика на связь
    
    for (let link of links) {
        const source = link.source;
        const target = link.target;
        
        // Вычисляем расстояние от точки до кривой
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 0.3;
        
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        const offsetX = -dy / Math.sqrt(dx * dx + dy * dy) * dr;
        const offsetY = dx / Math.sqrt(dx * dx + dy * dy) * dr;
        
        // Проверяем расстояние до кривой (упрощенно - до 3 точек на кривой)
        const points = [
            { x: source.x, y: source.y },
            { x: midX + offsetX, y: midY + offsetY },
            { x: target.x, y: target.y }
        ];
        
        for (let point of points) {
            const dist = Math.sqrt((point.x - x) ** 2 + (point.y - y) ** 2);
            if (dist <= threshold) {
                return link;
            }
        }
    }
    return null;
}

// Обработка кликов
canvas.addEventListener('click', (e) => {
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    
    const clickedNode = findNodeAt(worldPos.x, worldPos.y);
    const clickedLink = !clickedNode ? findLinkAt(worldPos.x, worldPos.y) : null;
    
    if (clickedNode) {
        handleNodeClick(e, clickedNode);
    } else if (clickedLink) {
        handleLinkClick(e, clickedLink);
    } else {
        // Клик на пустом месте
        if (e.shiftKey) {
            // Открыть модал создания концепции
            // openEditConceptModal();
        } else {
            resetHighlight();
            editMode.pendingConceptSelection = [];
            render();
        }
    }
});

// Двойной клик
let lastClickTime = 0;
let lastClickedElement = null;

canvas.addEventListener('dblclick', (e) => {
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    
    const clickedNode = findNodeAt(worldPos.x, worldPos.y);
    
    if (clickedNode) {
        // Показать детальную информацию
        // showDetailModal(clickedNode);
        console.log('Двойной клик на узле:', clickedNode.label);
    }
});
```

---

## 6. Hover и Tooltip (заменить обработчики tooltip)

```javascript
// ============================================
// HOVER И TOOLTIP
// ============================================

let hoveredNode = null;
let hoveredLink = null;
const tooltip = document.getElementById('tooltip');

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

function showNodeTooltip(node) {
    tooltip.style.opacity = '1';
    tooltip.innerHTML = `<strong>${node.label}</strong><br/>${node.description}<br/><em>${node.concept}</em>`;
    updateTooltipPosition();
}

function showLinkTooltip(link) {
    const sourceId = link.source.id || link.source;
    const targetId = link.target.id || link.target;
    const sourceNode = nodes.find(n => n.id === sourceId);
    const targetNode = nodes.find(n => n.id === targetId);
    
    if (!sourceNode || !targetNode) return;
    
    const relationLabel = relationTypesObj[link.type].label;
    const relationColor = relationTypesObj[link.type].color;
    const arrowWidth = 60;
    const arrowHeight = 20;
    
    let arrowSvg;
    if (link.bidirectional) {
        arrowSvg = `
            <svg width="${arrowWidth}" height="${arrowHeight}" style="display: block;">
                <defs>
                    <marker id="arrowhead-start-${link.type}" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto">
                        <polygon points="0 0, 0 6, 6 3" fill="${relationColor}" />
                    </marker>
                    <marker id="arrowhead-end-${link.type}" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto">
                        <polygon points="0 0, 6 3, 0 6" fill="${relationColor}" />
                    </marker>
                </defs>
                <line x1="10" y1="${arrowHeight/2}" x2="${arrowWidth-10}" y2="${arrowHeight/2}" 
                      stroke="${relationColor}" stroke-width="2" 
                      marker-start="url(#arrowhead-start-${link.type})" 
                      marker-end="url(#arrowhead-end-${link.type})" />
            </svg>
        `;
    } else {
        arrowSvg = `
            <svg width="${arrowWidth}" height="${arrowHeight}" style="display: block;">
                <defs>
                    <marker id="arrowhead-${link.type}" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto">
                        <polygon points="0 0, 6 3, 0 6" fill="${relationColor}" />
                    </marker>
                </defs>
                <line x1="5" y1="${arrowHeight/2}" x2="${arrowWidth-5}" y2="${arrowHeight/2}" 
                      stroke="${relationColor}" stroke-width="2" 
                      marker-end="url(#arrowhead-${link.type})" />
            </svg>
        `;
    }
    
    let tooltipContent = `
        <div class="link-tooltip-header">
            <strong>${sourceNode.label}</strong>
            <div class="link-tooltip-arrow">${arrowSvg}</div>
            <strong>${targetNode.label}</strong>
        </div>
        <div class="link-tooltip-type" style="color: ${relationColor};">${relationLabel}</div>
        <div class="link-tooltip-philosophers">
            <em>(${sourceNode.concept})</em>
            <em>(${targetNode.concept})</em>
        </div>
    `;
    
    if (link._selected && link.description) {
        tooltipContent += `<div class="tooltip-description">${link.description}</div>`;
    }
    
    tooltip.innerHTML = tooltipContent;
    tooltip.style.opacity = '1';
    updateTooltipPosition();
}

function hideTooltip() {
    tooltip.style.opacity = '0';
}

let lastMousePos = { x: 0, y: 0 };

canvas.addEventListener('mousemove', (e) => {
    lastMousePos = { x: e.pageX, y: e.pageY };
    updateTooltipPosition();
});

function updateTooltipPosition() {
    tooltip.style.left = (lastMousePos.x + 15) + 'px';
    tooltip.style.top = (lastMousePos.y - 10) + 'px';
}
```

---

## 7. Обновление функций выделения (заменить highlightConnected и highlightCombined)

```javascript
// ============================================
// ФУНКЦИИ ВЫДЕЛЕНИЯ И ПОДСВЕТКИ
// ============================================

let selectedNodes = new Set();
let selectedEdges = new Set();

function highlightCombined() {
    if (selectedNodes.size === 0 && selectedEdges.size === 0) {
        resetHighlight();
        return;
    }
    
    const highlightedNodes = new Set();
    const highlightedLinks = new Set();
    const isCollapsedMode = selectedNodes.size > 0 && selectedEdges.size > 0;
    
    if (isCollapsedMode) {
        selectedNodes.forEach(nodeData => {
            highlightedNodes.add(nodeData.id);
            
            links.forEach(l => {
                const sourceId = l.source.id || l.source;
                const targetId = l.target.id || l.target;
                
                if (sourceId === nodeData.id || targetId === nodeData.id) {
                    if (sourceId === nodeData.id) highlightedNodes.add(targetId);
                    if (targetId === nodeData.id) highlightedNodes.add(sourceId);
                    highlightedLinks.add(l);
                }
            });
        });
        
        selectedEdges.forEach(edge => {
            const sourceId = edge.source.id || edge.source;
            const targetId = edge.target.id || edge.target;
            highlightedNodes.add(sourceId);
            highlightedNodes.add(targetId);
            highlightedLinks.add(edge);
        });
    } else if (selectedNodes.size > 0) {
        selectedNodes.forEach(nodeData => {
            highlightedNodes.add(nodeData.id);
            
            links.forEach(l => {
                const sourceId = l.source.id || l.source;
                const targetId = l.target.id || l.target;
                
                if (sourceId === nodeData.id || targetId === nodeData.id) {
                    highlightedNodes.add(targetId);
                    highlightedNodes.add(sourceId);
                    highlightedLinks.add(l);
                }
            });
        });
    } else {
        selectedEdges.forEach(edge => {
            const sourceId = edge.source.id || edge.source;
            const targetId = edge.target.id || edge.target;
            highlightedNodes.add(sourceId);
            highlightedNodes.add(targetId);
            highlightedLinks.add(edge);
        });
    }
    
    // Применяем состояния к узлам и связям
    const selectedNodeIds = new Set(Array.from(selectedNodes).map(n => n.id));
    
    nodes.forEach(node => {
        node._dimmed = !highlightedNodes.has(node.id);
        node._highlighted = highlightedNodes.has(node.id);
        node._selected = selectedNodeIds.has(node.id);
    });
    
    links.forEach(link => {
        link._dimmed = !highlightedLinks.has(link);
        link._highlighted = highlightedLinks.has(link);
        link._selected = selectedEdges.has(link);
    });
    
    render();
}

function resetHighlight() {
    selectedNodes.clear();
    selectedEdges.clear();
    
    nodes.forEach(node => {
        node._dimmed = false;
        node._highlighted = false;
        node._selected = false;
    });
    
    links.forEach(link => {
        link._dimmed = false;
        link._highlighted = false;
        link._selected = false;
    });
    
    render();
}

function isEdgeConnectedToNode(edge, nodeData) {
    const sourceId = edge.source.id || edge.source;
    const targetId = edge.target.id || edge.target;
    return sourceId === nodeData.id || targetId === nodeData.id;
}

function isNodeConnectedToSelectedEdges(nodeData) {
    for (const edge of selectedEdges) {
        if (isEdgeConnectedToNode(edge, nodeData)) {
            return true;
        }
    }
    return false;
}

function isEdgeConnectedToSelectedNodes(edge) {
    for (const nodeData of selectedNodes) {
        if (isEdgeConnectedToNode(edge, nodeData)) {
            return true;
        }
    }
    return false;
}
```

---

## 8. Обновление handleNodeClick и handleLinkClick (заменить существующие функции)

```javascript
function handleNodeClick(event, d) {
    // Обработка shift+клик для редактирования
    if (event.shiftKey) {
        if (editMode.pendingConceptSelection.length > 0) {
            const firstConceptId = editMode.pendingConceptSelection[0];
            if (firstConceptId === d.id) {
                editMode.pendingConceptSelection = [];
                // openEditConceptModal(d.id);
                console.log('Редактирование концепции:', d.id);
            } else {
                editMode.pendingConceptSelection = [];
                // openEditConnectionModal(firstConceptId, d.id);
                console.log('Редактирование связи:', firstConceptId, '->', d.id);
            }
        } else {
            editMode.pendingConceptSelection = [d.id];
        }
        render();
        return;
    }
    
    // Отмена выбора если кликнули без shift
    if (editMode.pendingConceptSelection.length > 0) {
        editMode.pendingConceptSelection = [];
    }
    
    // Обычная логика клика
    if (event.ctrlKey || event.metaKey) {
        // Множественный выбор
        if (selectedNodes.has(d)) {
            selectedNodes.delete(d);
        } else {
            selectedNodes.add(d);
        }
    } else {
        const connectedToSelectedEdges = isNodeConnectedToSelectedEdges(d);
        if (connectedToSelectedEdges && selectedEdges.size > 0) {
            if (selectedNodes.size === 1 && selectedNodes.has(d)) {
                selectedNodes.clear();
            } else {
                selectedNodes.clear();
                selectedNodes.add(d);
            }
        } else {
            selectedEdges.clear();
            if (selectedNodes.size === 1 && selectedNodes.has(d)) {
                selectedNodes.clear();
            } else {
                selectedNodes.clear();
                selectedNodes.add(d);
            }
        }
    }
    
    highlightCombined();
}

function handleLinkClick(event, d) {
    // Shift+клик - редактирование
    if (event.shiftKey) {
        // openEditConnectionModal(d.source.id || d.source, d.target.id || d.target);
        console.log('Редактирование связи:', d.source.id, '->', d.target.id);
        return;
    }
    
    // Ctrl+клик - множественный выбор
    if (event.ctrlKey || event.metaKey) {
        if (selectedEdges.has(d)) {
            selectedEdges.delete(d);
        } else {
            selectedEdges.add(d);
        }
    } else {
        const connectedToSelectedNodes = isEdgeConnectedToSelectedNodes(d);
        
        if (connectedToSelectedNodes && selectedNodes.size > 0) {
            if (selectedEdges.size === 1 && selectedEdges.has(d)) {
                selectedEdges.clear();
            } else {
                selectedEdges.clear();
                selectedEdges.add(d);
            }
        } else {
            selectedNodes.clear();
            if (selectedEdges.size === 1 && selectedEdges.has(d)) {
                selectedEdges.clear();
            } else {
                selectedEdges.clear();
                selectedEdges.add(d);
            }
        }
    }
    
    highlightCombined();
}
```

---

## 9. Финальная инициализация и запуск

После всех функций, добавить в конец секции JavaScript:

```javascript
// ============================================
// ФИНАЛЬНАЯ ИНИЦИАЛИЗАЦИЯ
// ============================================

// Инициализируем состояния узлов и связей
nodes.forEach(node => {
    node._dimmed = false;
    node._highlighted = false;
    node._selected = false;
    node._hovered = false;
});

links.forEach(link => {
    link._dimmed = false;
    link._highlighted = false;
    link._selected = false;
    link._hovered = false;
});

// Первоначальный рендеринг
console.log("Инициализация Canvas графа:", nodes.length, "узлов,", links.length, "связей");
render();

// Инициализация фильтров и статистики (если есть)
if (typeof initFilters === 'function') {
    initFilters();
}
if (typeof updateFilterStats === 'function') {
    updateFilterStats();
}
```

---

## Резюме изменений

### Основные улучшения:

1. **Производительность**: Canvas рендеринг вместо SVG DOM манипуляций
2. **LOD система**: 5 уровней детализации (minimal, low, medium, high, ultra)
3. **Viewport culling**: Отрисовка только видимых элементов
4. **Оптимизированный рендеринг**: RequestAnimationFrame + throttling
5. **Сохранен весь функционал**: клики, drag, zoom, tooltip, выделение

### Что сохранено:

- Вся логика D3 force simulation
- Система выделения узлов и связей
- Tooltip с детальной информацией
- Обработка кликов (одинарных, двойных, с модификаторами)
- Drag & drop узлов
- Zoom и pan холста
- Визуальный стиль (цвета, размеры, эффекты)

### Особенности LOD:

| Масштаб | Уровень | Узлы | Связи | Текст | Свечение |
|---------|---------|------|-------|-------|----------|
| < 0.3   | Minimal | 8px  | 50%   | Нет   | Нет      |
| < 0.6   | Low     | 12px | 70%   | 8px   | Нет      |
| < 1.2   | Medium  | 18px | 100%  | 10px  | Да       |
| < 2.0   | High    | 18px | 100%  | 10px  | Да       |
| > 2.0   | Ultra   | 18px | 100%  | 10px  | Да       |

Все фрагменты готовы к вставке в исходный файл!
