# Таблица миграции CSS классов

## Модальные окна

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#detailModal` | `.detail-modal` | Базовый класс для всех модальных окон |
| `#philosopherDetailModal` | `#philosopherDetailModal.detail-modal` | Специфичные размеры через ID + класс |
| `#editPhilosopherModal` | `.detail-modal.edit-mode` | Режим редактирования через класс |
| `#editConceptModal` | `.detail-modal.edit-mode` | Режим редактирования через класс |
| `#editConnectionModal` | `.detail-modal.edit-mode` | Режим редактирования через класс |
| `#detailModal.show` | `.detail-modal.show` | Видимость окна |
| `#modalOverlay` | `#modalOverlay` | Без изменений |
| `#modalContent` | `.modal-content` | Класс вместо ID |

## Кнопки закрытия

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#detailModal .close-btn` | `.detail-modal .modal-close` | Унифицированное имя |
| `.edit-modal-close` | `.detail-modal .modal-close` | Единый стиль для всех |

## Заголовки

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#detailModal h2` | `.detail-modal h2` | Универсальный стиль |
| `.edit-modal-header h3` | `.detail-modal h3` | Без специальной обёртки |

## Элементы контента

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#detailModal .philosopher-tag` | `.detail-modal .philosopher-tag` | Универсально для всех |
| `#detailModal .description` | `.detail-modal .description` | Универсально для всех |
| `#detailModal .rubric-section` | `.detail-modal .rubric-section` | Только для концепций |
| `#detailModal .rubric-title` | `.detail-modal .rubric-title` | Только для концепций |
| `#detailModal .rubric-description` | `.detail-modal .rubric-description` | Только для концепций |

## Концепции и связи

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#detailModal .related-concepts` | `.detail-modal .related-concepts` | Универсально |
| `#detailModal .related-title` | `.detail-modal .related-title` | Универсально |
| `#detailModal .concept-item` | `.detail-modal .concept-item` | Универсально |
| `#detailModal .concept-color` | `.detail-modal .concept-color` | Универсально |
| `#detailModal .concept-name` | `.detail-modal .concept-name` | Универсально |
| `#detailModal .concept-philosopher` | `.detail-modal .concept-philosopher` | Универсально |
| `.connections-section` | `.detail-modal .connections-section` | Добавлен контекст |
| `.connections-title` | `.detail-modal .connections-title` | Добавлен контекст |
| `.connection-item` | `.detail-modal .connection-item` | Добавлен контекст |
| `.connection-arrow` | `.detail-modal .connection-arrow` | Добавлен контекст |
| `.connection-toggle` | `.detail-modal .connection-toggle` | Добавлен контекст |
| `.connection-description` | `.detail-modal .connection-description` | Добавлен контекст |

## Взаимодействия философов (новое)

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| *нет* | `.detail-modal .philosopher-interactions` | Новая секция |
| *нет* | `.detail-modal .interaction-item` | Новый элемент |
| *нет* | `.detail-modal .interaction-philosopher` | Новый элемент |
| *нет* | `.detail-modal .interaction-description` | Новый элемент |

## Формы редактирования

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.edit-modal` | `.detail-modal.edit-mode` | Режим через класс |
| `.edit-modal-header` | *удалено* | Заменено на обычные h2/h3 |
| `.edit-modal-body` | `.detail-modal` (сам контейнер) | Упрощена структура |
| `.edit-form-group` | `.modal-form-group` | Префикс `modal-` |
| `.edit-form-group.inline` | `.modal-form-inline` | Отдельный класс |
| `.edit-form-checkbox` | `.modal-form-checkbox` | Префикс `modal-` |
| `.edit-modal-actions` | `.modal-actions` | Префикс `modal-` |

## Кнопки действий

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.edit-btn` | `.modal-btn` | Префикс `modal-` |
| `.edit-btn-primary` | `.modal-btn-primary` | Префикс `modal-` |
| `.edit-btn-secondary` | `.modal-btn-secondary` | Префикс `modal-` |
| `.edit-btn-danger` | `.modal-btn-danger` | Префикс `modal-` |
| `.goto-node-btn` | `.detail-modal .goto-node-btn` | Добавлен контекст |
| `.show-all-concepts-btn` | `.detail-modal .show-all-concepts-btn` | Добавлен контекст |
| `.toggle-all-descriptions-btn` | `.detail-modal .toggle-all-descriptions-btn` | Добавлен контекст |

