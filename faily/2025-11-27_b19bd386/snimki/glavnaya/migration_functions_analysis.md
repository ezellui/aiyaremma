# Миграция функций из старой системы в унифицированную модальную систему

## Анализ функций и констант

### ✅ ФУНКЦИИ, КОТОРЫЕ МОЖНО БЕЗОПАСНО УДАЛИТЬ

Эти функции **полностью заменены** новыми аналогами в унифицированной системе:

| Старая функция | Новый аналог | Причина замены |
|----------------|--------------|----------------|
| `closeEditConnectionModal()` | `closeUniversalModal()` | Единое окно для всех сущностей |
| `closeEditConceptModal()` | `closeUniversalModal()` | Единое окно для всех сущностей |
| `closeEditPhilosopherModal()` | `closeUniversalModal()` | Единое окно для всех сущностей |
| `saveConnection()` | `saveConnectionData()` | Более универсальная реализация |
| `saveConcept()` | `saveConceptData()` | Более универсальная реализация |
| `selectConnectionConcept()` | `selectConnectionEditConcept()` | Новая система с разделением view/edit |
| `handleConnectionConceptSearch()` | `handleConnectionEditSearch()` | Новая система с разделением view/edit |

**Действие:** Эти функции можно **удалить** из кода.

---

### 🔄 ФУНКЦИИ, ИНТЕГРИРОВАННЫЕ В НОВУЮ СИСТЕМУ

Эти функции не существуют как отдельные, но их логика **встроена** в генераторы контента:

| Старая функция | Где теперь логика | Комментарий |
|----------------|-------------------|-------------|
| `loadConceptConnections()` | `generateConceptEditContent()` | Встроено в генерацию контента |
| `loadPhilosopherConcepts()` | `generatePhilosopherEditContent()` | Встроено в генерацию контента |
| `addConnectionFromConcept()` | `createNewConnectionForConcept()` | Новая функция в унифицированной системе |
| `addConceptFromPhilosopher()` | `createNewConceptForPhilosopher()` | Новая функция в унифицированной системе |
| `handleConceptSelection()` | `selectConnectionEditConcept()` | Логика выбора концепции |
| `deleteConnectionFromList()` | Вызов `deleteConnection()` | Прямой вызов функции удаления |
| `deleteConceptFromList()` | Вызов `deleteConcept()` | Прямой вызов функции удаления |

**Действие:** Эти функции можно **удалить**, их функциональность уже реализована.

---

### 💾 ПОЛЕЗНЫЕ УТИЛИТЫ - НУЖНО СОХРАНИТЬ И ДОРАБОТАТЬ

Эти функции являются полезными утилитами, которые стоит **сохранить**, но возможно адаптировать:

#### 1. `generateId()` - СОХРАНИТЬ

```javascript
/**
 * Генерация уникального ID
 */
function generateId(prefix = 'item') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

**Использование:** В `saveConceptData()`, `saveConnectionData()` и т.д.

---

#### 2. `findConceptById(id)` - МОЖНО ЗАМЕНИТЬ

```javascript
// Старая функция
function findConceptById(id) {
    return nodes.find(n => n.id === id);
}

// Можно везде заменить на:
nodes.find(n => n.id === id)
```

**Действие:** Можно **удалить**, заменив все вызовы на прямое использование `nodes.find()`.

---

#### 3. `findPhilosopherByName(name)` - МОЖНО ЗАМЕНИТЬ

```javascript
// Старая функция
function findPhilosopherByName(name) {
    return philosophers.find(p => p.nameRu === name);
}

// Можно везде заменить на:
philosophers.find(p => p.nameRu === name)
```

**Действие:** Можно **удалить**, заменив все вызовы на прямое использование `philosophers.find()`.

---

#### 4. `findConnection(sourceId, targetId)` - СОХРАНИТЬ И ДОРАБОТАТЬ

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

**Использование:** Полезна в `saveConnectionData()` для проверки существующих связей.

---

#### 5. `getConceptConnections(conceptId)` - СОХРАНИТЬ

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

**Использование:** Полезна для анализа связей концепции.

---

#### 6. `isConceptIsolated(conceptId)` - СОХРАНИТЬ

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

**Использование:** Полезна перед удалением концепции.

---

#### 7. `getIsolatedConceptsAfterDeletion(philosopherName)` - СОХРАНИТЬ

```javascript
/**
 * Получение концепций, которые станут изолированными после удаления философа
 * @param {string} philosopherName - Имя философа
 * @returns {Array} - Массив изолированных концепций
 */
