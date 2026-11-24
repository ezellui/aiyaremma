# Руководство по добавлению интерактивного редактирования графа философских концепций

## Оглавление
1. [CSS стили для модальных окон редактирования](#1-css-стили)
2. [HTML разметка модальных окон](#2-html-разметка)
3. [JavaScript функции редактирования](#3-javascript-функции)
4. [Интеграция с существующим кодом](#4-интеграция)

---

## 1. CSS стили

### Добавить в секцию `<style>` (после существующих стилей модальных окон, примерно после строки 800):

```css
/* ============================================
   СТИЛИ ДЛЯ РЕДАКТИРОВАНИЯ
   ============================================ */

/* Общие стили для модальных окон редактирования */
.edit-modal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    border-radius: 15px;
    box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
    z-index: 10001;
    max-width: 600px;
    width: 90%;
    max-height: 85vh;
    overflow-y: auto;
    padding: 0;
}

.edit-modal.show {
    display: block;
    animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translate(-50%, -48%);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%);
    }
}

.edit-modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 25px;
    border-radius: 15px 15px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.edit-modal-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

.edit-modal-close {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s;
}

.edit-modal-close:hover {
    background: rgba(255, 255, 255, 0.3);
}

.edit-modal-body {
    padding: 25px;
}

.edit-form-group {
    margin-bottom: 20px;
}

.edit-form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2d3436;
    font-size: 14px;
}

.edit-form-group input[type="text"],
.edit-form-group input[type="number"],
.edit-form-group textarea,
.edit-form-group select {
    width: 100%;
    padding: 10px 12px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.3s;
    box-sizing: border-box;
}

.edit-form-group input:focus,
.edit-form-group textarea:focus,
.edit-form-group select:focus {
    outline: none;
    border-color: #667eea;
}

.edit-form-group textarea {
    min-height: 80px;
    resize: vertical;
}

.edit-form-group input[type="color"] {
    width: 60px;
    height: 40px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    cursor: pointer;
}

.edit-form-group.inline {
    display: flex;
    gap: 15px;
}

.edit-form-group.inline > div {
    flex: 1;
}

.edit-form-checkbox {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}

.edit-form-checkbox input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: #667eea;
}

.edit-form-checkbox label {
    margin: 0;
    cursor: pointer;
    font-weight: 600;
}

/* Кнопки действий */
.edit-modal-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 2px solid #e1e8ed;
}

.edit-btn {
    flex: 1;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.edit-btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.edit-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.edit-btn-secondary {
    background: #95a5a6;
    color: white;
}

.edit-btn-secondary:hover {
    background: #7f8c8d;
}

.edit-btn-danger {
    background: #e74c3c;
    color: white;
}

.edit-btn-danger:hover {
    background: #c0392b;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
}

/* Секция списка элементов в модальном окне */
.edit-list-section {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.edit-list-section h4 {
    margin: 0 0 15px 0;
    font-size: 16px;
    color: #2d3436;
}

.edit-list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px;
    background: white;
    border-radius: 6px;
    margin-bottom: 8px;
    transition: background 0.2s;
}

.edit-list-item:hover {
    background: #e8f4f8;
}

.edit-list-item-content {
    flex: 1;
    cursor: pointer;
}

.edit-list-item-name {
    font-weight: 600;
    color: #2d3436;
    margin-bottom: 3px;
}

.edit-list-item-desc {
    font-size: 12px;
    color: #636e72;
}

.edit-list-item-actions {
    display: flex;
    gap: 8px;
}

.edit-list-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 5px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.edit-list-btn-edit {
    background: #3498db;
    color: white;
}

.edit-list-btn-edit:hover {
    background: #2980b9;
}

.edit-list-btn-delete {
    background: #e74c3c;
    color: white;
}

.edit-list-btn-delete:hover {
    background: #c0392b;
}

.edit-list-btn-add {
    width: 100%;
    padding: 10px;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.3s;
    margin-top: 10px;
}

.edit-list-btn-add:hover {
    background: #229954;
}

/* Поиск концепций */
.concept-search-container {
    position: relative;
    margin-bottom: 15px;
}

.concept-search-input {
    width: 100%;
    padding: 10px 12px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    font-size: 14px;
    box-sizing: border-box;
}

.concept-search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 200px;
    overflow-y: auto;
    background: white;
    border: 2px solid #667eea;
    border-radius: 8px;
    margin-top: 5px;
    z-index: 1000;
    display: none;
}

.concept-search-results.show {
    display: block;
}

.concept-search-item {
    padding: 10px;
    cursor: pointer;
    border-bottom: 1px solid #e1e8ed;
    display: flex;
    align-items: center;
    gap: 10px;
}

.concept-search-item:hover {
    background: #f0f3ff;
}

.concept-search-item:last-child {
    border-bottom: none;
}

.concept-search-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.concept-search-name {
    font-weight: 600;
    color: #2d3436;
}

.concept-search-philosopher {
    font-size: 12px;
    color: #636e72;
    margin-left: auto;
}

/* Режим выбора на графе */
.graph-selection-mode {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    z-index: 1000;
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.graph-selection-mode h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
}

.graph-selection-mode p {
    margin: 0;
    font-size: 13px;
    opacity: 0.9;
}

.graph-selection-cancel {
    margin-top: 10px;
    padding: 8px 15px;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.3s;
    width: 100%;
}

.graph-selection-cancel:hover {
    background: rgba(255, 255, 255, 0.3);
}

/* Стили для legend при редактировании */
.legend-item.editable {
    cursor: pointer;
}

.legend-item.editable:hover {
    background: #e8f4f8;
}

.philosopher-item-editable {
    cursor: pointer;
    transition: background 0.2s;
}

.philosopher-item-editable:hover {
    background: rgba(108, 92, 231, 0.1);
}

/* Предупреждающие сообщения */
.warning-message {
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}

.warning-message h4 {
    margin: 0 0 8px 0;
    color: #856404;
    font-size: 15px;
}

.warning-message p {
    margin: 0;
    color: #856404;
    font-size: 13px;
}

.warning-list {
    margin: 10px 0 0 20px;
    color: #856404;
}

/* Индикатор изменений */
.edit-mode-indicator {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #27ae60;
    color: white;
    padding: 12px 20px;
    border-radius: 25px;
    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.4);
    font-weight: 600;
    z-index: 999;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.4);
    }
    50% {
        box-shadow: 0 4px 25px rgba(39, 174, 96, 0.7);
    }
}
```

---

## 2. HTML разметка

### Добавить перед закрывающим тегом `</body>` (перед строкой 2315):

```html
<!-- ============================================
     МОДАЛЬНЫЕ ОКНА РЕДАКТИРОВАНИЯ
     ============================================ -->

<!-- Модальное окно редактирования философа -->
<div id="editPhilosopherModal" class="edit-modal">
    <div class="edit-modal-header">
        <h3 id="editPhilosopherTitle">Редактировать философа</h3>
        <button class="edit-modal-close" onclick="closeEditPhilosopherModal()">×</button>
    </div>
    <div class="edit-modal-body">
        <div class="edit-form-group">
            <label for="philosopherName">Имя философа *</label>
            <input type="text" id="philosopherName" placeholder="Например: Иммануил Кант">
        </div>
        
        <div class="edit-form-group">
            <label for="philosopherColor">Цвет *</label>
            <input type="color" id="philosopherColor">
        </div>
        
        <div class="edit-form-group inline">
            <div>
                <label for="philosopherBirthYear">Год рождения</label>
                <input type="number" id="philosopherBirthYear" placeholder="1724">
            </div>
            <div>
                <label for="philosopherDeathYear">Год смерти</label>
                <input type="number" id="philosopherDeathYear" placeholder="1804">
            </div>
        </div>
        
        <!-- Список концепций философа -->
        <div class="edit-list-section" id="philosopherConceptsList">
            <h4>Концепции философа (<span id="philosopherConceptsCount">0</span>)</h4>
            <div id="philosopherConceptsContainer"></div>
            <button class="edit-list-btn-add" onclick="addConceptFromPhilosopher()">+ Добавить концепцию</button>
        </div>
        
        <div class="edit-modal-actions">
            <button class="edit-btn edit-btn-primary" onclick="savePhilosopher()">Сохранить</button>
            <button class="edit-btn edit-btn-secondary" onclick="closeEditPhilosopherModal()">Отмена</button>
            <button class="edit-btn edit-btn-danger" id="deletePhilosopherBtn" onclick="deletePhilosopher()" style="display: none;">Удалить философа</button>
        </div>
    </div>
</div>

<!-- Модальное окно редактирования концепции -->
<div id="editConceptModal" class="edit-modal">
    <div class="edit-modal-header">
        <h3 id="editConceptTitle">Редактировать концепцию</h3>
        <button class="edit-modal-close" onclick="closeEditConceptModal()">×</button>
    </div>
    <div class="edit-modal-body">
        <div class="edit-form-group">
            <label for="conceptLabel">Название концепции *</label>
            <input type="text" id="conceptLabel" placeholder="Например: Категорический императив">
        </div>
        
        <div class="edit-form-group">
            <label for="conceptPhilosopher">Философ *</label>
            <select id="conceptPhilosopher">
                <option value="">Выберите философа</option>
            </select>
        </div>
        
        <div class="edit-form-group">
            <label for="conceptRubric">Рубрика</label>
            <select id="conceptRubric">
                <option value="">Выберите рубрику (необязательно)</option>
            </select>
        </div>
        
        <div class="edit-form-group">
            <label for="conceptDescription">Краткое описание</label>
            <textarea id="conceptDescription" placeholder="Краткое описание концепции"></textarea>
        </div>
        
        <div class="edit-form-group">
            <label for="conceptExtendedDescription">Расширенное описание</label>
            <textarea id="conceptExtendedDescription" placeholder="Подробное описание концепции"></textarea>
        </div>
        
        <!-- Список связей концепции -->
        <div class="edit-list-section" id="conceptConnectionsList">
            <h4>Связи концепции (<span id="conceptConnectionsCount">0</span>)</h4>
            <div id="conceptConnectionsContainer"></div>
            <button class="edit-list-btn-add" onclick="addConnectionFromConcept()">+ Добавить связь</button>
        </div>
        
        <div class="edit-modal-actions">
            <button class="edit-btn edit-btn-primary" onclick="saveConcept()">Сохранить</button>
            <button class="edit-btn edit-btn-secondary" onclick="closeEditConceptModal()">Отмена</button>
            <button class="edit-btn edit-btn-danger" id="deleteConceptBtn" onclick="deleteConcept()" style="display: none;">Удалить концепцию</button>
        </div>
    </div>
</div>

<!-- Модальное окно редактирования связи -->
<div id="editConnectionModal" class="edit-modal">
    <div class="edit-modal-header">
        <h3 id="editConnectionTitle">Редактировать связь</h3>
        <button class="edit-modal-close" onclick="closeEditConnectionModal()">×</button>
    </div>
    <div class="edit-modal-body">
        <div class="edit-form-group">
            <label for="connectionType">Тип связи *</label>
            <select id="connectionType">
                <option value="">Выберите тип связи</option>
            </select>
        </div>
        
        <div class="edit-form-group">
            <label for="connectionWeight">Вес связи *</label>
            <select id="connectionWeight">
                <option value="1">1 - Слабая</option>
                <option value="2" selected>2 - Средняя</option>
                <option value="3">3 - Сильная</option>
            </select>
        </div>
        
        <div class="edit-form-checkbox">
            <input type="checkbox" id="connectionBidirectional">
            <label for="connectionBidirectional">Двунаправленная связь</label>
        </div>
        
        <!-- Выбор начальной концепции -->
        <div class="edit-form-group">
            <label>Начальная концепция *</label>
            <div class="concept-search-container">
                <input type="text" id="connectionSourceSearch" class="concept-search-input" placeholder="Поиск концепции..." readonly>
                <div id="connectionSourceResults" class="concept-search-results"></div>
            </div>
            <button class="edit-btn edit-btn-secondary" onclick="selectConceptOnGraph('source')" style="margin-top: 10px; width: 100%;">
                Указать на графе
            </button>
        </div>
        
        <!-- Выбор конечной концепции -->
        <div class="edit-form-group">
            <label>Конечная концепция *</label>
            <div class="concept-search-container">
                <input type="text" id="connectionTargetSearch" class="concept-search-input" placeholder="Поиск концепции..." readonly>
                <div id="connectionTargetResults" class="concept-search-results"></div>
            </div>
            <button class="edit-btn edit-btn-secondary" onclick="selectConceptOnGraph('target')" style="margin-top: 10px; width: 100%;">
                Указать на графе
            </button>
        </div>
        
        <div class="edit-form-group">
            <label for="connectionDescription">Описание связи</label>
            <textarea id="connectionDescription" placeholder="Описание связи (необязательно)"></textarea>
        </div>
        
        <div class="edit-modal-actions">
            <button class="edit-btn edit-btn-primary" onclick="saveConnection()">Сохранить</button>
            <button class="edit-btn edit-btn-secondary" onclick="closeEditConnectionModal()">Отмена</button>
            <button class="edit-btn edit-btn-danger" id="deleteConnectionBtn" onclick="deleteConnection()" style="display: none;">Удалить связь</button>
        </div>
    </div>
</div>

<!-- Индикатор режима выбора на графе -->
<div id="graphSelectionMode" class="graph-selection-mode" style="display: none;">
    <h4 id="selectionModeTitle">Выберите концепцию</h4>
    <p id="selectionModeDesc">Кликните на концепцию в графе</p>
    <button class="graph-selection-cancel" onclick="cancelGraphSelection()">Отмена</button>
</div>
```

---

## 3. JavaScript функции

### Добавить в конец секции `<script>` (перед закрывающим тегом `</script>` на строке 2313):

```javascript
// ============================================
// СИСТЕМА РЕДАКТИРОВАНИЯ ГРАФА
// ============================================

// Глобальные переменные для редактирования
let editMode = {
    active: false,
    type: null, // 'philosopher', 'concept', 'connection'
    data: null,
    isNew: false,
    graphSelectionMode: false,
    graphSelectionTarget: null, // 'source' or 'target' for connections
    connectionSourceId: null,
    connectionTargetId: null,
    pendingConceptSelection: [] // Для последовательного выбора двух концепций
};

// ============================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================

// Генерация уникального ID
function generateId(prefix = 'id') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Поиск философа по имени
function findPhilosopherByName(name) {
    return Object.values(philosopherConcepts).find(p => p.name === name);
}

// Поиск концепции по ID
function findConceptById(conceptId) {
    return nodes.find(n => n.id === conceptId);
}

// Поиск связи между концепциями
function findConnection(sourceId, targetId) {
    return connections.find(c => 
        (c.from === sourceId && c.to === targetId) ||
        (c.bidirectional && c.from === targetId && c.to === sourceId)
    );
}

// Получение всех связей концепции
function getConceptConnections(conceptId) {
    return connections.filter(c => c.from === conceptId || c.to === conceptId);
}

// Проверка изолированности концепции
function isConceptIsolated(conceptId) {
    return getConceptConnections(conceptId).length === 0;
}

// Получение изолированных концепций после удаления связей
function getIsolatedConceptsAfterDeletion(connectionsToDelete) {
    const affectedConcepts = new Set();
    connectionsToDelete.forEach(conn => {
        affectedConcepts.add(conn.from);
        affectedConcepts.add(conn.to);
    });
    
    const isolated = [];
    affectedConcepts.forEach(conceptId => {
        const remainingConnections = connections.filter(c => 
            !connectionsToDelete.includes(c) && 
            (c.from === conceptId || c.to === conceptId)
        );
        if (remainingConnections.length === 0) {
            const concept = findConceptById(conceptId);
            if (concept) isolated.push(concept);
        }
    });
    
    return isolated;
}

// Обновление графа без полной перезагрузки
function updateGraphData() {
    // Пересоздаем массив links из connections
    links = connections.map(conn => ({
        source: conn.from,
        target: conn.to,
        type: conn.type,
        weight: conn.weight || 2,
        bidirectional: conn.bidirectional || false
    }));
    
    // Перезапускаем симуляцию с новыми данными
    simulation.nodes(nodes);
    simulation.force("link").links(links);
    
    // Обновляем визуальные элементы
    updateGraphVisualization();
    
    // Перезапускаем симуляцию
    simulation.alpha(0.3).restart();
}

// Обновление визуализации графа
function updateGraphVisualization() {
    // Обновляем связи
    link = link.data(links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
    link.exit().remove();
    
    const linkEnter = link.enter()
        .append("path")
        .attr("class", d => {
            let classes = "link";
            classes += ` weight-${d.weight === 1 ? 'weak' : d.weight === 3 ? 'strong' : 'medium'}`;
            if (d.bidirectional) classes += " bidirectional";
            return classes;
        })
        .attr("stroke", d => relationTypesObj[d.type].color)
        .attr("marker-end", d => !d.bidirectional ? `url(#arrow-${d.type})` : "")
        .on("click", function(event, d) {
            if (event.shiftKey) {
                event.stopPropagation();
                openEditConnectionModal(d.source.id || d.source, d.target.id || d.target);
            } else {
                handleLinkClick(event, d);
            }
        });
    
    link = linkEnter.merge(link);
    
    // Обновляем узлы
    node = node.data(nodes, d => d.id);
    node.exit().remove();
    
    const nodeEnter = node.enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("click", handleNodeClick)
        .on("contextmenu", function(event, d) {
            event.preventDefault();
            showDetailModal(d);
        });
    
    nodeEnter.append("circle")
        .attr("r", 12)
        .attr("fill", d => philosopherConcepts[d.concept].color)
        .attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));
    
    nodeEnter.append("text")
        .attr("dy", 20)
        .attr("text-anchor", "middle")
        .text(d => d.label);
    
    node = nodeEnter.merge(node);
    
    // Обновляем цвета существующих узлов (на случай изменения философа)
    node.select("circle")
        .attr("fill", d => philosopherConcepts[d.concept].color)
        .attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));
    
    node.select("text")
        .text(d => d.label);
}

