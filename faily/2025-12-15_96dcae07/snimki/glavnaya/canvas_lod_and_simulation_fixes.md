# Исправления: LOD и симуляция при drag

## Исправление 1: Правильные уровни детализации

Проблема: кривизна связей и алгоритмы не соответствуют первой версии на промежуточных уровнях.

### Полная замена функции `drawLinks()`:

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
            // УРОВНИ ДЕТАЛИЗАЦИИ С LOD (первоначальная версия)
            opacity = isDimmed ? 0.1 : 0.4;
            if (isHighlighted) opacity = 1.0;
            
            lineWidth = LOD.getEdgeWidth(link.weight);
            if (isHovered) lineWidth *= 3;
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
        
        // Рисуем кривую (РАЗНАЯ формула для максимальной и остальных уровней)
        ctx.beginPath();
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        
        if (isMaxDetail) {
            // Для максимального уровня - как в исходном SVG (dr * 1.5)
            const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
            const angle = Math.atan2(dy, dx);
            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;
            const controlX = midX - Math.sin(angle) * dr * 0.15;
            const controlY = midY + Math.cos(angle) * dr * 0.15;
            
            ctx.moveTo(source.x, source.y);
            ctx.quadraticCurveTo(controlX, controlY, target.x, target.y);
        } else {
            // Для остальных уровней - первоначальная версия (dr * 0.3)
            const dr = Math.sqrt(dx * dx + dy * dy) * 0.3;
            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;
            const offsetX = -dy / Math.sqrt(dx * dx + dy * dy) * dr;
            const offsetY = dx / Math.sqrt(dx * dx + dy * dy) * dr;
            
            ctx.moveTo(source.x, source.y);
            ctx.quadraticCurveTo(midX + offsetX, midY + offsetY, target.x, target.y);
        }
        
        ctx.stroke();
        
        // Пунктирная линия для двунаправленных связей
        if (link.bidirectional && ((lodEnabled && drawDetails) || !lodEnabled)) {
            ctx.setLineDash([5 / transform.k, 5 / transform.k]);
            ctx.stroke();
            ctx.setLineDash([]);
        }
        
        // Фильтр свечения для highlighted связей (только при максимальной детализации)
        if (isMaxDetail && (isHighlighted || isSelected)) {
            ctx.shadowBlur = 5 / transform.k;
            ctx.shadowColor = color;
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
        
        // Рисуем стрелку на конце (если детализация позволяет)
        if ((lodEnabled && drawDetails) || !lodEnabled) {
            if (isMaxDetail) {
                const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
                const angle = Math.atan2(dy, dx);
                const midX = (source.x + target.x) / 2;
                const midY = (source.y + target.y) / 2;
                const controlX = midX - Math.sin(angle) * dr * 0.15;
                const controlY = midY + Math.cos(angle) * dr * 0.15;
                drawArrow(target.x, target.y, controlX, controlY, color, lineWidth / transform.k);
            } else {
                const dr = Math.sqrt(dx * dx + dy * dy) * 0.3;
                const midX = (source.x + target.x) / 2;
                const midY = (source.y + target.y) / 2;
                const offsetX = -dy / Math.sqrt(dx * dx + dy * dy) * dr;
                const offsetY = dx / Math.sqrt(dx * dx + dy * dy) * dr;
                drawArrow(target.x, target.y, midX + offsetX, midY + offsetY, color, lineWidth / transform.k);
            }
        }
        
        ctx.restore();
    });
}
```

### Полная замена функции `drawNodes()`:

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
            // УРОВНИ ДЕТАЛИЗАЦИИ С LOD (первоначальная версия - градиент)
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
            
            if (isHovered) {
                ctx.shadowBlur = 10 / transform.k;
                ctx.shadowColor = 'rgba(255, 255, 255, 0.5)';
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

## Исправление 2: Правильная работа симуляции при drag

Проблема: нужно воспроизвести оригинальную логику D3 drag (dragstarted, dragged, dragended).

### Обновить обработчики мыши для canvas:

```javascript
// ============================================
// ОБРАБОТЧИКИ МЫШИ (правильная работа с симуляцией)
// ============================================

