# Точечные исправления Canvas графа

## Исправление 1: Точная отрисовка ТОЛЬКО для максимального уровня детализации

### Заменить функцию `drawLinks()`:

```javascript
function drawLinks() {
    const drawDetails = LOD.shouldDrawEdgeDetails();
    const currentLOD = LOD.getCurrentLevel();
    const isMaxDetail = !lodEnabled || currentLOD === 'ultra'; // Максимальная детализация
    
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
        
        // Определяем визуальные параметры
        let opacity, lineWidth;
        
        if (isMaxDetail) {
            // МАКСИМАЛЬНАЯ ДЕТАЛИЗАЦИЯ - точно по исходным CSS стилям
            opacity = 0.4; // базовая opacity из .link
            if (isDimmed) opacity = 0.1; // из .link.dimmed
            if (isHighlighted) opacity = 1.0; // из .link.highlighted
            if (isHovered) opacity = 0.9; // из .link:hover
            
            // Определяем толщину линии согласно weight (из CSS)
            if (link.weight === 1) lineWidth = 2; // .link.weight-weak
            else if (link.weight === 2) lineWidth = 3; // .link.weight-medium
            else if (link.weight === 3) lineWidth = 5; // .link.weight-strong
            else lineWidth = 2;
            
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
        } else {
            // УРОВНИ ДЕТАЛИЗАЦИИ С LOD (как было раньше)
            opacity = isDimmed ? 0.1 : 0.4;
            if (isHighlighted) opacity = 1.0;
            
            lineWidth = LOD.getEdgeWidth(link.weight);
            if (link._hovered) lineWidth *= 3;
            if (isSelected) lineWidth *= 1.5;
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
        
        // Фильтр свечения для highlighted связей (только при максимальной детализации)
        if (isMaxDetail && (isHighlighted || isSelected)) {
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
```

### Заменить функцию `drawNodes()`:

```javascript
function drawNodes() {
    const currentLOD = LOD.getCurrentLevel();
    const isMaxDetail = !lodEnabled || currentLOD === 'ultra'; // Максимальная детализация
    
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
        
        // Определяем opacity
        let opacity = 1.0;
        if (isDimmed) opacity = 0.2; // из .node.dimmed
        
        const color = philosopherConcepts[node.concept].color;
        
        ctx.save();
        ctx.globalAlpha = opacity;
        
        if (isMaxDetail) {
            // МАКСИМАЛЬНАЯ ДЕТАЛИЗАЦИЯ - точное свечение как в исходных CSS
            
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
        } else {
            // УРОВНИ ДЕТАЛИЗАЦИИ С LOD (упрощенное свечение)
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

## Исправление 2: Предотвращение изменения выделенности при перетаскивании

Проблема: при отпускании узла после drag срабатывает событие `click`, которое меняет выделение.

### Решение: отслеживать, был ли реальный drag

Добавить перед обработчиками событий canvas:

```javascript
// Флаг для отслеживания реального перемещения при drag
let hasDragged = false;
```

### Обновить обработчики canvas:

```javascript
canvas.addEventListener('mousedown', (e) => {
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    
    // Сбрасываем флаг drag
    hasDragged = false;
    
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
        // Отмечаем, что произошло реальное перемещение
        hasDragged = true;
        
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
        // Отмечаем, что произошло реальное перемещение
        hasDragged = true;
        
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
    const worldPos = inverseTransform(mousePos.x, worldPos.y);
    updateHoverState(worldPos.x, worldPos.y);
});
```

### Обновить обработчик click (добавить проверку hasDragged):

```javascript
canvas.addEventListener('click', (e) => {
    // Игнорируем клик если был реальный drag
    if (hasDragged) {
        hasDragged = false;
        return;
    }
    
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
```

---

## Резюме исправлений

### Исправление 1: Точная отрисовка для максимального уровня
- ✅ Сохранены все прежние уровни детализации (minimal, low, medium, high)
- ✅ Изменен ТОЛЬКО максимальный уровень (`ultra` или при выключенном LOD)
- ✅ При максимальной детализации узлы и связи рисуются точно по исходным CSS стилям
- ✅ Правильные толщины связей: 2/3/5 и 8/10/12 при hover
- ✅ Точное свечение с shadowBlur 15/20 для узлов
- ✅ Золотая обводка 6px для selected узлов

### Исправление 2: Выделение при drag
- ✅ Добавлен флаг `hasDragged` для отслеживания реального перемещения
- ✅ Если узел просто перетащили и отпустили, событие `click` игнорируется
- ✅ Невыделенные узлы остаются невыделенными после drag
- ✅ Выделенные узлы остаются выделенными после drag
- ✅ Обычные клики продолжают работать как положено

Применив эти исправления, граф будет работать точно как требуется!
