# КРАТКАЯ ПАМЯТКА: ЗАМЕНА КЛАССОВ

## 🔄 ТАБЛИЦА ЗАМЕНЫ КЛАССОВ

| **СТАРЫЙ КЛАСС** | **НОВЫЙ КЛАСС** | **ПРИМЕЧАНИЕ** |
|------------------|-----------------|----------------|
| `.edit-modal` | `.detail-modal` | Базовое модальное окно |
| `.edit-modal.show` | `.detail-modal.show` | Показ окна |
| `.edit-modal-header` | (убрано) | Используем единую структуру |
| `.edit-modal-close` | `.modal-close` | Кнопка закрытия |
| `.edit-modal-body` | `.modal-content` | Контент окна |
| `.edit-form-group` | `.modal-form-group` | Группа полей формы |
| `.edit-form-group.inline` | `.modal-form-inline` | Поля в строку |
| `.edit-form-checkbox` | `.modal-form-checkbox` | Чекбокс |
| `.edit-modal-actions` | `.modal-actions` | Контейнер кнопок |
| `.edit-btn` | `.modal-btn` | Базовая кнопка |
| `.edit-btn-primary` | `.modal-btn-primary` | Главная кнопка |
| `.edit-btn-secondary` | `.modal-btn-secondary` | Вторичная кнопка |
| `.edit-btn-danger` | `.modal-btn-danger` | Кнопка удаления |
| `.edit-list-section` | `.modal-edit-section` | Секция списка |
| `.edit-list-item` | `.modal-edit-list-item` | Элемент списка |
| `.edit-list-item-content` | `.modal-edit-list-item-content` | Контент элемента |
| `.edit-list-item-name` | `.modal-edit-list-item-name` | Название элемента |
| `.edit-list-item-desc` | `.modal-edit-list-item-desc` | Описание элемента |
| `.edit-list-item-actions` | `.modal-edit-list-item-actions` | Кнопки действий |
| `.edit-list-btn` | `.modal-list-btn` | Кнопка в списке |
| `.edit-list-btn-edit` | `.modal-list-btn-edit` | Кнопка редактирования |
| `.edit-list-btn-delete` | `.modal-list-btn-delete` | Кнопка удаления |
| `.edit-list-btn-add` | `.modal-list-btn-add` | Кнопка добавления |
| `.concept-search-container` | `.modal-concept-search` | Контейнер поиска |
| `.concept-search-input` | `.modal-concept-search-input` | Поле поиска |
| `.concept-search-results` | `.modal-concept-search-results` | Результаты поиска |
| `.concept-search-item` | `.modal-concept-search-item` | Элемент результата |
| `.concept-search-color` | `.modal-concept-search-color` | Цвет концепции |
| `.concept-search-name` | `.modal-concept-search-name` | Название концепции |
| `.concept-search-philosopher` | `.modal-concept-search-philosopher` | Философ |
| `.warning-message` | `.modal-warning` | Предупреждение |

---

## ✨ НОВЫЕ КЛАССЫ

| **КЛАСС** | **НАЗНАЧЕНИЕ** |
|-----------|----------------|
| `.mode-switch-btn` | Кнопка переключения режимов |
| `.detail-modal.edit-mode` | Режим редактирования |
| `.collapsible-section` | Сворачиваемая секция |
| `.collapsible-header` | Заголовок секции |
| `.collapsible-content` | Контент секции |
| `.modal-divider` | Разделитель |
| `.modal-hint` | Подсказка |
| `.modal-status-badge` | Статусный значок |

---

## 📝 БЫСТРЫЕ ПРИМЕРЫ

### Простая форма редактирования:
```html
<div class="modal-form-group">
    <label>Название</label>
    <input type="text" placeholder="Введите название...">
</div>

<div class="modal-actions">
    <button class="modal-btn modal-btn-primary">Сохранить</button>
    <button class="modal-btn modal-btn-secondary">Отмена</button>
</div>
```

### Список с кнопками редактирования:
```html
<div class="modal-edit-section">
    <h4>Список элементов</h4>
    <div class="modal-edit-list">
        <div class="modal-edit-list-item">
            <div class="modal-edit-list-item-content">
                <div class="modal-edit-list-item-name">Элемент 1</div>
            </div>
            <div class="modal-edit-list-item-actions">
                <button class="modal-list-btn modal-list-btn-edit">✏️</button>
                <button class="modal-list-btn modal-list-btn-delete">🗑️</button>
            </div>
        </div>
    </div>
    <button class="modal-list-btn-add">+ Добавить</button>
</div>
```

### Сворачиваемая секция:
```html
<div class="collapsible-section">
    <div class="collapsible-header" onclick="toggleCollapse(this)">
        <span class="collapsible-header-title">Внутренние связи</span>
        <span class="collapsible-toggle">▼</span>
    </div>
    <div class="collapsible-content">
        <!-- Контент -->
    </div>
</div>
```

---

## 🎯 ОСНОВНЫЕ ПРАВИЛА

1. **Все модальные окна** → используют класс `.detail-modal`
2. **Режим редактирования** → добавляется класс `.edit-mode`
3. **Префикс `modal-`** → для всех элементов модального окна
4. **ID селекторы** → только для `#universalModal`, `#modalOverlay`, `#modalSearch`
5. **Классы `edit-*`** → заменяются на `modal-*`

---

## ⚡ ПОИСК И ЗАМЕНА В КОДЕ

```javascript
// JavaScript: Find & Replace

// 1. Замена открытия модальных окон
showDetailModal(data) → openUniversalModal('concept', data, 'view')
showPhilosopherDetailModal(name) → openUniversalModal('philosopher', name, 'view')
openEditPhilosopherModal(name) → openUniversalModal('philosopher', name, 'edit')
openEditConceptModal(data) → openUniversalModal('concept', data, 'edit')
openEditConnectionModal(data) → openUniversalModal('connection', data, 'edit')

// 2. Замена закрытия модальных окон
closeDetailModal() → closeUniversalModal()
closeEditModal() → closeUniversalModal()
```

```html
<!-- HTML: Find & Replace -->

edit-modal → detail-modal
edit-modal-close → modal-close
edit-modal-body → modal-content
edit-form-group → modal-form-group
edit-modal-actions → modal-actions
edit-btn → modal-btn
edit-list-section → modal-edit-section
edit-list-item → modal-edit-list-item
concept-search-container → modal-concept-search
warning-message → modal-warning
```

---

## 🔍 КЛАССЫ, КОТОРЫЕ ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ

Эти классы используются вне модальных окон и не требуют изменений:

- `.node`, `.link` (граф)
- `#legend`, `.legend-item` (легенда)
- `#legendSearch` (поиск в легенде)
- `.graph-selection-mode` (режим выбора)
- `.philosopher-tag` (теги философов - используется и в модальных окнах)
- `.connection-*` (элементы связей - используются и в модальных окнах)
- `.concept-*` (элементы концепций - используются и в модальных окнах)

---

**Все файлы готовы! ✅**
- `unified_modal_styles_COMPLETE.css` - полный файл стилей
- `unified_modal_styles_GUIDE.md` - подробное руководство
- `unified_modal_styles_CHEATSHEET.md` - эта краткая памятка
