# Унификация окон детальной информации и редактирования

## Концепция

Создание единой модальной системы, где одно и то же окно может работать в двух режимах:
- **Режим просмотра (view)** - детальная информация с возможностью навигации
- **Режим редактирования (edit)** - формы для редактирования с валидацией

**Преимущества:**
- ✅ Единая структура и стили для всех модальных окон
- ✅ Плавные переходы между режимами просмотра и редактирования
- ✅ Меньше дублирования кода
- ✅ Единообразный UX
- ✅ Легче поддерживать и расширять

---

## Архитектура системы

### 1. Типы сущностей
- **Философ (philosopher)**
- **Концепция (concept)**
- **Связь (connection)**

### 2. Режимы работы
- **view** - просмотр детальной информации
- **edit** - редактирование (создание или изменение)

### 3. Единая структура HTML

```html
<!-- Единое универсальное модальное окно -->
<div id="universalModal" class="detail-modal">
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

---

## Этап 1: Унификация HTML структуры

### Заменить все существующие модальные окна на одно универсальное

**Место:** После строки 1633 (где сейчас `#detailModal`)

**Удалить:**
```html
<div id="detailModal" class="detail-modal">
    <button class="close-btn" onclick="closeDetailModal()">×</button>
    <div id="modalContent" class="modal-content"></div>
</div>

<div id="philosopherDetailModal" class="detail-modal">
    <button class="close-btn" onclick="closePhilosopherDetailModal()">×</button>
    <div id="philosopherModalContent" class="modal-content"></div>
</div>
```

**А также удалить (строки 5200-5366):**
```html
<!-- Модальное окно редактирования философа -->
<div id="editPhilosopherModal" class="edit-modal">...</div>

<!-- Модальное окно редактирования концепции -->
<div id="editConceptModal" class="edit-modal">...</div>

<!-- Модальное окно редактирования связи -->
<div id="editConnectionModal" class="edit-modal">...</div>
```

**Заменить все на:**
```html
<!-- Универсальное модальное окно для всех сущностей и режимов -->
<div id="universalModal" class="detail-modal">
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    <div id="universalModalContent" class="modal-content"></div>
</div>
```

---

## Этап 2: Унификация CSS стилей

### 2.1. Обновить общие стили модального окна

**Место:** Строки 489-659 (блок `.detail-modal`)

**Изменить:**
```css
/* ============================================ */
/* УНИВЕРСАЛЬНАЯ МОДАЛЬНАЯ СИСТЕМА */
/* ============================================ */

.detail-modal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.92);
    color: white;
    padding: 25px 30px;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.7);
    max-width: 650px;
    max-height: 85vh;
    overflow-y: auto;
    z-index: 2000;
    border: 1px solid rgba(255,255,255,0.2);
    transition: all 0.3s ease;
}

.detail-modal.show {
    display: block;
    animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
    from {
        opacity: 0;
        transform: translate(-50%, -48%);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%);
    }
}

/* Режим редактирования - индикатор */
.detail-modal.edit-mode {
    border-color: #a29bfe;
    box-shadow: 0 10px 40px rgba(162, 155, 254, 0.4);
}

.detail-modal.edit-mode::before {
    content: '✏️ Режим редактирования';
    position: absolute;
    top: 15px;
    left: 25px;
    font-size: 11px;
    color: #a29bfe;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Заголовки в режиме редактирования сдвигаем вниз */
.detail-modal.edit-mode h2 {
    margin-top: 20px;
}

#modalOverlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 1999;
    transition: opacity 0.3s ease;
}

#modalOverlay.show {
    display: block;
}

.detail-modal h2 {
    margin: 0 0 8px 0;
    color: #a29bfe;
    font-size: 22px;
    font-weight: 600;
}

.detail-modal .philosopher-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    color: white;
    margin-bottom: 12px;
    opacity: 0.9;
    cursor: pointer;
    transition: opacity 0.2s;
}

.detail-modal .philosopher-tag:hover {
    opacity: 1;
}

.detail-modal .description {
    color: #e0e0e0;
    margin-bottom: 18px;
    line-height: 1.6;
    font-size: 13px;
}

.detail-modal .modal-close {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    transition: all 0.2s;
    z-index: 10;
}

.detail-modal .modal-close:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: rotate(90deg);
}

.detail-modal::-webkit-scrollbar {
    width: 6px;
}

.detail-modal::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

.detail-modal::-webkit-scrollbar-thumb {
    background: #a29bfe;
    border-radius: 10px;
}

.detail-modal::-webkit-scrollbar-thumb:hover {
    background: #8b7fe6;
}
```

