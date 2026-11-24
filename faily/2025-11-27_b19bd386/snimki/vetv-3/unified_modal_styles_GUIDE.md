# РУКОВОДСТВО ПО ПРИМЕНЕНИЮ УНИФИЦИРОВАННЫХ СТИЛЕЙ
# Полный анализ и инструкции

## 📋 ОБЗОР

Этот документ содержит:
1. Анализ всех стилей из оригинального файла
2. Исчерпывающую секцию стилей для унифицированной системы
3. Рекомендации по применению
4. Изменения, которые нужно внести в HTML

---

## 🔍 АНАЛИЗ ОРИГИНАЛЬНЫХ СТИЛЕЙ

### Найдено в оригинальном файле (строки 489-1626):

#### 1. **Базовые стили модального окна** (строки 489-659)
- ✅ **Адаптировано** → `.detail-modal` (вместо `#detailModal`)
- Включает: фон, позиционирование, размеры, overflow
- Стили для кнопки закрытия
- Scrollbar стили
- Стили для `philosopher-tag`, `description`, `rubric-section`, `related-concepts`

#### 2. **Стили для связей на графе** (строки 662-723)
- ✅ **Оставлено без изменений** (не относится к модальным окнам)
- Веса связей: `.link.weight-weak`, `.link.weight-medium`, `.link.weight-strong`
- Внутренние противоречия: `.link.internal-contradiction`
- Легенда весов: `.weight-legend`, `.weight-item`

#### 3. **Секция связей узла** (строки 724-886)
- ✅ **Адаптировано** → добавлено в новую систему
- Кнопки: `.goto-node-btn`, `.show-all-concepts-btn`, `.toggle-all-descriptions-btn`
- Секция связей: `.connections-section`, `.connection-item`
- Раскрытие описаний: `.connection-toggle`, `.connection-description`
- Стрелки с подсказками: `.connection-arrow`, `.connection-arrow-tooltip`

#### 4. **Режим одинаковой толщины связей** (строки 888-891)
- ✅ **Оставлено без изменений** (не относится к модальным окнам)
- `.uniform-width-links .link`

#### 5. **Поиск в панели фильтров (легенде)** (строки 893-1033)
- ✅ **Оставлено без изменений** (не относится к модальным окнам)
- `#legendSearch` и связанные стили

#### 6. **Поиск в модальном окне** (строки 1034-1109)
- ✅ **Адаптировано** → сохранено в `#modalSearch`
- Темная тема для модального окна
- Все стили для поиска внутри модального окна

#### 7. **Модальные окна редактирования** (строки 1110-1626)
- ✅ **Полностью адаптировано** → интегрировано в новую систему
- Заменено:
  - `.edit-modal` → `.detail-modal.edit-mode`
  - `.edit-modal-header` → убрано (используем единую структуру)
  - `.edit-modal-body` → `.modal-content`
  - `.edit-form-group` → `.modal-form-group`
  - `.edit-modal-actions` → `.modal-actions`
  - `.edit-btn` → `.modal-btn`
  - `.edit-list-section` → `.modal-edit-section`
  - `.edit-list-item` → `.modal-edit-list-item`
  - `.concept-search-container` → `.modal-concept-search`

---

## 📦 ЧТО ВКЛЮЧЕНО В НОВУЮ СИСТЕМУ СТИЛЕЙ

### Секция 1: Базовая структура модального окна
- Overlay (`#modalOverlay`)
- Универсальное модальное окно (`.detail-modal`)
- Специфичные настройки для окна философа (`#philosopherDetailModal.detail-modal`)

### Секция 2: Кнопка закрытия
- `.modal-close`, `.close-btn`

### Секция 3: Кнопка переключения режимов
- ✨ **НОВОЕ**: `.mode-switch-btn`

### Секция 4: Индикатор режима редактирования
- ✨ **НОВОЕ**: `.detail-modal.edit-mode`
- ✨ **НОВОЕ**: `.detail-modal.edit-mode::before` (метка "✏️ Режим редактирования")

