# Обработчики событий графа для унифицированной системы

## Изменения от старой системы к новой

### Замены констант и функций:

| Старое | Новое | Причина |
|--------|-------|---------|
| `editMode` | `ModalContext` + `window.graphSelectionContext` | Новая система контекста |
| `editMode.graphSelectionMode` | `window.graphSelectionContext.active` | Режим выбора на графе |
| `editMode.pendingConceptSelection` | `window.pendingConceptSelection` | Глобальная переменная для отложенного выбора |
| `openEditConceptModal()` | `openUniversalModal('concept', data, 'edit')` | Унифицированная система |
| `openEditConnectionModal()` | `openUniversalModal('connection', data, 'edit')` | Унифицированная система |
| `showDetailModal()` | `openUniversalModal('concept', data, 'view')` | Унифицированная система |

---

## Полный код исправленных обработчиков

```javascript
// ============================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ ОБРАБОТЧИКОВ
// ============================================

// Для отложенного выбора концепций (shift+клик)
window.pendingConceptSelection = [];

// ============================================
// ОПРЕДЕЛЕНИЕ ОБРАБОТЧИКОВ (функции)
// ============================================

// Обработка клика на узле с исправлением утечки таймера
let clickTimer = null;
let clickCount = 0;
let lastClickedNode = null;

function handleNodeClick(event, d) {
    event.stopPropagation();
    
    // Обработка shift+клик для редактирования узла
    if (event.shiftKey) {
        clickCount++;
        
        if (clickTimer) {
            clearTimeout(clickTimer);
            clickTimer = null;
        }
        
        if (clickCount === 1) {
            lastClickedNode = d;
            clickTimer = setTimeout(() => {
                // Shift+ОДИНАРНЫЙ клик
                
                // ✅ ИЗМЕНЕНИЕ: Проверка режима выбора на графе через window.graphSelectionContext
                if (window.graphSelectionContext && window.graphSelectionContext.active) {
                    // Режим выбора концепции для связи активен
                    handleGraphConceptSelection(d, window.graphSelectionContext.type, window.graphSelectionContext.mode);
                } 
                // ✅ ИЗМЕНЕНИЕ: Использование window.pendingConceptSelection вместо editMode
                else if (window.pendingConceptSelection.length > 0) {
                    const firstConceptId = window.pendingConceptSelection[0];
                    
                    // Второй клик на том же узле - редактирование концепции
                    if (firstConceptId === d.id) {
                        window.pendingConceptSelection = [];
                        node.classed('selected', false);
                        // ✅ ИЗМЕНЕНИЕ: Используем новую функцию
                        openUniversalModal('concept', d, 'edit');
                    } else {
                        // Второй клик на другом узле - редактирование связи между ними
                        window.pendingConceptSelection = [];
                        node.classed('selected', false);
                        
                        // ✅ ИЗМЕНЕНИЕ: Создаем объект связи для редактирования
                        const connectionData = {
                            source: firstConceptId,
                            target: d.id
                        };
                        openUniversalModal('connection', connectionData, 'edit');
                    }
                } else {
                    // Первый shift+клик - начинаем отложенный выбор
                    window.pendingConceptSelection = [d.id];
                    node.classed('selected', n => n.id === d.id);
                }
                
                clickCount = 0;
                clickTimer = null;
                lastClickedNode = null;
            }, 300);
        } else if (clickCount === 2) {
            // Shift+ДВОЙНОЙ клик - редактирование концепции
            window.pendingConceptSelection = [];
            node.classed('selected', false);
            // ✅ ИЗМЕНЕНИЕ: Используем новую функцию
            openUniversalModal('concept', d, 'edit');
            
            clickCount = 0;
            clickTimer = null;
            lastClickedNode = null;
        }
        return;
    }
    
    // ✅ ИЗМЕНЕНИЕ: Отменяем выбор если кликнули без shift
    if (window.pendingConceptSelection.length > 0) {
        window.pendingConceptSelection = [];
        node.classed('selected', false);
    }
    
    // Обычная логика клика (без shift)
    clickCount++;
    
    if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
    }
    
    if (clickCount === 1) {
        lastClickedNode = d;
        clickTimer = setTimeout(() => {
            // Одинарный клик - выделение узла с его связями
            if (event.ctrlKey || event.metaKey) {
                if (selectedNodes.has(lastClickedNode)) {
                    selectedNodes.delete(lastClickedNode);
                } else {
                    selectedNodes.add(lastClickedNode);
                }
            } else {
                const connectedToSelectedEdges = isNodeConnectedToSelectedEdges(lastClickedNode);
                if (connectedToSelectedEdges && selectedEdges.size > 0) {
                    if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                        selectedNodes.clear();
                    } else {
                        selectedNodes.clear();
                        selectedNodes.add(lastClickedNode);
                    }
                } else {
                    selectedEdges.clear();
                    if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                        selectedNodes.clear();
                    } else {
                        selectedNodes.clear();
                        selectedNodes.add(lastClickedNode);
                    }
                }
            }
            
            highlightCombined();
            clickCount = 0;
            clickTimer = null;
            lastClickedNode = null;
        }, 300);
    } else if (clickCount === 2) {
        // Двойной клик - детальная информация об узле
        // ✅ ИЗМЕНЕНИЕ: Используем новую функцию
        openUniversalModal('concept', d, 'view');
        clickCount = 0;
        clickTimer = null;
        lastClickedNode = null;
    }
}

function handleLinkClick(event, d) {
    event.stopPropagation();
    
    // Shift+клик - редактирование связи
    if (event.shiftKey) {
        // ✅ ИЗМЕНЕНИЕ: Создаем объект для редактирования связи
        const connectionData = {
            source: d.source,
            target: d.target,
            type: d.type,
            weight: d.weight,
            bidirectional: d.bidirectional,
            description: d.description
        };
        openUniversalModal('connection', connectionData, 'edit');
        return;
    }
    
    // Ctrl+клик - множественный выбор узлов/связей
    if (event.ctrlKey || event.metaKey) {
        if (selectedEdges.has(d)) {
            selectedEdges.delete(d);
        } else {
            selectedEdges.add(d);
        }
    } else {
        // Обычный клик - умная логика
        const connectedToSelectedNodes = isEdgeConnectedToSelectedNodes(d);
        
        if (connectedToSelectedNodes && selectedNodes.size > 0) {
            if (selectedEdges.size === 1 && selectedEdges.has(d)) {
                selectedEdges.clear();
            } else {
                selectedEdges.clear();
                selectedEdges.add(d);
            }
        } else {
            selectedNodes.clear();
            if (selectedEdges.size === 1 && selectedEdges.has(d)) {
                selectedEdges.clear();
            } else {
                selectedEdges.clear();
                selectedEdges.add(d);
            }
        }
    }
    
    highlightCombined();
}

// ============================================
// ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ ОБРАБОТЧИКОВ
// ============================================

function initGraphEventHandlers() {
    // Обработчики для связей
    link.on("click", handleLinkClick);
    
    // Обработчики для узлов
    node.on("click", handleNodeClick);
    
    // Обработчик для SVG (фон)
    svg.on("click.background", function(event) {
        // Клик "всплыл" до SVG без stopPropagation - это клик на фоне
        if (event.shiftKey) {
            // ✅ ИЗМЕНЕНИЕ: Shift+клик на фоне - создание новой концепции
            openUniversalModal('concept', null, 'edit');
        } else {
            // Обычный клик - сброс выделения
            resetHighlight();
            // ✅ ИЗМЕНЕНИЕ: Очистка отложенного выбора
            window.pendingConceptSelection = [];
            node.classed('selected', false);
        }
    });
}
```

