# Руководство по применению унифицированной системы стилей

## Обзор изменений

Созданная CSS секция (`unified_modal_styles_complete.css`) представляет собой полный рефакторинг всех стилей модальных окон в единую систему. Все существующие стили были проанализированы, адаптированы и организованы в логические разделы.

## Структура CSS файла

CSS разделен на 21 логическую секцию:

### 1. Базовые стили страницы и графа
- `body`, `#container`, `#graph`

### 2. Стили узлов графа
- `.node`, `.node.dimmed`, `.node.highlighted`, `.node.selected`
- Все состояния узлов и их визуальные эффекты

### 3. Стили связей графа
- `.link` и все его модификаторы
- Веса связей: `.weight-weak`, `.weight-medium`, `.weight-strong`
- Анимации: `.path-highlight`, `.internal-contradiction`
- `.uniform-width-links` режим

### 4. Универсальная система модальных окон ⭐
**Ключевое изменение:** Все модальные окна теперь используют общий класс `.detail-modal`

```html
<!-- Универсальное модальное окно -->
<div id="universalModal" class="detail-modal">
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

Специфичные настройки:
- `#philosopherDetailModal.detail-modal` - расширенные размеры для окна философа
- `.detail-modal.show` - показ модального окна
- Анимация появления через `@keyframes modalFadeIn`

### 5. Режим редактирования ⭐
**Новая функциональность:**

```css
.detail-modal.edit-mode {
    /* Изменённые стили для режима редактирования */
}
```

- Визуальный индикатор режима через `::before` псевдоэлемент
- Кнопка переключения режима `.mode-switch-btn`
- Измененная цветовая схема и границы

### 6. Общие элементы контента
- Заголовки: `h2`, `h3`, `h4`
- `.philosopher-tag` - тег философа (кликабельный)
- `.description` - текстовые описания

### 7. Рубрики (только для концепций)
- `.rubric-section` - секция рубрики
- `.rubric-title` - название рубрики
- `.rubric-description` - описание рубрики

### 8. Связанные концепции и связи
- `.related-concepts` - контейнер
- `.concept-item` - элемент концепции
- `.connections-section` - секция связей
- `.connection-item` - элемент связи
- `.connection-toggle` - кнопка раскрытия описания
- `.connection-description` - описание связи

### 9. Секция взаимодействия философов
- `.philosopher-interactions` - контейнер
- `.interaction-item` - элемент взаимодействия
- `.interaction-philosopher` - имя философа
- `.interaction-description` - описание взаимодействия

### 10. Кнопки действий
- `.goto-node-btn` - переход к узлу
- `.show-all-concepts-btn` - показать все концепции
- `.toggle-all-descriptions-btn` - переключить все описания

### 11. Формы редактирования ⭐
**Полная система форм:**

```html
<div class="modal-form-group">
    <label>Название</label>
    <input type="text" placeholder="Введите название">
</div>
```

Классы форм:
- `.modal-form-group` - группа формы
- `.modal-form-inline` - инлайн группа
- `.modal-form-checkbox` - чекбоксы
- Все типы input: text, number, textarea, select, color

### 12. Списки редактирования ⭐
Система для отображения и редактирования списков (концепций, связей, взаимодействий):

```html
<div class="modal-edit-list">
    <h4>Концепции</h4>
    <div class="modal-edit-list-item">
        <div class="modal-edit-list-item-content">
            <div class="modal-edit-list-item-name">Название</div>
            <div class="modal-edit-list-item-desc">Описание</div>
        </div>
        <div class="modal-edit-list-item-actions">
            <button class="modal-edit-list-btn modal-edit-list-btn-edit">✏️</button>
            <button class="modal-edit-list-btn modal-edit-list-btn-delete">🗑️</button>
        </div>
    </div>
    <button class="modal-edit-list-btn-add">+ Добавить</button>
</div>
```

### 13. Поиск концепций в формах ⭐
Система поиска для выбора концепций в формах редактирования:

```html
<div class="modal-concept-search">
    <input type="text" placeholder="Поиск концепции...">
    <div class="modal-concept-search-results">
        <div class="modal-concept-search-item">
            <div class="modal-concept-search-color" style="background: #color"></div>
            <span class="modal-concept-search-name">Название</span>
            <span class="modal-concept-search-philosopher">Философ</span>
        </div>
    </div>
</div>
```