// ============================================
// РЕДАКТИРОВАНИЕ ФИЛОСОФА
// ============================================

function openEditPhilosopherModal(philosopherName = null) {
    const modal = document.getElementById('editPhilosopherModal');
    const overlay = document.getElementById('modalOverlay');
    const title = document.getElementById('editPhilosopherTitle');
    const deleteBtn = document.getElementById('deletePhilosopherBtn');
    
    editMode.active = true;
    editMode.type = 'philosopher';
    editMode.isNew = !philosopherName;
    editMode.data = philosopherName ? findPhilosopherByName(philosopherName) : null;
    
    if (editMode.isNew) {
        title.textContent = 'Добавить философа';
        document.getElementById('philosopherName').value = '';
        document.getElementById('philosopherColor').value = '#' + Math.floor(Math.random()*16777215).toString(16);
        document.getElementById('philosopherBirthYear').value = '';
        document.getElementById('philosopherDeathYear').value = '';
        deleteBtn.style.display = 'none';
    } else {
        title.textContent = 'Редактировать философа';
        const philosopher = editMode.data;
        document.getElementById('philosopherName').value = philosopher.name;
        document.getElementById('philosopherColor').value = philosopher.color;
        document.getElementById('philosopherBirthYear').value = philosopher.birth || '';
        document.getElementById('philosopherDeathYear').value = philosopher.death || '';
        deleteBtn.style.display = 'block';
        
        // Загружаем список концепций
        loadPhilosopherConcepts(philosopher.name);
    }
    
    modal.classList.add('show');
    overlay.classList.add('show');
}

