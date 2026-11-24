# Быстрые исправления - код для замены

## ✅ ИСПРАВЛЕНИЕ #1: philosopher is null

**Строка 2330** - найти:
```javascript
<input type="checkbox" id="phil-${name}" checked onchange="togglePhilosopher('${name}')">
```

Заменить на:
```javascript
<input type="checkbox" id="phil-${name}" value="${name}" checked onchange="togglePhilosopher('${name}')">
```

---

## ✅ ИСПРАВЛЕНИЕ #2: Shift+клик на пустом месте не работает

**Строки 4576-4584** - найти:
```javascript
// Shift+click на пустом месте блока философов для добавления нового
const philosophersSection = document.querySelector('.legend-section');
if (philosophersSection) {
    philosophersSection.addEventListener('click', function(event) {
        if (event.shiftKey && event.target === this) {
            openEditPhilosopherModal();
        }
    });
}
```

Заменить на:
```javascript
// Shift+click на пустом месте блока философов для добавления нового
const philContainer = document.getElementById('philosopherFilters');
if (philContainer) {
    philContainer.addEventListener('click', function(event) {
        // Проверяем что клик был НЕ на legend-item
        if (event.shiftKey && !event.target.closest('.legend-item')) {
            event.preventDefault();
            event.stopPropagation();
            openEditPhilosopherModal();
        }
    });
}
```

---

## ✅ ИСПРАВЛЕНИЕ #3: Shift+клик на концепции - убрать таймер

### Шаг 1: Найти обработчик кликов на узлах (примерно строка 3029)

Найти:
```javascript
node.on("click", function(event, d) {
    event.stopPropagation();
    
    clickCount++;
```

### Шаг 2: Добавить ПЕРЕД `clickCount++` следующий код:

```javascript
node.on("click", function(event, d) {
    event.stopPropagation();
    
    // ============ ДОБАВИТЬ ЭТОТ БЛОК ============
    // Обработка shift+клик для редактирования и создания связей
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
    // ============ КОНЕЦ ДОБАВЛЕНИЯ ============
    
    clickCount++;
    // ... остальной код остается без изменений
```

### Шаг 3: Удалить строки 4524-4561

Найти и УДАЛИТЬ весь этот блок:
```javascript
// Модифицируем существующую функцию handleNodeClick
const originalHandleNodeClick = handleNodeClick;
function handleNodeClick(event, d) {
    if (event.shiftKey) {
        // ... весь код до строки 4561
    }
}
```

---

## 📝 Проверка после исправлений

После внесения изменений проверьте:

1. ✅ Shift+клик на философе в легенде → открывается окно редактирования с заполненными полями
2. ✅ Shift+клик на пустом месте между философами в легенде → открывается окно добавления философа
3. ✅ Первый shift+клик на концепции → узел выделяется, ожидается второй клик
4. ✅ Второй shift+клик на другой концепции → открывается окно создания связи между ними
5. ✅ Повторный shift+клик на той же концепции → открывается окно редактирования концепции
6. ✅ Обычный клик (без shift) после выбора узла → снимается выделение

---

## 🎯 Логика работы после исправлений

### Shift+клик на узлах графа:
1. **Первый shift+клик** → узел выделяется желтым
2. **Второй shift+клик на ДРУГОМ узле** → окно создания связи
3. **Второй shift+клик на ТОМ ЖЕ узле** → окно редактирования концепции
4. **Обычный клик** → отмена выбора

### Shift+клик в легенде философов:
1. **На философе** → окно редактирования философа
2. **На пустом месте** → окно добавления нового философа

### Shift+клик на связи:
- Открывает окно редактирования связи (уже работает)
