# Исправления для трех обнаруженных проблем

## ПРОБЛЕМА #1: `philosopher is null` при shift+клик на философе в легенде

### Причина:
У чекбоксов философов нет атрибута `value`, поэтому `checkbox.value` возвращает дефолтное "on" вместо имени философа.

### Где ошибка:
Строка 2330 в функции `initFilters()`:
```javascript
<input type="checkbox" id="phil-${name}" checked onchange="togglePhilosopher('${name}')">
```
❌ Отсутствует `value="${name}"`

### Исправление:
Строка 2330 - изменить на:
```javascript
<input type="checkbox" id="phil-${name}" value="${name}" checked onchange="togglePhilosopher('${name}')">
```

---

## ПРОБЛЕМА #2: Shift+клик на пустом месте секции философов не работает

### Причина:
1. Селектор `.legend-section` выбирает ПЕРВУЮ секцию, но в HTML их несколько (философы, связи, рубрики и т.д.)
2. Нужно выбрать именно секцию философов по ID или более специфичному селектору
3. Клик может попадать на дочерние элементы (заголовок, кнопки), а не на саму секцию

### Где ошибка:
Строки 4576-4584 в функции `makeLegendsEditable()`:
```javascript
const philosophersSection = document.querySelector('.legend-section');  // ❌ Выбирает первую секцию
if (philosophersSection) {
    philosophersSection.addEventListener('click', function(event) {
        if (event.shiftKey && event.target === this) {  // ❌ event.target === this почти никогда не true
            openEditPhilosopherModal();
        }
    });
}
```

### Исправление:
Строки 4576-4584 - заменить на:
```javascript
// Shift+click на пустом месте блока философов для добавления нового
const philContainer = document.getElementById('philosopherFilters');
if (philContainer) {
    philContainer.addEventListener('click', function(event) {
        // Проверяем что клик был на самом контейнере или на элементах между айтемами
        if (event.shiftKey && !event.target.closest('.legend-item')) {
            event.preventDefault();
            event.stopPropagation();
            openEditPhilosopherModal();
        }
    });
}
```

**Альтернативный вариант (если хотите кликать на заголовок секции):**
```javascript
// Добавить обработчик на заголовок секции философов
const philHeader = document.querySelector('.legend-section h4');
if (philHeader && philHeader.textContent.includes('Философы')) {
    philHeader.addEventListener('click', function(event) {
        if (event.shiftKey) {
            event.preventDefault();
            event.stopPropagation();
            openEditPhilosopherModal();
        }
    });
    // Визуальная подсказка
    philHeader.style.cursor = 'pointer';
    philHeader.title = 'Shift+клик для добавления философа';
}
```

---

## ПРОБЛЕМА #3: Shift+клик на концепции сразу открывает редактирование вместо выбора двух концепций

### Причина:
Таймер на 2 секунды (строка 4549) срабатывает ВСЕГДА, даже если пользователь все еще держит shift и планирует кликнуть на второй узел. Таймер не проверяет состояние клавиши shift.

### Дополнительная проблема:
Код на строках 4524-4561 определяет функцию `handleNodeClick`, но она НЕ установлена на узлы! Узлы используют обработчик на строке 3029.

### Решение А (рекомендуется): Интегрировать shift-логику в основной обработчик

Найдите обработчик `node.on("click", function(event, d) {` на строке 3029 и добавьте проверку shift В САМОЕ НАЧАЛО:

```javascript
node.on("click", function(event, d) {
    event.stopPropagation();
    
    // ========== ДОБАВИТЬ ЭТО В НАЧАЛО ==========
    if (event.shiftKey) {
        if (editMode.graphSelectionMode) {
            // Режим выбора концепции для связи (из модального окна)
            handleConceptSelection(d.id);
            return;
        } else if (editMode.pendingConceptSelection.length > 0) {
            // Второй shift+click - создаем связь
            const firstConceptId = editMode.pendingConceptSelection[0];
            if (firstConceptId !== d.id) {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConnectionModal(firstConceptId, d.id);
            } else {
                // Кликнули на тот же узел - отменяем выбор
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
            }
            return;
        } else {
            // Первый shift+click - запоминаем узел
            editMode.pendingConceptSelection = [d.id];
            node.classed('selected', n => n.id === d.id);
            
            // Показываем подсказку пользователю
            console.log(`Выбран узел "${d.label}". Shift+клик на другой узел для создания связи, или обычный клик для отмены.`);
            
            // НЕ открываем редактирование автоматически!
            // Пользователь может кликнуть на второй узел или просто отменить выбор
            return;
        }
    }
    // ========== КОНЕЦ ДОБАВЛЕНИЯ ==========
    
    // Далее идет существующая логика для обычных кликов
    clickCount++;
    
    // Очищаем предыдущий таймер при новом клике
    if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
    }
    
    // ... остальной код остается без изменений
});
```