## Списки редактирования

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.edit-list-section` | `.modal-edit-list` | Переименовано |
| `.edit-list-item` | `.modal-edit-list-item` | Префикс `modal-` |
| `.edit-list-item-content` | `.modal-edit-list-item-content` | Префикс `modal-` |
| `.edit-list-item-name` | `.modal-edit-list-item-name` | Префикс `modal-` |
| `.edit-list-item-desc` | `.modal-edit-list-item-desc` | Префикс `modal-` |
| `.edit-list-item-actions` | `.modal-edit-list-item-actions` | Префикс `modal-` |
| `.edit-list-btn` | `.modal-edit-list-btn` | Префикс `modal-` |
| `.edit-list-btn-edit` | `.modal-edit-list-btn-edit` | Префикс `modal-` |
| `.edit-list-btn-delete` | `.modal-edit-list-btn-delete` | Префикс `modal-` |
| `.edit-list-btn-add` | `.modal-edit-list-btn-add` | Префикс `modal-` |

## Поиск концепций

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.concept-search-container` | `.modal-concept-search` | Переименовано |
| `.concept-search-input` | `.modal-concept-search input` | Упрощена структура |
| `.concept-search-results` | `.modal-concept-search-results` | Префикс `modal-` |
| `.concept-search-item` | `.modal-concept-search-item` | Префикс `modal-` |
| `.concept-search-color` | `.modal-concept-search-color` | Префикс `modal-` |
| `.concept-search-name` | `.modal-concept-search-name` | Префикс `modal-` |
| `.concept-search-philosopher` | `.modal-concept-search-philosopher` | Префикс `modal-` |

## Новые классы

| Новый селектор | Назначение |
|---------------|-----------|
| `.mode-switch-btn` | Кнопка переключения режима просмотр/редактирование |
| `.detail-modal.edit-mode::before` | Индикатор режима редактирования |
| `.collapsible-header` | Заголовок сворачиваемой секции |
| `.collapsible-content` | Контент сворачиваемой секции |
| `.collapsible-header.collapsed` | Свёрнутое состояние |
| `.collapsible-content.collapsed` | Скрытый контент |

## Scrollbar стили

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#detailModal::-webkit-scrollbar` | `.detail-modal::-webkit-scrollbar` | Универсально |
| `#detailModal::-webkit-scrollbar-track` | `.detail-modal::-webkit-scrollbar-track` | Универсально |
| `#detailModal::-webkit-scrollbar-thumb` | `.detail-modal::-webkit-scrollbar-thumb` | Универсально |

## Поиск в модальном окне

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `#modalSearch` | `#modalSearch` | Без изменений (ID сохранён) |
| `#modalSearch .legend-search-*` | `#modalSearch .legend-search-*` | Без изменений |
| `#modalSearch .search-results` | `#modalSearch .search-results` | Без изменений |

## Режим выбора на графе

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.graph-selection-mode` | `.graph-selection-mode` | Без изменений |
| `.graph-selection-cancel` | `.graph-selection-cancel` | Без изменений |

## Предупреждения

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.warning-message` | `.detail-modal .warning-message` | Добавлен контекст |
| `.warning-list` | `.detail-modal .warning-list` | Добавлен контекст |

## Индикаторы

| Старый селектор | Новый селектор | Комментарий |
|----------------|---------------|------------|
| `.edit-mode-indicator` | `.edit-mode-indicator` | Без изменений |

---

## Руководство по замене в коде

### Поиск и замена в HTML/JavaScript

#### 1. ID модальных окон

```javascript
// Найти:
document.getElementById('detailModal')
document.getElementById('editPhilosopherModal')
document.getElementById('editConceptModal')

// Заменить на:
document.getElementById('universalModal')
```

#### 2. Классы в HTML строках

```javascript
// Найти:
'<div class="edit-form-group">'
'<button class="edit-btn edit-btn-primary">'
'<div class="edit-list-section">'

// Заменить на:
'<div class="modal-form-group">'
'<button class="modal-btn modal-btn-primary">'
'<div class="modal-edit-list">'
```

#### 3. Селекторы в querySelector

```javascript
// Найти:
document.querySelector('#detailModal .close-btn')
document.querySelector('.edit-modal-close')
document.querySelectorAll('.edit-list-item')

// Заменить на:
document.querySelector('.detail-modal .modal-close')
document.querySelector('.detail-modal .modal-close')
document.querySelectorAll('.modal-edit-list-item')
```

#### 4. Манипуляция классами

```javascript
// Найти:
modal.classList.add('show')
editModal.classList.add('show')

// Заменить на:
universalModal.classList.add('show')
universalModal.classList.add('edit-mode') // если редактирование
```

### Регулярные выражения для замены

#### В HTML строках

```regex
Найти: class="edit-form-group"
Заменить: class="modal-form-group"

Найти: class="edit-btn (edit-btn-\w+)"
Заменить: class="modal-btn modal-btn-$1"

Найти: class="edit-list-(\w+)"
Заменить: class="modal-edit-list-$1"

Найти: class="concept-search-(\w+)"
Заменить: class="modal-concept-search-$1"
```

#### В CSS селекторах

