# БЫСТРО: Исправить handleNodeClick

## ❌ Ошибка
```
handleNodeClick is not defined (строка 3798)
```

## ✅ Решение в 3 шага

### Шаг 1: Создать функцию handleNodeClick

**ПЕРЕД строкой 3025** добавить:

```javascript
// Обработчик кликов на узлах (с поддержкой shift+click для редактирования)
function handleNodeClick(event, d) {
    event.stopPropagation();
    
    // Обработка shift+клик для редактирования
    if (event.shiftKey) {
        if (editMode.graphSelectionMode) {
            handleConceptSelection(d.id);
            return;
        } else if (editMode.pendingConceptSelection.length > 0) {
            const firstConceptId = editMode.pendingConceptSelection[0];
            if (firstConceptId === d.id) {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConceptModal(d.id);
            } else {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConnectionModal(firstConceptId, d.id);
            }
            return;
        } else {
            editMode.pendingConceptSelection = [d.id];
            node.classed('selected', n => n.id === d.id);
            return;
        }
    }
    
    // Отменяем выбор если кликнули без shift
    if (editMode.pendingConceptSelection.length > 0) {
        editMode.pendingConceptSelection = [];
        node.classed('selected', false);
    }
    
    // Обычная логика клика (двойной клик, выделение)
    clickCount++;
    
    if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
    }
    
    if (clickCount === 1) {
        lastClickedNode = d;
        clickTimer = setTimeout(() => {
            // Одинарный клик - выделение
            if (event.ctrlKey || event.metaKey) {
                if (selectedNodes.has(lastClickedNode)) {
                    selectedNodes.delete(lastClickedNode);
                } else {
                    selectedNodes.add(lastClickedNode);
                }
            } else {
                const connectedToSelectedEdges = isNodeConnectedToSelectedEdges(lastClickedNode);
                
                if (connectedToSelectedEdges && selectedEdges.size > 0) {
                    if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                        selectedNodes.clear();
                    } else {
                        selectedNodes.clear();
                        selectedNodes.add(lastClickedNode);
                    }
                } else {
                    selectedEdges.clear();
                    if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                        selectedNodes.clear();
                    } else {
                        selectedNodes.clear();
                        selectedNodes.add(lastClickedNode);
                    }
                }
            }
            
            highlightCombined();
            clickCount = 0;
            clickTimer = null;
            lastClickedNode = null;
        }, 300);
    } else if (clickCount === 2) {
        // Двойной клик - детальная информация
        showDetailModal(d);
        clickCount = 0;
        clickTimer = null;
        lastClickedNode = null;
    }
}
```

---

### Шаг 2: Заменить анонимную функцию

**Строка 3029** - найти:
```javascript
        node.on("click", function(event, d) {
            event.stopPropagation();
            
            clickCount++;
            // ... много кода ...
        });
```

**Заменить ВСЮ эту анонимную функцию (примерно строки 3029-3094) на:**
```javascript
        node.on("click", handleNodeClick);
```

---

### Шаг 3: Проверить updateGraphVisualization

**Строка 3798** должна содержать:
```javascript
.on("click", handleNodeClick)
```

Если там что-то другое - исправьте на это. ✅

---

## 🗑️ Удалить дублирующий код (если есть)

Если где-то есть блок (примерно строки 4524-4561):
```javascript
const originalHandleNodeClick = handleNodeClick;
function handleNodeClick(event, d) {
    ...
}
```

**УДАЛИТЕ его полностью** - это был временный код, который больше не нужен.

---

## ✅ Готово!

Теперь:
- ✅ Обычные клики работают
- ✅ Двойные клики работают  
- ✅ Shift+клики для редактирования работают
- ✅ Обновление графа работает без ошибок
- ✅ Создание философов/концепций/связей работает

---

## 📍 Где что находится

```
Строка ~3025: function handleNodeClick(event, d) { ... }  ← Создать здесь
Строка ~3029: node.on("click", handleNodeClick);          ← Использовать здесь
Строка ~3798: .on("click", handleNodeClick)               ← Уже есть, проверить
```
