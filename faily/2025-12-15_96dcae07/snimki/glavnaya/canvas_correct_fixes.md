# ПРАВИЛЬНЫЕ исправления: белые точки и работающая симуляция

## Исправление 1: БЕЛЫЕ точки на мелком масштабе

### Полная замена функции `drawNodes()`:

```javascript
function drawNodes() {
    const currentLOD = LOD.getCurrentLevel();
    const isMaxDetail = !lodEnabled || currentLOD === 'ultra';
    
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
        
        let opacity = 1.0;
        if (isDimmed) opacity = 0.2;
        
        const color = philosopherConcepts[node.concept].color;
        
        ctx.save();
        ctx.globalAlpha = opacity;
        
        // КЛЮЧЕВОЕ РАЗЛИЧИЕ: на мелких масштабах - БЕЛЫЕ точки
        const isMinimalScale = lodEnabled && (currentLOD === 'minimal' || currentLOD === 'low');
        
        if (isMinimalScale) {
            // БЕЛЫЕ маленькие точки на мелком масштабе - без обводки, без свечения
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeRadius / transform.k, 0, Math.PI * 2);
            ctx.fill();
            // НЕТ обводки для minimal/low
            
        } else if (isMaxDetail) {
            // МАКСИМАЛЬНАЯ ДЕТАЛИЗАЦИЯ - точное свечение как в исходных CSS
            if ((isHighlighted || isSelected) && drawGlow) {
                const shadowBlur = isSelected ? 15 : 20;
                ctx.shadowBlur = shadowBlur / transform.k;
                ctx.shadowColor = isSelected ? '#ffd700' : 'rgba(255,255,255,0.8)';
            }
            
            if (isHovered) {
                ctx.shadowBlur = 10 / transform.k;
                ctx.shadowColor = 'rgba(255,255,255,0.4)';
            }
            
            // Цветной круг узла
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeRadius / transform.k, 0, Math.PI * 2);
            ctx.fill();
            
            // Обводка
            if (isSelected) {
                ctx.strokeStyle = '#ffd700';
                ctx.lineWidth = 6 / transform.k;
            } else if (isHighlighted) {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 5 / transform.k;
            } else {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 3 / transform.k;
            }
            ctx.stroke();
            
            ctx.shadowBlur = 0;
            ctx.shadowColor = 'transparent';
            
        } else {
            // СРЕДНИЕ УРОВНИ ДЕТАЛИЗАЦИИ (medium, high) - градиентное свечение, цветные узлы
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
            
            // Цветной круг узла
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeRadius / transform.k, 0, Math.PI * 2);
            ctx.fill();
            
            // Обводка
            if (isSelected) {
                ctx.strokeStyle = '#ffd700';
                ctx.lineWidth = 6 / transform.k;
            } else if (isHighlighted) {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 5 / transform.k;
            } else {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 3 / transform.k;
            }
            ctx.stroke();
            
            ctx.shadowBlur = 0;
        }
        
        // Текст (метка узла) - только если не minimal/low
        if (!isMinimalScale && drawLabels && fontSize > 0) {
            ctx.fillStyle = '#fff';
            ctx.font = `600 ${fontSize / transform.k}px 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            
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

## Исправление 2: РАБОТАЮЩАЯ симуляция при drag

Проблема в том, что `tickCount` достигает `maxTicks` и симуляция останавливается навсегда. Нужно УБРАТЬ ограничение по tickCount и полагаться только на естественное затухание alpha.

### Заменить обработчик simulation.on("tick"):

```javascript
simulation.on("tick", () => {
    const now = Date.now();
    if (now - lastTickUpdate < TICK_UPDATE_INTERVAL) {
        return;
    }
    lastTickUpdate = now;
    
    // УБИРАЕМ счетчик tickCount и ограничение maxTicks
    // Симуляция остановится естественным образом, когда alpha станет мал
    
    requestAnimationFrame(render);
});
```

### Заменить обработчик mousedown:

```javascript
canvas.addEventListener('mousedown', (e) => {
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    
    hasDragged = false;
    
    const clickedNode = findNodeAt(worldPos.x, worldPos.y);
    
    if (clickedNode && !e.shiftKey) {
        // Начинаем перетаскивание узла
        isDraggingNode = true;
        draggedNode = clickedNode;
        
        // ВСЕГДА перезапускаем симуляцию при drag
        // Это гарантирует, что остальные узлы будут реагировать
        simulation.alphaTarget(0.3).restart();
        
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
```

### Заменить обработчик mouseup:

```javascript
canvas.addEventListener('mouseup', (e) => {
    if (isDraggingNode) {
        isDraggingNode = false;
        if (draggedNode) {
            // Останавливаем целевое значение alpha
            // Симуляция продолжит работать и естественно затухнет
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
    
    const mousePos = { x: e.offsetX, y: e.offsetY };
    const worldPos = inverseTransform(mousePos.x, mousePos.y);
    updateHoverState(worldPos.x, worldPos.y);
});
```

---

## Дополнительно: Удалить переменные tickCount и maxTicks

Найдите в коде эти строки и УДАЛИТЕ их:

```javascript
// УДАЛИТЬ:
let tickCount = 0;
const maxTicks = 300;
```

И УДАЛИТЕ эти строки из simulation.on("tick"):

```javascript
// УДАЛИТЬ:
tickCount++;
```

---

## Также обновить simulation.on("end"):

```javascript
simulation.on("end", () => {
    console.log("Симуляция завершена естественным образом");
    console.log("Производительность - узлов:", nodes.length, "связей:", links.length);
    if (performance.memory) {
        console.log("Использование памяти:", 
            Math.round(performance.memory.usedJSHeapSize / 1048576), "МБ");
    }
    render();
});
```

---

## Резюме ПРАВИЛЬНЫХ исправлений

### 1. Белые точки на мелком масштабе ✅
- **minimal и low уровни**: БЕЛЫЕ точки без обводки, без свечения
- **medium и high уровни**: цветные узлы с градиентным свечением
- **ultra уровень**: цветные узлы с точным shadowBlur свечением (как в CSS)

### 2. Работающая симуляция ✅
- **УБРАНО ограничение maxTicks** - симуляция работает постоянно
- При начале drag: **ВСЕГДА** `alphaTarget(0.3).restart()`
- При окончании drag: `alphaTarget(0)` - симуляция естественно затухает
- Симуляция продолжает работать после отпускания узла
- Остальные узлы реагируют на перемещение в реальном времени

Эти исправления ДЕЙСТВИТЕЛЬНО решают обе проблемы!
