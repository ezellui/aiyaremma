# Интеграция функций в унифицированную систему (ИСПРАВЛЕННАЯ ВЕРСИЯ)

## Важное уточнение

Многие паттерны использования `nodes.find()` и `philosophers.find()` **уже реализованы** в ранее созданных функциях. Этот документ фокусируется только на **новых местах использования**.

---

## 1. generateId() и поле id в связях

### Вопрос: Нужен ли id для связей?

**Краткий ответ:** В текущей архитектуре - НЕТ.

**Объяснение:**
- В D3.js связи идентифицируются парой `source-target`
- В массиве `links` используется функция ключа: `d => '${d.source.id || d.source}-${d.target.id || d.target}'`
- В массиве `connections` связи идентифицируются по полям `from` и `to`

**Если всё же нужен id:**

```javascript
function saveConnectionData() {
    // ... валидация ...
    
    if (isNew) {
        const connectionId = generateId('connection'); // ← ИСПОЛЬЗОВАНИЕ
        
        const newConnection = {
            id: connectionId,  // ← Добавляем ID
            from: source,
            to: target,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description
        };
        
        const newLink = {
            id: connectionId,  // ← Добавляем ID и в link
            source: source,
            target: target,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description
        };
        
        connections.push(newConnection);
        links.push(newLink);
        
        // Использование ID для удаления:
        // const connToDelete = connections.find(c => c.id === connectionId);
    }
}
```

**Рекомендация:** Оставьте как есть (без ID для связей), используйте пару source-target.

---

## 2. Утилиты - где объявить и РЕАЛЬНО использовать

### 2.1. generateId() 

**Где объявить:** После ModalContext

```javascript
/**
 * Генерация уникального ID
 */
function generateId(prefix = 'item') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

**Где РЕАЛЬНО использовать:**

#### В saveConceptData() - ЕДИНСТВЕННОЕ реальное использование:

```javascript
function saveConceptData() {
    // ...
    if (isNew) {
        // ✅ ЗДЕСЬ РЕАЛЬНО НУЖНО ИСПОЛЬЗОВАТЬ
        const id = generateId('concept');
        
        const newConcept = {
            id: id,  // ← вместо хардкода
            // ...
        };
    }
}
```

**Итого:** Используется ТОЛЬКО в saveConceptData() при создании новой концепции.

---

### 2.2. findConnection()

**Где объявить:** После generateId()

```javascript
/**
 * Поиск связи между двумя концепциями
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

**Где РЕАЛЬНО использовать:**

#### В saveConnectionData() - проверка существующей связи:

```javascript
function saveConnectionData() {
    // ... получение данных формы ...
    
    if (isNew) {
        // ✅ ЗДЕСЬ РЕАЛЬНО НУЖНО ИСПОЛЬЗОВАТЬ
        const existingLink = findConnection(source, target, true);
        
        if (existingLink) {
            const overwrite = confirm('Связь между этими концепциями уже существует. Заменить её?');
            if (!overwrite) return;
            
            // Удаляем существующую
            const linkIndex = links.indexOf(existingLink);
            if (linkIndex !== -1) links.splice(linkIndex, 1);
            
            const srcId = existingLink.source.id || existingLink.source;
            const tgtId = existingLink.target.id || existingLink.target;
            const connIndex = connections.findIndex(c => c.from === srcId && c.to === tgtId);
            if (connIndex !== -1) connections.splice(connIndex, 1);
        }
        
        // Создаем новую связь
        // ...
    }
}
```

#### ❌ НЕ НУЖНО использовать в других функциях - там уже есть прямые вызовы links.filter()

---

### 2.3. getConceptConnections()

**Где объявить:** После findConnection()

```javascript
/**
 * Получение всех связей концепции
 */