### 2.2. Добавить стили для режима редактирования

**Место:** После общих стилей модального окна

```css
/* ============================================ */
/* СТИЛИ ДЛЯ РЕЖИМА РЕДАКТИРОВАНИЯ */
/* ============================================ */

/* Формы ввода */
.modal-form-group {
    margin-bottom: 20px;
}

.modal-form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #a29bfe;
    font-size: 14px;
}

.modal-form-group input[type="text"],
.modal-form-group input[type="number"],
.modal-form-group input[type="color"],
.modal-form-group select,
.modal-form-group textarea {
    width: 100%;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    font-size: 14px;
    color: #e0e0e0;
    box-sizing: border-box;
    transition: all 0.3s;
    font-family: inherit;
}

.modal-form-group input:focus,
.modal-form-group select:focus,
.modal-form-group textarea:focus {
    outline: none;
    border-color: #a29bfe;
    background: rgba(255, 255, 255, 0.12);
}

.modal-form-group textarea {
    min-height: 80px;
    resize: vertical;
}

.modal-form-group input::placeholder,
.modal-form-group textarea::placeholder {
    color: rgba(224, 224, 224, 0.5);
}

/* Чекбоксы */
.modal-form-checkbox {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.modal-form-checkbox input[type="checkbox"] {
    margin-right: 10px;
    width: 18px;
    height: 18px;
    cursor: pointer;
}

.modal-form-checkbox label {
    color: #e0e0e0;
    cursor: pointer;
    user-select: none;
}

/* Инлайн формы (например, год рождения/смерти) */
.modal-form-inline {
    display: flex;
    gap: 15px;
}

.modal-form-inline > div {
    flex: 1;
}

/* Кнопки действий */
.modal-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-btn {
    flex: 1;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.modal-btn-primary {
    background: #a29bfe;
    color: white;
}

.modal-btn-primary:hover {
    background: #8b7fe6;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(162, 155, 254, 0.4);
}

.modal-btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #e0e0e0;
}

.modal-btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
}

.modal-btn-danger {
    background: #e74c3c;
    color: white;
}

.modal-btn-danger:hover {
    background: #c0392b;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
}

/* Кнопка переключения режима (просмотр <-> редактирование) */
.mode-switch-btn {
    position: absolute;
    top: 12px;
    right: 50px;
    padding: 6px 12px;
    background: rgba(162, 155, 254, 0.2);
    border: 1px solid #a29bfe;
    border-radius: 6px;
    color: #a29bfe;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    z-index: 10;
}

.mode-switch-btn:hover {
    background: rgba(162, 155, 254, 0.3);
    transform: translateY(-2px);
}

/* Списки в режиме редактирования */
.modal-edit-list {
    margin-top: 20px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-edit-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.modal-edit-list-title {
    font-weight: 700;
    color: #a29bfe;
    font-size: 14px;
}

.modal-edit-list-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    margin: 8px 0;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-edit-list-item-content {
    flex: 1;
    font-size: 13px;
    color: #e0e0e0;
}

.modal-edit-list-btn {
    padding: 6px 12px;
    background: rgba(231, 76, 60, 0.2);
    border: 1px solid #e74c3c;
    border-radius: 5px;
    color: #e74c3c;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.modal-edit-list-btn:hover {
    background: #e74c3c;
    color: white;
}

.modal-edit-list-btn-add {
    width: 100%;
    padding: 10px;
    background: rgba(46, 204, 113, 0.2);
    border: 1px solid #2ecc71;
    border-radius: 6px;
    color: #2ecc71;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 10px;
}

.modal-edit-list-btn-add:hover {
    background: #2ecc71;
    color: white;
}

/* Поиск концепций в режиме редактирования связей */
.modal-concept-search {
    position: relative;
    margin: 10px 0;
}

.modal-concept-search input {
    width: 100%;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    color: #e0e0e0;
    font-size: 13px;
}

.modal-concept-search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 200px;
    overflow-y: auto;
    background: rgba(42, 42, 62, 0.98);
    border: 2px solid #a29bfe;
    border-radius: 8px;
    margin-top: 5px;
    z-index: 1000;
    display: none;
}

.modal-concept-search-results.show {
    display: block;
}

.modal-concept-search-item {
    padding: 10px;
    cursor: pointer;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 10px;
}

.modal-concept-search-item:hover {
    background: rgba(162, 155, 254, 0.2);
}

/* Секция заголовков */
.modal-section-title {
    font-size: 15px;
    font-weight: 700;
    color: #a29bfe;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(162, 155, 254, 0.3);
    display: flex;
    align-items: center;
    gap: 8px;
}
```