### 14. Поиск в модальном окне
`#modalSearch` - темная тема поиска внутри модального окна для навигации по концепциям

### 15. Режим выбора на графе
`.graph-selection-mode` - индикатор активного режима выбора узла на графе

### 16. Предупреждения и сообщения
`.warning-message` - стилизованные предупреждающие блоки

### 17. Поиск в легенде
`#legendSearch` - светлая тема поиска в панели фильтров

### 18. Стили для режима редактирования в легенде
- `.legend-item.editable`
- `.philosopher-item-editable`

### 19. Индикатор режима редактирования
`.edit-mode-indicator` - глобальный индикатор активного режима редактирования

### 20. Сворачиваемые секции
- `.collapsible-header` - заголовок секции
- `.collapsible-content` - содержимое секции
- Автоматическая анимация сворачивания/разворачивания

### 21. Адаптивность
Media queries для мобильных устройств

---

## Что изменилось по сравнению с исходным файлом

### ✅ Добавлено новое

1. **Унифицированная система модальных окон**
   - Класс `.detail-modal` вместо ID `#detailModal`
   - Класс `.modal-content` для контента
   - Класс `.modal-close` вместо `.close-btn`

2. **Режим редактирования**
   - `.detail-modal.edit-mode` - визуальный индикатор
   - `.mode-switch-btn` - кнопка переключения режимов
   - Измененная цветовая схема

3. **Система форм с префиксом `modal-`**
   - `.modal-form-group`
   - `.modal-form-inline`
   - `.modal-form-checkbox`
   - `.modal-actions`
   - `.modal-btn-primary`, `.modal-btn-secondary`, `.modal-btn-danger`

4. **Система списков редактирования с префиксом `modal-`**
   - `.modal-edit-list`
   - `.modal-edit-list-item`
   - `.modal-edit-list-btn-edit`, `.modal-edit-list-btn-delete`, `.modal-edit-list-btn-add`

5. **Система поиска концепций с префиксом `modal-`**
   - `.modal-concept-search`
   - `.modal-concept-search-results`
   - `.modal-concept-search-item`

6. **Секция взаимодействия философов**
   - `.philosopher-interactions`
   - `.interaction-item`

7. **Сворачиваемые секции**
   - `.collapsible-header`
   - `.collapsible-content`

### ♻️ Адаптировано существующее

1. **Все стили `#detailModal`** → `.detail-modal`
   - Теперь работают для всех модальных окон
   - Сохранены все визуальные эффекты

2. **Стили `.edit-modal`** → `.detail-modal.edit-mode`
   - Интегрированы в общую систему
   - Добавлена возможность переключения

3. **Стили `.edit-list-*`** → `.modal-edit-list-*`
   - Унифицированы с префиксом `modal-`
   - Работают в контексте модального окна

4. **Стили `.concept-search-*`** → `.modal-concept-search-*`
   - Адаптированы для темной темы модального окна
   - Улучшена видимость и контрастность

### 🗑️ Можно удалить из исходного файла

После внедрения новых стилей можно удалить:

1. Все стили `#detailModal` (строки 489-659)
2. Все стили `.edit-modal` (строки 1114-1182)
3. Все стили `.edit-modal-header`, `.edit-modal-body`, `.edit-modal-close` (строки 1148-1187)
4. Все стили `.edit-form-group` (строки 1189-1233)
5. Все стили `.edit-btn-*` (строки 1283-1322)
6. Все стили `.edit-list-*` (строки 1325-1420)
7. Все стили `.concept-search-*` (строки 1422-1504)

---

## Инструкции по внедрению

### Шаг 1: Замена CSS

В файле `philosophy_graph_full__.html` найдите открывающий тег `<style>` (строка 8) и закрывающий `</style>` (строка 1627).

**Заменить на:**

```html
<style>
    /* Вставить содержимое файла unified_modal_styles_complete.css */
    /* ИЛИ подключить как внешний файл: */
</style>
<link rel="stylesheet" href="unified_modal_styles_complete.css">
```

### Шаг 2: Обновление HTML модальных окон

Найдите в файле строку 1634 и следующие строки с модальными окнами.