function getConceptConnections(conceptId) {
    return links.filter(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        return srcId === conceptId || tgtId === conceptId;
    });
}
```

**Где РЕАЛЬНО использовать:**

#### В новой функции deleteConcept():

```javascript
function deleteConcept(conceptId) {
    const concept = nodes.find(n => n.id === conceptId);
    if (!concept) {
        alert('Концепция не найдена');
        return;
    }
    
    // ✅ ЗДЕСЬ РЕАЛЬНО НУЖНО ИСПОЛЬЗОВАТЬ
    const conceptConnections = getConceptConnections(conceptId);
    
    if (conceptConnections.length > 0) {
        const confirmed = confirm(
            `Концепция "${concept.label}" имеет ${conceptConnections.length} связей. ` +
            `При удалении эти связи также будут удалены. Продолжить?`
        );
        if (!confirmed) return;
        
        // Удаляем связи
        conceptConnections.forEach(conn => {
            const linkIndex = links.indexOf(conn);
            if (linkIndex !== -1) links.splice(linkIndex, 1);
            
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            const connIndex = connections.findIndex(c => c.from === srcId && c.to === tgtId);
            if (connIndex !== -1) connections.splice(connIndex, 1);
        });
    }
    
    // Удаляем концепцию
    const nodeIndex = nodes.findIndex(n => n.id === conceptId);
    const conceptIndex = concepts.findIndex(c => c.id === conceptId);
    
    if (nodeIndex !== -1) nodes.splice(nodeIndex, 1);
    if (conceptIndex !== -1) concepts.splice(conceptIndex, 1);
    
    delete conceptToRubrics[conceptId];
    
    // Обновляем граф
    updateGraphData();
    
    closeUniversalModal();
}
```

**Где объявить deleteConcept():** В секции функций сохранения/удаления (после saveConceptData)

#### ❌ НЕ НУЖНО использовать в generateConceptViewContent и generateConceptEditContent - там уже есть прямые links.filter()

---

### 2.4. isConceptIsolated()

**Где объявить:** После getConceptConnections()

```javascript
/**
 * Проверка, является ли концепция изолированной (нет связей)
 */
function isConceptIsolated(conceptId) {
    return getConceptConnections(conceptId).length === 0;
}
```

**Где РЕАЛЬНО использовать:**

#### В функции deleteConcept() - можно добавить предупреждение:

```javascript
function deleteConcept(conceptId) {
    const concept = nodes.find(n => n.id === conceptId);
    if (!concept) {
        alert('Концепция не найдена');
        return;
    }
    
    // ✅ МОЖНО ИСПОЛЬЗОВАТЬ для улучшения UX
    if (isConceptIsolated(conceptId)) {
        const confirmed = confirm(
            `Концепция "${concept.label}" не имеет связей с другими концепциями. Удалить?`
        );
        if (!confirmed) return;
    } else {
        const conceptConnections = getConceptConnections(conceptId);
        const confirmed = confirm(
            `Концепция "${concept.label}" имеет ${conceptConnections.length} связей. ` +
            `При удалении эти связи также будут удалены. Продолжить?`
        );
        if (!confirmed) return;
        
        // Удаляем связи
        conceptConnections.forEach(conn => {
            const linkIndex = links.indexOf(conn);
            if (linkIndex !== -1) links.splice(linkIndex, 1);
            
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            const connIndex = connections.findIndex(c => c.from === srcId && c.to === tgtId);
            if (connIndex !== -1) connections.splice(connIndex, 1);
        });
    }
    
    // Удаляем концепцию
    const nodeIndex = nodes.findIndex(n => n.id === conceptId);
    const conceptIndex = concepts.findIndex(c => c.id === conceptId);
    
    if (nodeIndex !== -1) nodes.splice(nodeIndex, 1);
    if (conceptIndex !== -1) concepts.splice(conceptIndex, 1);
    
    delete conceptToRubrics[conceptId];
    
    updateGraphData();
    closeUniversalModal();
}
```

---

### 2.5. getIsolatedConceptsAfterDeletion()

**Где объявить:** После isConceptIsolated()

```javascript
/**
 * Получение концепций, которые станут изолированными после удаления философа
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

**Где РЕАЛЬНО использовать:**

#### В новой функции deletePhilosopher():

```javascript
function deletePhilosopher(philosopherName) {
    const philosopherData = philosophers.find(p => p.nameRu === philosopherName);
    if (!philosopherData) {
        alert('Философ не найден');
        return;
    }
    
    const philosopherConceptsNodes = nodes.filter(n => n.concept === philosopherName);
    
    // ✅ ЗДЕСЬ РЕАЛЬНО НУЖНО ИСПОЛЬЗОВАТЬ
    const isolated = getIsolatedConceptsAfterDeletion(philosopherName);
    
    let confirmMessage = `Вы уверены, что хотите удалить философа "${philosopherName}"?\n\n`;
    confirmMessage += `Это приведет к удалению ${philosopherConceptsNodes.length} концепций.\n`;
    
    if (isolated.length > 0) {
        confirmMessage += `\n⚠️ Изолированные концепции (не имеют связей с другими философами):\n`;
        confirmMessage += isolated.slice(0, 5).map(c => `• ${c.label}`).join('\n');
        if (isolated.length > 5) {
            confirmMessage += `\n... и ещё ${isolated.length - 5}`;
        }
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
        
        delete conceptToRubrics[concept.id];
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

**Где объявить deletePhilosopher():** В секции функций сохранения/удаления (после savePhilosopherData)

---

## 3. Функции выбора на графе

### 3.1. initConnectionSearchFields()

**Где объявить:** В секции функций работы с графом

```javascript
/**
 * Инициализация полей поиска концепций с возможностью выбора на графе
 */