---

## Этап 3: Создание универсальной системы управления модальным окном

**Место:** После строки 4070 (где были функции closeDetailModal и т.д.)

**Удалить все старые функции:**
- `showDetailModal`
- `closeDetailModal`
- `showPhilosopherDetailModal`
- `closePhilosopherDetailModal`
- Все функции `openEdit...Modal`, `closeEdit...Modal`

**Добавить новую систему:**

```javascript
// ============================================
// УНИВЕРСАЛЬНАЯ СИСТЕМА МОДАЛЬНЫХ ОКОН
// ============================================

/**
 * Глобальный контекст модального окна
 */
const ModalContext = {
    currentEntity: null,      // 'philosopher', 'concept', 'connection'
    currentMode: 'view',      // 'view' или 'edit'
    currentData: null,        // данные текущей сущности
    editState: {}             // состояние редактирования (для форм)
};

/**
 * Главная функция открытия универсального модального окна
 * @param {string} entityType - тип сущности: 'philosopher', 'concept', 'connection'
 * @param {object} data - данные сущности
 * @param {string} mode - режим: 'view' или 'edit'
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
    
    // Добавляем кнопку переключения режима (если не создание новой сущности)
    if (data && data.id) {
        html = `
            <button class="mode-switch-btn" onclick="toggleModalMode()">
                ${mode === 'view' ? '✏️ Редактировать' : '👁️ Просмотр'}
            </button>
        ` + html;
    }
    
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
}

/**
 * Закрытие универсального модального окна
 */
function closeUniversalModal() {
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    
    content.innerHTML = '';
    modal.classList.remove('show', 'edit-mode');
    overlay.classList.remove('show');
    
    // Очищаем контекст
    ModalContext.currentEntity = null;
    ModalContext.currentMode = 'view';
    ModalContext.currentData = null;
    ModalContext.editState = {};
    
    unfreezeSimulation();
}

/**
 * Переключение между режимами просмотра и редактирования
 */
function toggleModalMode() {
    const newMode = ModalContext.currentMode === 'view' ? 'edit' : 'view';
    
    // Если переходим из режима редактирования в просмотр, спросим о несохраненных изменениях
    if (ModalContext.currentMode === 'edit' && hasUnsavedChanges()) {
        if (!confirm('У вас есть несохраненные изменения. Отменить их?')) {
            return;
        }
    }
    
    // Перезагружаем окно в новом режиме
    openUniversalModal(
        ModalContext.currentEntity,
        ModalContext.currentData,
        newMode
    );
}

/**
 * Проверка наличия несохраненных изменений
 */
function hasUnsavedChanges() {
    // TODO: реализовать проверку изменений в формах
    return false;
}

// ============================================
// ГЕНЕРАТОРЫ КОНТЕНТА ДЛЯ РЕЖИМА ПРОСМОТРА
// ============================================

/**
 * Генерация контента для просмотра философа
 */
function generatePhilosopherViewContent(philosopherName) {
    const philosopherData = philosophers.find(p => p.nameRu === philosopherName);
    if (!philosopherData) return '<p>Философ не найден</p>';
    
    const philColor = philosopherConcepts[philosopherName].color;
    const formattedDescription = philosopherData.description.replace(/\n\n/g, '<br><br>');
    
    let html = `
        <h2>${philosopherName}</h2>
        <div class="philosopher-tag" style="background: ${philColor}">
            ${philosopherData.years}
        </div>
        <div class="description">${formattedDescription}</div>
    `;
    
    // Добавляем все секции из предыдущей версии:
    // - Взаимодействие с другими философами
    // - Направления работы
    // - Концепции философа
    // - Связи концепций
    
    // (Весь код из предыдущей функции showPhilosopherDetailModal)
    
    return html;
}

/**
 * Генерация контента для просмотра концепции
 */
function generateConceptViewContent(conceptData) {
    const philColor = philosopherConcepts[conceptData.concept].color;
    
    let html = `
        <h2>${conceptData.label}</h2>
        <div class="philosopher-tag" style="background: ${philColor}; cursor: pointer;" 
             onclick="openUniversalModal('philosopher', '${conceptData.concept}', 'view');"
             title="Кликните для просмотра информации о философе">
            ${conceptData.concept}
        </div>
        <div class="description">${conceptData.extendedDescription}</div>
        <button class="toggle-all-descriptions-btn" onclick="gotoNodeFromModal('${conceptData.id}')">
            🎯 Перейти к узлу
        </button>
    `;
    
    // Добавляем секции связей, рубрик и т.д.
    // (Весь код из предыдущей функции showDetailModal)
    
    return html;
}

/**
 * Генерация контента для просмотра связи
 */
function generateConnectionViewContent(connectionData) {
    // TODO: реализовать просмотр связи
    return '<p>Просмотр связи</p>';
}

// ============================================
// ГЕНЕРАТОРЫ КОНТЕНТА ДЛЯ РЕЖИМА РЕДАКТИРОВАНИЯ
// ============================================

/**
 * Генерация контента для редактирования философа
 */
function generatePhilosopherEditContent(philosopherName) {
    const philosopherData = philosopherName 
        ? philosophers.find(p => p.nameRu === philosopherName)
        : null;
    
    const isNew = !philosopherData;
    const philColor = philosopherData ? philosopherConcepts[philosopherName].color : '#8E44AD';
    
    let html = `
        <h2>${isNew ? 'Создать философа' : 'Редактировать философа'}</h2>
        
        <div class="modal-form-group">
            <label for="philName">Имя философа *</label>
            <input type="text" id="philName" 
                   value="${philosopherData?.nameRu || ''}" 
                   placeholder="Например: Иммануил Кант">
        </div>
        
        <div class="modal-form-group">
            <label for="philColor">Цвет *</label>
            <input type="color" id="philColor" value="${philColor}">
        </div>
        
        <div class="modal-form-inline">
            <div class="modal-form-group">
                <label for="philBirth">Год рождения</label>
                <input type="number" id="philBirth" 
                       value="${philosopherData?.birth || ''}" 
                       placeholder="1724">
            </div>
            <div class="modal-form-group">
                <label for="philDeath">Год смерти</label>
                <input type="number" id="philDeath" 
                       value="${philosopherData?.death || ''}" 
                       placeholder="1804">
            </div>
        </div>
        
        <div class="modal-form-group">
            <label for="philDescription">Описание</label>
            <textarea id="philDescription" 
                      placeholder="Подробное описание философа..."
                      rows="10">${philosopherData?.description || ''}</textarea>
        </div>
    `;
    
    // Если редактируем существующего философа, показываем его концепции
    if (philosopherData) {
        const philosopherConceptsNodes = nodes.filter(n => n.concept === philosopherName);
        
        html += `
            <div class="modal-section-title">
                💡 Концепции философа (${philosopherConceptsNodes.length})
            </div>
            <div class="modal-edit-list">
        `;
        
        philosopherConceptsNodes.forEach(c => {
            html += `
                <div class="modal-edit-list-item">
                    <div class="modal-edit-list-item-content">
                        <strong>${c.label}</strong> - ${c.description}
                    </div>
                    <button class="modal-btn-secondary" style="flex: none; padding: 6px 12px;"
                            onclick="openUniversalModal('concept', nodes.find(n => n.id === '${c.id}'), 'view')">
                        👁️ Просмотр
                    </button>
                    <button class="modal-btn-secondary" style="flex: none; padding: 6px 12px;"
                            onclick="openUniversalModal('concept', nodes.find(n => n.id === '${c.id}'), 'edit')">
                        ✏️ Изменить
                    </button>
                </div>
            `;
        });
        
        html += `
                <button class="modal-edit-list-btn-add" onclick="createNewConceptForPhilosopher('${philosopherName}')">
                    + Добавить концепцию
                </button>
            </div>
        `;
    }
    
    // Кнопки действий
    html += `
        <div class="modal-actions">
            <button class="modal-btn modal-btn-primary" onclick="savePhilosopherData()">
                💾 Сохранить
            </button>
            <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
                ✖️ Отмена
            </button>
            ${!isNew ? `
                <button class="modal-btn modal-btn-danger" onclick="deletePhilosopher('${philosopherName}')">
                    🗑️ Удалить
                </button>
            ` : ''}
        </div>
    `;
    
    return html;
}

/**
 * Генерация контента для редактирования концепции
 */
function generateConceptEditContent(conceptData) {
    const isNew = !conceptData || !conceptData.id;
    
    let html = `
        <h2>${isNew ? 'Создать концепцию' : 'Редактировать концепцию'}</h2>
        
        <div class="modal-form-group">
            <label for="conceptLabel">Название концепции *</label>
            <input type="text" id="conceptLabel" 
                   value="${conceptData?.label || ''}" 
                   placeholder="Например: Категорический императив">
        </div>
        
        <div class="modal-form-group">
            <label for="conceptPhilosopher">Философ *</label>
            <select id="conceptPhilosopher">
                <option value="">Выберите философа</option>
                ${Object.keys(philosopherConcepts).map(phil => `
                    <option value="${phil}" ${conceptData?.concept === phil ? 'selected' : ''}>
                        ${phil}
                    </option>
                `).join('')}
            </select>
        </div>
        
        <div class="modal-form-group">
            <label for="conceptRubric">Рубрика</label>
            <select id="conceptRubric" multiple size="5">
                ${rubrics.map(rubric => {
                    const isSelected = conceptData && 
                        (conceptToRubrics[conceptData.id] || []).includes(rubric.id);
                    return `
                        <option value="${rubric.id}" ${isSelected ? 'selected' : ''}>
                            ${rubric.name}
                        </option>
                    `;
                }).join('')}
            </select>
        </div>
        
        <div class="modal-form-group">
            <label for="conceptDescription">Краткое описание</label>
            <textarea id="conceptDescription" 
                      placeholder="Краткое описание концепции"
                      rows="2">${conceptData?.description || ''}</textarea>
        </div>
        
        <div class="modal-form-group">
            <label for="conceptExtendedDescription">Расширенное описание</label>
            <textarea id="conceptExtendedDescription" 
                      placeholder="Подробное описание концепции"
                      rows="6">${conceptData?.extendedDescription || ''}</textarea>
        </div>
    `;
    
    // Если редактируем существующую концепцию, показываем её связи
    if (conceptData && conceptData.id) {
        const conceptConnections = links.filter(l => {
            const srcId = l.source.id || l.source;
            const tgtId = l.target.id || l.target;
            return srcId === conceptData.id || tgtId === conceptData.id;
        });
        
        html += `
            <div class="modal-section-title">
                🔗 Связи концепции (${conceptConnections.length})
            </div>
            
            <div class="connections-section">
        `;
        
        // Разделяем на внутренние и внешние связи, как в режиме просмотра
        const internalConnections = [];
        const externalConnections = [];
        
        conceptConnections.forEach(conn => {
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            const srcNode = nodes.find(n => n.id === srcId);
            const tgtNode = nodes.find(n => n.id === tgtId);
            
            if (!srcNode || !tgtNode) return;
            
            const isSource = srcId === conceptData.id;
            const connectedNode = isSource ? tgtNode : srcNode;
            
            if (connectedNode.concept === conceptData.concept) {
                internalConnections.push({ conn, connectedNode, isSource });
            } else {
                externalConnections.push({ conn, connectedNode, isSource });
            }
        });
        
        // ВНУТРЕННИЕ СВЯЗИ
        if (internalConnections.length > 0) {
            html += `
                <div class="connections-subsection">
                    <div class="subsection-header" onclick="toggleSubsection('edit-internal-${conceptData.id}')">
                        <div class="subsection-title">
                            🔗 Связи внутри системы ${conceptData.concept}
                            <span style="font-weight: 400; font-size: 11px;">(${internalConnections.length})</span>
                        </div>
                        <span class="subsection-toggle" id="toggle-edit-internal-${conceptData.id}">▼</span>
                    </div>
                    <div class="subsection-content" id="content-edit-internal-${conceptData.id}">
            `;
            
            internalConnections.forEach(({ conn, connectedNode, isSource }) => {
                const linkColor = relationTypesObj[conn.type].color;
                const linkLabel = relationTypesObj[conn.type].label;
                const arrow = conn.bidirectional ? '↔' : (isSource ? '→' : '←');
                
                html += `
                    <div class="connection-item">
                        <div class="concept-color" style="background: ${philosopherConcepts[connectedNode.concept].color}"></div>
                        <div class="connection-arrow" style="color: ${linkColor};">
                            ${arrow}
                            <span class="connection-arrow-tooltip">${linkLabel}</span>
                        </div>
                        <div style="flex-grow: 1;">
                            <div class="concept-name">${connectedNode.label}</div>
                        </div>
                        <button class="modal-btn-secondary" style="flex: none; padding: 6px 12px;"
                                onclick="openUniversalModal('connection', ${JSON.stringify(conn)}, 'edit')">
                            ✏️
                        </button>
                        <button class="modal-edit-list-btn" style="flex: none;"
                                onclick="deleteConnection('${conn.source.id || conn.source}', '${conn.target.id || conn.target}')">
                            🗑️
                        </button>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        // ВНЕШНИЕ СВЯЗИ
        if (externalConnections.length > 0) {
            html += `
                <div class="connections-subsection">
                    <div class="subsection-header" onclick="toggleSubsection('edit-external-${conceptData.id}')">
                        <div class="subsection-title">
                            🌐 Связи с концепциями других философов
                            <span style="font-weight: 400; font-size: 11px;">(${externalConnections.length})</span>
                        </div>
                        <span class="subsection-toggle" id="toggle-edit-external-${conceptData.id}">▼</span>
                    </div>
                    <div class="subsection-content" id="content-edit-external-${conceptData.id}">
            `;
            
            externalConnections.forEach(({ conn, connectedNode, isSource }) => {
                const linkColor = relationTypesObj[conn.type].color;
                const linkLabel = relationTypesObj[conn.type].label;
                const arrow = conn.bidirectional ? '↔' : (isSource ? '→' : '←');
                
                html += `
                    <div class="connection-item">
                        <div class="concept-color" style="background: ${philosopherConcepts[connectedNode.concept].color}"></div>
                        <div class="connection-arrow" style="color: ${linkColor};">
                            ${arrow}
                            <span class="connection-arrow-tooltip">${linkLabel}</span>
                        </div>
                        <div style="flex-grow: 1;">
                            <div class="concept-name">${connectedNode.label}</div>
                            <div class="concept-philosopher">${connectedNode.concept}</div>
                        </div>
                        <button class="modal-btn-secondary" style="flex: none; padding: 6px 12px;"
                                onclick="openUniversalModal('connection', ${JSON.stringify(conn)}, 'edit')">
                            ✏️
                        </button>
                        <button class="modal-edit-list-btn" style="flex: none;"
                                onclick="deleteConnection('${conn.source.id || conn.source}', '${conn.target.id || conn.target}')">
                            🗑️
                        </button>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `
                <button class="modal-edit-list-btn-add" onclick="createNewConnectionForConcept('${conceptData.id}')">
                    + Добавить связь
                </button>
            </div>
        `;
    }
    
    // Кнопки действий
    html += `
        <div class="modal-actions">
            <button class="modal-btn modal-btn-primary" onclick="saveConceptData()">
                💾 Сохранить
            </button>
            <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
                ✖️ Отмена
            </button>
            ${!isNew ? `
                <button class="modal-btn modal-btn-danger" onclick="deleteConcept('${conceptData.id}')">
                    🗑️ Удалить
                </button>
            ` : ''}
        </div>
    `;
    
    return html;
}

/**
 * Генерация контента для редактирования связи
 */
function generateConnectionEditContent(connectionData) {
    const isNew = !connectionData || (!connectionData.source && !connectionData.target);
    
    let html = `
        <h2>${isNew ? 'Создать связь' : 'Редактировать связь'}</h2>
        
        <div class="modal-form-group">
            <label for="connType">Тип связи *</label>
            <select id="connType">
                <option value="">Выберите тип связи</option>
                ${Object.entries(relationTypesObj).map(([type, data]) => `
                    <option value="${type}" ${connectionData?.type === type ? 'selected' : ''}>
                        ${data.label}
                    </option>
                `).join('')}
            </select>
        </div>
        
        <div class="modal-form-group">
            <label for="connWeight">Вес связи *</label>
            <select id="connWeight">
                <option value="1" ${connectionData?.weight === 1 ? 'selected' : ''}>1 - Слабая</option>
                <option value="2" ${!connectionData || connectionData?.weight === 2 ? 'selected' : ''}>2 - Средняя</option>
                <option value="3" ${connectionData?.weight === 3 ? 'selected' : ''}>3 - Сильная</option>
            </select>
        </div>
        
        <div class="modal-form-checkbox">
            <input type="checkbox" id="connBidirectional" 
                   ${connectionData?.bidirectional ? 'checked' : ''}>
            <label for="connBidirectional">Двунаправленная связь</label>
        </div>
        
        <div class="modal-form-group">
            <label>Начальная концепция *</label>
            <div class="modal-concept-search">
                <input type="text" id="connSourceSearch" placeholder="Поиск концепции...">
                <div class="modal-concept-search-results" id="connSourceResults"></div>
            </div>
            <div id="connSourceSelected" style="margin-top: 10px; padding: 10px; background: rgba(162,155,254,0.1); border-radius: 6px; display: ${connectionData?.source ? 'block' : 'none'};">
                Выбрано: <strong id="connSourceLabel">${
                    connectionData ? (nodes.find(n => n.id === (connectionData.source.id || connectionData.source))?.label || '') : ''
                }</strong>
            </div>
        </div>
        
        <div style="text-align: center; margin: 15px 0;">
            <button class="modal-btn-secondary" style="padding: 8px 20px;" onclick="swapConnectionConcepts()">
                ⇅ Поменять местами
            </button>
        </div>
        
        <div class="modal-form-group">
            <label>Конечная концепция *</label>
            <div class="modal-concept-search">
                <input type="text" id="connTargetSearch" placeholder="Поиск концепции...">
                <div class="modal-concept-search-results" id="connTargetResults"></div>
            </div>
            <div id="connTargetSelected" style="margin-top: 10px; padding: 10px; background: rgba(162,155,254,0.1); border-radius: 6px; display: ${connectionData?.target ? 'block' : 'none'};">
                Выбрано: <strong id="connTargetLabel">${
                    connectionData ? (nodes.find(n => n.id === (connectionData.target.id || connectionData.target))?.label || '') : ''
                }</strong>
            </div>
        </div>
        
        <div class="modal-form-group">
            <label for="connDescription">Описание связи</label>
            <textarea id="connDescription" 
                      placeholder="Описание связи (необязательно)"
                      rows="3">${connectionData?.description || ''}</textarea>
        </div>
        
        <div class="modal-actions">
            <button class="modal-btn modal-btn-primary" onclick="saveConnectionData()">
                💾 Сохранить
            </button>
            <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
                ✖️ Отмена
            </button>
            ${!isNew ? `
                <button class="modal-btn modal-btn-danger" onclick="deleteConnection()">
                    🗑️ Удалить
                </button>
            ` : ''}
        </div>
    `;
    
    return html;
}

// ============================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================

/**
 * Создание новой концепции для философа
 */
function createNewConceptForPhilosopher(philosopherName) {
    const newConcept = {
        concept: philosopherName,
        label: '',
        description: '',
        extendedDescription: ''
    };
    
    openUniversalModal('concept', newConcept, 'edit');
}

/**
 * Создание новой связи для концепции
 */
function createNewConnectionForConcept(conceptId) {
    const connection = {
        source: conceptId,
        target: null,
        type: '',
        weight: 2,
        bidirectional: false,
        description: ''
    };
    
    openUniversalModal('connection', connection, 'edit');
}

// ============================================
// АДАПТЕРЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
// ============================================

// Эти функции нужны для обратной совместимости со старым кодом
function showDetailModal(conceptData) {
    openUniversalModal('concept', conceptData, 'view');
}

function showPhilosopherDetailModal(philosopherName) {
    openUniversalModal('philosopher', philosopherName, 'view');
}

function openEditPhilosopherModal(philosopherName = null) {
    openUniversalModal('philosopher', philosopherName, 'edit');
}

function openEditConceptModal(conceptData = null) {
    openUniversalModal('concept', conceptData, 'edit');
}

function openEditConnectionModal(connectionData = null) {
    openUniversalModal('connection', connectionData, 'edit');
}

function closeDetailModal() {
    closeUniversalModal();
}

function closePhilosopherDetailModal() {
    closeUniversalModal();
}
```

---

## Этап 4: Обновление вызовов модальных окон по всему коду

**Места изменений:**

1. **Двойной клик на философе в легенде** (функция `makeLegendsEditable`):
```javascript
item.addEventListener('dblclick', function(event) {
    event.preventDefault();
    event.stopPropagation();
    openUniversalModal('philosopher', philosopherName, 'view');
});
```

2. **Shift+клик на философе** (для редактирования):
```javascript
item.addEventListener('click', function(event) {
    if (event.shiftKey) {
        event.preventDefault();
        event.stopPropagation();
        openUniversalModal('philosopher', philosopherName, 'edit');
    }
});
```

3. **Двойной клик на узле графа**:
```javascript
function handleNodeClick(event, d) {
    // ... существующий код ...
    if (clickCount === 2) {
        openUniversalModal('concept', d, 'view');
    }
}
```

4. **Клик по тегу философа в окне концепции**:
```javascript
<div class="philosopher-tag" 
     onclick="openUniversalModal('philosopher', '${conceptData.concept}', 'view');">
```

5. **Обновить обработчики ESC и overlay**:
```javascript
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeUniversalModal();
        closePathDescriptionsModal();
    }
});

document.getElementById('modalOverlay').addEventListener('click', function() {
    closeUniversalModal();
    closePathDescriptionsModal();
});
```

---

## Этап 5: Реализация функций сохранения данных

```javascript
/**
 * Сохранение данных философа
 */
function savePhilosopherData() {
    const name = document.getElementById('philName').value;
    const color = document.getElementById('philColor').value;
    const birth = parseInt(document.getElementById('philBirth').value) || null;
    const death = parseInt(document.getElementById('philDeath').value) || null;
    const description = document.getElementById('philDescription').value;
    
    if (!name) {
        alert('Укажите имя философа');
        return;
    }
    
    // TODO: Реализовать сохранение в массив philosophers
    // и обновление philosopherConcepts
    
    console.log('Сохранение философа:', { name, color, birth, death, description });
    
    // Закрываем окно и переходим в режим просмотра
    openUniversalModal('philosopher', name, 'view');
}

/**
 * Сохранение данных концепции
 */
function saveConceptData() {
    const label = document.getElementById('conceptLabel').value;
    const philosopher = document.getElementById('conceptPhilosopher').value;
    const rubricSelect = document.getElementById('conceptRubric');
    const rubrics = Array.from(rubricSelect.selectedOptions).map(opt => opt.value);
    const description = document.getElementById('conceptDescription').value;
    const extendedDescription = document.getElementById('conceptExtendedDescription').value;
    
    if (!label || !philosopher) {
        alert('Укажите название концепции и философа');
        return;
    }
    
    // TODO: Реализовать сохранение в массив concepts и nodes
    
    console.log('Сохранение концепции:', { 
        label, philosopher, rubrics, description, extendedDescription 
    });
    
    // Закрываем окно
    closeUniversalModal();
    
    // TODO: Обновить граф
}

/**
 * Сохранение данных связи
 */
function saveConnectionData() {
    const type = document.getElementById('connType').value;
    const weight = parseInt(document.getElementById('connWeight').value);
    const bidirectional = document.getElementById('connBidirectional').checked;
    const description = document.getElementById('connDescription').value;
    
    // Получаем выбранные концепции из ModalContext.editState
    const source = ModalContext.editState.selectedSource;
    const target = ModalContext.editState.selectedTarget;
    
    if (!type || !source || !target) {
        alert('Укажите тип связи и обе концепции');
        return;
    }
    
    // TODO: Реализовать сохранение в массив connections и links
    
    console.log('Сохранение связи:', {
        source, target, type, weight, bidirectional, description
    });
    
    // Закрываем окно
    closeUniversalModal();
    
    // TODO: Обновить граф
}
```

---

## Преимущества унифицированной системы

✅ **Единообразие** - все модальные окна работают одинаково  
✅ **Меньше кода** - одна HTML структура вместо 5 разных окон  
✅ **Плавные переходы** - можно переключаться между режимами без закрытия окна  
✅ **Легче поддерживать** - изменения в одном месте  
✅ **Лучший UX** - пользователь видит одинаковую информацию в режимах view и edit  
✅ **Расширяемость** - легко добавить новые типы сущностей или режимы  

---

## Что нужно сделать дальше

1. **Реализовать полные генераторы контента** для всех сущностей и режимов
2. **Добавить валидацию** форм перед сохранением
3. **Реализовать функции сохранения** данных в массивы
4. **Добавить обработку изменений** в графе после сохранения
5. **Реализовать поиск концепций** в формах связей
6. **Добавить подтверждения** перед удалением
7. **Реализовать проверку несохраненных изменений**

---

## Примечания

- Код выше - это каркас архитектуры. Полная реализация всех генераторов контента будет объемной
- Можно постепенно мигрировать на новую систему, начиная с одного типа сущности
- Старые функции остаются как адаптеры для обратной совместимости
- Система легко расширяется для новых типов сущностей (например, "рубрика")
