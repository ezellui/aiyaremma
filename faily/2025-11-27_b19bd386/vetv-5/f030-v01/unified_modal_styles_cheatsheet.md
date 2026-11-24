# Краткая справочная памятка по стилям унифицированной системы

## 🎯 Быстрый старт

### Основная структура HTML
```html
<div id="universalModal" class="detail-modal">
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

### Открытие окна
```javascript
openUniversalModal('philosopher', data, 'view');  // Просмотр философа
openUniversalModal('concept', data, 'edit');      // Редактирование концепции
```

---

## 📋 Основные классы

### Модальное окно
| Класс | Назначение |
|-------|-----------|
| `.detail-modal` | Основной контейнер |
| `.detail-modal.show` | Показать окно |
| `.detail-modal.edit-mode` | Режим редактирования |
| `.modal-close` | Кнопка закрытия |
| `.mode-switch-btn` | Переключение view ↔ edit |

### Контент
| Класс | Назначение |
|-------|-----------|
| `h2` | Главный заголовок |
| `h3` | Подзаголовок |
| `.philosopher-tag` | Тег философа (кликабельный) |
| `.description` | Текстовое описание |

### Рубрики (только view)
| Класс | Назначение |
|-------|-----------|
| `.rubric-section` | Контейнер рубрики |
| `.rubric-title` | Заголовок |
| `.rubric-description` | Описание |

### Списки концепций (view)
| Класс | Назначение |
|-------|-----------|
| `.related-concepts` | Контейнер списка |
| `.concept-item` | Элемент концепции |
| `.concept-color` | Цветовой индикатор |
| `.concept-name` | Название |
| `.concept-philosopher` | Философ |

### Концепции философа (view)
| Класс | Назначение |
|-------|-----------|
| `.philosopher-concepts-list` | Контейнер всех концепций |
| `.philosopher-concept-item` | Элемент концепции |
| `.philosopher-concept-header` | Заголовок с кнопкой |
| `.toggle-concept-desc-btn` | Кнопка раскрытия описания |
| `.concept-extended-desc` | Развёрнутое описание |
| `.concept-extended-desc.show` | Показать описание |

### Связи (view и edit)
| Класс | Назначение |
|-------|-----------|
| `.connections-section` | Основной контейнер |
| `.connections-subsection` | Подсекция (внутренние/внешние) |
| `.subsection-header` | Кликабельный заголовок |
| `.subsection-toggle` | Стрелка ▼ |
| `.subsection-content` | Контент подсекции |
| `.connection-item` | Элемент связи |
| `.connection-arrow` | Стрелка с типом связи |
| `.connection-toggle` | Кнопка раскрытия описания |
| `.connection-description` | Описание связи |
| `.connection-description.show` | Показать описание |

### Формы (edit)
| Класс | Назначение |
|-------|-----------|
| `.modal-form-group` | Группа полей |
| `label` | Метка поля |
| `input[type="text"]` | Текстовое поле |
| `input[type="number"]` | Числовое поле |
| `input[type="color"]` | Выбор цвета |
| `textarea` | Многострочное поле |
| `select` | Выпадающий список |
| `.modal-form-checkbox` | Чекбокс |
| `.modal-form-inline` | Горизонтальные поля |

### Кнопки (edit)
| Класс | Назначение | Цвет |
|-------|-----------|------|
| `.modal-btn` | Базовая кнопка | - |
| `.modal-btn-primary` | Сохранить | Фиолетовый |
| `.modal-btn-secondary` | Отмена | Серый |
| `.modal-btn-danger` | Удалить | Красный |
| `.modal-actions` | Контейнер кнопок | - |

### Списки редактирования (edit)
| Класс | Назначение |
|-------|-----------|
| `.modal-edit-list` | Контейнер списка |
| `.modal-edit-list-header` | Заголовок с кнопкой |
| `.modal-edit-list-item` | Элемент списка |
| `.modal-edit-list-btn` | Кнопка удаления (красная) |
| `.modal-edit-list-btn-add` | Кнопка добавления (зелёная) |

### Поиск концепций (edit)
| Класс | Назначение |
|-------|-----------|
| `.modal-concept-search` | Контейнер поиска |
| `input` | Поле ввода |
| `.modal-concept-search-results` | Список результатов |
| `.modal-concept-search-results.show` | Показать результаты |
| `.modal-concept-search-item` | Элемент результата |

### Утилитарные классы
| Класс | Эффект |
|-------|--------|
| `.hidden` | Скрыть элемент |
| `.text-ellipsis` | Обрезать текст с ... |
| `.divider` | Горизонтальная линия |
| `.font-bold` | Жирный текст |
| `.font-italic` | Курсив |
| `.text-small` | Мелкий текст |
| `.text-muted` | Приглушённый цвет |
| `.text-center` | Центрировать |
| `.mt-10`, `.mt-15`, `.mt-20` | Отступ сверху |
| `.mb-10`, `.mb-15`, `.mb-20` | Отступ снизу |

---

## 🎨 Цветовая палитра

| Назначение | Цвет | HEX |
|------------|------|-----|
| Акцент | 🟣 | `#a29bfe` |
| Акцент (hover) | 🟣 | `#8b7fe6` |
| Primary кнопка | 🟣 | `#a29bfe` |
| Danger кнопка | 🔴 | `#e74c3c` |
| Success кнопка | 🟢 | `#2ecc71` |
| Текст основной | ⚪ | `#e0e0e0` |
| Текст приглушённый | ⚪ | `#b0b0b0` |
| Фон окна | ⚫ | `rgba(0,0,0,0.92)` |
| Фон поля | ⚪ | `rgba(255,255,255,0.08)` |