### Секция 5: Контент модального окна
- Заголовки: `h2`, `h3`, `h4`
- Описания: `.description`

### Секция 6: Теги философов
- `.philosopher-tag` (с hover эффектом)

### Секция 7: Секция рубрик
- `.rubric-section`, `.rubric-title`, `.rubric-description`
- Показывается только в режиме просмотра концепции

### Секция 8: Связанные концепции
- `.related-concepts`, `.related-title`, `.concept-item`
- Элементы: `.concept-color`, `.concept-name`, `.concept-philosopher`

### Секция 9: Секция связей узла
- `.connections-section`, `.connections-title`, `.connection-item`
- Раскрывающиеся описания: `.connection-toggle`, `.connection-description`
- Кнопки: `.toggle-all-descriptions-btn`, `.show-all-concepts-btn`, `.goto-node-btn`

### Секция 10: Секция взаимодействия философов
- ✨ **НОВОЕ**: `.philosopher-interactions-section`
- `.philosopher-interaction-item`

### Секция 11: Поиск в модальном окне
- Сохранено `#modalSearch` (темная тема)
- Все стили для поиска

### Секция 12: Scrollbar
- Стили для scrollbar модального окна

### Секция 13: Формы редактирования
- `.modal-form-group` (было `.edit-form-group`)
- Все типы input элементов
- `.modal-form-inline` (для размещения полей в строку)
- `.modal-form-checkbox` (для чекбоксов)

### Секция 14: Кнопки действий
- `.modal-actions` (было `.edit-modal-actions`)
- `.modal-btn`, `.modal-btn-primary`, `.modal-btn-secondary`, `.modal-btn-danger`

### Секция 15: Списки редактирования
- `.modal-edit-section` (было `.edit-list-section`)
- `.modal-edit-list`, `.modal-edit-list-item`
- Кнопки: `.modal-list-btn-edit`, `.modal-list-btn-delete`, `.modal-list-btn-add`

### Секция 16: Поиск концепций в формах
- `.modal-concept-search` (было `.concept-search-container`)
- `.modal-concept-search-input`, `.modal-concept-search-results`
- `.modal-concept-search-item`

### Секция 17: Режим выбора на графе
- `.graph-selection-mode`
- `.graph-selection-cancel`

### Секция 18: Предупреждающие сообщения
- `.modal-warning` (было `.warning-message`)

### Секция 19: Сворачиваемые секции
- ✨ **НОВОЕ**: `.collapsible-section`, `.collapsible-header`, `.collapsible-content`

### Секция 20: Анимации
- `@keyframes modalSlideIn`
- `@keyframes slideDown`
- `@keyframes slideInRight`

### Секция 21: Дополнительные утилиты
- ✨ **НОВОЕ**: `.modal-divider`, `.modal-hint`, `.modal-status-badge`

---

## 🔄 ЧТО НУЖНО ИЗМЕНИТЬ В HTML

### 1. Замена всех модальных окон на одно универсальное

**БЫЛО (5 разных окон):**
```html
<div id="detailModal">...</div>
<div id="philosopherDetailModal">...</div>
<div id="editPhilosopherModal" class="edit-modal">...</div>
<div id="editConceptModal" class="edit-modal">...</div>
<div id="editConnectionModal" class="edit-modal">...</div>
```

**СТАЛО (1 универсальное окно):**
```html
<div id="universalModal" class="detail-modal">
    <button class="mode-switch-btn" onclick="toggleModalMode()">
        <span id="modeIcon">✏️</span> <span id="modeText">Редактировать</span>
    </button>
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

### 2. Замена классов в генераторах контента

#### В режиме просмотра (view mode):

**Секция рубрик:**
```html
<div class="rubric-section">
    <div class="rubric-title">Название рубрики</div>
    <div class="rubric-description">Описание рубрики</div>
</div>
```

**Секция связей:**
```html
<div class="connections-section">
    <div class="connections-title">Связи концепции</div>
    <div class="connection-item">
        <!-- Элементы связи -->
    </div>