---

## Дополнительные пояснения

### 1. Переменная window.pendingConceptSelection

**Где объявить:** В начале скрипта (после глобальных переменных, перед ModalContext)

```javascript
// ============================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ============================================

// ... существующие переменные ...

// Для отложенного выбора концепций (shift+клик)
window.pendingConceptSelection = [];
```

**Зачем нужна:** Позволяет создавать связи между концепциями через shift+клик:
1. Shift+клик на первую концепцию → запоминается в массиве
2. Shift+клик на вторую концепцию → открывается форма создания связи между ними

---

### 2. Режим выбора на графе (window.graphSelectionContext)

Эта переменная уже создаётся в функции `selectConceptOnGraph()`:

```javascript
window.graphSelectionContext = {
    active: true,
    type: 'source' | 'target',
    mode: 'edit' | 'view'
};
```

**Проверка активности:**
```javascript
if (window.graphSelectionContext && window.graphSelectionContext.active) {
    // Режим выбора активен
}
```

---

### 3. Создание объектов данных для связей

При shift+клике на связь создаём полный объект:

```javascript
const connectionData = {
    source: d.source,        // объект или ID
    target: d.target,        // объект или ID
    type: d.type,           // тип связи
    weight: d.weight,       // вес связи
    bidirectional: d.bidirectional,  // двунаправленная
    description: d.description       // описание
};
```

