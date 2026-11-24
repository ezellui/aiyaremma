# Анализ совместимости функций старой системы с новой унифицированной системой

## Обзор

Проверяем 13 функций из старой системы, вызываемых в новой. Для каждой определяем:
- ✅ Совместима без изменений
- 🔧 Требует небольших изменений
- 🆕 Требует полной переработки
- ❌ Уже создана новая версия

---

## 1. toggleConnectionDescription

**Статус:** ✅ Совместима без изменений

**Что делает:** Переключает видимость описания отдельной связи

**Текущая реализация (старая система):**
```javascript
function toggleConnectionDescription(descId) {
    const descElement = document.getElementById(`desc-${descId}`);
    const toggleBtn = event.target;
    
    if (descElement.classList.contains('show')) {
        descElement.classList.remove('show');
        toggleBtn.classList.remove('expanded');
    } else {
        descElement.classList.add('show');
        toggleBtn.classList.add('expanded');
    }
}
```

**Анализ:** Функция работает с ID элементов, которые генерируются одинаково в обеих системах (`desc-${conceptId1}-${conceptId2}`). 

**Вывод:** ✅ Не требует изменений.

---

## 2. toggleAllConnectionDescriptions

**Статус:** 🔧 Требует небольших изменений для универсальности

**Что делает:** Раскрывает/сворачивает все описания связей в текущем окне

**Текущая реализация (старая система):**
```javascript
let allConnectionDescriptionsExpanded = false;

function toggleAllConnectionDescriptions(conceptId) {
    const modal = document.getElementById('detailModal');
    const descriptions = modal.querySelectorAll('.connection-description');
    const toggleButtons = modal.querySelectorAll('.connection-toggle');
    const toggleAllBtn = event.target;
    
    allConnectionDescriptionsExpanded = !allConnectionDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allConnectionDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allConnectionDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allConnectionDescriptionsExpanded ? 
        '▲ Свернуть все описания связей' : 
        '▼ Развернуть все описания связей';
}
```

**Проблема:** Хардкод `#detailModal` - не будет работать для `#universalModal`

**Исправленная версия:**
```javascript
let allConnectionDescriptionsExpanded = false;

function toggleAllConnectionDescriptions(conceptId) {
    // 🔧 ИЗМЕНЕНИЕ: Ищем модальное окно универсально
    const modal = document.querySelector('.detail-modal.show');
    if (!modal) return;
    
    const descriptions = modal.querySelectorAll('.connection-description');
    const toggleButtons = modal.querySelectorAll('.connection-toggle');
    const toggleAllBtn = event.target;
    
    allConnectionDescriptionsExpanded = !allConnectionDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allConnectionDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allConnectionDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allConnectionDescriptionsExpanded ? 
        '▲ Свернуть все описания связей' : 
        '▼ Развернуть все описания связей';
}
```

**Вывод:** 🔧 Заменить `getElementById('detailModal')` на `querySelector('.detail-modal.show')`

---

## 3. toggleSubsection

**Статус:** ✅ Совместима без изменений

**Что делает:** Сворачивает/разворачивает подсекции (внутренние/внешние связи)

**Текущая реализация (старая система):**
```javascript
function toggleSubsection(sectionId) {
    const content = document.getElementById(`content-${sectionId}`);
    const toggle = document.getElementById(`toggle-${sectionId}`);
    
    if (content.classList.contains('show')) {
        content.classList.remove('show');
        toggle.textContent = '▼';
    } else {
        content.classList.add('show');
        toggle.textContent = '▲';
    }
}
```

**Анализ:** Работает с ID элементов, которые генерируются одинаково в обеих системах.

**Вывод:** ✅ Не требует изменений.

---

## 4. gotoNodeFromModal

**Статус:** 🔧 Требует изменений для закрытия правильного окна

**Что делает:** Переходит к узлу на графе, закрывая модальное окно