</div>
```

**Секция взаимодействия философов:**
```html
<div class="philosopher-interactions-section">
    <div class="philosopher-interactions-title">Взаимодействия с другими философами</div>
    <div class="philosopher-interaction-item">
        <!-- Элементы взаимодействия -->
    </div>
</div>
```

#### В режиме редактирования (edit mode):

**Группы форм:**
```html
<div class="modal-form-group">
    <label>Название</label>
    <input type="text" placeholder="Введите название...">
</div>

<div class="modal-form-group modal-form-inline">
    <div>
        <label>Поле 1</label>
        <input type="text">
    </div>
    <div>
        <label>Поле 2</label>
        <input type="text">
    </div>
</div>

<div class="modal-form-checkbox">
    <input type="checkbox" id="someCheckbox">
    <label for="someCheckbox">Опция</label>
</div>
```

**Кнопки действий:**
```html
<div class="modal-actions">
    <button class="modal-btn modal-btn-primary" onclick="saveData()">Сохранить</button>
    <button class="modal-btn modal-btn-secondary" onclick="cancel()">Отмена</button>
    <button class="modal-btn modal-btn-danger" onclick="deleteData()">Удалить</button>
</div>
```

**Секция редактирования списков:**
```html
<div class="modal-edit-section">
    <h4>Связи концепции</h4>
    <div class="modal-edit-list">
        <div class="modal-edit-list-item">
            <div class="modal-edit-list-item-content">
                <div class="modal-edit-list-item-name">Название связи</div>
                <div class="modal-edit-list-item-desc">Описание</div>
            </div>
            <div class="modal-edit-list-item-actions">
                <button class="modal-list-btn modal-list-btn-edit">✏️</button>
                <button class="modal-list-btn modal-list-btn-delete">🗑️</button>
            </div>
        </div>
    </div>
    <button class="modal-list-btn-add">+ Добавить связь</button>
</div>
```

**Поиск концепций:**
```html
<div class="modal-concept-search">
    <input type="text" 
           class="modal-concept-search-input" 
           placeholder="Поиск концепций...">
    <div class="modal-concept-search-results">
        <div class="modal-concept-search-item">
            <div class="modal-concept-search-color" style="background: #ff0000;"></div>
            <div class="modal-concept-search-name">Название концепции</div>
            <div class="modal-concept-search-philosopher">Философ</div>
        </div>
    </div>
</div>
```

**Сворачиваемая секция:**
```html
<div class="collapsible-section">
    <div class="collapsible-header" onclick="toggleCollapse(this)">
        <span class="collapsible-header-title">Внутренние связи</span>
        <span class="collapsible-toggle">▼</span>
    </div>
    <div class="collapsible-content">
        <!-- Контент секции -->
    </div>
</div>
```

---

## 🎯 РЕКОМЕНДАЦИИ ПО ПРИМЕНЕНИЮ

### 1. Порядок внедрения стилей

#### Шаг 1: Замена в `<style>` секции HTML файла
```html
<style>
    /* Базовые стили body, graph, nodes, links (оставить без изменений) */
    
    /* ВСТАВИТЬ СЮДА ВСЕ СТИЛИ ИЗ unified_modal_styles_COMPLETE.css */
    
    /* Стили легенды и других элементов (оставить без изменений) */
</style>
```

#### Шаг 2: Замена HTML структуры модальных окон
Заменить все 5 модальных окон на одно универсальное (см. раздел выше).

#### Шаг 3: Обновление генераторов контента
Заменить все классы в функциях генерации контента:
- `generatePhilosopherViewContent()`
- `generatePhilosopherEditContent()`
- `generateConceptViewContent()`
- `generateConceptEditContent()`
- `generateConnectionViewContent()`
- `generateConnectionEditContent()`

### 2. Сохранённые ID селекторы

Эти стили остались с ID селекторами (не менять):
- `#modalOverlay` - overlay для всех модальных окон
- `#universalModal` - основной ID универсального модального окна
- `#philosopherDetailModal` - если решишь оставить отдельное окно для философа
- `#modalSearch` - поиск внутри модального окна

