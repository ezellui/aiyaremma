# Добавление поиска концепций в окне редактирования связей и управление overlay

## ЧАСТЬ 1: Убрать readonly с полей поиска

### Строки 4761 и 4773

**Было:**
```html
<input type="text" id="connectionSourceSearch" class="concept-search-input" placeholder="Поиск концепции..." readonly>
```
```html
<input type="text" id="connectionTargetSearch" class="concept-search-input" placeholder="Поиск концепции..." readonly>
```

**Должно быть:**
```html
<input type="text" id="connectionSourceSearch" class="concept-search-input" placeholder="Поиск концепции...">
```
```html
<input type="text" id="connectionTargetSearch" class="concept-search-input" placeholder="Поиск концепции...">
```

---

## ЧАСТЬ 2: Добавить функции поиска концепций

### Добавить ПОСЛЕ функции handleConceptSelection (после строки 4518):

```javascript
// ============================================
// ПОИСК КОНЦЕПЦИЙ В ПОЛЯХ СВЯЗИ
// ============================================

function initConnectionSearchFields() {
    const sourceInput = document.getElementById('connectionSourceSearch');
    const targetInput = document.getElementById('connectionTargetSearch');
    const sourceResults = document.getElementById('connectionSourceResults');
    const targetResults = document.getElementById('connectionTargetResults');
    
    if (sourceInput) {
        // Обработчик ввода для начальной концепции
        sourceInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            handleConnectionConceptSearch(query, 'source', sourceResults);
        });
        
        // Фокус - показать результаты если есть текст
        sourceInput.addEventListener('focus', function(e) {
            const query = e.target.value.trim();
            if (query) {
                handleConnectionConceptSearch(query, 'source', sourceResults);
            }
        });
        
        // Клик вне поля - скрыть результаты
        sourceInput.addEventListener('blur', function(e) {
            // Задержка, чтобы клик по результату успел сработать
            setTimeout(() => {
                sourceResults.classList.remove('show');
            }, 200);
        });
    }
    
    if (targetInput) {
        // Обработчик ввода для конечной концепции
        targetInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            handleConnectionConceptSearch(query, 'target', targetResults);
        });
        
        // Фокус - показать результаты если есть текст
        targetInput.addEventListener('focus', function(e) {
            const query = e.target.value.trim();
            if (query) {
                handleConnectionConceptSearch(query, 'target', targetResults);
            }
        });
        
        // Клик вне поля - скрыть результаты
        targetInput.addEventListener('blur', function(e) {
            setTimeout(() => {
                targetResults.classList.remove('show');
            }, 200);
        });
    }
}

function handleConnectionConceptSearch(query, target, resultsContainer) {
    if (!query || query.trim() === '') {
        resultsContainer.classList.remove('show');
        resultsContainer.innerHTML = '';
        return;
    }
    
    // Используем существующую функцию searchNodes
    const results = searchNodes(query);
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="concept-search-item" style="color: #95a5a6; cursor: default;">Ничего не найдено</div>';
        resultsContainer.classList.add('show');
        return;
    }
    
    // Отображаем результаты
    resultsContainer.innerHTML = results.slice(0, 10).map(node => `
        <div class="concept-search-item" onclick="selectConnectionConcept('${node.id}', '${target}')">
            <div class="concept-search-color" style="background: ${philosopherConcepts[node.concept].color}"></div>
            <div>
                <div class="concept-search-name">${node.label}</div>
                <div class="concept-search-philosopher">${node.concept}</div>
            </div>
        </div>
    `).join('');
    
    resultsContainer.classList.add('show');
}

function selectConnectionConcept(conceptId, target) {
    const concept = findConceptById(conceptId);
    
    if (target === 'source') {
        editMode.connectionSourceId = conceptId;
        document.getElementById('connectionSourceSearch').value = 
            `${concept.label} (${concept.concept})`;
        document.getElementById('connectionSourceResults').classList.remove('show');
    } else {
        editMode.connectionTargetId = conceptId;
        document.getElementById('connectionTargetSearch').value = 
            `${concept.label} (${concept.concept})`;
        document.getElementById('connectionTargetResults').classList.remove('show');
    }
}

function clearConnectionSearchField(target) {
    if (target === 'source') {
        document.getElementById('connectionSourceSearch').value = '';
        document.getElementById('connectionSourceResults').classList.remove('show');
        editMode.connectionSourceId = null;
    } else {
        document.getElementById('connectionTargetSearch').value = '';
        document.getElementById('connectionTargetResults').classList.remove('show');
        editMode.connectionTargetId = null;
    }
}
```

---

## ЧАСТЬ 3: Инициализировать поиск при открытии модального окна

### Найти функцию openEditConnectionModal (примерно строка 4281)

Добавить в КОНЕЦ функции (перед последними строками `modal.classList.add('show')` и `overlay.classList.add('show')`):

```javascript
function openEditConnectionModal(sourceId = null, targetId = null) {
    // ... весь существующий код ...
    
    // ============ ДОБАВИТЬ ПЕРЕД modal.classList.add('show') ============
    // Инициализируем поиск концепций
    initConnectionSearchFields();
    // ============ КОНЕЦ ДОБАВЛЕНИЯ ============
    
    modal.classList.add('show');
    overlay.classList.add('show');
}
```

---

## ЧАСТЬ 4: Управление overlay при выборе на графе

### Исправить функцию selectConceptOnGraph (строка 4474)

**Было:**
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
    
    // Временно скрываем модальное окно
    document.getElementById('editConnectionModal').style.opacity = '0.3';
}
```

**Должно быть:**
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
    
    // Скрываем модальное окно и overlay для доступа к графу
    modal.style.display = 'none';
    overlay.classList.remove('show');
}
```

---