```regex
Найти: #detailModal\s
Заменить: .detail-modal 

Найти: \.edit-modal\b
Заменить: .detail-modal.edit-mode

Найти: \.edit-form-
Заменить: .modal-form-

Найти: \.edit-btn
Заменить: .modal-btn

Найти: \.edit-list-
Заменить: .modal-edit-list-
```

---

## Пример миграции функции

### Было:

```javascript
function openEditPhilosopherModal(philosopherName) {
    const modal = document.getElementById('editPhilosopherModal');
    const modalBody = modal.querySelector('.edit-modal-body');
    
    modalBody.innerHTML = `
        <div class="edit-form-group">
            <label>Имя философа</label>
            <input type="text" value="${philosopherName}">
        </div>
        <div class="edit-modal-actions">
            <button class="edit-btn edit-btn-primary" onclick="savePhilosopher()">
                Сохранить
            </button>
            <button class="edit-btn edit-btn-secondary" onclick="closeEditModal()">
                Отмена
            </button>
        </div>
    `;
    
    modal.classList.add('show');
    document.getElementById('modalOverlay').classList.add('show');
}
```

### Стало:

```javascript
function openUniversalModal(entityType, data, mode) {
    const modal = document.getElementById('universalModal');
    const modalContent = modal.querySelector('.modal-content');
    
    // Установить режим
    if (mode === 'edit') {
        modal.classList.add('edit-mode');
    } else {
        modal.classList.remove('edit-mode');
    }
    
    // Генерировать контент в зависимости от типа и режима
    if (entityType === 'philosopher' && mode === 'edit') {
        modalContent.innerHTML = `
            <h2>Редактирование философа</h2>
            <div class="modal-form-group">
                <label>Имя философа</label>
                <input type="text" value="${data}">
            </div>
            <div class="modal-actions">
                <button class="modal-btn modal-btn-primary" onclick="savePhilosopher()">
                    Сохранить
                </button>
                <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
                    Отмена
                </button>
            </div>
        `;
    }
    
    modal.classList.add('show');
    document.getElementById('modalOverlay').classList.add('show');
}

// Вызов:
openUniversalModal('philosopher', 'Кант', 'edit');
```

---

## Проверка после миграции

### 1. Визуальная проверка

- [ ] Модальные окна отображаются корректно
- [ ] Кнопки имеют правильные стили
- [ ] Формы выглядят единообразно
- [ ] Scrollbar виден и работает
- [ ] Анимации плавные

### 2. Функциональная проверка

- [ ] Открытие/закрытие модальных окон
- [ ] Переключение между режимами
- [ ] Сохранение данных из форм
- [ ] Поиск концепций работает
- [ ] Сворачивание секций работает

### 3. Проверка консоли

Открыть DevTools и проверить:
- [ ] Нет ошибок JavaScript
- [ ] Нет предупреждений о несуществующих селекторах
- [ ] Все обработчики событий работают

### 4. Адаптивность

- [ ] Модальные окна корректны на мобильных
- [ ] Кнопки доступны
- [ ] Текст читаем
- [ ] Формы удобны для заполнения

---

## Обратная совместимость

Если нужна постепенная миграция, можно создать адаптеры:

```javascript
// Адаптеры для обратной совместимости
function showDetailModal(conceptData) {
    openUniversalModal('concept', conceptData, 'view');
}

function showPhilosopherDetailModal(philosopherName) {
    openUniversalModal('philosopher', philosopherName, 'view');
}

function openEditPhilosopherModal(philosopherName) {
    openUniversalModal('philosopher', philosopherName, 'edit');
}

function openEditConceptModal(conceptData) {
    openUniversalModal('concept', conceptData, 'edit');
}

function closeDetailModal() {
    closeUniversalModal();
}

function closeEditModal() {
    closeUniversalModal();
}
```

Это позволит:
1. Сначала внедрить новую систему стилей
2. Создать адаптеры для старых функций
3. Постепенно мигрировать код на новые функции
4. Удалить адаптеры когда миграция завершена

---

## Итоговая статистика миграции

| Категория | Старых классов | Новых классов | Удалено | Добавлено |
|-----------|---------------|---------------|---------|-----------|
| Модальные окна | 5+ ID | 1 класс | 5 | 1 |
| Формы | 8 классов | 8 классов | 0 | 3 (новые) |
| Списки | 8 классов | 8 классов | 0 | 0 |
| Кнопки | 6 классов | 6 классов | 0 | 1 (mode-switch) |
| Поиск | 6 классов | 6 классов | 0 | 0 |
| **ИТОГО** | **~35** | **~30** | **5** | **5** |

### Выигрыш:
- **-5 дублированных ID** → 1 универсальный класс
- **+5 новых функций** (режимы, взаимодействия, сворачивание)
- **~40% сокращение CSS кода** за счёт унификации
- **100% совместимость** через адаптеры

---

Эта таблица поможет быстро и безошибочно провести миграцию на новую систему стилей.