**Текущая реализация (старая система):**
```javascript
function gotoNodeFromModal(nodeId) {
    closeDetailModal();
    
    const node = simulation.nodes().find(n => n.id === nodeId);
    if (!node) return;
    
    // Центрируем камеру на узле
    const scale = 1.5;
    const x = -node.x * scale + width / 2;
    const y = -node.y * scale + height / 2;
    
    svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity.translate(x, y).scale(scale));
    
    // Подсвечиваем узел
    d3.selectAll('.node')
        .filter(d => d.id === nodeId)
        .select('circle')
        .transition()
        .duration(300)
        .attr('r', 25)
        .transition()
        .duration(300)
        .attr('r', 18);
}
```

**Проблема:** Вызывает `closeDetailModal()` вместо `closeUniversalModal()`

**Исправленная версия:**
```javascript
function gotoNodeFromModal(nodeId) {
    // 🔧 ИЗМЕНЕНИЕ: Используем новую функцию закрытия
    closeUniversalModal();
    
    const node = simulation.nodes().find(n => n.id === nodeId);
    if (!node) return;
    
    // Центрируем камеру на узле
    const scale = 1.5;
    const x = -node.x * scale + width / 2;
    const y = -node.y * scale + height / 2;
    
    svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity.translate(x, y).scale(scale));
    
    // Подсвечиваем узел
    d3.selectAll('.node')
        .filter(d => d.id === nodeId)
        .select('circle')
        .transition()
        .duration(300)
        .attr('r', 25)
        .transition()
        .duration(300)
        .attr('r', 18);
}
```

**Вывод:** 🔧 Заменить `closeDetailModal()` на `closeUniversalModal()`

---

## 5. showAllConcepts

**Статус:** ✅ Совместима без изменений

**Что делает:** Показывает все концепции в рубрике (раскрывает скрытые)

**Текущая реализация (старая система):**
```javascript
function showAllConcepts(rubricId, currentConceptId) {
    const relatedConcepts = nodes.filter(n => {
        const nRubrics = conceptToRubrics[n.id] || [];
        return nRubrics.includes(rubricId) && n.id !== currentConceptId;
    });
    
    const container = document.getElementById(`show-all-${rubricId}-container`);
    const button = document.getElementById(`show-all-${rubricId}`);
    
    container.innerHTML = relatedConcepts.map(c => `
        <div class="concept-item" onclick="showDetailModal(nodes.find(n => n.id === '${c.id}'));">
            <div class="concept-color" style="background: ${philosopherConcepts[c.concept].color}"></div>
            <div class="concept-name">${c.label}</div>
            <div class="concept-philosopher">${c.concept}</div>
        </div>
    `).join('');
    
    button.style.display = 'none';
}
```

**Проблема:** Вызывает `showDetailModal()` - но это уже адаптер к новой системе!

**Анализ:** Если мы создали адаптеры (как планировалось), то `showDetailModal()` будет вызывать `openUniversalModal()`. Если адаптеры не созданы, нужно исправить.

**Вариант 1 (если есть адаптеры):** ✅ Не требует изменений

**Вариант 2 (если нет адаптеров):** 🔧 Заменить вызовы

**Исправленная версия (если нет адаптеров):**
```javascript
function showAllConcepts(rubricId, currentConceptId) {
    const relatedConcepts = nodes.filter(n => {
        const nRubrics = conceptToRubrics[n.id] || [];
        return nRubrics.includes(rubricId) && n.id !== currentConceptId;
    });
    
    const container = document.getElementById(`show-all-${rubricId}-container`);
    const button = document.getElementById(`show-all-${rubricId}`);
    
    container.innerHTML = relatedConcepts.map(c => `
        <div class="concept-item" onclick="openUniversalModal('concept', nodes.find(n => n.id === '${c.id}'), 'view');">
            <div class="concept-color" style="background: ${philosopherConcepts[c.concept].color}"></div>
            <div class="concept-name">${c.label}</div>
            <div class="concept-philosopher">${c.concept}</div>
        </div>
    `).join('');
    
    button.style.display = 'none';
}
```

**Вывод:** 🔧 Если нет адаптеров - заменить `showDetailModal` на `openUniversalModal`

---

## 6. togglePhilosopherConceptDescription

