# Интеграция утилит и функций в унифицированную модальную систему

## Раздел 1: Утилиты общего назначения

### 1.1. generateId()

**Где объявить:** После `ModalContext` (сразу после глобальных переменных)

```javascript
/**
 * Генерация уникального ID
 * @param {string} prefix - Префикс для ID
 * @returns {string} - Уникальный ID
 */
function generateId(prefix = 'item') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

**Где использовать:**

#### В saveConceptData() - строка создания нового ID:

```javascript
function saveConceptData() {
    // ... валидация ...
    
    const isNew = !originalData || !originalData.id;
    
    if (isNew) {
        // ИСПОЛЬЗОВАНИЕ generateId
        const id = generateId('concept');
        
        const newConcept = {
            id: id,
            label: label,
            // ...
        };
        // ...
    }
}
```

#### В saveConnectionData() - если нужно создавать ID для связей:

```javascript
function saveConnectionData() {
    // ... валидация ...
    
    if (isNew) {
        // Если connections тоже нужны ID
        const connectionId = generateId('connection');
        
        const newConnection = {
            id: connectionId, // если нужно
            from: source,
            to: target,
            // ...
        };
    }
}
```

---

### 1.2. nodes.find(n => n.id === id) вместо findConceptById()

**Где использовать:** Везде, где нужно найти концепцию по ID

**Примеры замены:**

#### В generateConceptViewContent():
```javascript
// БЫЛО:
const conceptData = findConceptById(conceptId);

// СТАЛО:
const conceptData = nodes.find(n => n.id === conceptId);
```

#### В generateConnectionViewContent():
```javascript
// При обработке связей
const sourceNode = nodes.find(n => n.id === sourceId);
const targetNode = nodes.find(n => n.id === targetId);
```

#### В selectConnectionEditConcept():
```javascript
function selectConnectionEditConcept(type, conceptId) {
    const conceptData = nodes.find(n => n.id === conceptId);
    if (!conceptData) return;
    // ...
}
```

#### В generatePhilosopherEditContent():
```javascript
philosopherConceptsNodes.forEach(c => {
    html += `
        <button onclick="openUniversalModal('concept', nodes.find(n => n.id === '${c.id}'), 'view')">
            👁️ Просмотр
        </button>
    `;
});
```

**Вывод:** Не нужна отдельная функция, используйте прямо `nodes.find(n => n.id === id)` везде.

---

### 1.3. philosophers.find(p => p.nameRu === name) вместо findPhilosopherByName()

**Где использовать:** Везде, где нужно найти философа по имени

**Примеры замены:**

#### В savePhilosopherData():
```javascript
function savePhilosopherData() {
    const originalName = ModalContext.currentData;
    
    // Проверяем, существует ли уже
    if (philosophers.find(p => p.nameRu === name)) {
        alert('Философ с таким именем уже существует');
        return;
    }
    
    // Находим для редактирования
    const philosopherIndex = philosophers.findIndex(p => p.nameRu === originalName);
    // ...
}
```

#### В generatePhilosopherViewContent():
```javascript
function generatePhilosopherViewContent(philosopherName) {
    const philosopherData = philosophers.find(p => p.nameRu === philosopherName);
    if (!philosopherData) return '<p>Философ не найден</p>';
    // ...
}
```

#### В saveConceptData():
```javascript
function saveConceptData() {
    // ...
    const philosopherData = philosophers.find(p => p.nameRu === philosopher);
    if (!philosopherData) {
        alert('Философ не найден');
        return;
    }
    // ...
}
```

**Вывод:** Не нужна отдельная функция, используйте прямо `philosophers.find(p => p.nameRu === name)` везде.

---

### 1.4. findConnection() - доработанная

**Где объявить:** После generateId()

```javascript
/**
 * Поиск связи между двумя концепциями
 * @param {string} sourceId - ID начальной концепции
 * @param {string} targetId - ID конечной концепции
 * @param {boolean} bidirectional - Искать в обе стороны
 * @returns {object|null} - Найденная связь или null
 */
