# Быстрое исправление: Поиск концепций + управление overlay

## 🔧 Изменение 1: Убрать readonly

**Строки 4761 и 4773** - удалить `readonly`:

```html
<!-- Было -->
<input type="text" id="connectionSourceSearch" class="concept-search-input" placeholder="Поиск концепции..." readonly>
<input type="text" id="connectionTargetSearch" class="concept-search-input" placeholder="Поиск концепции..." readonly>

<!-- Стало -->
<input type="text" id="connectionSourceSearch" class="concept-search-input" placeholder="Поиск концепции...">
<input type="text" id="connectionTargetSearch" class="concept-search-input" placeholder="Поиск концепции...">
```

---

## 🔧 Изменение 2: Добавить функции поиска

**После строки 4518** (после функции handleConceptSelection) добавить:

```javascript
// Поиск концепций в полях связи
function initConnectionSearchFields() {
    const sourceInput = document.getElementById('connectionSourceSearch');
    const targetInput = document.getElementById('connectionTargetSearch');
    const sourceResults = document.getElementById('connectionSourceResults');
    const targetResults = document.getElementById('connectionTargetResults');
    
    if (sourceInput) {
        sourceInput.addEventListener('input', function(e) {
            handleConnectionConceptSearch(e.target.value.trim(), 'source', sourceResults);
        });
        sourceInput.addEventListener('focus', function(e) {
            if (e.target.value.trim()) {
                handleConnectionConceptSearch(e.target.value.trim(), 'source', sourceResults);
            }
        });
        sourceInput.addEventListener('blur', function() {
            setTimeout(() => sourceResults.classList.remove('show'), 200);
        });
    }
    
    if (targetInput) {
        targetInput.addEventListener('input', function(e) {
            handleConnectionConceptSearch(e.target.value.trim(), 'target', targetResults);
        });
        targetInput.addEventListener('focus', function(e) {
            if (e.target.value.trim()) {
                handleConnectionConceptSearch(e.target.value.trim(), 'target', targetResults);
            }
        });
        targetInput.addEventListener('blur', function() {
            setTimeout(() => targetResults.classList.remove('show'), 200);
        });
    }
}

function handleConnectionConceptSearch(query, target, resultsContainer) {
    if (!query) {
        resultsContainer.classList.remove('show');
        resultsContainer.innerHTML = '';
        return;
    }
    
    const results = searchNodes(query);
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="concept-search-item" style="color: #95a5a6; cursor: default;">Ничего не найдено</div>';
        resultsContainer.classList.add('show');
        return;
    }
    
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
        document.getElementById('connectionSourceSearch').value = `${concept.label} (${concept.concept})`;
        document.getElementById('connectionSourceResults').classList.remove('show');
    } else {
        editMode.connectionTargetId = conceptId;
        document.getElementById('connectionTargetSearch').value = `${concept.label} (${concept.concept})`;
        document.getElementById('connectionTargetResults').classList.remove('show');
    }
}
```

---

## 🔧 Изменение 3: Инициализировать поиск при открытии

**В функции openEditConnectionModal** (найти строку `modal.classList.add('show')`)

Добавить ПЕРЕД `modal.classList.add('show')`:

```javascript
// ... существующий код функции openEditConnectionModal ...

    // ⬇️ ДОБАВИТЬ ЭТУ СТРОКУ ⬇️
    initConnectionSearchFields();
    
    modal.classList.add('show');
    overlay.classList.add('show');
}
```

---

## 🔧 Изменение 4: Исправить selectConceptOnGraph

**Строка 4474** - заменить всю функцию:

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
    modal.style.display = 'none';
    overlay.classList.remove('show');
}
```

---

## 🔧 Изменение 5: Исправить cancelGraphSelection

**Строка 4493** - заменить всю функцию:

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

## ✅ Результат

После этих 5 изменений:

1. ✅ В полях "Начальная/Конечная концепция" можно печатать
2. ✅ При вводе появляется выпадающий список с результатами поиска
3. ✅ Клик по результату заполняет поле
4. ✅ При нажатии "Указать на графе" затемнение исчезает
5. ✅ После выбора на графе затемнение возвращается
6. ✅ Поиск работает для обоих полей

---

## 🎯 Проверка

Откройте окно редактирования связи и проверьте:

```
1. Начните печатать "кант" в поле → видны концепции Канта
2. Кликните на концепцию → поле заполнится
3. Нажмите "Указать на графе" → затемнение исчезло, граф доступен
4. Кликните на концепцию в графе → поле заполнилось, затемнение вернулось
5. Нажмите ESC или "Отмена" → все закрылось корректно
```
