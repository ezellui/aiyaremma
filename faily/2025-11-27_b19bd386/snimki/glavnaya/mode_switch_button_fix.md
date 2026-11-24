# Проблема с кнопкой переключения режима в модальном окне

## Анализ проблемы

### Текущее условие:
```javascript
if (data && data.id) {
    html = `<button class="mode-switch-btn" onclick="toggleModalMode()">...</button>` + html;
}
```

### Почему не работает для разных сущностей:

| Тип сущности | Что передается в `data` | Есть ли `data.id`? | Кнопка показывается? |
|--------------|-------------------------|-------------------|---------------------|
| **Концепция** | Объект: `{id: "concept_123", label: "...", ...}` | ✅ Да | ✅ Да |
| **Философ** | Строка: `"Кант"` | ❌ Нет (строка не имеет поля id) | ❌ Нет |
| **Связь** | Объект: `{source: "...", target: "...", type: "..."}` | ❌ Нет (связи не имеют id) | ❌ Нет |

### Вывод:
Условие `data.id` работает только для концепций, потому что только они имеют поле `id`.

---

## Решение

Нужно адаптировать условие для каждого типа сущности:

### Вариант 1: Проверка по типу сущности (рекомендуется)

```javascript
/**
 * Главная функция открытия универсального модального окна
 */
function openUniversalModal(entityType, data, mode = 'view') {
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    
    freezeSimulation();
    
    // Сохраняем контекст
    ModalContext.currentEntity = entityType;
    ModalContext.currentMode = mode;
    ModalContext.currentData = data;
    
    // Применяем класс режима
    if (mode === 'edit') {
        modal.classList.add('edit-mode');
    } else {
        modal.classList.remove('edit-mode');
    }
    
    // Генерируем контент в зависимости от типа и режима
    let html = '';
    
    switch(entityType) {
        case 'philosopher':
            html = mode === 'view' 
                ? generatePhilosopherViewContent(data)
                : generatePhilosopherEditContent(data);
            break;
        case 'concept':
            html = mode === 'view'
                ? generateConceptViewContent(data)
                : generateConceptEditContent(data);
            break;
        case 'connection':
            html = mode === 'view'
                ? generateConnectionViewContent(data)
                : generateConnectionEditContent(data);
            break;
    }
    
    // ✅ ИСПРАВЛЕНИЕ: Определяем, является ли это редактированием существующей сущности
    let isExistingEntity = false;
    
    switch(entityType) {
        case 'philosopher':
            // Философ существует, если передано имя (строка)
            isExistingEntity = data && typeof data === 'string' && data.length > 0;
            break;
        case 'concept':
            // Концепция существует, если есть id
            isExistingEntity = data && data.id;
            break;
        case 'connection':
            // Связь существует, если есть source и target
            isExistingEntity = data && (data.source || data.from) && (data.target || data.to);
            break;
    }
    
    // Добавляем кнопку переключения режима (если не создание новой сущности)
    if (isExistingEntity) {
        html = `
            <button class="mode-switch-btn" onclick="toggleModalMode()">
                ${mode === 'view' ? '✏️ Редактировать' : '👁️ Просмотр'}
            </button>
        ` + html;
    }
    
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
    
    // ✅ ДОБАВИТЬ: Инициализация для связей (если нужна форма поиска)
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
}
```

---

### Вариант 2: Универсальная проверка (проще, но менее строгая)

```javascript
// Добавляем кнопку переключения режима (если не создание новой сущности)
const isExistingEntity = data && (
    // Для философа - непустая строка
    (entityType === 'philosopher' && typeof data === 'string' && data.length > 0) ||
    // Для концепции - есть id
    (entityType === 'concept' && data.id) ||
    // Для связи - есть source и target
    (entityType === 'connection' && (data.source || data.from) && (data.target || data.to))
);

if (isExistingEntity) {
    html = `
        <button class="mode-switch-btn" onclick="toggleModalMode()">
            ${mode === 'view' ? '✏️ Редактировать' : '👁️ Просмотр'}
        </button>
    ` + html;
}
```

---

### Вариант 3: Проверка через отрицание (самый простой)