**Статус:** ✅ Совместима без изменений

**Что делает:** Переключает описание концепции в окне философа

**Текущая реализация (старая система):**
```javascript
function togglePhilosopherConceptDescription(conceptId) {
    const descElement = document.getElementById(`phil-concept-desc-${conceptId}`);
    const toggleBtn = event.target;
    
    if (descElement.classList.contains('show')) {
        descElement.classList.remove('show');
        toggleBtn.classList.remove('expanded');
    } else {
        descElement.classList.add('show');
        toggleBtn.classList.add('expanded');
    }
}
```

**Анализ:** Работает с префиксом `phil-concept-desc-`, который одинаков в обеих системах.

**Вывод:** ✅ Не требует изменений.

---

## 7. toggleAllPhilosopherConceptDescriptions

**Статус:** 🔧 Требует небольших изменений

**Что делает:** Раскрывает/сворачивает все описания концепций философа

**Текущая реализация (старая система):**
```javascript
let allPhilosopherConceptDescriptionsExpanded = false;

function toggleAllPhilosopherConceptDescriptions() {
    const modal = document.getElementById('philosopherDetailModal');
    const descriptions = modal.querySelectorAll('.concept-extended-desc');
    const toggleButtons = modal.querySelectorAll('.toggle-concept-desc-btn');
    const toggleAllBtn = event.target;
    
    allPhilosopherConceptDescriptionsExpanded = !allPhilosopherConceptDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allPhilosopherConceptDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allPhilosopherConceptDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allPhilosopherConceptDescriptionsExpanded ? 
        '▲ Свернуть все описания концепций' : 
        '▼ Развернуть все описания концепций';
}
```

**Проблема:** Хардкод `#philosopherDetailModal` - теперь используется `#universalModal`

**Исправленная версия:**
```javascript
let allPhilosopherConceptDescriptionsExpanded = false;

function toggleAllPhilosopherConceptDescriptions() {
    // 🔧 ИЗМЕНЕНИЕ: Ищем модальное окно универсально
    const modal = document.querySelector('.detail-modal.show');
    if (!modal) return;
    
    const descriptions = modal.querySelectorAll('.concept-extended-desc');
    const toggleButtons = modal.querySelectorAll('.toggle-concept-desc-btn');
    const toggleAllBtn = event.target;
    
    allPhilosopherConceptDescriptionsExpanded = !allPhilosopherConceptDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allPhilosopherConceptDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allPhilosopherConceptDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allPhilosopherConceptDescriptionsExpanded ? 
        '▲ Свернуть все описания концепций' : 
        '▼ Развернуть все описания концепций';
}
```

**Вывод:** 🔧 Заменить `getElementById('philosopherDetailModal')` на `querySelector('.detail-modal.show')`

---

## 8. toggleAllPhilosopherConnectionDescriptions

**Статус:** 🔧 Требует небольших изменений

**Что делает:** Раскрывает/сворачивает все описания связей в окне философа

**Исправленная версия:**
```javascript
let allPhilosopherConnectionDescriptionsExpanded = false;

function toggleAllPhilosopherConnectionDescriptions() {
    // 🔧 ИЗМЕНЕНИЕ: Ищем модальное окно универсально
    const modal = document.querySelector('.detail-modal.show');
    if (!modal) return;
    
    const descriptions = modal.querySelectorAll('.connection-description');
    const toggleButtons = modal.querySelectorAll('.connection-toggle');
    const toggleAllBtn = event.target;
    
    allPhilosopherConnectionDescriptionsExpanded = !allPhilosopherConnectionDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allPhilosopherConnectionDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allPhilosopherConnectionDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allPhilosopherConnectionDescriptionsExpanded ? 
        '▲ Свернуть все описания связей' : 
        '▼ Развернуть все описания связей';
}
```

**Вывод:** 🔧 Заменить хардкод ID на универсальный селектор

---

## 9. deletePhilosopher

**Статус:** ❌ УЖЕ создана новая версия

**Анализ:** Мы создали новую версию в предыдущем документе с использованием `getIsolatedConceptsAfterDeletion()` и `closeUniversalModal()`.

