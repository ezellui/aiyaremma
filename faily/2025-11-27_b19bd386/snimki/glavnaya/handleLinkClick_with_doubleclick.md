# Обновленный обработчик handleLinkClick с двойным кликом

## Добавленная функциональность

**Двойной клик на связи** → открывает окно **просмотра** связи (режим view)
**Shift+клик на связи** → открывает окно **редактирования** связи (режим edit)

---

## Полный обновленный код handleLinkClick

```javascript
// Обработка клика на связи с поддержкой двойного клика
let linkClickTimer = null;
let linkClickCount = 0;
let lastClickedLink = null;

function handleLinkClick(event, d) {
    event.stopPropagation();
    
    // Shift+клик - редактирование связи
    if (event.shiftKey) {
        // Создаем объект для редактирования связи
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
    
    // Обработка одинарного/двойного клика
    linkClickCount++;
    
    if (linkClickTimer) {
        clearTimeout(linkClickTimer);
        linkClickTimer = null;
    }
    
    if (linkClickCount === 1) {
        lastClickedLink = d;
        linkClickTimer = setTimeout(() => {
            // Одинарный клик - выделение связи
            
            // Ctrl+клик - множественный выбор
            if (event.ctrlKey || event.metaKey) {
                if (selectedEdges.has(lastClickedLink)) {
                    selectedEdges.delete(lastClickedLink);
                } else {
                    selectedEdges.add(lastClickedLink);
                }
            } else {
                // Обычный клик - умная логика выделения
                const connectedToSelectedNodes = isEdgeConnectedToSelectedNodes(lastClickedLink);
                
                if (connectedToSelectedNodes && selectedNodes.size > 0) {
                    if (selectedEdges.size === 1 && selectedEdges.has(lastClickedLink)) {
                        selectedEdges.clear();
                    } else {
                        selectedEdges.clear();
                        selectedEdges.add(lastClickedLink);
                    }
                } else {
                    selectedNodes.clear();
                    if (selectedEdges.size === 1 && selectedEdges.has(lastClickedLink)) {
                        selectedEdges.clear();
                    } else {
                        selectedEdges.clear();
                        selectedEdges.add(lastClickedLink);
                    }
                }
            }
            
            highlightCombined();
            linkClickCount = 0;
            linkClickTimer = null;
            lastClickedLink = null;
        }, 300);
    } else if (linkClickCount === 2) {
        // ✅ НОВОЕ: Двойной клик - просмотр связи
        const connectionData = {
            source: d.source,
            target: d.target,
            type: d.type,
            weight: d.weight,
            bidirectional: d.bidirectional,
            description: d.description
        };
        openUniversalModal('connection', connectionData, 'view');
        
        linkClickCount = 0;
        linkClickTimer = null;
        lastClickedLink = null;
    }
}
```

---

## Что изменилось

### 1. Добавлены переменные для отслеживания кликов на связях

```javascript
let linkClickTimer = null;      // Таймер для определения двойного клика
let linkClickCount = 0;         // Счетчик кликов
let lastClickedLink = null;     // Последняя кликнутая связь
```

**Где объявить:** Рядом с аналогичными переменными для узлов (после `let lastClickedNode = null;`)

### 2. Логика обработки кликов

**Shift+клик** (без задержки):
```javascript
if (event.shiftKey) {
    // Сразу открываем редактирование
    openUniversalModal('connection', connectionData, 'edit');
    return;
}
```

**Одинарный клик** (задержка 300мс):
```javascript
if (linkClickCount === 1) {
    linkClickTimer = setTimeout(() => {
        // Логика выделения связи
        // Ctrl+клик - множественное выделение
        // Обычный клик - умное выделение
        highlightCombined();
    }, 300);
}
```

**Двойной клик** (в течение 300мс):
```javascript
else if (linkClickCount === 2) {
    // Открываем просмотр связи
    openUniversalModal('connection', connectionData, 'view');
}
```

---

## Полный обновленный файл обработчиков

