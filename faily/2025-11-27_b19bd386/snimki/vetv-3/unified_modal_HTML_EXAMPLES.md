# ПРАКТИЧЕСКИЕ ПРИМЕРЫ HTML
# Готовые шаблоны для генераторов контента

---

## 📋 ОГЛАВЛЕНИЕ

1. [Базовая структура модального окна](#базовая-структура)
2. [Просмотр концепции](#просмотр-концепции)
3. [Редактирование концепции](#редактирование-концепции)
4. [Просмотр философа](#просмотр-философа)
5. [Редактирование философа](#редактирование-философа)
6. [Просмотр связи](#просмотр-связи)
7. [Редактирование связи](#редактирование-связи)

---

## <a name="базовая-структура"></a>1. БАЗОВАЯ СТРУКТУРА МОДАЛЬНОГО ОКНА

```html
<!-- Overlay -->
<div id="modalOverlay" class="show"></div>

<!-- Универсальное модальное окно -->
<div id="universalModal" class="detail-modal show">
    <!-- Кнопка переключения режимов -->
    <button class="mode-switch-btn" onclick="toggleModalMode()">
        <span id="modeIcon">✏️</span> 
        <span id="modeText">Редактировать</span>
    </button>
    
    <!-- Кнопка закрытия -->
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    
    <!-- Контент (генерируется динамически) -->
    <div id="universalModalContent" class="modal-content">
        <!-- Здесь будет контент в зависимости от режима -->
    </div>
</div>
```

---

## <a name="просмотр-концепции"></a>2. ПРОСМОТР КОНЦЕПЦИИ (view mode)

```html
<div id="universalModalContent" class="modal-content">
    <!-- Заголовок -->
    <h2>Категорический императив</h2>
    
    <!-- Тег философа -->
    <span class="philosopher-tag" 
          style="background-color: #e74c3c;"
          onclick="openUniversalModal('philosopher', 'Кант', 'view')">
        Кант
    </span>
    
    <!-- Краткое описание -->
    <div class="description">
        Фундаментальный принцип морали, согласно которому поступок является моральным, 
        если его можно превратить в универсальный закон.
    </div>
    
    <!-- Секция рубрик -->
    <div class="rubric-section">
        <div class="rubric-title">Этика</div>
        <div class="rubric-description">
            Философское учение о морали и нравственности
        </div>
        
        <div class="related-concepts">
            <div class="related-title">Другие концепции в этой рубрике:</div>
            
            <div class="concept-item" onclick="openUniversalModal('concept', conceptData, 'view')">
                <div class="concept-color" style="background-color: #3498db;"></div>
                <div class="concept-name">Утилитаризм</div>
                <div class="concept-philosopher">(Бентам)</div>
            </div>
            
            <div class="concept-item" onclick="openUniversalModal('concept', conceptData, 'view')">
                <div class="concept-color" style="background-color: #9b59b6;"></div>
                <div class="concept-name">Этика добродетели</div>
                <div class="concept-philosopher">(Аристотель)</div>
            </div>
        </div>
    </div>
    
    <!-- Секция связей -->
    <div class="connections-section">
        <div class="connections-title">Связи концепции</div>
        
        <!-- Кнопка раскрытия всех описаний -->
        <button class="toggle-all-descriptions-btn" onclick="toggleAllDescriptions()">
            Раскрыть все описания
        </button>
        
        <!-- Сворачиваемая секция: Внутренние связи -->
        <div class="collapsible-section">
            <div class="collapsible-header" onclick="toggleCollapse(this)">
                <span class="collapsible-header-title">Внутренние связи (2)</span>
                <span class="collapsible-toggle expanded">▼</span>
            </div>
            <div class="collapsible-content show">
                <!-- Связь 1 -->
                <div class="connection-item">
                    <div class="concept-color" style="background-color: #e74c3c;"></div>
                    <span class="concept-name">Категорический императив</span>
                    
                    <span class="connection-arrow">
                        ➔
                        <span class="connection-arrow-tooltip">влияет на</span>
                    </span>
                    
                    <div class="concept-color" style="background-color: #e74c3c;"></div>
                    <span class="concept-name">Моральный закон</span>
                    
                    <button class="connection-toggle" onclick="toggleConnectionDescription(this)">
                        ▼
                    </button>
                    
                    <div class="connection-description">
                        Категорический императив определяет форму морального закона, 
                        который должен быть универсальным и применимым ко всем.
                    </div>
                </div>
                
                <!-- Связь 2 -->
                <div class="connection-item">
                    <!-- Аналогично связи 1 -->
                </div>
            </div>
        </div>
        
        <!-- Сворачиваемая секция: Внешние связи -->
        <div class="collapsible-section">
            <div class="collapsible-header" onclick="toggleCollapse(this)">
                <span class="collapsible-header-title">Внешние связи (3)</span>
                <span class="collapsible-toggle">▼</span>
            </div>
            <div class="collapsible-content">
                <!-- Внешние связи -->
            </div>
        </div>
    </div>
    
    <!-- Поиск концепций на графе -->
    <div id="modalSearch">
        <div class="legend-search-header">
            <div class="legend-search-icon">🔍</div>
            <div class="legend-search-input-wrapper">
                <input type="text" 
                       class="legend-search-input" 
                       placeholder="Найти и перейти к концепции..."
                       oninput="handleModalSearch(this.value)">
                <span class="legend-search-clear" onclick="clearModalSearch()">✖</span>
            </div>
        </div>
        <div class="search-results">
            <!-- Результаты поиска -->
        </div>
    </div>
</div>
```

---

## <a name="редактирование-концепции"></a>3. РЕДАКТИРОВАНИЕ КОНЦЕПЦИИ (edit mode)

```html
<!-- Модальное окно с классом edit-mode -->
<div id="universalModal" class="detail-modal show edit-mode">
    <button class="mode-switch-btn" onclick="toggleModalMode()">
        <span id="modeIcon">👁️</span> 
        <span id="modeText">Просмотр</span>
    </button>
    <button class="modal-close" onclick="closeUniversalModal()">×</button>
    
    <div id="universalModalContent" class="modal-content">
        <h2>Редактирование концепции</h2>
        
        <!-- Основная информация -->
        <div class="modal-form-group">
            <label>Название концепции *</label>
            <input type="text" 
                   id="conceptName" 
                   value="Категорический императив"
                   placeholder="Введите название концепции...">
        </div>
        
        <div class="modal-form-group">
            <label>Философ *</label>
            <select id="conceptPhilosopher">
                <option value="Кант" selected>Кант</option>
                <option value="Гегель">Гегель</option>
                <option value="Ницше">Ницше</option>
            </select>
        </div>
        
        <div class="modal-form-group">
            <label>Рубрики</label>
            <div id="rubricsList">
                <div class="modal-form-checkbox">
                    <input type="checkbox" id="rubric_ethics" checked>
                    <label for="rubric_ethics">Этика</label>
                </div>
                <div class="modal-form-checkbox">
                    <input type="checkbox" id="rubric_epistemology">
                    <label for="rubric_epistemology">Эпистемология</label>
                </div>
            </div>
        </div>
        
        <div class="modal-form-group">
            <label>Краткое описание</label>
            <textarea id="conceptShortDesc" 
                      placeholder="Краткое описание концепции...">Фундаментальный принцип морали...</textarea>
        </div>
        
        <div class="modal-form-group">
            <label>Полное описание</label>
            <textarea id="conceptFullDesc" 
                      placeholder="Развёрнутое описание концепции...">Категорический императив - это...</textarea>
        </div>
        
        <!-- Секция редактирования связей -->
        <div class="modal-edit-section">
            <h4>Связи концепции</h4>
            
            <!-- Сворачиваемая секция: Внутренние связи -->
            <div class="collapsible-section">
                <div class="collapsible-header" onclick="toggleCollapse(this)">
                    <span class="collapsible-header-title">Внутренние связи (2)</span>
                    <span class="collapsible-toggle expanded">▼</span>
                </div>
                <div class="collapsible-content show">
                    <div class="modal-edit-list">
                        <!-- Связь 1 -->
                        <div class="modal-edit-list-item">
                            <div class="modal-edit-list-item-content" 
                                 onclick="openUniversalModal('connection', connectionData, 'edit')">
                                <div class="modal-edit-list-item-name">
                                    Категорический императив ➔ Моральный закон
                                </div>
                                <div class="modal-edit-list-item-desc">
                                    влияет на (вес: сильная)
                                </div>
                            </div>
                            <div class="modal-edit-list-item-actions">
                                <button class="modal-list-btn modal-list-btn-edit" 
                                        onclick="openUniversalModal('connection', connectionData, 'edit')">
                                    ✏️
                                </button>
                                <button class="modal-list-btn modal-list-btn-delete" 
                                        onclick="deleteConnection(connectionId)">
                                    🗑️
                                </button>
                            </div>
                        </div>
                        
                        <!-- Связь 2 -->
                        <div class="modal-edit-list-item">
                            <!-- Аналогично -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Сворачиваемая секция: Внешние связи -->
            <div class="collapsible-section">
                <div class="collapsible-header" onclick="toggleCollapse(this)">
                    <span class="collapsible-header-title">Внешние связи (3)</span>
                    <span class="collapsible-toggle">▼</span>
                </div>
                <div class="collapsible-content">
                    <!-- Внешние связи -->
                </div>
            </div>
            
            <!-- Кнопка добавления связи -->
            <button class="modal-list-btn-add" 
                    onclick="createNewConnectionForConcept(conceptId)">
                + Добавить связь
            </button>
        </div>
        
        <!-- Предупреждение -->
        <div class="modal-warning">
            <h4>⚠️ Внимание</h4>
            <p>Изменение названия концепции повлияет на все связанные элементы.</p>
        </div>
        
        <!-- Разделитель -->
        <div class="modal-divider"></div>
        
        <!-- Кнопки действий -->
        <div class="modal-actions">
            <button class="modal-btn modal-btn-primary" onclick="saveConceptData()">
                💾 Сохранить
            </button>
            <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
                ✖ Отмена
            </button>
            <button class="modal-btn modal-btn-danger" onclick="deleteConcept()">
                🗑️ Удалить концепцию
            </button>
        </div>
        
        <!-- Подсказка -->
        <div class="modal-hint">
            💡 Для сохранения нажмите Enter или кнопку "Сохранить"
        </div>
    </div>
</div>
```

---

## <a name="просмотр-философа"></a>4. ПРОСМОТР ФИЛОСОФА (view mode)

```html
<div id="universalModalContent" class="modal-content">
    <h2>Иммануил Кант</h2>
    
    <!-- Статусный значок -->
    <span class="modal-status-badge success">Активен</span>
    
    <!-- Цвет философа -->
    <div class="modal-form-group">
        <label>Цвет на графе:</label>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #e74c3c; 
                        box-shadow: 0 0 10px #e74c3c;"></div>
            <span style="color: #e74c3c; font-weight: 600;">#e74c3c</span>
        </div>
    </div>
    
    <!-- Описание -->
    <div class="description">
        Немецкий философ, основоположник критической философии. 
        Известен своими работами по эпистемологии, этике и эстетике.
    </div>
    
    <!-- Секция концепций -->
    <div class="connections-section">
        <div class="connections-title">Концепции философа (5)</div>
        
        <div class="concept-item" onclick="openUniversalModal('concept', conceptData, 'view')">
            <div class="concept-color" style="background-color: #e74c3c;"></div>
            <div class="concept-name">Категорический императив</div>
        </div>
        
        <div class="concept-item" onclick="openUniversalModal('concept', conceptData, 'view')">
            <div class="concept-color" style="background-color: #e74c3c;"></div>
            <div class="concept-name">Критика чистого разума</div>
        </div>
        
        <div class="concept-item" onclick="openUniversalModal('concept', conceptData, 'view')">
            <div class="concept-color" style="background-color: #e74c3c;"></div>
            <div class="concept-name">Априорное знание</div>
        </div>
        
        <button class="show-all-concepts-btn" onclick="showAllPhilosopherConcepts('Кант')">
            Показать все концепции на графе
        </button>
    </div>
    
    <!-- Секция взаимодействия с другими философами -->
    <div class="philosopher-interactions-section">
        <div class="philosopher-interactions-title">
            Взаимодействия с другими философами (3)
        </div>
        
        <div class="philosopher-interaction-item" 
             onclick="openUniversalModal('philosopher', 'Гегель', 'view')">
            <span class="philosopher-tag" style="background-color: #3498db;">Гегель</span>
            <span style="margin: 0 10px;">→</span>
            <span style="color: #e0e0e0;">развивает идеи</span>
        </div>
        
        <div class="philosopher-interaction-item" 
             onclick="openUniversalModal('philosopher', 'Юм', 'view')">
            <span class="philosopher-tag" style="background-color: #e67e22;">Юм</span>
            <span style="margin: 0 10px;">←</span>
            <span style="color: #e0e0e0;">критикует</span>
        </div>
        
        <div class="philosopher-interaction-item" 
             onclick="openUniversalModal('philosopher', 'Ницше', 'view')">
            <span class="philosopher-tag" style="background-color: #9b59b6;">Ницше</span>
            <span style="margin: 0 10px;">⟷</span>
            <span style="color: #e0e0e0;">полемизирует</span>
        </div>
    </div>
    
    <!-- Поиск концепций -->
    <div id="modalSearch">
        <!-- Аналогично поиску в концепции -->
    </div>
</div>
```

---

## <a name="редактирование-философа"></a>5. РЕДАКТИРОВАНИЕ ФИЛОСОФА (edit mode)

```html
<div id="universalModalContent" class="modal-content">
    <h2>Редактирование философа</h2>
    
    <!-- Основная информация -->
    <div class="modal-form-group">
        <label>Имя философа *</label>
        <input type="text" 
               id="philosopherName" 
               value="Иммануил Кант"
               placeholder="Введите имя философа...">
    </div>
    
    <div class="modal-form-group modal-form-inline">
        <div>
            <label>Цвет на графе</label>
            <input type="color" id="philosopherColor" value="#e74c3c">
        </div>
        <div>
            <label>Предпросмотр</label>
            <div style="width: 40px; height: 40px; border-radius: 50%; 
                        background-color: #e74c3c; box-shadow: 0 0 10px #e74c3c;"></div>
        </div>
    </div>
    
    <div class="modal-form-group">
        <label>Описание</label>
        <textarea id="philosopherDescription" 
                  placeholder="Описание философа...">Немецкий философ...</textarea>
    </div>
    
    <!-- Секция концепций -->
    <div class="modal-edit-section">
        <h4>Концепции философа (5)</h4>
        
        <div class="modal-edit-list">
            <div class="modal-edit-list-item">
                <div class="modal-edit-list-item-content" 
                     onclick="openUniversalModal('concept', conceptData, 'view')">
                    <div class="modal-edit-list-item-name">
                        Категорический императив
                    </div>
                    <div class="modal-edit-list-item-desc">
                        Рубрики: Этика
                    </div>
                </div>
                <div class="modal-edit-list-item-actions">
                    <button class="modal-list-btn modal-list-btn-edit" 
                            onclick="openUniversalModal('concept', conceptData, 'edit')">
                        ✏️
                    </button>
                    <button class="modal-list-btn modal-list-btn-delete" 
                            onclick="deleteConcept(conceptId)">
                        🗑️
                    </button>
                </div>
            </div>
            
            <!-- Остальные концепции -->
        </div>
        
        <button class="modal-list-btn-add" 
                onclick="createNewConceptForPhilosopher('Кант')">
            + Добавить концепцию
        </button>
    </div>
    
    <!-- Секция взаимодействий -->
    <div class="modal-edit-section">
        <h4>Взаимодействия с другими философами</h4>
        
        <div class="modal-edit-list">
            <div class="modal-edit-list-item">
                <div class="modal-edit-list-item-content">
                    <div class="modal-edit-list-item-name">
                        Кант → Гегель
                    </div>
                    <div class="modal-edit-list-item-desc">
                        развивает идеи
                    </div>
                </div>
                <div class="modal-edit-list-item-actions">
                    <button class="modal-list-btn modal-list-btn-edit">✏️</button>
                    <button class="modal-list-btn modal-list-btn-delete">🗑️</button>
                </div>
            </div>
        </div>
        
        <button class="modal-list-btn-add">
            + Добавить взаимодействие
        </button>
    </div>
    
    <!-- Кнопки действий -->
    <div class="modal-actions">
        <button class="modal-btn modal-btn-primary" onclick="savePhilosopherData()">
            💾 Сохранить
        </button>
        <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
            ✖ Отмена
        </button>
        <button class="modal-btn modal-btn-danger" onclick="deletePhilosopher()">
            🗑️ Удалить философа
        </button>
    </div>
</div>
```

---

## <a name="просмотр-связи"></a>6. ПРОСМОТР СВЯЗИ (view mode)

```html
<div id="universalModalContent" class="modal-content">
    <h2>Связь концепций</h2>
    
    <!-- Визуализация связи -->
    <div style="display: flex; align-items: center; justify-content: center; 
                padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px;
                margin-bottom: 20px;">
        <div style="text-align: center;">
            <div class="concept-color" 
                 style="background-color: #e74c3c; width: 20px; height: 20px; 
                        margin: 0 auto 5px;"></div>
            <div style="color: #e0e0e0; font-weight: 600;">
                Категорический императив
            </div>
            <div style="color: #b0b0b0; font-size: 11px;">
                (Кант)
            </div>
        </div>
        
        <div style="margin: 0 30px; font-size: 24px; color: #3498db;">
            ➔
        </div>
        
        <div style="text-align: center;">
            <div class="concept-color" 
                 style="background-color: #e74c3c; width: 20px; height: 20px; 
                        margin: 0 auto 5px;"></div>
            <div style="color: #e0e0e0; font-weight: 600;">
                Моральный закон
            </div>
            <div style="color: #b0b0b0; font-size: 11px;">
                (Кант)
            </div>
        </div>
    </div>
    
    <!-- Информация о связи -->
    <div class="modal-form-group">
        <label>Тип связи:</label>
        <div style="color: #e0e0e0;">влияет на</div>
    </div>
    
    <div class="modal-form-group">
        <label>Вес связи:</label>
        <span class="modal-status-badge success">Сильная</span>
    </div>
    
    <div class="modal-form-group">
        <label>Направление:</label>
        <div style="color: #e0e0e0;">Однонаправленная</div>
    </div>
    
    <!-- Описание связи -->
    <div class="description">
        Категорический императив определяет форму морального закона, 
        который должен быть универсальным и применимым ко всем разумным существам.
    </div>
    
    <!-- Кнопки навигации -->
    <div class="modal-actions">
        <button class="modal-btn modal-btn-primary" 
                onclick="openUniversalModal('concept', sourceData, 'view')">
            👁️ Просмотреть источник
        </button>
        <button class="modal-btn modal-btn-primary" 
                onclick="openUniversalModal('concept', targetData, 'view')">
            👁️ Просмотреть цель
        </button>
    </div>
</div>
```

---

## <a name="редактирование-связи"></a>7. РЕДАКТИРОВАНИЕ СВЯЗИ (edit mode)

```html
<div id="universalModalContent" class="modal-content">
    <h2>Редактирование связи</h2>
    
    <!-- Выбор концепций -->
    <div class="modal-form-group">
        <label>Исходная концепция *</label>
        <div class="modal-concept-search">
            <input type="text" 
                   class="modal-concept-search-input"
                   id="sourceConceptSearch"
                   value="Категорический императив"
                   placeholder="Поиск концепции..."
                   oninput="searchConcepts(this.value, 'source')">
            <div class="modal-concept-search-results" id="sourceSearchResults">
                <!-- Результаты поиска -->
            </div>
        </div>
    </div>
    
    <!-- Кнопка смены направления -->
    <div style="text-align: center; margin: 10px 0;">
        <button class="modal-btn modal-btn-secondary" 
                onclick="swapConnectionConcepts()"
                style="max-width: 200px;">
            ⇅ Поменять местами
        </button>
    </div>
    
    <div class="modal-form-group">
        <label>Целевая концепция *</label>
        <div class="modal-concept-search">
            <input type="text" 
                   class="modal-concept-search-input"
                   id="targetConceptSearch"
                   value="Моральный закон"
                   placeholder="Поиск концепции..."
                   oninput="searchConcepts(this.value, 'target')">
            <div class="modal-concept-search-results" id="targetSearchResults">
                <!-- Результаты поиска -->
            </div>
        </div>
    </div>
    
    <!-- Тип связи -->
    <div class="modal-form-group">
        <label>Тип связи *</label>
        <select id="connectionType">
            <option value="influences" selected>влияет на</option>
            <option value="contradicts">противоречит</option>
            <option value="develops">развивает</option>
            <option value="criticizes">критикует</option>
            <option value="supports">поддерживает</option>
            <option value="precedes">предшествует</option>
        </select>
    </div>
    
    <!-- Вес связи -->
    <div class="modal-form-group">
        <label>Вес связи</label>
        <select id="connectionWeight">
            <option value="weak">Слабая</option>
            <option value="medium">Средняя</option>
            <option value="strong" selected>Сильная</option>
        </select>
    </div>
    
    <!-- Направление -->
    <div class="modal-form-checkbox">
        <input type="checkbox" id="bidirectional">
        <label for="bidirectional">Двунаправленная связь</label>
    </div>
    
    <!-- Описание -->
    <div class="modal-form-group">
        <label>Описание связи</label>
        <textarea id="connectionDescription" 
                  placeholder="Опишите характер связи...">Категорический императив определяет форму морального закона...</textarea>
    </div>
    
    <!-- Подсказка -->
    <div class="modal-hint">
        💡 Двунаправленная связь создаёт взаимное влияние между концепциями
    </div>
    
    <!-- Кнопки действий -->
    <div class="modal-actions">
        <button class="modal-btn modal-btn-primary" onclick="saveConnectionData()">
            💾 Сохранить
        </button>
        <button class="modal-btn modal-btn-secondary" onclick="closeUniversalModal()">
            ✖ Отмена
        </button>
        <button class="modal-btn modal-btn-danger" onclick="deleteConnection()">
            🗑️ Удалить связь
        </button>
    </div>
</div>
```

---

## 🔧 ВСПОМОГАТЕЛЬНЫЕ JAVASCRIPT ФУНКЦИИ

```javascript
// Переключение режимов
function toggleModalMode() {
    const modal = document.getElementById('universalModal');
    const modeIcon = document.getElementById('modeIcon');
    const modeText = document.getElementById('modeText');
    const isEditMode = modal.classList.contains('edit-mode');
    
    if (isEditMode) {
        // Переход view ← edit
        modal.classList.remove('edit-mode');
        modeIcon.textContent = '✏️';
        modeText.textContent = 'Редактировать';
        regenerateModalContent(ModalContext.currentEntity, ModalContext.currentData, 'view');
    } else {
        // Переход view → edit
        modal.classList.add('edit-mode');
        modeIcon.textContent = '👁️';
        modeText.textContent = 'Просмотр';
        regenerateModalContent(ModalContext.currentEntity, ModalContext.currentData, 'edit');
    }
}

// Переключение сворачиваемых секций
function toggleCollapse(headerElement) {
    const toggle = headerElement.querySelector('.collapsible-toggle');
    const content = headerElement.nextElementSibling;
    
    toggle.classList.toggle('expanded');
    content.classList.toggle('show');
}

// Переключение описания связи
function toggleConnectionDescription(button) {
    const description = button.nextElementSibling;
    button.classList.toggle('expanded');
    description.classList.toggle('show');
}

// Раскрытие/скрытие всех описаний
function toggleAllDescriptions() {
    const descriptions = document.querySelectorAll('.connection-description');
    const button = event.target;
    const allExpanded = Array.from(descriptions).every(d => d.classList.contains('show'));
    
    descriptions.forEach(desc => {
        const toggle = desc.previousElementSibling;
        if (allExpanded) {
            desc.classList.remove('show');
            toggle.classList.remove('expanded');
        } else {
            desc.classList.add('show');
            toggle.classList.add('expanded');
        }
    });
    
    button.textContent = allExpanded ? 'Раскрыть все описания' : 'Свернуть все описания';
}

// Смена направления связи
function swapConnectionConcepts() {
    const sourceInput = document.getElementById('sourceConceptSearch');
    const targetInput = document.getElementById('targetConceptSearch');
    
    const temp = sourceInput.value;
    sourceInput.value = targetInput.value;
    targetInput.value = temp;
}
```

---

**Все примеры готовы к использованию! 🎉**

Эти HTML шаблоны можно использовать в генераторах контента:
- `generateConceptViewContent()`
- `generateConceptEditContent()`
- `generatePhilosopherViewContent()`
- `generatePhilosopherEditContent()`
- `generateConnectionViewContent()`
- `generateConnectionEditContent()`