---

## 📱 Z-index иерархия

| Элемент | Z-index |
|---------|---------|
| Graph selection mode | 1000 |
| Concept search results | 1000 |
| Modal overlay | 1999 |
| Modal window | 2000 |
| Close button & mode switch | 10 (relative to modal) |

---

## 🔄 Состояния и модификаторы

### Показать/скрыть
```css
.element { display: none; }
.element.show { display: block; }
```

### Режим редактирования
```css
.detail-modal.edit-mode { /* стили */ }
```

### Свёрнутое состояние
```css
.subsection-content.collapsed { display: none; }
.subsection-toggle.collapsed { transform: rotate(-90deg); }
```

### Раскрытое описание
```css
.concept-extended-desc.show { display: block; }
.toggle-concept-desc-btn.expanded { background: #a29bfe; }
```

---

## 🎬 Анимации

| Анимация | Применение |
|----------|-----------|
| `modalFadeIn` | Появление окна (0.3s) |
| `slideInRight` | Появление graph-selection-mode (0.3s) |
| `hover transitions` | Все интерактивные элементы (0.2-0.3s) |

---

## 📦 Шаблоны использования

### Кнопка с иконкой
```html
<button class="modal-btn modal-btn-primary">
    💾 Сохранить
</button>
```

### Группа полей формы
```html
<div class="modal-form-group">
    <label>Название концепции</label>
    <input type="text" placeholder="Введите название">
</div>
```

### Инлайн поля (год рождения/смерти)
```html
<div class="modal-form-inline">
    <div class="modal-form-group">
        <label>Год рождения</label>
        <input type="number" placeholder="1724">
    </div>
    <div class="modal-form-group">
        <label>Год смерти</label>
        <input type="number" placeholder="1804">
    </div>
</div>
```

### Чекбокс
```html
<div class="modal-form-checkbox">
    <input type="checkbox" id="bidirectional">
    <label for="bidirectional">Двунаправленная связь</label>
</div>
```

### Концепция в списке
```html
<div class="concept-item" onclick="showDetailModal(concept)">
    <div class="concept-color" style="background: #ff6b6b"></div>
    <div class="concept-name">Категорический императив</div>
    <div class="concept-philosopher">Кант</div>
</div>
```

### Связь с описанием
```html
<div class="connection-item">
    <div class="concept-color" style="background: #ff6b6b"></div>
    <div style="flex-grow: 1;">
        <span>Априорное знание</span>
        <div class="connection-arrow" style="color: #4ecdc4;">
            →
            <span class="connection-arrow-tooltip">Основа для</span>
        </div>
        <span>Трансцендентальное единство апперцепции</span>
    </div>
    <button class="connection-toggle" onclick="toggleConnectionDescription('id')">
        ▼
    </button>
</div>
<div class="connection-description" id="desc-id">
    Априорное знание служит основой для...
</div>
```

### Кнопки действий
```html
<div class="modal-actions">
    <button class="modal-btn modal-btn-primary" onclick="save()">
        💾 Сохранить
    </button>
    <button class="modal-btn modal-btn-secondary" onclick="cancel()">
        ✖️ Отмена
    </button>
    <button class="modal-btn modal-btn-danger" onclick="deleteItem()">
        🗑️ Удалить
    </button>
</div>
```

---

## 🐛 Частые ошибки

### ❌ Неправильно
```html
<!-- Класс .show забыт -->
<div id="universalModal" class="detail-modal">

<!-- Неправильная вложенность -->
<div class="modal-actions modal-btn-primary">

<!-- ID вместо класса -->
<div id="detail-modal">
```

### ✅ Правильно
```html
<!-- Класс .show добавлен -->
<div id="universalModal" class="detail-modal show">

<!-- Правильная вложенность -->
<div class="modal-actions">
    <button class="modal-btn modal-btn-primary">

<!-- Класс вместо ID -->
<div class="detail-modal">
```

---

## 🔍 Поиск нужного стиля

### "Как стилизовать..."

**...заголовок в модальном окне?**
→ `h2` или `h3`

**...тег философа?**
→ `.philosopher-tag`

**...список концепций?**
→ `.related-concepts` → `.concept-item`

**...связи между концепциями?**
→ `.connections-section` → `.connection-item`

**...поле ввода в форме?**
→ `.modal-form-group` → `input`

**...кнопку "Сохранить"?**
→ `.modal-btn.modal-btn-primary`

**...кнопку удаления в списке?**
→ `.modal-edit-list-btn`

**...поиск концепций?**
→ `.modal-concept-search`

---

## 📚 Полезные ссылки

- **Полная CSS:** `unified_modal_complete_styles.css`
- **Документация:** `unified_modal_styles_documentation.md`
- **Архитектура:** `unified_modal_architecture.md`

---

## 💡 Советы

1. **Всегда используйте классы**, не ID для стилизации
2. **Не модифицируйте базовые классы** (`.detail-modal`), создавайте специфичные
3. **Используйте утилитарные классы** для быстрой стилизации
4. **Следуйте иерархии** классов (не вкладывайте `.modal-btn` вне `.modal-actions`)
5. **Тестируйте оба режима** (view и edit) после изменений

---

*Эта памятка содержит 95% самых часто используемых классов и паттернов*
