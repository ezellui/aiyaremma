# ИСПРАВЛЕНИЕ: handleNodeClick is not defined

## Проблема

1. В исходной инициализации графа (строка 3029) используется **анонимная функция**
2. В `updateGraphVisualization` (строка 3798) пытаемся использовать **несуществующую функцию** `handleNodeClick`
3. Shift-логика не была интегрирована в обработчик кликов

## ✅ РЕШЕНИЕ: Создать функцию handleNodeClick

### Шаг 1: Создать функцию handleNodeClick ПЕРЕД строкой 3025

**Найти строку 3025** (где начинаются переменные для двойного клика):
```javascript
        let clickTimer = null;
        let clickCount = 0;
        let lastClickedNode = null;
```

**ДОБАВИТЬ ПЕРЕД НИМИ (перед строкой 3025):**

```javascript
        // ============================================
        // ОБРАБОТЧИК КЛИКОВ НА УЗЛАХ
        // ============================================
        
        function handleNodeClick(event, d) {
            event.stopPropagation();
            
            // ========== ОБРАБОТКА SHIFT+КЛИК ==========
            if (event.shiftKey) {
                if (editMode.graphSelectionMode) {
                    // Режим выбора концепции из модального окна связи
                    handleConceptSelection(d.id);
                    return;
                } else if (editMode.pendingConceptSelection.length > 0) {
                    // Второй shift+click
                    const firstConceptId = editMode.pendingConceptSelection[0];
                    if (firstConceptId === d.id) {
                        // Повторный клик на том же узле - открываем редактирование
                        editMode.pendingConceptSelection = [];
                        node.classed('selected', false);
                        openEditConceptModal(d.id);
                    } else {
                        // Клик на другом узле - создаем связь между ними
                        editMode.pendingConceptSelection = [];
                        node.classed('selected', false);
                        openEditConnectionModal(firstConceptId, d.id);
                    }
                    return;
                } else {
                    // Первый shift+click - запоминаем узел для возможной связи
                    editMode.pendingConceptSelection = [d.id];
                    node.classed('selected', n => n.id === d.id);
                    console.log(`Выбран узел: ${d.label}. Shift+клик на другой узел для связи, или повторный shift+клик для редактирования.`);
                    return;
                }
            }
            
            // Отменяем выбор если кликнули без shift
            if (editMode.pendingConceptSelection.length > 0) {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
            }
            // ========== КОНЕЦ ОБРАБОТКИ SHIFT+КЛИК ==========
            
            // ========== ОБЫЧНАЯ ЛОГИКА КЛИКА ==========
            clickCount++;
            
            // Очищаем предыдущий таймер при новом клике
            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
            }
            
            if (clickCount === 1) {
                lastClickedNode = d;
                // Первый клик - ждём, будет ли второй
                clickTimer = setTimeout(() => {
                    // Одинарный клик - умная логика выделения
                    
                    if (event.ctrlKey || event.metaKey) {
                        // Ctrl зажат - множественный выбор узлов (не трогаем связи)
                        if (selectedNodes.has(lastClickedNode)) {
                            selectedNodes.delete(lastClickedNode);
                        } else {
                            selectedNodes.add(lastClickedNode);
                        }
                    } else {
                        // Ctrl не зажат - умная логика
                        
                        // Проверяем, участвует ли узел в выделенных связях
                        const connectedToSelectedEdges = isNodeConnectedToSelectedEdges(lastClickedNode);
                        
                        if (connectedToSelectedEdges && selectedEdges.size > 0) {
                            // Узел участвует в выделенной связи - ОСТАВЛЯЕМ связи, добавляем узел
                            if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                                // Если это единственный выделенный узел, и кликнули на него - снимаем
                                selectedNodes.clear();
                            } else {
                                selectedNodes.clear();
                                selectedNodes.add(lastClickedNode);
                            }
                        } else {
                            // Узел НЕ участвует в выделенной связи - ОЧИЩАЕМ связи, выделяем только узел
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
                // Двойной клик - показываем детальную информацию
                showDetailModal(d);
                clickCount = 0;
                clickTimer = null;
                lastClickedNode = null;
            }
        }
        
        let clickTimer = null;
        let clickCount = 0;
        let lastClickedNode = null;
```

---

### Шаг 2: Заменить анонимную функцию на handleNodeClick

**Строка 3029** - найти:
```javascript
        node.on("click", function(event, d) {
            event.stopPropagation();
            
            clickCount++;
            
            // ... весь остальной код до строки ~3094
        });
```

**ЗАМЕНИТЬ на:**
```javascript
        node.on("click", handleNodeClick);
```

**ВСЕ строки от 3029 до примерно 3094** (всю анонимную функцию) нужно **УДАЛИТЬ** и заменить одной строкой выше.

---

### Шаг 3: Проверить updateGraphVisualization

**Строка 3798** уже содержит:
```javascript
.on("click", handleNodeClick)
```

Это правильно, ничего менять не нужно ✅

---

## 📝 Итоговая структура кода

После исправления структура будет такой:

```javascript
// Строка ~3025:
function handleNodeClick(event, d) {
    // Shift-логика
    // Обычная логика клика (двойной клик, выделение)
}

let clickTimer = null;
let clickCount = 0;
let lastClickedNode = null;

// Строка ~3029 (после всех изменений):
node.on("click", handleNodeClick);

// ... далее остальной код инициализации графа ...

// Строка ~3798 в updateGraphVisualization:
.on("click", handleNodeClick)  // ✅ Теперь работает!
```

---

## ⚠️ ВАЖНО: Удалить дублирующий код

Если где-то есть блок кода (примерно строки 4524-4561), который начинается с:
```javascript
// Модифицируем существующую функцию handleNodeClick
const originalHandleNodeClick = handleNodeClick;
function handleNodeClick(event, d) {
```

**УДАЛИТЕ его полностью**. Этот код был временным решением и больше не нужен.

---

## ✅ Проверка после исправления

1. Обычный клик на узел → работает выделение
2. Двойной клик на узел → открывается детальная информация
3. Shift+клик на узел → узел выделяется желтым
4. Shift+клик на второй узел → открывается окно создания связи
5. Shift+клик дважды на один узел → открывается окно редактирования
6. Создание философа → граф обновляется без ошибок ✅
7. Добавление концепции → граф обновляется без ошибок ✅

---

## 🎯 Краткая версия (что делать)

1. **Создать функцию** `handleNodeClick` перед строкой 3025
2. **Скопировать** в неё всю логику из анонимной функции (строки 3030-3093)
3. **Добавить** в начало функции shift-логику
4. **Заменить** строку 3029 на `node.on("click", handleNodeClick);`
5. **Удалить** остальную часть анонимной функции (строки 3030-3094)
6. **Проверить** что в updateGraphVisualization (строка 3798) уже есть `handleNodeClick`

Готово! 🎉