```javascript
// Добавляем кнопку переключения режима (если data не null/undefined)
// Исключаем только явное создание новой сущности (data === null)
if (data !== null && data !== undefined) {
    html = `
        <button class="mode-switch-btn" onclick="toggleModalMode()">
            ${mode === 'view' ? '✏️ Редактировать' : '👁️ Просмотр'}
        </button>
    ` + html;
}
```

⚠️ **Внимание:** Вариант 3 может показать кнопку даже для создания новых сущностей, если они вызываются с пустым объектом `{}` вместо `null`.

---

## Рекомендуемое решение

Используйте **Вариант 1** (проверка по типу сущности) - он наиболее надежный и явный.

### Полная исправленная функция:

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    
    freezeSimulation();
    
    ModalContext.currentEntity = entityType;
    ModalContext.currentMode = mode;
    ModalContext.currentData = data;
    
    if (mode === 'edit') {
        modal.classList.add('edit-mode');
    } else {
        modal.classList.remove('edit-mode');
    }
    
    // Генерируем контент
    let html = '';
    
    switch(entityType) {
        case 'philosopher':
            html = mode === 'view' 
                ? generatePhilosopherViewContent(data)
                : generatePhilosopherEditContent(data);
            break;
        case 'concept':
            html = mode === 'view'
                ? generateConceptViewContent(data)
                : generateConceptEditContent(data);
            break;
        case 'connection':
            html = mode === 'view'
                ? generateConnectionViewContent(data)
                : generateConnectionEditContent(data);
            break;
    }
    
    // Определяем, является ли это существующей сущностью
    let isExistingEntity = false;
    
    switch(entityType) {
        case 'philosopher':
            isExistingEntity = data && typeof data === 'string' && data.length > 0;
            break;
        case 'concept':
            isExistingEntity = data && data.id;
            break;
        case 'connection':
            isExistingEntity = data && (data.source || data.from) && (data.target || data.to);
            break;
    }
    
    // Добавляем кнопку переключения режима
    if (isExistingEntity) {
        html = `
            <button class="mode-switch-btn" onclick="toggleModalMode()">
                ${mode === 'view' ? '✏️ Редактировать' : '👁️ Просмотр'}
            </button>
        ` + html;
    }
    
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
    
    // Инициализация для связей
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
}
```

---

## Проверочная таблица после исправления

| Сценарий | data | isExistingEntity | Кнопка показывается? |
|----------|------|------------------|---------------------|
| Просмотр Канта | `"Кант"` | ✅ true | ✅ Да |
| Создание философа | `null` | ❌ false | ❌ Нет |
| Просмотр концепции | `{id: "123", label: "..."}` | ✅ true | ✅ Да |
| Создание концепции | `null` | ❌ false | ❌ Нет |
| Просмотр связи | `{source: "123", target: "456", ...}` | ✅ true | ✅ Да |
| Создание связи | `null` или `{source: "123", target: "456"}` | ✅ true | ✅ Да |

---

## Дополнительное замечание: Создание связи

При создании новой связи через shift+клик на двух узлах, вы передаете:
```javascript
const connectionData = {
    source: firstConceptId,
    target: d.id
};
openUniversalModal('connection', connectionData, 'edit');
```

В этом случае `data.source` и `data.target` существуют, поэтому кнопка переключения **будет показана**. Это правильно, так как пользователь может захотеть переключиться в режим просмотра, чтобы увидеть, есть ли уже связь между этими концепциями.

Если вы хотите **скрывать** кнопку при создании новой связи, измените условие:

```javascript
case 'connection':
    // Связь существует, если это объект с type (существующая связь)
    // или если мы в режиме view (просмотр всегда означает существующую связь)
    isExistingEntity = data && (
        data.type || // Есть тип связи = существующая
        mode === 'view' // Режим просмотра = существующая
    );
    break;
```

---

## Итого

**Причина проблемы:** Условие `data.id` работает только для концепций

**Решение:** Использовать специфичные проверки для каждого типа сущности

**Результат:** Кнопка "✏️ Редактировать" теперь отображается во всех окнах просмотра!