function findConnection(sourceId, targetId, bidirectional = true) {
    return links.find(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        
        if (srcId === sourceId && tgtId === targetId) {
            return true;
        }
        
        if (bidirectional && srcId === targetId && tgtId === sourceId) {
            return true;
        }
        
        return false;
    }) || null;
}
```

**Где использовать:**

#### В saveConnectionData() - проверка существующей связи:

```javascript
function saveConnectionData() {
    // ... получение данных формы ...
    
    if (isNew) {
        // ИСПОЛЬЗОВАНИЕ findConnection
        const existingLink = findConnection(source, target, true);
        
        if (existingLink) {
            const overwrite = confirm('Связь между этими концепциями уже существует. Заменить её?');
            if (!overwrite) return;
            
            // Удаляем старую связь
            const linkIndex = links.indexOf(existingLink);
            const connIndex = connections.findIndex(c => 
                c.from === (existingLink.source.id || existingLink.source) && 
                c.to === (existingLink.target.id || existingLink.target)
            );
            
            if (linkIndex !== -1) links.splice(linkIndex, 1);
            if (connIndex !== -1) connections.splice(connIndex, 1);
            
            // Удаляем визуальный элемент
            link.filter(d => d === existingLink).remove();
        }
        
        // Создаем новую связь
        // ...
    }
}
```

#### В функции проверки валидности данных:

```javascript
function validateConnectionData(source, target) {
    if (source === target) {
        alert('Нельзя создать связь концепции с самой собой');
        return false;
    }
    
    // Проверка существующей связи
    if (findConnection(source, target)) {
        // Связь уже существует
        return false;
    }
    
    return true;
}
```

---

### 1.5. getConceptConnections()

**Где объявить:** После findConnection()

```javascript
/**
 * Получение всех связей концепции
 * @param {string} conceptId - ID концепции
 * @returns {Array} - Массив связей
 */
function getConceptConnections(conceptId) {
    return links.filter(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        return srcId === conceptId || tgtId === conceptId;
    });
}
```

**Где использовать:**

#### В generateConceptViewContent() - для отображения связей:

```javascript
function generateConceptViewContent(conceptData) {
    // ... начальная часть ...
    
    // ИСПОЛЬЗОВАНИЕ getConceptConnections
    const nodeConnections = getConceptConnections(conceptData.id);
    
    if (nodeConnections.length > 0) {
        html += `
            <div class="connections-section">
                <div class="connections-title">📊 Связи узла (${nodeConnections.length})</div>
        `;
        // ... отображение связей ...
    }
    
    return html;
}
```

#### В generateConceptEditContent() - для редактирования связей:

```javascript
function generateConceptEditContent(conceptData) {
    // ...
    
    if (conceptData && conceptData.id) {
        // ИСПОЛЬЗОВАНИЕ getConceptConnections
        const conceptConnections = getConceptConnections(conceptData.id);
        
        html += `
            <div class="modal-section-title">
                🔗 Связи концепции (${conceptConnections.length})
            </div>
        `;
        // ... отображение и редактирование связей ...
    }
    
    return html;
}
```

#### В функции анализа концепции:

```javascript
function analyzeConceptImportance(conceptId) {
    const connections = getConceptConnections(conceptId);
    
    return {
        totalConnections: connections.length,
        incomingConnections: connections.filter(c => {
            const tgtId = c.target.id || c.target;
            return tgtId === conceptId;
        }).length,
        outgoingConnections: connections.filter(c => {
            const srcId = c.source.id || c.source;
            return srcId === conceptId;
        }).length
    };
}
```

---

### 1.6. isConceptIsolated()

**Где объявить:** После getConceptConnections()

```javascript
/**
 * Проверка, является ли концепция изолированной (нет связей)
 * @param {string} conceptId - ID концепции
 * @returns {boolean}
 */