function loadPhilosopherConcepts(philosopherName) {
    const concepts = nodes.filter(n => n.concept === philosopherName);
    const container = document.getElementById('philosopherConceptsContainer');
    const count = document.getElementById('philosopherConceptsCount');
    
    count.textContent = concepts.length;
    
    if (concepts.length === 0) {
        container.innerHTML = '<p style="color: #95a5a6; font-size: 13px; margin: 10px 0;">Нет концепций</p>';
        return;
    }
    
    container.innerHTML = concepts.map(concept => `
        <div class="edit-list-item">
            <div class="edit-list-item-content" onclick="openEditConceptModal('${concept.id}')">
                <div class="edit-list-item-name">${concept.label}</div>
                <div class="edit-list-item-desc">${concept.description || 'Без описания'}</div>
            </div>
            <div class="edit-list-item-actions">
                <button class="edit-list-btn edit-list-btn-edit" onclick="event.stopPropagation(); openEditConceptModal('${concept.id}')">Изменить</button>
                <button class="edit-list-btn edit-list-btn-delete" onclick="event.stopPropagation(); deleteConceptFromList('${concept.id}')">Удалить</button>
            </div>
        </div>
    `).join('');
}

function savePhilosopher() {
    const name = document.getElementById('philosopherName').value.trim();
    const color = document.getElementById('philosopherColor').value;
    const birth = document.getElementById('philosopherBirthYear').value;
    const death = document.getElementById('philosopherDeathYear').value;
    
    if (!name) {
        alert('Пожалуйста, введите имя философа');
        return;
    }
    
    if (editMode.isNew) {
        // Проверяем, не существует ли уже философ с таким именем
        if (findPhilosopherByName(name)) {
            alert('Философ с таким именем уже существует');
            return;
        }
        
        // Добавляем нового философа
        philosopherConcepts[name] = {
            name: name,
            color: color,
            birth: birth || null,
            death: death || null
        };
    } else {
        // Обновляем существующего философа
        const oldName = editMode.data.name;
        
        if (name !== oldName && findPhilosopherByName(name)) {
            alert('Философ с таким именем уже существует');
            return;
        }
        
        // Обновляем данные философа
        if (name !== oldName) {
            // Если имя изменилось, обновляем все концепции
            nodes.forEach(node => {
                if (node.concept === oldName) {
                    node.concept = name;
                }
            });
            
            // Удаляем старую запись и создаем новую
            delete philosopherConcepts[oldName];
            philosopherConcepts[name] = {
                name: name,
                color: color,
                birth: birth || null,
                death: death || null
            };
        } else {
            // Просто обновляем свойства
            philosopherConcepts[name].color = color;
            philosopherConcepts[name].birth = birth || null;
            philosopherConcepts[name].death = death || null;
        }
    }
    
    // Обновляем граф и легенду
    updateGraphData();
    initFilters();
    
    closeEditPhilosopherModal();
}