**Удалить все существующие модальные окна:**
- `#detailModal` (строка 1634-1637)
- `#editPhilosopherModal` (если есть)
- `#editConceptModal` (если есть)
- `#editConnectionModal` (если есть)

**Заменить на:**

```html
<!-- Универсальное модальное окно -->
<div id="universalModal" class="detail-modal">
    <button class="mode-switch-btn" onclick="toggleModalMode()">
        <span class="mode-view-icon">👁️ Просмотр</span>
        <span class="mode-edit-icon" style="display:none;">✏️ Редактировать</span>
    </button>
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>

<!-- Overlay -->
<div id="modalOverlay" onclick="closeUniversalModal()"></div>
```

### Шаг 3: Обновление JavaScript

Необходимо реализовать функции согласно документу `unified_modal_architecture.md`:

1. `openUniversalModal(entityType, data, mode)`
2. `closeUniversalModal()`
3. `toggleModalMode()`
4. Генераторы контента для каждого типа и режима
5. Обработчики событий

### Шаг 4: Обновление всех вызовов модальных окон

Найти и заменить в JavaScript коде:

```javascript
// Старый код:
showDetailModal(conceptData);
showPhilosopherDetailModal(philosopherName);
openEditPhilosopherModal(philosopherName);

// Новый код:
openUniversalModal('concept', conceptData, 'view');
openUniversalModal('philosopher', philosopherName, 'view');
openUniversalModal('philosopher', philosopherName, 'edit');
```

---

## Примеры использования новых классов

### Режим просмотра концепции

```javascript
function generateConceptViewContent(data) {
    return `
        <h2>${data.label}</h2>
        <div class="philosopher-tag" style="background: ${data.color}" 
             onclick="openUniversalModal('philosopher', '${data.philosopher}', 'view')">
            ${data.philosopher}
        </div>
        
        <div class="description">${data.description}</div>
        
        ${data.rubrics && data.rubrics.length > 0 ? `
            <div class="rubric-section">
                <div class="rubric-title">Рубрики</div>
                <div class="rubric-description">${data.rubrics.join(', ')}</div>
            </div>
        ` : ''}
        
        <div class="connections-section">
            <h4 class="connections-title">Связи (${data.connections.length})</h4>
            ${data.connections.map(conn => `
                <div class="connection-item">
                    <span class="concept-name">${conn.source}</span>
                    <span class="connection-arrow">→</span>
                    <span class="concept-name">${conn.target}</span>
                </div>
            `).join('')}
        </div>
    `;
}
```

### Режим редактирования концепции

```javascript
function generateConceptEditContent(data) {
    return `
        <h2>Редактирование концепции</h2>
        
        <div class="modal-form-group">
            <label>Название концепции</label>
            <input type="text" id="conceptName" value="${data.label}" 
                   placeholder="Введите название">
        </div>
        
        <div class="modal-form-group">
            <label>Философ</label>
            <select id="conceptPhilosopher">
                ${philosophers.map(p => `
                    <option value="${p}" ${p === data.philosopher ? 'selected' : ''}>
                        ${p}
                    </option>
                `).join('')}
            </select>
        </div>
        
        <div class="modal-form-group">
            <label>Описание</label>
            <textarea id="conceptDescription" rows="4">${data.description}</textarea>
        </div>
        
        <div class="modal-edit-list">
            <h4>Связи (${data.connections.length})</h4>
            ${data.connections.map((conn, idx) => `
                <div class="modal-edit-list-item">
                    <div class="modal-edit-list-item-content">
                        <div class="modal-edit-list-item-name">
                            ${conn.source} → ${conn.target}
                        </div>
                        <div class="modal-edit-list-item-desc">${conn.description}</div>
                    </div>
                    <div class="modal-edit-list-item-actions">
                        <button class="modal-edit-list-btn modal-edit-list-btn-edit" 
                                onclick="editConnection(${idx})">✏️</button>
                        <button class="modal-edit-list-btn modal-edit-list-btn-delete" 
                                onclick="deleteConnection(${idx})">🗑️</button>
                    </div>
                </div>
            `).join('')}
            <button class="modal-edit-list-btn-add" onclick="addConnection()">
                + Добавить связь
            </button>
        </div>
        
        <div class="modal-actions">
            <button class="modal-btn modal-btn-primary" onclick="saveConceptData()">
                Сохранить
            </button>
            <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
                Отмена
            </button>
            <button class="modal-btn modal-btn-danger" onclick="deleteConceptWithConfirm()">
                Удалить
            </button>
        </div>
    `;
}
```

