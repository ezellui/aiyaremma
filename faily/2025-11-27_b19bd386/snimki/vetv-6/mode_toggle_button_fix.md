# Проблема: Кнопка "Редактировать" не отображается для философа и связи

## Диагностика проблемы

Кнопка переключения режима (режим просмотра ↔ режим редактирования) должна добавляться в функции `openUniversalModal()`, но скорее всего там есть условие, которое ограничивает её добавление только для концепций.

---

## Где должна быть кнопка

Кнопка переключения режима обычно добавляется в функции `openUniversalModal()` после генерации основного контента, но **перед** закрывающей кнопкой.

### Типичное место добавления кнопки:

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    // ... код генерации контента ...
    
    content.innerHTML = html;
    
    // ✅ ЗДЕСЬ должна добавляться кнопка переключения режима
    
    modal.classList.add('show');
    overlay.classList.add('show');
    
    // ...
}
```

---

## Решение: Универсальная кнопка для всех типов сущностей

### Вариант 1: Добавление кнопки в HTML каждого генератора (не рекомендуется)

Можно добавить кнопку в конец HTML каждого генератора контента:

```javascript
function generatePhilosopherViewContent(philosopherName) {
    let html = `<h2>...`;
    // ... весь контент ...
    
    // Добавляем кнопку редактирования
    html += `
        <div style="margin-top: 20px; text-align: right;">
            <button class="modal-btn-primary" onclick="toggleModalMode()">
                ✏️ Редактировать
            </button>
        </div>
    `;
    
    return html;
}
```

**Проблема:** Нужно добавлять в каждый генератор отдельно - дублирование кода.

---

### Вариант 2: Добавление кнопки программно в openUniversalModal (РЕКОМЕНДУЕТСЯ)

Добавляем кнопку универсально для всех типов сущностей после установки HTML:

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    ModalContext.currentEntity = entityType;
    ModalContext.currentMode = mode;
    ModalContext.currentData = data;
    ModalContext.editState = {};
    
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    
    freezeSimulation();
    
    let html = '';
    
    // Генерируем контент в зависимости от типа и режима
    if (mode === 'view') {
        if (entityType === 'philosopher') {
            html = generatePhilosopherViewContent(data);
        } else if (entityType === 'concept') {
            html = generateConceptViewContent(data);
        } else if (entityType === 'connection') {
            html = generateConnectionViewContent(data);
        }
    } else if (mode === 'edit') {
        if (entityType === 'philosopher') {
            html = generatePhilosopherEditContent(data);
        } else if (entityType === 'concept') {
            html = generateConceptEditContent(data);
        } else if (entityType === 'connection') {
            html = generateConnectionEditContent(data);
        }
    }
    
    content.innerHTML = html;
    
    // ✅ ДОБАВЛЕНИЕ: Кнопка переключения режима для режима просмотра
    if (mode === 'view') {
        addModeToggleButton(entityType);
    }
    
    modal.classList.add('show');
    if (mode === 'edit') {
        modal.classList.add('edit-mode');
    }
    overlay.classList.add('show');
    
    // Инициализация дополнительных обработчиков
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
}
```

---

### Функция addModeToggleButton

```javascript
/**
 * Добавление кнопки переключения режима в модальное окно
 * @param {string} entityType - Тип сущности ('philosopher', 'concept', 'connection')
 */
function addModeToggleButton(entityType) {
    const content = document.getElementById('universalModalContent');
    if (!content) return;
    
    // Создаем кнопку
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'mode-toggle-container';
    buttonContainer.style.cssText = 'margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1); text-align: right;';
    
    const toggleButton = document.createElement('button');
    toggleButton.className = 'modal-btn-primary mode-toggle-btn';
    toggleButton.onclick = toggleModalMode;
    
    // Определяем текст кнопки в зависимости от типа сущности
    let buttonText = '✏️ Редактировать';
    if (entityType === 'philosopher') {
        buttonText = '✏️ Редактировать философа';
    } else if (entityType === 'concept') {
        buttonText = '✏️ Редактировать концепцию';
    } else if (entityType === 'connection') {
        buttonText = '✏️ Редактировать связь';
    }
    
    toggleButton.textContent = buttonText;
    
    buttonContainer.appendChild(toggleButton);
    content.appendChild(buttonContainer);
}
```

**Где объявить:** После функции `openUniversalModal()`

---

### Обновленная функция toggleModalMode

Нужно убедиться, что она удаляет старую кнопку и добавляет новую при переключении:

```javascript
/**
 * Переключение между режимами просмотра и редактирования
 */
function toggleModalMode() {
    const currentMode = ModalContext.currentMode;
    const newMode = currentMode === 'view' ? 'edit' : 'view';
    
    // Проверяем несохраненные изменения при переходе из edit в view
    if (currentMode === 'edit' && hasUnsavedChanges()) {
        const confirmed = confirm('Есть несохраненные изменения. Вы уверены, что хотите вернуться к просмотру?');
        if (!confirmed) return;
    }
    
    // Переоткрываем окно в новом режиме
    openUniversalModal(ModalContext.currentEntity, ModalContext.currentData, newMode);
}
```

---

## Альтернативное решение: Кнопка в заголовке окна

Можно добавить кнопку прямо в заголовок (в HTML структуру модального окна):

### Обновленная HTML структура универсального окна