И УДАЛИТЬ строки 4524-4561 (дублирующий код handleNodeClick).

### Альтернативное улучшение: Открывать редактирование при двойном shift+click

Если хотите сохранить возможность редактирования одной концепции через shift+клик:

```javascript
if (event.shiftKey) {
    if (editMode.graphSelectionMode) {
        handleConceptSelection(d.id);
        return;
    } else if (editMode.pendingConceptSelection.length > 0) {
        const firstConceptId = editMode.pendingConceptSelection[0];
        if (firstConceptId === d.id) {
            // Двойной shift+click на том же узле - открываем редактирование
            editMode.pendingConceptSelection = [];
            node.classed('selected', false);
            openEditConceptModal(d.id);
        } else {
            // Shift+click на другом узле - создаем связь
            editMode.pendingConceptSelection = [];
            node.classed('selected', false);
            openEditConnectionModal(firstConceptId, d.id);
        }
        return;
    } else {
        // Первый shift+click
        editMode.pendingConceptSelection = [d.id];
        node.classed('selected', n => n.id === d.id);
        
        // Подсказка
        const tooltip = d3.select("#tooltip");
        tooltip.style("display", "block")
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px")
            .html(`<strong>${d.label}</strong><br>
                   Shift+клик на другой узел - создать связь<br>
                   Shift+клик снова - редактировать<br>
                   Обычный клик - отмена`);
        
        setTimeout(() => tooltip.style("display", "none"), 3000);
        return;
    }
}
```

### Решение Б: Отменять таймер при отпускании shift

Если хотите сохранить существующую логику с таймером:

```javascript
// Строки 4542-4556 заменить на:
} else {
    // Первый shift+click на концепции
    editMode.pendingConceptSelection = [d.id];
    node.classed('selected', n => n.id === d.id);
    
    // Создаем обработчик для отслеживания отпускания shift
    let shiftReleased = false;
    const shiftUpHandler = (e) => {
        if (!e.shiftKey) {
            shiftReleased = true;
            document.removeEventListener('keyup', shiftUpHandler);
        }
    };
    document.addEventListener('keyup', shiftUpHandler);
    
    // Запускаем таймер
    const timerId = setTimeout(() => {
        document.removeEventListener('keyup', shiftUpHandler);
        
        // Открываем редактирование ТОЛЬКО если:
        // 1. Выбор все еще активен
        // 2. Shift был отпущен (не держится все это время)
        if (editMode.pendingConceptSelection.length > 0 && 
            editMode.pendingConceptSelection[0] === d.id &&
            shiftReleased) {
            editMode.pendingConceptSelection = [];
            node.classed('selected', false);
            openEditConceptModal(d.id);
        }
    }, 2000);
    
    // Сохраняем ID таймера для возможной отмены
    editMode.pendingTimerId = timerId;
}
```

---

## ДОПОЛНИТЕЛЬНО: Отмена выбора при обычном клике

Добавьте в конец обработчика клика на узлы (после всей shift-логики, но в начале обычной логики):

```javascript
// Если был активен выбор для связи, но кликнули без shift - отменяем
if (editMode.pendingConceptSelection.length > 0) {
    editMode.pendingConceptSelection = [];
    node.classed('selected', false);
}
```

---

## Итоговый порядок исправлений:

1. **Исправление #1**: Добавить `value="${name}"` к чекбоксу на строке 2330
2. **Исправление #2**: Исправить обработчик shift+клик на пустом месте (строки 4576-4584)
3. **Исправление #3А**: Интегрировать shift-логику в основной обработчик (строка 3029) и удалить строки 4524-4561
   ИЛИ
4. **Исправление #3Б**: Добавить отслеживание отпускания shift в таймере (строки 4542-4556)

Рекомендую использовать **Решение А** для проблемы #3, так как оно проще и понятнее для пользователя.