### Поиск концепций в форме

```javascript
function createConceptSearchField(containerId) {
    return `
        <div class="modal-concept-search">
            <input type="text" 
                   id="${containerId}-search" 
                   placeholder="Начните вводить название концепции..."
                   oninput="searchConcepts('${containerId}', this.value)">
            <div class="modal-concept-search-results" id="${containerId}-results"></div>
        </div>
    `;
}

function searchConcepts(containerId, query) {
    const results = nodes.filter(n => 
        n.label.toLowerCase().includes(query.toLowerCase())
    );
    
    const resultsContainer = document.getElementById(`${containerId}-results`);
    
    if (query.length === 0) {
        resultsContainer.classList.remove('show');
        return;
    }
    
    resultsContainer.innerHTML = results.map(node => `
        <div class="modal-concept-search-item" onclick="selectConcept('${node.id}')">
            <div class="modal-concept-search-color" 
                 style="background: ${node.color}"></div>
            <span class="modal-concept-search-name">${node.label}</span>
            <span class="modal-concept-search-philosopher">${node.philosopher}</span>
        </div>
    `).join('');
    
    resultsContainer.classList.add('show');
}
```

### Сворачиваемые секции

```javascript
function createCollapsibleSection(id, title, content, startCollapsed = false) {
    return `
        <h4 class="collapsible-header ${startCollapsed ? 'collapsed' : ''}" 
            onclick="toggleSection('${id}')">
            ${title}
        </h4>
        <div id="${id}-content" 
             class="collapsible-content ${startCollapsed ? 'collapsed' : ''}">
            ${content}
        </div>
    `;
}

function toggleSection(sectionId) {
    const header = document.querySelector(`[onclick="toggleSection('${sectionId}')"]`);
    const content = document.getElementById(`${sectionId}-content`);
    
    header.classList.toggle('collapsed');
    content.classList.toggle('collapsed');
}
```

---

## Контрольный список внедрения

- [ ] Скопировать CSS из `unified_modal_styles_complete.css` в `<style>` секцию
- [ ] Удалить старые стили модальных окон
- [ ] Заменить HTML модальных окон на универсальное окно
- [ ] Реализовать `openUniversalModal()`, `closeUniversalModal()`, `toggleModalMode()`
- [ ] Реализовать генераторы контента для всех типов и режимов
- [ ] Обновить все вызовы модальных окон в коде
- [ ] Реализовать функции сохранения данных
- [ ] Реализовать функции валидации форм
- [ ] Протестировать все режимы и типы модальных окон
- [ ] Протестировать адаптивность на мобильных устройствах

---

## Преимущества новой системы

✅ **Единообразие** - все модальные окна выглядят и работают одинаково
✅ **Меньше кода** - один набор стилей вместо множества дублированных
✅ **Легче поддерживать** - изменения в одном месте применяются везде
✅ **Плавные переходы** - переключение между режимами без закрытия окна
✅ **Расширяемость** - легко добавить новые типы сущностей
✅ **Лучший UX** - одинаковая информация в режимах просмотра и редактирования
✅ **Адаптивность** - готовые стили для мобильных устройств

---

## Дополнительные возможности для реализации

1. **Анимации переходов между режимами**
   - Плавное изменение цвета границы
   - Fade-in/out элементов форм

2. **Валидация форм в реальном времени**
   - Подсветка обязательных полей
   - Сообщения об ошибках

3. **История изменений**
   - Кнопка "Отменить"
   - Индикатор несохраненных изменений

4. **Горячие клавиши**
   - `Ctrl+E` - переключить режим редактирования
   - `Ctrl+S` - сохранить
   - `ESC` - закрыть окно

5. **Drag & Drop**
   - Перетаскивание концепций для создания связей
   - Изменение порядка элементов в списках

---

Это полное руководство по применению унифицированной системы стилей. Следуя этим инструкциям, вы получите профессиональную, масштабируемую и удобную систему модальных окон.