function isConceptIsolated(conceptId) {
    return getConceptConnections(conceptId).length === 0;
}
```

**Где использовать:**

#### В функции deleteConcept() - предупреждение перед удалением:

```javascript
function deleteConcept(conceptId) {
    const concept = nodes.find(n => n.id === conceptId);
    if (!concept) {
        alert('Концепция не найдена');
        return;
    }
    
    // ИСПОЛЬЗОВАНИЕ isConceptIsolated
    if (!isConceptIsolated(conceptId)) {
        const confirmed = confirm(
            `Концепция "${concept.label}" имеет связи с другими концепциями. ` +
            `При удалении эти связи также будут удалены. Продолжить?`
        );
        if (!confirmed) return;
    }
    
    // Удаляем все связи концепции
    const connections = getConceptConnections(conceptId);
    connections.forEach(conn => {
        const linkIndex = links.indexOf(conn);
        if (linkIndex !== -1) links.splice(linkIndex, 1);
    });
    
    // Удаляем концепцию из массивов
    const nodeIndex = nodes.findIndex(n => n.id === conceptId);
    const conceptIndex = concepts.findIndex(c => c.id === conceptId);
    
    if (nodeIndex !== -1) nodes.splice(nodeIndex, 1);
    if (conceptIndex !== -1) concepts.splice(conceptIndex, 1);
    
    // Обновляем граф
    updateGraphData();
    
    closeUniversalModal();
}
```

#### Где объявить deleteConcept(): В секции функций сохранения/удаления (рядом с saveConceptData)

#### В отображении статистики концепции:

```javascript
function generateConceptStats(conceptData) {
    const isolated = isConceptIsolated(conceptData.id);
    
    return `
        <div class="concept-stats">
            <div>Статус: ${isolated ? '🔴 Изолированная' : '🟢 Связанная'}</div>
            ${isolated ? '<div style="color: #e74c3c; font-size: 11px;">⚠️ Эта концепция не имеет связей</div>' : ''}
        </div>
    `;
}
```

---

### 1.7. getIsolatedConceptsAfterDeletion()

**Где объявить:** После isConceptIsolated()

```javascript
/**
 * Получение концепций, которые станут изолированными после удаления философа
 * @param {string} philosopherName - Имя философа
 * @returns {Array} - Массив изолированных концепций
 */
function getIsolatedConceptsAfterDeletion(philosopherName) {
    const philosopherConceptsNodes = nodes.filter(n => n.concept === philosopherName);
    const philosopherConceptIds = philosopherConceptsNodes.map(c => c.id);
    
    const isolated = [];
    
    philosopherConceptsNodes.forEach(concept => {
        const connections = getConceptConnections(concept.id);
        
        // Проверяем, есть ли связи с концепциями других философов
        const externalConnections = connections.filter(conn => {
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            const otherConceptId = srcId === concept.id ? tgtId : srcId;
            return !philosopherConceptIds.includes(otherConceptId);
        });
        
        if (externalConnections.length === 0) {
            isolated.push(concept);
        }
    });
    
    return isolated;
}
```

**Где использовать:**

#### В функции deletePhilosopher() - предупреждение об изолированных концепциях:

```javascript
function deletePhilosopher(philosopherName) {
    const philosopherData = philosophers.find(p => p.nameRu === philosopherName);
    if (!philosopherData) {
        alert('Философ не найден');
        return;
    }
    
    const philosopherConceptsNodes = nodes.filter(n => n.concept === philosopherName);
    
    // ИСПОЛЬЗОВАНИЕ getIsolatedConceptsAfterDeletion
    const isolated = getIsolatedConceptsAfterDeletion(philosopherName);
    
    let confirmMessage = `Вы уверены, что хотите удалить философа "${philosopherName}"?\n\n`;
    confirmMessage += `Это приведет к удалению ${philosopherConceptsNodes.length} концепций.\n`;
    
    if (isolated.length > 0) {
        confirmMessage += `\n⚠️ Изолированные концепции (не имеют связей с другими философами):\n`;
        confirmMessage += isolated.map(c => `• ${c.label}`).join('\n');
        confirmMessage += `\n\nВсе эти концепции и их связи будут безвозвратно удалены.`;
    } else {
        confirmMessage += `\n⚠️ Все концепции философа имеют связи с концепциями других философов.`;
        confirmMessage += `\nЭти связи также будут удалены.`;
    }
    
    const confirmed = confirm(confirmMessage);
    if (!confirmed) return;
    
    // Удаляем все связи концепций философа
    philosopherConceptsNodes.forEach(concept => {
        const connections = getConceptConnections(concept.id);
        connections.forEach(conn => {
            const linkIndex = links.indexOf(conn);
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            const connIndex = connections.findIndex(c => c.from === srcId && c.to === tgtId);
            
            if (linkIndex !== -1) links.splice(linkIndex, 1);
            if (connIndex !== -1) connections.splice(connIndex, 1);
        });
    });
    
    // Удаляем концепции
    philosopherConceptsNodes.forEach(concept => {
        const nodeIndex = nodes.findIndex(n => n.id === concept.id);
        const conceptIndex = concepts.findIndex(c => c.id === concept.id);
        
        if (nodeIndex !== -1) nodes.splice(nodeIndex, 1);
        if (conceptIndex !== -1) concepts.splice(conceptIndex, 1);
    });
    
    // Удаляем философа
    const philIndex = philosophers.findIndex(p => p.nameRu === philosopherName);
    if (philIndex !== -1) philosophers.splice(philIndex, 1);
    
    delete philosopherConcepts[philosopherName];
    delete philosopherOrder[philosopherName];
    
    // Обновляем граф и фильтры
    updateGraphData();
    initFilters();
    setTimeout(makeLegendsEditable, 100);
    
    closeUniversalModal();
}
```

#### Где объявить deletePhilosopher(): В секции функций сохранения/удаления (рядом с savePhilosopherData)

---

## Раздел 2: Функции выбора концепций на графе

### 2.1. initConnectionSearchFields() - адаптированная

**Где объявить:** В секции функций работы с графом (после функций удаления)

```javascript
/**
 * Инициализация полей поиска концепций с возможностью выбора на графе
 * @param {string} mode - 'edit' или 'view'
 */