function deletePhilosopher() {
    const philosopherName = editMode.data.name;
    const concepts = nodes.filter(n => n.concept === philosopherName);
    
    if (concepts.length > 0) {
        const confirmMsg = `Вы уверены, что хотите удалить философа "${philosopherName}"?\n\n` +
                          `Это удалит ${concepts.length} концепци(й/ю/ий) и все связанные с ними связи.\n\n` +
                          `Концепции: ${concepts.map(c => c.label).join(', ')}`;
        
        if (!confirm(confirmMsg)) return;
        
        // Удаляем все концепции философа
        concepts.forEach(concept => {
            const conceptConnections = getConceptConnections(concept.id);
            conceptConnections.forEach(conn => {
                const index = connections.indexOf(conn);
                if (index > -1) connections.splice(index, 1);
            });
            
            const nodeIndex = nodes.findIndex(n => n.id === concept.id);
            if (nodeIndex > -1) nodes.splice(nodeIndex, 1);
        });
    } else {
        if (!confirm(`Вы уверены, что хотите удалить философа "${philosopherName}"?`)) return;
    }
    
    // Удаляем философа
    delete philosopherConcepts[philosopherName];
    
    // Обновляем граф и легенду
    updateGraphData();
    initFilters();
    
    closeEditPhilosopherModal();
}