```javascript
// ============================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ ОБРАБОТЧИКОВ
// ============================================

// Для отложенного выбора концепций (shift+клик)
window.pendingConceptSelection = [];

// ============================================
// ОПРЕДЕЛЕНИЕ ОБРАБОТЧИКОВ (функции)
// ============================================

// Переменные для обработки кликов на узлах
let clickTimer = null;
let clickCount = 0;
let lastClickedNode = null;

// ✅ НОВОЕ: Переменные для обработки кликов на связях
let linkClickTimer = null;
let linkClickCount = 0;
let lastClickedLink = null;

// Обработка клика на узле
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
                
                if (window.graphSelectionContext && window.graphSelectionContext.active) {
                    // Режим выбора концепции для связи активен
                    handleGraphConceptSelection(d, window.graphSelectionContext.type, window.graphSelectionContext.mode);
                } 
                else if (window.pendingConceptSelection.length > 0) {
                    const firstConceptId = window.pendingConceptSelection[0];
                    
                    // Второй клик на том же узле - редактирование концепции
                    if (firstConceptId === d.id) {
                        window.pendingConceptSelection = [];
                        node.classed('selected', false);
                        openUniversalModal('concept', d, 'edit');
                    } else {
                        // Второй клик на другом узле - редактирование связи между ними
                        window.pendingConceptSelection = [];
                        node.classed('selected', false);
                        
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
            openUniversalModal('concept', d, 'edit');
            
            clickCount = 0;
            clickTimer = null;
            lastClickedNode = null;
        }
        return;
    }
    
    // Отменяем выбор если кликнули без shift
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
        openUniversalModal('concept', d, 'view');
        clickCount = 0;
        clickTimer = null;
        lastClickedNode = null;
    }
}

// ✅ ОБНОВЛЕНО: Обработка клика на связи с поддержкой двойного клика
function handleLinkClick(event, d) {
    event.stopPropagation();
    
    // Shift+клик - редактирование связи
    if (event.shiftKey) {
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
    
    // Обработка одинарного/двойного клика
    linkClickCount++;
    
    if (linkClickTimer) {
        clearTimeout(linkClickTimer);
        linkClickTimer = null;
    }
    
    if (linkClickCount === 1) {
        lastClickedLink = d;
        linkClickTimer = setTimeout(() => {
            // Одинарный клик - выделение связи
            
            // Ctrl+клик - множественный выбор
            if (event.ctrlKey || event.metaKey) {
                if (selectedEdges.has(lastClickedLink)) {
                    selectedEdges.delete(lastClickedLink);
                } else {
                    selectedEdges.add(lastClickedLink);
                }
            } else {
                // Обычный клик - умная логика выделения
                const connectedToSelectedNodes = isEdgeConnectedToSelectedNodes(lastClickedLink);
                
                if (connectedToSelectedNodes && selectedNodes.size > 0) {
                    if (selectedEdges.size === 1 && selectedEdges.has(lastClickedLink)) {
                        selectedEdges.clear();
                    } else {
                        selectedEdges.clear();
                        selectedEdges.add(lastClickedLink);
                    }
                } else {
                    selectedNodes.clear();
                    if (selectedEdges.size === 1 && selectedEdges.has(lastClickedLink)) {
                        selectedEdges.clear();
                    } else {
                        selectedEdges.clear();
                        selectedEdges.add(lastClickedLink);
                    }
                }
            }
            
            highlightCombined();
            linkClickCount = 0;
            linkClickTimer = null;
            lastClickedLink = null;
        }, 300);
    } else if (linkClickCount === 2) {
        // ✅ НОВОЕ: Двойной клик - просмотр связи
        const connectionData = {
            source: d.source,
            target: d.target,
            type: d.type,
            weight: d.weight,
            bidirectional: d.bidirectional,
            description: d.description
        };
        openUniversalModal('connection', connectionData, 'view');
        
        linkClickCount = 0;
        linkClickTimer = null;
        lastClickedLink = null;
    }
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
            // Shift+клик на фоне - создание новой концепции
            openUniversalModal('concept', null, 'edit');
        } else {
            // Обычный клик - сброс выделения
            resetHighlight();
            window.pendingConceptSelection = [];
            node.classed('selected', false);
        }
    });
}
```

---

## Таблица взаимодействий со связями

| Действие | Результат | Режим |
|----------|-----------|-------|
| **Одинарный клик** | Выделение связи | - |
| **Двойной клик** | 🆕 Просмотр связи | view |
| **Shift+клик** | Редактирование связи | edit |
| **Ctrl+клик** | Множественное выделение | - |

---

## Таблица взаимодействий с узлами (для сравнения)

| Действие | Результат | Режим |
|----------|-----------|-------|
| **Одинарный клик** | Выделение узла | - |
| **Двойной клик** | Просмотр концепции | view |
| **Shift+клик (одинарный)** | Начало выбора для связи | - |
| **Shift+клик на том же узле** | Редактирование концепции | edit |
| **Shift+клик на другом узле** | Создание связи | edit |
| **Shift+двойной клик** | Редактирование концепции | edit |
| **Ctrl+клик** | Множественное выделение | - |

---

## Проверочный чек-лист

После обновления проверьте:

### ✅ Работа со связями:
- [ ] **Одинарный клик на связи** → связь выделяется
- [ ] **Двойной клик на связи** → открывается просмотр связи (новое!)
- [ ] **Shift+клик на связи** → открывается редактирование связи
- [ ] **Ctrl+клик на связи** → множественное выделение

### ✅ Работа с узлами (не должна сломаться):
- [ ] Двойной клик на узле → просмотр концепции
- [ ] Shift+двойной клик → редактирование концепции
- [ ] Shift+клик на двух узлах → создание связи

### ✅ Отсутствие конфликтов:
- [ ] Таймеры узлов и связей не пересекаются
- [ ] Клики обрабатываются корректно

---

## Итого изменений

**Добавлено:**
- 3 новые переменные для обработки кликов на связях
- Логика двойного клика для связей (аналогично узлам)
- Вызов `openUniversalModal('connection', data, 'view')` при двойном клике

**Результат:** Теперь связи имеют полноценную поддержку двойного клика для просмотра, как и узлы!