function initConnectionSearchFields(mode = 'edit') {
    const prefix = mode === 'view' ? 'connView' : 'conn';
    
    const sourceInput = document.getElementById(`${prefix}SourceSearch`);
    const targetInput = document.getElementById(`${prefix}TargetSearch`);
    
    if (!sourceInput || !targetInput) return;
    
    // Добавляем кнопки для выбора на графе
    const sourceContainer = sourceInput.parentElement;
    const targetContainer = targetInput.parentElement;
    
    // Создаем кнопки "Выбрать на графе"
    const createSelectButton = (type) => {
        const btn = document.createElement('button');
        btn.className = 'modal-btn-secondary';
        btn.style.cssText = 'margin-top: 8px; padding: 6px 12px; font-size: 11px; width: 100%;';
        btn.innerHTML = '🎯 Выбрать на графе';
        btn.onclick = (e) => {
            e.preventDefault();
            selectConceptOnGraph(type, mode);
        };
        return btn;
    };
    
    if (!sourceContainer.querySelector('.graph-select-btn')) {
        const sourceBtn = createSelectButton('source');
        sourceBtn.className += ' graph-select-btn';
        sourceContainer.appendChild(sourceBtn);
    }
    
    if (!targetContainer.querySelector('.graph-select-btn')) {
        const targetBtn = createSelectButton('target');
        targetBtn.className += ' graph-select-btn';
        targetContainer.appendChild(targetBtn);
    }
}
```

**Где использовать:**

#### В generateConnectionEditContent() - после отрисовки HTML:

```javascript
function generateConnectionEditContent(connectionData) {
    // ... генерация HTML ...
    
    let html = `
        <h2>${isNew ? 'Создать связь' : 'Редактировать связь'}</h2>
        <!-- ... поля формы ... -->
    `;
    
    // После вставки HTML нужно инициализировать кнопки выбора на графе
    // Это делается через setTimeout, чтобы HTML успел отрендериться
    
    return html;
}

// В функции openUniversalModal, после установки content.innerHTML = html:
function openUniversalModal(entityType, data, mode = 'view') {
    // ...
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
    
    // ИСПОЛЬЗОВАНИЕ initConnectionSearchFields
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
}
```

#### В generateConnectionViewContent() - аналогично:

```javascript
// В функции openUniversalModal:
if (entityType === 'connection' && mode === 'view') {
    setTimeout(() => {
        initConnectionSearchFields('view');
    }, 0);
}
```

---

### 2.2. selectConceptOnGraph() - адаптированная

**Где объявить:** После initConnectionSearchFields()

```javascript
/**
 * Активация режима выбора концепции на графе
 * @param {string} type - 'source' или 'target'
 * @param {string} mode - 'edit' или 'view'
 */