### 3. Новые возможности

#### Переключатель режимов
```javascript
function toggleModalMode() {
    const modal = document.getElementById('universalModal');
    const isEditMode = modal.classList.contains('edit-mode');
    
    if (isEditMode) {
        // Переход из edit → view
        modal.classList.remove('edit-mode');
        // Регенерировать контент в режиме просмотра
        regenerateModalContent(ModalContext.currentEntity, ModalContext.currentData, 'view');
    } else {
        // Переход из view → edit
        modal.classList.add('edit-mode');
        // Регенерировать контент в режиме редактирования
        regenerateModalContent(ModalContext.currentEntity, ModalContext.currentData, 'edit');
    }
}
```

#### Использование сворачиваемых секций
```javascript
function toggleCollapse(headerElement) {
    const toggle = headerElement.querySelector('.collapsible-toggle');
    const content = headerElement.nextElementSibling;
    
    toggle.classList.toggle('expanded');
    content.classList.toggle('show');
}
```

### 4. Стили, которые можно оставить без изменений

**НЕ относятся к модальным окнам и остаются как есть:**
- Стили для графа (nodes, links)
- Стили для легенды (`#legend`)
- Стили для поиска в легенде (`#legendSearch`)
- Стили для весов связей (`.link.weight-*`)
- Стили для режима одинаковой толщины (`.uniform-width-links`)
- Все остальные стили до строки 489 и после строки 1626

---

## ✅ ПРЕИМУЩЕСТВА НОВОЙ СИСТЕМЫ СТИЛЕЙ

1. **Единообразие** - все модальные окна используют одни и те же классы
2. **DRY принцип** - нет дублирования кода
3. **Легко поддерживать** - изменения в одном месте
4. **Масштабируемость** - легко добавить новые типы сущностей
5. **Режим редактирования** - встроенная поддержка с визуальным индикатором
6. **Переключение режимов** - плавные переходы без закрытия окна
7. **Больше возможностей** - сворачиваемые секции, статусные значки, подсказки

---

## 📝 ЧЕКЛИСТ ВНЕДРЕНИЯ

- [ ] Заменить секцию стилей в HTML файле (строки 489-1626)
- [ ] Вставить стили из `unified_modal_styles_COMPLETE.css`
- [ ] Заменить HTML структуру модальных окон (5 окон → 1 окно)
- [ ] Обновить генераторы контента (6 функций)
- [ ] Обновить функции открытия модальных окон
- [ ] Реализовать функцию `toggleModalMode()`
- [ ] Обновить обработчики событий (ESC, overlay)
- [ ] Протестировать все режимы работы
- [ ] Протестировать переключение режимов
- [ ] Протестировать формы редактирования

---

## 🎨 ВИЗУАЛЬНЫЕ ОСОБЕННОСТИ

### В режиме просмотра (view):
- Стандартная тёмная тема
- Синяя рамка окна
- Секции с информацией
- Кнопка "✏️ Редактировать" в правом верхнем углу

### В режиме редактирования (edit):
- Тёмная тема с фиолетовой рамкой
- Индикатор "✏️ Режим редактирования" над окном
- Формы с полями ввода
- Кнопки действий внизу (Сохранить, Отмена, Удалить)
- Кнопка "👁️ Просмотр" для возврата

### Общие элементы:
- Кнопка закрытия "×" в правом верхнем углу
- Scrollbar с тёмной темой
- Плавные анимации при открытии/закрытии
- Hover эффекты на всех интерактивных элементах

---

## 📞 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

Полный файл стилей сохранён в:
`/mnt/user-data/outputs/unified_modal_styles_COMPLETE.css`

Размер: 21 секция, ~1100 строк CSS
Совместимость: все современные браузеры (Chrome, Firefox, Safari, Edge)
Зависимости: нет (чистый CSS)

---

**Готово к применению! 🚀**
