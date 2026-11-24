# Проблема с кнопкой "Редактировать" в унифицированной системе

## Диагностика проблемы

### Симптом
Кнопка "Редактировать" отображается **только в окне просмотра концепции**, но отсутствует в окнах просмотра философа и связи.

### Причина
Кнопка добавляется **индивидуально в каждом генераторе контента**, а не централизованно в `openUniversalModal()`. 

Вероятно:
- ✅ В `generateConceptViewContent()` кнопка добавлена
- ❌ В `generatePhilosopherViewContent()` кнопка НЕ добавлена
- ❌ В `generateConnectionViewContent()` кнопка НЕ добавлена

---

## Решение 1: Централизованное добавление кнопки (РЕКОМЕНДУЕТСЯ)

Добавить кнопку "Редактировать" автоматически в функции `openUniversalModal()` для **всех** режимов просмотра.

### Обновленная функция openUniversalModal()

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    
    // Сохраняем контекст
    ModalContext.currentEntity = entityType;
    ModalContext.currentMode = mode;
    ModalContext.currentData = data;
    
    // Генерируем контент в зависимости от типа и режима
    let html = '';
    
    if (mode === 'view') {
        switch(entityType) {
            case 'philosopher':
                html = generatePhilosopherViewContent(data);
                break;
            case 'concept':
                html = generateConceptViewContent(data);
                break;
            case 'connection':
                html = generateConnectionViewContent(data);
                break;
        }
    } else if (mode === 'edit') {
        switch(entityType) {
            case 'philosopher':
                html = generatePhilosopherEditContent(data);
                break;
            case 'concept':
                html = generateConceptEditContent(data);
                break;
            case 'connection':
                html = generateConnectionEditContent(data);
                break;
        }
    }
    
    content.innerHTML = html;
    
    // ✅ НОВОЕ: Добавляем кнопку переключения режима для режима просмотра
    if (mode === 'view') {
        const editButton = document.createElement('button');
        editButton.className = 'mode-switch-btn';
        editButton.innerHTML = '✏️ Редактировать';
        editButton.onclick = () => toggleModalMode();
        
        // Вставляем кнопку в начало контента
        content.insertBefore(editButton, content.firstChild);
    }
    
    // Добавляем класс режима редактирования
    if (mode === 'edit') {
        modal.classList.add('edit-mode');
    } else {
        modal.classList.remove('edit-mode');
    }
    
    modal.classList.add('show');
    overlay.classList.add('show');
    
    // Инициализация дополнительных обработчиков
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
    
    freezeSimulation();
}
```

### CSS для кнопки переключения режима

Если у вас ещё нет стилей для `.mode-switch-btn`, добавьте:

```css
.mode-switch-btn {
    position: absolute;
    top: 20px;
    right: 60px; /* Справа от кнопки закрытия */
    padding: 8px 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    z-index: 1001;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.mode-switch-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.mode-switch-btn:active {
    transform: translateY(0);
}
```

---

## Решение 2: Добавление кнопки в каждый генератор (альтернатива)

Если по какой-то причине вы хотите добавлять кнопку индивидуально, вот код для каждого генератора:

### В generatePhilosopherViewContent()

```javascript
function generatePhilosopherViewContent(philosopherName) {
    const philosopherData = philosophers.find(p => p.nameRu === philosopherName);
    if (!philosopherData) return '<p>Философ не найден</p>';
    
    // ✅ ДОБАВИТЬ В НАЧАЛО
    let html = `
        <button class="mode-switch-btn" onclick="toggleModalMode()">
            ✏️ Редактировать
        </button>
        <h2>${philosopherData.nameRu}</h2>
    `;
    
    // ... остальной код ...
    
    return html;
}
```

### В generateConnectionViewContent()

```javascript
function generateConnectionViewContent(connectionData) {
    // ✅ ДОБАВИТЬ В НАЧАЛО
    let html = `
        <button class="mode-switch-btn" onclick="toggleModalMode()">
            ✏️ Редактировать
        </button>
        <h2>Просмотр связи</h2>
    `;
    
    // ... остальной код ...
    
    return html;
}
```

### Проверка в generateConceptViewContent()

Убедитесь, что кнопка добавлена в начале:

```javascript
function generateConceptViewContent(conceptData) {
    let html = `
        <button class="mode-switch-btn" onclick="toggleModalMode()">
            ✏️ Редактировать
        </button>
        <h2>${conceptData.label}</h2>
    `;
    
    // ... остальной код ...
    
    return html;
}
```

---

## Сравнение решений

| Аспект | Решение 1 (Централизованное) | Решение 2 (Индивидуальное) |
|--------|------------------------------|----------------------------|
| **Место добавления** | `openUniversalModal()` | Каждый генератор |
| **Преимущества** | ✅ Единообразие<br>✅ Меньше дублирования<br>✅ Легче поддерживать | ✅ Больше контроля<br>✅ Можно настроить позицию |
| **Недостатки** | ⚠️ Кнопка через DOM API | ⚠️ Дублирование кода<br>⚠️ Легко забыть |
| **Рекомендация** | ⭐ РЕКОМЕНДУЕТСЯ | Только если нужна гибкость |

---

## Дополнительно: Кнопка переключения в режиме редактирования

В режиме редактирования можно добавить кнопку "👁️ Просмотр" по аналогии:

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    // ... существующий код ...
    
    content.innerHTML = html;
    
    // Добавляем кнопку переключения режима
    if (mode === 'view') {
        const editButton = document.createElement('button');
        editButton.className = 'mode-switch-btn';
        editButton.innerHTML = '✏️ Редактировать';
        editButton.onclick = () => toggleModalMode();
        content.insertBefore(editButton, content.firstChild);
    } else if (mode === 'edit') {
        // ✅ ОПЦИОНАЛЬНО: Кнопка "Просмотр" в режиме редактирования
        const viewButton = document.createElement('button');
        viewButton.className = 'mode-switch-btn';
        viewButton.innerHTML = '👁️ Просмотр';
        viewButton.onclick = () => toggleModalMode();
        content.insertBefore(viewButton, content.firstChild);
    }
    
    // ... остальной код ...
}
```

---

## Функция toggleModalMode()

Убедитесь, что функция правильно переключает режимы:

```javascript
function toggleModalMode() {
    // Проверка несохраненных изменений при переходе из edit в view
    if (ModalContext.currentMode === 'edit' && hasUnsavedChanges()) {
        const confirmed = confirm('Есть несохраненные изменения. Покинуть режим редактирования?');
        if (!confirmed) return;
    }
    
    // Переключаем режим
    const newMode = ModalContext.currentMode === 'view' ? 'edit' : 'view';
    
    // Перезагружаем модальное окно с новым режимом
    openUniversalModal(
        ModalContext.currentEntity,
        ModalContext.currentData,
        newMode
    );
}
```

---

## Проверочный чек-лист

После внедрения решения проверьте:

### ✅ Кнопка "Редактировать" отображается:
- [ ] В окне просмотра философа
- [ ] В окне просмотра концепции
- [ ] В окне просмотра связи

### ✅ Кнопка работает:
- [ ] Клик на "Редактировать" переключает в режим edit
- [ ] Клик на "Просмотр" (если добавлена) переключает в режим view
- [ ] При несохраненных изменениях показывается предупреждение

### ✅ Визуальное оформление:
- [ ] Кнопка видна и не перекрывается другими элементами
- [ ] Кнопка находится в удобном месте (правый верхний угол)
- [ ] Кнопка не конфликтует с кнопкой закрытия

---

## Рекомендация

**Используйте Решение 1 (Централизованное добавление)** - это более надежный и поддерживаемый подход.

Просто добавьте код в `openUniversalModal()`:

```javascript
// После content.innerHTML = html;

if (mode === 'view') {
    const editButton = document.createElement('button');
    editButton.className = 'mode-switch-btn';
    editButton.innerHTML = '✏️ Редактировать';
    editButton.onclick = () => toggleModalMode();
    content.insertBefore(editButton, content.firstChild);
}
```

И все три типа окон автоматически получат кнопку "Редактировать"!

---

## Итого

**Проблема:** Кнопка добавлялась только в одном генераторе

**Решение:** Добавить кнопку централизованно в `openUniversalModal()` через DOM API

**Результат:** Все окна просмотра (философ, концепция, связь) имеют кнопку "Редактировать"