function selectConceptOnGraph(type, mode = 'edit') {
    // Сохраняем контекст выбора
    window.graphSelectionContext = {
        active: true,
        type: type,
        mode: mode
    };
    
    // Визуальная подсветка режима выбора
    const overlay = document.getElementById('modalOverlay');
    overlay.style.cursor = 'crosshair';
    
    // Меняем курсор на всех узлах
    d3.selectAll('.node').style('cursor', 'crosshair');
    
    // Показываем подсказку
    const hint = document.createElement('div');
    hint.id = 'graph-selection-hint';
    hint.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(162, 155, 254, 0.95);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        z-index: 2001;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    hint.innerHTML = `
        🎯 Выберите ${type === 'source' ? 'начальную' : 'конечную'} концепцию на графе
        <button onclick="cancelGraphSelection()" style="margin-left: 15px; padding: 4px 10px; background: white; color: #6c5ce7; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">
            ✖️ Отмена
        </button>
    `;
    document.body.appendChild(hint);
    
    // Добавляем одноразовый обработчик клика на узлы
    const nodeClickHandler = function(event, d) {
        event.stopPropagation();
        handleGraphConceptSelection(d, type, mode);
    };
    
    // Сохраняем обработчик для возможности удаления
    window.graphSelectionHandler = nodeClickHandler;
    
    d3.selectAll('.node').on('click.selection', nodeClickHandler);
}
```

**Где использовать:** Вызывается автоматически при клике на кнопку "🎯 Выбрать на графе" (создаваемую в initConnectionSearchFields).

---

### 2.3. handleGraphConceptSelection() - НОВАЯ

**Где объявить:** После selectConceptOnGraph()

```javascript
/**
 * Обработка выбора концепции на графе
 * @param {object} conceptData - Данные выбранной концепции
 * @param {string} type - 'source' или 'target'
 * @param {string} mode - 'edit' или 'view'
 */
function handleGraphConceptSelection(conceptData, type, mode) {
    if (!window.graphSelectionContext || !window.graphSelectionContext.active) {
        return;
    }
    
    // Вызываем соответствующую функцию выбора
    if (mode === 'view') {
        selectConnectionViewConcept(type, conceptData.id);
    } else {
        selectConnectionEditConcept(type, conceptData.id);
    }
    
    // Отменяем режим выбора
    cancelGraphSelection();
}
```

**Где использовать:** Вызывается автоматически при клике на узел графа в режиме выбора концепции.

---

### 2.4. cancelGraphSelection()

**Где объявить:** После handleGraphConceptSelection()

```javascript
/**
 * Отмена режима выбора концепции на графе
 */
function cancelGraphSelection() {
    if (!window.graphSelectionContext) return;
    
    // Убираем контекст
    window.graphSelectionContext = { active: false };
    
    // Восстанавливаем курсор
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.style.cursor = '';
    
    d3.selectAll('.node').style('cursor', 'pointer');
    
    // Убираем подсказку
    const hint = document.getElementById('graph-selection-hint');
    if (hint) hint.remove();
    
    // Удаляем обработчик клика
    d3.selectAll('.node').on('click.selection', null);
}
```

**Где использовать:**
1. Вызывается автоматически после выбора концепции (в handleGraphConceptSelection)
2. Вызывается при клике на кнопку "✖️ Отмена" в подсказке
3. Можно вызывать при закрытии модального окна для очистки:

```javascript
function closeUniversalModal() {
    // ... существующий код ...
    
    // Отменяем режим выбора на графе, если он активен
    if (window.graphSelectionContext && window.graphSelectionContext.active) {
        cancelGraphSelection();
    }
    
    // ... остальной код ...
}
```

---

## Раздел 3: Функции обновления графа

### 3.1. updateGraphData() - упрощённая

**Где объявить:** В секции функций работы с графом (после функций выбора)

```javascript
/**
 * Обновление данных графа после изменений
 */
function updateGraphData() {
    // Обновляем данные симуляции
    simulation.nodes(nodes);
    simulation.force('link').links(links);
    
    // Обновляем визуальные элементы
    updateGraphVisualization();
    
    // Перезапускаем симуляцию
    simulation.alpha(0.3).restart();
}
```

**Где использовать:**

#### После удаления философа:
```javascript
function deletePhilosopher(philosopherName) {
    // ... удаление концепций и связей ...
    
    // ИСПОЛЬЗОВАНИЕ updateGraphData
    updateGraphData();
    
    // Обновляем фильтры
    initFilters();
    setTimeout(makeLegendsEditable, 100);
    
    closeUniversalModal();
}
```

#### После удаления концепции:
```javascript
function deleteConcept(conceptId) {
    // ... удаление связей и концепции ...
    
    // ИСПОЛЬЗОВАНИЕ updateGraphData
    updateGraphData();
    
    closeUniversalModal();
}
```

#### После массового изменения данных:
```javascript
function importGraphData(newNodes, newLinks) {
    nodes = newNodes;
    links = newLinks;
    
    // ИСПОЛЬЗОВАНИЕ updateGraphData
    updateGraphData();
}
```

---

### 3.2. updateGraphVisualization() - упрощённая

**Где объявить:** После updateGraphData()

```javascript
/**
 * Обновление визуализации графа
 */