function getIsolatedConceptsAfterDeletion(philosopherName) {
    const philosopherConcepts = nodes.filter(n => n.concept === philosopherName);
    const philosopherConceptIds = philosopherConcepts.map(c => c.id);
    
    const isolated = [];
    
    philosopherConcepts.forEach(concept => {
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

**Использование:** При удалении философа, чтобы предупредить об изолированных концепциях.

---

### 🎯 ФУНКЦИИ ВЫБОРА НА ГРАФЕ - НУЖНО АДАПТИРОВАТЬ

Эти функции предоставляют ценную функциональность **выбора концепций прямо на графе**. Их стоит **сохранить и адаптировать** к новой системе:

#### 1. `initConnectionSearchFields()` - АДАПТИРОВАТЬ

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

---

#### 2. `selectConceptOnGraph(type, mode)` - АДАПТИРОВАТЬ

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

---

#### 3. `handleGraphConceptSelection(conceptData, type, mode)` - СОЗДАТЬ НОВУЮ

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

---

#### 4. `cancelGraphSelection()` - СОХРАНИТЬ

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

**Действие:** Эти 4 функции нужно **сохранить и интегрировать** в новую систему.

---

### 📊 ФУНКЦИИ ОБНОВЛЕНИЯ ГРАФА - АДАПТИРОВАТЬ

#### 1. `updateGraphData()` - МОЖНО УПРОСТИТЬ

Старая версия была очень сложной. В новой системе можно упростить:

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

---

#### 2. `updateGraphVisualization()` - УПРОСТИТЬ

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

---

### 🗑️ КОНСТАНТА editMode - УДАЛИТЬ

```javascript
// Старая константа
let editMode = {
    active: false,
    type: null, // 'philosopher', 'concept', 'connection'
    data: null
};

// Заменена на
ModalContext = {
    currentEntity: null,
    currentMode: 'view',
    currentData: null,
    editState: {}
};
```

**Действие:** Удалить `editMode`, везде заменить на `ModalContext`.

---

## Итоговый чек-лист миграции

### ✅ Удалить полностью:
- [ ] `closeEditConnectionModal()`
- [ ] `closeEditConceptModal()`
- [ ] `closeEditPhilosopherModal()`
- [ ] `saveConnection()`
- [ ] `saveConcept()`
- [ ] `selectConnectionConcept()`
- [ ] `handleConnectionConceptSearch()`
- [ ] `loadConceptConnections()`
- [ ] `loadPhilosopherConcepts()`
- [ ] `addConnectionFromConcept()`
- [ ] `addConceptFromPhilosopher()`
- [ ] `handleConceptSelection()`
- [ ] `deleteConnectionFromList()`
- [ ] `deleteConceptFromList()`
- [ ] `findConceptById()` (заменить на `nodes.find()`)
- [ ] `findPhilosopherByName()` (заменить на `philosophers.find()`)
- [ ] Константа `editMode`

### 💾 Сохранить и доработать:
- [ ] `generateId()` - сохранить как есть
- [ ] `findConnection()` - сохранить, доработать
- [ ] `getConceptConnections()` - сохранить
- [ ] `isConceptIsolated()` - сохранить
- [ ] `getIsolatedConceptsAfterDeletion()` - сохранить
- [ ] `updateGraphData()` - упростить
- [ ] `updateGraphVisualization()` - упростить

### 🎯 Адаптировать к новой системе:
- [ ] `initConnectionSearchFields()` - адаптировать для view/edit
- [ ] `selectConceptOnGraph()` - адаптировать
- [ ] `cancelGraphSelection()` - сохранить как есть
- [ ] Создать `handleGraphConceptSelection()` - новая функция

### 🆕 Уже реализовано в новой системе:
- [x] `createNewConnectionForConcept()`
- [x] `createNewConceptForPhilosopher()`
- [x] `selectConnectionEditConcept()`
- [x] `handleConnectionEditSearch()`
- [x] `saveConnectionData()`
- [x] `saveConceptData()`
- [x] `savePhilosopherData()`
- [x] `closeUniversalModal()`

---

## Рекомендации по порядку миграции

1. **Первый этап:** Удалить очевидно ненужные функции (close..., save..., старые поисковые)
2. **Второй этап:** Заменить `findConceptById()` и `findPhilosopherByName()` на прямые вызовы
3. **Третий этап:** Сохранить утилиты (generateId, findConnection, getConceptConnections и т.д.)
4. **Четвертый этап:** Адаптировать функции выбора на графе
5. **Пятый этап:** Упростить функции обновления графа
6. **Шестой этап:** Удалить константу `editMode`, заменив на `ModalContext`

---

## Важное замечание

Функциональность **выбора концепций на графе** (`selectConceptOnGraph` и связанные) - это очень удобная фича, которую стоит **обязательно сохранить** и интегрировать в новую систему. Она значительно улучшает UX при создании связей.