При создании новой связи через shift+клик на двух узлах:

```javascript
const connectionData = {
    source: firstConceptId,   // ID первой концепции
    target: d.id             // ID второй концепции
};
```

---

## Сравнительная таблица изменений

### Shift+клик на узле (одинарный)

| Сценарий | Старое | Новое |
|----------|--------|-------|
| Режим выбора на графе активен | `editMode.graphSelectionMode` → `handleConceptSelection()` | `window.graphSelectionContext.active` → `handleGraphConceptSelection()` |
| Есть отложенный выбор (1-я концепция) | `editMode.pendingConceptSelection.length > 0` | `window.pendingConceptSelection.length > 0` |
| Клик на ту же концепцию | `openEditConceptModal(d.id)` | `openUniversalModal('concept', d, 'edit')` |
| Клик на другую концепцию | `openEditConnectionModal(first, d.id)` | `openUniversalModal('connection', {source, target}, 'edit')` |
| Первый клик | `editMode.pendingConceptSelection = [d.id]` | `window.pendingConceptSelection = [d.id]` |

### Shift+двойной клик на узле

| Старое | Новое |
|--------|-------|
| `openEditConceptModal(d.id)` | `openUniversalModal('concept', d, 'edit')` |

### Двойной клик на узле

| Старое | Новое |
|--------|-------|
| `showDetailModal(d)` | `openUniversalModal('concept', d, 'view')` |

### Shift+клик на связи

| Старое | Новое |
|--------|-------|
| `openEditConnectionModal(d.source.id, d.target.id)` | `openUniversalModal('connection', connectionData, 'edit')` |

### Shift+клик на фоне

| Старое | Новое |
|--------|-------|
| `openEditConceptModal()` | `openUniversalModal('concept', null, 'edit')` |

---

## Проверочный чек-лист

После замены обработчиков проверьте следующие сценарии:

### ✅ Работа с узлами:
- [ ] Двойной клик на узле → открывается просмотр концепции
- [ ] Shift+двойной клик на узле → открывается редактирование концепции
- [ ] Shift+клик на узле → узел выделяется (первый выбор)
- [ ] Shift+клик на том же узле → открывается редактирование концепции
- [ ] Shift+клик на первом узле, затем на втором → открывается создание связи

### ✅ Работа со связями:
- [ ] Shift+клик на связи → открывается редактирование связи

### ✅ Работа с фоном:
- [ ] Shift+клик на фоне → открывается создание новой концепции
- [ ] Клик на фоне (без shift) → сброс выделения

### ✅ Режим выбора на графе:
- [ ] Кнопка "🎯 Выбрать на графе" активирует режим
- [ ] Клик на узле в режиме выбора → концепция выбирается для связи
- [ ] Кнопка "Отмена" отменяет режим выбора

### ✅ Отмена выбора:
- [ ] Клик без shift отменяет window.pendingConceptSelection
- [ ] Закрытие модального окна очищает состояние

---

## Итого

**Изменено:** 8 вызовов функций, 1 новая переменная

**Результат:** Обработчики полностью совместимы с новой унифицированной системой модальных окон.