function initConnectionSearchFields(mode = 'edit') {
    const prefix = mode === 'view' ? 'connView' : 'conn';
    
    const sourceInput = document.getElementById(`${prefix}SourceSearch`);
    const targetInput = document.getElementById(`${prefix}TargetSearch`);
    
    if (!sourceInput || !targetInput) return;
    
    const sourceContainer = sourceInput.parentElement;
    const targetContainer = targetInput.parentElement;
    
    const createSelectButton = (type) => {
        const btn = document.createElement('button');
        btn.className = 'modal-btn-secondary graph-select-btn';
        btn.style.cssText = 'margin-top: 8px; padding: 6px 12px; font-size: 11px; width: 100%;';
        btn.innerHTML = '🎯 Выбрать на графе';
        btn.onclick = (e) => {
            e.preventDefault();
            selectConceptOnGraph(type, mode);
        };
        return btn;
    };
    
    if (!sourceContainer.querySelector('.graph-select-btn')) {
        sourceContainer.appendChild(createSelectButton('source'));
    }
    
    if (!targetContainer.querySelector('.graph-select-btn')) {
        targetContainer.appendChild(createSelectButton('target'));
    }
}
```

**Где РЕАЛЬНО использовать:**

#### В функции openUniversalModal() - после установки HTML:

```javascript
function openUniversalModal(entityType, data, mode = 'view') {
    // ... существующий код ...
    
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
    
    // ✅ ДОБАВИТЬ ЗДЕСЬ
    if (entityType === 'connection') {
        setTimeout(() => {
            initConnectionSearchFields(mode);
        }, 0);
    }
}
```

---

### 3.2. selectConceptOnGraph()

**Где объявить:** После initConnectionSearchFields()

```javascript
/**
 * Активация режима выбора концепции на графе
 */
function selectConceptOnGraph(type, mode = 'edit') {
    window.graphSelectionContext = {
        active: true,
        type: type,
        mode: mode
    };
    
    const overlay = document.getElementById('modalOverlay');
    overlay.style.cursor = 'crosshair';
    
    d3.selectAll('.node').style('cursor', 'crosshair');
    
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
    
    const nodeClickHandler = function(event, d) {
        event.stopPropagation();
        handleGraphConceptSelection(d, type, mode);
    };
    
    window.graphSelectionHandler = nodeClickHandler;
    d3.selectAll('.node').on('click.selection', nodeClickHandler);
}
```

**Где использовать:** Вызывается автоматически кнопкой "🎯 Выбрать на графе"

---

### 3.3. handleGraphConceptSelection() - НОВАЯ ФУНКЦИЯ

**Где объявить:** После selectConceptOnGraph()

```javascript
/**
 * Обработка выбора концепции на графе
 */
