# Уменьшение размера белых точек на мелком масштабе

## Обновить функцию drawNodes():

Заменить блок для `isMinimalScale`:

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
        
        // КЛЮЧЕВОЕ РАЗЛИЧИЕ: на мелких масштабах - БЕЛЫЕ маленькие точки
        const isMinimalScale = lodEnabled && (currentLOD === 'minimal' || currentLOD === 'low');
        
        if (isMinimalScale) {
            // БЕЛЫЕ МАЛЕНЬКИЕ точки на мелком масштабе
            // Используем уменьшенный радиус - например, 60% от обычного
            const smallRadius = nodeRadius * 0.6;
            
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(node.x, node.y, smallRadius / transform.k, 0, Math.PI * 2);
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

## Альтернативный вариант: еще меньше

Если хотите сделать точки еще меньше (например, 40% от обычного размера), замените строку:

```javascript
const smallRadius = nodeRadius * 0.6;
```

на:

```javascript
const smallRadius = nodeRadius * 0.4;
```

## Или фиксированный размер

Можно также задать фиксированный размер в пикселях для белых точек:

```javascript
// Вместо:
const smallRadius = nodeRadius * 0.6;

// Использовать фиксированный размер:
const smallRadius = 5; // Всегда 5 пикселей независимо от LOD.getNodeRadius()
```

---

## Варианты размеров:

- **60%** (0.6) - небольшое уменьшение, точки хорошо видны
- **50%** (0.5) - половина размера, сбалансировано
- **40%** (0.4) - заметно меньше, более компактно
- **Фиксированный 5px** - самый минималистичный вариант

Рекомендую начать с **50%** (0.5) - это даст хороший баланс между видимостью и компактностью!