```html
<div id="universalModal" class="detail-modal">
    <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <button class="modal-close" onclick="closeUniversalModal()">×</button>
        <button class="mode-toggle-btn-header" id="modeToggleBtn" onclick="toggleModalMode()" style="display: none;">
            ✏️ Редактировать
        </button>
    </div>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

### CSS для кнопки в заголовке

```css
.mode-toggle-btn-header {
    background: #6c5ce7;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.mode-toggle-btn-header:hover {
    background: #5f50d8;
    transform: translateY(-1px);
}
```

### Обновление openUniversalModal для показа/скрытия кнопки

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    // ... существующий код ...
    
    content.innerHTML = html;
    
    // Показываем/скрываем кнопку переключения режима
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    if (modeToggleBtn) {
        if (mode === 'view') {
            modeToggleBtn.style.display = 'block';
            // Обновляем текст кнопки
            if (entityType === 'philosopher') {
                modeToggleBtn.innerHTML = '✏️ Редактировать философа';
            } else if (entityType === 'concept') {
                modeToggleBtn.innerHTML = '✏️ Редактировать концепцию';
            } else if (entityType === 'connection') {
                modeToggleBtn.innerHTML = '✏️ Редактировать связь';
            }
        } else {
            modeToggleBtn.style.display = 'none';
        }
    }
    
    modal.classList.add('show');
    // ...
}
```

---

## Сравнение решений

| Решение | Плюсы | Минусы |
|---------|-------|--------|
| **Вариант 1: В каждом генераторе** | Гибкость в размещении кнопки | Дублирование кода, трудно поддерживать |
| **Вариант 2: Программное добавление** | Централизованная логика, нет дублирования | Кнопка всегда внизу контента |
| **Альтернатива: Кнопка в заголовке** | Всегда на видном месте, не нужно скроллить | Требует изменения HTML структуры |

---

## Рекомендуемое решение

**Вариант 2 + Альтернатива (комбинация)**:

1. **Добавить кнопку в заголовок HTML** (всегда на виду)
2. **Управлять видимостью в openUniversalModal** (простая логика show/hide)

### Пошаговая реализация:

#### Шаг 1: Обновить HTML структуру универсального окна

Найти в HTML:
```html
<div id="universalModal" class="detail-modal">
    <button class="close-btn" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

Заменить на:
```html
<div id="universalModal" class="detail-modal">
    <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <button class="mode-toggle-btn" id="modeToggleBtn" onclick="toggleModalMode()" style="display: none;">
            ✏️ Редактировать
        </button>
        <button class="close-btn" onclick="closeUniversalModal()">×</button>
    </div>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

#### Шаг 2: Добавить CSS для кнопки

```css
.mode-toggle-btn {
    background: #6c5ce7;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(108, 92, 231, 0.3);
}

.mode-toggle-btn:hover {
    background: #5f50d8;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(108, 92, 231, 0.4);
}

.mode-toggle-btn:active {
    transform: translateY(0);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}
```

#### Шаг 3: Обновить openUniversalModal

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    ModalContext.currentEntity = entityType;
    ModalContext.currentMode = mode;
    ModalContext.currentData = data;
    ModalContext.editState = {};
    
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    
    freezeSimulation();
    
    let html = '';
    
    // Генерируем контент
    if (mode === 'view') {
        if (entityType === 'philosopher') {
            html = generatePhilosopherViewContent(data);
        } else if (entityType === 'concept') {
            html = generateConceptViewContent(data);
        } else if (entityType === 'connection') {
            html = generateConnectionViewContent(data);
        }
    } else if (mode === 'edit') {
        if (entityType === 'philosopher') {
            html = generatePhilosopherEditContent(data);
        } else if (entityType === 'concept') {
            html = generateConceptEditContent(data);
        } else if (entityType === 'connection') {
            html = generateConnectionEditContent(data);
        }
    }
    
    content.innerHTML = html;
    
    // ✅ ИСПРАВЛЕНИЕ: Показываем кнопку в режиме просмотра, скрываем в режиме редактирования
    if (modeToggleBtn) {
        if (mode === 'view') {
            modeToggleBtn.style.display = 'block';
            
            // Обновляем текст кнопки в зависимости от типа сущности
            if (entityType === 'philosopher') {
                modeToggleBtn.innerHTML = '✏️ Редактировать философа';
            } else if (entityType === 'concept') {
                modeToggleBtn.innerHTML = '✏️ Редактировать концепцию';
            } else if (entityType === 'connection') {
                modeToggleBtn.innerHTML = '✏️ Редактировать связь';
            }
        } else {
            modeToggleBtn.style.display = 'none';
        }
    }
    
    modal.classList.add('show');
    if (mode === 'edit') {
        modal.classList.add('edit-mode');
    } else {
        modal.classList.remove('edit-mode');
    }
    overlay.classList.add('show');
    
    // Инициализация дополнительных обработчиков
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
}
```

---

## Проверочный чек-лист

После внесения изменений проверьте:

- [ ] **Окно философа (view)**: Кнопка "✏️ Редактировать философа" отображается
- [ ] **Окно концепции (view)**: Кнопка "✏️ Редактировать концепцию" отображается
- [ ] **Окно связи (view)**: Кнопка "✏️ Редактировать связь" отображается
- [ ] **Окно философа (edit)**: Кнопка **НЕ** отображается
- [ ] **Окно концепции (edit)**: Кнопка **НЕ** отображается
- [ ] **Окно связи (edit)**: Кнопка **НЕ** отображается
- [ ] **Клик на кнопку**: Переключает в режим редактирования
- [ ] **Текст кнопки**: Соответствует типу сущности

---

## Итого

**Причина проблемы:** Кнопка переключения режима, скорее всего, не была добавлена в функцию `openUniversalModal()` для всех типов сущностей, или была добавлена только в генератор контента концепции.

**Решение:** Добавить кнопку в HTML структуру модального окна и управлять её видимостью в `openUniversalModal()`.

**Результат:** Кнопка "Редактировать" будет отображаться для всех типов сущностей в режиме просмотра.