function handleGraphConceptSelection(conceptData, type, mode) {
    if (!window.graphSelectionContext || !window.graphSelectionContext.active) {
        return;
    }
    
    // ✅ ИСПОЛЬЗОВАНИЕ УЖЕ СУЩЕСТВУЮЩИХ ФУНКЦИЙ
    if (mode === 'view') {
        selectConnectionViewConcept(type, conceptData.id);
    } else {
        selectConnectionEditConcept(type, conceptData.id);
    }
    
    cancelGraphSelection();
}
```

---

### 3.4. cancelGraphSelection()

**Где объявить:** После handleGraphConceptSelection()

```javascript
/**
 * Отмена режима выбора концепции на графе
 */
function cancelGraphSelection() {
    if (!window.graphSelectionContext) return;
    
    window.graphSelectionContext = { active: false };
    
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.style.cursor = '';
    
    d3.selectAll('.node').style('cursor', 'pointer');
    
    const hint = document.getElementById('graph-selection-hint');
    if (hint) hint.remove();
    
    d3.selectAll('.node').on('click.selection', null);
}
```

**Где РЕАЛЬНО использовать:**

#### В функции closeUniversalModal() - для очистки:

```javascript
function closeUniversalModal() {
    const modal = document.getElementById('universalModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('universalModalContent');
    
    content.innerHTML = '';
    modal.classList.remove('show', 'edit-mode');
    overlay.classList.remove('show');
    
    // ✅ ДОБАВИТЬ ЗДЕСЬ
    if (window.graphSelectionContext && window.graphSelectionContext.active) {
        cancelGraphSelection();
    }
    
    ModalContext.currentEntity = null;
    ModalContext.currentMode = 'view';
    ModalContext.currentData = null;
    ModalContext.editState = {};
    
    unfreezeSimulation();
}
```

---

## 4. Функции обновления графа

### 4.1. updateGraphData()

**Где объявить:** В секции функций работы с графом

```javascript
/**
 * Обновление данных графа после изменений
 */
function updateGraphData() {
    simulation.nodes(nodes);
    simulation.force('link').links(links);
    
    updateGraphVisualization();
    
    simulation.alpha(0.3).restart();
}
```

**Где РЕАЛЬНО использовать:**

#### В deleteConcept():
```javascript
function deleteConcept(conceptId) {
    // ... удаление концепции и связей ...
    
    // ✅ ИСПОЛЬЗОВАНИЕ
    updateGraphData();
    
    closeUniversalModal();
}
```

#### В deletePhilosopher():
```javascript
function deletePhilosopher(philosopherName) {
    // ... удаление философа, концепций и связей ...
    
    // ✅ ИСПОЛЬЗОВАНИЕ
    updateGraphData();
    
    initFilters();
    setTimeout(makeLegendsEditable, 100);
    
    closeUniversalModal();
}
```

---

### 4.2. updateGraphVisualization()

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
    
    updateFilterStats();
}
```

**Где использовать:** Вызывается автоматически из updateGraphData()

---

## 5. Итоговая структура кода

```javascript
// ============================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ============================================
const ModalContext = { ... };

// ============================================
// УТИЛИТЫ
// ============================================
function generateId(prefix) { ... }                              // ← ДОБАВИТЬ
function findConnection(sourceId, targetId, bidirectional) { ... } // ← ДОБАВИТЬ
function getConceptConnections(conceptId) { ... }                // ← ДОБАВИТЬ
function isConceptIsolated(conceptId) { ... }                    // ← ДОБАВИТЬ
function getIsolatedConceptsAfterDeletion(philosopherName) { ... } // ← ДОБАВИТЬ

// ============================================
// УНИВЕРСАЛЬНАЯ МОДАЛЬНАЯ СИСТЕМА
// ============================================
function openUniversalModal(entityType, data, mode) { 
    // ...
    // ✅ ДОБАВИТЬ: if (entityType === 'connection') initConnectionSearchFields(mode);
}
function closeUniversalModal() { 
    // ...
    // ✅ ДОБАВИТЬ: cancelGraphSelection();
}
// ... остальные функции модальной системы ...

// ============================================
// ГЕНЕРАТОРЫ КОНТЕНТА
// ============================================
// (УЖЕ СОЗДАНЫ - НЕ МЕНЯТЬ)

// ============================================
// ФУНКЦИИ СОХРАНЕНИЯ И УДАЛЕНИЯ
// ============================================
function savePhilosopherData() { ... }  // УЖЕ СОЗДАНА
function deletePhilosopher(philosopherName) { ... }  // ← ДОБАВИТЬ (код выше)

function saveConceptData() { 
    // ...
    // ✅ ДОБАВИТЬ: const id = generateId('concept');
}
function deleteConcept(conceptId) { ... }  // ← ДОБАВИТЬ (код выше)

function saveConnectionData() { 
    // ...
    // ✅ ДОБАВИТЬ: const existingLink = findConnection(source, target);
}

// ============================================
// ФУНКЦИИ ВЫБОРА НА ГРАФЕ
// ============================================
function initConnectionSearchFields(mode) { ... }         // ← ДОБАВИТЬ
function selectConceptOnGraph(type, mode) { ... }        // ← ДОБАВИТЬ
function handleGraphConceptSelection(conceptData, type, mode) { ... }  // ← ДОБАВИТЬ
function cancelGraphSelection() { ... }                  // ← ДОБАВИТЬ

// ============================================
// ФУНКЦИИ ОБНОВЛЕНИЯ ГРАФА
// ============================================
function updateGraphData() { ... }                       // ← ДОБАВИТЬ
function updateGraphVisualization() { ... }              // ← ДОБАВИТЬ
// addNodeToGraph, updateNodeOnGraph, addLinkToGraph, updateLinkOnGraph - УЖЕ СОЗДАНЫ
```

---

## 6. Чек-лист реальных изменений

### ✅ Новые функции для добавления:
- [ ] `generateId()` - после ModalContext
- [ ] `findConnection()` - после generateId()
- [ ] `getConceptConnections()` - после findConnection()
- [ ] `isConceptIsolated()` - после getConceptConnections()
- [ ] `getIsolatedConceptsAfterDeletion()` - после isConceptIsolated()
- [ ] `deleteConcept()` - после saveConceptData()
- [ ] `deletePhilosopher()` - после savePhilosopherData()
- [ ] `initConnectionSearchFields()` - секция работы с графом
- [ ] `selectConceptOnGraph()` - после initConnectionSearchFields()
- [ ] `handleGraphConceptSelection()` - после selectConceptOnGraph()
- [ ] `cancelGraphSelection()` - после handleGraphConceptSelection()
- [ ] `updateGraphData()` - секция работы с графом
- [ ] `updateGraphVisualization()` - после updateGraphData()

### ✅ Изменения в существующих функциях:
- [ ] В `openUniversalModal()` добавить вызов `initConnectionSearchFields()`
- [ ] В `closeUniversalModal()` добавить вызов `cancelGraphSelection()`
- [ ] В `saveConceptData()` добавить использование `generateId()`
- [ ] В `saveConnectionData()` добавить использование `findConnection()`

### ❌ НЕ НУЖНО менять:
- Все генераторы контента (там уже правильно используются прямые вызовы)
- savePhilosopherData() (там уже правильно используются прямые вызовы)

---

**Итого:** 13 новых функций + 4 изменения в существующих функциях = 17 действий.