function closeEditPhilosopherModal() {
    const modal = document.getElementById('editPhilosopherModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    overlay.classList.remove('show');
    
    editMode.active = false;
    editMode.type = null;
    editMode.data = null;
    editMode.isNew = false;
}

function addConceptFromPhilosopher() {
    const philosopherName = editMode.isNew ? 
        document.getElementById('philosopherName').value.trim() : 
        editMode.data.name;
    
    if (!philosopherName) {
        alert('Сначала укажите имя философа');
        return;
    }
    
    closeEditPhilosopherModal();
    setTimeout(() => openEditConceptModal(null, philosopherName), 100);
}

// ============================================
// РЕДАКТИРОВАНИЕ КОНЦЕПЦИИ
// ============================================

function openEditConceptModal(conceptId = null, presetPhilosopher = null) {
    const modal = document.getElementById('editConceptModal');
    const overlay = document.getElementById('modalOverlay');
    const title = document.getElementById('editConceptTitle');
    const deleteBtn = document.getElementById('deleteConceptBtn');
    
    editMode.active = true;
    editMode.type = 'concept';
    editMode.isNew = !conceptId;
    editMode.data = conceptId ? findConceptById(conceptId) : null;
    
    // Заполняем селект философов
    const philosopherSelect = document.getElementById('conceptPhilosopher');
    philosopherSelect.innerHTML = '<option value="">Выберите философа</option>' +
        Object.keys(philosopherConcepts).map(name => 
            `<option value="${name}">${name}</option>`
        ).join('');
    
    // Заполняем селект рубрик
    const rubricSelect = document.getElementById('conceptRubric');
    rubricSelect.innerHTML = '<option value="">Выберите рубрику (необязательно)</option>' +
        rubrics.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
    
    if (editMode.isNew) {
        title.textContent = 'Добавить концепцию';
        document.getElementById('conceptLabel').value = '';
        document.getElementById('conceptPhilosopher').value = presetPhilosopher || '';
        document.getElementById('conceptRubric').value = '';
        document.getElementById('conceptDescription').value = '';
        document.getElementById('conceptExtendedDescription').value = '';
        deleteBtn.style.display = 'none';
        document.getElementById('conceptConnectionsContainer').innerHTML = 
            '<p style="color: #95a5a6; font-size: 13px; margin: 10px 0;">Нет связей</p>';
        document.getElementById('conceptConnectionsCount').textContent = '0';
    } else {
        title.textContent = 'Редактировать концепцию';
        const concept = editMode.data;
        document.getElementById('conceptLabel').value = concept.label;
        document.getElementById('conceptPhilosopher').value = concept.concept;
        
        const conceptRubrics = conceptToRubrics[concept.id] || [];
        document.getElementById('conceptRubric').value = conceptRubrics[0] || '';
        
        document.getElementById('conceptDescription').value = concept.description || '';
        document.getElementById('conceptExtendedDescription').value = concept.extendedDescription || '';
        deleteBtn.style.display = 'block';
        
        // Загружаем список связей
        loadConceptConnections(concept.id);
    }
    
    modal.classList.add('show');
    overlay.classList.add('show');
}

function loadConceptConnections(conceptId) {
    const conceptConnections = getConceptConnections(conceptId);
    const container = document.getElementById('conceptConnectionsContainer');
    const count = document.getElementById('conceptConnectionsCount');
    
    count.textContent = conceptConnections.length;
    
    if (conceptConnections.length === 0) {
        container.innerHTML = '<p style="color: #95a5a6; font-size: 13px; margin: 10px 0;">Нет связей</p>';
        return;
    }
    
    container.innerHTML = conceptConnections.map(conn => {
        const isSource = conn.from === conceptId;
        const otherConceptId = isSource ? conn.to : conn.from;
        const otherConcept = findConceptById(otherConceptId);
        const relationType = relationTypesObj[conn.type];
        const arrow = conn.bidirectional ? '↔' : (isSource ? '→' : '←');
        
        return `
            <div class="edit-list-item">
                <div class="edit-list-item-content" onclick="openEditConnectionModal('${conn.from}', '${conn.to}')">
                    <div class="edit-list-item-name">
                        ${arrow} ${otherConcept.label} (${otherConcept.concept})
                    </div>
                    <div class="edit-list-item-desc">${relationType.label}</div>
                </div>
                <div class="edit-list-item-actions">
                    <button class="edit-list-btn edit-list-btn-edit" onclick="event.stopPropagation(); openEditConnectionModal('${conn.from}', '${conn.to}')">Изменить</button>
                    <button class="edit-list-btn edit-list-btn-delete" onclick="event.stopPropagation(); deleteConnectionFromList('${conn.from}', '${conn.to}')">Удалить</button>
                </div>
            </div>
        `;
    }).join('');
}

function saveConcept() {
    const label = document.getElementById('conceptLabel').value.trim();
    const philosopher = document.getElementById('conceptPhilosopher').value;
    const rubric = document.getElementById('conceptRubric').value;
    const description = document.getElementById('conceptDescription').value.trim();
    const extendedDescription = document.getElementById('conceptExtendedDescription').value.trim();
    
    if (!label) {
        alert('Пожалуйста, введите название концепции');
        return;
    }
    
    if (!philosopher) {
        alert('Пожалуйста, выберите философа');
        return;
    }
    
    if (editMode.isNew) {
        // Создаем новую концепцию
        const newConcept = {
            id: generateId('concept'),
            label: label,
            concept: philosopher,
            description: description || undefined,
            extendedDescription: extendedDescription || undefined
        };
        
        nodes.push(newConcept);
        
        // Добавляем рубрику, если выбрана
        if (rubric) {
            if (!conceptToRubrics[newConcept.id]) {
                conceptToRubrics[newConcept.id] = [];
            }
            if (!conceptToRubrics[newConcept.id].includes(rubric)) {
                conceptToRubrics[newConcept.id].push(rubric);
            }
        }
    } else {
        // Обновляем существующую концепцию
        const concept = editMode.data;
        concept.label = label;
        concept.concept = philosopher;
        concept.description = description || undefined;
        concept.extendedDescription = extendedDescription || undefined;
        
        // Обновляем рубрику
        if (rubric) {
            if (!conceptToRubrics[concept.id]) {
                conceptToRubrics[concept.id] = [];
            }
            conceptToRubrics[concept.id] = [rubric];
        } else {
            delete conceptToRubrics[concept.id];
        }
    }
    
    // Обновляем граф
    updateGraphData();
    
    closeEditConceptModal();
}

function deleteConcept() {
    const concept = editMode.data;
    const conceptConnections = getConceptConnections(concept.id);
    
    let confirmMsg = `Вы уверены, что хотите удалить концепцию "${concept.label}"?`;
    
    if (conceptConnections.length > 0) {
        confirmMsg += `\n\nЭто удалит ${conceptConnections.length} связ(ь/и/ей).`;
        
        // Проверяем, какие концепции станут изолированными
        const isolated = getIsolatedConceptsAfterDeletion(conceptConnections);
        if (isolated.length > 0) {
            confirmMsg += `\n\nВнимание! После удаления следующие концепции останутся без связей:\n${isolated.map(c => `- ${c.label} (${c.concept})`).join('\n')}`;
        }
    }
    
    if (!confirm(confirmMsg)) return;
    
    // Удаляем все связи концепции
    conceptConnections.forEach(conn => {
        const index = connections.indexOf(conn);
        if (index > -1) connections.splice(index, 1);
    });
    
    // Удаляем концепцию из узлов
    const nodeIndex = nodes.findIndex(n => n.id === concept.id);
    if (nodeIndex > -1) nodes.splice(nodeIndex, 1);
    
    // Удаляем из рубрик
    delete conceptToRubrics[concept.id];
    
    // Обновляем граф
    updateGraphData();
    
    closeEditConceptModal();
    
    // Показываем список изолированных концепций, если есть
    const isolated = nodes.filter(n => isConceptIsolated(n.id));
    if (isolated.length > 0) {
        alert(`Внимание! Следующие концепции остались без связей:\n${isolated.map(c => `- ${c.label} (${c.concept})`).join('\n')}`);
    }
}

function closeEditConceptModal() {
    const modal = document.getElementById('editConceptModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    overlay.classList.remove('show');
    
    editMode.active = false;
    editMode.type = null;
    editMode.data = null;
    editMode.isNew = false;
}

function deleteConceptFromList(conceptId) {
    const concept = findConceptById(conceptId);
    if (!concept) return;
    
    const conceptConnections = getConceptConnections(conceptId);
    
    let confirmMsg = `Удалить концепцию "${concept.label}"?`;
    if (conceptConnections.length > 0) {
        confirmMsg += `\n\nЭто удалит ${conceptConnections.length} связ(ь/и/ей).`;
    }
    
    if (!confirm(confirmMsg)) return;
    
    // Удаляем связи
    conceptConnections.forEach(conn => {
        const index = connections.indexOf(conn);
        if (index > -1) connections.splice(index, 1);
    });
    
    // Удаляем концепцию
    const nodeIndex = nodes.findIndex(n => n.id === conceptId);
    if (nodeIndex > -1) nodes.splice(nodeIndex, 1);
    
    delete conceptToRubrics[conceptId];
    
    // Обновляем граф
    updateGraphData();
    
    // Перезагружаем список
    if (editMode.type === 'philosopher') {
        loadPhilosopherConcepts(editMode.data.name);
    }
}

function addConnectionFromConcept() {
    const conceptId = editMode.isNew ? null : editMode.data.id;
    
    if (!conceptId) {
        alert('Сначала сохраните концепцию');
        return;
    }
    
    closeEditConceptModal();
    setTimeout(() => {
        openEditConnectionModal(conceptId, null);
    }, 100);
}

// ============================================
// РЕДАКТИРОВАНИЕ СВЯЗИ
// ============================================

function openEditConnectionModal(sourceId = null, targetId = null) {
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    const title = document.getElementById('editConnectionTitle');
    const deleteBtn = document.getElementById('deleteConnectionBtn');
    
    editMode.active = true;
    editMode.type = 'connection';
    editMode.connectionSourceId = sourceId;
    editMode.connectionTargetId = targetId;
    
    const existingConnection = sourceId && targetId ? findConnection(sourceId, targetId) : null;
    editMode.isNew = !existingConnection;
    editMode.data = existingConnection;
    
    // Заполняем селект типов связей
    const typeSelect = document.getElementById('connectionType');
    typeSelect.innerHTML = '<option value="">Выберите тип связи</option>' +
        relationTypes.map(type => 
            `<option value="${type.id}">${type.label}</option>`
        ).join('');
    
    if (editMode.isNew) {
        title.textContent = 'Добавить связь';
        document.getElementById('connectionType').value = '';
        document.getElementById('connectionWeight').value = '2';
        document.getElementById('connectionBidirectional').checked = false;
        document.getElementById('connectionDescription').value = '';
        deleteBtn.style.display = 'none';
        
        // Устанавливаем начальную и конечную концепции, если они переданы
        if (sourceId) {
            const sourceConcept = findConceptById(sourceId);
            document.getElementById('connectionSourceSearch').value = 
                `${sourceConcept.label} (${sourceConcept.concept})`;
        } else {
            document.getElementById('connectionSourceSearch').value = '';
        }
        
        if (targetId) {
            const targetConcept = findConceptById(targetId);
            document.getElementById('connectionTargetSearch').value = 
                `${targetConcept.label} (${targetConcept.concept})`;
        } else {
            document.getElementById('connectionTargetSearch').value = '';
        }
    } else {
        title.textContent = 'Редактировать связь';
        const conn = existingConnection;
        document.getElementById('connectionType').value = conn.type;
        document.getElementById('connectionWeight').value = conn.weight || 2;
        document.getElementById('connectionBidirectional').checked = conn.bidirectional || false;
        document.getElementById('connectionDescription').value = conn.description || '';
        deleteBtn.style.display = 'block';
        
        const sourceConcept = findConceptById(conn.from);
        const targetConcept = findConceptById(conn.to);
        
        document.getElementById('connectionSourceSearch').value = 
            `${sourceConcept.label} (${sourceConcept.concept})`;
        document.getElementById('connectionTargetSearch').value = 
            `${targetConcept.label} (${targetConcept.concept})`;
    }
    
    modal.classList.add('show');
    overlay.classList.add('show');
}

function saveConnection() {
    const type = document.getElementById('connectionType').value;
    const weight = parseInt(document.getElementById('connectionWeight').value);
    const bidirectional = document.getElementById('connectionBidirectional').checked;
    const description = document.getElementById('connectionDescription').value.trim();
    
    if (!type) {
        alert('Пожалуйста, выберите тип связи');
        return;
    }
    
    if (!editMode.connectionSourceId || !editMode.connectionTargetId) {
        alert('Пожалуйста, выберите начальную и конечную концепции');
        return;
    }
    
    if (editMode.connectionSourceId === editMode.connectionTargetId) {
        alert('Начальная и конечная концепции должны быть различными');
        return;
    }
    
    if (editMode.isNew) {
        // Проверяем, не существует ли уже такая связь
        const existing = findConnection(editMode.connectionSourceId, editMode.connectionTargetId);
        if (existing) {
            alert('Связь между этими концепциями уже существует');
            return;
        }
        
        // Создаем новую связь
        const newConnection = {
            from: editMode.connectionSourceId,
            to: editMode.connectionTargetId,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description || undefined
        };
        
        connections.push(newConnection);
    } else {
        // Обновляем существующую связь
        const conn = editMode.data;
        conn.type = type;
        conn.weight = weight;
        conn.bidirectional = bidirectional;
        conn.description = description || undefined;
    }
    
    // Обновляем граф
    updateGraphData();
    
    closeEditConnectionModal();
}

function deleteConnection() {
    const conn = editMode.data;
    const sourceConcept = findConceptById(conn.from);
    const targetConcept = findConceptById(conn.to);
    
    let confirmMsg = `Удалить связь между "${sourceConcept.label}" и "${targetConcept.label}"?`;
    
    // Проверяем изолированность
    const isolated = getIsolatedConceptsAfterDeletion([conn]);
    if (isolated.length > 0) {
        confirmMsg += `\n\nВнимание! После удаления следующие концепции останутся без связей:\n${isolated.map(c => `- ${c.label} (${c.concept})`).join('\n')}`;
    }
    
    if (!confirm(confirmMsg)) return;
    
    // Удаляем связь
    const index = connections.indexOf(conn);
    if (index > -1) connections.splice(index, 1);
    
    // Обновляем граф
    updateGraphData();
    
    closeEditConnectionModal();
}

function closeEditConnectionModal() {
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    overlay.classList.remove('show');
    
    editMode.active = false;
    editMode.type = null;
    editMode.data = null;
    editMode.isNew = false;
    editMode.connectionSourceId = null;
    editMode.connectionTargetId = null;
}

function deleteConnectionFromList(sourceId, targetId) {
    const conn = findConnection(sourceId, targetId);
    if (!conn) return;
    
    const sourceConcept = findConceptById(sourceId);
    const targetConcept = findConceptById(targetId);
    
    if (!confirm(`Удалить связь между "${sourceConcept.label}" и "${targetConcept.label}"?`)) {
        return;
    }
    
    const index = connections.indexOf(conn);
    if (index > -1) connections.splice(index, 1);
    
    updateGraphData();
    
    // Перезагружаем список связей
    if (editMode.type === 'concept') {
        loadConceptConnections(editMode.data.id);
    }
}

// ============================================
// ВЫБОР КОНЦЕПЦИИ НА ГРАФЕ
// ============================================

function selectConceptOnGraph(target) {
    editMode.graphSelectionMode = true;
    editMode.graphSelectionTarget = target;
    
    const modeIndicator = document.getElementById('graphSelectionMode');
    const title = document.getElementById('selectionModeTitle');
    const desc = document.getElementById('selectionModeDesc');
    
    title.textContent = target === 'source' ? 
        'Выберите начальную концепцию' : 
        'Выберите конечную концепцию';
    desc.textContent = 'Кликните на концепцию в графе';
    
    modeIndicator.style.display = 'block';
    
    // Временно скрываем модальное окно
    document.getElementById('editConnectionModal').style.opacity = '0.3';
}

function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    document.getElementById('editConnectionModal').style.opacity = '1';
}

function handleConceptSelection(conceptId) {
    if (!editMode.graphSelectionMode) return;
    
    const concept = findConceptById(conceptId);
    const target = editMode.graphSelectionTarget;
    
    if (target === 'source') {
        editMode.connectionSourceId = conceptId;
        document.getElementById('connectionSourceSearch').value = 
            `${concept.label} (${concept.concept})`;
    } else {
        editMode.connectionTargetId = conceptId;
        document.getElementById('connectionTargetSearch').value = 
            `${concept.label} (${concept.concept})`;
    }
    
    cancelGraphSelection();
}

// ============================================
// ОБРАБОТЧИКИ SHIFT+CLICK
// ============================================

// Модифицируем существующую функцию handleNodeClick
const originalHandleNodeClick = handleNodeClick;
function handleNodeClick(event, d) {
    if (event.shiftKey) {
        event.stopPropagation();
        
        if (editMode.graphSelectionMode) {
            // Режим выбора концепции для связи
            handleConceptSelection(d.id);
        } else if (editMode.pendingConceptSelection.length > 0) {
            // Второй клик для создания связи
            const firstConceptId = editMode.pendingConceptSelection[0];
            if (firstConceptId !== d.id) {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConnectionModal(firstConceptId, d.id);
            }
        } else {
            // Первый shift+click на концепции - открываем редактирование или начинаем выбор второй концепции
            editMode.pendingConceptSelection = [d.id];
            
            // Визуально выделяем первую концепцию
            node.classed('selected', n => n.id === d.id);
            
            // Запускаем таймер - если второго клика не будет в течение 2 секунд, открываем редактирование
            setTimeout(() => {
                if (editMode.pendingConceptSelection.length > 0 && editMode.pendingConceptSelection[0] === d.id) {
                    editMode.pendingConceptSelection = [];
                    node.classed('selected', false);
                    openEditConceptModal(d.id);
                }
            }, 2000);
        }
    } else {
        // Обычный клик - используем оригинальную функцию
        originalHandleNodeClick.call(this, event, d);
    }
}

// Shift+click на пустом месте графа
d3.select('#graph').on('click', function(event) {
    if (event.shiftKey && event.target.tagName === 'svg') {
        openEditConceptModal();
    }
});

// ============================================
// ИНТЕГРАЦИЯ С ЛЕГЕНДОЙ
// ============================================

// Делаем блок философов интерактивным для редактирования
function makeLegendsEditable() {
    // Shift+click на пустом месте блока философов для добавления нового
    const philosophersSection = document.querySelector('.legend-section');
    if (philosophersSection) {
        philosophersSection.addEventListener('click', function(event) {
            if (event.shiftKey && event.target === this) {
                openEditPhilosopherModal();
            }
        });
    }
    
    // Делаем каждого философа кликабельным
    document.querySelectorAll('.legend-item').forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) {
            const philosopherName = checkbox.value;
            
            item.addEventListener('click', function(event) {
                if (event.shiftKey) {
                    event.preventDefault();
                    event.stopPropagation();
                    openEditPhilosopherModal(philosopherName);
                }
            });
        }
    });
}