let isDragging = false;
let isDraggingNode = false;
let draggedNode = null;
let dragStart = { x: 0, y: 0 };
let lastTransform = { ...transform };
let hasDragged = false;

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
        
        // Логика dragstarted из оригинального кода
        // Запускаем симуляцию, если она не была активна
        if (simulation.alpha() < 0.001) {
            tickCount = 0; // Сбрасываем счетчик
            simulation.alphaTarget(0.3).restart();
        }
        
        draggedNode.fx = draggedNode.x;
        draggedNode.fy = draggedNode.y;
        
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
        
        // Логика dragged из оригинального кода
        draggedNode.fx = worldPos.x;
        draggedNode.fy = worldPos.y;
        
        // Обновляем также x и y для плавного отображения
        draggedNode.x = worldPos.x;
        draggedNode.y = worldPos.y;
        
        // Перерисовываем
        render();
        
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
            // Логика dragended из оригинального кода
            // Останавливаем целевое значение alpha, но не останавливаем симуляцию
            simulation.alphaTarget(0);
            
            // Освобождаем фиксацию позиции
            draggedNode.fx = null;
            draggedNode.fy = null;
            
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
        simulation.alphaTarget(0);
        draggedNode.fx = null;
        draggedNode.fy = null;
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

## Исправление 3: Обновить findLinkAt для обеих формул кривизны

Поскольку теперь мы используем разные формулы кривизны для разных уровней детализации, функция `findLinkAt` должна проверять обе возможные кривые:

```javascript
function findLinkAt(x, y) {
    const threshold = Math.max(10, 15 / transform.k); // Адаптивный порог
    let closestLink = null;
    let minDistance = threshold;
    
    for (let link of links) {
        const source = link.source;
        const target = link.target;
        
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        
        // Определяем, какую формулу кривизны использовать
        const currentLOD = LOD.getCurrentLevel();
        const isMaxDetail = !lodEnabled || currentLOD === 'ultra';
        
        let controlX, controlY;
        
        if (isMaxDetail) {
            // Формула для максимального уровня (dr * 1.5)
            const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;
            const angle = Math.atan2(dy, dx);
            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;
            controlX = midX - Math.sin(angle) * dr * 0.15;
            controlY = midY + Math.cos(angle) * dr * 0.15;
        } else {
            // Формула для остальных уровней (dr * 0.3)
            const dr = Math.sqrt(dx * dx + dy * dy) * 0.3;
            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;
            const offsetX = -dy / Math.sqrt(dx * dx + dy * dy) * dr;
            const offsetY = dx / Math.sqrt(dx * dx + dy * dy) * dr;
            controlX = midX + offsetX;
            controlY = midY + offsetY;
        }
        
        // Проверяем расстояние до кривой Безье в нескольких точках
        const numSamples = 20;
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

## Важное замечание по симуляции

Также нужно убедиться, что в коде simulation.on("tick") НЕ останавливается симуляция принудительно после maxTicks, если идет drag. Найдите в коде:

```javascript
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
```

И замените последнюю часть на:

```javascript
simulation.on("tick", () => {
    const now = Date.now();
    if (now - lastTickUpdate < TICK_UPDATE_INTERVAL) {
        return;
    }
    lastTickUpdate = now;
    tickCount++;
    
    // Вместо обновления DOM, просто перерисовываем canvas
    requestAnimationFrame(render);
    
    // Останавливаем только если не идет перетаскивание
    if (tickCount >= maxTicks && !isDraggingNode) {
        simulation.stop();
    }
});
```

---

## Резюме исправлений

### Исправление 1: Правильные уровни детализации
- ✅ Для максимального уровня: кривизна `dr * 1.5`, точные CSS стили
- ✅ Для остальных уровней: кривизна `dr * 0.3`, первоначальные алгоритмы
- ✅ Разная логика отрисовки связей в зависимости от уровня детализации

### Исправление 2: Работа симуляции при drag
- ✅ При начале drag: `alphaTarget(0.3).restart()` если симуляция была остановлена
- ✅ При окончании drag: `alphaTarget(0)` но НЕ `stop()`
- ✅ Симуляция продолжает работать после отпускания узла
- ✅ Плавное перетаскивание с обновлением позиции в реальном времени

### Исправление 3: Обновление findLinkAt
- ✅ Использует правильную формулу кривизны в зависимости от текущего уровня детализации
- ✅ Точное определение клика на связях

Эти исправления должны полностью решить обе проблемы!