function updateGraphVisualization() {
    // Обновляем связи
    link = g.select('g:nth-child(1)').selectAll('.link')
        .data(links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
    
    link.exit().remove();
    
    const linkEnter = link.enter().append('path')
        .attr('class', d => {
            let classes = 'link';
            if (d.bidirectional) classes += ' bidirectional';
            if (d.type === 'internal_contradiction') classes += ' internal-contradiction';
            if (d.weight === 1) classes += ' weight-weak';
            else if (d.weight === 2) classes += ' weight-medium';
            else if (d.weight === 3) classes += ' weight-strong';
            return classes;
        })
        .attr('stroke', d => relationTypesObj[d.type].color)
        .attr('marker-end', d => `url(#arrow-${d.type})`)
        .style('cursor', 'pointer')
        .on('click', handleLinkClick);
    
    link = linkEnter.merge(link);
    
    // Обновляем узлы
    node = g.select('g:nth-child(2)').selectAll('.node')
        .data(nodes, d => d.id);
    
    node.exit().remove();
    
    const nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    nodeEnter.append('circle')
        .attr('r', 18)
        .attr('fill', d => philosopherConcepts[d.concept].color)
        .attr('stroke', '#fff');
    
    nodeEnter.append('text')
        .attr('dy', -25)
        .attr('text-anchor', 'middle')
        .text(d => d.label);
    
    node = nodeEnter.merge(node);
    
    node.on('click', handleNodeClick);
    
    // Обновляем фильтры
    updateFilterStats();
}
```

**Где использовать:** Вызывается автоматически из updateGraphData(), но можно использовать отдельно:

#### При изменении цветов философов:
```javascript
function updatePhilosopherColors() {
    // Обновляем только цвета узлов без перестройки всего графа
    node.selectAll('circle')
        .attr('fill', d => philosopherConcepts[d.concept].color);
}
```

#### При изменении меток узлов:
```javascript
function updateNodeLabels() {
    node.selectAll('text')
        .text(d => d.label);
}
```

---

## Раздел 4: Сводная таблица размещения функций

| Функция | Где объявить | Основное использование |
|---------|--------------|------------------------|
| `generateId()` | После ModalContext | `saveConceptData()`, `saveConnectionData()` |
| `findConnection()` | После generateId() | `saveConnectionData()` - проверка дубликатов |
| `getConceptConnections()` | После findConnection() | `generateConceptViewContent()`, `generateConceptEditContent()` |
| `isConceptIsolated()` | После getConceptConnections() | `deleteConcept()` - предупреждение |
| `getIsolatedConceptsAfterDeletion()` | После isConceptIsolated() | `deletePhilosopher()` - анализ перед удалением |
| `initConnectionSearchFields()` | Секция работы с графом | `openUniversalModal()` для connection |
| `selectConceptOnGraph()` | После initConnectionSearchFields() | Кнопка "Выбрать на графе" |
| `handleGraphConceptSelection()` | После selectConceptOnGraph() | Клик на узел в режиме выбора |
| `cancelGraphSelection()` | После handleGraphConceptSelection() | Отмена выбора, закрытие окна |
| `updateGraphData()` | Секция работы с графом | `deleteConcept()`, `deletePhilosopher()` |
| `updateGraphVisualization()` | После updateGraphData() | Вызывается из updateGraphData() |
| `deleteConcept()` | Рядом с saveConceptData() | Кнопка удаления в режиме edit |
| `deletePhilosopher()` | Рядом с savePhilosopherData() | Кнопка удаления в режиме edit |

---

## Раздел 5: Структура кода (рекомендуемый порядок)

```javascript
// ============================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ И КОНТЕКСТ
// ============================================
const ModalContext = { ... };

// ============================================
// УТИЛИТЫ ОБЩЕГО НАЗНАЧЕНИЯ
// ============================================
function generateId(prefix) { ... }
function findConnection(sourceId, targetId, bidirectional) { ... }
function getConceptConnections(conceptId) { ... }
function isConceptIsolated(conceptId) { ... }
function getIsolatedConceptsAfterDeletion(philosopherName) { ... }

// ============================================
// УНИВЕРСАЛЬНАЯ СИСТЕМА МОДАЛЬНЫХ ОКОН
// ============================================
function openUniversalModal(entityType, data, mode) { ... }
function closeUniversalModal() { ... }
function toggleModalMode() { ... }
function hasUnsavedChanges() { ... }

// ============================================
// ГЕНЕРАТОРЫ КОНТЕНТА ДЛЯ РЕЖИМА ПРОСМОТРА
// ============================================
function generatePhilosopherViewContent(philosopherName) { ... }
function generateConceptViewContent(conceptData) { ... }
function generateConnectionViewContent(connectionData) { ... }

// ============================================
// ГЕНЕРАТОРЫ КОНТЕНТА ДЛЯ РЕЖИМА РЕДАКТИРОВАНИЯ
// ============================================
function generatePhilosopherEditContent(philosopherName) { ... }
function generateConceptEditContent(conceptData) { ... }
function generateConnectionEditContent(connectionData) { ... }

// ============================================
// ФУНКЦИИ СОХРАНЕНИЯ И УДАЛЕНИЯ
// ============================================
function savePhilosopherData() { ... }
function deletePhilosopher(philosopherName) { ... }

function saveConceptData() { ... }
function deleteConcept(conceptId) { ... }

function saveConnectionData() { ... }
function deleteConnection(sourceId, targetId) { ... }

// ============================================
// ФУНКЦИИ ВЫБОРА КОНЦЕПЦИЙ НА ГРАФЕ
// ============================================
function initConnectionSearchFields(mode) { ... }
function selectConceptOnGraph(type, mode) { ... }
function handleGraphConceptSelection(conceptData, type, mode) { ... }
function cancelGraphSelection() { ... }

// ============================================
// ФУНКЦИИ ОБНОВЛЕНИЯ ГРАФА
// ============================================
function updateGraphData() { ... }
function updateGraphVisualization() { ... }
function addNodeToGraph(nodeData) { ... }
function updateNodeOnGraph(nodeData) { ... }
function addLinkToGraph(linkData) { ... }
function updateLinkOnGraph(linkData) { ... }

// ============================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================
function createNewConceptForPhilosopher(philosopherName) { ... }
function createNewConnectionForConcept(conceptId) { ... }
// ... и т.д.
```

---

## Раздел 6: Чек-лист интеграции

### ✅ Утилиты:
- [ ] Добавить `generateId()` после ModalContext
- [ ] Заменить все `findConceptById()` на `nodes.find(n => n.id === id)`
- [ ] Заменить все `findPhilosopherByName()` на `philosophers.find(p => p.nameRu === name)`
- [ ] Добавить `findConnection()` после generateId()
- [ ] Добавить `getConceptConnections()` после findConnection()
- [ ] Добавить `isConceptIsolated()` после getConceptConnections()
- [ ] Добавить `getIsolatedConceptsAfterDeletion()` после isConceptIsolated()

### ✅ Функции удаления:
- [ ] Создать `deleteConcept()` с использованием isConceptIsolated()
- [ ] Создать `deletePhilosopher()` с использованием getIsolatedConceptsAfterDeletion()

### ✅ Выбор на графе:
- [ ] Добавить `initConnectionSearchFields()` в секцию работы с графом
- [ ] Добавить `selectConceptOnGraph()` после initConnectionSearchFields()
- [ ] Добавить `handleGraphConceptSelection()` после selectConceptOnGraph()
- [ ] Добавить `cancelGraphSelection()` после handleGraphConceptSelection()
- [ ] Вызвать `initConnectionSearchFields()` в openUniversalModal() для connection
- [ ] Добавить вызов `cancelGraphSelection()` в closeUniversalModal()

### ✅ Обновление графа:
- [ ] Добавить `updateGraphData()` в секцию работы с графом
- [ ] Добавить `updateGraphVisualization()` после updateGraphData()
- [ ] Использовать `updateGraphData()` в deleteConcept()
- [ ] Использовать `updateGraphData()` в deletePhilosopher()

---

**Примечание:** Этот документ содержит полную карту интеграции всех функций в унифицированную систему с точным указанием мест размещения и использования.