// Вызываем после инициализации фильтров
setTimeout(makeLegendsEditable, 100);
```

---

## 4. Интеграция с существующим кодом

### 4.1 Обновление функции `initFilters()` для поддержки редактирования

Найдите функцию `initFilters()` (примерно на строке 1380) и после её определения добавьте вызов:

```javascript
// В конце функции initFilters() добавить:
makeLegendsEditable();
```

### 4.2 Обновление обработчика кликов на связях

Найдите обработчик `.on("click", ...)` для связей (примерно строка 1600) и замените на:

```javascript
.on("click", function(event, d) {
    if (event.shiftKey) {
        event.stopPropagation();
        openEditConnectionModal(d.source.id || d.source, d.target.id || d.target);
    } else {
        handleLinkClick(event, d);
    }
})
```

### 4.3 Добавление обработчика для escape-клавиши

Добавьте в конец скрипта (перед `</script>`):

```javascript
// Закрытие модальных окон по ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        if (editMode.graphSelectionMode) {
            cancelGraphSelection();
        } else if (document.getElementById('editPhilosopherModal').classList.contains('show')) {
            closeEditPhilosopherModal();
        } else if (document.getElementById('editConceptModal').classList.contains('show')) {
            closeEditConceptModal();
        } else if (document.getElementById('editConnectionModal').classList.contains('show')) {
            closeEditConnectionModal();
        }
    }
});

