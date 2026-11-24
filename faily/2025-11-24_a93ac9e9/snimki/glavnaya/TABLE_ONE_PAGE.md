# ТАБЛИЦА ИЗМЕНЕНИЙ БАЗОВОГО ФУНКЦИОНАЛА (одна страница)

| # | Категория | Строка | Что изменить | Зачем | Критичность |
|---|-----------|--------|-------------|-------|-------------|
| 1 | Данные | 1779 | `const nodes` → `let nodes` | Переприсваивание в updateGraphData | 🔴 Критично |
| 2 | Данные | 1788 | `const links` → `let links` | Переприсваивание в updateGraphData | 🔴 Критично |
| 3 | Данные | После 1795 | Добавить `let connections = ...` | Нужна для 17 функций редактирования | 🔴 Критично |
| 4 | Данные | 1755-1761 | Добавить `name`, `birth`, `death` в объект | Используется в редактировании | 🔴 Критично |
| 5 | D3 | 2811 | `const link` → `let link` | D3 update pattern | 🔴 Критично |
| 6 | D3 | 3003 | `const node` → `let node` | D3 update pattern | 🔴 Критично |
| 7 | Клики | Перед 3025 | Создать функцию `handleNodeClick()` | Обработка кликов + shift-логика | 🔴 Критично |
| 8 | Клики | 3029 | Заменить на `node.on("click", handleNodeClick)` | Использование именованной функции | 🔴 Критично |
| 9 | Клики | 3030-3094 | Удалить анонимную функцию | Избежать дублирования | 🔴 Критично |
| 10 | Клики | После 3025 | Создать функцию `handleLinkClick()` | Обработка кликов на связях | 🔴 Критично |
| 11 | Визуал | 3807 | Stroke → `"#fff"`, добавить stroke-width | Белый ободок узлов | 🟡 Важно |
| 12 | Визуал | 3819 | Stroke → `"#fff"`, добавить stroke-width | Белый ободок узлов | 🟡 Важно |
| 13 | Легенда | 2325 | Добавить `philContainer.innerHTML = ''` | Избежать дублирования философов | 🔴 Критично |
| 14 | Легенда | 2340 | Добавить `relContainer.innerHTML = ''` | Избежать дублирования связей | 🔴 Критично |
| 15 | Легенда | 2330 | Добавить `value="${name}"` в input | Shift+клик на философе работает | 🔴 Критично |
| 16 | Функции | 3688-3690 | Исправить `findPhilosopherByName()` | Эффективность O(1) вместо O(n) | 🔴 Критично |
| 17 | UX | После 3022 | Добавить `node.on("contextmenu", ...)` | Правый клик → детали | 🟢 Опционально |

---

## КОД ДЛЯ БЫСТРОЙ ЗАМЕНЫ

### #1-2: const → let для данных
```javascript
let nodes = concepts.map(c => ({    // строка 1779
let links = relations.map(r => ({    // строка 1788
```

### #3: Добавить connections (после строки 1795)
```javascript
let connections = relations.map(r => ({
    from: r.source,
    to: r.target,
    type: r.type,
    weight: r.weight || 2,
    bidirectional: r.bidirectional || false,
    description: r.description
}));
```

### #4: Исправить philosopherConcepts (строки 1755-1761)
```javascript
const philosopherConcepts = {};
philosophers.forEach(p => {
    philosopherConcepts[p.nameRu] = {
        name: p.nameRu,        // добавить
        color: p.color,
        years: p.years,
        birth: p.birth,        // добавить
        death: p.death         // добавить
    };
});
```

### #5-6: const → let для D3
```javascript
let link = g.append("g")    // строка 2811
let node = g.append("g")    // строка 3003
```

### #7: Создать handleNodeClick (перед строкой 3025)
```javascript
function handleNodeClick(event, d) {
    event.stopPropagation();
    
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
    
    if (editMode.pendingConceptSelection.length > 0) {
        editMode.pendingConceptSelection = [];
        node.classed('selected', false);
    }
    
    clickCount++;
    if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
    }
    
    if (clickCount === 1) {
        lastClickedNode = d;
        clickTimer = setTimeout(() => {
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
        showDetailModal(d);
        clickCount = 0;
        clickTimer = null;
        lastClickedNode = null;
    }
}
```

### #8-9: Заменить обработчик (строка 3029)
```javascript
node.on("click", handleNodeClick);
// Удалить строки 3030-3094 (старая анонимная функция)
```

### #10: Создать handleLinkClick (после handleNodeClick)
```javascript
function handleLinkClick(event, d) {
    if (selectedEdges.has(d)) {
        selectedEdges.delete(d);
    } else {
        if (!(event.ctrlKey || event.metaKey)) {
            selectedEdges.clear();
            selectedNodes.clear();
        }
        selectedEdges.add(d);
    }
    highlightCombined();
}
```

### #11-12: Белый ободок (строки 3807 и 3819)
```javascript
.attr("stroke", "#fff")
.attr("stroke-width", 3);
```

### #13-14: Очистка контейнеров (строки 2325 и 2340)
```javascript
philContainer.innerHTML = '';  // строка 2325
relContainer.innerHTML = '';   // строка 2340
```

### #15: Value в чекбоксе (строка 2330)
```javascript
<input type="checkbox" id="phil-${name}" value="${name}" checked ...>
```

### #16: Исправить findPhilosopherByName (строки 3688-3690)
```javascript
function findPhilosopherByName(name) {
    if (philosopherConcepts[name]) {
        return { name: name, ...philosopherConcepts[name] };
    }
    return null;
}
```

### #17: Contextmenu (опционально, после строки 3022)
```javascript
node.on("contextmenu", function(event, d) {
    event.preventDefault();
    showDetailModal(d);
});
```

---

## ПРОВЕРКА: 3 команды

После всех изменений откройте консоль браузера и выполните:

```javascript
// 1. Проверка переменных
console.log(typeof nodes, typeof links, typeof connections);
// Должно вывести: object object object

// 2. Проверка функций
console.log(typeof handleNodeClick, typeof handleLinkClick);
// Должно вывести: function function

// 3. Проверка philosopherConcepts
console.log(Object.values(philosopherConcepts)[0]);
// Должно вывести объект с полями: name, color, years, birth, death
```

Если всё `undefined` или `object` вместо `function` - проверьте изменения еще раз.

---

**🔴 Критично: 14** | **🟡 Важно: 2** | **🟢 Опционально: 1** | **Всего: 17**
