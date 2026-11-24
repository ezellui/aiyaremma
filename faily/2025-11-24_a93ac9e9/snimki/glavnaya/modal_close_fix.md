# Исправление: Модальное окно не закрывается после выбора на графе

## Проблема

После выбора концепции на графе окно не закрывается, потому что:

1. `selectConceptOnGraph` устанавливает `modal.style.display = 'none'` (inline стиль)
2. `cancelGraphSelection` устанавливает `modal.style.display = 'block'` (inline стиль)
3. `closeEditConnectionModal` использует `modal.classList.remove('show')`
4. **Inline стили имеют приоритет над CSS классами** → окно не скрывается

## Решение A (Рекомендуется): Использовать z-index вместо display

Вместо полного скрытия модального окна, просто опустим его под граф.

### Исправить selectConceptOnGraph (строка ~4474):

**ЗАМЕНИТЬ:**
```javascript
function selectConceptOnGraph(target) {
    editMode.graphSelectionMode = true;
    editMode.graphSelectionTarget = target;
    
    const modeIndicator = document.getElementById('graphSelectionMode');
    const title = document.getElementById('selectionModeTitle');
    const desc = document.getElementById('selectionModeDesc');
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    title.textContent = target === 'source' ? 
        'Выберите начальную концепцию' : 
        'Выберите конечную концепцию';
    desc.textContent = 'Кликните на концепцию в графе';
    
    modeIndicator.style.display = 'block';
    
    // Скрываем модальное окно и overlay
    modal.style.display = 'none';      // ❌ ПРОБЛЕМА
    overlay.classList.remove('show');
}
```

**НА:**
```javascript
function selectConceptOnGraph(target) {
    editMode.graphSelectionMode = true;
    editMode.graphSelectionTarget = target;
    
    const modeIndicator = document.getElementById('graphSelectionMode');
    const title = document.getElementById('selectionModeTitle');
    const desc = document.getElementById('selectionModeDesc');
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    title.textContent = target === 'source' ? 
        'Выберите начальную концепцию' : 
        'Выберите конечную концепцию';
    desc.textContent = 'Кликните на концепцию в графе';
    
    modeIndicator.style.display = 'block';
    
    // Опускаем модальное окно под граф и убираем overlay
    modal.style.zIndex = '1';           // ✅ Вместо display
    modal.style.opacity = '0.3';        // ✅ Делаем полупрозрачным
    overlay.classList.remove('show');
}
```

### Исправить cancelGraphSelection (строка ~4493):

**ЗАМЕНИТЬ:**
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // Восстанавливаем модальное окно и overlay
    modal.style.display = 'block';     // ❌ ПРОБЛЕМА
    overlay.classList.add('show');
}
```

**НА:**
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // Возвращаем модальное окно наверх и восстанавливаем overlay
    modal.style.zIndex = '';            // ✅ Убираем z-index (вернется к 10001)
    modal.style.opacity = '';           // ✅ Убираем opacity (вернется к 1)
    overlay.classList.add('show');
}
```

---

## Решение B (Альтернативное): Очищать inline стили

Если хотите использовать display, то нужно **очищать** inline стили, а не устанавливать их.

### Исправить selectConceptOnGraph:

```javascript
function selectConceptOnGraph(target) {
    // ... существующий код ...
    
    modeIndicator.style.display = 'block';
    
    // Скрываем модальное окно через класс
    modal.classList.remove('show');     // ✅ Используем класс
    overlay.classList.remove('show');
}
```

### Исправить cancelGraphSelection:

```javascript
function cancelGraphSelection() {
    // ... существующий код ...
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // Показываем модальное окно через класс
    modal.classList.add('show');        // ✅ Используем класс
    overlay.classList.add('show');
}
```

---

## Решение C: Убирать inline стиль при закрытии

Если не хотите менять selectConceptOnGraph и cancelGraphSelection, можно исправить closeEditConnectionModal:

### Добавить в closeEditConnectionModal (строка 4433):

```javascript
function closeEditConnectionModal() {
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    modal.style.display = '';           // ✅ ДОБАВИТЬ: Очищаем inline стиль
    modal.style.zIndex = '';            // ✅ ДОБАВИТЬ: Очищаем z-index если был
    modal.style.opacity = '';           // ✅ ДОБАВИТЬ: Очищаем opacity если был
    overlay.classList.remove('show');
    
    editMode.active = false;
    editMode.type = null;
    editMode.data = null;
    editMode.isNew = false;
    editMode.connectionSourceId = null;
    editMode.connectionTargetId = null;
}
```

---

## Рекомендация

**Используйте Решение A (z-index)** - это самое чистое решение:

1. ✅ Модальное окно остается в DOM с классом `show`
2. ✅ Просто опускается под граф
3. ✅ Не конфликтует с механизмом закрытия
4. ✅ Дает визуальную обратную связь (полупрозрачное окно видно)

**Или используйте Решение C** - добавить очистку inline стилей при закрытии. Это универсальное решение, которое защитит от любых inline стилей.

---

## Проверка после исправления

1. Открыть окно редактирования связи
2. Нажать "Указать на графе"
3. Выбрать концепцию на графе
4. Нажать кнопку закрытия "×" → окно должно закрыться
5. Открыть окно снова
6. Нажать "Указать на графе"  
7. Выбрать концепцию
8. Нажать ESC → окно должно закрыться
9. Открыть окно снова
10. Нажать "Указать на графе"
11. Нажать "Отмена" в индикаторе
12. Нажать кнопку закрытия → окно должно закрыться

Все должно работать!