// Сброс выделения при обычном клике на графе
svg.on('click.clearSelection', function(event) {
    if (!event.shiftKey && event.target.tagName === 'svg') {
        editMode.pendingConceptSelection = [];
        node.classed('selected', false);
    }
});
```

---

## Инструкция по использованию

### Добавление философа:
1. Shift+Click на пустом месте блока "Философы" в легенде
2. Заполните форму и нажмите "Сохранить"

### Редактирование философа:
1. Shift+Click на философе в легенде
2. Измените данные и нажмите "Сохранить"

### Добавление концепции:
1. Shift+Click на пустом месте графа
2. Заполните форму и нажмите "Сохранить"

### Редактирование концепции:
1. Shift+Click на концепции в графе
2. Измените данные и нажмите "Сохранить"

### Добавление связи (способ 1):
1. Shift+Click на первой концепции
2. В течение 2 секунд Shift+Click на второй концепции
3. Откроется окно редактирования связи

### Добавление связи (способ 2):
1. Откройте редактирование концепции
2. Нажмите "+ Добавить связь"
3. Выберите концепции через поиск или кнопку "Указать на графе"

### Редактирование связи:
1. Shift+Click на связи в графе
2. Измените данные и нажмите "Сохранить"

---

## Важные замечания

1. **Автосохранение отсутствует** - все изменения применяются немедленно после нажатия "Сохранить"
2. **Предупреждения об изолированных концепциях** появляются автоматически при удалении связей
3. **Граф обновляется без перезагрузки** благодаря функции `updateGraphData()`
4. **Все изменения происходят в памяти браузера** и не сохраняются на сервер
5. **Валидация данных** происходит перед сохранением
6. **ESC** закрывает открытые модальные окна

---

**Конец документа**