## ЧАСТЬ 5: Восстановить overlay при отмене/завершении выбора

### Исправить функцию cancelGraphSelection (строка 4493)

**Было:**
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    document.getElementById('editConnectionModal').style.opacity = '1';
}
```

**Должно быть:**
```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // Восстанавливаем модальное окно и overlay
    modal.style.display = 'block';
    overlay.classList.add('show');
}
```

---

## ЧАСТЬ 6: Обновить handleConceptSelection (строка 4501)

Добавить восстановление overlay:

**Было:**
```javascript
function handleConceptSelection(conceptId) {
    if (!editMode.graphSelectionMode) return;
    
    const concept = findConceptById(conceptId);
    const target = editMode.graphSelectionTarget;
    
    if (target === 'source') {
        editMode.connectionSourceId = conceptId;
        document.getElementById('connectionSourceSearch').value = 
            `${concept.label} (${concept.concept})`;
    } else {
        editMode.connectionTargetId = conceptId;
        document.getElementById('connectionTargetSearch').value = 
            `${concept.label} (${concept.concept})`;
    }
    
    cancelGraphSelection();
}
```

**Должно быть (без изменений, только для проверки):**
```javascript
function handleConceptSelection(conceptId) {
    if (!editMode.graphSelectionMode) return;
    
    const concept = findConceptById(conceptId);
    const target = editMode.graphSelectionTarget;
    
    if (target === 'source') {
        editMode.connectionSourceId = conceptId;
        document.getElementById('connectionSourceSearch').value = 
            `${concept.label} (${concept.concept})`;
    } else {
        editMode.connectionTargetId = conceptId;
        document.getElementById('connectionTargetSearch').value = 
            `${concept.label} (${concept.concept})`;
    }
    
    cancelGraphSelection();  // ← Это уже восстановит overlay
}
```

---

## ДОПОЛНИТЕЛЬНО: Добавить кнопки очистки полей (опционально)

Если хотите добавить кнопки "×" для очистки полей, измените HTML (строки 4758-4779):

```html
<!-- Выбор начальной концепции -->
<div class="edit-form-group">
    <label>Начальная концепция *</label>
    <div class="concept-search-container">
        <input type="text" id="connectionSourceSearch" class="concept-search-input" placeholder="Поиск концепции...">
        <button type="button" class="concept-search-clear" onclick="clearConnectionSearchField('source')" style="display: none;">×</button>
        <div id="connectionSourceResults" class="concept-search-results"></div>
    </div>
    <button class="edit-btn edit-btn-secondary" onclick="selectConceptOnGraph('source')" style="margin-top: 10px; width: 100%;">
        Указать на графе
    </button>
</div>

<!-- Выбор конечной концепции -->
<div class="edit-form-group">
    <label>Конечная концепция *</label>
    <div class="concept-search-container">
        <input type="text" id="connectionTargetSearch" class="concept-search-input" placeholder="Поиск концепции...">
        <button type="button" class="concept-search-clear" onclick="clearConnectionSearchField('target')" style="display: none;">×</button>
        <div id="connectionTargetResults" class="concept-search-results"></div>
    </div>
    <button class="edit-btn edit-btn-secondary" onclick="selectConceptOnGraph('target')" style="margin-top: 10px; width: 100%;">
        Указать на графе
    </button>
</div>
```

И добавить стили для кнопки очистки (если еще нет):

```css
.concept-search-clear {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #95a5a6;
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    line-height: 1;
    display: none;
}

.concept-search-clear:hover {
    color: #e74c3c;
}

.concept-search-clear.show {
    display: block;
}
```

И обновить функцию selectConnectionConcept чтобы показывать кнопку очистки:

```javascript
function selectConnectionConcept(conceptId, target) {
    const concept = findConceptById(conceptId);
    
    if (target === 'source') {
        editMode.connectionSourceId = conceptId;
        const input = document.getElementById('connectionSourceSearch');
        input.value = `${concept.label} (${concept.concept})`;
        document.getElementById('connectionSourceResults').classList.remove('show');
        
        // Показать кнопку очистки
        const clearBtn = input.parentElement.querySelector('.concept-search-clear');
        if (clearBtn) clearBtn.style.display = 'block';
    } else {
        editMode.connectionTargetId = conceptId;
        const input = document.getElementById('connectionTargetSearch');
        input.value = `${concept.label} (${concept.concept})`;
        document.getElementById('connectionTargetResults').classList.remove('show');
        
        // Показать кнопку очистки
        const clearBtn = input.parentElement.querySelector('.concept-search-clear');
        if (clearBtn) clearBtn.style.display = 'block';
    }
}
```

---

## ИТОГО: Порядок действий

1. ✅ Убрать `readonly` из обоих input (строки 4761, 4773)
2. ✅ Добавить функции поиска после handleConceptSelection (после строки 4518)
3. ✅ Добавить вызов initConnectionSearchFields() в openEditConnectionModal
4. ✅ Исправить selectConceptOnGraph (строка 4474) - скрывать modal и overlay
5. ✅ Исправить cancelGraphSelection (строка 4493) - показывать modal и overlay
6. ⭐ Опционально: добавить кнопки очистки полей

---

## Проверка после изменений

После внесения изменений проверьте:

1. ✅ Открыть окно редактирования связи
2. ✅ Начать печатать в поле "Начальная концепция" → появляются результаты поиска
3. ✅ Клик на результат → поле заполняется, результаты скрываются
4. ✅ Клик "Указать на графе" → overlay исчезает, граф доступен
5. ✅ Выбор концепции на графе → overlay возвращается, окно показывается
6. ✅ Клик "Отмена" в индикаторе → overlay возвращается, окно показывается
7. ✅ То же самое для поля "Конечная концепция"