**Вывод:** ❌ Использовать новую версию из `functions_integration_corrected.md`

---

## 10. deleteConcept

**Статус:** ❌ УЖЕ создана новая версия

**Анализ:** Мы создали новую версию в предыдущем документе с использованием `getConceptConnections()` и `closeUniversalModal()`.

**Вывод:** ❌ Использовать новую версию из `functions_integration_corrected.md`

---

## 11. deleteConnection

**Статус:** 🆕 Требует создания новой версии

**Что делает:** Удаляет связь между концепциями

**Старая версия (если была):**
```javascript
function deleteConnection(sourceId, targetId) {
    // ... старая логика ...
}
```

**НОВАЯ версия для унифицированной системы:**

```javascript
/**
 * Удаление связи между концепциями
 * @param {string} sourceId - ID начальной концепции (опционально)
 * @param {string} targetId - ID конечной концепции (опционально)
 */
function deleteConnection(sourceId = null, targetId = null) {
    // Если ID не переданы, берем из текущего контекста модального окна
    if (!sourceId || !targetId) {
        const originalData = ModalContext.currentData;
        if (!originalData) {
            alert('Не удалось определить связь для удаления');
            return;
        }
        sourceId = originalData.source.id || originalData.source;
        targetId = originalData.target.id || originalData.target;
    }
    
    // Находим связь
    const connection = findConnection(sourceId, targetId, true);
    
    if (!connection) {
        alert('Связь не найдена');
        return;
    }
    
    const srcNode = nodes.find(n => n.id === sourceId);
    const tgtNode = nodes.find(n => n.id === targetId);
    
    const confirmMessage = `Удалить связь между концепциями "${srcNode?.label}" и "${tgtNode?.label}"?`;
    const confirmed = confirm(confirmMessage);
    
    if (!confirmed) return;
    
    // Удаляем из links
    const linkIndex = links.indexOf(connection);
    if (linkIndex !== -1) {
        links.splice(linkIndex, 1);
    }
    
    // Удаляем из connections
    const srcId = connection.source.id || connection.source;
    const tgtId = connection.target.id || connection.target;
    const connIndex = connections.findIndex(c => 
        (c.from === srcId && c.to === tgtId) || 
        (c.from === tgtId && c.to === srcId)
    );
    
    if (connIndex !== -1) {
        connections.splice(connIndex, 1);
    }
    
    // Обновляем граф
    updateGraphData();
    
    // Закрываем модальное окно, если оно открыто
    if (ModalContext.currentEntity === 'connection' && ModalContext.currentMode === 'edit') {
        closeUniversalModal();
    }
}
```

**Где объявить:** В секции функций удаления (после deleteConcept)

**Вывод:** 🆕 Создать новую версию с использованием `findConnection()`, `updateGraphData()` и `closeUniversalModal()`

---

## 12. swapConnectionConcepts

**Статус:** 🔧 Требует адаптации к новой системе

**Что делает:** Меняет местами начальную и конечную концепции в форме редактирования связи

**Старая версия:**
```javascript
function swapConnectionConcepts() {
    // Меняем местами source и target в editMode
    const temp = editMode.data.source;
    editMode.data.source = editMode.data.target;
    editMode.data.target = temp;
    
    // Перерисовываем форму
    openEditConnectionModal(editMode.data);
}
```

**НОВАЯ версия для унифицированной системы:**

