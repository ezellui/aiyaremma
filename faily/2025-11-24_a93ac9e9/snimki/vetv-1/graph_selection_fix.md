# Исправление выбора концепций на графе

## Проблемы:
1. ❌ Затемнение не убирается при нажатии "Указать на графе"
2. ❌ Окно редактирования не возвращается после выбора концепции

## Причины:
- **Overlay** (модальный фон) не скрывается
- **Затемнение графа** (классы .dimmed/.highlighted) не сбрасывается
- Модальное окно не возвращается видимым после выбора

---

## ИСПРАВЛЕНИЕ 1: Функция selectConceptOnGraph (строка 4474)

### Текущий код (НЕПРАВИЛЬНЫЙ):
```javascript
function selectConceptOnGraph(target) {
    editMode.graphSelectionMode = true;
    editMode.graphSelectionTarget = target;
    
    const modeIndicator = document.getElementById('graphSelectionMode');
    const title = document.getElementById('selectionModeTitle');
    const desc = document.getElementById('selectionModeDesc');
    
    title.textContent = target === 'source' ? 
        'Выберите начальную концепцию' : 
        'Выберите конечную концепцию';
    desc.textContent = 'Кликните на концепцию в графе';
    
    modeIndicator.style.display = 'block';
    
    // ❌ НЕПРАВИЛЬНО - только меняет прозрачность
    document.getElementById('editConnectionModal').style.opacity = '0.3';
}
```

### ПРАВИЛЬНЫЙ код:
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
    
    // ✅ ПРАВИЛЬНО - полностью скрываем модальное окно и overlay
    modal.style.display = 'none';
    overlay.classList.remove('show');
    
    // ✅ ВАЖНО - убираем затемнение графа
    resetHighlight();
}
```

---

## ИСПРАВЛЕНИЕ 2: Функция cancelGraphSelection (строка 4493)

### Текущий код (НЕПРАВИЛЬНЫЙ):
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // ❌ НЕПРАВИЛЬНО - только меняет прозрачность
    document.getElementById('editConnectionModal').style.opacity = '1';
}
```

### ПРАВИЛЬНЫЙ код:
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // ✅ ПРАВИЛЬНО - восстанавливаем модальное окно и overlay
    modal.style.display = 'block';
    overlay.classList.add('show');
}
```

---

## ДОПОЛНИТЕЛЬНО: Сохранение состояния выделения (опционально)

Если хотите, чтобы после выбора концепции восстанавливалось выделение связи, которая редактируется:

### Вариант А: Сохранять и восстанавливать выделение

В **selectConceptOnGraph** сохранить текущее состояние:
```javascript
function selectConceptOnGraph(target) {
    // ... существующий код ...
    
    // Сохраняем текущее выделение
    editMode.savedSelection = {
        nodes: new Set(selectedNodes),
        edges: new Set(selectedEdges)
    };
    
    // Убираем затемнение
    resetHighlight();
    
    // ... остальной код ...
}
```

В **cancelGraphSelection** и **handleConceptSelection** восстанавливать:
```javascript
function cancelGraphSelection() {
    // ... существующий код восстановления окна ...
    
    // Восстанавливаем выделение
    if (editMode.savedSelection) {
        selectedNodes = editMode.savedSelection.nodes;
        selectedEdges = editMode.savedSelection.edges;
        highlightCombined();
        editMode.savedSelection = null;
    }
}
```

И то же самое добавить в конец **handleConceptSelection** (после `cancelGraphSelection()`):
```javascript
function handleConceptSelection(conceptId) {
    // ... существующий код ...
    
    cancelGraphSelection();
    
    // cancelGraphSelection уже восстановит выделение
}
```

### Вариант Б: Не восстанавливать выделение (проще)

Просто оставить код как в Исправлениях 1 и 2 - после выбора концепции выделение будет сброшено.

---

## ПРОВЕРКА после исправлений:

1. ✅ Откройте окно редактирования связи (shift+клик на связи или выбор двух узлов)
2. ✅ Нажмите "Указать на графе" для начальной концепции
   - Модальное окно исчезает
   - Серый фон (overlay) исчезает
   - Затемнение узлов исчезает
   - Граф полностью доступен
3. ✅ Кликните на любую концепцию в графе
   - Модальное окно появляется обратно
   - Серый фон (overlay) возвращается
   - Поле "Начальная концепция" заполнено
4. ✅ Нажмите "Указать на графе" для конечной концепции
   - То же самое - все скрывается
5. ✅ Кликните на другую концепцию
   - Окно возвращается
   - Поле "Конечная концепция" заполнено
6. ✅ Можете сохранить связь

---

## Минимальное решение (только 2 функции):

Если нужно быстрое решение БЕЗ сохранения выделения:

**1. Заменить selectConceptOnGraph (строка 4474):**
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
    modal.style.display = 'none';
    overlay.classList.remove('show');
    resetHighlight();
}
```

**2. Заменить cancelGraphSelection (строка 4493):**
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    modal.style.display = 'block';
    overlay.classList.add('show');
}
```

---

## Почему это работает:

### Два вида затемнения:
1. **Overlay** (`#modalOverlay`) - серый полупрозрачный фон
   - Управляется классом `.show`
   - Блокирует клики по графу
   
2. **Затемнение графа** (классы `.dimmed`/`.highlighted`)
   - Управляется функциями `highlightCombined()`, `resetHighlight()`
   - Делает невыделенные узлы/связи полупрозрачными

### Что делали раньше (НЕПРАВИЛЬНО):
- `style.opacity = '0.3'` - только меняет прозрачность окна
- Overlay остается видимым и блокирует граф
- Затемнение графа не убирается

### Что делаем теперь (ПРАВИЛЬНО):
- `style.display = 'none'` - полностью скрывает окно
- `overlay.classList.remove('show')` - убирает серый фон
- `resetHighlight()` - убирает затемнение узлов/связей
- Граф полностью доступен для клика