```javascript
/**
 * Меняет местами начальную и конечную концепции в форме редактирования связи
 */
function swapConnectionConcepts() {
    // Меняем местами source и target в ModalContext
    const temp = ModalContext.editState.selectedSource;
    ModalContext.editState.selectedSource = ModalContext.editState.selectedTarget;
    ModalContext.editState.selectedTarget = temp;
    
    // Обновляем отображение выбранных концепций
    const sourceSelected = document.getElementById('connSourceSelected');
    const targetSelected = document.getElementById('connTargetSelected');
    const sourceLabel = document.getElementById('connSourceLabel');
    const targetLabel = document.getElementById('connTargetLabel');
    const sourcePhil = document.getElementById('connSourcePhil');
    const targetPhil = document.getElementById('connTargetPhil');
    
    // Получаем данные концепций
    const sourceConcept = ModalContext.editState.selectedSource ? 
        nodes.find(n => n.id === ModalContext.editState.selectedSource) : null;
    const targetConcept = ModalContext.editState.selectedTarget ? 
        nodes.find(n => n.id === ModalContext.editState.selectedTarget) : null;
    
    // Обновляем отображение
    if (sourceConcept) {
        sourceSelected.style.display = 'block';
        sourceLabel.textContent = sourceConcept.label;
        sourcePhil.textContent = sourceConcept.concept;
    } else {
        sourceSelected.style.display = 'none';
    }
    
    if (targetConcept) {
        targetSelected.style.display = 'block';
        targetLabel.textContent = targetConcept.label;
        targetPhil.textContent = targetConcept.concept;
    } else {
        targetSelected.style.display = 'none';
    }
}
```

**Вывод:** 🔧 Заменить `editMode` на `ModalContext.editState` и обновить DOM напрямую

---

## 13. makeLegendsEditable

**Статус:** 🔧 Требует изменений для вызова новых функций

**Что делает:** Делает элементы легенды кликабельными для редактирования

**Старая версия:**
```javascript
function makeLegendsEditable() {
    // Shift+click на заголовок для добавления нового философа
    const philHeader = document.querySelector('.legend-section h4');
    if (philHeader && philHeader.textContent.includes('Философы')) {
        philHeader.addEventListener('click', function(event) {
            if (event.shiftKey) {
                event.preventDefault();
                event.stopPropagation();
                openEditPhilosopherModal();
            }
        });
        philHeader.style.cursor = 'pointer';
        philHeader.title = 'Shift+клик для добавления философа';
    }
    
    // Делаем каждого философа кликабельным
    document.querySelectorAll('.legend-item').forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) {
            const philosopherName = checkbox.value;
            
            // Shift+клик для редактирования
            item.addEventListener('click', function(event) {
                if (event.shiftKey) {
                    event.preventDefault();
                    event.stopPropagation();
                    openEditPhilosopherModal(philosopherName);
                }
            });
            
            // Двойной клик для детальной информации
            item.addEventListener('dblclick', function(event) {
                event.preventDefault();
                event.stopPropagation();
                showPhilosopherDetailModal(philosopherName);
            });
            
            item.title = 'Двойной клик - детальная информация, Shift+клик - редактирование';
        }
    });
}
```

**Проблема:** Вызывает старые функции `openEditPhilosopherModal()` и `showPhilosopherDetailModal()`

**Исправленная версия:**

```javascript
function makeLegendsEditable() {
    // Shift+click на заголовок для добавления нового философа
    const philHeader = document.querySelector('.legend-section h4');
    if (philHeader && philHeader.textContent.includes('Философы')) {
        philHeader.addEventListener('click', function(event) {
            if (event.shiftKey) {
                event.preventDefault();
                event.stopPropagation();
                // 🔧 ИЗМЕНЕНИЕ: Используем новую функцию
                openUniversalModal('philosopher', null, 'edit');
            }
        });
        philHeader.style.cursor = 'pointer';
        philHeader.title = 'Shift+клик для добавления философа';
    }
    
    // Делаем каждого философа кликабельным
    document.querySelectorAll('.legend-item').forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) {
            const philosopherName = checkbox.value;
            
            // Shift+клик для редактирования
            item.addEventListener('click', function(event) {
                if (event.shiftKey) {
                    event.preventDefault();
                    event.stopPropagation();
                    // 🔧 ИЗМЕНЕНИЕ: Используем новую функцию
                    openUniversalModal('philosopher', philosopherName, 'edit');
                }
            });
            
            // Двойной клик для детальной информации
            item.addEventListener('dblclick', function(event) {
                event.preventDefault();
                event.stopPropagation();
                // 🔧 ИЗМЕНЕНИЕ: Используем новую функцию
                openUniversalModal('philosopher', philosopherName, 'view');
            });
            
            item.title = 'Двойной клик - детальная информация, Shift+клик - редактирование';
        }
    });
}
```

**Вывод:** 🔧 Заменить все вызовы старых функций на `openUniversalModal()`

---

## Итоговая сводная таблица

| № | Функция | Статус | Действие |
|---|---------|--------|----------|
| 1 | `toggleConnectionDescription` | ✅ | Не требует изменений |
| 2 | `toggleAllConnectionDescriptions` | 🔧 | Заменить `getElementById('detailModal')` на `querySelector('.detail-modal.show')` |
| 3 | `toggleSubsection` | ✅ | Не требует изменений |
| 4 | `gotoNodeFromModal` | 🔧 | Заменить `closeDetailModal()` на `closeUniversalModal()` |
| 5 | `showAllConcepts` | 🔧 | Заменить `showDetailModal()` на `openUniversalModal()` (если нет адаптеров) |
| 6 | `togglePhilosopherConceptDescription` | ✅ | Не требует изменений |
| 7 | `toggleAllPhilosopherConceptDescriptions` | 🔧 | Заменить хардкод ID на универсальный селектор |
| 8 | `toggleAllPhilosopherConnectionDescriptions` | 🔧 | Заменить хардкод ID на универсальный селектор |
| 9 | `deletePhilosopher` | ❌ | Использовать новую версию |
| 10 | `deleteConcept` | ❌ | Использовать новую версию |
| 11 | `deleteConnection` | 🆕 | Создать новую версию |
| 12 | `swapConnectionConcepts` | 🔧 | Заменить `editMode` на `ModalContext.editState` |
| 13 | `makeLegendsEditable` | 🔧 | Заменить все вызовы на `openUniversalModal()` |

---

## Рекомендации по адаптерам

Для упрощения миграции можно создать **функции-адаптеры**, которые будут вызывать новые функции:

```javascript
// ============================================
// АДАПТЕРЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
// ============================================

// Адаптеры для модальных окон
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

**С адаптерами:** Функции 5, 13 не потребуют изменений!

---

## Чек-лист адаптации

### ✅ Не требуют изменений (2 функции):
- [ ] `toggleConnectionDescription`
- [ ] `toggleSubsection`
- [ ] `togglePhilosopherConceptDescription`

### 🔧 Требуют небольших изменений (7 функций):
- [ ] `toggleAllConnectionDescriptions` - заменить селектор модального окна
- [ ] `gotoNodeFromModal` - заменить функцию закрытия
- [ ] `showAllConcepts` - заменить вызов функции (если нет адаптеров)
- [ ] `toggleAllPhilosopherConceptDescriptions` - заменить селектор
- [ ] `toggleAllPhilosopherConnectionDescriptions` - заменить селектор
- [ ] `swapConnectionConcepts` - заменить editMode на ModalContext
- [ ] `makeLegendsEditable` - заменить все вызовы

### 🆕 Требуют создания новой версии (1 функция):
- [ ] `deleteConnection` - создать с нуля

### ❌ Уже созданы новые версии (2 функции):
- [x] `deletePhilosopher` - использовать из `functions_integration_corrected.md`
- [x] `deleteConcept` - использовать из `functions_integration_corrected.md`

### 💾 ОПЦИОНАЛЬНО - Создать адаптеры:
- [ ] Добавить 7 функций-адаптеров для упрощения миграции

---

## Рекомендуемый порядок действий

1. **Создать адаптеры** (самое простое) - сэкономит время на правках
2. **Исправить функции с селекторами** (3 функции) - простая замена строки
3. **Исправить gotoNodeFromModal** - замена одного вызова
4. **Исправить swapConnectionConcepts** - замена объекта состояния
5. **Создать deleteConnection** - новая функция
6. **Исправить makeLegendsEditable** - если не создавали адаптеры
7. **Исправить showAllConcepts** - если не создавали адаптеры

**С адаптерами:** 5 изменений
**Без адаптеров:** 9 изменений

**Рекомендация:** Создайте адаптеры - это сэкономит время и упростит миграцию!
